/**
 * Pure-function tests for src/cacheStatus.ts aggregator + formatter.
 * The modal class itself is smoke-tested at the user gate.
 */
import { aggregateStatus, formatBytes } from "../src/cacheStatus";

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
      { language: "tikz", count: 2, bytes: 3000 },
      { language: "d2", count: 1, bytes: 500 },
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
