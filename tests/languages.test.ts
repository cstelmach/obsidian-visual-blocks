import {
  DEFAULT_ENABLED_LANGUAGES,
  VISUAL_BLOCK_LANGUAGES,
  buildLanguageFilterArgs,
  canonicalizeFenceLanguage,
  enabledLanguageIds,
  hasEnabledSupportedBlock,
  isLanguageEnabled,
  isSupportedFenceLanguage,
  languageLabel,
} from "../src/languages";

describe("Visual Blocks language metadata", () => {
  it("defines the five canonical renderer languages in stable order", () => {
    expect(VISUAL_BLOCK_LANGUAGES.map((l) => l.id)).toEqual([
      "tikz",
      "graphviz",
      "d2",
      "lilypond",
      "smiles",
    ]);
  });

  it("treats tikz-paused as the tikz language toggle", () => {
    expect(canonicalizeFenceLanguage("tikz-paused")).toBe("tikz");
    expect(canonicalizeFenceLanguage("tikz")).toBe("tikz");
  });

  it("recognizes supported fence aliases and rejects unrelated fences", () => {
    expect(isSupportedFenceLanguage("lilypond")).toBe(true);
    expect(isSupportedFenceLanguage("tikz-paused")).toBe(true);
    expect(isSupportedFenceLanguage("mermaid")).toBe(false);
    expect(isSupportedFenceLanguage("python")).toBe(false);
  });

  it("defaults every language to enabled", () => {
    expect(DEFAULT_ENABLED_LANGUAGES).toEqual({
      tikz: true,
      graphviz: true,
      d2: true,
      lilypond: true,
      smiles: true,
    });
  });

  it("filters enabled language ids in canonical order", () => {
    const enabled = {
      ...DEFAULT_ENABLED_LANGUAGES,
      lilypond: false,
      graphviz: false,
    };
    expect(enabledLanguageIds(enabled)).toEqual(["tikz", "d2", "smiles"]);
  });

  it("uses the tikz toggle for tikz-paused aliases", () => {
    const enabled = { ...DEFAULT_ENABLED_LANGUAGES, tikz: false };
    expect(isLanguageEnabled(enabled, "tikz")).toBe(false);
    expect(isLanguageEnabled(enabled, "tikz-paused")).toBe(false);
    expect(isLanguageEnabled(enabled, "d2")).toBe(true);
  });

  it("builds explicit --languages args for plugin-triggered Python renders", () => {
    expect(
      buildLanguageFilterArgs({
        ...DEFAULT_ENABLED_LANGUAGES,
        lilypond: false,
      }),
    ).toEqual(["--languages", "tikz,graphviz,d2,smiles"]);
  });

  it("returns null language-filter args when every language is disabled", () => {
    expect(
      buildLanguageFilterArgs({
        tikz: false,
        graphviz: false,
        d2: false,
        lilypond: false,
        smiles: false,
      }),
    ).toBeNull();
  });

  it("detects only enabled supported blocks in markdown source", () => {
    const text = [
      "```lilypond",
      "{ c'4 }",
      "```",
      "",
      "```d2",
      "a -> b",
      "```",
    ].join("\n");
    expect(
      hasEnabledSupportedBlock(text, {
        ...DEFAULT_ENABLED_LANGUAGES,
        lilypond: false,
      }),
    ).toBe(true);
    expect(
      hasEnabledSupportedBlock(text, {
        tikz: false,
        graphviz: false,
        d2: false,
        lilypond: false,
        smiles: false,
      }),
    ).toBe(false);
  });

  it("provides user-facing labels for disabled placeholders", () => {
    expect(languageLabel("lilypond")).toBe("LilyPond");
    expect(languageLabel("smiles")).toBe("SMILES");
  });
});
