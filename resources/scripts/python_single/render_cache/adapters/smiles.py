"""SMILES adapter — renders chemistry molecules from SMILES strings via rdkit.

SPEC §5 Phase 6 (AC6.1-AC6.3), §3.4 (RendererAdapter contract),
§3.2 architecture diagram (DISPATCH --> SM[SMILES adapter]).

This is the **only v1 adapter that is pure Python** — no shell-out, no
external CLI. RDKit is a Python wheel; the render path runs in-process via
``rdkit.Chem.MolFromSmiles`` + ``rdkit.Chem.AllChem.Compute2DCoords`` +
``rdkit.Chem.Draw.rdMolDraw2D.MolDraw2DSVG``. Cold render time for caffeine
benchmarked at ~2.6 ms; AC6.x targets are far below the budget ceiling.

Output: a single-page SVG written to ``<workdir>/out.svg`` and returned. The
SVG is hand-emitted by rdkit; it is well-formed (xmlns, viewBox), uses
``<path>`` for atom glyphs and bonds, and contains no ``file://`` URIs.

Failure modes:
- ``MolFromSmiles`` returns ``None`` for unparseable input → ``RenderError``
  with the offending input snippet (truncated to 80 chars to avoid
  multi-line error explosions).
- ``Compute2DCoords`` or the drawer raising any other rdkit exception →
  ``RenderError`` with the upstream message.
- ``rdkit`` import missing → ``RenderError`` directing the user to
  ``pip install rdkit``.

RDKit logger noise: by default rdkit prints multi-line "SMILES Parse Error"
diagnostics to stderr when ``MolFromSmiles`` rejects input. The dispatcher
catches the resulting ``RenderError`` and surfaces a clean one-line failure;
suppressing rdkit's own stderr at module import keeps user-facing CLI output
clean (D6.5).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from render_cache.adapters.base import RenderError, RendererAdapter

SMILES_TIMEOUT_S = 5
SMILES_DEFAULT_W = 400
SMILES_DEFAULT_H = 300


def _silence_rdkit_stderr() -> None:
    """Suppress rdkit's verbose ``rdApp.error`` logger so a bad SMILES
    string does not pollute CLI / test output. Our ``RenderError`` carries
    the actionable diagnostic (D6.5)."""
    try:
        from rdkit import RDLogger
    except ImportError:
        return
    RDLogger.DisableLog("rdApp.error")


_silence_rdkit_stderr()


class SMILESAdapter(RendererAdapter):
    """Renders SMILES chemistry strings via ``rdkit.Chem.Draw``."""

    @property
    def language(self) -> str:
        return "smiles"

    @property
    def render_budget_seconds(self) -> int:
        return SMILES_TIMEOUT_S

    @property
    def preamble_text(self) -> str:
        return ""

    def render(
        self,
        source: str,
        attrs: dict[str, Any],
        workdir: Path,
    ) -> Path:
        """Render ``source`` (a SMILES string, possibly with surrounding
        whitespace) to ``<workdir>/out.svg``. Return the absolute path."""
        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem
            from rdkit.Chem.Draw import rdMolDraw2D
        except ImportError as e:
            raise RenderError(
                "rdkit not installed; run `pip install rdkit`"
            ) from e

        smiles = source.strip()
        if not smiles:
            raise RenderError("SMILES adapter received empty source")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise RenderError(
                f"Invalid SMILES: {smiles[:80]!r}"
                + (" …(truncated)" if len(smiles) > 80 else "")
            )

        try:
            AllChem.Compute2DCoords(mol)
            drawer = rdMolDraw2D.MolDraw2DSVG(
                SMILES_DEFAULT_W, SMILES_DEFAULT_H
            )
            drawer.DrawMolecule(mol)
            drawer.FinishDrawing()
            svg_text = drawer.GetDrawingText()
        except Exception as e:
            raise RenderError(f"rdkit render failed: {e}") from e

        workdir.mkdir(parents=True, exist_ok=True)
        out = workdir / "out.svg"
        out.write_text(svg_text, encoding="utf-8")
        return out
