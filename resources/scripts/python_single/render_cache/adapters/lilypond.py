"""LilyPond adapter — wraps the ``lilypond`` CLI in source → SVG mode.

SPEC §5 Phase 5 (AC5.1-AC5.3), §3.4 (RendererAdapter contract),
§3.7 T2 (mandatory ``-dpoint-and-click=#f`` flag).

LilyPond source is self-contained, so ``preamble_text`` returns the empty
string and ``preamble_digest("")`` is elided from the SPEC §3.7 T10 cache
key (mirroring D3.2/D4.2).

Flag choices (PLAN §Phase 5 reference command):

- ``-dpoint-and-click=#f``         — MANDATORY (T2). Without this flag,
  LilyPond bakes absolute ``file://`` URIs into the SVG so users can click
  notes to jump to source in editor; the URIs (a) leak local filesystem
  paths into cached output, (b) thrash the cache because they vary by
  build directory.
- ``-dbackend=svg``                — emit SVG (vs default PostScript).
- ``-dno-include-book-title-preview`` — drop the auto-generated title
  preview block. Notes only.
- ``-o <prefix>``                  — output prefix; LilyPond will write
  ``<prefix>.svg`` for single-page or ``<prefix>-1.svg``,
  ``<prefix>-page1.svg`` (varies by version) for multi-page scores.

Output discovery: LilyPond does not let us name the output file directly,
only the prefix. The single-page common case produces ``out.svg``;
multi-page scores produce a numbered series. We glob ``out*.svg`` and
return the first hit. Multi-page handling (composing multiple SVGs into
one cache entry) is deferred to v1.1; v1's test sandbox uses single-page
inputs.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from render_cache.adapters.base import RenderError, RendererAdapter

LILYPOND_TIMEOUT_S = 30


class LilyPondAdapter(RendererAdapter):
    """Renders LilyPond music-notation blocks via ``lilypond -dbackend=svg``."""

    @property
    def language(self) -> str:
        return "lilypond"

    @property
    def render_budget_seconds(self) -> int:
        return LILYPOND_TIMEOUT_S

    @property
    def preamble_text(self) -> str:
        return ""

    def render(
        self,
        source: str,
        attrs: dict[str, Any],
        workdir: Path,
    ) -> Path:
        """Render ``source`` to ``<workdir>/out*.svg``. Return the absolute
        path of the first SVG produced (single-page expectation for v1)."""
        workdir.mkdir(parents=True, exist_ok=True)
        src_path = workdir / "source.ly"
        src_path.write_text(source, encoding="utf-8")

        try:
            result = subprocess.run(
                [
                    "lilypond",
                    "-dpoint-and-click=#f",
                    "-dbackend=svg",
                    "-dno-include-book-title-preview",
                    "-o", str(workdir / "out"),
                    str(src_path),
                ],
                capture_output=True,
                text=True,
                timeout=LILYPOND_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired as e:
            raise RenderError(
                f"lilypond timeout after {LILYPOND_TIMEOUT_S}s"
            ) from e
        except FileNotFoundError as e:
            raise RenderError("lilypond not found on PATH") from e

        if result.returncode != 0:
            raise RenderError(
                f"lilypond failed: {result.stderr.strip()[:300]}"
            )

        # LilyPond writes out.svg for single-page, out-1.svg / out-page1.svg
        # for multi-page (naming varies by version). Glob and pick the first.
        svgs = sorted(workdir.glob("out*.svg"))
        if not svgs:
            raise RenderError(
                f"lilypond produced no SVG output in {workdir} "
                f"(stderr: {result.stderr.strip()[:200]})"
            )
        return svgs[0]
