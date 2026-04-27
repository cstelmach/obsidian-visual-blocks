"""Cache-key computation per SPEC §3.9 (canonical formula).

::

    key = SHA-256(
        normalize(source) + 0x00
      + language.encode('utf-8') + 0x00
      + json.dumps(attrs, sorted_keys=True).encode('utf-8') + 0x00
      + preamble_hash.encode('utf-8')
    ).hex()[0:16]

The 16-char truncation gives ~4 × 10⁻¹⁵ collision probability at a 600-block
vault scale (SPEC §3.7 T8) and keeps cache filenames readable. The TypeScript
plugin must produce byte-identical output (T12); see ``main.ts`` once Phase 8
lands.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from render_cache.normalize import normalize

_KEY_LEN = 16


def compute_key(
    source: str,
    language: str,
    attrs: dict[str, Any],
    preamble_hash: str,
) -> str:
    """Return the canonical 16-char SHA-256 cache key per SPEC §3.9.

    Args:
        source: Raw block source. Will be passed through ``normalize`` first.
        language: Canonical language tag (``"tikz"``, ``"graphviz"``, ...).
        attrs: Per-block render attributes; serialised with ``sort_keys=True``
            for canonical JSON.
        preamble_hash: 16-char digest of the active preamble (see
            ``preamble_digest``).
    """
    payload = (
        normalize(source).encode("utf-8") + b"\x00"
        + language.encode("utf-8") + b"\x00"
        + json.dumps(attrs, sort_keys=True).encode("utf-8") + b"\x00"
        + preamble_hash.encode("utf-8")
    )
    return hashlib.sha256(payload).hexdigest()[:_KEY_LEN]


def preamble_digest(preamble_text: str) -> str:
    """Return a 16-char SHA-256 digest of a preamble.

    Phase 2 hashes the adapter's hardcoded ``preamble_text``. Phase 8+ extends
    this to per-folder ``_preamble.<lang>`` files so a preamble change anywhere
    in the vault correctly invalidates affected caches (SPEC §3.7 T10).
    """
    return hashlib.sha256(preamble_text.encode("utf-8")).hexdigest()[:_KEY_LEN]
