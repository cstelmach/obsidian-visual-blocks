"""Source-text canonicalisation for stable hashing.

SPEC §3.7 T9: source normalisation (whitespace, comments, line endings) BEFORE
hashing — otherwise trivial edits thrash the cache.

Phase 2 implements the language-agnostic part: line endings, per-line whitespace
trim, blank-line collapse, leading/trailing blank strip. Per-language comment
stripping (e.g. TikZ '%' to end-of-line) is the adapter's responsibility — the
adapter pre-processes its source before passing it through ``compute_key``.
This module owns whitespace canonicalisation only.
"""
from __future__ import annotations


def normalize(source: str) -> str:
    """Canonicalise ``source`` for hashing.

    Operations (in order):
        1. CRLF / lone-CR → LF
        2. Strip leading and trailing whitespace from each line
        3. Collapse runs of blank lines to a single blank line
        4. Strip leading and trailing blank lines

    Examples:
        >>> normalize("  hello\\n\\n\\n\\n  world  ")
        'hello\\n\\nworld'
        >>> normalize("a\\r\\nb")
        'a\\nb'
        >>> normalize("\\n\\nhello\\n\\n")
        'hello'
    """
    s = source.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.strip() for ln in s.split("\n")]

    out: list[str] = []
    prev_blank = True  # treating start as blank skips leading blank lines
    for ln in lines:
        if ln == "":
            if prev_blank:
                continue
            out.append("")
            prev_blank = True
        else:
            out.append(ln)
            prev_blank = False
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)
