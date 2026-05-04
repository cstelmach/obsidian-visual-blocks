"""
test_smiles_adapter.py — Verifies Phase 6 (Add RDKit / SMILES adapter).

References: SPEC §5 Phase 6 (AC6.1-AC6.3), §3.4 (RendererAdapter contract),
SPEC architecture diagram §3.2 (DISPATCH --> SM[SMILES adapter]).
PLAN §Phase 6.

Phase 6 differs structurally from Phases 3-5: SMILES rendering is **pure
Python via rdkit** (no subprocess shell-out). The adapter is the only v1
adapter that does NOT spawn an external process. Tests therefore mirror
Phase 5's shape but skip subprocess-only assertions.

Three tiers:
  - Structure tier:  adapter file exists, importable, registered in REGISTRY
  - Behavior tier:   contract semantics, markdown_io recognizes ```smiles fences
  - Integration tier (slow): actually calls rdkit + runs CLI on sandbox

Run all:           pytest tests/test_smiles_adapter.py -v
Run fast only:     pytest tests/test_smiles_adapter.py -v -m "not slow"
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

PYTHON_SINGLE = Path(__file__).resolve().parents[1]
REPO_ROOT = PYTHON_SINGLE.parents[2]
RENDER_CACHE_PKG = PYTHON_SINGLE / "render_cache"
RENDER_CACHE_CLI = PYTHON_SINGLE / "render_cache.py"
SANDBOX_MD = REPO_ROOT / "kn/math/concepts/_RENDER_TEST_smiles.md"

# Make the package importable inside the test process.
if str(PYTHON_SINGLE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SINGLE))


# ---------------------------------------------------------------------------
# Structure tier.

def test_smiles_adapter_module_exists() -> None:
    """PLAN Phase 6: render_cache/adapters/smiles.py present."""
    assert (RENDER_CACHE_PKG / "adapters" / "smiles.py").exists(), (
        "render_cache/adapters/smiles.py missing — Phase 6 not yet done."
    )


def test_smiles_adapter_importable() -> None:
    """No heavy I/O at import time. RDKit imports may be lazy or eager —
    either is acceptable, as long as the module loads."""
    from render_cache.adapters.smiles import SMILESAdapter  # noqa: F401


# ---------------------------------------------------------------------------
# Behavior tier — adapter contract (SPEC §3.4).

def test_smiles_adapter_implements_contract() -> None:
    from render_cache.adapters.base import RendererAdapter
    from render_cache.adapters.smiles import SMILESAdapter
    a = SMILESAdapter()
    assert isinstance(a, RendererAdapter)
    assert a.language == "smiles"
    assert isinstance(a.render_budget_seconds, int)
    assert a.render_budget_seconds > 0


def test_smiles_adapter_render_budget_per_decision() -> None:
    """D6.3: render_budget_seconds = 5. SMILES rendering is pure-Python
    rdkit calls; smoke-tested at 2.6 ms for caffeine. 5 s gives ~2000x
    headroom, surfaces pathological hangs (large polymers) without being
    so generous that CI hangs on a stuck call."""
    from render_cache.adapters.smiles import SMILESAdapter
    assert SMILESAdapter().render_budget_seconds == 5


def test_smiles_adapter_preamble_is_empty() -> None:
    """SMILES strings are self-contained — no preamble concept (D6.2 mirrors
    D3.2/D4.2/D5.2). Per-folder default-image-size or atom-numbering
    overrides are deferred to Phase 8+."""
    from render_cache.adapters.smiles import SMILESAdapter
    assert SMILESAdapter().preamble_text == ""


def test_smiles_adapter_uses_rdkit_chem_api() -> None:
    """SPEC §5 Phase 6 / SPEC §3.2 (architecture): SMILES adapter must use
    rdkit's Chem + Draw API (NOT a subprocess to obabel, openchem, or
    other CLI tools). Source-text guard against accidental refactor that
    introduces a shell-out path. Strips docstrings/comments before
    grepping per the Phase 1/2/5 helper pattern."""
    import inspect
    from render_cache.adapters import smiles as smiles_mod
    src = inspect.getsource(smiles_mod)
    code_only_lines = [
        ln for ln in src.splitlines()
        if not ln.lstrip().startswith("#")
        and '"""' not in ln
        and "'''" not in ln
    ]
    code_only = "\n".join(code_only_lines)
    assert "rdkit" in code_only, (
        "SMILES adapter must use rdkit (SPEC §5 Phase 6). 'rdkit' import "
        "missing — pure-Python contract violated."
    )
    assert "subprocess" not in code_only, (
        "SMILES adapter must NOT use subprocess (SPEC §5 Phase 6: "
        "pure-Python). Found subprocess reference."
    )


