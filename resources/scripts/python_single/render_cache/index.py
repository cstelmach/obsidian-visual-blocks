"""Cache ``index.json`` reader/writer (SPEC §3.4 schema).

Phase 2 location: ``attachments/cache/tikz/index.json`` (legacy directory
retained — see ``cache_paths.py`` and ``PLAN.md`` Phase 2 common-mistakes
note). Phase 8 / Phase 12 migrate it to
``resources/data/cache/visual-blocks/index.json``.

The file is rewritten atomically via tempfile + rename so a crash mid-write
cannot corrupt it.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
RENDERER_VERSION = "0.2.0"  # bumped at Phase 13 release


def empty_index() -> dict[str, Any]:
    """Return a fresh, empty index document conforming to SPEC §3.4."""
    return {
        "schemaVersion": SCHEMA_VERSION,
        "rendererVersion": RENDERER_VERSION,
        "lastSweep": None,
        "preambleHashes": {},
        "notes": {},
    }


def load_index(path: Path) -> dict[str, Any]:
    """Load the index file. Returns an empty default if absent or malformed."""
    if not path.exists():
        return empty_index()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return empty_index()
    if not isinstance(data, dict):
        return empty_index()
    data.setdefault("schemaVersion", SCHEMA_VERSION)
    data.setdefault("rendererVersion", RENDERER_VERSION)
    data.setdefault("lastSweep", None)
    data.setdefault("preambleHashes", {})
    data.setdefault("notes", {})
    return data


def save_index(path: Path, data: dict[str, Any]) -> None:
    """Atomically write the index file. Creates parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_str = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp_str, path)
    except Exception:
        try:
            os.unlink(tmp_str)
        except FileNotFoundError:
            pass
        raise
