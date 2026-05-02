/**
 * obsidian-render-cache — Phase 9 command implementations.
 *
 * The 7 commands per SPEC §5 Phase 9:
 *   refresh-block (AC9.1)
 *   refresh-note  (AC9.2)
 *   refresh-vault (AC9.3, with streaming progress)
 *   show-status   (AC9.4)
 *   sweep         (AC9.5, --sweep)
 *   toggle-mode   (AC9.6)
 *   clear-all     (AC9.7, with strong confirmation)
 *
 * Pure helpers (`findBlockAtCursorLine`, `nextMode-helper-for-toggle`) are
 * unit-tested. The Obsidian-side glue is smoke-tested at the user gate.
 */
import {
  App,
  Modal,
  Notice,
  Plugin,
  TFile,
  MarkdownView,
} from "obsidian";
import {
  CacheStatus,
  CacheStatusModal,
  aggregateStatus,
} from "./cacheStatus";
import {
  RenderCacheSettings,
  effectiveMode,
  nextMode,
} from "./settings";
import { spawnRender, spawnRenderWithNotice } from "./render";

/** Languages the plugin handles. Single source of truth for command palette
 *  output; mirrors LANGUAGES in main.ts. */
const SUPPORTED_LANGUAGES = [
  "tikz",
  "graphviz",
  "d2",
  "lilypond",
  "smiles",
] as const;

/** Find which fenced block contains the given line. Returns blockIdx (0-based,
 *  counting only blocks of supported languages) or null if cursor is not inside
 *  one. Pure: no Obsidian deps. */
export function findBlockAtCursorLine(
  source: string,
  cursorLine: number,
): { blockIdx: number; language: string; lineStart: number; lineEnd: number } | null {
  const lines = source.split("\n");
  let blockIdx = -1;
  let inBlock = false;
  let blockLang = "";
  let blockStart = -1;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const fenceMatch = /^```(\w[\w-]*)/.exec(line);
    if (!inBlock && fenceMatch) {
      const lang = fenceMatch[1].toLowerCase();
      if (
        (SUPPORTED_LANGUAGES as readonly string[]).includes(lang) ||
        lang === "tikz-paused"
      ) {
        inBlock = true;
        blockLang = lang === "tikz-paused" ? "tikz" : lang;
        blockStart = i;
        blockIdx += 1;
      }
      continue;
    }
    if (inBlock && /^```\s*$/.test(line)) {
      // closing fence
      if (cursorLine >= blockStart && cursorLine <= i) {
        return {
          blockIdx,
          language: blockLang,
          lineStart: blockStart,
          lineEnd: i,
        };
      }
      inBlock = false;
      blockStart = -1;
      blockLang = "";
    }
  }
  return null;
}

interface IndexShape {
  notes: Record<string, { blocks: BlockEntry[] }>;
  preambleHashes?: Record<string, string>;
  schemaVersion?: number;
  rendererVersion?: string;
}

interface BlockEntry {
  blockIdx: number;
  language: string;
  sourceHash: string;
  cachePath: string;
  outputBytes: number;
  outputFormat: string;
  renderedAt: string | null;
  rendererVersion: string;
  lastError: string | null;
}

/** Plugin context the commands need from main.ts. */
export interface CommandContext {
  app: App;
  plugin: Plugin;
  settings: () => RenderCacheSettings;
  vaultRoot: () => string;
  reloadIndex: () => Promise<void>;
  getIndex: () => IndexShape | null;
  setRendering?: (sourcePath: string, rendering: boolean) => void;
  cacheRoot: string; // e.g., ".obsidian/plugins/obsidian-render-cache/cache"
  indexPath: string; // e.g., ".obsidian/plugins/obsidian-render-cache/cache/index.json"
}

