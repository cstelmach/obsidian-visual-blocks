/**
 * obsidian-render-cache — Phase 9 cache status modal + pure aggregator.
 *
 * AC9.4: Run "Show cache status" → modal displays count, total disk size,
 * per-language breakdown.
 *
 * Pure aggregation (`aggregateStatus`) is unit-tested. The modal class itself
 * is smoke-tested at the user gate.
 */
import { App, Modal } from "obsidian";

interface BlockEntryShape {
  language: string;
  outputBytes: number;
  cachePath: string;
  lastError?: string | null;
}

interface IndexShape {
  notes: Record<string, { blocks: BlockEntryShape[] }>;
  preambleHashes?: Record<string, string>;
  schemaVersion?: number;
  rendererVersion?: string;
}

export interface PerLanguageStat {
  language: string;
  count: number;
  bytes: number;
}

export interface CacheStatus {
  totalNotes: number;
  totalBlocks: number;
  totalBytes: number;
  perLanguage: PerLanguageStat[];
  errorCount: number;
  schemaVersion?: number;
  rendererVersion?: string;
}

export interface NoteCacheStatus {
  totalBlocks: number;
  errorCount: number;
}

/** Aggregate counts/bytes/per-language from a parsed index.json.
 *  Pure: no I/O, no Obsidian deps. */
export function aggregateStatus(index: IndexShape | null): CacheStatus {
  if (!index || !index.notes) {
    return {
      totalNotes: 0,
      totalBlocks: 0,
      totalBytes: 0,
      perLanguage: [],
      errorCount: 0,
      schemaVersion: index?.schemaVersion,
      rendererVersion: index?.rendererVersion,
    };
  }

  const notes = Object.values(index.notes);
  const totalNotes = notes.length;

  let totalBlocks = 0;
  let totalBytes = 0;
  let errorCount = 0;
  const langMap: Record<string, { count: number; bytes: number }> = {};

  for (const note of notes) {
    for (const b of note.blocks ?? []) {
      totalBlocks += 1;
      totalBytes += b.outputBytes ?? 0;
      if (b.lastError) errorCount += 1;
      const lang = b.language || "unknown";
      if (!langMap[lang]) langMap[lang] = { count: 0, bytes: 0 };
      langMap[lang].count += 1;
      langMap[lang].bytes += b.outputBytes ?? 0;
    }
  }

  const perLanguage: PerLanguageStat[] = Object.entries(langMap)
    .map(([language, v]) => ({ language, count: v.count, bytes: v.bytes }))
    .sort((a, b) => b.count - a.count); // descending by count

  return {
    totalNotes,
    totalBlocks,
    totalBytes,
    perLanguage,
    errorCount,
    schemaVersion: index.schemaVersion,
    rendererVersion: index.rendererVersion,
  };
}

/** Aggregate cache state for a single note. Pure: no Obsidian deps. */
export function aggregateNoteStatus(
  index: IndexShape | null,
  sourcePath: string | null,
): NoteCacheStatus {
  if (!index || !index.notes || !sourcePath) {
    return { totalBlocks: 0, errorCount: 0 };
  }
  const note = index.notes[sourcePath];
  if (!note) return { totalBlocks: 0, errorCount: 0 };

  let totalBlocks = 0;
  let errorCount = 0;
  for (const block of note.blocks ?? []) {
    totalBlocks += 1;
    if (block.lastError) errorCount += 1;
  }
  return { totalBlocks, errorCount };
}

/** Text for the status-bar item (SPEC AC10.3). */
export function statusBarText(
  status: NoteCacheStatus,
  isRendering: boolean,
): string {
  if (isRendering) {
    return status.totalBlocks > 0
      ? `rendering 1/${status.totalBlocks}…`
      : "rendering…";
  }
  if (status.errorCount > 0) {
    return `⚠ ${status.errorCount} failed`;
  }
  if (status.totalBlocks > 0) {
    return `✓ ${status.totalBlocks} item${status.totalBlocks === 1 ? "" : "s"}`;
  }
  return "no cache";
}

/** Format bytes as a human-readable string (KiB/MiB). Pure. */
export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KiB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MiB`;
}

export class CacheStatusModal extends Modal {
  private readonly status: CacheStatus;

  constructor(app: App, status: CacheStatus) {
    super(app);
    this.status = status;
  }

  onOpen(): void {
    const { contentEl } = this;
    contentEl.empty();
    contentEl.createEl("h2", { text: "Render Cache — status" });

    const summary = contentEl.createEl("div", { cls: "render-cache-summary" });
    summary.createEl("p", {
      text:
        `${this.status.totalBlocks} block(s) cached across ` +
        `${this.status.totalNotes} note(s); ` +
        `${formatBytes(this.status.totalBytes)} total on disk.`,
    });
    if (this.status.errorCount > 0) {
      summary.createEl("p", {
        text: `${this.status.errorCount} block(s) have a captured render error.`,
        cls: "render-cache-error-note",
      });
    }
    if (this.status.rendererVersion) {
      summary.createEl("p", {
        text: `Renderer version: ${this.status.rendererVersion}, schema v${this.status.schemaVersion ?? "?"}`,
        cls: "render-cache-meta",
      });
    }

    contentEl.createEl("h3", { text: "Per language" });
    if (this.status.perLanguage.length === 0) {
      contentEl.createEl("p", { text: "(empty cache)" });
    } else {
      const table = contentEl.createEl("table", { cls: "render-cache-table" });
      const head = table.createEl("tr");
      head.createEl("th", { text: "Language" });
      head.createEl("th", { text: "Blocks" });
      head.createEl("th", { text: "Disk" });
      for (const row of this.status.perLanguage) {
        const tr = table.createEl("tr");
        tr.createEl("td", { text: row.language });
        tr.createEl("td", { text: String(row.count) });
        tr.createEl("td", { text: formatBytes(row.bytes) });
      }
    }
  }

  onClose(): void {
    this.contentEl.empty();
  }
}
