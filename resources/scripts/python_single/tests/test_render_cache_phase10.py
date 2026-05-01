"""
Phase 10 tests — error metadata for plugin inline error display.

The Obsidian plugin can only render an inline error block if the Python
dispatcher records failed blocks in ``index.json``. A failed render must not
silently remove the block from the note's index entry.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PYTHON_SINGLE = Path("/Users/cs/Obsidian/_/resources/scripts/python_single")
if str(PYTHON_SINGLE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SINGLE))


def test_process_file_records_last_error_for_failed_render(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    """AC10.1 foundation: render failures stay addressable in ``index.json``."""
    import render_cache as rc
    from render_cache.adapters.base import RenderError, RendererAdapter

    class FailingTikzAdapter(RendererAdapter):
        @property
        def language(self) -> str:
            return "tikz"

        @property
        def render_budget_seconds(self) -> int:
            return 1

        @property
        def preamble_text(self) -> str:
            return "\\documentclass{standalone}"

        def render(
            self,
            source: str,
            attrs: dict[str, Any],
            workdir: Path,
        ) -> Path:
            raise RenderError("lualatex failed: Undefined control sequence \\undefinedmacro")

    cache_dir = tmp_path / "cache"
    index_path = cache_dir / "index.json"

    def temp_cache_path(stem: str, idx: int, key: str, ext: str = "svg") -> Path:
        return cache_dir / rc.cache_filename(stem, idx, key, ext)

    monkeypatch.setattr(rc, "CACHE_DIR", cache_dir)
    monkeypatch.setattr(rc, "INDEX_PATH", index_path)
    monkeypatch.setattr(rc, "cache_path_for", temp_cache_path)
    monkeypatch.setattr(rc, "REGISTRY", {"tikz": FailingTikzAdapter()})

    md_path = tmp_path / "broken.md"
    original = "```tikz\n\\undefinedmacro\n```\n"
    md_path.write_text(original, encoding="utf-8")

    failed = rc.process_file(md_path, force=True, dry_run=False)

    assert failed == 1
    assert md_path.read_text(encoding="utf-8") == original

    index = json.loads(index_path.read_text(encoding="utf-8"))
    note = index["notes"][md_path.as_posix()]
    assert len(note["blocks"]) == 1
    block = note["blocks"][0]
    assert block["blockIdx"] == 0
    assert block["language"] == "tikz"
    assert block["outputBytes"] == 0
    assert block["renderedAt"] is None
    assert block["lastError"] == (
        "lualatex failed: Undefined control sequence \\undefinedmacro"
    )
    assert block["cachePath"].endswith(".svg")
