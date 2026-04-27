# Implementation Plan — Obsidian Render Cache

**Spec:** `/Users/cs/Obsidian/_/docs/specs/render-cache/SPEC.md`
**Created:** 2026-04-26
**Agent:** execute-spec (manual mode — user-driven phase progression)
**Predecessor plan:** `/Users/cs/Obsidian/_/docs/specs/tikz-cache/PLAN.md` (TikZ-only PNG; superseded)

---

## Note on This Plan

This document is the executable companion to `SPEC.md`. The SPEC defines
WHAT the system must do and WHY. This plan defines HOW to build it,
phase by phase.

Each phase has tasks, verification commands, common-mistake callouts, and
exit criteria. **If a verification fails, stop and read the troubleshooting
table for that phase before improvising.**

For design rationale or component contracts, refer to the SPEC sections
listed at the top of each phase.

---

## Pre-Plan State (verified 2026-04-26)

These are facts about the project at SPEC-acceptance time.

| Item | Status | Source |
|---|---|---|
| `tikz_cache.py` exists, currently outputs PNG via `pdftoppm` | Present | `resources/scripts/python_single/tikz_cache.py` |
| 5 cached PNG files at `attachments/cache/tikz/` | Present (~663 KB total) | tikz-cache predecessor work |
| 5 markdown files have `![[…|tikz-cache]]` PNG references | Present | mSB3-4_reals, mSB5-2_partial, mLA5-1_eigenvalues (×2), mSB3-5_complex |
| `.obsidian/snippets/tikz-cache.css` (hybrid variant) | Present | `tikz-cache` Phase 5 |
| `.obsidian/plugins/obsidian-render-cache/` | Does not exist | New, Phase 8 creates |
| `dvisvgm` binary | Available via TeX Live | `/Library/TeX/texbin/dvisvgm` |
| `lualatex` binary | Available | `/Library/TeX/texbin/lualatex` |
| `dot` binary (Graphviz) | TBD — Phase 3 pre-flight | `which dot` |
| `d2` binary | TBD — Phase 4 pre-flight | `which d2` |
| `lilypond` binary | TBD — Phase 5 pre-flight | `which lilypond` |
| RDKit Python package | TBD — Phase 6 pre-flight | `python3 -c "import rdkit"` |

---

## Pre-Flight Checks

Run **before** Phase 1. Stop if any required check fails.

### Mandatory (Phases 1–2)

| # | Check | Command | Pass criteria |
|---|---|---|---|
| 0.1 | Vault root | `test -d /Users/cs/Obsidian/_ && echo OK` | `OK` |
| 0.2 | LuaLaTeX | `which lualatex` | path |
| 0.3 | dvisvgm | `which dvisvgm` | path |
| 0.4 | dvisvgm version ≥ 3.0 | `dvisvgm --version \| head -1` | "dvisvgm 3.x" or higher |
| 0.5 | Python 3.10+ | `python3 --version` | `3.10` or higher |
| 0.6 | Existing tikz_cache.py compiles | `python3 -c "import ast; ast.parse(open('/Users/cs/Obsidian/_/resources/scripts/python_single/tikz_cache.py').read())"` | exit 0 |
| 0.7 | Existing cache dir | `test -d /Users/cs/Obsidian/_/attachments/cache/tikz && echo OK` | `OK` |
| 0.8 | New cache dir creatable | `mkdir -p /Users/cs/Obsidian/_/.obsidian/plugins/obsidian-render-cache/cache && echo OK` | `OK` |

### Per-language (deferred to corresponding phase)

| Phase | Check | Command | Pass criteria |
|---|---|---|---|
| 3 | Graphviz | `which dot && dot -V` | path; "graphviz version 2.X+" |
| 4 | D2 | `which d2 && d2 --version` | path; "v0.7.0" or higher |
| 5 | LilyPond | `which lilypond && lilypond --version \| head -1` | path; "GNU LilyPond 2.24" or higher |
| 6 | RDKit | `python3 -c "from rdkit import Chem; print(Chem.__version__)"` | version string |

If a per-language tool is missing, **install it via brew/pip THEN proceed**:

```bash
brew install graphviz d2 lilypond
pip3 install rdkit
```

### Plugin development (Phase 8+)

| # | Check | Command | Pass criteria |
|---|---|---|---|
| 0.9 | Node.js | `node --version` | `v18` or higher |
| 0.10 | npm | `npm --version` | `9` or higher |

---

## Dependency Graph

```
                Pre-Flight (mandatory checks)
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  Phase 1: PNG → SVG migration      │ (3–5h)
        │  (tikz_cache.py: pdftoppm→dvisvgm) │
        └─────────────────┬──────────────────┘
                          ▼
        ┌────────────────────────────────────┐
        │  Phase 2: Package restructure      │ (2–4h)
        │  (render_cache/ skeleton)          │
        └─────────┬──────────────────────────┘
                  │
       ┌──────────┴──────────────┬─────────────────┐
       ▼          ▼              ▼                 ▼
   ┌───────┐  ┌───────┐  ┌─────────────┐    ┌──────────────────┐
   │ Phase │  │ Phase │  │ Phase 7:    │    │ Phase 8:         │
   │  3:   │  │  4:   │  │ SVG hardening│    │ Plugin scaffold  │
   │ Graph │  │  D2   │  │ (postprocess) │    │                  │
   │viz    │  │       │  │ (4–6h)       │    │ (4–6h)           │
   │(1–2h) │  │(1–2h) │  │              │    │                  │
   └───┬───┘  └───┬───┘  └──────┬───────┘    └────────┬─────────┘
       │          │             │                     │
       └──────────┴────────┬────┴─────────────────────┤
                           ▼                          ▼
                  ┌──────────────────┐      ┌────────────────────┐
                  │ Phase 5/6:       │      │ Phase 9: Commands   │
                  │ LilyPond/RDKit   │      │ + modes (4–6h)      │
                  │ (2–3h each)      │      └─────────┬──────────┘
                  └──────────────────┘                ▼
                                            ┌────────────────────┐
                                            │ Phase 10: Errors    │
                                            │ + status bar (2–3h) │
                                            └─────────┬──────────┘
                                                      ▼
                                            ┌────────────────────┐
                                            │ Phase 12: Migration │
                                            │ tool (2–3h)         │
                                            └─────────┬──────────┘
                                                      ▼
                                            ┌────────────────────┐
                                            │ Phase 11: iOS       │
                                            │ validation (USER)   │
                                            └─────────┬──────────┘
                                                      ▼
                                            ┌────────────────────┐
                                            │ Phase 13: Docs      │
                                            │ (2–3h)              │
                                            └─────────┬──────────┘
                                                      ▼
                                          [optional Phase 14]
```

