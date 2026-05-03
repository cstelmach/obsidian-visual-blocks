/**
 * Pure-function tests for src/cacheStatus.ts aggregator + formatter.
 * The modal class itself is smoke-tested at the user gate.
 */
import {
  aggregateNoteStatus,
  aggregateStatus,
  formatBytes,
  statusBarText,
} from "../src/cacheStatus";
import { DEFAULT_ENABLED_LANGUAGES } from "../src/languages";

describe("formatBytes", () => {
  it("returns plain bytes for small values", () => {
    expect(formatBytes(0)).toBe("0 B");
    expect(formatBytes(1023)).toBe("1023 B");
  });

  it("returns KiB at 1024+", () => {
    expect(formatBytes(1024)).toBe("1.0 KiB");
    expect(formatBytes(2560)).toBe("2.5 KiB");
  });

  it("returns MiB at 1024² and above", () => {
    expect(formatBytes(1024 * 1024)).toBe("1.00 MiB");
    expect(formatBytes(8.6 * 1024 * 1024)).toBe("8.60 MiB");
  });
});

describe("aggregateNoteStatus", () => {
  it("returns an empty note status for missing index or missing path", () => {
    expect(aggregateNoteStatus(null, "a.md")).toEqual({
      totalBlocks: 0,
      errorCount: 0,
      disabledBlocks: 0,
    });
    expect(aggregateNoteStatus({ notes: {} }, "a.md")).toEqual({
      totalBlocks: 0,
      errorCount: 0,
      disabledBlocks: 0,
    });
  });

  it("counts blocks and errors for one note only", () => {
    const index = {
      notes: {
        "a.md": {
          blocks: [
            { language: "tikz", outputBytes: 100, cachePath: "x" },
            {
              language: "d2",
              outputBytes: 0,
              cachePath: "y",
              lastError: "d2 failed",
            },
          ],
        },
        "b.md": {
          blocks: [
            {
              language: "smiles",
              outputBytes: 0,
              cachePath: "z",
              lastError: "invalid smiles",
            },
          ],
        },
      },
    };
    expect(aggregateNoteStatus(index, "a.md", DEFAULT_ENABLED_LANGUAGES)).toEqual({
      totalBlocks: 2,
      errorCount: 1,
      disabledBlocks: 0,
    });
  });

  it("excludes disabled languages from displayable note totals", () => {
    const index = {
      notes: {
        "a.md": {
          blocks: [
            { language: "lilypond", outputBytes: 100, cachePath: "x" },
            { language: "d2", outputBytes: 200, cachePath: "y" },
          ],
        },
      },
    };
    expect(
      aggregateNoteStatus(index, "a.md", {
        ...DEFAULT_ENABLED_LANGUAGES,
        lilypond: false,
      }),
    ).toEqual({
      totalBlocks: 1,
      errorCount: 0,
      disabledBlocks: 1,
    });
  });
});

describe("statusBarText", () => {
  it("shows no-cache state for notes without cached blocks", () => {
    expect(statusBarText({ totalBlocks: 0, errorCount: 0, disabledBlocks: 0 }, false)).toBe(
      "no cache",
    );
  });

  it("shows idle item count when the current note has cached blocks", () => {
    expect(statusBarText({ totalBlocks: 3, errorCount: 0, disabledBlocks: 0 }, false)).toBe(
      "✓ 3 items",
    );
    expect(statusBarText({ totalBlocks: 1, errorCount: 0, disabledBlocks: 0 }, false)).toBe(
      "✓ 1 item",
    );
  });

  it("prioritizes captured render errors over idle state", () => {
    expect(statusBarText({ totalBlocks: 3, errorCount: 1, disabledBlocks: 0 }, false)).toBe(
      "⚠ 1 failed",
    );
    expect(statusBarText({ totalBlocks: 3, errorCount: 2, disabledBlocks: 0 }, false)).toBe(
      "⚠ 2 failed",
    );
  });

  it("shows rendering progress when the active note is being rendered", () => {
    expect(statusBarText({ totalBlocks: 5, errorCount: 0, disabledBlocks: 0 }, true)).toBe(
      "rendering 1/5…",
    );
    expect(statusBarText({ totalBlocks: 0, errorCount: 0, disabledBlocks: 0 }, true)).toBe(
      "rendering…",
    );
  });

  it("shows disabled-block state when only disabled cached blocks exist", () => {
    expect(statusBarText({ totalBlocks: 0, errorCount: 0, disabledBlocks: 2 }, false)).toBe(
      "2 disabled blocks",
    );
  });
});

