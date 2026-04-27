"""SVG post-processing — Phase 7 will implement the SPEC §3.7 T3/T4/T5 hardening
(ID-prefix to avoid cross-block ID collisions, ``currentColor`` for dark-mode
adaptation, ``viewBox`` normalisation with ``pt`` unit stripping).

Phase 2 is a pass-through stub so the dispatch path is complete and Phase 7
only fills in the body without rewiring callers.
"""
from __future__ import annotations


def apply(svg_text: str, key: str) -> str:
    """Apply hardening rules to an SVG. Phase 2: pass-through.

    Args:
        svg_text: Raw SVG content read from the renderer's working file.
        key: 16-char cache key — Phase 7 will use this as the unique ID prefix.
    """
    return svg_text
