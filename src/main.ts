/**
 * visual-blocks — Phase 9 plugin (commands + modes + save hook).
 *
 * Architecture: a viewer + thin command surface for Python pipeline.
 * Renders happen at save time via resources/scripts/python_single/render_cache.py
 * (SPEC §1.2 D04 — Python is canonical writer, plugin is reader-only).
 *
 * Phase 9 adds:
 *   • 7 commands (refresh-block / refresh-note / refresh-vault / show-status
 *     / sweep / toggle-mode / clear-all) — see commands.ts.
 *   • 3 render modes (hybrid / cache-only / live). Mobile auto-overrides to
 *     cache-only regardless of stored setting.
 *   • Settings tab — see settings.ts.
 *   • triggerOnSave: when a markdown file with a supported codeblock is
 *     saved, automatically run render_cache.py on it (desktop only).
 *
 * For each registered language the plugin:
 *   1. Computes the canonical 16-char SHA-256 cache key from the block
 *      source (see hash.ts; byte-identical to Python compute_key per T12).
 *   2. Looks up the entry in .obsidian/plugins/visual-blocks/cache/index.json by
 *      sourceHash (advisor: first match wins; identical-source duplicates
 *      have identical cached SVGs).
 *   3. Mode-aware behavior:
 *        hybrid     → on hit show img; on miss show clickable placeholder
 *        cache-only → on hit show img; on miss show non-clickable placeholder
 *        live       → on every load, fire `render_cache.py FILE.md --force`
 *                     in the background; show stale cache while it runs;
 *                     reload index when render returns. AC9.8: fresh mtime
 *                     on every load.
 */
import {
  MarkdownPostProcessorContext,
  Notice,
  Platform,
  Plugin,
  TFile,
  FileSystemAdapter,
} from "obsidian";
import { computeKey } from "./hash";
import {
  CommandContext,
  fireLiveRender,
  registerCommands,
} from "./commands";
import { spawnRender } from "./render";
import {
  DEFAULT_SETTINGS,
  RenderCacheSettings,
  RenderCacheSettingTab,
  effectiveMode,
  isPlaceholderClickable,
  missMessage,
  normalizeSettings,
} from "./settings";
import {
  LanguageId,
  VISUAL_BLOCK_LANGUAGES,
  buildLanguageFilterArgs,
  canonicalizeFenceLanguage,
  hasEnabledSupportedBlock,
  isLanguageEnabled,
  languageLabel,
} from "./languages";
import {
  CacheStatusModal,
  aggregateNoteStatus,
  aggregateStatus,
  statusBarText,
} from "./cacheStatus";
import {
  shouldRunStartupAutoRefresh,
  startupAutoRefreshArgs,
  startupAutoRefreshDelayMs,
} from "./startup";

const LANGUAGES: LanguageId[] = VISUAL_BLOCK_LANGUAGES.map((l) => l.id);
const FENCE_LANGUAGES = VISUAL_BLOCK_LANGUAGES.flatMap((l) => l.fences);

const CACHE_ROOT = ".obsidian/plugins/visual-blocks/cache";
const INDEX_PATH = `${CACHE_ROOT}/index.json`;

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

interface IndexFile {
  schemaVersion?: number;
  rendererVersion?: string;
  preambleHashes: Record<string, string>;
  notes: Record<string, { blocks: BlockEntry[] }>;
}

export default class RenderCachePlugin extends Plugin {
  settings: RenderCacheSettings = { ...DEFAULT_SETTINGS };
  private index: IndexFile | null = null;
  private commandCtx!: CommandContext;
  private liveRenderInFlight = new Set<string>(); // file paths currently being live-rendered
  private renderingFiles = new Set<string>();
  private statusBarEl: HTMLElement | null = null;

