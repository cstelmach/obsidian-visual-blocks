#!/usr/bin/env python3
"""[DEPRECATED] Use ``render_cache.py`` instead.

This forwarder is retained for backward compatibility with existing scripts,
shell aliases, and the SPEC's Phase 2 acceptance criteria. It emits a
``DeprecationWarning`` and delegates to ``render_cache.main()``.

The rendering implementation now lives in
``render_cache/adapters/tikz.py`` (the same lualatex(DVI) → dvisvgm(SVG)
pipeline, with the Phase 1 regression fixes locked in: ``--no-fonts``,
``--bbox=min``, ``--libgs=`` auto-detection).
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

# Ensure the sibling ``render_cache`` package is importable.
sys.path.insert(0, str(Path(__file__).parent))

from render_cache import main as render_main  # noqa: E402

warnings.warn(
    "tikz_cache.py is a deprecated shim; call render_cache.py directly.",
    DeprecationWarning,
    stacklevel=2,
)

if __name__ == "__main__":
    sys.exit(render_main())
