"""One-shot migration into the sync-friendly Visual Blocks cache layout.

Copies existing Visual Blocks SVGs into
``resources/data/cache/visual-blocks/v1/<note-path>/`` and rewrites markdown
image refs to ``visual-blocks``. The previous cache root is retained as
rollback until the user explicitly approves cleanup.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from render_cache.cache_paths import (
    INDEX_PATH,
    LEGACY_CACHE_DIR,
    LEGACY_INDEX_PATH,
    OLD_PLUGIN_INDEX_PATH,
    VAULT_ROOT,
    cache_path_for_rel,
)
from render_cache.index import empty_index, save_index

CONTENT_ROOTS = (
    "kn",
    "journal",
    "sources",
    "inbox",
    "todo",
    "archive",
)

LEGACY_SVG_RE = re.compile(r"^(.+)__(\d+)__([0-9a-f]{8,16})\.svg$")
LEGACY_PNG_RE = re.compile(r"^(.+)__(\d+)__([0-9a-f]{8,16})\.png$")
CACHE_REF_RE = re.compile(
    r"!\[\[([^\]|\n]+\.(?:png|svg))\|(tikz-cache|render-cache|visual-blocks)\]\]"
)


@dataclass(frozen=True)
class SvgCopy:
    old_rel: str
    new_rel: str
    old_abs: Path
    new_abs: Path


@dataclass(frozen=True)
class MarkdownUpdate:
    file: Path
    replacements: dict[str, str]


@dataclass
class MigrationPlan:
    vault_root: Path
    old_index_path: Path
    new_index_path: Path
    new_index: dict[str, Any]
    copies: list[SvgCopy] = field(default_factory=list)
    markdown_updates: list[MarkdownUpdate] = field(default_factory=list)
    png_deletes: list[Path] = field(default_factory=list)
    orphan_svg_deletes: list[Path] = field(default_factory=list)
    dropped_index_notes: list[str] = field(default_factory=list)
    missing_svg_refs: list[str] = field(default_factory=list)


@dataclass
class MigrationSummary:
    copied_svgs: int = 0
    updated_markdown_files: int = 0
    updated_markdown_refs: int = 0
    deleted_pngs: int = 0
    deleted_orphan_svgs: int = 0
    dropped_index_notes: int = 0
    missing_svg_refs: int = 0
    retained_old_cache_dir: bool = False


def _vault_relative(vault_root: Path, path: Path) -> str:
    return path.relative_to(vault_root).as_posix()


def _load_legacy_index(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_index()
    return json.loads(path.read_text(encoding="utf-8"))


def _rel_from_module_vault(path: Path) -> str:
    return _vault_relative(VAULT_ROOT, path)


def _index_candidates(vault_root: Path) -> list[Path]:
    return [
        vault_root / _rel_from_module_vault(INDEX_PATH),
        vault_root / _rel_from_module_vault(OLD_PLUGIN_INDEX_PATH),
        vault_root / _rel_from_module_vault(LEGACY_INDEX_PATH),
    ]


def _select_index_path(vault_root: Path) -> Path:
    for path in _index_candidates(vault_root):
        if path.exists():
            return path
    return vault_root / _rel_from_module_vault(INDEX_PATH)


def _is_vault_relative_note(note_rel: str) -> bool:
    if note_rel.startswith("/"):
        return False
    if note_rel.startswith("../"):
        return False
    return note_rel.endswith(".md")


def _iter_markdown_files(vault_root: Path) -> list[Path]:
    files: list[Path] = []
    for root_name in CONTENT_ROOTS:
        root = vault_root / root_name
        if not root.exists():
            continue
        files.extend(root.rglob("*.md"))
    return sorted(files)


def _first_existing_ref_text(ref_name: str, text: str) -> str | None:
    for match in CACHE_REF_RE.finditer(text):
        target = match.group(1)
        if target == ref_name or Path(target).name == ref_name:
            return match.group(0)
    return None


def _legacy_svg_names(legacy_dir: Path) -> set[str]:
    if not legacy_dir.exists():
        return set()
    return {p.name for p in legacy_dir.glob("*.svg")}


def _register_ref_mapping(
    mappings: dict[str, str],
    old_target: str,
    new_target: str,
) -> None:
    old_name = Path(old_target).name
    mappings[old_name] = new_target
    mappings[old_target] = new_target


def build_plan(vault_root: Path = VAULT_ROOT) -> MigrationPlan:
    """Build a complete migration plan without touching the filesystem."""
    vault_root = vault_root.resolve()
    old_index_path = _select_index_path(vault_root)
    new_index_path = vault_root / _rel_from_module_vault(INDEX_PATH)
    legacy_dir = vault_root / _rel_from_module_vault(LEGACY_CACHE_DIR)
    old_index = _load_legacy_index(old_index_path)
    new_index = empty_index()
    for key in ("schemaVersion", "rendererVersion", "lastSweep", "preambleHashes"):
        if key in old_index:
            new_index[key] = old_index[key]

    moved_old_names: set[str] = set()
    ref_mappings: dict[str, str] = {}
    slot_mappings: dict[tuple[str, int], str] = {}
    plan = MigrationPlan(
        vault_root=vault_root,
        old_index_path=old_index_path,
        new_index_path=new_index_path,
        new_index=new_index,
    )

    notes = old_index.get("notes", {})
    if not isinstance(notes, dict):
        notes = {}

    for note_rel, note_entry in sorted(notes.items()):
        note_path = vault_root / note_rel if _is_vault_relative_note(note_rel) else None
        if note_path is None or not note_path.exists():
            plan.dropped_index_notes.append(note_rel)
            continue

        new_blocks: list[dict[str, Any]] = []
        for block in note_entry.get("blocks", []):
            if not isinstance(block, dict):
                continue
            block_idx = int(block.get("blockIdx", len(new_blocks)))
            source_hash = str(block.get("sourceHash", ""))
            if not source_hash:
                continue
            new_abs = vault_root / _vault_relative(
                VAULT_ROOT,
                cache_path_for_rel(note_rel, block_idx, source_hash),
            )
            new_rel = _vault_relative(vault_root, new_abs)
            old_rel = str(block.get("cachePath", ""))
            old_abs = vault_root / old_rel
            new_block = dict(block)
            new_block["cachePath"] = new_rel

            if old_abs.exists() and old_abs.suffix == ".svg":
                if old_abs.resolve() != new_abs.resolve():
                    plan.copies.append(SvgCopy(old_rel, new_rel, old_abs, new_abs))
                moved_old_names.add(old_abs.name)
                _register_ref_mapping(ref_mappings, old_rel, new_rel)
                slot_mappings[(note_path.stem, block_idx + 1)] = new_rel
            elif new_abs.exists() or new_block.get("lastError"):
                pass
            else:
                plan.missing_svg_refs.append(old_rel or new_rel)
            new_blocks.append(new_block)

        new_index["notes"][note_rel] = {"blocks": new_blocks}

    for png in sorted(legacy_dir.glob("*.png")) if legacy_dir.exists() else []:
        m = LEGACY_PNG_RE.match(png.name)
        if m:
            mapped = slot_mappings.get((m.group(1), int(m.group(2))))
            if mapped:
                _register_ref_mapping(ref_mappings, png.name, mapped)

    for svg in sorted(legacy_dir.glob("*.svg")) if legacy_dir.exists() else []:
        if svg.name not in moved_old_names:
            pass

    for md in _iter_markdown_files(vault_root):
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        replacements: dict[str, str] = {}
        for old_target, new_target in ref_mappings.items():
            existing = _first_existing_ref_text(old_target, text)
            replacement = f"![[{new_target}|visual-blocks]]"
            if existing is not None and existing != replacement:
                replacements[existing] = replacement
        if replacements:
            plan.markdown_updates.append(MarkdownUpdate(md, replacements))

    return plan


def execute_plan(plan: MigrationPlan, dry_run: bool) -> MigrationSummary:
    """Execute a migration plan, or report counts only when ``dry_run`` is true."""
    summary = MigrationSummary(
        copied_svgs=len(plan.copies),
        updated_markdown_files=len(plan.markdown_updates),
        updated_markdown_refs=sum(len(u.replacements) for u in plan.markdown_updates),
        deleted_pngs=len(plan.png_deletes),
        deleted_orphan_svgs=len(plan.orphan_svg_deletes),
        dropped_index_notes=len(plan.dropped_index_notes),
        missing_svg_refs=len(plan.missing_svg_refs),
    )
    if dry_run:
        return summary

    for copy in plan.copies:
        copy.new_abs.parent.mkdir(parents=True, exist_ok=True)
        if copy.old_abs.exists():
            if copy.new_abs.exists():
                copy.new_abs.unlink()
            shutil.copy2(str(copy.old_abs), str(copy.new_abs))

    for update in plan.markdown_updates:
        text = update.file.read_text(encoding="utf-8")
        for old, new in update.replacements.items():
            text = text.replace(old, new)
        update.file.write_text(text, encoding="utf-8")

    plan.new_index_path.parent.mkdir(parents=True, exist_ok=True)
    save_index(plan.new_index_path, plan.new_index)

    summary.retained_old_cache_dir = plan.old_index_path.parent.exists()
    return summary


def print_plan(plan: MigrationPlan, summary: MigrationSummary, dry_run: bool) -> None:
    mode = "DRY RUN" if dry_run else "EXECUTE"
    print(f"Visual Blocks cache-root migration plan ({mode})")
    print(f"- SVG copies: {summary.copied_svgs}")
    print(f"- Markdown files to update: {summary.updated_markdown_files}")
    print(f"- Markdown refs to update: {summary.updated_markdown_refs}")
    print(f"- Legacy PNGs to delete: {summary.deleted_pngs}")
    print(f"- Orphan SVGs to delete: {summary.deleted_orphan_svgs}")
    print(f"- Dropped non-vault/missing index notes: {summary.dropped_index_notes}")
    print(f"- Missing SVG refs: {summary.missing_svg_refs}")
    print(f"- Old index: {_vault_relative(plan.vault_root, plan.old_index_path)}")
    print(f"- New index: {_vault_relative(plan.vault_root, plan.new_index_path)}")
    if dry_run:
        print("- No filesystem changes were made.")
    else:
        print(f"- Old cache directory retained: {summary.retained_old_cache_dir}")

    if plan.copies:
        print("\nSample copies:")
        for copy in plan.copies[:10]:
            print(f"  {copy.old_rel} -> {copy.new_rel}")
    if plan.markdown_updates:
        print("\nSample markdown updates:")
        for update in plan.markdown_updates[:10]:
            rel = _vault_relative(plan.vault_root, update.file)
            print(f"  {rel}: {len(update.replacements)} ref(s)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Migrate Visual Blocks cache into a sync-friendly vault folder."
    )
    parser.add_argument("--dry-run", action="store_true", help="report only")
    parser.add_argument(
        "--vault-root",
        default=str(VAULT_ROOT),
        help="vault root path (default: current Obsidian vault)",
    )
    args = parser.parse_args(argv)

    plan = build_plan(Path(args.vault_root))
    summary = execute_plan(plan, dry_run=args.dry_run)
    print_plan(plan, summary, dry_run=args.dry_run)
    if summary.missing_svg_refs:
        print(
            "Migration completed with missing SVG refs; inspect output before gate.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