  async onload(): Promise<void> {
    await this.loadSettings();
    await this.reloadIndex();

    this.commandCtx = {
      app: this.app,
      plugin: this,
      settings: () => this.settings,
      vaultRoot: () => this.vaultRoot(),
      reloadIndex: () => this.reloadIndex(),
      getIndex: () => this.index,
      setRendering: (sourcePath, rendering) =>
        this.setRendering(sourcePath, rendering),
      cacheRoot: CACHE_ROOT,
      indexPath: INDEX_PATH,
    };

    this.statusBarEl = this.addStatusBarItem();
    this.statusBarEl.classList.add("visual-blocks-status-bar");
    this.statusBarEl.onclick = () => {
      new CacheStatusModal(
        this.app,
        aggregateStatus(this.index, this.settings.enabledLanguages),
      ).open();
    };
    this.registerEvent(
      this.app.workspace.on("file-open", () => this.updateStatusBar()),
    );
    this.registerEvent(
      this.app.workspace.on("active-leaf-change", () =>
        this.updateStatusBar(),
      ),
    );
    this.updateStatusBar();

    for (const fenceLang of FENCE_LANGUAGES) {
      const lang = canonicalizeFenceLanguage(fenceLang);
      if (!lang) continue;
      this.registerMarkdownCodeBlockProcessor(
        fenceLang,
        async (source, el, ctx) => {
          try {
            await this.displayCachedBlock(source, lang, el, ctx);
          } catch (err) {
            this.renderError(el, lang, err);
          }
        },
      );
    }

    registerCommands(this.commandCtx);
    this.addSettingTab(new RenderCacheSettingTab(this.app, this));

    // triggerOnSave: re-render on file modify (desktop only).
    this.registerEvent(
      this.app.vault.on("modify", (file) => {
        if (Platform.isMobile) return;
        if (!this.settings.triggerOnSave) return;
        if (!(file instanceof TFile)) return;
        if (file.extension !== "md") return;
        void this.maybeReRenderOnSave(file);
      }),
    );

    this.scheduleStartupAutoRefresh();

    console.log(
      `visual-blocks: loaded; processors registered for ${FENCE_LANGUAGES.join(", ")}; ` +
        `mode=${this.settings.mode}; triggerOnSave=${this.settings.triggerOnSave}`,
    );
  }

  async onunload(): Promise<void> {
    console.log("visual-blocks: unloaded");
  }

  // ─── settings ─────────────────────────────────────────────────────────

  async loadSettings(): Promise<void> {
    const raw = (await this.loadData()) as Partial<RenderCacheSettings> | null;
    this.settings = normalizeSettings(raw);
  }

  async saveSettings(): Promise<void> {
    await this.saveData(this.settings);
  }

  // ─── index ────────────────────────────────────────────────────────────

  async reloadIndex(): Promise<void> {
    try {
      const exists = await this.app.vault.adapter.exists(INDEX_PATH);
      if (!exists) {
        this.index = null;
        return;
      }
      const text = await this.app.vault.adapter.read(INDEX_PATH);
      this.index = JSON.parse(text) as IndexFile;
    } catch (err) {
      console.error("visual-blocks: failed to load index", err);
      this.index = null;
    } finally {
      this.updateStatusBar();
    }
  }

  // ─── view path ────────────────────────────────────────────────────────

  private async displayCachedBlock(
    source: string,
    lang: LanguageId,
    el: HTMLElement,
    ctx: MarkdownPostProcessorContext,
  ): Promise<void> {
    el.empty();
    const wrapper = el.createDiv({ cls: "visual-blocks-block" });
    const mode = effectiveMode(this.settings, Platform.isMobile);

    if (!isLanguageEnabled(this.settings.enabledLanguages, lang)) {
      this.renderPlaceholder(
        wrapper,
        lang,
        `${languageLabel(lang)} is disabled in Visual Blocks settings.`,
        false,
        ctx.sourcePath,
      );
      return;
    }

    // Live mode (desktop only — mobile auto-overrides to cache-only above).
    // Fire async re-render of the entire file. Show stale cache or
    // placeholder in the meantime; reloadIndex on completion (next render
    // pass on this block will pick up the new entry naturally).
    if (mode === "live" && !Platform.isMobile && ctx.sourcePath) {
      if (!this.liveRenderInFlight.has(ctx.sourcePath)) {
        this.liveRenderInFlight.add(ctx.sourcePath);
        try {
          fireLiveRender(this.commandCtx, ctx.sourcePath);
        } finally {
          // Clear after a short cooldown so multiple blocks in the same note
          // don't each fire their own render.
          setTimeout(
            () => this.liveRenderInFlight.delete(ctx.sourcePath),
            5000,
          );
        }
      }
    }

    if (!this.index) {
      this.renderPlaceholder(
        wrapper,
        lang,
        `${lang}: Index not loaded. Run render_cache.py to (re)build the cache.`,
        false,
        ctx.sourcePath,
      );
      return;
    }

    const preambleHash = this.index.preambleHashes[`<adapter:${lang}>`] ?? "";
    if (!preambleHash) {
      this.renderPlaceholder(
        wrapper,
        lang,
        `${lang}: No preamble hash in index. Run render_cache.py.`,
        false,
        ctx.sourcePath,
      );
      return;
    }

    const key = await computeKey(source, lang, {}, preambleHash);
    const entry = this.findEntry(ctx.sourcePath, key);

    if (!entry) {
      this.renderPlaceholder(
        wrapper,
        lang,
        missMessage(mode, lang, Platform.isMobile),
        isPlaceholderClickable(mode, Platform.isMobile),
        ctx.sourcePath,
      );
      return;
    }

    if (entry.lastError) {
      this.renderInlineError(
        wrapper,
        lang,
        entry.lastError,
        !Platform.isMobile && Boolean(ctx.sourcePath),
        ctx.sourcePath,
      );
      return;
    }

    const fileExists = await this.app.vault.adapter.exists(entry.cachePath);
    if (!fileExists) {
      this.renderPlaceholder(
        wrapper,
        lang,
        `${lang}: Cache miss — ${entry.cachePath} listed in index but missing on disk.`,
        isPlaceholderClickable(mode, Platform.isMobile),
        ctx.sourcePath,
      );
      return;
    }

    const src = this.app.vault.adapter.getResourcePath(entry.cachePath);
    wrapper.createEl("img", {
      cls: "visual-blocks-img",
      attr: {
        src,
        alt: `${lang}-cache`,
        loading: "lazy",
      },
    });
  }

