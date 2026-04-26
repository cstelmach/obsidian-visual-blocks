#!/usr/bin/env python3
"""
tikz_cache.py — Render Obsidian TikZ blocks to cached PNGs.

Solves the mobile-rendering crash and reduces desktop reflow by pre-rendering
every ``` ```tikz ``` and ``` ```tikz-paused ``` block to a PNG file. Inserts a
companion `![[…|tikz-cache]]` image reference after each block; CSS toggles
which one is shown based on platform (see .obsidian/snippets/tikz-cache.css).

Hash-based invalidation: filename embeds an 8-char SHA256 of the TikZ source.
When the source changes, a new PNG is rendered and the reference is rewritten;
the old PNG is removed.

Render engine: lualatex → pdftoppm. Both must be on PATH.

Usage:
    tikz_cache.py FILE.md            # cache one file
    tikz_cache.py FILE.md --force    # re-render even if hash unchanged
    tikz_cache.py --all              # scan vault under SCAN_ROOTS
    tikz_cache.py --sweep            # remove orphaned cache images vault-wide
    tikz_cache.py FILE.md --dry-run  # show what would change

Exit codes: 0 success, 1 partial failures, 2 fatal error.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration

VAULT_ROOT = Path("/Users/cs/Obsidian/_")
CACHE_DIR = VAULT_ROOT / "attachments" / "tikz-cache"
SCAN_ROOTS = [VAULT_ROOT / "kn"]
DPI = 300
LUALATEX_TIMEOUT_S = 90
PDFTOPPM_TIMEOUT_S = 30

LATEX_PREAMBLE = textwrap.dedent(r"""
    \documentclass[border=4pt]{standalone}
    \usepackage{pgfplots}
    \pgfplotsset{compat=1.16}
    \usetikzlibrary{
        arrows.meta, positioning, decorations.pathreplacing,
        decorations.markings, calc, shapes, patterns,
        intersections, fit, backgrounds
    }
    \usepackage{amsmath, amssymb}
    \begin{document}
