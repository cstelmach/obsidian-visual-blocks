"""
test_d2_adapter.py — Verifies Phase 4 (Add D2 adapter).

References: SPEC §5 Phase 4 (AC4.1-AC4.3), §3.4 (RendererAdapter contract).
PLAN §Phase 4. The shape mirrors Phase 3's graphviz adapter tests.

Three tiers:
  - Structure tier: adapter file exists, importable, registered in REGISTRY
  - Behavior tier: contract semantics, markdown_io recognizes ```d2 fences
  - Integration tier (slow): actually invokes ``d2`` on a small graph

Run all:           pytest tests/test_d2_adapter.py -v
Run fast only:     pytest tests/test_d2_adapter.py -v -m "not slow"
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
SANDBOX_MD = REPO_ROOT / "kn/math/concepts/_RENDER_TEST_d2.md"

# Make the package importable inside the test process.
if str(PYTHON_SINGLE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SINGLE))


# ---------------------------------------------------------------------------
# Structure tier.

def test_d2_adapter_module_exists() -> None:
    """PLAN Phase 4: render_cache/adapters/d2.py present."""
    assert (RENDER_CACHE_PKG / "adapters" / "d2.py").exists(), (
        "render_cache/adapters/d2.py missing — Phase 4 not yet done."
    )


def test_d2_adapter_importable() -> None:
    """No heavy I/O or shell-out at import time."""
    from render_cache.adapters.d2 import D2Adapter  # noqa: F401


# ---------------------------------------------------------------------------
# Behavior tier — adapter contract (SPEC §3.4).

def test_d2_adapter_implements_contract() -> None:
    from render_cache.adapters.base import RendererAdapter
    from render_cache.adapters.d2 import D2Adapter
    a = D2Adapter()
    assert isinstance(a, RendererAdapter)
    assert a.language == "d2"
    assert isinstance(a.render_budget_seconds, int)
    assert a.render_budget_seconds > 0


def test_d2_adapter_render_budget_per_decision() -> None:
    """D4.3: render_budget_seconds = 15 (mirror dot=10 + headroom for ELK
    first-compile cold start)."""
    from render_cache.adapters.d2 import D2Adapter
    assert D2Adapter().render_budget_seconds == 15


def test_d2_adapter_preamble_is_empty() -> None:
    """D2 source is self-contained — no preamble concept (D4.2 mirrors D3.2)."""
    from render_cache.adapters.d2 import D2Adapter
    assert D2Adapter().preamble_text == ""


# ---------------------------------------------------------------------------
# Behavior tier — registry.

def test_registry_has_d2() -> None:
    """SPEC §3.4: REGISTRY keyed by language tag. Phase 4 must register."""
    from render_cache.adapters import REGISTRY
    assert "d2" in REGISTRY, "REGISTRY['d2'] missing"
    assert REGISTRY["d2"].language == "d2"


def test_registry_keeps_tikz_and_graphviz_intact() -> None:
    """Phase 4 must not remove or shadow Phase 2's TikZ adapter or
    Phase 3's Graphviz adapter."""
    from render_cache.adapters import REGISTRY
    assert "tikz" in REGISTRY
    assert REGISTRY["tikz"].language == "tikz"
    assert "graphviz" in REGISTRY
    assert REGISTRY["graphviz"].language == "graphviz"


# ---------------------------------------------------------------------------
# Behavior tier — markdown_io recognises ```d2 fence.

def test_markdown_io_finds_d2_block() -> None:
    """find_blocks must recognise ```d2 fences post-Phase-4."""
    from render_cache.markdown_io import find_blocks
    content = "Pre\n\n```d2\na -> b\n```\n\nPost"
    blocks = find_blocks(content)
    assert len(blocks) == 1
    assert blocks[0].language == "d2"
    assert blocks[0].fence_lang == "d2"
    assert "a -> b" in blocks[0].source


def test_markdown_io_finds_mixed_tikz_graphviz_d2() -> None:
    """All three supported languages in one file must all be detected,
    in document order."""
    from render_cache.markdown_io import find_blocks
    content = (
        "```graphviz\ndigraph A { x -> y; }\n```\n\n"
        "```d2\nfoo -> bar\n```\n\n"
        "```tikz\n\\draw (0,0) circle (1);\n```\n"
    )
    blocks = find_blocks(content)
    assert len(blocks) == 3
    assert blocks[0].language == "graphviz"
    assert blocks[1].language == "d2"
    assert blocks[2].language == "tikz"


