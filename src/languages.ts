export const VISUAL_BLOCK_LANGUAGES = [
  {
    id: "tikz",
    label: "TikZ",
    settingsName: "TikZ diagrams",
    description: "LuaLaTeX + dvisvgm diagrams. Also controls tikz-paused blocks.",
    fences: ["tikz", "tikz-paused"],
  },
  {
    id: "graphviz",
    label: "Graphviz",
    settingsName: "Graphviz / DOT",
    description: "Graphviz dot diagrams rendered with dot -Tsvg.",
    fences: ["graphviz"],
  },
  {
    id: "d2",
    label: "D2",
    settingsName: "D2 diagrams",
    description: "D2 CLI diagrams rendered with the ELK layout.",
    fences: ["d2"],
  },
  {
    id: "lilypond",
    label: "LilyPond",
    settingsName: "LilyPond music notation",
    description: "Music notation rendered by the LilyPond SVG backend.",
    fences: ["lilypond"],
  },
  {
    id: "smiles",
    label: "SMILES",
    settingsName: "SMILES chemistry structures",
    description: "Chemistry structures drawn with RDKit from SMILES strings.",
    fences: ["smiles"],
  },
] as const;

export type LanguageId = (typeof VISUAL_BLOCK_LANGUAGES)[number]["id"];
export type EnabledLanguages = Record<LanguageId, boolean>;

export const DEFAULT_ENABLED_LANGUAGES: EnabledLanguages = {
  tikz: true,
  graphviz: true,
  d2: true,
  lilypond: true,
  smiles: true,
};

const FENCE_TO_LANGUAGE: Record<string, LanguageId> = {};
for (const lang of VISUAL_BLOCK_LANGUAGES) {
  for (const fence of lang.fences) {
    FENCE_TO_LANGUAGE[fence] = lang.id;
  }
}

export function canonicalizeFenceLanguage(fence: string): LanguageId | null {
  return FENCE_TO_LANGUAGE[fence.toLowerCase()] ?? null;
}

export function isSupportedFenceLanguage(fence: string): boolean {
  return canonicalizeFenceLanguage(fence) !== null;
}

export function normalizeEnabledLanguages(
  raw: unknown,
): EnabledLanguages {
  const out: EnabledLanguages = { ...DEFAULT_ENABLED_LANGUAGES };
  if (!raw || typeof raw !== "object") return out;
  const record = raw as Record<string, unknown>;
  for (const lang of VISUAL_BLOCK_LANGUAGES) {
    if (typeof record[lang.id] === "boolean") {
      out[lang.id] = record[lang.id] as boolean;
    }
  }
  return out;
}

export function enabledLanguageIds(enabled: EnabledLanguages): LanguageId[] {
  return VISUAL_BLOCK_LANGUAGES
    .map((l) => l.id)
    .filter((id) => enabled[id]);
}

export function isLanguageEnabled(
  enabled: EnabledLanguages,
  langOrFence: string,
): boolean {
  const canonical = canonicalizeFenceLanguage(langOrFence);
  if (!canonical) return true;
  return enabled[canonical];
}

export function buildLanguageFilterArgs(
  enabled: EnabledLanguages,
): string[] | null {
  const ids = enabledLanguageIds(enabled);
  if (ids.length === 0) return null;
  return ["--languages", ids.join(",")];
}

export function hasEnabledSupportedBlock(
  text: string,
  enabled: EnabledLanguages,
): boolean {
  for (const line of text.split("\n")) {
    const m = /^```(\w[\w-]*)\b/.exec(line);
    if (!m) continue;
    const lang = canonicalizeFenceLanguage(m[1]);
    if (lang && enabled[lang]) return true;
  }
  return false;
}

export function languageLabel(langOrFence: string): string {
  const canonical = canonicalizeFenceLanguage(langOrFence);
  if (!canonical) return langOrFence;
  return (
    VISUAL_BLOCK_LANGUAGES.find((l) => l.id === canonical)?.label ??
    canonical
  );
}