Critical path: 1 → 2 → 7 → 8 → 11.
Phases 3, 4, 5, 6 parallelizable after Phase 2.
Phase 8 parallelizable with Phases 3–7.

---

## Phases

### Phase 1 — Migration: PNG → SVG via dvisvgm

**SPEC reference:** §5.1, §7.1, §7.3.
**Effort:** 3–5 hours.
**Owner:** agent.
**Depends on:** Pre-Flight 0.1–0.7.

**Goal:** Replace the `pdftoppm` PNG output path in `tikz_cache.py` with
`dvisvgm --no-fonts` SVG output. Re-render the existing 5 cached files
to SVG, update markdown image references from `*.png` to `*.svg`. The
`tikz_cache.py` keeps its current entry-point shape; the package
restructure is Phase 2.

#### Task 1.1 — Read current state of tikz_cache.py

**Action:** Read the script. Identify the section that calls `pdftoppm`.
Note the existing `LATEX_PREAMBLE`, `DPI`, `LUALATEX_TIMEOUT_S`,
`PDFTOPPM_TIMEOUT_S` constants — these change in this phase.

**Verify:** You can locate `subprocess.run([... "pdftoppm" ...])` and
the wrapping `render_tikz` function.

#### Task 1.2 — Replace pdftoppm call with dvisvgm

**Action:** In `render_tikz`, change the LaTeX compile to produce DVI
(not PDF), then call dvisvgm:

```python
# Replace the existing lualatex+pdftoppm sequence with:

# Compile to DVI (not PDF)
result = subprocess.run(
    ["lualatex", "-interaction=nonstopmode", "-halt-on-error",
     "-output-directory", str(work_dir),
     "-output-format=dvi",
     str(tex_path)],
    capture_output=True, text=True, timeout=LUALATEX_TIMEOUT_S,
)
if result.returncode != 0:
    return False, f"lualatex failed: {result.stderr.strip()[:300]}"

dvi_path = work_dir / f"{tex_path.stem}.dvi"
if not dvi_path.exists():
    return False, "lualatex produced no DVI"

# Convert DVI → SVG
out_svg = output_path  # output_path is now <stem>.svg, not <stem>.png
result = subprocess.run(
    ["dvisvgm",
     "--no-fonts",          # MANDATORY: glyph outlines, no font references
     "--exact-bbox",         # tight cropping
     "--bbox=preview",
     "--output", str(out_svg),
     str(dvi_path)],
    capture_output=True, text=True, timeout=DVISVGM_TIMEOUT_S,
)
if result.returncode != 0 or not out_svg.exists():
    return False, f"dvisvgm failed: {result.stderr.strip()[:300]}"

return True, None
```

Add the new constant `DVISVGM_TIMEOUT_S = 60` near the top of the file.
Remove `DPI` and `PDFTOPPM_TIMEOUT_S` (no longer used).

**Verify:**
```bash
python3 -c "import ast; ast.parse(open('/Users/cs/Obsidian/_/resources/scripts/python_single/tikz_cache.py').read())"
grep -c 'pdftoppm' /Users/cs/Obsidian/_/resources/scripts/python_single/tikz_cache.py  # → 0
grep -c 'dvisvgm' /Users/cs/Obsidian/_/resources/scripts/python_single/tikz_cache.py   # → ≥1
grep -c '\-\-no-fonts' /Users/cs/Obsidian/_/resources/scripts/python_single/tikz_cache.py  # → 1
```

#### Task 1.3 — Update output extension and cache path

**Action:** Change `output_png = ...` to `output_svg = ...`. Update
filename suffix from `.png` to `.svg` throughout (cache file names,
image-ref insertion, sweep regex).

**Verify:**
```bash
grep -c '\.png' /Users/cs/Obsidian/_/resources/scripts/python_single/tikz_cache.py  # → 0 (or only in comments)
grep -c '\.svg' /Users/cs/Obsidian/_/resources/scripts/python_single/tikz_cache.py  # → ≥3
```

#### Task 1.4 — Smoke test on known-good file

**Action:**
```bash
# Force re-render so it produces SVG
python3 /Users/cs/Obsidian/_/resources/scripts/python_single/tikz_cache.py \
    /Users/cs/Obsidian/_/kn/math/concepts/mSB3-4_reals.md --force
```

**Verify:**
1. Stdout shows `1 TikZ block(s)`, `→ render`, `file updated`.
2. New SVG file exists:
   ```bash
   ls -la /Users/cs/Obsidian/_/attachments/cache/tikz/mSB3-4_reals__1__*.svg
   ```