describe("aggregateStatus", () => {
  it("returns zeros for null/empty index", () => {
    const s = aggregateStatus(null);
    expect(s.totalNotes).toBe(0);
    expect(s.totalBlocks).toBe(0);
    expect(s.totalBytes).toBe(0);
    expect(s.perLanguage).toEqual([]);
    expect(s.errorCount).toBe(0);
  });

  it("counts notes/blocks/bytes correctly", () => {
    const index = {
      notes: {
        "a.md": {
          blocks: [
            { language: "tikz", outputBytes: 50000, cachePath: "x" },
            { language: "tikz", outputBytes: 30000, cachePath: "y" },
          ],
        },
        "b.md": {
          blocks: [{ language: "d2", outputBytes: 10000, cachePath: "z" }],
        },
      },
    };
    const s = aggregateStatus(index);
    expect(s.totalNotes).toBe(2);
    expect(s.totalBlocks).toBe(3);
    expect(s.totalBytes).toBe(90000);
  });

  it("groups per-language with counts and bytes, descending by count", () => {
    const index = {
      notes: {
        "a.md": {
          blocks: [
            { language: "tikz", outputBytes: 1000, cachePath: "x" },
            { language: "tikz", outputBytes: 2000, cachePath: "y" },
            { language: "d2", outputBytes: 500, cachePath: "z" },
          ],
        },
      },
    };
    const s = aggregateStatus(index);
    expect(s.perLanguage).toEqual([
      { language: "tikz", count: 2, bytes: 3000, enabled: true },
      { language: "d2", count: 1, bytes: 500, enabled: true },
    ]);
  });

  it("marks disabled languages in the per-language cache table data", () => {
    const index = {
      notes: {
        "a.md": {
          blocks: [
            { language: "lilypond", outputBytes: 1000, cachePath: "x" },
            { language: "d2", outputBytes: 2000, cachePath: "y" },
          ],
        },
      },
    };
    const s = aggregateStatus(index, {
      ...DEFAULT_ENABLED_LANGUAGES,
      lilypond: false,
    });
    expect(s.perLanguage).toEqual([
      { language: "lilypond", count: 1, bytes: 1000, enabled: false },
      { language: "d2", count: 1, bytes: 2000, enabled: true },
    ]);
  });

  it("counts blocks with lastError", () => {
    const index = {
      notes: {
        "a.md": {
          blocks: [
            { language: "tikz", outputBytes: 100, cachePath: "x" },
            {
              language: "tikz",
              outputBytes: 0,
              cachePath: "y",
              lastError: "boom",
            },
            {
              language: "d2",
              outputBytes: 50,
              cachePath: "z",
              lastError: "kaboom",
            },
          ],
        },
      },
    };
    const s = aggregateStatus(index);
    expect(s.errorCount).toBe(2);
    // Errored blocks still count toward total
    expect(s.totalBlocks).toBe(3);
  });

  it("treats missing language as 'unknown'", () => {
    const index = {
      notes: {
        "a.md": {
          blocks: [{ language: "", outputBytes: 100, cachePath: "x" }],
        },
      },
    };
    const s = aggregateStatus(index);
    expect(s.perLanguage[0].language).toBe("unknown");
  });

  it("handles missing outputBytes (treats as 0)", () => {
    const index = {
      notes: {
        "a.md": {
          blocks: [
            { language: "tikz", cachePath: "x" } as unknown as {
              language: string;
              outputBytes: number;
              cachePath: string;
            },
          ],
        },
      },
    };
    const s = aggregateStatus(index);
    expect(s.totalBytes).toBe(0);
    expect(s.totalBlocks).toBe(1);
  });

  it("propagates schemaVersion and rendererVersion when present", () => {
    const index = {
      notes: {},
      schemaVersion: 1,
      rendererVersion: "0.2.0",
    };
    const s = aggregateStatus(index);
    expect(s.schemaVersion).toBe(1);
    expect(s.rendererVersion).toBe("0.2.0");
  });
});