# ---------------------------------------------------------------------------
# Behavior tier — registry.

def test_registry_has_smiles() -> None:
    """SPEC §3.4: REGISTRY keyed by language tag. Phase 6 must register."""
    from render_cache.adapters import REGISTRY
    assert "smiles" in REGISTRY, "REGISTRY['smiles'] missing"
    assert REGISTRY["smiles"].language == "smiles"


def test_registry_keeps_all_prior_adapters_intact() -> None:
    """Phase 6 must not remove or shadow Phase 2's TikZ, Phase 3's
    Graphviz, Phase 4's D2, or Phase 5's LilyPond adapter."""
    from render_cache.adapters import REGISTRY
    for lang in ("tikz", "graphviz", "d2", "lilypond"):
        assert lang in REGISTRY, f"REGISTRY['{lang}'] missing post-Phase-6"
        assert REGISTRY[lang].language == lang


# ---------------------------------------------------------------------------
# Behavior tier — markdown_io recognises ```smiles fence.

def test_markdown_io_finds_smiles_block() -> None:
    """find_blocks must recognise ```smiles fences post-Phase-6."""
    from render_cache.markdown_io import find_blocks
    content = "Pre\n\n```smiles\nCN1C=NC2=C1C(=O)N(C(=O)N2C)C\n```\n\nPost"
    blocks = find_blocks(content)
    assert len(blocks) == 1
    assert blocks[0].language == "smiles"
    assert blocks[0].fence_lang == "smiles"
    assert "C(=O)" in blocks[0].source


def test_markdown_io_finds_mixed_all_five_languages() -> None:
    """All five v1 languages in one file must all be detected, in
    document order. Post-Phase-6 v1 language coverage is complete."""
    from render_cache.markdown_io import find_blocks
    content = (
        "```graphviz\ndigraph A { x -> y; }\n```\n\n"
        "```lilypond\n\\relative c' { c d e f }\n```\n\n"
        "```smiles\nCC(=O)OC1=CC=CC=C1C(=O)O\n```\n\n"
        "```d2\nfoo -> bar\n```\n\n"
        "```tikz\n\\draw (0,0) circle (1);\n```\n"
    )
    blocks = find_blocks(content)
    assert len(blocks) == 5
    assert blocks[0].language == "graphviz"
    assert blocks[1].language == "lilypond"
    assert blocks[2].language == "smiles"
    assert blocks[3].language == "d2"
    assert blocks[4].language == "tikz"


def test_markdown_io_smiles_block_span_correct() -> None:
    """span must cover the entire fenced block (including closing ```)."""
    from render_cache.markdown_io import find_blocks
    content = "X\n```smiles\nCCO\n```\nY"
    blocks = find_blocks(content)
    s, e = blocks[0].span
    assert content[s:s + len("```smiles")] == "```smiles"
    assert content[e - 3:e] == "```"


# ---------------------------------------------------------------------------
# Behavior tier — dispatcher fence-detection.

