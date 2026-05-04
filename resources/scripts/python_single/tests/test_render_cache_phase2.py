"""
test_render_cache_phase2.py — Verifies Phase 2 (Restructure into render_cache package).

References: SPEC §3.3 components, §3.4 adapter contract, §3.7 T8/T9/T10/T11
(cache-key constraints), §3.9 canonical key formula. PLAN §Phase 2.

Three tiers:
  - Structure tier: package skeleton present, importable, no heavy I/O at import
  - Behavior tier: normalize, hash, markdown_io, adapter contract semantics
  - Integration tier: CLI parity (render_cache.py vs tikz_cache.py shim)

Run all:    pytest tests/test_render_cache_phase2.py -v
"""

from __future__ import annotations

import importlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

PYTHON_SINGLE = Path(__file__).resolve().parents[1]
RENDER_CACHE_PKG = PYTHON_SINGLE / "render_cache"
RENDER_CACHE_CLI = PYTHON_SINGLE / "render_cache.py"
TIKZ_CACHE_SHIM = PYTHON_SINGLE / "tikz_cache.py"

# Make the package importable inside the test process.
if str(PYTHON_SINGLE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SINGLE))


# ---------------------------------------------------------------------------
# Structure tier — package skeleton.

EXPECTED_FILES = [
    "__init__.py",
    "normalize.py",
    "hash.py",
    "index.py",
    "postprocess.py",
    "markdown_io.py",
    "cache_paths.py",
    "adapters/__init__.py",
    "adapters/base.py",
    "adapters/tikz.py",
]


def test_package_skeleton_exists() -> None:
    """All Phase 2 modules must exist (PLAN Task 2.1)."""
    missing = [rel for rel in EXPECTED_FILES if not (RENDER_CACHE_PKG / rel).exists()]
    assert not missing, f"Missing Phase 2 modules: {missing}"


def test_package_modules_import_cleanly() -> None:
    """Importing the package and submodules must not crash, and must not run
    heavy LaTeX environment checks (so CLI startup stays snappy)."""
    importlib.import_module("render_cache")
    for rel in EXPECTED_FILES:
        if rel.endswith("__init__.py"):
            continue
        mod = "render_cache." + rel.replace("/", ".").removesuffix(".py")
        importlib.import_module(mod)


def test_cache_paths_default_vault_root_is_cwd(tmp_path: Path) -> None:
    """Standalone default: with no env override, cache paths resolve from cwd."""
    env = dict(**os.environ)
    env.pop("VISUAL_BLOCKS_VAULT_ROOT", None)
    env["PYTHONPATH"] = str(PYTHON_SINGLE)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from render_cache.cache_paths import VAULT_ROOT, CACHE_ROOT; "
            "print(VAULT_ROOT); print(CACHE_ROOT)",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    vault_root, cache_root = result.stdout.strip().splitlines()
    assert vault_root == str(tmp_path.resolve())
    assert cache_root == str(
        tmp_path.resolve() / ".obsidian/plugins/visual-blocks/cache"
    )


def test_cache_paths_honor_visual_blocks_vault_root(tmp_path: Path) -> None:
    """Fixture/dev override: VISUAL_BLOCKS_VAULT_ROOT chooses the vault root."""
    vault = tmp_path / "fixture-vault"
    vault.mkdir()
    env = dict(**os.environ)
    env["VISUAL_BLOCKS_VAULT_ROOT"] = str(vault)
    env["PYTHONPATH"] = str(PYTHON_SINGLE)
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from render_cache.cache_paths import VAULT_ROOT, INDEX_PATH; "
            "print(VAULT_ROOT); print(INDEX_PATH)",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    vault_root, index_path = result.stdout.strip().splitlines()
    assert vault_root == str(vault.resolve())
    assert index_path == str(
        vault.resolve() / ".obsidian/plugins/visual-blocks/cache/index.json"
    )


