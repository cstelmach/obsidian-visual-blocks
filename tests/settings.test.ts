/**
 * Pure-function unit tests for src/settings.ts.
 * Covers: nextMode (cycle), effectiveMode (mobile auto-override),
 * missMessage (5 cases), isPlaceholderClickable (4 cases),
 * DEFAULT_SETTINGS shape.
 *
 * The Obsidian SettingTab class itself is smoke-tested at the user gate.
 */
import {
  DEFAULT_SETTINGS,
  MODE_CYCLE,
  RenderMode,
  cacheRootPath,
  effectiveMode,
  indexPath,
  isPlaceholderClickable,
  missMessage,
  nextMode,
  normalizeSettings,
} from "../src/settings";
import { DEFAULT_ENABLED_LANGUAGES } from "../src/languages";

describe("nextMode (mode cycle)", () => {
  it("cycles hybrid → cache-only → live → hybrid", () => {
    expect(nextMode("hybrid")).toBe("cache-only");
    expect(nextMode("cache-only")).toBe("live");
    expect(nextMode("live")).toBe("hybrid");
  });

  it("returns hybrid for unknown input (defensive)", () => {
    expect(nextMode("garbage" as unknown as RenderMode)).toBe("hybrid");
  });

  it("MODE_CYCLE has exactly 3 modes in the SPEC-stated order", () => {
    expect([...MODE_CYCLE]).toEqual(["hybrid", "cache-only", "live"]);
  });
});

describe("effectiveMode (mobile auto-override AC9.9)", () => {
  it("respects setting on desktop", () => {
    expect(effectiveMode({ ...DEFAULT_SETTINGS, mode: "hybrid" }, false)).toBe(
      "hybrid",
    );
    expect(
      effectiveMode({ ...DEFAULT_SETTINGS, mode: "cache-only" }, false),
    ).toBe("cache-only");
    expect(effectiveMode({ ...DEFAULT_SETTINGS, mode: "live" }, false)).toBe(
      "live",
    );
  });

  it("forces cache-only on mobile regardless of setting (AC9.9)", () => {
    expect(effectiveMode({ ...DEFAULT_SETTINGS, mode: "hybrid" }, true)).toBe(
      "cache-only",
    );
    expect(effectiveMode({ ...DEFAULT_SETTINGS, mode: "live" }, true)).toBe(
      "cache-only",
    );
    expect(
      effectiveMode({ ...DEFAULT_SETTINGS, mode: "cache-only" }, true),
    ).toBe("cache-only");
  });
});

describe("missMessage", () => {
  it("mobile: 'open on desktop'", () => {
    expect(missMessage("cache-only", "tikz", true)).toBe(
      "tikz: Cache miss — open on desktop to render.",
    );
  });

  it("desktop cache-only: 'switch mode'", () => {
    expect(missMessage("cache-only", "d2", false)).toBe(
      "d2: Cache miss — cache-only mode; switch to hybrid or live to render.",
    );
  });

  it("desktop hybrid: 'click to render'", () => {
    expect(missMessage("hybrid", "graphviz", false)).toBe(
      "graphviz: Cache miss — click to render.",
    );
  });

  it("desktop live: 'click to render'", () => {
    expect(missMessage("live", "lilypond", false)).toBe(
      "lilypond: Cache miss — click to render.",
    );
  });

  it("preserves the lang argument verbatim", () => {
    expect(missMessage("hybrid", "smiles", false)).toContain("smiles:");
  });
});

describe("isPlaceholderClickable", () => {
  it("never clickable on mobile", () => {
    expect(isPlaceholderClickable("hybrid", true)).toBe(false);
    expect(isPlaceholderClickable("live", true)).toBe(false);
    expect(isPlaceholderClickable("cache-only", true)).toBe(false);
  });

  it("clickable on desktop in hybrid + live, not in cache-only", () => {
    expect(isPlaceholderClickable("hybrid", false)).toBe(true);
    expect(isPlaceholderClickable("live", false)).toBe(true);
    expect(isPlaceholderClickable("cache-only", false)).toBe(false);
  });
});