def test_markdown_io_d2_block_span_correct() -> None:
    """span must cover the entire fenced block (including closing ```)."""
    from render_cache.markdown_io import find_blocks
    content = "X\n```d2\na -> b\n```\nY"
    blocks = find_blocks(content)
    s, e = blocks[0].span
    assert content[s:s + len("```d2")] == "```d2"
    assert content[e - 3:e] == "```"


# ---------------------------------------------------------------------------
# Behavior tier — dispatcher fence-detection.

def test_find_all_md_with_blocks_includes_d2() -> None:
    """``find_all_md_with_blocks`` must scan for ```d2 blocks too,
    otherwise --all skips D2 files entirely."""
    import inspect
    from render_cache import find_all_md_with_blocks
    src = inspect.getsource(find_all_md_with_blocks)
    assert '"d2"' in src or "'d2'" in src, (
        "find_all_md_with_blocks must include d2 in its fence-tag scan list."
    )


# ---------------------------------------------------------------------------
# Integration tier — actually invoke `d2`.

@pytest.fixture(scope="module")
def have_d2() -> bool:
    return shutil.which("d2") is not None


SIMPLE_D2 = "a -> b\nb -> c\na -> c\n"


@pytest.mark.slow
def test_d2_adapter_renders_simple_graph(have_d2: bool) -> None:
    """AC4.1: D2Adapter.render produces a valid SVG file with d2-typical
    structure (xmlns SVG, at least one drawing element)."""
    if not have_d2:
        pytest.skip("d2 not installed — install via `brew install d2`")
    from render_cache.adapters.d2 import D2Adapter
    a = D2Adapter()
    with tempfile.TemporaryDirectory() as tmp:
        wd = Path(tmp)
        out = a.render(SIMPLE_D2, attrs={}, workdir=wd)
        assert out.exists(), "Adapter returned a path that doesn't exist"
        assert out.suffix == ".svg"
        text = out.read_text(encoding="utf-8")
        assert "<svg" in text
        # d2 emits node shapes as <rect>/<ellipse>/<polygon> and edges as <path>.
        # At least one drawing element must be present.
        assert any(tag in text for tag in ("<rect", "<ellipse", "<polygon", "<path")), (
            f"Rendered SVG has no drawing elements:\n{text[:400]}"
        )


@pytest.mark.slow
def test_d2_adapter_raises_on_invalid_source(have_d2: bool) -> None:
    """Adapter must surface d2's compile failure as a RenderError, not silently
    produce a broken SVG."""
    if not have_d2:
        pytest.skip("d2 not installed")
    from render_cache.adapters.base import RenderError
    from render_cache.adapters.d2 import D2Adapter
    a = D2Adapter()
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(RenderError):
            a.render("{ {{{ broken d2 syntax }}}\n", attrs={}, workdir=Path(tmp))


@pytest.mark.slow
def test_d2_cli_renders_sandbox(have_d2: bool) -> None:
    """AC4.1 + AC4.3: CLI on the test sandbox produces SVGs without error,
    second run is a cache hit (idempotent)."""
    if not have_d2:
        pytest.skip("d2 not installed")
    if not SANDBOX_MD.exists():
        pytest.skip(f"Test sandbox not present: {SANDBOX_MD}")

    # First run: render
    r1 = subprocess.run(
        [sys.executable, str(RENDER_CACHE_CLI), str(SANDBOX_MD)],
        capture_output=True, text=True, timeout=120,
    )
    assert r1.returncode == 0, (
        f"First render run failed:\nstdout={r1.stdout}\nstderr={r1.stderr}"
    )
    # Second run: should be cache hits
    r2 = subprocess.run(
        [sys.executable, str(RENDER_CACHE_CLI), str(SANDBOX_MD)],
        capture_output=True, text=True, timeout=120,
    )
    assert r2.returncode == 0
    assert "cache hit" in r2.stdout, (
        f"Second run did not report cache hit (idempotence broken):\n{r2.stdout}"
    )