3. SVG file size 50–500 KB (much larger than old PNG; expected).
4. SVG opens visually (preview app or browser): real number line with
   √2/π/e/1/3 dots, "No gaps" callout.
5. Markdown reference updated to `.svg`:
   ```bash
   grep 'tikz-cache' /Users/cs/Obsidian/_/kn/math/concepts/mSB3-4_reals.md
   # Should show: ![[mSB3-4_reals__1__<hash>.svg|tikz-cache]]
   ```
6. The SVG is path-only (no font references):
   ```bash
   grep -c '<text' /Users/cs/Obsidian/_/attachments/cache/tikz/mSB3-4_reals__1__*.svg  # → 0
   grep -c '<path' /Users/cs/Obsidian/_/attachments/cache/tikz/mSB3-4_reals__1__*.svg  # → ≥1
   ```

#### Task 1.5 — Re-render the rest of the cached files

**Action:**
```bash
for f in mSB5-2_partial mLA5-1_eigenvalues mSB3-5_complex; do
    python3 /Users/cs/Obsidian/_/resources/scripts/python_single/tikz_cache.py \
        /Users/cs/Obsidian/_/kn/math/concepts/$f.md --force
done
```

**Verify:** All 5 cached files now have `.svg` versions; old `.png` files
remain (will be swept in Phase 12). Markdown image refs all point to
`.svg`.

#### Task 1.6 — iOS sanity test (manual)

**Action:** Open one of the migrated files (e.g., `mSB3-4_reals.md`) on
the iOS Obsidian app. Note: this requires the file to sync first.

**Verify:** SVG renders visibly. Math symbols (√, π, etc.) are correctly
positioned (not collapsed to Times New Roman fallback).

**If verification fails:** the SVG was not produced with `--no-fonts`.
Re-check Task 1.2.

#### Common mistakes (Phase 1)

- **Forgetting `-output-format=dvi`** — lualatex produces PDF by default,
  but dvisvgm wants DVI. Without this flag dvisvgm errors with "PDF
  not supported."
- **Forgetting to update file extensions in markdown image refs** — old
  `.png` refs will resolve to nonexistent files.
- **Leaving `pdftoppm` import or constants** — produces a "configured but
  unused" smell that will confuse the next reader.

#### Exit criteria

- All 5 existing cached files have `.svg` versions.
- Markdown refs all updated.
- Smoke-tested on desktop and iOS.
- Old `.png` files still present (sweep is Phase 12).

---

### Phase 2 — Restructure into render_cache package

**SPEC reference:** §3.3, §5.6.
**Effort:** 2–4 hours.
**Owner:** agent.
**Depends on:** Phase 1 done.

**Goal:** Carve `tikz_cache.py` into a clean Python package with adapter
interfaces, leaving the old script as a backward-compat shim. After this
phase, `render_cache.py` is the new canonical CLI; `tikz_cache.py`
forwards to it.

#### Task 2.1 — Create package skeleton

**Action:**
```bash
mkdir -p /Users/cs/Obsidian/_/resources/scripts/python_single/render_cache/adapters
cd /Users/cs/Obsidian/_/resources/scripts/python_single
# Create empty modules:
for f in render_cache/__init__.py \
         render_cache/adapters/__init__.py \
         render_cache/adapters/base.py \
         render_cache/adapters/tikz.py \
         render_cache/normalize.py \
         render_cache/hash.py \
         render_cache/index.py \
         render_cache/postprocess.py \
         render_cache/markdown_io.py \
         render_cache/cache_paths.py; do
    touch "$f"
done
```

**Verify:** `find render_cache -name '*.py' | wc -l` → 9 files.

#### Task 2.2 — Move logic from tikz_cache.py into modules

**Action:** Extract:
- Block-finding regex → `markdown_io.py`
- Source normalization → `normalize.py`
- Hash computation → `hash.py`
- Index file read/write → `index.py`
- TikZ rendering (the lualatex+dvisvgm sequence) → `adapters/tikz.py`
- Cache path construction → `cache_paths.py`
- Postprocess hooks (empty for now; Phase 7 fills in) → `postprocess.py`

Define the abstract base class in `adapters/base.py` per SPEC §5.6.

**Verify:**
```bash
python3 -c "from render_cache.adapters.tikz import TikzAdapter; t = TikzAdapter(); print(t.language)"
# → "tikz"
python3 -c "from render_cache.normalize import normalize; print(normalize('  hello\n\n\n\n  world  '))"
# → "hello\n\nworld" (or similar — verify whitespace + blank-line collapse)
```

#### Task 2.3 — Wire up render_cache.py CLI

**Action:** Create `render_cache.py` (alongside `tikz_cache.py`) as the
new entry point. Argument parser supports the same flags as today
(`--force`, `--dry-run`, `--sweep`, `--all`) plus future flags.

```python
#!/usr/bin/env python3
"""Render code-block visualizations to cached SVGs."""

import argparse, sys
from pathlib import Path
from render_cache.adapters import REGISTRY  # dict: lang → adapter
from render_cache.markdown_io import find_blocks
from render_cache.index import load_index, save_index
# ...

def main():
    parser = argparse.ArgumentParser(...)
    # parse, dispatch, exit
    ...

if __name__ == "__main__":
    main()
```

**Verify:**
```bash
python3 /Users/cs/Obsidian/_/resources/scripts/python_single/render_cache.py --help  # shows argparse help
python3 /Users/cs/Obsidian/_/resources/scripts/python_single/render_cache.py \
    /Users/cs/Obsidian/_/kn/math/concepts/mSB3-4_reals.md
# Should produce same output as tikz_cache.py did in Phase 1
```

