"""
test_graphviz_adapter.py — Verifies Phase 3 (Add Graphviz adapter).

References: SPEC §5 Phase 3 (AC3.1-AC3.4), §3.4 (RendererAdapter contract).
PLAN §Phase 3 (Tasks 3.1-3.3). The shape mirrors Phase 2's tikz adapter tests.

Three tiers:
  - Structure tier: adapter file exists, importable, registered in REGISTRY
  - Behavior tier: contract semantics, markdown_io recognizes ```graphviz fences
  - Integration tier (slow): actually invokes ``dot -Tsvg`` on a small graph

Run all:           pytest tests/test_graphviz_adapter.py -v
Run fast only:     pytest tests/test_graphviz_adapter.py -v -m "not slow"
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
SANDBOX_MD = REPO_ROOT / "kn/math/concepts/_RENDER_TEST_graphviz.md"

# Make the package importable inside the test process.
if str(PYTHON_SINGLE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SINGLE))


# ---------------------------------------------------------------------------
# Structure tier.

def test_graphviz_adapter_module_exists() -> None:
    """PLAN Task 3.2: render_cache/adapters/graphviz.py present."""
    assert (RENDER_CACHE_PKG / "adapters" / "graphviz.py").exists(), (
        "render_cache/adapters/graphviz.py missing — Phase 3 PLAN Task 3.2 not yet done."
    )


def test_graphviz_adapter_importable() -> None:
    """No heavy I/O or shell-out at import time."""
    from render_cache.adapters.graphviz import GraphvizAdapter  # noqa: F401


# ---------------------------------------------------------------------------
# Behavior tier — adapter contract (SPEC §3.4).

def test_graphviz_adapter_implements_contract() -> None:
    from render_cache.adapters.base import RendererAdapter
    from render_cache.adapters.graphviz import GraphvizAdapter
    a = GraphvizAdapter()
    assert isinstance(a, RendererAdapter)
    assert a.language == "graphviz"
    assert isinstance(a.render_budget_seconds, int)
    assert a.render_budget_seconds > 0


def test_graphviz_adapter_render_budget_per_spec() -> None:
    """AC3.4: PLAN says ``render_budget_seconds = 10`` for Graphviz."""
    from render_cache.adapters.graphviz import GraphvizAdapter
    assert GraphvizAdapter().render_budget_seconds == 10


def test_graphviz_adapter_preamble_is_empty() -> None:
    """Graphviz has no preamble concept — return empty string so the
    SPEC §3.7 T10 hash doesn't pull preamble bytes that don't exist."""
    from render_cache.adapters.graphviz import GraphvizAdapter
    assert GraphvizAdapter().preamble_text == ""


# ---------------------------------------------------------------------------
# Behavior tier — registry.

def test_registry_has_graphviz() -> None:
    """SPEC §3.4: REGISTRY keyed by language tag. Phase 3 must register."""
    from render_cache.adapters import REGISTRY
    assert "graphviz" in REGISTRY, "REGISTRY['graphviz'] missing"
    assert REGISTRY["graphviz"].language == "graphviz"


def test_registry_keeps_tikz_intact() -> None:
    """Phase 3 must not remove or shadow Phase 2's TikZ adapter."""
    from render_cache.adapters import REGISTRY
    assert "tikz" in REGISTRY
    assert REGISTRY["tikz"].language == "tikz"


# ---------------------------------------------------------------------------
# Behavior tier — markdown_io recognises ```graphviz fence.

def test_markdown_io_finds_graphviz_block() -> None:
    """find_blocks must recognise ```graphviz fences post-Phase-3."""
    from render_cache.markdown_io import find_blocks
    content = "Pre\n\n```graphviz\ndigraph G { a -> b; }\n```\n\nPost"
    blocks = find_blocks(content)
    assert len(blocks) == 1
    assert blocks[0].language == "graphviz"
    assert blocks[0].fence_lang == "graphviz"
    assert "digraph" in blocks[0].source


def test_markdown_io_finds_mixed_tikz_and_graphviz() -> None:
    """Multiple supported languages in one file must all be detected,
    in document order."""
    from render_cache.markdown_io import find_blocks
    content = (
        "```graphviz\ndigraph A { x -> y; }\n```\n\n"
        "```tikz\n\\draw (0,0) circle (1);\n```\n"
    )
    blocks = find_blocks(content)
    assert len(blocks) == 2
    assert blocks[0].language == "graphviz"
    assert blocks[1].language == "tikz"


