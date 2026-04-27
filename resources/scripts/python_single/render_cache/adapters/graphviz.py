"""Graphviz adapter — wraps the ``dot`` CLI in DOT-source → SVG mode.

SPEC §5 Phase 3 (AC3.1-AC3.4), §3.4 (RendererAdapter contract).

Graphviz has no preamble concept (a DOT file is self-contained), so
``preamble_text`` returns the empty string and ``preamble_digest("")`` is
elided from the SPEC §3.7 T10 cache key.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from render_cache.adapters.base import RenderError, RendererAdapter

DOT_TIMEOUT_S = 10


class GraphvizAdapter(RendererAdapter):
    """Renders Graphviz DOT blocks via ``dot -Tsvg``."""

    @property
    def language(self) -> str:
        return "graphviz"

    @property
    def render_budget_seconds(self) -> int:
        return DOT_TIMEOUT_S

    @property
    def preamble_text(self) -> str:
        return ""

    def render(
        self,
        source: str,
        attrs: dict[str, Any],
        workdir: Path,
    ) -> Path:
        """Render ``source`` to ``<workdir>/out.svg``. Return the absolute path."""
        workdir.mkdir(parents=True, exist_ok=True)
        src_path = workdir / "source.dot"
        out_path = workdir / "out.svg"
        src_path.write_text(source, encoding="utf-8")

        try:
            result = subprocess.run(
                ["dot", "-Tsvg", "-o", str(out_path), str(src_path)],
                capture_output=True,
                text=True,
                timeout=DOT_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired as e:
            raise RenderError(f"dot timeout after {DOT_TIMEOUT_S}s") from e
        except FileNotFoundError as e:
            raise RenderError("dot not found on PATH") from e

        if result.returncode != 0 or not out_path.exists():
            raise RenderError(f"dot failed: {result.stderr.strip()[:300]}")

        return out_path