#### Task 2.4 — Convert tikz_cache.py to a shim

**Action:** Replace `tikz_cache.py` body with a deprecation forwarder:

```python
#!/usr/bin/env python3
"""[DEPRECATED] Use render_cache.py instead. Forwarder retained for
backward compatibility with existing user scripts/aliases."""

import sys
import warnings
from pathlib import Path

# Reuse the new CLI
sys.path.insert(0, str(Path(__file__).parent))
from render_cache import main as render_main

warnings.warn(
    "tikz_cache.py is a deprecated shim; call render_cache.py directly.",
    DeprecationWarning, stacklevel=2,
)
sys.exit(render_main())
```

**Verify:** Existing invocations still work; deprecation warning visible.

#### Common mistakes (Phase 2)

- **Importing inside `__init__.py`** that triggers heavy LaTeX environment
  checks at import time → CLI startup is slow. Lazy-import inside
  `main()`.
- **Forgetting that the index file path moves** in Phase 8 (plugin uses
  `.obsidian/plugins/.../cache/index.json`). For now, keep the existing
  location; Phase 8 + Phase 12 migrate it.

#### Exit criteria

- Package layout per SPEC §3.3 in place.
- `render_cache.py` produces identical output to Phase 1 `tikz_cache.py`.
- `tikz_cache.py` warns on deprecated invocation but works.
- All Phase 1 verifications still pass.

---

### Phase 3 — Add Graphviz adapter

**SPEC reference:** §5.2.
**Effort:** 1–2 hours.
**Owner:** agent.
**Depends on:** Phase 2 done. Pre-flight check 3 (which dot).

#### Task 3.1 — Create test sandbox

**Action:** Create `kn/math/concepts/_RENDER_TEST_graphviz.md` with
2–3 representative DOT blocks (a simple digraph, a labeled edge graph,
a clustered subgraph).

#### Task 3.2 — Implement adapter

**Action:** Create `render_cache/adapters/graphviz.py`:

```python
import subprocess
from pathlib import Path
from .base import RendererAdapter, RenderError

class GraphvizAdapter(RendererAdapter):
    @property
    def language(self) -> str: return "graphviz"

    @property
    def render_budget_seconds(self) -> int: return 10

    def render(self, source: str, attrs: dict, workdir: Path) -> Path:
        src_path = workdir / "source.dot"
        out_path = workdir / "out.svg"
        src_path.write_text(source, encoding="utf-8")

        result = subprocess.run(
            ["dot", "-Tsvg", "-o", str(out_path), str(src_path)],
            capture_output=True, text=True,
            timeout=self.render_budget_seconds,
        )
        if result.returncode != 0 or not out_path.exists():
            raise RenderError(f"dot failed: {result.stderr.strip()[:300]}")
        return out_path
```

Register in `adapters/__init__.py` `REGISTRY["graphviz"] = GraphvizAdapter()`.

#### Task 3.3 — Verify

**Action:**
```bash
python3 /Users/cs/Obsidian/_/resources/scripts/python_single/render_cache.py \
    /Users/cs/Obsidian/_/kn/math/concepts/_RENDER_TEST_graphviz.md
```

**Verify:** SVG produced for each Graphviz block; visually correct
(open in Preview); file size 5–50 KB.

#### Exit criteria (Phase 3)

- Acceptance criterion 8.2 met.
- Test sandbox renders.

---

### Phase 4 — Add D2 adapter

**SPEC reference:** §5.3.
**Effort:** 1–2 hours.
**Owner:** agent.
**Depends on:** Phase 2 done. Pre-flight check 4 (which d2).

Same shape as Phase 3. Adapter command:

```python
result = subprocess.run(
    ["d2", "--layout=elk", "--pad=20", "--theme=0",
     "--bundle=true",
     str(src_path), str(out_path)],
    capture_output=True, text=True, timeout=self.render_budget_seconds,
)
```

Test sandbox: `_RENDER_TEST_d2.md` with 2–3 representative D2 blocks.

**Exit criteria:** Acceptance criterion 8.3 met.

---

### Phase 5 — Add LilyPond adapter

**SPEC reference:** §5.4.
**Effort:** 2–3 hours.
**Owner:** agent.
**Depends on:** Phase 2 done. Pre-flight check 5 (which lilypond).

Adapter command:

```python
result = subprocess.run(
    ["lilypond",
     "-dpoint-and-click=#f",                    # MANDATORY
     "-dbackend=svg",
     "-dno-include-book-title-preview",
     "-o", str(workdir / "out"),
     str(src_path)],
    capture_output=True, text=True, timeout=self.render_budget_seconds,
)
# LilyPond produces out.svg or out-1.svg, etc.
out_path = next(workdir.glob("out*.svg"))
```

Test sandbox: `_RENDER_TEST_lilypond.md` with a simple melody and a
short lead sheet.

**Verification specifics:**
- `grep -c 'file://' out.svg` → 0 (acceptance criterion 8.4)

**Exit criteria:** Acceptance criterion 8.4 met.

---

### Phase 6 — Add RDKit adapter

**SPEC reference:** §5.5.
**Effort:** 2–3 hours.
**Owner:** agent.
**Depends on:** Phase 2 done. Pre-flight check 6 (`import rdkit`).

Adapter implementation: pure Python, no shell-out. Use code from SPEC §5.5.

Test sandbox: `_RENDER_TEST_smiles.md` with caffeine, aspirin, and
ibuprofen SMILES strings.

**Exit criteria:** Acceptance criterion 8.5 met. Recognizable molecule
diagrams.

---

### Phase 7 — Apply SVG postprocessing hardening

