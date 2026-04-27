"""SVG post-processing — Phase 7 (SPEC §3.7 T3/T4/T5, §5 Phase 7).

Three hardening rules run between adapter render and cache write:

- :func:`prefix_ids` — hash-prefix all element IDs and ``href`` references
  so multiple cached SVGs on one Obsidian page can't collide. Generic IDs
  like dvisvgm's ``g0-N`` or Graphviz's ``node1`` would otherwise corrupt
  each other when two diagrams from the same renderer share a page (T3 /
  AC7.1).
- :func:`substitute_current_color` — replace hardcoded black
  (``#000000``, ``#000``, ``black``) with ``currentColor`` so Obsidian's
  light/dark theme flows through to cached diagrams. Two surfaces:
  attribute form (``fill="black"``) AND CSS-style form
  (``style="...stroke:#000000;..."`` — rdkit/SMILES emits this exclusively)
  (T5 / AC7.2).
- :func:`enforce_viewbox` — strip ``pt`` units from ``width`` / ``height``
  (iOS WKWebView with ``pt`` and no viewBox renders 0×0 silently); inject
  ``viewBox`` if absent (T4 / AC7.3).

All regexes are quote-agnostic: dvisvgm and rdkit emit single-quoted
attributes (``fill='#000000'``), Graphviz/D2/LilyPond emit double-quoted.
The PLAN's pseudocode pinned double quotes only and would silently no-op
on TikZ + SMILES — fixed here.

The colour rules deliberately match only black variants. White (``#FFFFFF``,
``white``) and other colours are preserved so D2/Graphviz background rects
and user-chosen colours survive intact.
"""
from __future__ import annotations

import re
from typing import Final

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------
#
# Quote-agnostic strategy: each regex captures the opening quote with
# ``(["'])`` and back-references it via ``\\1`` so the closing quote must
# match. Replacements preserve the original quote style by emitting the
# captured group unchanged.

_ID_RE: Final = re.compile(r"""\bid=(["'])([^"']+)\1""")

# Two href flavours: ``xlink:href="#frag"`` (SVG 1.1, dvisvgm) and bare
# ``href="#frag"`` (SVG 2). Both must be rewritten when they target an
# in-document fragment (``#``-prefixed). Data URIs (``href="data:..."``)
# are skipped because the value doesn't start with ``#``.
_HREF_RE: Final = re.compile(
    r"""\b(xlink:)?href=(["'])#([^"']+)\2"""
)

# Black colour patterns. Word boundary ``\b`` after the colour keyword/hex
# prevents partial matches: ``#000`` followed by ``a`` (``#000a`` short
# hex) and ``black`` followed by ``s`` (``blacksmith``) both fail to
# match. Case-insensitive so ``#FFF`` style hex parens around black work.
_BLACK_VALUE: Final = r"(?:#000000|#000(?![0-9a-fA-F])|black\b)"

# Attribute form: ``fill='black'`` / ``stroke="#000000"``
_BLACK_ATTR_RE: Final = re.compile(
    rf"""\b(fill|stroke)=(["']){_BLACK_VALUE}\2""",
    re.IGNORECASE,
)

# CSS-style form: ``style='...;fill:#000000;...'`` — rdkit emits these
# exclusively for SMILES. Match the property name + colon + (optional ws)
# + black value. Replacement omits the captured value.
_BLACK_STYLE_RE: Final = re.compile(
    rf"""\b(fill|stroke):\s*{_BLACK_VALUE}""",
    re.IGNORECASE,
)

# Width / height with ``pt`` unit. SPEC AC7.3 specifies ``pt`` only —
# don't generalise to mm/cm/px (PLAN §Phase 7 common mistakes).
_WIDTH_PT_RE: Final = re.compile(
    r"""\bwidth=(["'])([0-9.]+)pt\1"""
)
_HEIGHT_PT_RE: Final = re.compile(
    r"""\bheight=(["'])([0-9.]+)pt\1"""
)

# Detect any width/height attribute (with or without unit) for viewBox
# injection. Unitless / ``px`` / ``mm`` are all valid here — we just need
# the numeric value to build a viewBox.
_WIDTH_NUM_RE: Final = re.compile(
    r"""\bwidth=(["'])([0-9.]+)(?:pt|px|mm)?\1"""
)
_HEIGHT_NUM_RE: Final = re.compile(
    r"""\bheight=(["'])([0-9.]+)(?:pt|px|mm)?\1"""
)

_VIEWBOX_RE: Final = re.compile(r"""\bviewBox=["']""")

# Match the opening ``<svg`` element so we can inject a viewBox attribute
# before the existing attribute list.
_SVG_OPEN_RE: Final = re.compile(r"""<svg(\s|>)""")

# ID-prefix rule
# ---------------------------------------------------------------------------

_PREFIX_LEN: Final = 6


