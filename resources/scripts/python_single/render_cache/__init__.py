"""``render_cache`` — multi-language pre-render cache for Obsidian.

This package replaces the single-file ``tikz_cache.py`` with a clean
adapter-based architecture per SPEC §3.3. Phase 2 ships:

    - ``normalize``    : source canonicalisation (SPEC §3.7 T9)
    - ``hash``         : canonical 16-char cache key (SPEC §3.9)
    - ``markdown_io``  : code-block extraction + image-ref insertion
    - ``cache_paths``  : filesystem layout (legacy dir retained — Phase 12 migrates)
    - ``index``        : ``index.json`` reader/writer (SPEC §3.4 schema)
    - ``postprocess``  : Phase 7 SVG hardening hooks (Phase 2: pass-through)
    - ``adapters.base``: ``RendererAdapter`` ABC (SPEC §3.4)
    - ``adapters.tikz``: TikZ adapter (lualatex+dvisvgm, Phase 1 invariants preserved)

The CLI entry point lives at ``render_cache.py`` (the file) at the package's
parent directory. ``tikz_cache.py`` is a deprecation shim that forwards here.
"""
from __future__ import annotations

import argparse
import shutil
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

from render_cache.adapters import REGISTRY
from render_cache.adapters.base import RenderError
from render_cache.cache_paths import (
    CACHE_DIR,
    INDEX_PATH,
    VAULT_ROOT,
    cache_filename,
    cache_path_for,
)
from render_cache.hash import compute_key, preamble_digest
from render_cache.index import RENDERER_VERSION, load_index, save_index
from render_cache.markdown_io import find_blocks, find_existing_ref
from render_cache.postprocess import apply as postprocess_apply

__all__ = ["main", "process_file", "sweep_orphans", "find_all_md_with_blocks"]