def test_find_all_md_with_blocks_includes_smiles() -> None:
    """``find_all_md_with_blocks`` must scan for ```smiles blocks too,
    otherwise --all skips SMILES files entirely."""
    import inspect
    from render_cache import find_all_md_with_blocks
    src = inspect.getsource(find_all_md_with_blocks)
    assert '"smiles"' in src or "'smiles'" in src, (
        "find_all_md_with_blocks must include smiles in its fence-tag scan list."
    )


# ---------------------------------------------------------------------------
# Integration tier — actually invoke rdkit + the CLI.

# Caffeine: 14 atoms. Distinctive fused bicyclic purine ring system.
CAFFEINE_SMILES = "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
# Aspirin: acetylsalicylic acid. 13 atoms; benzene ring + acetyl ester.
ASPIRIN_SMILES = "CC(=O)OC1=CC=CC=C1C(=O)O"


@pytest.fixture(scope="module")
def have_rdkit() -> bool:
    try:
        import rdkit  # noqa: F401
        return True
    except ImportError:
        return False


@pytest.mark.slow
def test_smiles_adapter_renders_caffeine(have_rdkit: bool) -> None:
    """AC6.1 + AC6.2: SMILESAdapter.render produces a valid SVG file with
    drawing-typical structure (xmlns SVG, viewBox, multiple <path>
    elements). Caffeine has 14 atoms + 14 bonds → expect a substantial
    number of <path> elements (atoms drawn as glyphs, bonds as paths)."""
    if not have_rdkit:
        pytest.skip("rdkit not installed — install via `pip install rdkit`")
    from render_cache.adapters.smiles import SMILESAdapter
    a = SMILESAdapter()
    with tempfile.TemporaryDirectory() as tmp:
        wd = Path(tmp)
        out = a.render(CAFFEINE_SMILES, attrs={}, workdir=wd)
        assert out.exists(), "Adapter returned a path that doesn't exist"
        assert out.suffix == ".svg"
        text = out.read_text(encoding="utf-8")
        assert "<svg" in text
        assert "viewBox" in text or "viewbox" in text.lower()
        # Caffeine: 14 atoms × 1+ paths each + 14 bonds → expect ≥20 paths.
        # Smoke test reported 44; floor at 20 is generous.
        assert text.count("<path") >= 20, (
            f"Caffeine SVG has too few <path> elements (rdkit should emit "
            f"per-atom and per-bond glyphs):\n{text[:600]}"
        )
        # No file:// URIs (rdkit doesn't emit them, but guard against
        # future regressions if --useSVG-extras or similar gets added).
        assert text.count("file://") == 0


@pytest.mark.slow
def test_smiles_adapter_raises_on_invalid_source(have_rdkit: bool) -> None:
    """AC6.3: Invalid SMILES must raise ``RenderError`` with a
    user-friendly message, not silently produce a broken SVG."""
    if not have_rdkit:
        pytest.skip("rdkit not installed")
    from render_cache.adapters.base import RenderError
    from render_cache.adapters.smiles import SMILESAdapter
    a = SMILESAdapter()
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(RenderError) as excinfo:
            a.render("INVALID_SMILES_!!!", attrs={}, workdir=Path(tmp))
        # User-friendly message must include the offending input.
        msg = str(excinfo.value).lower()
        assert "smiles" in msg or "invalid" in msg, (
            f"RenderError message should mention 'smiles' or 'invalid': "
            f"got {excinfo.value!r}"
        )


@pytest.mark.slow
def test_smiles_cli_renders_sandbox(have_rdkit: bool) -> None:
    """AC6.1 + idempotence: CLI on the test sandbox produces SVGs without
    error, second run is a cache hit (idempotent)."""
    if not have_rdkit:
        pytest.skip("rdkit not installed")
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
        capture_output=True, text=True, timeout=60,
    )
    assert r2.returncode == 0
    assert "cache hit" in r2.stdout, (
        f"Second run did not report cache hit (idempotence broken):\n{r2.stdout}"
    )