  private findEntry(sourcePath: string, key: string): BlockEntry | null {
    if (!this.index) return null;
    const note = this.index.notes[sourcePath];
    if (!note) return null;
    return note.blocks.find((b) => b.sourceHash === key) ?? null;
  }

  private renderPlaceholder(
    parent: HTMLElement,
    lang: LanguageId,
    msg: string,
    clickable: boolean,
    sourcePath: string | null,
  ): void {
    const el = parent.createDiv({
      cls:
        "visual-blocks-placeholder" + (clickable ? " is-clickable" : ""),
    });
    el.appendText(msg);
    if (clickable) {
      el.onclick = () => {
        if (!sourcePath) {
          new Notice("No source path; reload the note and try again.", 4000);
          return;
        }
        new Notice(`Refreshing ${sourcePath}…`, 3000);
        void this.runRenderForFile(sourcePath);
      };
    }
  }

  /** Click-to-render handler. Runs render_cache.py FILE.md (no --force) so
   *  only the missing block actually compiles. Reloads index on success. */
  private async runRenderForFile(
    filePath: string,
    force: boolean = false,
  ): Promise<void> {
    const languageArgs = buildLanguageFilterArgs(this.settings.enabledLanguages);
    if (!languageArgs) {
      new Notice("No Visual Blocks visualization libraries are enabled.", 4000);
      return;
    }
    this.setRendering(filePath, true);
    try {
      const result = await spawnRender(
        this.settings,
        force ? [filePath, "--force", ...languageArgs] : [filePath, ...languageArgs],
        this.vaultRoot(),
      );
      await this.reloadIndex();
      if (result.exitCode === 0) {
        new Notice(
          `Render complete. Reload the note to see the diagram.`,
          4000,
        );
      } else {
        new Notice(
          `render_cache.py exited ${result.exitCode}.\n` +
            (result.stderr.trim().slice(0, 600) ||
              result.stdout.trim().slice(0, 600) ||
              "(no diagnostic)"),
          8000,
        );
      }
    } catch (err) {
      new Notice(
        `Spawn failed: ${String(err)}.\nCheck Python path settings.`,
        8000,
      );
    } finally {
      this.setRendering(filePath, false);
    }
  }

  private renderInlineError(
    parent: HTMLElement,
    lang: LanguageId,
    message: string,
    clickable: boolean,
    sourcePath: string | null,
  ): void {
    const el = parent.createDiv({
      cls:
        "visual-blocks-inline-error" + (clickable ? " is-clickable" : ""),
    });
    el.createDiv({
      cls: "visual-blocks-error-title",
      text: `${lang}: render failed`,
    });
    el.createEl("pre", {
      cls: "visual-blocks-error-message",
      text: message,
    });
    el.createDiv({
      cls: "visual-blocks-error-help",
      text: clickable
        ? "Click to retry this note."
        : "Open on desktop to retry.",
    });

    if (clickable) {
      el.onclick = () => {
        if (!sourcePath) return;
        new Notice(`Retrying render for ${sourcePath}…`, 3000);
        void this.runRenderForFile(sourcePath, true);
      };
    }
  }

  private renderError(el: HTMLElement, lang: LanguageId, err: unknown): void {
    el.empty();
    const div = el.createDiv({ cls: "visual-blocks-error" });
    div.appendText(
      `visual-blocks: ${lang} block failed — ${String(err)}`,
    );
  }

