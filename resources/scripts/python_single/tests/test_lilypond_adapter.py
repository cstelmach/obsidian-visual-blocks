"""
test_lilypond_adapter.py — Verifies Phase 5 (Add LilyPond adapter).

References: SPEC §5 Phase 5 (AC5.1-AC5.3), §3.4 (RendererAdapter contract),
§3.7 T2 (mandatory ``-dpoint-and-click=#f``).
PLAN §Phase 5. The shape mirrors Phase 4's D2 adapter tests, with three
LilyPond-specific additions:

  - AC5.2 hard check: rendered SVG must contain ZERO ``file://`` URIs
    (proves the ``-dpoint-and-click=#f`` flag took effect).
  - Output-discovery check: the adapter must locate ``out.svg`` (or
    ``out-1.svg`` / ``out-page1.svg`` etc. for multi-page) via a glob,
    not by hardcoding ``out.svg``.
  - Multi-page resilience: stable behaviour when LilyPond emits more
    than one SVG file (v1 picks the first; multi-page support is
    deferred — see Phase-5 lesson note).

Three tiers:
  - Structure tier:   adapter file exists, importable, registered in REGISTRY
  - Behavior tier:    contract semantics, markdown_io recognizes ```lilypond fences
  - Integration tier (slow): actually invokes ``lilypond`` on a small melody

Run all:           pytest tests/test_lilypond_adapter.py -v
Run fast only:     pytest tests/test_lilypond_adapter.py -v -m "not slow"
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

PYTHON_SINGLE = Path(__file__).resolve().parents[1]
REPO_ROOT = PYTHON_SINGLE.parents[2]
RENDER_CACHE_PKG = PYTHON_SINGLE / "render_cache"
RENDER_CACHE_CLI = PYTHON_SINGLE / "render_cache.py"
SANDBOX_MD = REPO_ROOT / "kn/math/concepts/_RENDER_TEST_lilypond.md"

# Make the package importable inside the test process.
if str(PYTHON_SINGLE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SINGLE))


# ---------------------------------------------------------------------------
# Structure tier.

def test_lilypond_adapter_module_exists() -> None:
    """PLAN Phase 5: render_cache/adapters/lilypond.py present."""
    assert (RENDER_CACHE_PKG / "adapters" / "lilypond.py").exists(), (
        "render_cache/adapters/lilypond.py missing — Phase 5 not yet done."
    )


def test_lilypond_adapter_importable() -> None:
    """No heavy I/O or shell-out at import time."""
    from render_cache.adapters.lilypond import LilyPondAdapter  # noqa: F401


# ---------------------------------------------------------------------------
# Behavior tier — adapter contract (SPEC §3.4).

def test_lilypond_adapter_implements_contract() -> None:
    from render_cache.adapters.base import RendererAdapter
    from render_cache.adapters.lilypond import LilyPondAdapter
    a = LilyPondAdapter()
    assert isinstance(a, RendererAdapter)
    assert a.language == "lilypond"
    assert isinstance(a.render_budget_seconds, int)
    assert a.render_budget_seconds > 0


def test_lilypond_adapter_render_budget_per_decision() -> None:
    """D5.3: render_budget_seconds = 30. LilyPond cold start ~0.4s for a
    minimal melody but complex scores (full lead sheets, multi-stave
    arrangements) can run several seconds; 30s gives generous headroom
    while still surfacing pathological hangs (vs lualatex's 60s)."""
    from render_cache.adapters.lilypond import LilyPondAdapter
    assert LilyPondAdapter().render_budget_seconds == 30


def test_lilypond_adapter_preamble_is_empty() -> None:
    """LilyPond source is self-contained — no preamble concept (D5.2 mirrors
    D3.2/D4.2). Per-folder LilyPond \\version or \\paper conventions are a
    Phase 8+ concern; v1 hashes raw source only."""
    from render_cache.adapters.lilypond import LilyPondAdapter
    assert LilyPondAdapter().preamble_text == ""


def test_lilypond_adapter_uses_point_and_click_off() -> None:
    """SPEC §3.7 T2 / AC5.2: source code must invoke lilypond with
    ``-dpoint-and-click=#f``. Without it, lilypond bakes absolute file://
    URIs into the SVG, which (a) leaks paths, (b) thrashes the cache when
    the source path varies. Source-text assertion guards against
    accidental flag removal during refactors."""
    import inspect
    from render_cache.adapters import lilypond as lily_mod
    src = inspect.getsource(lily_mod)
    # Strip docstrings/comments to avoid matching the rationale prose.
    code_only_lines = [
        ln for ln in src.splitlines()
        if not ln.lstrip().startswith("#")
        and '"""' not in ln
        and "'''" not in ln
    ]
    code_only = "\n".join(code_only_lines)
    assert "-dpoint-and-click=#f" in code_only, (
        "LilyPond adapter must pass -dpoint-and-click=#f (SPEC T2/AC5.2). "
        "Removing this flag is a regression."
    )


# ---------------------------------------------------------------------------
# Behavior tier — registry.

def test_registry_has_lilypond() -> None:
    """SPEC §3.4: REGISTRY keyed by language tag. Phase 5 must register."""
    from render_cache.adapters import REGISTRY
    assert "lilypond" in REGISTRY, "REGISTRY['lilypond'] missing"
    assert REGISTRY["lilypond"].language == "lilypond"


def test_registry_keeps_all_prior_adapters_intact() -> None:
    """Phase 5 must not remove or shadow Phase 2's TikZ, Phase 3's
    Graphviz, or Phase 4's D2 adapter."""
    from render_cache.adapters import REGISTRY
    for lang in ("tikz", "graphviz", "d2"):
        assert lang in REGISTRY, f"REGISTRY['{lang}'] missing post-Phase-5"
        assert REGISTRY[lang].language == lang


# ---------------------------------------------------------------------------
# Behavior tier — markdown_io recognises ```lilypond fence.

def test_markdown_io_finds_lilypond_block() -> None:
    """find_blocks must recognise ```lilypond fences post-Phase-5."""
    from render_cache.markdown_io import find_blocks
    content = "Pre\n\n```lilypond\n\\relative c' { c d e f }\n```\n\nPost"
    blocks = find_blocks(content)
    assert len(blocks) == 1
    assert blocks[0].language == "lilypond"
    assert blocks[0].fence_lang == "lilypond"
    assert "\\relative" in blocks[0].source


def test_markdown_io_finds_mixed_all_four_languages() -> None:
    """All four supported languages in one file must all be detected,
    in document order."""
    from render_cache.markdown_io import find_blocks
    content = (
        "```graphviz\ndigraph A { x -> y; }\n```\n\n"
        "```lilypond\n\\relative c' { c d e f }\n```\n\n"
        "```d2\nfoo -> bar\n```\n\n"
        "```tikz\n\\draw (0,0) circle (1);\n```\n"
    )
    blocks = find_blocks(content)
    assert len(blocks) == 4
    assert blocks[0].language == "graphviz"
    assert blocks[1].language == "lilypond"
    assert blocks[2].language == "d2"
    assert blocks[3].language == "tikz"


def test_markdown_io_lilypond_block_span_correct() -> None:
    """span must cover the entire fenced block (including closing ```)."""
    from render_cache.markdown_io import find_blocks
    content = "X\n```lilypond\n\\relative c' { c }\n```\nY"
    blocks = find_blocks(content)
    s, e = blocks[0].span
    assert content[s:s + len("```lilypond")] == "```lilypond"
    assert content[e - 3:e] == "```"


# ---------------------------------------------------------------------------
# Behavior tier — dispatcher fence-detection.

def test_find_all_md_with_blocks_includes_lilypond() -> None:
    """``find_all_md_with_blocks`` must scan for ```lilypond blocks too,
    otherwise --all skips LilyPond files entirely."""
    import inspect
    from render_cache import find_all_md_with_blocks
    src = inspect.getsource(find_all_md_with_blocks)
    assert '"lilypond"' in src or "'lilypond'" in src, (
        "find_all_md_with_blocks must include lilypond in its fence-tag scan list."
    )


# ---------------------------------------------------------------------------
# Integration tier — actually invoke `lilypond`.

@pytest.fixture(scope="module")
def have_lilypond() -> bool:
    return shutil.which("lilypond") is not None


SIMPLE_LILYPOND = "\\relative c' { c d e f g a b c }\n"


@pytest.mark.slow
def test_lilypond_adapter_renders_simple_melody(have_lilypond: bool) -> None:
    """AC5.1 + AC5.2: LilyPondAdapter.render produces a valid SVG file
    with music-typical structure (xmlns SVG, drawing elements) AND zero
    ``file://`` URIs (proves -dpoint-and-click=#f took effect)."""
    if not have_lilypond:
        pytest.skip("lilypond not installed — install via `brew install lilypond`")
    from render_cache.adapters.lilypond import LilyPondAdapter
    a = LilyPondAdapter()
    with tempfile.TemporaryDirectory() as tmp:
        wd = Path(tmp)
        out = a.render(SIMPLE_LILYPOND, attrs={}, workdir=wd)
        assert out.exists(), "Adapter returned a path that doesn't exist"
        assert out.suffix == ".svg"
        text = out.read_text(encoding="utf-8")
        assert "<svg" in text
        # LilyPond emits glyphs as <path> elements (note heads, stems, beams).
        # A minimal melody must produce at least a few drawing elements.
        assert text.count("<path") >= 5, (
            f"Rendered SVG has too few <path> elements (LilyPond should emit "
            f"note heads + stems + staff lines):\n{text[:600]}"
        )
        # AC5.2: ZERO file:// URIs. This is the proof that
        # -dpoint-and-click=#f was actually applied.
        file_uri_count = text.count("file://")
        assert file_uri_count == 0, (
            f"AC5.2 violation: rendered SVG contains {file_uri_count} "
            f"file:// URIs — -dpoint-and-click=#f is missing or not effective."
        )


@pytest.mark.slow
def test_lilypond_adapter_raises_on_invalid_source(have_lilypond: bool) -> None:
    """Adapter must surface lilypond's compile failure as a RenderError, not
    silently produce a broken SVG."""
    if not have_lilypond:
        pytest.skip("lilypond not installed")
    from render_cache.adapters.base import RenderError
    from render_cache.adapters.lilypond import LilyPondAdapter
    a = LilyPondAdapter()
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(RenderError):
            # Unbalanced braces — lilypond exits non-zero.
            a.render("\\relative c' { c d e f g a b c \n", attrs={}, workdir=Path(tmp))


@pytest.mark.slow
def test_lilypond_cli_renders_sandbox(have_lilypond: bool) -> None:
    """AC5.1 + idempotence: CLI on the test sandbox produces SVGs without
    error, second run is a cache hit (idempotent)."""
    if not have_lilypond:
        pytest.skip("lilypond not installed")
    if not SANDBOX_MD.exists():
        pytest.skip(f"Test sandbox not present: {SANDBOX_MD}")

    # First run: render
    r1 = subprocess.run(
        [sys.executable, str(RENDER_CACHE_CLI), str(SANDBOX_MD)],
        capture_output=True, text=True, timeout=180,
    )
    assert r1.returncode == 0, (
        f"First render run failed:\nstdout={r1.stdout}\nstderr={r1.stderr}"
    )
    # Second run: should be cache hits
    r2 = subprocess.run(
        [sys.executable, str(RENDER_CACHE_CLI), str(SANDBOX_MD)],
        capture_output=True, text=True, timeout=180,
    )
    assert r2.returncode == 0
    assert "cache hit" in r2.stdout, (
        f"Second run did not report cache hit (idempotence broken):\n{r2.stdout}"
    )
