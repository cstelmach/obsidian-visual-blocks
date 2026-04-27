"""Renderer-adapter contract (SPEC §3.4).

The dispatcher is language-agnostic; every concrete adapter implements this
abstract base. Adding a new language is purely additive: subclass, register in
``adapters/__init__.py`` ``REGISTRY``, write tests.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class RenderError(RuntimeError):
    """Raised by an adapter when rendering fails. Should carry the captured
    stderr / log snippet so the dispatcher can surface a useful diagnostic."""


class RendererAdapter(ABC):
    """Abstract adapter — one concrete subclass per language tag."""

    @property
    @abstractmethod
    def language(self) -> str:
        """Canonical language tag (e.g. ``"tikz"``, ``"graphviz"``)."""

    @property
    @abstractmethod
    def render_budget_seconds(self) -> int:
        """Wall-clock budget for a single block render. Used for timeouts and
        for billing-style telemetry once observability lands."""

    @abstractmethod
    def render(
        self,
        source: str,
        attrs: dict[str, Any],
        workdir: Path,
    ) -> Path:
        """Render ``source`` to an SVG inside ``workdir``.

        Return the absolute path of the produced SVG. Raise ``RenderError``
        on failure — the dispatcher will catch it and record the message.
        """

    @property
    def preamble_text(self) -> str:
        """Return the active preamble text used by this adapter.

        Phase 2 returns the adapter's hardcoded preamble so
        ``preamble_digest(adapter.preamble_text)`` participates in cache
        invalidation per SPEC §3.7 T10. Phase 8+ may override per-folder.
        """
        return ""