/** Register all 7 commands with the plugin's command palette. */
export function registerCommands(ctx: CommandContext): void {
  const p = ctx.plugin;

  p.addCommand({
    id: "refresh-block",
    name: "Refresh this block",
    callback: () => refreshBlock(ctx),
  });

  p.addCommand({
    id: "refresh-note",
    name: "Refresh all blocks in this note",
    callback: () => refreshNote(ctx),
  });

  p.addCommand({
    id: "refresh-vault",
    name: "Refresh entire vault (with confirmation)",
    callback: () => refreshVault(ctx),
  });

  p.addCommand({
    id: "show-status",
    name: "Show cache status",
    callback: () => showStatus(ctx),
  });

  p.addCommand({
    id: "sweep",
    name: "Sweep orphan cache files",
    callback: () => sweepOrphans(ctx),
  });

  p.addCommand({
    id: "toggle-mode",
    name: "Toggle render mode (hybrid → cache-only → live)",
    callback: () => toggleMode(ctx),
  });

  p.addCommand({
    id: "clear-all",
    name: "Clear entire cache (DESTRUCTIVE)",
    callback: () => clearAll(ctx),
  });
}

// ─── refresh-block (AC9.1) ────────────────────────────────────────────────

async function refreshBlock(ctx: CommandContext): Promise<void> {
  const view = ctx.app.workspace.getActiveViewOfType(MarkdownView);
  if (!view || !view.file) {
    new Notice("No active markdown view.", 4000);
    return;
  }
  const file = view.file as TFile;
  const cursor = view.editor.getCursor();
  const source = view.editor.getValue();
  const block = findBlockAtCursorLine(source, cursor.line);
  if (!block) {
    new Notice(
      "Place the cursor inside a TikZ / Graphviz / D2 / LilyPond / SMILES code block.",
      4000,
    );
    return;
  }

  // CRITICAL: Python reads the file from DISK. If the user edited the block
  // but hasn't saved, the editor buffer differs from disk content and
  // `render_cache.py FILE.md` would re-render the OLD content (silent no-op
  // for the user). Persist the editor buffer first so refresh-block always
  // reflects the visible source. Advisor §1 (Phase 9 pre-ship review).
  try {
    const onDisk = await ctx.app.vault.read(file);
    if (onDisk !== source) {
      await ctx.app.vault.modify(file, source);
    }
  } catch (err) {
    console.warn("render-cache: refresh-block disk-sync failed", err);
  }

  // Find the matching index entry by blockIdx (within the same note).
  const idx = ctx.getIndex();
  const entry = idx?.notes[file.path]?.blocks.find(
    (b) => b.blockIdx === block.blockIdx,
  );
  if (entry) {
    try {
      const exists = await ctx.app.vault.adapter.exists(entry.cachePath);
      if (exists) await ctx.app.vault.adapter.remove(entry.cachePath);
    } catch (err) {
      console.warn("render-cache: refresh-block remove failed", err);
    }
  }

  new Notice(`Refreshing ${block.language} block #${block.blockIdx}…`, 3000);
  ctx.setRendering?.(file.path, true);
  try {
    const ok = await spawnRenderWithNotice(
      ctx.settings(),
      [file.path],
      ctx.vaultRoot(),
      `${block.language} block #${block.blockIdx} refreshed.`,
    );
    if (ok) await ctx.reloadIndex();
  } finally {
    ctx.setRendering?.(file.path, false);
  }
}

// ─── refresh-note (AC9.2) ─────────────────────────────────────────────────

async function refreshNote(ctx: CommandContext): Promise<void> {
  const file = ctx.app.workspace.getActiveFile();
  if (!file) {
    new Notice("No active file.", 4000);
    return;
  }

  // Same disk-sync as refresh-block: if the user has unsaved edits in the
  // current view, persist them first so Python sees the visible source.
  // Advisor §1 (Phase 9 pre-ship review).
  const view = ctx.app.workspace.getActiveViewOfType(MarkdownView);
  if (view?.file?.path === file.path) {
    try {
      const buffer = view.editor.getValue();
      const onDisk = await ctx.app.vault.read(file);
      if (onDisk !== buffer) {
        await ctx.app.vault.modify(file, buffer);
      }
    } catch (err) {
      console.warn("render-cache: refresh-note disk-sync failed", err);
    }
  }

  new Notice(`Refreshing all blocks in ${file.path}…`, 3000);
  ctx.setRendering?.(file.path, true);
  try {
    const ok = await spawnRenderWithNotice(
      ctx.settings(),
      [file.path, "--force"],
      ctx.vaultRoot(),
      `Refreshed: ${file.path}`,
    );
    if (ok) await ctx.reloadIndex();
  } finally {
    ctx.setRendering?.(file.path, false);
  }
}