**SPEC reference:** §7.1, §7.3, §7.4.
**Effort:** 4–6 hours.
**Owner:** agent.
**Depends on:** Phase 2 done; Phases 3–6 produce SVGs to test against.

**Goal:** Implement the four postprocessing rules in
`render_cache/postprocess.py`, wire them into the dispatcher between
adapter render and cache write.

#### Task 7.1 — Implement rule 1: ID prefix

**Action:** In `postprocess.py`:

```python
import re
from typing import Final

_ID_RE: Final = re.compile(r'\bid="([^"]+)"')
_HREF_RE: Final = re.compile(r'\b(xlink:)?href="#([^"]+)"')

def prefix_ids(svg_text: str, prefix: str) -> str:
    """Hash-prefix all SVG element IDs to prevent cross-block collisions."""
    safe_prefix = prefix[:6]  # First 6 chars of cache hash
    svg_text = _ID_RE.sub(lambda m: f'id="{safe_prefix}__{m.group(1)}"', svg_text)
    svg_text = _HREF_RE.sub(
        lambda m: f'{m.group(1) or ""}href="#{safe_prefix}__{m.group(2)}"',
        svg_text,
    )
    return svg_text
```

**Test:**
```python
svg = '<svg><defs><path id="g1-12"/></defs><use xlink:href="#g1-12"/></svg>'
assert 'id="abc123__g1-12"' in prefix_ids(svg, "abc123")
assert 'href="#abc123__g1-12"' in prefix_ids(svg, "abc123")
```

#### Task 7.2 — Implement rule 2: currentColor substitution

**Action:**

```python
_BLACK_FILL_RE: Final = re.compile(r'\bfill="(#000000|#000|black)"', re.IGNORECASE)
_BLACK_STROKE_RE: Final = re.compile(r'\bstroke="(#000000|#000|black)"', re.IGNORECASE)

def substitute_current_color(svg_text: str) -> str:
    """Replace hardcoded black with currentColor for dark-mode adaptation."""
    svg_text = _BLACK_FILL_RE.sub('fill="currentColor"', svg_text)
    svg_text = _BLACK_STROKE_RE.sub('stroke="currentColor"', svg_text)
    return svg_text
```

#### Task 7.3 — Implement rule 3: viewBox enforcement

**Action:**

```python
_WIDTH_RE: Final = re.compile(r'\bwidth="([0-9.]+)(pt|px)?"')
_HEIGHT_RE: Final = re.compile(r'\bheight="([0-9.]+)(pt|px)?"')
_VIEWBOX_RE: Final = re.compile(r'\bviewBox="')

def enforce_viewbox(svg_text: str) -> str:
    """Strip pt units, force viewBox if missing."""
    width_match = _WIDTH_RE.search(svg_text)
    height_match = _HEIGHT_RE.search(svg_text)
    has_viewbox = bool(_VIEWBOX_RE.search(svg_text))

    if width_match and height_match:
        w = float(width_match.group(1))
        h = float(height_match.group(1))
        # Strip pt units always
        svg_text = _WIDTH_RE.sub(f'width="{w:g}"', svg_text, count=1)
        svg_text = _HEIGHT_RE.sub(f'height="{h:g}"', svg_text, count=1)
        # Inject viewBox if absent
        if not has_viewbox:
            svg_text = svg_text.replace(
                "<svg ", f'<svg viewBox="0 0 {w:g} {h:g}" ', 1
            )
    return svg_text
```

#### Task 7.4 — Implement rule 4: SVGO conservative

**Action:** SVGO is a Node.js tool. Either:
- (A) Invoke it via `subprocess` — adds Node dependency.
- (B) Use a Python-native equivalent (`scour`, `pylsd`) — less mature.
- (C) Skip SVGO for v1, rely on the three custom rules + dvisvgm's own
  output cleanliness.

**Recommended for v1:** Option C (skip SVGO). Add a TODO note for
revisit in v1.1.

**Verify:** Phase 7 still produces clean SVG without SVGO.

#### Task 7.5 — Wire postprocessing into the pipeline

**Action:** In `render_cache.py` (or the dispatcher), after each adapter's
`render()` returns, apply postprocessing:

```python
svg_text = out_path.read_text(encoding="utf-8")
svg_text = postprocess.prefix_ids(svg_text, cache_hash)
svg_text = postprocess.substitute_current_color(svg_text)
svg_text = postprocess.enforce_viewbox(svg_text)
out_path.write_text(svg_text, encoding="utf-8")
```

#### Task 7.6 — Re-render existing cache to apply hardening

**Action:**
```bash
for f in mSB3-4_reals mSB5-2_partial mLA5-1_eigenvalues mSB3-5_complex; do
    python3 /Users/cs/Obsidian/_/resources/scripts/python_single/render_cache.py \
        /Users/cs/Obsidian/_/kn/math/concepts/$f.md --force
done
```

#### Task 7.7 — Verify hardening on real outputs

**Action:**
```bash
cd /Users/cs/Obsidian/_/attachments/cache/tikz/

# Rule 1: IDs prefixed
grep -l 'id="g1-' *.svg          # → empty (no unprefixed dvisvgm IDs)
grep -l 'id="[0-9a-f]\{6\}__' *.svg | wc -l  # → 5 (all files)

# Rule 2: currentColor present, hardcoded black absent
grep -c 'currentColor' mSB3-4_reals__1__*.svg   # → ≥1
grep -c 'fill="#000000"' mSB3-4_reals__1__*.svg # → 0

# Rule 3: viewBox present, no pt units
grep -c 'viewBox=' mSB3-4_reals__1__*.svg       # → 1
grep -c '"[0-9.]*pt"' mSB3-4_reals__1__*.svg    # → 0
```