SCAN_ROOTS = [VAULT_ROOT / "kn"]


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def _vault_relative(p: Path) -> str:
    try:
        return p.relative_to(VAULT_ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def process_file(md_path: Path, force: bool, dry_run: bool) -> int:
    """Process one markdown file. Return number of failed blocks (0 = all ok)."""
    if not md_path.exists():
        print(f"[!] not found: {md_path}", file=sys.stderr)
        return 1

    content = md_path.read_text(encoding="utf-8")
    blocks = find_blocks(content)
    if not blocks:
        return 0

    rel = _vault_relative(md_path)
    print(f"=> {rel}: {len(blocks)} block(s)")

    index = load_index(INDEX_PATH)
    note_entry = index["notes"].setdefault(rel, {"blocks": []})

    edits: list[tuple[int, int, str]] = []
    in_use_filenames: set[str] = set()
    failed = 0
    new_blocks_meta: list[dict] = []

    for idx, block in enumerate(blocks, 1):
        adapter = REGISTRY.get(block.language)
        if adapter is None:
            print(f"   [{idx}] {block.language}: no adapter — skipped")
            failed += 1
            continue

        attrs: dict = {}
        preamble_h = preamble_digest(adapter.preamble_text)
        if preamble_h:
            index["preambleHashes"].setdefault(
                f"<adapter:{block.language}>", preamble_h
            )

        key = compute_key(block.source, block.language, attrs, preamble_h)
        svg_name = cache_filename(md_path.stem, idx, key)
        svg_path = cache_path_for(md_path.stem, idx, key)
        in_use_filenames.add(svg_name)

        rendered = False
        ok = True
        if force or not svg_path.exists():
            print(f"   [{idx}] {block.language} key={key} → render")
            if dry_run:
                print(f"        (dry-run) would render to {svg_path}")
                ok = svg_path.exists()
            else:
                workdir = CACHE_DIR / f"_work_{md_path.stem}_{idx}"
                workdir.mkdir(parents=True, exist_ok=True)
                try:
                    out_svg = adapter.render(block.source, attrs, workdir)
                    svg_text = out_svg.read_text(encoding="utf-8")
                    svg_text = postprocess_apply(svg_text, key)
                    svg_path.parent.mkdir(parents=True, exist_ok=True)
                    svg_path.write_text(svg_text, encoding="utf-8")
                    rendered = True
                except RenderError as e:
                    print(f"        FAILED: {e}")
                    ok = False
                    failed += 1
                finally:
                    shutil.rmtree(workdir, ignore_errors=True)
        else:
            print(f"   [{idx}] {block.language} key={key} → cache hit")

        if ok:
            new_blocks_meta.append(
                {
                    "blockIdx": idx - 1,  # SPEC §3.4 uses 0-based block index
                    "language": block.language,
                    "sourceHash": key,
                    "cachePath": _vault_relative(svg_path),
                    "renderedAt": _utc_now() if rendered else None,
                    "rendererVersion": RENDERER_VERSION,
                    "outputFormat": "svg",
                    "renderMs": None,
                    "outputBytes": svg_path.stat().st_size if svg_path.exists() else 0,
                    "lastError": None,
                }
            )

            block_end = block.span[1]
            new_ref = f"\n\n![[{svg_name}|tikz-cache]]"
            existing, ref_start, ref_end = find_existing_ref(content, block_end)
            if existing is None:
                edits.append((block_end, block_end, new_ref))
            elif existing.group(1) != svg_name:
                edits.append((ref_start, ref_end, new_ref))

    new_content = content
    for start, end, replacement in sorted(edits, key=lambda e: -e[0]):
        new_content = new_content[:start] + replacement + new_content[end:]

    # Cleanup orphaned SVGs for this note (different key, same stem+idx slot).
    if not dry_run:
        for old_svg in CACHE_DIR.glob(f"{md_path.stem}__*.svg"):
            if old_svg.name not in in_use_filenames:
                print(f"   [-] orphan: {old_svg.name}")
                old_svg.unlink()

    if new_content != content:
        if dry_run:
            print("   [+] (dry-run) would update file")
        else:
            md_path.write_text(new_content, encoding="utf-8")
            print("   [+] file updated")

    note_entry["blocks"] = new_blocks_meta
    if not dry_run:
        save_index(INDEX_PATH, index)

    return failed


def sweep_orphans(dry_run: bool) -> int:
    """Vault-wide: delete cache SVGs whose source is gone or whose key no
    longer matches any block in the corresponding markdown file."""
    if not CACHE_DIR.exists():
        print("(cache dir doesn't exist yet)")
        return 0

    cache_files = list(CACHE_DIR.glob("*.svg"))
    if not cache_files:
        print("(no cache files found)")
        return 0

    md_by_stem: dict[str, Path] = {}
    for root in SCAN_ROOTS:
        for md in root.rglob("*.md"):
            md_by_stem.setdefault(md.stem, md)

    import re as _re

    name_re = _re.compile(r"^(.+)__(\d+)__([0-9a-f]{8,})\.svg$")
    source_keys: dict[str, set[tuple[int, str]]] = {}

    deleted = 0
    for svg in cache_files:
        m = name_re.match(svg.name)
        if not m:
            print(f"   [?] unparseable cache name, leaving: {svg.name}")
            continue
        stem, idx_s, key = m.group(1), int(m.group(2)), m.group(3)

        md = md_by_stem.get(stem)
        if md is None:
            print(f"   [-] no source for {svg.name}")
            if not dry_run:
                svg.unlink()
            deleted += 1
            continue

        if stem not in source_keys:
            blocks = find_blocks(md.read_text(encoding="utf-8"))
            keys: set[tuple[int, str]] = set()
            for i, b in enumerate(blocks, 1):
                adapter = REGISTRY.get(b.language)
                if adapter is None:
                    continue
                ph = preamble_digest(adapter.preamble_text)
                k = compute_key(b.source, b.language, {}, ph)
                keys.add((i, k))
            source_keys[stem] = keys

        if (idx_s, key) not in source_keys[stem]:
            print(f"   [-] stale: {svg.name}")
            if not dry_run:
                svg.unlink()
            deleted += 1

    print(
        f"sweep complete: {deleted} cache file(s) "
        f"{'would be ' if dry_run else ''}removed"
    )

    if not dry_run:
        index = load_index(INDEX_PATH)
        index["lastSweep"] = _utc_now()
        save_index(INDEX_PATH, index)

    return deleted


def find_all_md_with_blocks() -> list[Path]:
    """Return markdown files containing at least one supported codeblock fence.

    When Phase 5-6 add adapters, append their fence tag to ``fence_tags`` so
    ``--all`` walks Markdown for the new language too.
    """
    files: list[Path] = []
    fence_tags = ("tikz", "tikz-paused", "graphviz", "d2")
    for root in SCAN_ROOTS:
        for md in root.rglob("*.md"):
            try:
                text = md.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if any(f"```{tag}" in text for tag in fence_tags):
                files.append(md)
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="render_cache",
        description="Render code-block visualisations to cached SVGs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              %(prog)s kn/math/concepts/mSB3-5_complex.md
              %(prog)s kn/math/concepts/mSB3-5_complex.md --force
              %(prog)s --all
              %(prog)s --sweep
              %(prog)s kn/math/concepts/mSB3-5_complex.md --dry-run
            """
        ),
    )
    parser.add_argument("path", nargs="?", help="Markdown file to process")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Scan all markdown under SCAN_ROOTS for supported blocks",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-render even when the key matches the existing cache",
    )
    parser.add_argument(
        "--sweep",
        action="store_true",
        help="Vault-wide: delete orphaned/stale cache SVGs",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write files or run renderers; just report what would happen",
    )
    args = parser.parse_args(argv)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if args.sweep:
        sweep_orphans(args.dry_run)
        return 0

    if args.all:
        files = find_all_md_with_blocks()
        print(f"Found {len(files)} markdown file(s) with supported blocks.\n")
        any_failed = False
        for f in files:
            failed = process_file(f, force=args.force, dry_run=args.dry_run)
            if failed:
                any_failed = True
        return 1 if any_failed else 0

    if not args.path:
        parser.print_help()
        return 2

    md_path = Path(args.path)
    if not md_path.is_absolute():
        md_path = (Path.cwd() / md_path).resolve()
    return 1 if process_file(md_path, force=args.force, dry_run=args.dry_run) else 0