def test_cli_relative_path_resolves_against_configured_vault_root(
    tmp_path: Path,
) -> None:
    """A standalone invocation can target a vault with a relative note path."""
    vault = tmp_path / "fixture-vault"
    note = vault / "kn/math/concepts/example.md"
    note.parent.mkdir(parents=True)
    note.write_text("```d2\na -> b\n```\n", encoding="utf-8")

    env = dict(**os.environ)
    env["VISUAL_BLOCKS_VAULT_ROOT"] = str(vault)
    env["PYTHONPATH"] = str(PYTHON_SINGLE)
    result = subprocess.run(
        [
            sys.executable,
            str(RENDER_CACHE_CLI),
            "kn/math/concepts/example.md",
            "--dry-run",
            "--languages",
            "d2",
        ],
        cwd=PYTHON_SINGLE.parents[2],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert "=> kn/math/concepts/example.md: 1 block(s)" in result.stdout
    assert "would render" in result.stdout


# ---------------------------------------------------------------------------
# Behavior tier — normalize.

def test_normalize_plan_example() -> None:
    """PLAN Task 2.2 verify example: '  hello\\n\\n\\n\\n  world  ' → 'hello\\n\\nworld'."""
    from render_cache.normalize import normalize
    assert normalize("  hello\n\n\n\n  world  ") == "hello\n\nworld"


def test_normalize_crlf_to_lf() -> None:
    """SPEC §3.7 T9: line endings canonicalised."""
    from render_cache.normalize import normalize
    assert normalize("a\r\nb\r\nc") == "a\nb\nc"


def test_normalize_isolated_cr_to_lf() -> None:
    from render_cache.normalize import normalize
    assert normalize("a\rb") == "a\nb"


def test_normalize_strips_leading_trailing_blank_lines() -> None:
    from render_cache.normalize import normalize
    assert normalize("\n\n\nhello\n\n\n") == "hello"


def test_normalize_collapses_blank_runs() -> None:
    from render_cache.normalize import normalize
    assert normalize("a\n\n\n\nb") == "a\n\nb"


def test_normalize_strips_per_line_whitespace() -> None:
    from render_cache.normalize import normalize
    assert normalize("  a  \n  b  ") == "a\nb"


def test_normalize_idempotent() -> None:
    from render_cache.normalize import normalize
    s = "  hello\n\n\n  world  "
    assert normalize(normalize(s)) == normalize(s)


def test_normalize_empty_inputs() -> None:
    from render_cache.normalize import normalize
    assert normalize("") == ""
    assert normalize("\n\n\n") == ""
    assert normalize("   \n   ") == ""


# ---------------------------------------------------------------------------
# Behavior tier — hash (SPEC §3.9 canonical formula).

def test_hash_compute_key_length_and_charset() -> None:
    """SPEC §3.7 T8: SHA-256 truncated to 16 hex chars (64 bits)."""
    from render_cache.hash import compute_key
    k = compute_key("foo", "tikz", {}, "")
    assert len(k) == 16
    assert re.match(r"^[0-9a-f]{16}$", k), f"Non-hex key: {k!r}"


def test_hash_deterministic() -> None:
    from render_cache.hash import compute_key
    assert compute_key("foo", "tikz", {}, "") == compute_key("foo", "tikz", {}, "")


def test_hash_canonical_formula() -> None:
    """SPEC §3.9: key = SHA-256(normalize(source) || \\x00 || lang || \\x00 || JSON(attrs, sorted) || \\x00 || preamble)[0:16]."""
    import hashlib
    from render_cache.hash import compute_key
    from render_cache.normalize import normalize

    payload = (
        normalize("foo").encode("utf-8") + b"\x00"
        + b"tikz" + b"\x00"
        + json.dumps({}, sort_keys=True).encode("utf-8") + b"\x00"
        + b""
    )
    expected = hashlib.sha256(payload).hexdigest()[:16]
    assert compute_key("foo", "tikz", {}, "") == expected


def test_hash_includes_language() -> None:
    """SPEC §3.7 T10: same source, different language → different key."""
    from render_cache.hash import compute_key
    assert compute_key("foo", "tikz", {}, "") != compute_key("foo", "graphviz", {}, "")


def test_hash_includes_attrs() -> None:
    """SPEC §3.7 T10: render attributes are part of the key."""
    from render_cache.hash import compute_key
    assert compute_key("foo", "tikz", {}, "") != compute_key("foo", "tikz", {"a": 1}, "")


def test_hash_attrs_order_insensitive() -> None:
    """JSON dump uses sort_keys=True (canonicalisation)."""
    from render_cache.hash import compute_key
    a = compute_key("foo", "tikz", {"a": 1, "b": 2}, "")
    b = compute_key("foo", "tikz", {"b": 2, "a": 1}, "")
    assert a == b


def test_hash_includes_preamble() -> None:
    """SPEC §3.7 T10: preamble change must invalidate cache."""
    from render_cache.hash import compute_key
    assert compute_key("foo", "tikz", {}, "") != compute_key("foo", "tikz", {}, "deadbeef00000000")


def test_hash_normalises_source() -> None:
    """SPEC §3.7 T9: trivial whitespace edits must NOT change the key."""
    from render_cache.hash import compute_key
    assert compute_key("foo", "tikz", {}, "") == compute_key("  foo  \n", "tikz", {}, "")


def test_preamble_digest_length() -> None:
    from render_cache.hash import preamble_digest
    d = preamble_digest("\\documentclass{standalone}\n")
    assert len(d) == 16
    assert re.match(r"^[0-9a-f]{16}$", d)


# ---------------------------------------------------------------------------
# Behavior tier — markdown_io.

def test_markdown_io_finds_tikz_block() -> None:
    from render_cache.markdown_io import find_blocks
    content = "Pre\n\n```tikz\n\\draw (0,0) circle (1);\n```\n\nPost"
    blocks = find_blocks(content)
    assert len(blocks) == 1
    assert blocks[0].language == "tikz"
    assert "circle" in blocks[0].source


def test_markdown_io_tikz_paused_normalises_to_tikz() -> None:
    """Both `tikz` and `tikz-paused` recognised; both normalize language → 'tikz'
    so pausing/unpausing a block does not thrash the cache."""
    from render_cache.markdown_io import find_blocks
    content = "```tikz-paused\n\\draw (0,0) circle (1);\n```"
    blocks = find_blocks(content)
    assert len(blocks) == 1
    assert blocks[0].language == "tikz", "tikz-paused must canonicalise to 'tikz'"
    assert blocks[0].fence_lang == "tikz-paused"


def test_markdown_io_block_span() -> None:
    """span covers the entire fenced block including closing ```."""
    from render_cache.markdown_io import find_blocks
    content = "X\n```tikz\nA\n```\nY"
    blocks = find_blocks(content)
    s, e = blocks[0].span
    assert content[s:s + len("```tikz")] == "```tikz"
    assert content[e - 3:e] == "```"


def test_markdown_io_finds_existing_ref_both_extensions() -> None:
    from render_cache.markdown_io import find_existing_ref
    for ext in ("svg", "png"):
        content = f"\n\n![[file_1_abcd1234.{ext}|tikz-cache]]"
        m, _, _ = find_existing_ref(content, 0)
        assert m is not None, f"Failed to match {ext} ref"
        assert m.group(1).endswith("." + ext)


# ---------------------------------------------------------------------------
# Behavior tier — adapter contract (SPEC §3.4).

def test_adapter_base_is_abstract() -> None:
    from render_cache.adapters.base import RendererAdapter
    with pytest.raises(TypeError):
        RendererAdapter()  # type: ignore[abstract]


def test_tikz_adapter_implements_contract() -> None:
    from render_cache.adapters.base import RendererAdapter
    from render_cache.adapters.tikz import TikzAdapter
    a = TikzAdapter()
    assert isinstance(a, RendererAdapter)
    assert a.language == "tikz"
    assert isinstance(a.render_budget_seconds, int)
    assert a.render_budget_seconds > 0
    assert isinstance(a.preamble_text, str)
    assert "standalone" in a.preamble_text  # hardcoded preamble must include the document class


def test_adapter_registry_has_tikz() -> None:
    """SPEC §3.4: REGISTRY keyed by language tag."""
    from render_cache.adapters import REGISTRY
    assert "tikz" in REGISTRY
    assert REGISTRY["tikz"].language == "tikz"


# ---------------------------------------------------------------------------
# Behavior tier — index.

def test_index_empty_default() -> None:
    from render_cache.index import empty_index
    idx = empty_index()
    assert idx["schemaVersion"] == 1
    assert "rendererVersion" in idx
    assert idx["preambleHashes"] == {}
    assert idx["notes"] == {}


def test_index_load_save_roundtrip(tmp_path: Path) -> None:
    from render_cache.index import empty_index, load_index, save_index
    p = tmp_path / "index.json"
    data = empty_index()
    data["notes"]["foo.md"] = {"blocks": [{"sourceHash": "abcd1234abcd1234"}]}
    save_index(p, data)
    loaded = load_index(p)
    assert loaded["notes"]["foo.md"]["blocks"][0]["sourceHash"] == "abcd1234abcd1234"


def test_index_load_missing_returns_empty(tmp_path: Path) -> None:
    from render_cache.index import load_index
    out = load_index(tmp_path / "does-not-exist.json")
    assert out["notes"] == {}


def test_index_load_malformed_returns_empty(tmp_path: Path) -> None:
    from render_cache.index import load_index
    p = tmp_path / "bad.json"
    p.write_text("{ this is not valid json", encoding="utf-8")
    out = load_index(p)
    assert out["notes"] == {}


# ---------------------------------------------------------------------------
# Integration tier — CLI parity.

def test_render_cache_cli_help() -> None:
    """render_cache.py --help shows argparse help including the same flags as Phase 1."""
    result = subprocess.run(
        [sys.executable, str(RENDER_CACHE_CLI), "--help"],
        capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == 0, f"--help failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    out = result.stdout
    for flag in ("--all", "--force", "--sweep", "--dry-run"):
        assert flag in out, f"--help missing {flag}"


def test_render_cache_cli_no_args_prints_help() -> None:
    """No arguments → print help, non-zero exit (PLAN Task 2.3 parity)."""
    result = subprocess.run(
        [sys.executable, str(RENDER_CACHE_CLI)],
        capture_output=True, text=True, timeout=20,
    )
    assert result.returncode != 0
    assert "usage" in (result.stdout + result.stderr).lower()


# ---------------------------------------------------------------------------
# Integration tier — tikz_cache.py shim (PLAN Task 2.4).

def _strip_docstrings_and_comments(source: str) -> str:
    """Return ``source`` with triple-quoted strings and ``#`` comments removed."""
    s = re.sub(r'"""(.*?)"""', "", source, flags=re.DOTALL)
    s = re.sub(r"'''(.*?)'''", "", s, flags=re.DOTALL)
    s = "\n".join(ln for ln in s.splitlines() if not ln.lstrip().startswith("#"))
    return s


def test_tikz_cache_shim_is_thin() -> None:
    """The shim is a forwarder, not the implementation. It must NOT contain
    rendering logic (no lualatex/dvisvgm subprocess calls in executable code)."""
    src = TIKZ_CACHE_SHIM.read_text(encoding="utf-8")
    code = _strip_docstrings_and_comments(src)
    code_lines = [ln for ln in code.splitlines() if ln.strip()]
    # Effective lines should be small (a true forwarder is ~10–30 lines).
    assert len(code_lines) < 50, (
        f"Shim has {len(code_lines)} effective lines — expected a thin forwarder."
    )
    # No rendering subprocess calls in executable code.
    assert "lualatex" not in code, "Shim must not invoke lualatex directly"
    assert "dvisvgm" not in code, "Shim must not invoke dvisvgm directly"
    assert "subprocess" not in code, "Shim must not run subprocesses"


def test_tikz_cache_shim_imports_render_cache() -> None:
    src = TIKZ_CACHE_SHIM.read_text(encoding="utf-8")
    assert (
        "from render_cache" in src or "import render_cache" in src
    ), "Shim must import from render_cache to forward."


def test_tikz_cache_shim_emits_deprecation_warning() -> None:
    src = TIKZ_CACHE_SHIM.read_text(encoding="utf-8")
    assert "DeprecationWarning" in src
    assert "warnings.warn" in src or "warn(" in src


def test_tikz_cache_shim_runs_with_help() -> None:
    """Invoking the shim with --help must succeed (forwarded to render_cache.main)."""
    result = subprocess.run(
        [sys.executable, str(TIKZ_CACHE_SHIM), "--help"],
        capture_output=True, text=True, timeout=20,
    )
    assert result.returncode == 0
    assert "usage" in (result.stdout + result.stderr).lower()
