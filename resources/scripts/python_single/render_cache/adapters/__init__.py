"""Adapter registry. Adapter classes are constructed at import time but their
constructors only do lightweight setup (path probing) — no LaTeX environment
checks happen here, so CLI startup stays snappy (< 100 ms).

Adding a new language: import the adapter class and add it to ``REGISTRY``.
Tests in ``test_render_cache_phase2.py::test_adapter_registry_has_tikz`` guard
the registry shape.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from render_cache.adapters.tikz import TikzAdapter

if TYPE_CHECKING:
    from render_cache.adapters.base import RendererAdapter


REGISTRY: "dict[str, RendererAdapter]" = {
    "tikz": TikzAdapter(),
}


def get_adapter(language: str):
    """Return the adapter registered for ``language``. Raises ``KeyError``."""
    return REGISTRY[language]
