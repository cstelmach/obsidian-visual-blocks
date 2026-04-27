# SPEC — Obsidian Render Cache

**Document version:** 0.1
**Date:** 2026-04-26
**Status:** DRAFT — pending user review
**Slug:** `render-cache`
**Predecessor:** `docs/specs/tikz-cache/` (TikZ-only PNG pipeline; absorbed by this SPEC)
**Research grounding:**
- `/tmp/gemini-research-tikzjax-foundation-20260426.md`
- `/tmp/gemini-research-obsidian-caching-mobile-20260426.md`
- `/tmp/gemini-research-rendering-alternatives-20260426.md`
- `/tmp/gemini-research-caching-architecture-20260426.md`
- `/tmp/gemini-research-universal-renderer-20260426.md`
- `/tmp/gemini-research-best-of-breed-tools-20260426.md`
- `/tmp/gemini-research-multilang-patterns-20260426.md`
- `/tmp/gemini-research-mobile-cacheable-formats-20260426.md`

---

## 0. Reader Orientation

This document is the design source-of-truth for a system that turns code-described
visualizations (TikZ, Graphviz, D2, LilyPond, RDKit/SMILES) inside an Obsidian
vault into **deterministic, hash-keyed, locally-rendered SVG files** that display
reliably on macOS desktop and iOS mobile, offline, with no in-app rendering on
mobile. The accompanying `PLAN.md` decomposes this into executable phases.

**Read this section first if you are landing cold.** §1 covers the motivation,
§2 defines goals/non-goals, §3 describes the architecture, §4 specifies the
cache schema, §5 catalogs the renderer commands, §6 specifies the plugin, §7
lists hardening rules that are mandatory, §8 lists acceptance criteria, §9
phases (high-level), §10 risks, §11 deferred questions.

---

## 1. Background and Motivation

### 1.1 The problem we are solving

The user maintains a personal Obsidian vault with hundreds of math/science
notes. Each note typically contains one or more code-described diagrams.
Today these are TikZ blocks rendered by the `obsidian-tikzjax` community
plugin (a WASM port of TeX with a custom DVI→SVG converter).

Three failure modes drove this SPEC:

1. **Mobile crashes.** iOS Obsidian crashes on notes with multiple complex
   TikZ blocks. The crash is a `WKWebView` memory eviction caused by the
   WASM TeX engine's allocation pattern. It is architectural; no setting
   on the existing plugin avoids it.
2. **Silent rendering failures.** Specific TikZ patterns (notably title
   nodes positioned at certain coordinates) silently fail in TikZJax
   because the plugin's `dvi2html` converter (NOT `dvisvgm`) produces
   degenerate SVG bounding boxes. No error reaches the user; the diagram
   just doesn't appear.
3. **Stale engine.** TikZJax bundles a TeX Live snapshot from approximately
   2020-02-02; `pgfplots` 1.18+ features fail. The toolchain that builds
   this WASM (`web2js`) has been abandoned since 2021-09-10.

### 1.2 The premise we explicitly rejected

The user initially considered forking and modernizing `obsidian-tikzjax`.
Eight web-research streams (saved in `/tmp/`) converged on the same answer:
**fork-and-modernize is the wrong move.** The actual silent-failure source
(`dvi2html`) is custom JS, not the TeX engine; even a successful WASM
bundle bump would not fix the rendering bugs. The Pascal→WASM compiler
that builds the TeX bundle has been dead three years.

Cost/benefit:
- Medium fork (rebuild WASM, bump TeX Live, bundle more packages): 150–250+ hours.
- The user's existing Python `tikz_cache.py` already produces higher-fidelity
  output via native `lualatex` than any WASM TeX bundle could.

The right move is to make the native pipeline the canonical renderer, give
it a proper Obsidian-side viewer plugin, and make it multi-language.

### 1.3 The premise we explicitly rejected next

The user then asked whether a single newer engine (Typst, SwiftLaTeX, etc.)
might replace the entire LaTeX dependency. Research again: **no single
universal engine exists.**

- LaTeX + TikZ family covers 11–13 of 16 plausible domains at production quality.
- Typst is pre-1.0, has immature chemistry/circuits packages, no auto-converter
  from existing TikZ source. Migration cost is high; payoff is unclear.