describe("DEFAULT_SETTINGS shape", () => {
  it("has exactly the documented keys", () => {
    expect(Object.keys(DEFAULT_SETTINGS).sort()).toEqual([
      "autoRefreshOnStartup",
      "cacheRootPath",
      "enabledLanguages",
      "mode",
      "pythonPath",
      "scriptPath",
      "startupRefreshDelaySeconds",
      "startupRefreshLastRunAt",
      "startupRefreshMinIntervalHours",
      "triggerOnSave",
      "useLoginShell",
    ]);
  });

  it("default mode is hybrid (SPEC-recommended)", () => {
    expect(DEFAULT_SETTINGS.mode).toBe("hybrid");
  });

  it("default pythonPath is python3 (works via login shell)", () => {
    expect(DEFAULT_SETTINGS.pythonPath).toBe("python3");
  });

  it("default scriptPath is the canonical render_cache.py location", () => {
    expect(DEFAULT_SETTINGS.scriptPath).toBe(
      "resources/scripts/python_single/render_cache.py",
    );
  });

  it("default cacheRootPath is the sync-friendly vault data folder", () => {
    expect(DEFAULT_SETTINGS.cacheRootPath).toBe(
      "resources/data/cache/visual-blocks",
    );
  });

  it("default triggerOnSave is true (SPEC-recommended)", () => {
    expect(DEFAULT_SETTINGS.triggerOnSave).toBe(true);
  });

  it("default useLoginShell is true (macOS PATH inheritance)", () => {
    expect(DEFAULT_SETTINGS.useLoginShell).toBe(true);
  });

  it("startup auto-refresh is opt-in with a 5 minute delay and 6 hour cooldown", () => {
    expect(DEFAULT_SETTINGS.autoRefreshOnStartup).toBe(false);
    expect(DEFAULT_SETTINGS.startupRefreshDelaySeconds).toBe(300);
    expect(DEFAULT_SETTINGS.startupRefreshMinIntervalHours).toBe(6);
    expect(DEFAULT_SETTINGS.startupRefreshLastRunAt).toBeNull();
  });

  it("defaults every visualization library to enabled", () => {
    expect(DEFAULT_SETTINGS.enabledLanguages).toEqual(DEFAULT_ENABLED_LANGUAGES);
  });
});

describe("normalizeSettings", () => {
  it("fills enabledLanguages for older saved settings", () => {
    const normalized = normalizeSettings({
      mode: "cache-only",
      pythonPath: "/tmp/python",
    });
    expect(normalized.mode).toBe("cache-only");
    expect(normalized.pythonPath).toBe("/tmp/python");
    expect(normalized.enabledLanguages).toEqual(DEFAULT_ENABLED_LANGUAGES);
  });

  it("fills missing language keys with true", () => {
    const normalized = normalizeSettings({
      enabledLanguages: { lilypond: false },
    } as unknown as Partial<typeof DEFAULT_SETTINGS>);
    expect(normalized.enabledLanguages).toEqual({
      ...DEFAULT_ENABLED_LANGUAGES,
      lilypond: false,
    });
  });

  it("ignores unknown persisted language keys", () => {
    const normalized = normalizeSettings({
      enabledLanguages: {
        lilypond: false,
        mermaid: false,
      },
    } as unknown as Partial<typeof DEFAULT_SETTINGS>);
    expect(Object.keys(normalized.enabledLanguages).sort()).toEqual([
      "d2",
      "graphviz",
      "lilypond",
      "smiles",
      "tikz",
    ]);
    expect(normalized.enabledLanguages.lilypond).toBe(false);
  });

  it("preserves a valid vault-relative cacheRootPath", () => {
    const normalized = normalizeSettings({
      cacheRootPath: "resources/data/cache/custom-visual-blocks",
    });
    expect(normalized.cacheRootPath).toBe(
      "resources/data/cache/custom-visual-blocks",
    );
  });

  it("normalizes slashes and trims a valid cacheRootPath", () => {
    const normalized = normalizeSettings({
      cacheRootPath: " resources\\\\data//cache/visual-blocks/ ",
    });
    expect(normalized.cacheRootPath).toBe(
      "resources/data/cache/visual-blocks",
    );
  });

  it("rejects empty, absolute, and parent-traversing cacheRootPath values", () => {
    expect(normalizeSettings({ cacheRootPath: "" }).cacheRootPath).toBe(
      DEFAULT_SETTINGS.cacheRootPath,
    );
    expect(normalizeSettings({ cacheRootPath: "/tmp/cache" }).cacheRootPath).toBe(
      DEFAULT_SETTINGS.cacheRootPath,
    );
    expect(
      normalizeSettings({ cacheRootPath: "resources/../cache" }).cacheRootPath,
    ).toBe(DEFAULT_SETTINGS.cacheRootPath);
  });
});

describe("cache path helpers", () => {
  it("derives cache root and index path from settings", () => {
    const settings = normalizeSettings({
      cacheRootPath: "resources/data/cache/custom-visual-blocks",
    });
    expect(cacheRootPath(settings)).toBe(
      "resources/data/cache/custom-visual-blocks",
    );
    expect(indexPath(settings)).toBe(
      "resources/data/cache/custom-visual-blocks/index.json",
    );
  });
});
