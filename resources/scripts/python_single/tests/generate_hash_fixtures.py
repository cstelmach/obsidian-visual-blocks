"""Generate the cross-language hash fixture file.

Single source of truth for the cache-key contract (SPEC §3.9, T12).

Both sides consume the file:

- Python  : ``tests/test_hash_fixtures.py`` — re-derives every key, asserts
            equality with ``expectedKey``. Catches a regression in
            ``compute_key`` or ``normalize`` immediately.
- TypeScript: ``.obsidian/plugins/obsidian-render-cache/tests/hash.test.ts``
            — ports the same algorithm, asserts byte-identity. Catches
            divergence between Python and the plugin (T12).

Re-run after any change to ``hash.py`` / ``normalize.py``. The TS test will
fail until the TS port is updated to match.

Usage:
    python3 -m tests.generate_hash_fixtures   # writes plugin path
    python3 -m tests.generate_hash_fixtures --stdout
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "resources" / "scripts" / "python_single"))

from render_cache.hash import compute_key  # noqa: E402

DEFAULT_OUT = (
    REPO_ROOT
    / ".obsidian"
    / "plugins"
    / "obsidian-render-cache"
    / "tests"
    / "fixtures"
    / "hash_fixtures.json"
)

# Each fixture targets one normalization/canonicalization rule. Keep names
# stable — the TS test references them in failure messages.
_FIXTURES = [
    {
        "name": "empty_source",
        "description": "All-whitespace source collapses to empty string.",
        "source": "   \n   \n",
        "language": "tikz",
        "attrs": {},
        "preambleHash": "0000000000000000",
    },
    {
        "name": "simple_tikz",
        "description": "Plain TikZ block, no preamble, no attrs.",
        "source": r"\begin{tikzpicture}\draw (0,0) -- (1,1);\end{tikzpicture}",
        "language": "tikz",
        "attrs": {},
        "preambleHash": "0000000000000000",
    },
    {
        "name": "tikz_with_comments_NOT_stripped",
        "description": (
            "Python's normalize() does NOT strip TikZ '%' comments — the "
            "adapter is responsible for any per-language preprocessing, but "
            "the Phase 2 dispatcher passes block.source raw. The TS port must "
            "match this behavior; comments must alter the hash."
        ),
        "source": "\\draw (0,0) -- (1,1); % a comment\n\\draw (2,2) -- (3,3);",
        "language": "tikz",
        "attrs": {},
        "preambleHash": "0000000000000000",
    },
    {
        "name": "crlf_line_endings",
        "description": "CRLF must canonicalize to LF before hashing.",
        "source": "line one\r\nline two\r\nline three",
        "language": "graphviz",
        "attrs": {},
        "preambleHash": "0000000000000000",
    },
    {
        "name": "lone_cr_line_endings",
        "description": "Lone CR (legacy Mac) must canonicalize to LF.",
        "source": "line one\rline two\rline three",
        "language": "graphviz",
        "attrs": {},
        "preambleHash": "0000000000000000",
    },
    {
        "name": "multi_blank_line_collapse",
        "description": "Multiple blank-line runs collapse to a single blank line.",
        "source": "first\n\n\n\n\nsecond\n\n\nthird",
        "language": "d2",
        "attrs": {},
        "preambleHash": "0000000000000000",
    },
    {
        "name": "leading_trailing_blanks_stripped",
        "description": "Leading + trailing blank lines are dropped.",
        "source": "\n\n\nbody only\n\n\n",
        "language": "d2",
        "attrs": {},
        "preambleHash": "0000000000000000",
    },
    {
        "name": "per_line_whitespace_strip",
        "description": (
            "Python's normalize() uses ln.strip() per line — both leading AND "
            "trailing whitespace per line. PLAN.md §Phase 8 pseudocode said "
            "trimEnd() (trailing only), which would diverge. TS port MUST "
            "use full strip(); this fixture catches that bug."
        ),
        "source": "    leading  \n  middle  \n   trailing  ",
        "language": "lilypond",
        "attrs": {},
        "preambleHash": "0000000000000000",
    },
    {
        "name": "unicode_source",
        "description": "Non-ASCII content (Greek, em-dash, smart quotes).",
        "source": "α + β = γ — “smart” quotes here",
        "language": "smiles",
        "attrs": {},
        "preambleHash": "0000000000000000",
    },
    {
        "name": "language_distinguishes_hash",
        "description": (
            "Same source under a different language tag must hash differently "
            "(SPEC §3.7 T10)."
        ),
        "source": "abc",
        "language": "graphviz",
        "attrs": {},
        "preambleHash": "0000000000000000",
    },
    {
        "name": "preamble_change_invalidates_cache",
        "description": (
            "Different preambleHash → different cache key, even with identical "
            "source (SPEC §3.7 T10 anti-poisoning)."
        ),
        "source": r"\draw (0,0) circle (1);",
        "language": "tikz",
        "attrs": {},
        "preambleHash": "abcdef0123456789",
    },
    {
        "name": "attrs_empty_object",
        "description": (
            "attrs={} → both Python and JS produce the same JSON ('{}'). "
            "Baseline before the spaces-divergence fixture."
        ),
        "source": "x",
        "language": "smiles",
        "attrs": {},
        "preambleHash": "0000000000000000",
    },
    {
        "name": "attrs_single_key_PYTHON_JSON_SPACES",
        "description": (
            "Python json.dumps emits '{\"k\": \"v\"}' WITH a space after the "
            "colon; JS JSON.stringify emits '{\"k\":\"v\"}' WITHOUT. The TS "
            "port MUST replicate Python's spacing in its own pythonJsonDumps "
            "helper or the hash will diverge silently when attrs become "
            "non-empty in Phase 9+."
        ),
        "source": "x",
        "language": "tikz",
        "attrs": {"k": "v"},
        "preambleHash": "0000000000000000",
    },
    {
        "name": "attrs_multi_key_sorted",
        "description": (
            "Python sort_keys=True sorts top-level keys alphabetically; JS "
            "JSON.stringify(obj, Object.keys(obj).sort()) produces the same "
            "ordering BUT without the inter-key spaces. TS port must sort "
            "AND match Python's spacing."
        ),
        "source": "x",
        "language": "tikz",
        "attrs": {"zeta": "z", "alpha": "a", "mu": "m"},
        "preambleHash": "0000000000000000",
    },
]


def _build_fixture(spec: dict) -> dict:
    return {
        **spec,
        "expectedKey": compute_key(
            spec["source"], spec["language"], spec["attrs"], spec["preambleHash"]
        ),
    }


def build_fixtures() -> list[dict]:
    return [_build_fixture(s) for s in _FIXTURES]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "--stdout",
        action="store_true",
        help="Print to stdout instead of writing to the plugin fixture path.",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Output path (default: {DEFAULT_OUT}).",
    )
    args = p.parse_args(argv)

    fixtures = build_fixtures()
    payload = {
        "schemaVersion": 1,
        "rendererVersion": "0.2.0",
        "description": (
            "Cross-language hash fixture. Single source of truth for SPEC "
            "§3.9 / T12. Regenerated by tests/generate_hash_fixtures.py."
        ),
        "fixtures": fixtures,
    }
    text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False) + "\n"

    if args.stdout:
        sys.stdout.write(text)
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"wrote {len(fixtures)} fixtures to {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
