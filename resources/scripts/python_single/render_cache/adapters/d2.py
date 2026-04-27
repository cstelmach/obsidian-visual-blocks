"""D2 adapter — wraps the ``d2`` CLI in D2-source → SVG mode.

SPEC §5 Phase 4 (AC4.1-AC4.3), §3.4 (RendererAdapter contract).

D2 source is self-contained, so ``preamble_text`` returns the empty string
and ``preamble_digest("")`` is elided from the SPEC §3.7 T10 cache key.

Flag choices (PLAN §Phase 4 reference command):
- ``--layout=elk`` — d2 0.7.1 ships ``dagre`` (default) and ``elk`` bundled.
  ELK gives better hierarchical layout for the diagram styles we author.
- ``--pad=20``     — narrower margin than the d2 default (100 px).
- ``--theme=0``    — neutral theme; downstream Phase 7 hardening is theme-
  independent.
- ``--bundle=true``— inline icons/assets so the SVG is a single file the
  cache can serve standalone. d2 0.7.1's default; declared explicitly so
  the cache contract survives a future default flip.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from render_cache.adapters.base import RenderError, RendererAdapter

D2_TIMEOUT_S = 15


class D2Adapter(RendererAdapter):
    """Renders D2 blocks via the ``d2`` CLI."""

    @property
    def language(self) -> str:
        return "d2"

    @property
    def render_budget_seconds(self) -> int:
        return D2_TIMEOUT_S

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
        src_path = workdir / "source.d2"
        out_path = workdir / "out.svg"
        src_path.write_text(source, encoding="utf-8")

        try:
            result = subprocess.run(
                [
                    "d2",
                    "--layout=elk",
                    "--pad=20",
                    "--theme=0",
                    "--bundle=true",
                    str(src_path),
                    str(out_path),
                ],
                capture_output=True,
                text=True,
                timeout=D2_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired as e:
            raise RenderError(f"d2 timeout after {D2_TIMEOUT_S}s") from e
        except FileNotFoundError as e:
            raise RenderError("d2 not found on PATH") from e

        if result.returncode != 0 or not out_path.exists():
            raise RenderError(f"d2 failed: {result.stderr.strip()[:300]}")

        return out_path
