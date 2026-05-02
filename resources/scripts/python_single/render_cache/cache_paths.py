"""Cache filesystem layout helpers.

Phase 12 adopts the SPEC §3.8 plugin-managed layout:

``.obsidian/plugins/visual-blocks/cache/v1/<note-path>/<idx>__<hash>.svg``

``idx`` is the zero-based codeblock index, matching ``index.json``'s
``blockIdx`` field. The old flat ``attachments/cache/tikz`` directory remains
defined only for the migration script and rollback/debugging tools.
"""
from __future__ import annotations

from pathlib import Path, PurePosixPath
from urllib.parse import quote

VAULT_ROOT = Path("/Users/cs/Obsidian/_")

# Phase 1-11 legacy cache directory. Phase 12 migrates data out of it.
LEGACY_CACHE_DIR = VAULT_ROOT / "attachments" / "cache" / "tikz"
LEGACY_INDEX_PATH = LEGACY_CACHE_DIR / "index.json"

# Canonical Phase 12+ plugin-managed cache directory.
CACHE_ROOT = VAULT_ROOT / ".obsidian" / "plugins" / "visual-blocks" / "cache"
CACHE_VERSION = "v1"
CACHE_DIR = CACHE_ROOT / CACHE_VERSION
INDEX_PATH = CACHE_ROOT / "index.json"


def _escape_component(component: str) -> str:
    """Escape one POSIX path component for cross-platform cache paths."""
    return quote(component, safe="-_.~")


def _vault_relative(p: Path) -> str:
    try:
        return p.relative_to(VAULT_ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def note_cache_dir_for_rel(note_rel: str) -> Path:
    """Return the versioned cache directory for a vault-relative markdown path."""
    posix = PurePosixPath(note_rel)
    parts = list(posix.parts)
    if not parts:
        raise ValueError("note_rel must not be empty")
    leaf = parts[-1]
    if leaf.endswith(".md"):
        leaf = leaf[:-3]
    encoded = [_escape_component(p) for p in parts[:-1] + [leaf]]
    return CACHE_DIR.joinpath(*encoded)


def note_cache_dir_for(md_path: Path) -> Path:
    """Return the versioned cache directory for an absolute markdown path."""
    return note_cache_dir_for_rel(_vault_relative(md_path))


def cache_filename(block_idx: int, key: str, ext: str = "svg") -> str:
    """Return canonical Phase-12 filename: ``<zero-based-idx>__<hash>.<ext>``."""
    return f"{block_idx}__{key}.{ext}"


def cache_path_for_rel(
    note_rel: str,
    block_idx: int,
    key: str,
    ext: str = "svg",
) -> Path:
    """Return absolute cache path for a vault-relative markdown path."""
    return note_cache_dir_for_rel(note_rel) / cache_filename(block_idx, key, ext)


def cache_path_for_note(
    md_path: Path,
    block_idx: int,
    key: str,
    ext: str = "svg",
) -> Path:
    """Return absolute cache path for a markdown file path."""
    return note_cache_dir_for(md_path) / cache_filename(block_idx, key, ext)


def legacy_cache_filename(stem: str, idx: int, key: str, ext: str = "svg") -> str:
    """Return the legacy flat filename: ``<stem>__<one-based-idx>__<hash>.<ext>``."""
    return f"{stem}__{idx}__{key}.{ext}"


def legacy_cache_path_for(stem: str, idx: int, key: str, ext: str = "svg") -> Path:
    """Return the legacy flat cache path for migration/rollback helpers."""
    return LEGACY_CACHE_DIR / legacy_cache_filename(stem, idx, key, ext)