  // ─── triggerOnSave ────────────────────────────────────────────────────

  private modifyDebounce = new Map<string, number>();

  private async maybeReRenderOnSave(file: TFile): Promise<void> {
    const path = file.path;
    // Debounce: throttle to one render per file per 3 seconds.
    const now = Date.now();
    const last = this.modifyDebounce.get(path) ?? 0;
    if (now - last < 3000) return;
    this.modifyDebounce.set(path, now);

    // Only re-render if the file has at least one supported codeblock.
    let text: string;
    try {
      text = await this.app.vault.read(file);
    } catch {
      return;
    }
    if (!hasEnabledSupportedBlock(text, this.settings.enabledLanguages)) return;

    this.setRendering(path, true);
    try {
      const languageArgs = buildLanguageFilterArgs(this.settings.enabledLanguages);
      if (!languageArgs) return;
      const result = await spawnRender(
        this.settings,
        [path, ...languageArgs],
        this.vaultRoot(),
      );
      await this.reloadIndex();
      if (result.exitCode !== 0) {
        console.warn(
          `visual-blocks: triggerOnSave on ${path} exited ${result.exitCode}.\n` +
            result.stderr.slice(0, 400),
        );
      }
    } catch (err) {
      console.warn("visual-blocks: triggerOnSave spawn failed", err);
    } finally {
      this.setRendering(path, false);
    }
  }

  // ─── startup auto-refresh ─────────────────────────────────────────────

  private scheduleStartupAutoRefresh(): void {
    const decision = shouldRunStartupAutoRefresh(
      this.settings,
      Platform.isMobile,
      Date.now(),
    );
    if (!decision.shouldRun) return;

    const delayMs = startupAutoRefreshDelayMs(this.settings);
    const timeoutId = window.setTimeout(() => {
      void this.runStartupAutoRefresh();
    }, delayMs);
    this.registerInterval(timeoutId);
  }

  private async runStartupAutoRefresh(): Promise<void> {
    const decision = shouldRunStartupAutoRefresh(
      this.settings,
      Platform.isMobile,
      Date.now(),
    );
    if (!decision.shouldRun) return;

    const args = startupAutoRefreshArgs(this.settings);
    if (!args) return;

    this.setRendering("__vault__", true);
    console.log("visual-blocks: startup auto-refresh started");
    try {
      const result = await spawnRender(this.settings, args, this.vaultRoot());
      this.settings.startupRefreshLastRunAt = Date.now();
      await this.saveSettings();
      await this.reloadIndex();
      if (result.exitCode === 0) {
        console.log("visual-blocks: startup auto-refresh complete");
      } else {
        console.warn(
          `visual-blocks: startup auto-refresh exited ${result.exitCode}.\n` +
            (result.stderr.trim().slice(0, 800) ||
              result.stdout.trim().slice(0, 800) ||
              "(no diagnostic)"),
        );
      }
    } catch (err) {
      console.warn("visual-blocks: startup auto-refresh spawn failed", err);
    } finally {
      this.setRendering("__vault__", false);
    }
  }

  // ─── helpers ──────────────────────────────────────────────────────────

  private setRendering(sourcePath: string, rendering: boolean): void {
    if (rendering) this.renderingFiles.add(sourcePath);
    else this.renderingFiles.delete(sourcePath);
    this.updateStatusBar();
  }

  private updateStatusBar(): void {
    if (!this.statusBarEl) return;
    const active = this.app.workspace.getActiveFile();
    const sourcePath = active?.path ?? null;
    const noteStatus = aggregateNoteStatus(
      this.index,
      sourcePath,
      this.settings.enabledLanguages,
    );
    const isRendering =
      (sourcePath !== null && this.renderingFiles.has(sourcePath)) ||
      this.renderingFiles.has("__vault__");

    this.statusBarEl.textContent = statusBarText(noteStatus, isRendering);
    this.statusBarEl.setAttribute(
      "title",
      "Visual Blocks status — click for cache details",
    );
    this.statusBarEl.classList.toggle(
      "has-error",
      noteStatus.errorCount > 0 && !isRendering,
    );
    this.statusBarEl.classList.toggle("is-rendering", isRendering);
  }

  private vaultRoot(): string {
    const adapter = this.app.vault.adapter;
    if (adapter instanceof FileSystemAdapter) {
      return adapter.getBasePath();
    }
    // Mobile path — should never spawn here per AC9.9 mobile auto-override.
    return "";
  }
}