def test_markdown_io_graphviz_block_span_correct() -> None:
    """span must cover the entire fenced block (including closing ```)."""
    from render_cache.markdown_io import find_blocks
    content = "X\n```graphviz\ndigraph { a }\n```\nY"
    blocks = find_blocks(content)
    s, e = blocks[0].span
    assert content[s:s + len("```graphviz")] == "```graphviz"
    assert content[e - 3:e] == "```"


# ---------------------------------------------------------------------------
# Behavior tier — dispatcher fence-detection.

def test_find_all_md_with_blocks_includes_graphviz() -> None:
    """``find_all_md_with_blocks`` must scan for ```graphviz blocks too,
    otherwise --all skips Graphviz files entirely."""
    import inspect
    from render_cache import find_all_md_with_blocks
    src = inspect.getsource(find_all_md_with_blocks)
    assert '"graphviz"' in src or "'graphviz'" in src, (
        "find_all_md_with_blocks must include graphviz in its fence-tag scan list."
    )


# ---------------------------------------------------------------------------
# Integration tier — actually invoke `dot`.

@pytest.fixture(scope="module")
def have_dot() -> bool:
    return shutil.which("dot") is not None


SIMPLE_DOT = "digraph G { a -> b; b -> c; a -> c; }"


@pytest.mark.slow
def test_graphviz_adapter_renders_simple_digraph(have_dot: bool) -> None:
    """AC3.1: GraphvizAdapter.render produces a valid SVG file with
    Graphviz-typical structure (xmlns SVG, at least one path or polygon)."""
    if not have_dot:
        pytest.skip("graphviz `dot` not installed — install via `brew install graphviz`")
    from render_cache.adapters.graphviz import GraphvizAdapter
    a = GraphvizAdapter()
    with tempfile.TemporaryDirectory() as tmp:
        wd = Path(tmp)
        out = a.render(SIMPLE_DOT, attrs={}, workdir=wd)
        assert out.exists(), "Adapter returned a path that doesn't exist"
        assert out.suffix == ".svg"
        text = out.read_text(encoding="utf-8")
        assert "<svg" in text
        # Graphviz emits node shapes as <ellipse> / <polygon> and edges as <path>.
        # At least one drawing element must be present.
        assert any(tag in text for tag in ("<ellipse", "<polygon", "<path")), (
            f"Rendered SVG has no drawing elements:\n{text[:400]}"
        )


@pytest.mark.slow
def test_graphviz_adapter_raises_on_invalid_dot(have_dot: bool) -> None:
    """Adapter must surface dot's failure as a RenderError, not silently produce
    a broken SVG."""
    if not have_dot:
        pytest.skip("graphviz `dot` not installed")
    from render_cache.adapters.base import RenderError
    from render_cache.adapters.graphviz import GraphvizAdapter
    a = GraphvizAdapter()
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(RenderError):
            a.render("digraph { a -> }  // syntax error", attrs={}, workdir=Path(tmp))


@pytest.mark.slow
def test_graphviz_cli_renders_sandbox(have_dot: bool) -> None:
    """AC3.1 + AC3.3: CLI on the test sandbox produces SVGs without error,
    second run is a cache hit (idempotent)."""
    if not have_dot:
        pytest.skip("graphviz `dot` not installed")
    if not SANDBOX_MD.exists():
        pytest.skip(f"Test sandbox not present: {SANDBOX_MD}")

    # First run: render
    r1 = subprocess.run(
        [sys.executable, str(RENDER_CACHE_CLI), str(SANDBOX_MD)],
        capture_output=True, text=True, timeout=60,
    )
    assert r1.returncode == 0, (
        f"First render run failed:\nstdout={r1.stdout}\nstderr={r1.stderr}"
    )
    # Second run: should be cache hits
    r2 = subprocess.run(
        [sys.executable, str(RENDER_CACHE_CLI), str(SANDBOX_MD)],
        capture_output=True, text=True, timeout=60,
    )
    assert r2.returncode == 0
    assert "cache hit" in r2.stdout, (
        f"Second run did not report cache hit (idempotence broken):\n{r2.stdout}"
    )