#### Task 7.8 — Visual dark mode test

**Action:** Open one cached SVG file in Obsidian. Toggle dark mode.

**Verify:** Diagram lines/text adapt to dark mode foreground color
(not stuck on hardcoded black).

#### Common mistakes (Phase 7)

- **Replacing color in raster image data**: a `<image>` element with
  base64 data containing the bytes "000000" should NOT be touched. Limit
  regex to attribute contexts (`fill="..."`, `stroke="..."`).
- **Stripping `cm` or `mm` units instead of `pt`**: lualatex+dvisvgm
  always uses `pt`. Don't generalize unnecessarily.
- **Running postprocess BEFORE writing to cache** vs after: must run
  before, otherwise cache hits return unprocessed SVG.

#### Exit criteria

- Acceptance criteria 8.16, 8.17, 8.18 verified.
- Visual dark mode test passes.

---

### Phase 8 — Plugin scaffold

**SPEC reference:** §6.1, §6.2.
**Effort:** 4–6 hours.
**Owner:** agent.
**Depends on:** Phase 2 done (cache schema known). Pre-flight 0.9–0.10.

#### Task 8.1 — Initialize plugin from template

**Action:**
```bash
mkdir -p /Users/cs/Obsidian/_/.obsidian/plugins/obsidian-render-cache
cd /Users/cs/Obsidian/_/.obsidian/plugins/obsidian-render-cache
# Use Obsidian sample plugin as starting point
git clone https://github.com/obsidianmd/obsidian-sample-plugin .
rm -rf .git README.md  # we'll rewrite
npm install
```

#### Task 8.2 — Set manifest

**Action:** Edit `manifest.json`:
```json
{
  "id": "obsidian-render-cache",
  "name": "Render Cache",
  "version": "0.1.0",
  "minAppVersion": "1.4.16",
  "description": "Display cached SVGs of TikZ/Graphviz/D2/LilyPond/SMILES code blocks. Renders happen via render_cache.py at save time.",
  "author": "cstelmach",
  "isDesktopOnly": false
}
```

#### Task 8.3 — Implement codeblock processors

**Action:** In `main.ts`:

```typescript
import { Plugin, MarkdownPostProcessorContext, Platform } from "obsidian";

const LANGUAGES = ["tikz", "graphviz", "d2", "lilypond", "smiles"];

export default class RenderCachePlugin extends Plugin {
    async onload() {
        for (const lang of LANGUAGES) {
            this.registerMarkdownCodeBlockProcessor(
                lang,
                async (source, el, ctx) => {
                    await this.displayCachedBlock(source, lang, el, ctx);
                },
            );
        }
    }

    async displayCachedBlock(
        source: string,
        lang: string,
        el: HTMLElement,
        ctx: MarkdownPostProcessorContext,
    ) {
        // Implementation per SPEC §6.2
        ...
    }
}
```

Compile with `npm run build`.

#### Task 8.4 — Implement hash + index lookup

**Action:** Port the Python normalize and hash logic to TypeScript:

```typescript
import { createHash } from "crypto";

function normalize(source: string, lang: string): string {
    let s = source.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
    // line-end whitespace
    s = s.split("\n").map(line => line.trimEnd()).join("\n");
    // collapse blank-line runs
    s = s.replace(/\n{3,}/g, "\n\n").trim();
    // strip TikZ comments
    if (lang === "tikz") {
        s = s.split("\n")
            .filter(l => !/^\s*[^\\]?%/.test(l))
            .join("\n");
    }
    return s;
}

function cacheKey(source: string, lang: string, attrs: object, preambleHash: string): string {
    const payload = normalize(source, lang) + "\x00"
                  + lang + "\x00"
                  + JSON.stringify(attrs, Object.keys(attrs).sort()) + "\x00"
                  + preambleHash;
    return createHash("sha256").update(payload).digest("hex").slice(0, 16);
}
```

Cross-test: TypeScript hash output must match Python `hash.py` output for
identical inputs. Add a fixture test.

#### Task 8.5 — Smoke test in Obsidian

**Action:** In Obsidian (developer-mode-enabled), reload the plugin
(Settings → Community plugins → Render Cache → toggle off/on).

**Verify:**
- Open a note with a cached TikZ block. Image displays.
- Open a note with a TikZ block that has NO cache. Placeholder shows.
- Source mode shows the original code block; reading mode shows the SVG.

#### Common mistakes (Phase 8)

- **Hash divergence Python vs TypeScript**: byte-encoding, JSON key
  ordering, or normalization rules diverge silently. Always run the
  fixture test.
- **Trying to use `<img src="path/to/file.svg">` directly**: iOS blocks
  this. Use `app.vault.adapter.getResourcePath(…)` (research finding).
- **Forgetting `Platform.isMobile`** check: mobile must auto-degrade to
  cache-only mode.

#### Exit criteria

- Acceptance criterion 8.11 met for desktop.
- Plugin loads and registers all 5 codeblock processors.
- Cache hit displays SVG; cache miss shows placeholder.

---

### Phase 9 — Plugin commands and modes

**SPEC reference:** §6.3, §6.4, §6.5.
**Effort:** 4–6 hours.
**Owner:** agent.
**Depends on:** Phase 8.

Tasks: implement all 7 commands from SPEC §6.4. Implement settings UI
from §6.5. Implement mode switching from §6.3.

**Acceptance criteria covered:** 8.12, 8.13.

---

### Phase 10 — Plugin error display + status bar

**SPEC reference:** §6.6, §6.7.
**Effort:** 2–3 hours.
**Owner:** agent.
**Depends on:** Phase 8.

