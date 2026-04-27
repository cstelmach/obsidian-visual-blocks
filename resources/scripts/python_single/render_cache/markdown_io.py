"""Markdown code-block extraction and image-reference helpers.

Phase 2 covers TikZ blocks (``tikz`` and ``tikz-paused``). Phases 3-6 extend
the regex to ``graphviz``, ``d2``, ``lilypond``, ``smiles``.

Both ``tikz`` and ``tikz-paused`` are matched and BOTH normalise to
``language="tikz"`` for hash purposes — pausing or unpausing a block is a
display-only change and must not invalidate the cache.

The image alt-tag ``tikz-cache`` is preserved for backward compatibility with
``.obsidian/snippets/tikz-cache.css``. When non-TikZ adapters arrive, the alt
tag may evolve (out of scope for Phase 2).
"""
from __future__ import annotations

import re
from dataclasses import dataclass


# Match a fenced block in a v1-supported language.
# Captures: (1) full fence line including lang, (2) raw fence-language tag,
# (3) inner code (everything between the open fence and the closing ```).
BLOCK_RE = re.compile(
    r"^(```(tikz(?:-paused)?))\n(.*?)\n```",
    re.DOTALL | re.MULTILINE,
)

# Match an immediately-following ``![[FILENAME|tikz-cache]]`` reference. Both
# ``.png`` (legacy Phase 0/1) and ``.svg`` (Phase 1+) are accepted so refs
# get rewritten in place rather than duplicated.
CACHE_REF_RE = re.compile(
    r"\n+!\[\[([^\]|\n]+\.(?:png|svg))\|tikz-cache\]\]"
)

# Map raw fence tags to canonical hashing language.
_FENCE_TO_LANG = {
    "tikz": "tikz",
    "tikz-paused": "tikz",
}


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
        canonical = _FENCE_TO_LANG.get(fence_lang, fence_lang)
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
    """Find a ``![[…|tikz-cache]]`` reference immediately following ``after_pos``.

    Allows only blank lines between the block end and the reference. Returns
    ``(match, abs_start, abs_end)`` where positions are absolute in
    ``content``. Returns ``(None, -1, -1)`` if no reference is found.
    """
    tail = content[after_pos:after_pos + 400]
    m = CACHE_REF_RE.match(tail)
    if not m:
        return None, -1, -1
    return m, after_pos + m.start(), after_pos + m.end()