def prefix_ids(svg_text: str, prefix: str) -> str:
    """Hash-prefix all SVG element IDs and href references.

    Two cached SVGs from the same renderer can otherwise collide on shared
    IDs (``g0-N`` from dvisvgm; ``node1`` / ``edge1`` from Graphviz) when
    rendered on the same Obsidian page. The first 6 hex characters of the
    cache key form the prefix — short enough to keep IDs readable, long
    enough that a vault's worth of cached diagrams won't collide
    (16⁶ = 16.7M unique prefixes).

    The same prefix is applied to ``href="#..."`` and ``xlink:href="#..."``
    fragment references so element relationships survive intact. Data URIs
    (``href="data:..."``) are not rewritten because their value doesn't
    start with ``#``.

    No-op on SVGs without IDs (e.g., rdkit/SMILES).
    """
    safe_prefix = prefix[:_PREFIX_LEN]

    def _id_repl(m: re.Match[str]) -> str:
        quote, ident = m.group(1), m.group(2)
        return f"id={quote}{safe_prefix}__{ident}{quote}"

    def _href_repl(m: re.Match[str]) -> str:
        xlink_prefix = m.group(1) or ""
        quote, frag = m.group(2), m.group(3)
        return f"{xlink_prefix}href={quote}#{safe_prefix}__{frag}{quote}"

    svg_text = _ID_RE.sub(_id_repl, svg_text)
    svg_text = _HREF_RE.sub(_href_repl, svg_text)
    return svg_text


# currentColor substitution
# ---------------------------------------------------------------------------


def substitute_current_color(svg_text: str) -> str:
    """Replace hardcoded black with ``currentColor`` for dark-mode adaptation.

    Two surfaces are rewritten:

    1. **Attribute form** — ``fill="black"`` / ``stroke="#000000"`` →
       ``fill="currentColor"`` / ``stroke="currentColor"``. Quote style is
       preserved so dvisvgm's single quotes stay single.
    2. **CSS-style form** — ``style="...;fill:#000000;..."`` →
       ``...;fill:currentColor;...``. Required for rdkit/SMILES which emits
       all colours via ``style='...'`` rather than dedicated attributes.

    Only black variants (``#000000``, ``#000``, ``black`` — case-insensitive)
    are matched. White, ``none``, and user-chosen colours are preserved
    intact, so D2 / Graphviz background rects (``fill="white"``) and TikZ
    user palettes survive unchanged.
    """
    def _attr_repl(m: re.Match[str]) -> str:
        prop, quote = m.group(1), m.group(2)
        return f"{prop}={quote}currentColor{quote}"

    def _style_repl(m: re.Match[str]) -> str:
        prop = m.group(1)
        return f"{prop}:currentColor"

    svg_text = _BLACK_ATTR_RE.sub(_attr_repl, svg_text)
    svg_text = _BLACK_STYLE_RE.sub(_style_repl, svg_text)
    return svg_text


# viewBox + pt-stripping
# ---------------------------------------------------------------------------


def enforce_viewbox(svg_text: str) -> str:
    """Strip ``pt`` units from ``width`` / ``height``; inject viewBox if absent.

    iOS WKWebView silently renders an SVG with ``pt`` units and no viewBox
    as 0×0 — the most common silent failure mode the cache exists to
    prevent. dvisvgm always emits ``pt``; this rule strips them. Other
    units (``mm`` from LilyPond, ``px`` from rdkit) are preserved per
    SPEC AC7.3 which specifies ``pt`` only.

    If the SVG already has a ``viewBox`` (true for every v1 renderer's
    output today), we don't touch it. The injection branch only fires for
    SVGs that lack one — kept as a safety net for renderers we may add
    later.
    """
    # Strip pt units.
    def _strip_pt(m: re.Match[str]) -> str:
        quote, value = m.group(1), m.group(2)
        return f"width={quote}{value}{quote}"

    def _strip_pt_h(m: re.Match[str]) -> str:
        quote, value = m.group(1), m.group(2)
        return f"height={quote}{value}{quote}"

    svg_text = _WIDTH_PT_RE.sub(_strip_pt, svg_text)
    svg_text = _HEIGHT_PT_RE.sub(_strip_pt_h, svg_text)

    # Inject viewBox if absent.
    if not _VIEWBOX_RE.search(svg_text):
        w_match = _WIDTH_NUM_RE.search(svg_text)
        h_match = _HEIGHT_NUM_RE.search(svg_text)
        if w_match and h_match:
            w = float(w_match.group(2))
            h = float(h_match.group(2))
            # Format without trailing zeros: 100.0 -> "100"; 100.5 -> "100.5".
            w_str = f"{w:g}"
            h_str = f"{h:g}"
            viewbox = f'viewBox="0 0 {w_str} {h_str}" '

            def _inject(m: re.Match[str]) -> str:
                trailing = m.group(1)
                # Always insert a space before the existing trailing char so
                # ``<svg>`` becomes ``<svg viewBox="...">``  and ``<svg ...>``
                # becomes ``<svg viewBox="..." ...>``.
                return f"<svg {viewbox.rstrip()}{trailing if trailing == '>' else trailing}"

            svg_text = _SVG_OPEN_RE.sub(_inject, svg_text, count=1)

    return svg_text


# Top-level chaining
# ---------------------------------------------------------------------------


def apply(svg_text: str, key: str) -> str:
    """Apply hardening rules to an SVG.

    Args:
        svg_text: Raw SVG content read from the renderer's working file.
        key: 16-char cache key. First 6 hex characters become the unique
            ID prefix (per PLAN §Phase 7 Task 7.1).
    """
    svg_text = prefix_ids(svg_text, key)
    svg_text = substitute_current_color(svg_text)
    svg_text = enforce_viewbox(svg_text)
    return svg_text