// ─── refresh-vault (AC9.3) ────────────────────────────────────────────────

async function refreshVault(ctx: CommandContext): Promise<void> {
  const ok = await new Promise<boolean>((resolve) => {
    new ConfirmationModal(
      ctx.app,
      "Refresh entire vault?",
      "This runs `render_cache.py --all --force` and re-renders every cached " +
        "block in the vault. May take several minutes for large vaults.",
      "Refresh vault",
      resolve,
    ).open();
  });
  if (!ok) return;

  const progress = new ProgressModal(ctx.app, "Vault refresh");
  progress.open();
  ctx.setRendering?.("__vault__", true);
  try {
    const result = await spawnRender(
      ctx.settings(),
      ["--all", "--force"],
      ctx.vaultRoot(),
      (line, source) => progress.appendLine(line, source),
    );
    progress.setStatus(
      result.exitCode === 0
        ? "Done."
        : `Exited ${result.exitCode}.`,
    );
  } catch (err) {
    progress.setStatus(`Spawn failed: ${String(err)}`);
  } finally {
    ctx.setRendering?.("__vault__", false);
  }
  await ctx.reloadIndex();
}

// ─── show-status (AC9.4) ──────────────────────────────────────────────────

function showStatus(ctx: CommandContext): void {
  const idx = ctx.getIndex();
  const status: CacheStatus = aggregateStatus(idx);
  new CacheStatusModal(ctx.app, status).open();
}

// ─── sweep (AC9.5) ────────────────────────────────────────────────────────

async function sweepOrphans(ctx: CommandContext): Promise<void> {
  new Notice("Sweeping orphans…", 3000);
  const ok = await spawnRenderWithNotice(
    ctx.settings(),
    ["--sweep"],
    ctx.vaultRoot(),
    "Sweep complete.",
  );
  if (ok) await ctx.reloadIndex();
}

// ─── toggle-mode (AC9.6) ──────────────────────────────────────────────────

async function toggleMode(ctx: CommandContext): Promise<void> {
  const settings = ctx.settings();
  const next = nextMode(settings.mode);
  settings.mode = next;
  // Persist via the plugin's saveData (settings is the live reference).
  const p = ctx.plugin as unknown as { saveSettings: () => Promise<void> };
  if (typeof p.saveSettings === "function") await p.saveSettings();
  new Notice(`Render mode: ${next}`, 3000);
}

// ─── clear-all (AC9.7) ────────────────────────────────────────────────────

async function clearAll(ctx: CommandContext): Promise<void> {
  const ok = await new Promise<boolean>((resolve) => {
    new ConfirmationModal(
      ctx.app,
      "Clear entire cache?",
      "DESTRUCTIVE: deletes every cached SVG and the index. The next time " +
        "you open a note with a supported code block, it will show a cache-miss " +
        "placeholder until render_cache.py runs again.",
      "Yes, delete all",
      resolve,
    ).open();
  });
  if (!ok) return;

  // Walk the cache directory recursively. Phase 12 moves SVGs under v1/<note>.
  // We keep the top-level container directory so the plugin can recreate
  // index.json cleanly on the next render.
  const adapter = ctx.app.vault.adapter;
  let removed = 0;
  let errors = 0;
  try {
    const files = await listFilesRecursive(adapter, ctx.cacheRoot);
    for (const f of files) {
      try {
        await adapter.remove(f);
        removed += 1;
      } catch {
        errors += 1;
      }
    }
  } catch (err) {
    new Notice(`Cache directory not found: ${ctx.cacheRoot}`, 4000);
    return;
  }

  new Notice(
    `Cleared cache: ${removed} file(s) removed${errors ? `, ${errors} error(s)` : ""}.`,
    5000,
  );
  await ctx.reloadIndex();
}

