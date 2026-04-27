"""
test_tikz_cache_phase1.py — Verifies Phase 1 rendering invariants (PNG → SVG via dvisvgm).

Reference: docs/specs/render-cache/SPEC.md §3.7 T1, PLAN.md Phase 1.

After Phase 2 the rendering invariants (no-fonts, libgs detection, bbox flag,
DVI output, timeouts, .svg filename) live in `render_cache/adapters/tikz.py`.
The static tier therefore inspects the ADAPTER source, not the deprecated
`tikz_cache.py` shim. The smoke tier invokes the new CLI (`render_cache.py`).

Two tiers of tests:
  - Static tier: parses the adapter source, checks constants and call sites.
  - Smoke tier: invokes the CLI against a real cached file and verifies the
                produced SVG. Marked `@pytest.mark.slow` and gated by the
                presence of dvisvgm + lualatex (skipped otherwise).

Run all:        pytest -v
Skip smoke:     pytest -v -m "not slow"
Smoke only:     pytest -v -m slow
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ADAPTER = Path("/Users/cs/Obsidian/_/resources/scripts/python_single/render_cache/adapters/tikz.py")
CLI = Path("/Users/cs/Obsidian/_/resources/scripts/python_single/render_cache.py")
SMOKE_MD = Path("/Users/cs/Obsidian/_/kn/math/concepts/mSB3-4_reals.md")
CACHE_DIR = Path("/Users/cs/Obsidian/_/attachments/cache/tikz")


def _strip_docstrings_and_comments(source: str) -> str:
    """Return the ``source`` with triple-quoted docstrings and ``#`` comments
    removed. Used by tests that assert on executable code only."""
    s = re.sub(r'"""(.*?)"""', "", source, flags=re.DOTALL)
    s = re.sub(r"'''(.*?)'''", "", s, flags=re.DOTALL)
    s = "\n".join(
        ln for ln in s.splitlines() if not ln.lstrip().startswith("#")
    )
    return s


# ---------------------------------------------------------------------------
# Static tier — fast checks against the source file.

@pytest.fixture(scope="module")
def source() -> str:
    assert ADAPTER.exists(), f"Adapter not found: {ADAPTER}"
    return ADAPTER.read_text(encoding="utf-8")


def test_adapter_imports_cleanly(source: str) -> None:
    """The adapter file must be syntactically valid Python."""
    import ast
    ast.parse(source)  # raises SyntaxError on failure


def test_pdftoppm_call_removed(source: str) -> None:
    """No active call to pdftoppm. Stripped from the render path entirely."""
    # Allow the literal in a comment for historical context, but no active call.
    code_lines = [
        ln for ln in source.splitlines()
        if not ln.lstrip().startswith("#")
    ]
    code = "\n".join(code_lines)
    assert "pdftoppm" not in code, (
        "pdftoppm reference found in active code (Phase 1 must replace it with dvisvgm)"
    )


def test_pdftoppm_timeout_constant_removed(source: str) -> None:
    """PDFTOPPM_TIMEOUT_S must be deleted (no longer used)."""
    assert "PDFTOPPM_TIMEOUT_S" not in source, (
        "PDFTOPPM_TIMEOUT_S constant still defined; should be removed in Phase 1"
    )


def test_dpi_constant_removed(source: str) -> None:
    """DPI was a pdftoppm-only constant. Should be removed; dvisvgm is resolution-independent."""
    assert not re.search(r"^\s*DPI\s*=", source, re.MULTILINE), (
        "DPI = ... constant still defined; should be removed (SVG is resolution-independent)"
    )


def test_dvisvgm_invocation_present(source: str) -> None:
    """A subprocess call to dvisvgm must exist."""
    assert "dvisvgm" in source, "dvisvgm not invoked anywhere in the script"


def test_dvisvgm_no_fonts_flag(source: str) -> None:
    """SPEC §3.7 T1: --no-fonts is mandatory (path-only output, no font references)."""
    assert "--no-fonts" in source, (
        "--no-fonts flag missing — required by SPEC §3.7 T1"
    )


def test_libgs_path_detection_present(source: str) -> None:
    """The script must detect a Ghostscript shared library and pass it via
    --libgs=. Without libgs, dvisvgm silently drops TikZ's PostScript-special
    drawing commands → text-only SVGs with no geometry. Regression: 2026-04-27.
    """
    assert "LIBGS_PATH" in source, "LIBGS_PATH detection must be present"
    assert "--libgs=" in source, "--libgs= flag must appear in the dvisvgm invocation"
    assert "DVISVGM_LIBGS" in source, "DVISVGM_LIBGS env override must be supported"


def test_no_bbox_preview_flag(source: str) -> None:
    """`--bbox=preview` is for the LaTeX `preview` package, NOT `standalone`.
    Mixing it with `--exact-bbox` produces a degenerate 13pt bbox that clips
    most TikZ content. Regression: 2026-04-27.

    We check the *executable* code only — docstrings/comments may legitimately
    mention the flag while explaining why we do NOT pass it.
    """
    code = _strip_docstrings_and_comments(source)
    assert "--bbox=preview" not in code, (
        "--bbox=preview is for the `preview` LaTeX package; we use `standalone`. "
        "Use --bbox=min instead."
    )


def test_lualatex_dvi_output_format(source: str) -> None:
    """lualatex must emit DVI (not PDF) for dvisvgm to consume."""
    assert "-output-format=dvi" in source or "--output-format=dvi" in source, (
        "lualatex must use -output-format=dvi to produce DVI for dvisvgm"
    )


def test_dvisvgm_timeout_constant_present(source: str) -> None:
    """A DVISVGM_TIMEOUT_S constant must exist (per PLAN Task 1.2)."""
    assert re.search(r"^\s*DVISVGM_TIMEOUT_S\s*=", source, re.MULTILINE), (
        "DVISVGM_TIMEOUT_S constant must be defined"
    )


def test_lualatex_timeout_still_present(source: str) -> None:
    """LUALATEX_TIMEOUT_S preserved (no scope creep)."""
    assert re.search(r"^\s*LUALATEX_TIMEOUT_S\s*=", source, re.MULTILINE), (
        "LUALATEX_TIMEOUT_S removed accidentally — still needed"
    )


def test_svg_extension_in_cache_filename(source: str) -> None:
    """Cache filename pattern must use .svg, not .png."""
    # Look for the cached-name pattern: {stem}__{idx}__{hash}.svg
    assert re.search(r'\.svg["\'`]', source), (
        "No .svg literal found — cache filename pattern must produce .svg"
    )


def test_no_active_png_extension_in_render_path(source: str) -> None:
    """No `.png` literal in the adapter's active rendering / cache path code."""
    code_lines = [
        ln for ln in source.splitlines()
        if not ln.lstrip().startswith("#")
    ]
    code = "\n".join(code_lines)
    # Adapter must have NO .png literal whatsoever — output is .svg only.
    bare_png_construction = re.findall(r"f?[\"'][^\"']*\.png[\"']", code)
    assert len(bare_png_construction) == 0, (
        f"Found .png string literals in adapter: {bare_png_construction}"
    )


