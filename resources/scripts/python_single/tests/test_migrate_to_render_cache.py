"""Phase 12 tests — migrate legacy flat cache to plugin-managed layout."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PYTHON_SINGLE = Path(__file__).resolve().parents[1]
if str(PYTHON_SINGLE) not in sys.path:
    sys.path.insert(0, str(PYTHON_SINGLE))


def write_index(path: Path, note_rel: str, legacy_ref: str, key: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "rendererVersion": "0.2.0",
                "lastSweep": None,
                "preambleHashes": {"<adapter:tikz>": "abc123abc123abcd"},
                "notes": {
                    note_rel: {
                        "blocks": [
                            {
                                "blockIdx": 0,
                                "language": "tikz",
                                "sourceHash": key,
                                "cachePath": legacy_ref,
                                "renderedAt": "2026-05-02T00:00:00Z",
                                "rendererVersion": "0.2.0",
                                "outputFormat": "svg",
                                "renderMs": None,
                                "outputBytes": 11,
                                "lastError": None,
                            }
                        ]
                    }
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_cache_path_for_rel_uses_plugin_v1_note_layout() -> None:
    from render_cache.cache_paths import VAULT_ROOT, cache_path_for_rel

    path = cache_path_for_rel(
        "kn/math/concepts/mSB3-4_reals.md",
        block_idx=0,
        key="814d986af7c9302c",
    )

    assert path.relative_to(VAULT_ROOT).as_posix() == (
        ".obsidian/plugins/visual-blocks/cache/v1/"
        "kn/math/concepts/mSB3-4_reals/0__814d986af7c9302c.svg"
    )


def test_dry_run_reports_plan_without_filesystem_changes(tmp_path: Path) -> None:
    from migrate_to_render_cache import build_plan, execute_plan

    vault = tmp_path / "vault"
    note_rel = "kn/math/concepts/mSB3-4_reals.md"
    note = vault / note_rel
    legacy_dir = vault / "attachments/cache/tikz"
    legacy_ref = "attachments/cache/tikz/mSB3-4_reals__1__814d986af7c9302c.svg"
    legacy_svg = vault / legacy_ref
    key = "814d986af7c9302c"

    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text(
        "```tikz\n\\draw (0,0)--(1,1);\n```\n\n"
        "![[mSB3-4_reals__1__814d986af7c9302c.svg|tikz-cache]]\n",
        encoding="utf-8",
    )
    legacy_dir.mkdir(parents=True, exist_ok=True)
    legacy_svg.write_text("<svg viewBox='0 0 1 1'></svg>", encoding="utf-8")
    write_index(legacy_dir / "index.json", note_rel, legacy_ref, key)

    before_note = note.read_text(encoding="utf-8")
    before_svg = legacy_svg.read_text(encoding="utf-8")
    plan = build_plan(vault)
    summary = execute_plan(plan, dry_run=True)

    assert summary.moved_svgs == 1
    assert summary.updated_markdown_files == 1
    assert note.read_text(encoding="utf-8") == before_note
    assert legacy_svg.read_text(encoding="utf-8") == before_svg
    assert not (vault / ".obsidian/plugins/visual-blocks/cache/index.json").exists()


def test_real_run_moves_svg_updates_index_and_markdown(tmp_path: Path) -> None:
    from migrate_to_render_cache import build_plan, execute_plan

    vault = tmp_path / "vault"
    note_rel = "kn/math/concepts/mSB3-4_reals.md"
    note = vault / note_rel
    legacy_dir = vault / "attachments/cache/tikz"
    legacy_ref = "attachments/cache/tikz/mSB3-4_reals__1__814d986af7c9302c.svg"
    legacy_svg = vault / legacy_ref
    key = "814d986af7c9302c"
    new_rel = (
        ".obsidian/plugins/visual-blocks/cache/v1/"
        "kn/math/concepts/mSB3-4_reals/0__814d986af7c9302c.svg"
    )

    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text(
        "```tikz\n\\draw (0,0)--(1,1);\n```\n\n"
        "![[mSB3-4_reals__1__814d986af7c9302c.svg|tikz-cache]]\n",
        encoding="utf-8",
    )
    legacy_dir.mkdir(parents=True, exist_ok=True)
    legacy_svg.write_text("<svg viewBox='0 0 1 1'></svg>", encoding="utf-8")
    (legacy_dir / "old.png").write_text("png", encoding="utf-8")
    write_index(legacy_dir / "index.json", note_rel, legacy_ref, key)

    summary = execute_plan(build_plan(vault), dry_run=False)

    assert summary.moved_svgs == 1
    assert summary.deleted_pngs == 1
    assert not legacy_svg.exists()
    assert (vault / new_rel).read_text(encoding="utf-8") == (
        "<svg viewBox='0 0 1 1'></svg>"
    )
    assert f"![[{new_rel}|visual-blocks]]" in note.read_text(encoding="utf-8")

    new_index = json.loads(
        (vault / ".obsidian/plugins/visual-blocks/cache/index.json").read_text(
            encoding="utf-8"
        )
    )
    block = new_index["notes"][note_rel]["blocks"][0]
    assert block["cachePath"] == new_rel
    assert block["blockIdx"] == 0
    assert not legacy_dir.exists()


def test_real_run_replaces_existing_destination_svg(tmp_path: Path) -> None:
    from migrate_to_render_cache import build_plan, execute_plan

    vault = tmp_path / "vault"
    note_rel = "kn/math/concepts/mSB3-4_reals.md"
    note = vault / note_rel
    legacy_dir = vault / "attachments/cache/tikz"
    legacy_ref = "attachments/cache/tikz/mSB3-4_reals__1__814d986af7c9302c.svg"
    legacy_svg = vault / legacy_ref
    key = "814d986af7c9302c"
    new_rel = (
        ".obsidian/plugins/visual-blocks/cache/v1/"
        "kn/math/concepts/mSB3-4_reals/0__814d986af7c9302c.svg"
    )
    existing_dest = vault / new_rel

    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text(
        "```tikz\n\\draw (0,0)--(1,1);\n```\n\n"
        "![[mSB3-4_reals__1__814d986af7c9302c.svg|tikz-cache]]\n",
        encoding="utf-8",
    )
    legacy_dir.mkdir(parents=True, exist_ok=True)
    legacy_svg.write_text("<svg id='legacy'></svg>", encoding="utf-8")
    existing_dest.parent.mkdir(parents=True, exist_ok=True)
    existing_dest.write_text("<svg id='stale-dest'></svg>", encoding="utf-8")
    write_index(legacy_dir / "index.json", note_rel, legacy_ref, key)

    summary = execute_plan(build_plan(vault), dry_run=False)

    assert summary.moved_svgs == 1
    assert not legacy_svg.exists()
    assert existing_dest.read_text(encoding="utf-8") == "<svg id='legacy'></svg>"


def test_absolute_temp_vault_index_entries_are_dropped(tmp_path: Path) -> None:
    from migrate_to_render_cache import build_plan, execute_plan

    vault = tmp_path / "vault"
    legacy_dir = vault / "attachments/cache/tikz"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    legacy_svg = legacy_dir / "_PHASE9_GATE_d2__1__7d8f25d74720ebf0.svg"
    legacy_svg.write_text("<svg></svg>", encoding="utf-8")
    write_index(
        legacy_dir / "index.json",
        "/private/var/tmp/obsidian-test/kn/math/concepts/_PHASE9_GATE_d2.md",
        "attachments/cache/tikz/_PHASE9_GATE_d2__1__7d8f25d74720ebf0.svg",
        "7d8f25d74720ebf0",
    )

    plan = build_plan(vault)
    summary = execute_plan(plan, dry_run=False)

    assert summary.dropped_index_notes == 1
    assert summary.deleted_orphan_svgs == 1
    assert not legacy_svg.exists()
    new_index = json.loads(
        (vault / ".obsidian/plugins/visual-blocks/cache/index.json").read_text(
            encoding="utf-8"
        )
    )
    assert new_index["notes"] == {}
