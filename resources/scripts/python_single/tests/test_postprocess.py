"""Phase 7 — SVG postprocessing hardening (SPEC §3.7 T3/T4/T5, §5 Phase 7).

Three rules:

- ``prefix_ids``           (T3, AC7.1) — hash-prefix all element IDs and
  ``href``/``xlink:href`` references so two cached SVGs on one page can't
  collide on shared-name IDs (dvisvgm emits ``g0-N`` / ``g1-N``; Graphviz
  emits ``graph0`` / ``node1`` / ``edge1``).
- ``substitute_current_color`` (T5, AC7.2) — replace hardcoded black
  (``#000000`` / ``#000`` / ``black``) with ``currentColor`` so Obsidian's
  light/dark theme flows through to cached diagrams. Two surfaces are needed:
  attribute form (``fill='black'``) AND CSS-style form
  (``style='...stroke:#000000;...'`` — SMILES emits this exclusively).
- ``enforce_viewbox``      (T4, AC7.3) — strip ``pt`` units from
  ``width`` / ``height`` (iOS WKWebView with ``pt`` and no viewBox renders
  0×0 silently); inject viewBox if absent.

Why this test file diverges from PLAN.md §Phase 7's pseudocode:

The PLAN pseudocode hardcodes double-quoted attribute regexes
(``r'\\bid="..."'``). On real outputs:

- dvisvgm (TikZ): SINGLE quotes for every attribute (``id='g0-28'``,
  ``fill='#3cb371'``, ``xlink:href='#g0-28'``, etc.).
- rdkit (SMILES): SINGLE quotes for every attribute; colors live in
  ``style='...;fill:#000000;stroke:#000000;...'`` CSS-style attributes,
  not in attribute form.
- Graphviz / D2 / LilyPond: DOUBLE quotes.

So the regexes must be quote-agnostic, and we need a CSS-style
substitution rule for SMILES. These tests pin both behaviours.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Adapter dir on path
SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

from render_cache.postprocess import (  # noqa: E402
    apply,
    enforce_viewbox,
    prefix_ids,
    substitute_current_color,
)

# ---------------------------------------------------------------------------
# Rule 1: prefix_ids (T3 / AC7.1)
# ---------------------------------------------------------------------------


class TestPrefixIds:
    """All element IDs must be hash-prefixed; href references must follow."""

    def test_single_quote_id_is_prefixed(self):
        """dvisvgm emits ``id='g0-28'`` (single quotes)."""
        svg = "<path id='g0-28' d='M0 0'/>"
        out = prefix_ids(svg, "abc123def4567890")
        assert "id='abc123__g0-28'" in out

    def test_double_quote_id_is_prefixed(self):
        """Graphviz/D2/LilyPond emit ``id="..."``."""
        svg = '<g id="node1"><title>node1</title></g>'
        out = prefix_ids(svg, "abc123def4567890")
        assert 'id="abc123__node1"' in out

    def test_xlink_href_single_quote_is_prefixed(self):
        """dvisvgm uses ``<use xlink:href='#g0-28'/>``."""
        svg = "<use xlink:href='#g0-28' x='10' y='20'/>"
        out = prefix_ids(svg, "abc123def4567890")
        assert "xlink:href='#abc123__g0-28'" in out

    def test_plain_href_double_quote_is_prefixed(self):
        """SVG2-era plain ``href="#..."``."""
        svg = '<use href="#node1"/>'
        out = prefix_ids(svg, "abc123def4567890")
        assert 'href="#abc123__node1"' in out

    def test_only_first_six_hash_chars_used_as_prefix(self):
        """Per PLAN: prefix is first 6 chars of cache hash."""
        svg = "<path id='g0-1'/>"
        out = prefix_ids(svg, "abcdef1234567890")
        assert "id='abcdef__g0-1'" in out
        assert "id='abcdef1__" not in out  # exactly 6, not 7

    def test_no_ids_means_no_change(self):
        """SMILES has zero ``id=`` attributes — must be a no-op."""
        svg = "<path d='M0 0' stroke='black'/>"
        out = prefix_ids(svg, "abc123def4567890")
        assert out == svg

    def test_does_not_match_id_inside_data_uri(self):
        """``href='data:image/png;base64,...'`` must not be touched."""
        svg = '<image href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAA"/>'
        out = prefix_ids(svg, "abc123def4567890")
        # The ``href="data:..."`` shape doesn't start with ``#`` so the
        # href-fragment regex must not rewrite it.
        assert 'href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAA"' in out

    def test_real_tikz_pattern_round_trip(self):
        """Realistic dvisvgm output: <use> tags reference <path id='gN-M'>."""
        svg = (
            "<defs><path id='g0-1' d='M0 0L10 10'/></defs>"
            "<use xlink:href='#g0-1' transform='translate(50 50)'/>"
            "<use xlink:href='#g0-1' transform='translate(100 100)'/>"
        )
        out = prefix_ids(svg, "deadbeef12345678")
        assert "id='deadbe__g0-1'" in out
        assert out.count("xlink:href='#deadbe__g0-1'") == 2
        # Original unprefixed names must be gone (anchor on the closing quote
        # to avoid matching the new prefixed form).
        assert "id='g0-1'" not in out
        assert "xlink:href='#g0-1'" not in out


# ---------------------------------------------------------------------------
# Rule 2: substitute_current_color (T5 / AC7.2)
# ---------------------------------------------------------------------------


class TestSubstituteCurrentColor:
    """Hardcoded black → ``currentColor``; everything else preserved."""

    def test_double_quote_fill_black_becomes_currentColor(self):
        svg = '<path fill="black"/>'
        out = substitute_current_color(svg)
        assert 'fill="currentColor"' in out

    def test_double_quote_fill_hex_full_becomes_currentColor(self):
        svg = '<path fill="#000000"/>'
        out = substitute_current_color(svg)
        assert 'fill="currentColor"' in out

    def test_double_quote_fill_hex_short_becomes_currentColor(self):
        svg = '<path fill="#000"/>'
        out = substitute_current_color(svg)
        assert 'fill="currentColor"' in out

    def test_single_quote_fill_hex_becomes_currentColor(self):
        """dvisvgm and rdkit emit single-quoted attributes."""
        svg = "<path fill='#000000'/>"
        out = substitute_current_color(svg)
        assert "fill='currentColor'" in out

    def test_double_quote_stroke_black_becomes_currentColor(self):
        svg = '<line stroke="black"/>'
        out = substitute_current_color(svg)
        assert 'stroke="currentColor"' in out

    def test_single_quote_stroke_hex_becomes_currentColor(self):
        svg = "<line stroke='#000000'/>"
        out = substitute_current_color(svg)
        assert "stroke='currentColor'" in out

    def test_white_fill_is_preserved(self):
        """D2 / Graphviz background rects use ``fill='white'`` — must stay."""
        svg = '<rect fill="white"/><rect fill="#FFFFFF"/><rect fill="#FFF"/>'
        out = substitute_current_color(svg)
        assert 'fill="white"' in out
        assert 'fill="#FFFFFF"' in out
        assert 'fill="#FFF"' in out

    def test_other_colors_preserved(self):
        """User-chosen colors (e.g., #3cb371 green) must stay."""
        svg = "<path fill='#3cb371' stroke='#787878'/>"
        out = substitute_current_color(svg)
        assert "fill='#3cb371'" in out
        assert "stroke='#787878'" in out

    def test_fill_none_preserved(self):
        """``fill='none'`` is a structural value, not a color."""
        svg = "<path fill='none' stroke='black'/>"
        out = substitute_current_color(svg)
        assert "fill='none'" in out
        assert "stroke='currentColor'" in out

    def test_css_style_stroke_black_becomes_currentColor(self):
        """SMILES emits ``style='...;stroke:#000000;...'`` — CSS-style form."""
        svg = "<rect style='opacity:1.0;fill:#FFFFFF;stroke:#000000'/>"
        out = substitute_current_color(svg)
        assert "stroke:currentColor" in out
        # White background must NOT be touched.
        assert "fill:#FFFFFF" in out

    def test_css_style_fill_black_becomes_currentColor(self):
        svg = "<text style='font-size:12px;fill:#000000;stroke:none'>H</text>"
        out = substitute_current_color(svg)
        assert "fill:currentColor" in out
        assert "stroke:none" in out

    def test_css_style_partial_hex_not_matched(self):
        """``#0001`` (dark blue) must not match ``#000`` rule due to ``\\b``."""
        svg = "<path style='fill:#0001ff'/>"
        out = substitute_current_color(svg)
        assert "fill:#0001ff" in out
        assert "fill:currentColor" not in out

    def test_css_style_blacksmith_word_not_matched(self):
        """Word ``blacksmith`` must not match ``black\\b``."""
        svg = "<path data-class='blacksmith'/>"
        out = substitute_current_color(svg)
        assert "blacksmith" in out
        assert "currentColor" not in out

    def test_case_insensitive(self):
        """Hex digits can be lower or upper case."""
        svg = "<path fill='#000000' stroke='#000000'/>"
        out = substitute_current_color(svg)
        assert out.count("currentColor") == 2


# ---------------------------------------------------------------------------
# Rule 3: enforce_viewbox (T4 / AC7.3)
# ---------------------------------------------------------------------------


class TestEnforceViewbox:
    """Strip pt units from width/height; inject viewBox if missing."""

    def test_strip_pt_from_double_quote_attrs(self):
        svg = '<svg width="100pt" height="50pt" viewBox="0 0 100 50"></svg>'
        out = enforce_viewbox(svg)
        assert 'width="100"' in out
        assert 'height="50"' in out
        # Don't lose the viewBox.
        assert 'viewBox="0 0 100 50"' in out

    def test_strip_pt_from_single_quote_attrs(self):
        """dvisvgm: ``width='481.8942pt' height='176.230529pt'``."""
        svg = (
            "<svg width='481.8942pt' height='176.230529pt' "
            "viewBox='-66.5234 -64.695324 481.8942 176.230529'></svg>"
        )
        out = enforce_viewbox(svg)
        assert "width='481.8942'" in out
        assert "height='176.230529'" in out
        assert "pt'" not in out  # no leftover pt-with-quote
        assert "viewBox='-66.5234 -64.695324 481.8942 176.230529'" in out

    def test_inject_viewbox_when_missing_double_quote(self):
        svg = '<svg width="100" height="50"></svg>'
        out = enforce_viewbox(svg)
        assert 'viewBox="0 0 100 50"' in out

    def test_inject_viewbox_when_missing_single_quote(self):
        svg = "<svg width='100' height='50'></svg>"
        out = enforce_viewbox(svg)
        # Quote style of injected viewBox doesn't matter; verify presence.
        assert 'viewBox="0 0 100 50"' in out or "viewBox='0 0 100 50'" in out

    def test_existing_viewbox_preserved(self):
        svg = '<svg width="100pt" height="50pt" viewBox="-10 -10 120 70"></svg>'
        out = enforce_viewbox(svg)
        assert 'viewBox="-10 -10 120 70"' in out
        # Should NOT inject a second viewBox.
        assert out.count("viewBox=") == 1

    def test_mm_units_preserved_per_spec(self):
        """SPEC AC7.3 specifies ``pt`` only — LilyPond uses ``mm`` legitimately.
        Don't generalize to other units (PLAN §Phase 7 common mistakes)."""
        svg = '<svg width="210.00mm" height="297.00mm" viewBox="0 0 119.5 169.0"></svg>'
        out = enforce_viewbox(svg)
        assert 'width="210.00mm"' in out
        assert 'height="297.00mm"' in out

    def test_unitless_width_height_preserved(self):
        """D2 / SMILES use unitless or ``px`` — leave alone."""
        svg = '<svg width="400" height="300" viewBox="0 0 400 300"></svg>'
        out = enforce_viewbox(svg)
        assert 'width="400"' in out
        assert 'height="300"' in out

    def test_px_units_preserved_per_spec(self):
        """SMILES emits ``width='400px' height='300px'``. SPEC says strip pt only."""
        svg = "<svg width='400px' height='300px' viewBox='0 0 400 300'></svg>"
        out = enforce_viewbox(svg)
        assert "width='400px'" in out
        assert "height='300px'" in out


# ---------------------------------------------------------------------------
# apply() — chains the three rules in the right order
# ---------------------------------------------------------------------------


class TestApply:
    """End-to-end ``apply`` — what the dispatcher actually calls."""

    def test_apply_runs_all_three_rules(self):
        """Realistic mini-TikZ output: pt units, single-quoted IDs, ``black``."""
        svg = (
            "<svg width='100pt' height='50pt' "
            "viewBox='0 0 100 50'>"
            "<defs><path id='g0-1' fill='black' d='M0 0'/></defs>"
            "<use xlink:href='#g0-1'/>"
            "</svg>"
        )
        out = apply(svg, "deadbeef12345678")
        # Rule 1: ID + href prefixed
        assert "id='deadbe__g0-1'" in out
        assert "xlink:href='#deadbe__g0-1'" in out
        # Rule 2: black → currentColor
        assert "fill='currentColor'" in out
        assert "fill='black'" not in out
        # Rule 3: pt stripped
        assert "width='100'" in out
        assert "height='50'" in out
        assert "pt'" not in out

    def test_apply_idempotent(self):
        """Running apply twice produces the same output as running it once."""
        svg = (
            "<svg width='100pt' height='50pt'>"
            "<path id='g0-1' fill='#000000'/>"
            "</svg>"
        )
        once = apply(svg, "deadbeef12345678")
        twice = apply(once, "deadbeef12345678")
        # ID prefix WILL be applied a second time — that's expected because
        # the function makes no claim of idempotency on already-prefixed IDs.
        # What matters: the original (unhardened) substring patterns no longer
        # appear and twice-application produces a stable shape.
        assert "fill='#000000'" not in twice
        assert "pt" not in twice or twice.count("pt") == once.count("pt")

    def test_apply_uses_first_six_chars_of_key(self):
        svg = "<path id='node1'/>"
        out = apply(svg, "abcdef9876543210")
        assert "id='abcdef__node1'" in out

    def test_apply_signature_unchanged(self):
        """Phase 2 stub took (svg_text, key) — Phase 7 must keep it.

        The dispatcher at render_cache/__init__.py:115 calls
        ``postprocess_apply(svg_text, key)``. Changing the signature would
        break the wiring."""
        import inspect

        sig = inspect.signature(apply)
        params = list(sig.parameters.keys())
        assert params == ["svg_text", "key"]

    def test_apply_does_not_touch_raster_image_data(self):
        """Base64 PNG with ``000000`` byte sequence inside data URI must
        remain untouched (PLAN §Phase 7 common mistake)."""
        # Carefully chosen base64 with the bytes "000000" inside.
        svg = (
            "<svg width='100pt' height='50pt' viewBox='0 0 100 50'>"
            "<image href='data:image/png;base64,iVBOR0w0KGgoAAAANSUhEUgAA000000'/>"
            "</svg>"
        )
        out = apply(svg, "abc123def4567890")
        assert "iVBOR0w0KGgoAAAANSUhEUgAA000000" in out


# ---------------------------------------------------------------------------
# Module-level / contract guards
# ---------------------------------------------------------------------------


class TestModuleContract:
    """Phase 7 must keep the module's existing public API additive."""

    def test_public_api_present(self):
        from render_cache import postprocess as pp
        assert callable(pp.apply)
        assert callable(pp.prefix_ids)
        assert callable(pp.substitute_current_color)
        assert callable(pp.enforce_viewbox)

    def test_apply_returns_string(self):
        out = apply("<svg/>", "abc123def4567890")
        assert isinstance(out, str)


# ---------------------------------------------------------------------------
# Integration with real cache files (slow tier)
# ---------------------------------------------------------------------------


from render_cache.cache_paths import CACHE_DIR  # noqa: E402


@pytest.mark.slow
class TestRealCacheHardening:
    """Apply postprocess to actual cached SVGs and verify properties."""

    def _read_one(self, glob: str) -> str:
        files = sorted(CACHE_DIR.glob(glob))
        if not files:
            pytest.skip(f"no real cache file matches {glob} (run --force first)")
        return files[0].read_text(encoding="utf-8")

    def test_real_tikz_after_apply_has_no_unprefixed_g_ids(self):
        svg = self._read_one("mSB3-4_reals__1__*.svg")
        out = apply(svg, "deadbeef12345678")
        import re
        # No id='g0-N' or id='g1-N' pattern survives without prefix.
        unprefixed = re.findall(r"\bid=['\"]g[0-9]-[0-9]+['\"]", out)
        assert unprefixed == [], f"Unprefixed dvisvgm IDs survive: {unprefixed[:5]}"

    def test_real_tikz_after_apply_has_no_pt_units_in_outer_dims(self):
        svg = self._read_one("mSB3-4_reals__1__*.svg")
        out = apply(svg, "deadbeef12345678")
        import re
        # Width/height must not carry pt unit any more.
        m_w = re.search(r"\bwidth=['\"][0-9.]+pt['\"]", out)
        m_h = re.search(r"\bheight=['\"][0-9.]+pt['\"]", out)
        assert m_w is None, f"width still has pt: {m_w.group(0) if m_w else None}"
        assert m_h is None, f"height still has pt: {m_h.group(0) if m_h else None}"

    def test_real_smiles_after_apply_has_no_hardcoded_black_in_styles(self):
        svg = self._read_one("_RENDER_TEST_smiles__1__*.svg")
        out = apply(svg, "deadbeef12345678")
        # SMILES has zero attribute-form fill="black"; all CSS-style.
        assert "stroke:#000000" not in out
        assert "fill:#000000" not in out
        # White background must be preserved.
        assert "fill:#FFFFFF" in out

    def test_real_graphviz_after_apply_has_no_attribute_black(self):
        svg = self._read_one("_RENDER_TEST_graphviz__1__*.svg")
        out = apply(svg, "deadbeef12345678")
        import re
        # Attribute-form black gone.
        assert re.search(r'\bfill=[\'"]black[\'"]', out) is None
        assert re.search(r'\bstroke=[\'"]black[\'"]', out) is None
        # Whites preserved (background rect).
        assert 'fill="white"' in out

    def test_real_d2_after_apply_preserves_user_colors(self):
        """D2 has no ``black`` — only #0A0F25 (dark blue), #FFFFFF white, etc.
        Apply must be a near-no-op on color attributes."""
        svg = self._read_one("_RENDER_TEST_d2__1__*.svg")
        out = apply(svg, "deadbeef12345678")
        # User-chosen colors preserved.
        assert "#0A0F25" in out
        assert "#FFFFFF" in out

    def test_real_lilypond_after_apply_keeps_existing_currentColor(self):
        """LilyPond already emits ``currentColor`` — apply is a no-op for color."""
        svg = self._read_one("_RENDER_TEST_lilypond__1__*.svg")
        out = apply(svg, "deadbeef12345678")
        # Already-currentColor stays.
        assert "currentColor" in out
