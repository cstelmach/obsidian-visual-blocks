# Visual Blocks Repository Extraction

Last Updated: 2026-05-04
Version: 1.0

## Summary

This repository was extracted from the Obsidian vault at
`/Users/cs/Obsidian/_` to make Visual Blocks a standalone private plugin
project while preserving the relevant filtered development history.

## Source

- Original repository: `/Users/cs/Obsidian/_`
- Original branch: `notes`
- Frozen source commit:
  `d378ccf6d0324c8d366aab3641ef5171daa20167`
- Extraction workspace:
  `/Volumes/external/temp/obsidian-visual-blocks-extract-20260504-075433`
- Extraction date: 2026-05-04

The original vault history was not rewritten. Filtering happened only inside a
disposable clone under `/Volumes/external/temp`.

## Included History

The filtered history keeps the Visual Blocks plugin, Python renderer, renderer
tests, and render-cache project documentation:

- `.obsidian/plugins/obsidian-render-cache/`
- `.obsidian/plugins/visual-blocks/`
- `resources/scripts/python_single/render_cache.py`
- `resources/scripts/python_single/tikz_cache.py`
- `resources/scripts/python_single/migrate_to_render_cache.py`
- `resources/scripts/python_single/render_cache/`
- relevant `resources/scripts/python_single/tests/` renderer tests
- `docs/specs/render-cache/`

The Obsidian plugin paths were rewritten to the repository root, so files such
as `manifest.json`, `main.js`, `styles.css`, `src/`, and `tests/` live at the
top level of this standalone repo.

## Excluded History

Generated and vault-local material was intentionally excluded:

- `.obsidian/plugins/visual-blocks/cache/`
- `.obsidian/plugins/obsidian-render-cache/cache/`
- `.obsidian/plugins/visual-blocks/node_modules/`
- `.obsidian/plugins/visual-blocks/.pytest_cache/`
- Python bytecode and pytest caches
- unrelated vault notes, journals, archive files, and Obsidian metadata

## Commit Map

Filtered commit SHAs differ from the original vault SHAs because
`git-filter-repo` rewrites commit trees and parents.

Use `docs/extraction/commit-map.tsv` to map original commit IDs to extracted
commit IDs. A `0000000000000000000000000000000000000000` value means the
original commit did not contain retained Visual Blocks content after filtering.