async function listFilesRecursive(
  adapter: App["vault"]["adapter"],
  root: string,
): Promise<string[]> {
  const list = await adapter.list(root);
  const files = [...list.files];
  for (const folder of list.folders) {
    files.push(...await listFilesRecursive(adapter, folder));
  }
  return files;
}

// ─── Confirmation modal (used by refresh-vault + clear-all) ──────────────

class ConfirmationModal extends Modal {
  private readonly title: string;
  private readonly body: string;
  private readonly confirmText: string;
  private readonly resolve: (ok: boolean) => void;
  private resolved = false;

  constructor(
    app: App,
    title: string,
    body: string,
    confirmText: string,
    resolve: (ok: boolean) => void,
  ) {
    super(app);
    this.title = title;
    this.body = body;
    this.confirmText = confirmText;
    this.resolve = resolve;
  }

  onOpen(): void {
    const { contentEl } = this;
    contentEl.empty();
    contentEl.createEl("h2", { text: this.title });
    contentEl.createEl("p", { text: this.body });
    const btnRow = contentEl.createEl("div", { cls: "render-cache-btn-row" });
    const cancel = btnRow.createEl("button", { text: "Cancel" });
    cancel.onclick = () => {
      this.resolveOnce(false);
      this.close();
    };
    const confirm = btnRow.createEl("button", {
      text: this.confirmText,
      cls: "mod-warning",
    });
    confirm.onclick = () => {
      this.resolveOnce(true);
      this.close();
    };
  }

  onClose(): void {
    this.resolveOnce(false);
    this.contentEl.empty();
  }

  private resolveOnce(v: boolean): void {
    if (this.resolved) return;
    this.resolved = true;
    this.resolve(v);
  }
}

// ─── Progress modal (refresh-vault streaming) ────────────────────────────

class ProgressModal extends Modal {
  private readonly title: string;
  private logEl: HTMLElement | null = null;
  private statusEl: HTMLElement | null = null;

  constructor(app: App, title: string) {
    super(app);
    this.title = title;
  }

  onOpen(): void {
    const { contentEl } = this;
    contentEl.empty();
    contentEl.createEl("h2", { text: this.title });
    this.statusEl = contentEl.createEl("p", { text: "Running…" });
    this.logEl = contentEl.createEl("pre", { cls: "render-cache-log" });
    this.logEl.style.maxHeight = "300px";
    this.logEl.style.overflow = "auto";
  }

  onClose(): void {
    this.contentEl.empty();
    this.logEl = null;
    this.statusEl = null;
  }

  appendLine(line: string, source: "stdout" | "stderr"): void {
    if (!this.logEl) return;
    const span = document.createElement("span");
    span.textContent = (source === "stderr" ? "[stderr] " : "") + line + "\n";
    if (source === "stderr") span.style.color = "var(--text-error)";
    this.logEl.appendChild(span);
    this.logEl.scrollTop = this.logEl.scrollHeight;
  }

  setStatus(msg: string): void {
    if (this.statusEl) this.statusEl.textContent = msg;
  }
}

/** Helper: when `effectiveMode` is "live", caller should call this to kick a
 *  background re-render of the file. Used by main.ts displayCachedBlock when
 *  mode is live. Returns immediately (fire-and-forget). */
export function fireLiveRender(
  ctx: CommandContext,
  filePath: string,
): void {
  ctx.setRendering?.(filePath, true);
  void spawnRender(
    ctx.settings(),
    [filePath, "--force"],
    ctx.vaultRoot(),
  ).then(async (r) => {
    if (r.exitCode === 0) await ctx.reloadIndex();
  }).catch((err) => {
    console.warn("render-cache: live render failed", err);
  }).finally(() => {
    ctx.setRendering?.(filePath, false);
  });
}

/** Re-export for completeness. Allows main.ts to consult the helper without
 *  importing both modules. */
export { effectiveMode };
