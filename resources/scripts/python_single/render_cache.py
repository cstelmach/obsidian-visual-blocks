#!/usr/bin/env python3
"""Render code-block visualisations to cached SVGs.

Thin CLI entry point — defers to the ``render_cache`` package's ``main()``.
The package contains the dispatcher, hash logic, adapters, and I/O helpers;
this file exists so users (and the deprecation shim ``tikz_cache.py``) have a
canonical script path.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the sibling `render_cache` package is importable when this file is
# invoked directly (sys.path[0] is normally the script's directory, but be
# explicit for robustness against weird invocation contexts).
sys.path.insert(0, str(Path(__file__).parent))

from render_cache import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