- SwiftLaTeX (gboyd068's plugin) is GPL-3 and architecturally puts the
  compiler in the preview layer — opposite of our model. Low GitHub stars
  (18) and original SwiftLaTeX upstream stale since 2022.
- Quarto/Pandoc-with-filters are dispatchers that themselves shell out to
  LaTeX; using them adds a layer without removing the LaTeX dependency.

The right move is to **stay with LuaLaTeX+TikZ as the workhorse engine** and
add a small whitelist of supplementary CLI tools for what TikZ cannot do
naturally (music notation, force-directed graph layouts, declarative
diagrams).

### 1.4 What "done" looks like

When this SPEC is implemented:

- The user runs `python3 render_cache.py FILE.md` (or the plugin auto-triggers
  on save) and any code-described diagram in the file becomes a cached SVG.
- The cached SVG appears inline on desktop, edited in source mode shows the
  original code block, edits invalidate the cache automatically via hash.
- On iOS mobile, the same cached SVG appears inline. Nothing is rendered;
  no WASM runs. The note opens fast, does not crash.
- TikZ silent failures (title-node bug, etc.) do not exist because we use
  native `lualatex` + `dvisvgm`, not the broken `dvi2html`.
- Graphviz, D2, LilyPond, and SMILES code blocks render the same way in v1.

---

## 2. Goals, Non-Goals, and Constraints

### 2.1 Must-Have (v1 Goals)

1. **Multi-language render-at-save** for TikZ, Graphviz, D2, LilyPond, RDKit
   (SMILES). Mermaid is excluded because Obsidian core renders it natively
   and adding a parallel pipeline would conflict.
2. **SVG as primary cache format** (not PNG). All renderers must produce
   SVG either natively or via `dvisvgm`. WebP is the raster fallback when
   SVG is impossible.
3. **Hash-based cache invalidation** with deterministic content-addressing.
   Cache key includes language + render attributes + global preamble hash.
4. **Mobile-safe display.** Cached SVG renders correctly in iOS Obsidian
   without any in-app rendering, no WASM, no crashes.
5. **Plugin with three modes**: hybrid (default), cache-only (forced on
   mobile), live (re-render every load on desktop).
6. **Plugin commands**: refresh-this-block, refresh-this-note, refresh-vault,
   show-cache-status, sweep-orphans, toggle-mode.
7. **Renderer hardening** for known failure modes (see §7).
8. **Single source of truth**: Python is canonical; plugin reads only.

### 2.2 Explicit Non-Goals (v1)

1. **Live mobile rendering.** No WASM TeX or SwiftLaTeX in v1. Mobile is
   view-from-cache only.
2. **Programmatic animations.** Manim, motion-canvas, Lottie, p5.js, and
   similar are not handled by v1. Animations on iOS Obsidian are
   architecturally fragile (autoplay blocked under Low Power Mode, sync
   cost prohibitive at vault scale). Future SPEC may define a separate
   "media pipeline."
3. **Replacing LaTeX with Typst.** Typst is monitored for future
   consideration; no v1 work toward migration.
4. **Adopting SwiftLaTeX or gboyd068/obsidian-swiftlatex-render.**
   GPL-3 license, low community traction, architectural mismatch. Deferred
   to optional fallback evaluation only if the v1 pipeline proves
   insufficient (see §10.4).
5. **Build-time/CI pipeline.** No GitHub Actions, no scheduled batch jobs.
   Manual CLI + plugin-triggered render only.
6. **PlantUML, Vega-Lite, 3Dmol.js.** Not in v1 whitelist. Future
   consideration.
7. **Per-note configuration files.** Frontmatter or per-block fence options
   only.
8. **Custom DSL or new language.** Use existing languages; do not invent.
9. **Replacing Mermaid in Obsidian.** Mermaid stays native; we do not
   render it.

### 2.3 Hard Constraints

1. **Offline-first.** All rendering happens on the user's machine. No cloud
   APIs (quicklatex.com, latex2image, etc.).
2. **Cross-device.** Vault is used on macOS desktop AND iOS mobile.
   Solutions that only work on one platform are unacceptable.
3. **Existing source preserved.** TikZ and other code blocks remain in the
   Markdown file unchanged. Only an `![[...]]` image reference is appended;
   no fence rewriting (lesson from `tikz-cache` Phase 4: user rejected
   `tikz-paused` mechanism).
4. **Backward-compatible with existing tikz-cache work.** Existing 5 PNG
   cache files at `attachments/cache/tikz/` and their markdown references
   must continue to display correctly during the migration window. After
   migration, they become orphans and are swept.
5. **Vault size budget.** Cache total at 600-block scale must stay under
   ~150 MB (SVG) — the format-policy choice; PNG would be ~2.4 GB and is
   rejected.

---

## 3. Architecture

### 3.1 Pipeline diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│  AUTHOR-TIME (desktop only)                                              │
│                                                                          │
│   ┌──────────────────┐                                                   │
│   │ User edits .md   │                                                   │
│   └────────┬─────────┘                                                   │
│            │ save event OR manual CLI:                                   │
│            │ python3 render_cache.py FILE.md                             │
│            ▼                                                             │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  render_cache.py  (Python, evolution of tikz_cache.py)            │  │
│   │                                                                   │  │
│   │  1. Parse fences:  ```tikz / ```graphviz / ```d2 /                │  │
│   │                    ```lilypond / ```smiles                        │  │
│   │  2. Normalize source (whitespace, comments, line endings)         │  │
│   │  3. Compute hash key (see §4.2)                                   │  │
│   │  4. Lookup index.json by (note_path, block_idx, hash)             │  │
│   │  5. If MISS: dispatch to language adapter                         │  │
│   │     ├── tikz       → lualatex+dvisvgm (with hardening flags)      │  │
│   │     ├── graphviz   → dot -Tsvg                                    │  │
│   │     ├── d2         → d2 CLI                                       │  │
│   │     ├── lilypond   → lilypond -dpoint-and-click=#f -dbackend=svg  │  │
│   │     └── smiles     → RDKit (Python lib, no shell)                 │  │
│   │  6. Post-process SVG (see §7):                                    │  │
│   │     ID-prefix → currentColor → viewBox → SVGO conservative        │  │
│   │  7. Write SVG to .obsidian/plugins/obsidian-render-cache/         │  │
│   │       cache/v1/<note-path>/<idx>__<hash16>.svg                    │  │
│   │  8. Update cache/index.json                                       │  │
│   │  9. Insert/update ![[…|render-cache]] image reference in source .md│  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  VIEW-TIME (desktop or mobile)                                           │
│                                                                          │
│   ┌──────────────────┐                                                   │
│   │ Open note in     │                                                   │
│   │ Obsidian         │                                                   │
│   └────────┬─────────┘                                                   │
│            ▼                                                             │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  Plugin: obsidian-render-cache (TypeScript)                       │  │
│   │                                                                   │  │
│   │  registerMarkdownCodeBlockProcessor for each language:            │  │
│   │     ├── 'tikz'   ──┐                                              │  │
│   │     ├── 'graphviz'─┤   each calls displayCachedBlock(             │  │
│   │     ├── 'd2'    ───┤      source, lang, idx, ctx)                 │  │
│   │     ├── 'lilypond'─┤                                              │  │
│   │     └── 'smiles' ──┘                                              │  │
│   │                                                                   │  │
│   │  displayCachedBlock:                                              │  │
│   │     1. hash = computeHash(source, lang, attrs, preambleHash)      │  │
│   │     2. entry = index.notes[notePath]?.find(blockIdx + hash match) │  │
│   │     3. if entry && file exists:                                   │  │
│   │           inject <img src=getResourcePath(entry.cachePath)>       │  │
│   │     4. else (cache miss):                                         │  │
│   │           desktop: placeholder "Render needed (click to trigger)" │  │
│   │           mobile:  placeholder "Open on desktop to render"        │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│   Result: SVG visible inline. Source code block remains in markdown,    │
│   visible in source mode, hidden in reading mode by codeblock processor │
│   (which replaces it with the SVG).                                     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Architectural decisions log

These decisions are LOCKED. Re-litigation requires a new SPEC.

| # | Decision | Why |
|---|----------|-----|
| 3.2.1 | Render-at-save (Path C), not in-plugin rendering (Path A or B) | iOS sandboxing forbids native binaries; WASM TeX is unmaintained; native renderers produce higher fidelity; offline-first |
| 3.2.2 | Python `render_cache.py` is canonical writer; plugin reads only | Python pipeline already works (`tikz_cache.py`); avoids re-implementing render orchestration in TypeScript; clear ownership |
| 3.2.3 | LuaLaTeX + TikZ stays as primary engine | Covers ~80% of domains already; Typst not yet mature enough; user has it installed |
| 3.2.4 | v1 language whitelist: TikZ + Graphviz + D2 + LilyPond + RDKit | 80/20 coverage per research; ~480 MB extra disk; each adapter ~30–50 LOC |
| 3.2.5 | Mermaid stays native (not in our pipeline) | Obsidian core renders it; parallel pipeline would conflict |
| 3.2.6 | SVG primary, with `dvisvgm --no-fonts` mandatory | iOS WKWebView lacks Computer Modern; font-referenced SVG silently falls back to Times New Roman |
| 3.2.7 | Cache lives at `.obsidian/plugins/obsidian-render-cache/cache/`, not `attachments/` | iOS-friendly, hidden from indexer, Obsidian Sync excludes by default; per-note directory layout for orphan-cleanup ease |
| 3.2.8 | 16-char SHA-256 truncated hash | 4×10⁻¹⁵ collision rate at vault scale; readable filenames; matches Hugo precedent |
| 3.2.9 | Cache key includes lang + attrs + global_preamble_hash | Prevents cache poisoning when preamble changes; distinguishes same-source different-language ambiguity |
| 3.2.10 | Renderer version in directory path, not in hash | Clean GC across upgrades; old caches naturally segregated |
| 3.2.11 | Animations OUT OF SCOPE for v1 | iOS autoplay blocked under Low Power Mode; vault-size cost prohibitive |
| 3.2.12 | gboyd068/SwiftLaTeX hands-on eval DEFERRED to optional fallback phase | GPL-3 + low traction + stale upstream + architectural mismatch |

### 3.3 What lives where

```
/Users/cs/Obsidian/_/
├── kn/...                                 (markdown notes — unchanged scheme)
├── docs/specs/
│   ├── tikz-cache/                        (predecessor SPEC; historical)
│   └── render-cache/                      (this SPEC)
│       ├── SPEC.md
│       ├── PLAN.md
│       └── PROGRESS.md                    (created when implementation starts)
├── resources/scripts/python_single/
│   ├── tikz_cache.py                      (LEGACY — keep functional during migration)
│   └── render_cache.py                    (NEW canonical entry point)
├── resources/scripts/python_single/render_cache/
│   ├── __init__.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── tikz.py
│   │   ├── graphviz.py
│   │   ├── d2.py
│   │   ├── lilypond.py
│   │   └── smiles.py
│   ├── normalize.py                       (whitespace/comment/CRLF normalization)
│   ├── hash.py                            (cache key computation)
│   ├── index.py                           (index.json read/write)
│   ├── postprocess.py                     (SVG hardening)
│   ├── markdown_io.py                     (parse fences, insert image refs)
│   └── cache_paths.py                     (path construction utilities)
├── .obsidian/plugins/obsidian-render-cache/
│   ├── manifest.json
│   ├── main.js                            (plugin TypeScript bundle)
│   ├── styles.css
│   ├── data.json                          (plugin settings)
│   └── cache/
│       ├── index.json                     (cache index — see §4.3)
│       └── v1/                            (renderer version namespace)
│           └── <note-path>/<idx>__<hash16>.svg
└── .obsidian/snippets/
    └── render-cache.css                   (CSS for inline display)
```

The legacy `attachments/cache/tikz/` directory and its 5 PNGs are swept
during the migration phase. Existing markdown image references are
rewritten by the migration tool.

---

## 4. Cache Schema

### 4.1 Source normalization (mandatory before hashing)

The normalization pipeline ensures that visually-equivalent source variants
produce the same hash, eliminating cache thrash from trivial edits.

**Steps, in order:**

1. **Decode and unify line endings:** CRLF → LF, CR → LF.
2. **Strip trailing whitespace** from each line.
3. **Strip leading/trailing blank lines** of the entire block.
4. **Collapse runs of blank lines** of length ≥3 down to length 2.
5. **Strip LaTeX-style comments** (lines whose first non-whitespace char is
   `%`, with `\%` escaped). Applies only to TikZ. Other languages keep
   their comment conventions.
6. **Encode as UTF-8 bytes** for hashing.

The normalized source is **NOT** what gets rendered — the original raw
source goes to the renderer. Normalization affects only the cache key.

### 4.2 Cache key formula

```python
def cache_key(raw_source: str, lang: str, attrs: dict, preamble_hash: str) -> str:
    normalized = normalize(raw_source)
    payload = (
        normalized + b"\x00" +
        lang.encode("utf-8") + b"\x00" +
        json.dumps(attrs, sort_keys=True).encode("utf-8") + b"\x00" +
        preamble_hash.encode("utf-8")
    )
    return hashlib.sha256(payload).hexdigest()[:16]
```

- 16 hex chars = 64 bits; collision probability at 600 blocks ≈ 9.7×10⁻¹⁵.
- `attrs` is a dict of fence-tag attributes (e.g., `{"width": "400"}`).
  Empty dict for v1 (no per-block options yet).
- `preamble_hash` is the SHA-256 of the global TikZ preamble file (if it
  exists at `kn/math/concepts/_preamble.tikz` or similar). Empty string
  for languages that don't use a global preamble.
- Null bytes (`\x00`) separate fields; impossible in valid source so
  unambiguous.

### 4.3 Index file schema (`cache/index.json`)

```json
{
  "schemaVersion": 1,
  "rendererVersion": "1.0.0",
  "lastSweep": "2026-04-26T19:30:00Z",
  "preambleHashes": {
    "kn/math/concepts/_preamble.tikz": "f5a3c8e9d1234567"
  },
  "notes": {
    "kn/math/concepts/mSB5-2_partial.md": {
      "blocks": [
        {
          "blockIdx": 0,
          "language": "tikz",
          "sourceHash": "a1b2c3d4e5f67890",
          "cachePath": "v1/kn/math/concepts/mSB5-2_partial/0__a1b2c3d4e5f67890.svg",
          "renderedAt": "2026-04-26T19:25:14Z",
          "rendererVersion": "1.0.0",
          "outputFormat": "svg",
          "renderMs": 2103,
          "outputBytes": 408271
        }
      ]
    }
  }
}
```

- `schemaVersion` is bumped if this format ever changes; old indexes are
  migrated, not deleted.
- `rendererVersion` segregates caches per renderer release (see §4.5).
- `notes` is keyed by vault-relative POSIX path of the markdown file.
- `blocks` is ordered; `blockIdx` is the block's 0-based ordinal in the
  file (NOT the line number).
- `outputBytes` enables fast disk-usage reporting for the status command.

### 4.4 Cache directory layout

```
.obsidian/plugins/obsidian-render-cache/cache/
├── index.json                           ← global index
├── state.json                           ← plugin private state (last GC, etc.)
└── v1/                                  ← renderer version namespace
    ├── kn/math/concepts/                ← mirrors vault structure
    │   ├── mSB5-2_partial/
    │   │   └── 0__a1b2c3d4e5f67890.svg
    │   ├── mLA5-1_eigenvalues/
    │   │   ├── 0__1234567890abcdef.svg
    │   │   └── 1__fedcba0987654321.svg
    │   └── mSB3-5_complex/
    │       └── 0__9876543210fedcba.svg
    └── ...
```

**Path sanitization:** Note paths that include filesystem-unsafe chars
(spaces, colons in YAML, etc.) are URL-escaped. The escaped form goes in
`cachePath`; the raw form is the index key.

**Filename:** `<blockIdx>__<hash16>.<ext>`. The double underscore is the
separator; underscore is permitted inside the indexes if needed but for
v1 `blockIdx` is always a single integer.

### 4.5 Versioning strategy

When the renderer changes in a way that affects output (e.g., new dvisvgm
flag, new postprocessor rule), the renderer-version directory bumps
(`v1/` → `v2/`).

- Old version directories are kept for a configurable count `N` (default
  `N=2`) so the user can roll back.
- GC explicitly prunes version directories below `N`.
- Schema version (`index.json` `schemaVersion`) and renderer version are
  separate; schema bumps are rare and migrated, not regenerated.

---

## 5. Renderer Command Catalog

This is the canonical reference for what command each language adapter runs.
The Python adapters wrap these and apply the §7 hardening.

### 5.1 TikZ (lualatex + dvisvgm)

**Inputs:** TikZ block source `<src>`, optional global preamble `<preamble>`,
work directory `<work>`.

**Wrapper TeX file:**
```latex
\documentclass[border=4pt]{standalone}
\usepackage{tikz, pgfplots}
% global preamble injected here if present
<preamble>
\begin{document}
<src>
\end{document}
```

**Build commands:**
```bash
lualatex -interaction=nonstopmode -halt-on-error \
  -output-directory=<work> -output-format=dvi <work>/source.tex

dvisvgm --no-fonts \
  --bbox=preview \
  --exact-bbox \
  --output=<work>/out.svg \
  <work>/source.dvi
```

**Notes:**
- `--no-fonts` is **MANDATORY** (path conversion; iOS lacks Computer Modern).
- `--bbox=preview --exact-bbox` for tight cropping (replaces the need for
  the `preview` package or `\documentclass[border=4pt]{standalone}` magic
  in dvisvgm-aware setups, but we keep `standalone` because it's already
  working today).
- Use **lualatex**, not pdflatex — required for `tikz-feynman` auto-layout
  and `graphdrawing` force-directed networks; future-proofs for those
  domains.
- Render budget: 5s per block typical; 30s timeout.

### 5.2 Graphviz (dot)

**Inputs:** Graphviz DOT source `<src>`, work dir `<work>`.

**Build commands:**
```bash
dot -Tsvg -o<work>/out.svg <work>/source.dot
```

**Notes:**
- No special hardening at the dot level; postprocessor handles ID prefix
  and dark-mode fixes (§7).
- Render budget: <1s typical; 10s timeout.
- macOS install: `brew install graphviz`.

### 5.3 D2 (d2 CLI)

**Inputs:** D2 source `<src>`, work dir `<work>`.

**Build commands:**
```bash
d2 --layout=elk --pad=20 --theme=0 \
   --bundle=true \
   <work>/source.d2 <work>/out.svg
```

**Notes:**
- ELK layout for graph reliability (alternative engines: `dagre`, `tala`).
- `--theme=0` is the neutral palette; `currentColor` postprocessing
  retargets foreground to the Obsidian theme.
- `--bundle=true` inlines fonts and assets (we still re-strip to paths via
  postprocess if needed).
- Render budget: 1–3s typical; 15s timeout.
- macOS install: `brew install d2`.

### 5.4 LilyPond

**Inputs:** LilyPond source `<src>`, work dir `<work>`.

**Build commands:**
```bash
lilypond -dpoint-and-click=#f -dbackend=svg \
         -dno-include-book-title-preview \
         -o<work>/out <work>/source.ly
```

**Notes:**
- `-dpoint-and-click=#f` is **MANDATORY**. By default LilyPond bakes
  absolute file:// URIs into the SVG so users can click to jump back to
  the source line in their editor — that's a determinism killer for our
  cache (different machines yield different URIs → different bytes →
  cache thrash). Disabling is essential.
- LilyPond produces `out.svg` (or `out-1.svg`, `out-2.svg` for multi-page;
  v1 supports single-page only).
- Render budget: 2–5s typical; 30s timeout.
- macOS install: `brew install lilypond`.

### 5.5 RDKit (Python library, no shell)

**Inputs:** SMILES string `<src>`, work dir `<work>`.

**Python:**
```python
from rdkit import Chem
from rdkit.Chem import Draw, AllChem

mol = Chem.MolFromSmiles(src.strip())
if mol is None:
    raise RenderError(f"Invalid SMILES: {src!r}")

# Generate 2D coordinates
AllChem.Compute2DCoords(mol)

# Render to SVG
drawer = Draw.MolDraw2DSVG(400, 300)
drawer.DrawMolecule(mol)
drawer.FinishDrawing()
svg_text = drawer.GetDrawingText()

# Strip XML preamble for postprocessing
svg_text = re.sub(r'<\?xml[^>]+\?>\s*', '', svg_text, count=1)

(work / "out.svg").write_text(svg_text, encoding="utf-8")
```

**Notes:**
- No CLI shell-out; native Python integration via `pip install rdkit`.
- For multi-line SMILES (reactions, etc.), v1 parses single SMILES only;
  reactions are deferred.
- Output dimensions are fixed in v1 (400×300); future SPEC may add fence
  attributes for sizing.
- Render budget: <1s typical; 10s timeout.

### 5.6 Adapter contract (shared interface)

Every adapter implements:

```python
class RendererAdapter(ABC):
    @abstractmethod
    def render(self, source: str, attrs: dict, workdir: Path) -> Path:
        """
        Render `source` to an SVG file in `workdir`.
        Return the absolute path of the produced .svg file.
        Raise RenderError on failure (with stderr captured).
        """

    @property
    @abstractmethod
    def language(self) -> str: ...

    @property
    @abstractmethod
    def render_budget_seconds(self) -> int: ...
```

The dispatcher selects the adapter by `language` field from the parsed
fence tag.

---

## 6. Plugin Specification

The plugin is **deliberately small**. It does not render anything. It reads
the cache, displays SVGs, and exposes commands.

### 6.1 Identity

- **ID:** `obsidian-render-cache`
- **Name:** Render Cache
- **Author:** cstelmach
- **Min Obsidian version:** 1.4.16
- **Platforms:** desktop + mobile (iOS, Android)
- **License:** MIT (no GPL dependencies)

### 6.2 Codeblock processors

For each language in the v1 whitelist, register:

```typescript
this.registerMarkdownCodeBlockProcessor(
    "tikz",  // also: "graphviz", "d2", "lilypond", "smiles"
    async (source, el, ctx) => {
        await this.displayCachedBlock(source, "tikz", el, ctx);
    },
);
```

**`displayCachedBlock` flow:**

```typescript
async displayCachedBlock(
    source: string,
    lang: string,
    el: HTMLElement,
    ctx: MarkdownPostProcessorContext,
): Promise<void> {
    // 1. Resolve the note path
    const notePath = ctx.sourcePath; // e.g., "kn/math/concepts/mSB5-2_partial.md"

    // 2. Determine block index — count occurrences of fence in source up to ctx.frontmatter location
    const blockIdx = await this.computeBlockIdx(notePath, ctx);

    // 3. Compute cache key
    const normalized = normalizeSource(source, lang);
    const preambleHash = await this.preambleHashFor(notePath);
    const hash = sha256_truncated_16(normalized + lang + JSON.stringify({}) + preambleHash);

    // 4. Lookup
    const entry = this.index.notes[notePath]?.blocks
        ?.find(b => b.blockIdx === blockIdx && b.sourceHash === hash);

    // 5. Display
    el.empty();
    if (entry && await this.app.vault.adapter.exists(entry.cachePath)) {
        // CACHE HIT
        const img = el.createEl("img", { cls: "render-cache-img" });
        img.src = this.app.vault.adapter.getResourcePath(entry.cachePath);
        img.alt = `${lang}-cache`;
        img.loading = "lazy";
        img.dataset.lang = lang;
        img.dataset.hash = hash;
    } else {
        // CACHE MISS
        const placeholder = el.createDiv({ cls: "render-cache-placeholder" });
        if (Platform.isMobile || this.settings.mode === "cache-only") {
            placeholder.setText(`Render needed (open on desktop). [${lang}]`);
        } else {
            placeholder.setText(`Render needed. Click to render this block. [${lang}]`);
            placeholder.addEventListener("click", () => {
                this.triggerRender(notePath, blockIdx);
            });
        }
    }
}
```

### 6.3 Modes

- **`hybrid`** (default desktop): cache hit displays cached SVG; cache miss
  shows placeholder with click-to-render. Saving a note triggers Python
  via Shell Commands plugin (configurable).
- **`cache-only`** (default mobile): cache hit displays; cache miss shows
  read-only placeholder. No render trigger.
- **`live`** (desktop opt-in): every load bypasses cache and re-renders.
  Useful for actively debugging a TikZ block.

Mobile **always** behaves as `cache-only` regardless of setting (no
renderer available). Plugin auto-overrides on `Platform.isMobile`.

### 6.4 Commands (registered with Obsidian command palette)

| Command ID | Display Name | Behavior |
|---|---|---|
| `render-cache:refresh-block` | Render Cache: Refresh this block | Cursor-aware. Find current code block, force re-render, update cache. |
| `render-cache:refresh-note` | Render Cache: Refresh all blocks in this note | Iterate active note's code blocks; re-render all. |
| `render-cache:refresh-vault` | Render Cache: Refresh entire vault | Confirmation prompt; iterate all `.md` files; re-render any block. Long-running with progress. |
| `render-cache:show-status` | Render Cache: Show cache status | Modal: count by language, total disk size, last sweep, oldest cache, newest cache. |
| `render-cache:sweep-orphans` | Render Cache: Sweep orphaned cache files | Walk cache dir; remove files not in index; remove index entries pointing to deleted notes. |
| `render-cache:toggle-mode` | Render Cache: Cycle render mode | hybrid → cache-only → live → hybrid. |
| `render-cache:clear-all` | Render Cache: Clear entire cache | Strong confirmation; deletes all cached SVGs and `index.json`. |

### 6.5 Settings UI

Settings stored in `.obsidian/plugins/obsidian-render-cache/data.json`.

| Setting | Type | Default | Description |
|---|---|---|---|
| `mode` | enum | `hybrid` | hybrid / cache-only / live |
| `enabledLanguages` | string[] | all 5 | TikZ / Graphviz / D2 / LilyPond / RDKit |
| `pythonPath` | string | `python3` | Path to Python interpreter |
| `texBinDir` | string | (auto-detect) | Directory containing `lualatex`, `dvisvgm` |
| `renderTimeoutSeconds` | int | 30 | Per-block timeout |
| `versionRetention` | int | 2 | Keep N most recent renderer-version dirs |
| `triggerOnSave` | bool | true | Auto-render on note save (desktop) |
| `showStatusBar` | bool | true | Status bar progress indicator |
| `applyHardening` | bool | true | Apply postprocessing rules from §7 |

### 6.6 Error display

When a render fails, the cache `index.json` records the failure with
the captured stderr and the plugin shows an error block instead of a
placeholder:

```
┌─────────────────────────────────────────────┐
│  ⚠ Render failed: tikz block                │
│                                              │
│  ! Undefined control sequence \unknownmacro  │
│    Line 7: \unknownmacro{foo}                │
│                                              │
│  [Click to retry]                           │
└─────────────────────────────────────────────┘
```

This eliminates the silent-failure mode that plagued TikZJax.

### 6.7 Status bar

When `showStatusBar=true`, an item appears in the status bar:

- Idle: `Render Cache: ✓` (count of cached items in current note)
- Rendering: `Render Cache: rendering 2/5…`
- Error: `Render Cache: ⚠ 1 failed`

Click the status bar item to open the status modal.

---

## 7. Renderer Hardening (Mandatory)

These rules are not opt-in. They prevent known failure modes verified by
research. Each is a direct consequence of a documented iOS/Obsidian
limitation.

### 7.1 SVG postprocessing (applied to all SVG outputs)

**Order matters:**

1. **Hash-prefix all SVG IDs.**
   - Find every `id="X"`. Replace with `id="<short-hash>__X"` (use first
     6 chars of the cache hash as prefix).
   - Find every `href="#X"` and `xlink:href="#X"`. Replace with
     `href="#<short-hash>__X"`.
   - Reason: dvisvgm uses generic IDs like `g1-12`, `g1-13`. When two
     SVGs from different blocks share IDs on the same page, the second
     one's `<use>` references resolve against the first one's `<defs>`,
     producing visual corruption.

2. **Replace hardcoded black with `currentColor`.**
   - Find `fill="#000000"`, `stroke="#000000"`, `fill="black"`,
     `stroke="black"` (case-insensitive).
   - Replace with `fill="currentColor"`, `stroke="currentColor"`.
   - Apply only inside drawing primitives (`<path>`, `<text>`, `<line>`,
     etc.); leave raster image data unchanged.
   - Reason: enables Obsidian dark mode adaptation. Theme CSS sets
     `color: var(--text-normal)` which `currentColor` inherits.

3. **Force valid `viewBox`.**
   - If `<svg>` has `width="500pt" height="300pt"` but no `viewBox`, add
     `viewBox="0 0 500 300"` and strip units from `width`/`height`.
   - Reason: iOS WKWebView with `pt` units in `width`/`height` and no
     `viewBox` renders a 0×0 element silently.

4. **Run SVGO with conservative config.**
   - **Disabled plugins**: `cleanupIDs`, `removeHiddenElems`,
     `collapseGroups` (these break dvisvgm's `<defs>/<use>` glyph
     references).
   - **Enabled plugins**: `removeMetadata`, `removeComments`,
     `removeEmptyAttrs`, `removeUnusedNS`, `convertColors`.
   - Result: ~15–25% size reduction without breaking visuals.
   - **Never `.svgz`** (Obsidian's local protocol omits gzip header → file
     loads as binary garbage).

### 7.2 Determinism flags per renderer

| Renderer | Flag / Setting | Reason |
|---|---|---|
| `dvisvgm` | `--no-fonts` | iOS font fallback prevention (§7.3) |
| `dvisvgm` | `--exact-bbox` | Deterministic cropping |
| `lilypond` | `-dpoint-and-click=#f` | Strip absolute file:// URIs from SVG |
| `lilypond` | `-dno-include-book-title-preview` | Suppress preview rendering |
| `matplotlib` (future) | `rcParams['svg.hashsalt'] = 'render-cache'` | Stable element IDs across runs |
| `matplotlib` (future) | `metadata={'Date': None}` | No timestamp embed |

### 7.3 iOS font fallback prevention

Native LaTeX uses Computer Modern (cmr10, cmsy10, etc.). iOS WKWebView
ships with neither these TrueType fonts nor any fallback that resembles
them; `<text font="cmr10">` silently renders in Times New Roman, which
breaks math layout (subscript positions, integral sign sizing, etc.).

The fix is `dvisvgm --no-fonts`: convert all `<text>` elements to `<path>`
elements using glyph outlines embedded in the SVG. Resulting SVG is
larger (~15–25% bigger than font-referenced) but renders identically
on every platform. This is non-negotiable for our use case.

### 7.4 Idempotence guarantees

The renderer pipeline must be idempotent: running `render_cache.py FILE.md`
twice with no source changes produces no file changes (no new SVG, no
markdown rewrite, no index update beyond `lastSeen` timestamp).

Tests for idempotence are part of the acceptance criteria (§8).

---

## 8. Acceptance Criteria

A v1 is "done" when all of these are true. Each maps to verification.

| # | Criterion | Verification |
|---|---|---|
| 8.1 | TikZ block renders to SVG via `lualatex` + `dvisvgm --no-fonts` | Run `python3 render_cache.py kn/math/concepts/mSB3-4_reals.md`; resulting SVG has no `<text>` elements (only `<path>`); diagram visually correct |
| 8.2 | Graphviz block renders to SVG via `dot -Tsvg` | Test sandbox `_RENDER_TEST_graphviz.md` produces correct SVG |
| 8.3 | D2 block renders to SVG via `d2 CLI` | Test sandbox `_RENDER_TEST_d2.md` produces correct SVG |
| 8.4 | LilyPond block renders to SVG with no file:// URIs | Test sandbox `_RENDER_TEST_lilypond.md` produces SVG; `grep file:// out.svg` returns nothing |
| 8.5 | SMILES block renders to molecule SVG via RDKit | Test sandbox `_RENDER_TEST_smiles.md` with caffeine SMILES produces a recognizable molecule diagram |
| 8.6 | Cache hit on idempotent re-run | Run script twice on same file; second run reports "all hits"; mtimes unchanged |
| 8.7 | `--force` flag bypasses cache | Force flag generates new SVG even on hit |
| 8.8 | Hash-based invalidation: source change forces re-render | Edit one TikZ block; run script; only that block re-renders |
| 8.9 | Renderer-version namespace bump triggers full re-render | Bump `RENDERER_VERSION` constant in script; run on file; new `v2/` dir created |
| 8.10 | Sweep removes orphans, keeps current | Manual orphan creation + sweep; orphan gone, current cache preserved |
| 8.11 | Plugin shows cached SVG inline; source codeblock hidden in reading mode | Visual verification on desktop and mobile |
| 8.12 | Plugin "Refresh this block" command works | Cursor in TikZ block → run command → cache regenerates → SVG updates |
| 8.13 | Plugin "Show cache status" reports accurate counts | Status modal displays count = number of `*.svg` files in cache dir |
| 8.14 | iOS: no crash on previously-crashing notes | Open `kn/math/concepts/_TIKZ_TEST_mSB5-2.md` on phone; loads cleanly, no reload loop |
| 8.15 | iOS: SVG renders correctly (no font fallback to Times) | Visual verification: math symbols correctly positioned |
| 8.16 | Hardening verification: ID prefixes present in all cached SVGs | `grep -c 'id="g1-' cache/v1/.../*.svg` returns 0; `grep -c 'id="[0-9a-f]\{6\}__' cache/v1/.../*.svg` returns count > 0 |
| 8.17 | Hardening verification: `currentColor` substitution applied | Cached SVG opened in light vs dark Obsidian theme shows correct foreground color |
| 8.18 | Hardening verification: `viewBox` present in all cached SVGs | All cached SVGs contain `viewBox="..."`; no `pt` units in width/height |
| 8.19 | Migration: existing `attachments/cache/tikz/*.png` references rewritten to new SVG references | Run migration tool; verify all 5 PNG references replaced with corresponding SVG references; old PNGs swept |
| 8.20 | Cache key includes preamble hash | Modify global preamble; observe cascade re-render of all blocks using it |
| 8.21 | Per-block render error displays inline error block, not silent failure | Inject deliberate `\undefined` macro in a TikZ block; render fails; plugin shows inline error |

---

## 9. Phases (high-level summary)

`PLAN.md` provides full per-phase task breakdowns. The phases are:

| # | Phase | Effort | Owner | Deliverable |
|---|---|---|---|---|
| 1 | Migration: PNG→SVG for existing tikz_cache.py | 3–5 h | agent | `tikz_cache.py` outputs SVG via `dvisvgm --no-fonts`; existing 5 cached files re-rendered; markdown image refs updated |
| 2 | Restructure into render_cache package | 2–4 h | agent | `render_cache/` package with adapters/, normalize, hash, index, postprocess; `render_cache.py` is the CLI entry point |
| 3 | Add Graphviz adapter | 1–2 h | agent | `adapters/graphviz.py`; test sandbox; acceptance 8.2 |
| 4 | Add D2 adapter | 1–2 h | agent | `adapters/d2.py`; test sandbox; acceptance 8.3 |
| 5 | Add LilyPond adapter | 2–3 h | agent | `adapters/lilypond.py`; test sandbox; acceptance 8.4 |
| 6 | Add RDKit adapter | 2–3 h | agent | `adapters/smiles.py`; test sandbox; acceptance 8.5 |
| 7 | Apply SVG postprocessing hardening | 4–6 h | agent | `postprocess.py` with all §7 rules; acceptance 8.16/8.17/8.18 |
| 8 | Plugin scaffold (manifest, settings, codeblock processors) | 4–6 h | agent | `obsidian-render-cache/` plugin loads, shows placeholder for misses, displays cached SVG for hits |
| 9 | Plugin commands and modes | 4–6 h | agent | All 7 commands functional; mode toggle; status modal |
| 10 | Plugin error display + status bar | 2–3 h | agent | Inline error blocks; status bar item |
| 11 | iOS validation | 1–2 h | user | Install plugin on phone; verify no crash; verify SVG fidelity |
| 12 | Migration tool: legacy `attachments/cache/tikz/` → new layout | 2–3 h | agent | Tool moves SVGs (or regenerates), rewrites markdown refs, sweeps legacy dir; acceptance 8.19 |
| 13 | Documentation: README, install guide, troubleshooting | 2–3 h | agent | Plugin README; user-facing CLI docs |
| 14 | Optional: gboyd068/SwiftLaTeX hands-on eval | ~1 h | agent + user | Only if v1 has unresolved gaps; report saved to `/tmp/` |

**Total estimated effort:** 30–48 agent hours + 1–2 user hours, plus 1 h
optional Phase 14.

**Critical path:** 1 → 2 → 7 → 8 → 11. Phases 3–6 can be done in any order
after 2. Phases 9, 10, 12, 13 can run in parallel with 8 and after.

---

## 10. Risks and Mitigations

| # | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| 10.1 | `dvisvgm` rejects an existing TikZ block that pdftoppm accepted | Low | Block-level (one diagram fails) | Pre-flight all existing blocks with `dvisvgm --no-fonts`; capture errors; only migrate blocks that pass |
| 10.2 | Postprocessor breaks visually-significant SVG markup | Medium | Visual regression | Each rule has a roundtrip test (apply rule → reverse rule → byte-equal); visual diff tests on representative blocks |
| 10.3 | LuaLaTeX render time >30s on largest pgfplots blocks | Low | Render budget exceeded | Increase per-block timeout; document `\pgfplotsset{compat=1.18,reduced size}` workarounds |
| 10.4 | Cache thrash from non-deterministic renderer output | Medium | Sync noise, perpetual re-render | Determinism flags from §7.2; also smoke-test: render same input twice, byte-compare |
| 10.5 | Plugin hot-reload loses index state | Low | Session-local glitch | Plugin reads index from disk on every codeblock processor invocation in v1 (no in-memory cache); revisit after measurement |
| 10.6 | iOS sandbox prevents `<img>` access to `.obsidian/plugins/` files | High if `<img src>` used; Low with wikilink | Cache invisible on mobile | Always use Obsidian wikilink embed (`![[…]]`); never raw HTML `<img>` (research finding 4) |
| 10.7 | Two-sources-of-truth: legacy `tikz_cache.py` and new pipeline | Medium during migration | Cache divergence | During Phases 1–2, legacy script is updated, not replaced; after Phase 2 it becomes a thin shim that calls into `render_cache/` |
| 10.8 | Plugin TypeScript bundle size affects mobile load | Low | Slightly slower mobile launch | Keep plugin simple (~300–500 LOC); no heavy deps |
| 10.9 | gboyd068 plugin (deferred fallback) becomes unmaintained or unusable | Medium-High | If we ever need it, may not work | We do NOT depend on it for v1; only invoke if v1 has unmitigable gap. Acceptable risk. |
| 10.10 | TeX Live update breaks existing TikZ blocks | Low | Some diagrams stop rendering | Pin TeX Live snapshot via `tlmgr` lockfile; document in README |
| 10.11 | Renderer-version bump invalidates cache before user is ready | Low | Brief slow first-load after upgrade | Version retention `N=2` keeps the previous version's cache until next bump |
| 10.12 | iCloud sync of `.obsidian/plugins/.../cache/` is unreliable | High | Mobile cold-starts on first sync | Accept as known limitation. Document. Encourage Obsidian Sync (paid) for users who care; default behavior is "mobile renders from desktop-built cache eventually." |
| 10.13 | Content-hash collision at vault scale | Negligible (4×10⁻¹⁵) | Wrong SVG displayed | Accept as theoretical; use 16 hex chars (not 8 — that's 4% collision at our scale) |
| 10.14 | User edits markdown image ref by hand → drift between markdown and index | Medium | Plugin shows wrong image or no image | Plugin's hash lookup uses the codeblock source, not the image ref. The image ref is auxiliary (for non-plugin viewers like GitHub preview). Drift is recoverable via `refresh-note` command. |

---

## 11. Open Questions Deferred to Future Work

These are intentionally NOT decided in v1. They are not blockers; they are
explicit "to revisit" items.

| # | Question | Why deferred |
|---|---|---|
| 11.1 | Per-block fence attributes (e.g., `${\`\`\`tikz width=400}`) | YAGNI for v1; user has no current per-block need |
| 11.2 | Watch-mode auto-render daemon | Out of scope for personal-use SPEC; manual + on-save is sufficient |
| 11.3 | Vega-Lite, 3Dmol.js, PlantUML adapters | Not in 80/20 whitelist; revisit if user starts writing in those |
| 11.4 | Programmatic animation pipeline (Manim et al.) | iOS playback constraints; vault-size cost; separate SPEC |
| 11.5 | Typst migration | Pre-1.0 ecosystem; revisit when Typst 1.0 ships and chemistry/circuits packages mature |
| 11.6 | Cloud rendering fallback | Offline-first violated; only revisit if user explicitly opts in |
| 11.7 | Cross-vault cache sharing | Single-user single-vault is the only target |
| 11.8 | Mobile-side WASM rendering as fallback | gboyd068 path; deferred unless v1 has unfixable gap |
| 11.9 | Markdown ref: should we write `![[…|tikz-cache]]` or `![[…|render-cache]]` alt text? | TBD — backward compat with existing CSS rules suggests keep `tikz-cache` for migration period; revisit Phase 12 |
| 11.10 | First-class support for editing SVG metadata (titles, descriptions) | Accessibility win; not v1 scope |

---

## 12. Glossary (cross-reference)

| Term | Definition |
|---|---|
| **Render-at-save** | Architecture pattern (Path C) where rendering happens on file save (or manual CLI), not on view |
| **TikZJax** | The existing Obsidian plugin we are explicitly NOT modernizing |
| **dvisvgm** | The mature DVI→SVG converter (3.6 as of Jan 2026); replaces TikZJax's `dvi2html` |
| **LuaLaTeX** | Modern LaTeX engine; supports `tikz-feynman` and `graphdrawing` libraries unavailable elsewhere |
| **Cache key** | 16-char SHA-256 hash of (normalized source + lang + attrs + preamble hash) |
| **Renderer version namespace** | Top-level cache directory (e.g., `v1/`) that segregates caches per renderer release |
| **Path C** | The render-at-save architecture; see Round 1 research |
| **80/20 whitelist** | The minimal set of languages that covers the user's plausible need |
| **`obsidian-render-cache`** | The new plugin specified in §6 |
| **`render_cache.py`** | The new Python entry point (evolution of `tikz_cache.py`) |

---

## 13. Approval

This SPEC is awaiting user review. Once approved:

1. Status changes to ACCEPTED.
2. `PROGRESS.md` is created.
3. Implementation begins per `PLAN.md`, Phase 1.

---

*End of SPEC.*
