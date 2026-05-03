"""Markdown code-block extraction and image-reference helpers.

Phase 2 covers TikZ blocks (``tikz`` and ``tikz-paused``). Phase 3 adds
``graphviz``. Phase 4 adds ``d2``. Phase 5 adds ``lilypond``. Phase 6 adds
``smiles`` — completing the v1 language surface.

Both ``tikz`` and ``tikz-paused`` are matched and BOTH normalise to
``language="tikz"`` for hash purposes — pausing or unpausing a block is a
display-only change and must not invalidate the cache.

Phase 12 writes image refs as ``![[...|visual-blocks]]``. The matcher still
accepts legacy ``tikz-cache`` and interim ``render-cache`` alt tags so old
refs are rewritten in place rather than duplicated.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from render_cache.languages import canonicalize_fence_lang, fence_regex_alternation

# Match a fenced block in a v1-supported language.
# Captures: (1) full fence line including lang, (2) raw fence-language tag,
# (3) inner code (everything between the open fence and the closing ```).
# When a new language adapter is added (Phases 4-6), append its fence tag to
# the alternation below AND register the canonical mapping in _FENCE_TO_LANG.
BLOCK_RE = re.compile(
    rf"^(```({fence_regex_alternation()}))\n(.*?)\n```",
    re.DOTALL | re.MULTILINE,
)

# Match an immediately-following cache image reference. Both ``.png`` (legacy
# Phase 0/1) and ``.svg`` (Phase 1+) are accepted so refs get rewritten in
# place rather than duplicated. Alt accepts legacy ``tikz-cache``, interim
# ``render-cache``, and canonical Phase 12 ``visual-blocks``.
CACHE_REF_RE = re.compile(
    r"\n+!\[\[([^\]|\n]+\.(?:png|svg))\|(?:tikz-cache|render-cache|visual-blocks)\]\]"
)

@dataclass
class CodeBlock:
    """A discovered fenced code block.

    Attributes:
        language: Canonical hashing language (``tikz-paused`` → ``tikz``).
        fence_lang: Raw fence tag as it appears in the source.
        source: Inner source text (the body between the fences).
        span: ``(start, end)`` byte/character offsets covering the entire
            fenced block in the host markdown content.
    """

    language: str
    fence_lang: str
    source: str
    span: tuple[int, int]


def find_blocks(content: str) -> list[CodeBlock]:
    """Return supported fenced code blocks in document order."""
    out: list[CodeBlock] = []
    for m in BLOCK_RE.finditer(content):
        fence_lang = m.group(2)
        canonical = canonicalize_fence_lang(fence_lang)
        if canonical is None:
            continue
        out.append(
            CodeBlock(
                language=canonical,
                fence_lang=fence_lang,
                source=m.group(3),
                span=(m.start(), m.end()),
            )
        )
    return out


def find_existing_ref(
    content: str, after_pos: int
) -> tuple[re.Match[str] | None, int, int]:
    """Find a cache image reference immediately following ``after_pos``.

    Allows only blank lines between the block end and the reference. Returns
    ``(match, abs_start, abs_end)`` where positions are absolute in
    ``content``. Returns ``(None, -1, -1)`` if no reference is found.
    """
    tail = content[after_pos:after_pos + 400]
    m = CACHE_REF_RE.match(tail)
    if not m:
        return None, -1, -1
    return m, after_pos + m.start(), after_pos + m.end()