""").lstrip()

LATEX_POSTAMBLE = "\n\\end{document}\n"

# Match a fenced TikZ block (active or paused). Capture: (1) full fence open,
# (2) variant suffix ('' or '-paused'), (3) inner code.
TIKZ_BLOCK_RE = re.compile(
    r"^(```tikz(-paused)?)\n(.*?)\n```",
    re.DOTALL | re.MULTILINE,
)

# Match an immediately-following `![[FILENAME|tikz-cache]]` reference. The
# leading whitespace (\n+) is captured so we can replace cleanly.
CACHE_REF_RE = re.compile(
    r"\n+!\[\[([^\]|\n]+\.png)\|tikz-cache\]\]"
)


# ---------------------------------------------------------------------------
# Data

@dataclass
class BlockResult:
    index: int          # 1-based position in the file
    hash8: str          # 8-char source hash
    png_name: str       # basename of cached PNG
    rendered: bool      # True if we just rendered it (cache miss or force)
    ok: bool            # True if PNG exists at the end
    error: str | None = None


# ---------------------------------------------------------------------------
# Helpers

def hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:8]


def extract_tikz_body(block: str) -> str:
    """
    Strip wrappers TikZJax tolerates but `standalone` doesn't.

    - Drop any ``\\usepackage{tikz}`` (auto-loaded by both).
    - Drop the inner ``\\begin{document}`` / ``\\end{document}`` (the standalone
      template provides its own).
    - Keep ``\\usetikzlibrary{...}`` lines intact (the preamble already loads
      common ones, but extra ones are harmless).
    - Keep ``\\begin{tikzpicture} ... \\end{tikzpicture}`` exactly.
    """
    body = block

    # Drop \usepackage{tikz} (any whitespace variation)
    body = re.sub(r"\\usepackage\s*\{\s*tikz\s*\}\s*", "", body)

    # Strip \begin{document} ... \end{document} wrapper if present
    m = re.search(r"\\begin\{document\}(.*?)\\end\{document\}", body, re.DOTALL)
    if m:
        body = m.group(1)

    return body.strip() + "\n"


def render_tikz(block: str, output_png: Path, work_dir: Path) -> tuple[bool, str | None]:
    """
    Render one TikZ block to PNG. Returns (ok, error_message).
    """
    work_dir.mkdir(parents=True, exist_ok=True)
    body = extract_tikz_body(block)
    full_tex = LATEX_PREAMBLE + body + LATEX_POSTAMBLE

    tex_path = work_dir / "tikz.tex"
    pdf_path = work_dir / "tikz.pdf"
    tex_path.write_text(full_tex, encoding="utf-8")

    # 1. Compile to PDF
    try:
        result = subprocess.run(
            ["lualatex", "-interaction=nonstopmode", "-halt-on-error", "tikz.tex"],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=LUALATEX_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        return False, "lualatex timeout"
    except FileNotFoundError:
        return False, "lualatex not found on PATH"

    if not pdf_path.exists():
        # Bubble up the most relevant LaTeX error line for diagnostics
        log_path = work_dir / "tikz.log"
        snippet = ""
        if log_path.exists():
            log = log_path.read_text(errors="replace")
            err_lines = [ln for ln in log.splitlines() if ln.startswith("!")]
            snippet = " | ".join(err_lines[:3]) or log.splitlines()[-1] if log.splitlines() else ""
        return False, f"lualatex failed: {snippet[:200]}"

    # 2. Convert PDF → PNG @ DPI (standalone class already crops to content)
    out_stem = output_png.with_suffix("")
    try:
        result = subprocess.run(
            ["pdftoppm", "-r", str(DPI), "-png", "-singlefile",
             str(pdf_path), str(out_stem)],
            capture_output=True, text=True, timeout=PDFTOPPM_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        return False, "pdftoppm timeout"
    except FileNotFoundError:
        return False, "pdftoppm not found on PATH"

    if result.returncode != 0 or not output_png.exists():
        return False, f"pdftoppm failed: {result.stderr.strip()[:200]}"

    return True, None


def find_blocks(content: str) -> list[re.Match]:
    """Return a list of TIKZ_BLOCK_RE matches in document order."""
    return list(TIKZ_BLOCK_RE.finditer(content))


def find_existing_ref(content: str, after_pos: int) -> tuple[re.Match | None, int, int]:
    """
    Find a `![[…|tikz-cache]]` reference that immediately follows `after_pos`
    (allowing only blank lines between). Returns (match, abs_start, abs_end)
    where positions are absolute in `content`. (None, -1, -1) if not present.
    """
    tail = content[after_pos:after_pos + 400]
    m = CACHE_REF_RE.match(tail)
    if not m:
        return None, -1, -1
    return m, after_pos + m.start(), after_pos + m.end()


# ---------------------------------------------------------------------------
# Per-file processing

def process_file(md_path: Path, force: bool, dry_run: bool) -> list[BlockResult]:
    if not md_path.exists():
        print(f"[!] not found: {md_path}", file=sys.stderr)
        return []

    content = md_path.read_text(encoding="utf-8")
    blocks = find_blocks(content)
    if not blocks:
        return []

    rel = md_path.relative_to(VAULT_ROOT) if VAULT_ROOT in md_path.parents else md_path
    print(f"=> {rel}: {len(blocks)} TikZ block(s)")

    results: list[BlockResult] = []
    in_use_filenames: set[str] = set()
    edits: list[tuple[int, int, str]] = []  # (start, end, replacement)

    for idx, m in enumerate(blocks, 1):
        inner = m.group(3)
        h = hash_content(inner)
        png_name = f"{md_path.stem}__{idx}__{h}.png"
        png_path = CACHE_DIR / png_name
        in_use_filenames.add(png_name)

        rendered = False
        ok = True
        err = None
        if force or not png_path.exists():
            print(f"   [{idx}] hash={h} → render")
            if dry_run:
                print(f"        (dry-run) would render to {png_path}")
                ok = png_path.exists()  # treat as ok if existing
            else:
                work_dir = CACHE_DIR / f"_work_{md_path.stem}_{idx}"
                ok, err = render_tikz(inner, png_path, work_dir)
                shutil.rmtree(work_dir, ignore_errors=True)
                rendered = ok
                if not ok:
                    print(f"        FAILED: {err}")
        else:
            print(f"   [{idx}] hash={h} → cache hit")

        results.append(BlockResult(idx, h, png_name, rendered, ok, err))

        if not ok:
            continue  # leave reference alone if we have no fresh PNG

        # Plan the reference edit
        block_end = m.end()
        new_ref = f"\n\n![[{png_name}|tikz-cache]]"
        existing, ref_start, ref_end = find_existing_ref(content, block_end)
        if existing is None:
            edits.append((block_end, block_end, new_ref))
        else:
            existing_filename = existing.group(1)
            if existing_filename == png_name:
                continue  # already current
            edits.append((ref_start, ref_end, new_ref))

    # Apply edits in reverse so positions stay valid
    new_content = content
    for start, end, replacement in sorted(edits, key=lambda e: -e[0]):
        new_content = new_content[:start] + replacement + new_content[end:]

    # Cleanup: orphaned cache files for this note (different hash, same stem+idx slot)
    if not dry_run:
        for old_png in CACHE_DIR.glob(f"{md_path.stem}__*.png"):
            if old_png.name not in in_use_filenames:
                print(f"   [-] orphan: {old_png.name}")
                old_png.unlink()

    if new_content != content:
        if dry_run:
            print("   [+] (dry-run) would update file")
        else:
            md_path.write_text(new_content, encoding="utf-8")
            print("   [+] file updated")

    return results


def sweep_orphans(dry_run: bool) -> int:
    """
    Vault-wide: delete cache PNGs whose `<stem>` no longer corresponds to a
    markdown file containing tikz, OR whose `<hash>` no longer matches any
    block in the corresponding markdown file.
    """
    if not CACHE_DIR.exists():
        print("(cache dir doesn't exist yet)")
        return 0

    # Index every cache file by (stem, idx, hash)
    cache_files = list(CACHE_DIR.glob("*.png"))
    if not cache_files:
        print("(no cache files found)")
        return 0

    # Build a map: stem → set of (idx, hash) currently referenced in source
    source_hashes: dict[str, set[tuple[int, str]]] = {}
    md_by_stem: dict[str, Path] = {}
    for root in SCAN_ROOTS:
        for md in root.rglob("*.md"):
            md_by_stem.setdefault(md.stem, md)

    deleted = 0
    for png in cache_files:
        # Parse "<stem>__<idx>__<hash8>.png"
        m = re.match(r"^(.+)__(\d+)__([0-9a-f]{8})\.png$", png.name)
        if not m:
            print(f"   [?] unparseable cache name, leaving: {png.name}")
            continue
        stem, idx_s, h = m.group(1), int(m.group(2)), m.group(3)

        md = md_by_stem.get(stem)
        if md is None:
            print(f"   [-] no source for {png.name}")
            if not dry_run:
                png.unlink()
            deleted += 1
            continue

        # Lazy-cache: compute hashes per source file once
        if stem not in source_hashes:
            content = md.read_text(encoding="utf-8")
            blocks = find_blocks(content)
            source_hashes[stem] = {
                (i, hash_content(b.group(3))) for i, b in enumerate(blocks, 1)
            }

        if (idx_s, h) not in source_hashes[stem]:
            print(f"   [-] stale: {png.name}")
            if not dry_run:
                png.unlink()
            deleted += 1

    print(f"sweep complete: {deleted} cache file(s) {'would be ' if dry_run else ''}removed")
    return deleted


def find_all_md_with_tikz() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        for md in root.rglob("*.md"):
            try:
                if "```tikz" in md.read_text(encoding="utf-8"):
                    files.append(md)
            except (UnicodeDecodeError, OSError):
                continue
    return files


# ---------------------------------------------------------------------------
# CLI

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render Obsidian TikZ blocks to cached PNGs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              %(prog)s kn/math/concepts/mSB3-5_complex.md
              %(prog)s kn/math/concepts/mSB3-5_complex.md --force
              %(prog)s --all
              %(prog)s --sweep
              %(prog)s kn/math/concepts/mSB3-5_complex.md --dry-run
        """),
    )
    parser.add_argument("path", nargs="?", help="Markdown file to process")
    parser.add_argument("--all", action="store_true",
                        help="Scan all markdown under SCAN_ROOTS for TikZ blocks")
    parser.add_argument("--force", action="store_true",
                        help="Re-render even when the hash matches the existing cache")
    parser.add_argument("--sweep", action="store_true",
                        help="Vault-wide: delete orphaned/stale cache PNGs")
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't write files or run lualatex; just report what would happen")
    args = parser.parse_args()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    if args.sweep:
        sweep_orphans(args.dry_run)
        return 0

    if args.all:
        files = find_all_md_with_tikz()
        print(f"Found {len(files)} markdown file(s) with TikZ blocks.\n")
        any_failed = False
        for f in files:
            results = process_file(f, force=args.force, dry_run=args.dry_run)
            if any(not r.ok for r in results):
                any_failed = True
        return 1 if any_failed else 0

    if not args.path:
        parser.print_help()
        return 2

    md_path = Path(args.path)
    if not md_path.is_absolute():
        md_path = (Path.cwd() / md_path).resolve()
    results = process_file(md_path, force=args.force, dry_run=args.dry_run)
    return 1 if any(not r.ok for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
