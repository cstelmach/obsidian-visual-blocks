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
  effectiveMode,
  isPlaceholderClickable,
  missMessage,
  nextMode,
} from "../src/settings";

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
  it("has exactly the 5 documented keys", () => {
    expect(Object.keys(DEFAULT_SETTINGS).sort()).toEqual([
      "mode",
      "pythonPath",
      "scriptPath",
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

  it("default triggerOnSave is true (SPEC-recommended)", () => {
    expect(DEFAULT_SETTINGS.triggerOnSave).toBe(true);
  });

  it("default useLoginShell is true (macOS PATH inheritance)", () => {
    expect(DEFAULT_SETTINGS.useLoginShell).toBe(true);
  });
});