Tasks: implement inline error block rendering when index entry has
captured a render error. Implement status bar item.

**Acceptance criterion covered:** 8.21.

---

### Phase 11 — iOS validation (USER-DRIVEN)

**SPEC reference:** §1.1 (mobile crash motivation).
**Effort:** 1–2 hours user time.
**Owner:** user.
**Depends on:** Phases 1, 7, 8 done. iCloud sync of `.obsidian/` to phone.

#### Task 11.1 — User installs plugin on phone

User-side action: open Obsidian on iOS, Settings → Community plugins,
enable "Render Cache."

#### Task 11.2 — User opens previously-crashing notes

User-side test: open `kn/math/concepts/mSB5-2_partial.md` on phone.
Open `kn/math/concepts/_TIKZ_TEST_mSB5-2.md` on phone (the original
crash trigger).

**Acceptance criteria:** 8.14 (no crash), 8.15 (math correctly
positioned).

#### Task 11.3 — User reports findings

Findings → `PROGRESS.md` log entry.

If findings reveal sync issues (cache not present on mobile despite
desktop having it), proceed to Phase 11.4.

#### Task 11.4 — Sync resolution (if needed)

Options:
1. Wait for iCloud to sync `.obsidian/plugins/.../cache/` (unreliable per
   research; may not happen).
2. Switch to Obsidian Sync (paid, reliable).
3. Workaround: temporarily move cache to `attachments/cache/render/`
   (vault-synced) for mobile use; document as a known limitation.

User chooses; logged in PROGRESS.md.

#### Exit criteria

- Mobile no-crash verified on at least 3 representative files.
- SVG fidelity confirmed.

---

### Phase 12 — Migration tool: legacy → new layout

**SPEC reference:** §3.3 (locations); acceptance criterion 8.19.
**Effort:** 2–3 hours.
**Owner:** agent.
**Depends on:** Phases 1, 8.

#### Task 12.1 — Write migration script

**Action:** New script `migrate_to_render_cache.py`:

```python
"""One-shot migration from attachments/cache/tikz/ to
.obsidian/plugins/obsidian-render-cache/cache/v1/<note-path>/."""

# 1. Walk attachments/cache/tikz/
# 2. For each *.svg, parse note stem from filename
# 3. Move file to new location
# 4. Update markdown image refs to new path
# 5. Update index.json
# 6. Remove now-empty old dir
```

#### Task 12.2 — Dry-run migration

**Action:**
```bash
python3 migrate_to_render_cache.py --dry-run
```

**Verify:** Reports planned moves; no FS changes.

#### Task 12.3 — Execute migration

**Action:**
```bash
python3 migrate_to_render_cache.py
```

**Verify:**
- All cached files moved to new location.
- All markdown refs updated.
- Old `attachments/cache/tikz/` is empty (or removed).
- Index.json populated.

#### Task 12.4 — Sweep legacy PNG files

**Action:**
```bash
ls /Users/cs/Obsidian/_/attachments/cache/tikz/*.png 2>/dev/null
# If any remain (non-migrated), sweep:
rm /Users/cs/Obsidian/_/attachments/cache/tikz/*.png
```

#### Exit criteria

- Acceptance criterion 8.19 met.
- Old layout cleaned up.

---

### Phase 13 — Documentation

**Effort:** 2–3 hours.
**Owner:** agent.
**Depends on:** Phases 1–12 substantially done.

Deliverables:
- `.obsidian/plugins/obsidian-render-cache/README.md` — user-facing plugin
  README
- `resources/scripts/python_single/render_cache/CLAUDE.md` — agent-facing
  package documentation (per vault convention)
- Update `docs/specs/render-cache/PROGRESS.md` final summary
- Update `CLAUDE.md` (root) with section pointing to render-cache as
  the canonical TikZ pipeline

---

### Phase 14 — OPTIONAL: gboyd068/SwiftLaTeX hands-on eval

**SPEC reference:** §10.4, §11.8.
**Effort:** ~1 hour.
**Owner:** agent + user.
**Depends on:** Phases 1–11 done. Only triggered if v1 has unresolved
gaps that SwiftLaTeX might fix.