# ---------------------------------------------------------------------------
# Smoke tier — exercise the script end-to-end on a real file.

DVISVGM = shutil.which("dvisvgm")
LUALATEX = shutil.which("lualatex")
SMOKE_REQUIREMENTS = (DVISVGM, LUALATEX, SMOKE_MD.exists())


@pytest.mark.slow
@pytest.mark.skipif(
    not all(SMOKE_REQUIREMENTS),
    reason=f"smoke prereq missing: dvisvgm={DVISVGM}, lualatex={LUALATEX}, file={SMOKE_MD.exists()}",
)
def test_smoke_render_produces_path_only_svg(tmp_path: Path) -> None:
    """End-to-end: invoke the new CLI with --force on the canonical test file.
    Verify SVG produced, contains <path>, contains no <text>, and the markdown
    ref was rewritten to .svg.
    """
    # Snapshot the markdown so we can restore if the test interrupts.
    md_snapshot = SMOKE_MD.read_text(encoding="utf-8")

    try:
        result = subprocess.run(
            [sys.executable, str(CLI), str(SMOKE_MD), "--force"],
            capture_output=True, text=True, timeout=180,
        )
        assert result.returncode == 0, (
            f"Script failed (exit {result.returncode}). "
            f"stdout=\n{result.stdout}\nstderr=\n{result.stderr}"
        )

        # 1. SVG exists at expected path
        svgs = sorted(CACHE_DIR.glob(f"{SMOKE_MD.stem}__1__*.svg"))
        assert len(svgs) == 1, f"Expected 1 SVG for {SMOKE_MD.stem}, got {svgs}"
        svg = svgs[0]

        # 2. SVG file size is in plausible range (5 KB – 2 MB)
        size = svg.stat().st_size
        assert 5_000 < size < 2_000_000, (
            f"SVG size {size} outside plausible range — likely incomplete render"
        )

        # 3. SVG is path-only: no <text> elements (--no-fonts vectorized them)
        svg_text = svg.read_text(encoding="utf-8")
        assert "<text" not in svg_text, (
            "SVG contains <text> — --no-fonts may not be applied"
        )
        path_count = svg_text.count("<path")
        # mSB3-4_reals draws an axis with arrowheads, 7 ticks, a curve, 4
        # circle markers, 4 arrows, a rounded rectangle, dashed lines — many
        # dozens of <path> elements. <50 means PostScript-specials weren't
        # rendered (libgs missing or wrong --bbox flag); see 2026-04-27 fix.
        assert path_count >= 50, (
            f"SVG has only {path_count} <path> elements — TikZ geometry "
            "appears not rendered. Check that LIBGS_PATH is detected."
        )

        # 4. Markdown ref was rewritten to .svg with a hex hash. Phase 2 uses
        # the canonical 16-char SHA-256 prefix per SPEC §3.7 T8; legacy 8-char
        # hashes from Phase 1 are also tolerated for transition compatibility.
        new_md = SMOKE_MD.read_text(encoding="utf-8")
        ref_re = re.compile(
            rf"!\[\[{re.escape(SMOKE_MD.stem)}__1__[0-9a-f]{{8,}}\.svg\|tikz-cache\]\]"
        )
        assert ref_re.search(new_md), (
            f"Markdown ref not updated to .svg in {SMOKE_MD.name}"
        )

    finally:
        # Best-effort restore if the script left the markdown in an inconsistent state.
        # (We intentionally do NOT restore on success — the .svg ref is the desired post-condition.)
        if SMOKE_MD.read_text(encoding="utf-8") != md_snapshot:
            # Did the script update the ref correctly? Then keep changes. Else revert.
            new_text = SMOKE_MD.read_text(encoding="utf-8")
            if "tikz-cache" in new_text and ".svg|tikz-cache" not in new_text:
                SMOKE_MD.write_text(md_snapshot, encoding="utf-8")
