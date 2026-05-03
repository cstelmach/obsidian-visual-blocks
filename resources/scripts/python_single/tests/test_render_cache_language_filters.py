from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

PYTHON_SINGLE = Path("/Users/cs/Obsidian/_/resources/scripts/python_single")
if str(PYTHON_SINGLE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SINGLE))


def test_language_metadata_matches_v1_surface() -> None:
    from render_cache.languages import CANONICAL_LANGUAGES, canonicalize_fence_lang

    assert CANONICAL_LANGUAGES == ("tikz", "graphviz", "d2", "lilypond", "smiles")
    assert canonicalize_fence_lang("tikz-paused") == "tikz"
    assert canonicalize_fence_lang("d2") == "d2"
    assert canonicalize_fence_lang("mermaid") is None


def test_parse_language_filter_validates_unknown_ids() -> None:
    from render_cache.languages import parse_language_filter

    assert parse_language_filter(None) is None
    assert parse_language_filter("tikz,d2,smiles") == {"tikz", "d2", "smiles"}
    with pytest.raises(ValueError, match="unknown language"):
        parse_language_filter("tikz,mermaid")


def test_process_file_skips_disabled_language_and_preserves_existing_index(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    import render_cache as rc
    from render_cache.adapters.base import RendererAdapter

    calls: list[str] = []

    class FakeAdapter(RendererAdapter):
        def __init__(self, language: str) -> None:
            self._language = language

        @property
        def language(self) -> str:
            return self._language

        @property
        def render_budget_seconds(self) -> int:
            return 1

        @property
        def preamble_text(self) -> str:
            return ""

        def render(self, source: str, attrs: dict[str, Any], workdir: Path) -> Path:
            calls.append(self.language)
            workdir.mkdir(parents=True, exist_ok=True)
            out = workdir / "out.svg"
            out.write_text(f"<svg><text>{self.language}</text></svg>", encoding="utf-8")
            return out

    cache_dir = tmp_path / "cache"
    index_path = cache_dir / "index.json"

    def temp_cache_path(md_path: Path, block_idx: int, key: str, ext: str = "svg") -> Path:
        return cache_dir / md_path.stem / rc.cache_filename(block_idx, key, ext)

    monkeypatch.setattr(rc, "CACHE_DIR", cache_dir)
    monkeypatch.setattr(rc, "CACHE_ROOT", cache_dir)
    monkeypatch.setattr(rc, "INDEX_PATH", index_path)
    monkeypatch.setattr(rc, "cache_path_for_note", temp_cache_path)
    monkeypatch.setattr(
        rc,
        "REGISTRY",
        {
            "lilypond": FakeAdapter("lilypond"),
            "d2": FakeAdapter("d2"),
        },
    )

    md_path = tmp_path / "mixed.md"
    existing_lily = cache_dir / "mixed" / "0__oldlily.svg"
    existing_lily.parent.mkdir(parents=True)
    existing_lily.write_text("<svg><text>old lily</text></svg>", encoding="utf-8")
    index_path.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "rendererVersion": "0.2.0",
                "preambleHashes": {},
                "notes": {
                    md_path.as_posix(): {
                        "blocks": [
                            {
                                "blockIdx": 0,
                                "language": "lilypond",
                                "sourceHash": "oldlily",
                                "cachePath": existing_lily.as_posix(),
                                "renderedAt": "2026-05-03T00:00:00Z",
                                "rendererVersion": "0.2.0",
                                "outputFormat": "svg",
                                "renderMs": None,
                                "outputBytes": existing_lily.stat().st_size,
                                "lastError": None,
                            }
                        ]
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    md_path.write_text(
        "\n".join(
            [
                "```lilypond",
                "{ c'4 }",
                "```",
                "",
                "```d2",
                "a -> b",
                "```",
            ]
        ),
        encoding="utf-8",
    )

    failed = rc.process_file(md_path, force=True, dry_run=False, languages={"d2"})

    assert failed == 0
    assert calls == ["d2"]
    index = json.loads(index_path.read_text(encoding="utf-8"))
    blocks = index["notes"][md_path.as_posix()]["blocks"]
    assert [b["language"] for b in blocks] == ["lilypond", "d2"]
    assert blocks[0]["sourceHash"] == "oldlily"
    assert existing_lily.exists()


def test_find_all_md_with_blocks_respects_language_filter(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    import render_cache as rc

    root = tmp_path / "kn"
    root.mkdir()
    lily = root / "lily.md"
    d2 = root / "d2.md"
    mixed = root / "mixed.md"
    lily.write_text("```lilypond\n{ c'4 }\n```\n", encoding="utf-8")
    d2.write_text("```d2\na -> b\n```\n", encoding="utf-8")
    mixed.write_text("```lilypond\n{ c'4 }\n```\n\n```d2\na -> b\n```\n", encoding="utf-8")
    monkeypatch.setattr(rc, "SCAN_ROOTS", [root])

    assert set(rc.find_all_md_with_blocks({"d2"})) == {d2, mixed}
    assert set(rc.find_all_md_with_blocks({"lilypond"})) == {lily, mixed}