This phase is OPT-IN. Runs only when:
- v1 acceptance criteria pass except for some specific gap (e.g., a
  TikZ block that even native lualatex can't render).
- AND the user decides to invest the time.

If triggered: install gboyd068/obsidian-swiftlatex-render in a throwaway
test vault, render the user's three hardest blocks, compare output to
Path C output, report findings to `/tmp/`. Decision logged in PROGRESS.md.

If results are favorable AND v1 has gaps: future SPEC for hybrid
(Path C primary, SwiftLaTeX fallback for unrendererable blocks).

If results are unfavorable OR v1 has no gaps: gboyd068 mention stays
sidebar; no further work.

---

## Decision Tree (Quick Reference)

```
START
  │
  ├─ Pre-flight (mandatory) all pass? ─── NO ──► Stop. Resolve. Tell user.
  │       │ YES
  │       ▼
  │
  ├─ Phase 1 verify (§8.1)?  ── FAIL ──► Stop. Troubleshoot dvisvgm.
  │       │ PASS
  │       ▼
  ├─ Phase 2 done?           ── FAIL ──► Re-attempt restructure.
  │       │ PASS
  │       ▼
  ├─ Phases 3-6 (parallel)? ── ANY FAIL ──► Stop on that adapter. Triage.
  │       │ ALL PASS
  │       ▼
  ├─ Phase 7 hardening verified (§8.16-18)? ── FAIL ──► Re-check regex rules.
  │       │ PASS
  │       ▼
  ├─ Phase 8 plugin loads?   ── FAIL ──► Check Obsidian dev console.
  │       │ PASS
  │       ▼
  ├─ Phase 9-10 commands work? ── FAIL ──► Per-command triage.
  │       │ PASS
  │       ▼
  ├─ Phase 12 migration done? ── FAIL ──► Restore from git pre-migration commit.
  │       │ PASS
  │       ▼
  ├─ Phase 11 (USER) iOS no-crash?  ── FAIL ──► Phase 11.4 sync triage.
  │       │ PASS
  │       ▼
  ├─ Phase 13 docs written?
  │       │ DONE
  │       ▼
  ├─ Phase 14 needed?
  │     ├─ YES (gap exists) ──► run optional eval
  │     └─ NO ──► v1 SHIPPED
  └─ STOP.
```

---

## Acceptance Criteria Traceability

| Criterion | Verified in Phase |
|---|---|
| 8.1 (TikZ → SVG) | 1 |
| 8.2 (Graphviz) | 3 |
| 8.3 (D2) | 4 |
| 8.4 (LilyPond) | 5 |
| 8.5 (SMILES) | 6 |
| 8.6 (idempotent re-run) | 1 + 2 |
| 8.7 (--force) | 1 + 2 |
| 8.8 (hash invalidation) | 2 |
| 8.9 (renderer-version namespace) | 7 |
| 8.10 (sweep) | 12 |
| 8.11 (plugin display) | 8 |
| 8.12 (refresh-block command) | 9 |
| 8.13 (cache status) | 9 |
| 8.14 (iOS no crash) | 11 |
| 8.15 (iOS SVG fidelity) | 11 |
| 8.16 (ID prefix) | 7 |
| 8.17 (currentColor) | 7 |
| 8.18 (viewBox) | 7 |
| 8.19 (legacy migration) | 12 |
| 8.20 (preamble hash cascade) | 2 + 7 |
| 8.21 (inline error display) | 10 |

---

## Rollback Procedures

| What to undo | How |
|---|---|
| Phase 1 SVG migration broke things | `git revert` the Phase 1 commit; existing PNG cache remains usable; legacy `tikz_cache.py` still functional |
| Phase 2 restructure introduced bugs | `git revert`; old `tikz_cache.py` is intact in same commit |
| Phase 7 postprocess broke an SVG visually | Disable the offending rule (`applyHardening: false` in plugin settings) OR comment out the rule in Python; re-render |
| Phase 8 plugin breaks Obsidian | Disable plugin in Settings → Community plugins; remove `.obsidian/plugins/obsidian-render-cache/` if needed |
| Phase 12 migration moved files wrong | `git revert`; cached SVGs restored to `attachments/cache/tikz/`; markdown refs reverted |

The vault's auto-backup commits every ~10 minutes. Before any destructive
phase, check `git log --oneline -5` and consider an explicit commit
checkpoint.

---

## Critical Files Map

```
/Users/cs/Obsidian/_/
├── docs/specs/render-cache/
│   ├── SPEC.md                                     ← design source-of-truth
│   ├── PLAN.md                                     ← THIS file
│   └── PROGRESS.md                                 ← created when impl starts
│
├── resources/scripts/python_single/
│   ├── tikz_cache.py                               ← LEGACY shim after Phase 2
│   ├── render_cache.py                             ← NEW canonical CLI (Phase 2)
│   ├── render_cache/                               ← NEW package (Phase 2)
│   │   ├── __init__.py
│   │   ├── adapters/
│   │   │   ├── base.py
│   │   │   ├── tikz.py                            (Phase 2)
│   │   │   ├── graphviz.py                        (Phase 3)
│   │   │   ├── d2.py                              (Phase 4)
│   │   │   ├── lilypond.py                        (Phase 5)
│   │   │   └── smiles.py                          (Phase 6)
│   │   ├── normalize.py                            (Phase 2)
│   │   ├── hash.py                                 (Phase 2)
│   │   ├── index.py                                (Phase 2)
│   │   ├── postprocess.py                          (Phase 2 skeleton, Phase 7 fill)
│   │   ├── markdown_io.py                          (Phase 2)
│   │   └── cache_paths.py                          (Phase 2)
│   └── migrate_to_render_cache.py                  (Phase 12)
│
├── .obsidian/plugins/obsidian-render-cache/        ← created Phase 8
│   ├── manifest.json
│   ├── main.js                                     ← bundled TS
│   ├── styles.css
│   └── cache/
│       ├── index.json
│       └── v1/<note-path>/<idx>__<hash16>.svg
│
├── kn/math/concepts/
│   ├── _RENDER_TEST_graphviz.md                    (Phase 3)
│   ├── _RENDER_TEST_d2.md                          (Phase 4)
│   ├── _RENDER_TEST_lilypond.md                    (Phase 5)
│   └── _RENDER_TEST_smiles.md                      (Phase 6)
│
└── attachments/cache/tikz/                         ← LEGACY; emptied Phase 12
```

---

## Honest Scope Notes

- **No file watcher / auto-render daemon.** Manual CLI + plugin-on-save
  is sufficient for personal use.
- **Hash collisions theoretical, not practical.** 16 hex chars at 600
  block scale = 4×10⁻¹⁵.
- **Mobile sync is a known limitation.** `.obsidian/plugins/.../cache/`
  may not sync via iCloud reliably; Obsidian Sync (paid) is the only
  guaranteed path. Document; do not pretend.
- **Animations explicitly out.** Future SPEC if interest develops.
- **gboyd068 deferred.** Only revisited if v1 has unfixable gaps.

---

*End of PLAN.*
