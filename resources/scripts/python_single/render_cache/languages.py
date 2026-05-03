"""Shared language metadata for the Visual Blocks renderer."""
from __future__ import annotations

import re

CANONICAL_LANGUAGES = ("tikz", "graphviz", "d2", "lilypond", "smiles")

FENCE_TO_LANGUAGE = {
    "tikz": "tikz",
    "tikz-paused": "tikz",
    "graphviz": "graphviz",
    "d2": "d2",
    "lilypond": "lilypond",
    "smiles": "smiles",
}


def canonicalize_fence_lang(fence_lang: str) -> str | None:
    """Return canonical language for a fence tag, or ``None`` if unsupported."""
    return FENCE_TO_LANGUAGE.get(fence_lang.lower())


def parse_language_filter(raw: str | None) -> set[str] | None:
    """Parse ``--languages`` as comma-separated canonical language ids."""
    if raw is None:
        return None
    languages = {part.strip().lower() for part in raw.split(",") if part.strip()}
    unknown = sorted(languages.difference(CANONICAL_LANGUAGES))
    if unknown:
        raise ValueError(
            "unknown language(s): "
            + ", ".join(unknown)
            + "; expected one or more of "
            + ", ".join(CANONICAL_LANGUAGES)
        )
    return languages


def fence_tags_for_languages(languages: set[str] | None = None) -> tuple[str, ...]:
    """Return raw fence tags that map to the selected canonical languages."""
    selected = set(CANONICAL_LANGUAGES) if languages is None else set(languages)
    return tuple(
        fence
        for fence, canonical in FENCE_TO_LANGUAGE.items()
        if canonical in selected
    )


def fence_regex_alternation(languages: set[str] | None = None) -> str:
    """Regex alternation for supported fence tags, longest aliases first."""
    tags = sorted(fence_tags_for_languages(languages), key=len, reverse=True)
    return "|".join(re.escape(tag) for tag in tags)
