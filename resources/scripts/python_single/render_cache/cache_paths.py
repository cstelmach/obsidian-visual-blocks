"""Cache filesystem layout helpers.

Phase 2 keeps the legacy directory ``attachments/cache/tikz/`` (so existing
markdown wikilinks and ``.obsidian/snippets/tikz-cache.css`` continue to
resolve). The 16-char hash from SPEC §3.9 is now used in filenames.

SPEC §3.8 specifies a versioned layout under
``.obsidian/plugins/obsidian-render-cache/cache/v1/<note-path>/<idx>__<hash>.svg``.
Phase 8 (plugin scaffold) and Phase 12 (migration tool) will adopt that layout.
This module exists so that switch is a single-file change rather than a vault-
wide hunt.
"""
from __future__ import annotations

from pathlib import Path

VAULT_ROOT = Path("/Users/cs/Obsidian/_")

# Phase 2 cache directory (legacy location preserved). Phase 12 migrates.
CACHE_DIR = VAULT_ROOT / "attachments" / "cache" / "tikz"
INDEX_PATH = CACHE_DIR / "index.json"


def cache_filename(stem: str, idx: int, key: str, ext: str = "svg") -> str:
    """Return the canonical Phase-2 cache filename: ``<stem>__<idx>__<key>.<ext>``."""
    return f"{stem}__{idx}__{key}.{ext}"


def cache_path_for(stem: str, idx: int, key: str, ext: str = "svg") -> Path:
    """Return the absolute path of the cache file for ``(stem, idx, key)``."""
    return CACHE_DIR / cache_filename(stem, idx, key, ext)
