"""TikZ adapter — wraps the lualatex(DVI) → dvisvgm(SVG) pipeline.

SPEC §3.7:
    T1: ``dvisvgm --no-fonts`` is mandatory. Without it, dvisvgm leaves font
        references in the SVG; iOS WKWebView lacks Computer Modern and
        silently falls back to Times New Roman, breaking math layout.

Phase 1 regression fixes locked in here:
    - TeX Live's bundled dvisvgm has neither libgs nor MuPDF and silently
      drops PostScript specials → SVG with text glyphs but no geometry. We
      auto-detect a Ghostscript shared library and pass ``--libgs=`` so
      PostScript specials are honoured. Override path via ``DVISVGM_LIBGS``.
    - Use ``--bbox=min`` (the modern replacement for the deprecated
      ``--exact-bbox``). Do NOT pass ``--bbox=preview``: it is for the LaTeX
      ``preview`` package and produces a degenerate clipped bbox under
      ``standalone``.
    - dvisvgm 3.4+ requires ``--output=PATH`` (with ``=``). Space-separated
      form errors with ``option --output: string argument 'pattern' expected``.
"""
from __future__ import annotations

import os
import re
import subprocess
import textwrap
from pathlib import Path
from typing import Any

from render_cache.adapters.base import RenderError, RendererAdapter

LUALATEX_TIMEOUT_S = 90
DVISVGM_TIMEOUT_S = 60

LATEX_PREAMBLE = textwrap.dedent(r"""
    \documentclass[border=4pt]{standalone}
    \usepackage{pgfplots}
    \pgfplotsset{compat=1.16}
    \usetikzlibrary{
        arrows.meta, positioning, decorations.pathreplacing,
        decorations.markings, calc, shapes, patterns,
        intersections, fit, backgrounds
    }
    \usepackage{amsmath, amssymb}
    \begin{document}
""").lstrip()

LATEX_POSTAMBLE = "\n\\end{document}\n"


def _detect_libgs() -> str | None:
    env = os.environ.get("DVISVGM_LIBGS")
    candidates: tuple[str | None, ...] = (
        env,
        "/opt/homebrew/lib/libgs.dylib",          # Apple Silicon brew
        "/usr/local/lib/libgs.dylib",             # Intel macOS brew
        "/usr/lib/x86_64-linux-gnu/libgs.so",     # Debian / Ubuntu
        "/usr/lib64/libgs.so",                    # RHEL / CentOS 64-bit
        "/usr/lib/libgs.so",                      # generic Linux
    )
    return next((p for p in candidates if p and Path(p).exists()), None)


LIBGS_PATH: str | None = _detect_libgs()


def _extract_tikz_body(block: str) -> str:
    """Strip wrappers TikZJax tolerates but ``standalone`` doesn't."""
    body = block
    body = re.sub(r"\\usepackage\s*\{\s*tikz\s*\}\s*", "", body)
    m = re.search(r"\\begin\{document\}(.*?)\\end\{document\}", body, re.DOTALL)
    if m:
        body = m.group(1)
    return body.strip() + "\n"


class TikzAdapter(RendererAdapter):
    """Renders TikZ blocks via ``lualatex -output-format=dvi`` then
    ``dvisvgm --no-fonts --bbox=min --libgs=…``."""

    @property
    def language(self) -> str:
        return "tikz"

    @property
    def render_budget_seconds(self) -> int:
        return LUALATEX_TIMEOUT_S + DVISVGM_TIMEOUT_S

    @property
    def preamble_text(self) -> str:
        return LATEX_PREAMBLE

    def render(
        self,
        source: str,
        attrs: dict[str, Any],
        workdir: Path,
    ) -> Path:
        """Render ``source`` to ``<workdir>/out.svg``. Return the absolute path."""
        workdir.mkdir(parents=True, exist_ok=True)
        body = _extract_tikz_body(source)
        full_tex = LATEX_PREAMBLE + body + LATEX_POSTAMBLE

        tex_path = workdir / "tikz.tex"
        dvi_path = workdir / "tikz.dvi"
        svg_path = workdir / "out.svg"
        tex_path.write_text(full_tex, encoding="utf-8")

        # 1. Compile to DVI (not PDF — dvisvgm consumes DVI directly).
        try:
            subprocess.run(
                [
                    "lualatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "-output-format=dvi",
                    "tikz.tex",
                ],
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=LUALATEX_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired as e:
            raise RenderError("lualatex timeout") from e
        except FileNotFoundError as e:
            raise RenderError("lualatex not found on PATH") from e

        if not dvi_path.exists():
            log_path = workdir / "tikz.log"
            snippet = ""
            if log_path.exists():
                log = log_path.read_text(errors="replace")
                err_lines = [ln for ln in log.splitlines() if ln.startswith("!")]
                if err_lines:
                    snippet = " | ".join(err_lines[:3])
                elif log.splitlines():
                    snippet = log.splitlines()[-1]
            raise RenderError(f"lualatex failed: {snippet[:200]}")

        # 2. Convert DVI → SVG. Mandatory: --no-fonts (T1) + --bbox=min;
        # required for TikZ geometry: --libgs=<lib>.
        cmd = [
            "dvisvgm",
            "--no-fonts",
            "--bbox=min",
            f"--output={svg_path}",
        ]
        if LIBGS_PATH:
            cmd.insert(1, f"--libgs={LIBGS_PATH}")
        cmd.append(str(dvi_path))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=DVISVGM_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired as e:
            raise RenderError("dvisvgm timeout") from e
        except FileNotFoundError as e:
            raise RenderError("dvisvgm not found on PATH") from e

        if result.returncode != 0 or not svg_path.exists():
            raise RenderError(f"dvisvgm failed: {result.stderr.strip()[:200]}")
        if not LIBGS_PATH:
            # Soft-fail: dvisvgm wrote an SVG, but TikZ shapes are missing.
            # Hard failure here prevents producing broken cache files.
            raise RenderError(
                "dvisvgm produced an SVG, but no Ghostscript library was found. "
                "TikZ shapes (lines, circles, paths) will be missing. Install "
                "ghostscript (brew install ghostscript) or set DVISVGM_LIBGS."
            )

        return svg_path
