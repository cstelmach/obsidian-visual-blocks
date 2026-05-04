# render_cache Package Guide

**Last Updated:** 2026-05-03
**Version:** 0.2.0 renderer package, Visual Blocks plugin 0.5.0

This package is the canonical renderer for Visual Blocks. It replaces the old
single-purpose `tikz_cache.py` workflow with a multi-language cache pipeline.

Use this entry point:

```bash
python resources/scripts/python_single/render_cache.py <note.md>
```

Run commands from the vault root. Visual Blocks resolves cache paths from the
current working directory by default. For standalone development or fixture
tests, set `VISUAL_BLOCKS_VAULT_ROOT`:

```bash
VISUAL_BLOCKS_VAULT_ROOT=/path/to/vault \
  python resources/scripts/python_single/render_cache.py <note.md>
```

The Obsidian plugin keeps the current deployed behavior: it spawns Python with
cwd set to the vault root and uses the vault-relative script path
`resources/scripts/python_single/render_cache.py`.

`resources/scripts/python_single/tikz_cache.py` is only a compatibility shim.
Do not add new behavior there.

## Responsibilities

`render_cache` owns:

- discovering supported fenced code blocks in markdown
- normalizing source text before hashing
- computing the canonical 16-character SHA-256 cache key
- dispatching each block to the correct renderer adapter
- post-processing raw SVGs for Obsidian/iOS safety
- writing `.obsidian/plugins/visual-blocks/cache/index.json`
- inserting or updating `![[...|visual-blocks]]` markdown refs
- preserving failed render entries with `lastError`
- sweeping stale cache files

The Obsidian plugin at `.obsidian/plugins/visual-blocks/` owns viewing,
settings, commands, status UI, and desktop command spawning. The plugin does
not implement renderer logic.

## Architecture

```text
render_cache.py
  -> render_cache.main()
     -> markdown_io.find_blocks()
     -> adapters.REGISTRY[language]
     -> hash.compute_key()
     -> adapter.render()
     -> postprocess.apply()
     -> cache_paths.cache_path_for_note()
     -> index.save_index()
     -> markdown_io.find_existing_ref()
```

Key modules:

| Module | Purpose |
|--------|---------|
| `__init__.py` | CLI dispatcher, file processing, `--all`, `--sweep` |
| `normalize.py` | Canonical source normalization before hashing |
| `hash.py` | SPEC cache-key formula and preamble digest |
| `markdown_io.py` | Supported fence extraction and cache-ref matching |
| `cache_paths.py` | Plugin-managed cache layout helpers |
| `index.py` | Atomic `index.json` read/write helpers |
| `postprocess.py` | SVG hardening rules |
| `adapters/base.py` | `RendererAdapter` contract and `RenderError` |
| `adapters/*.py` | Concrete language renderers |

## Supported Fences

| Fence | Canonical language | Adapter |
|-------|--------------------|---------|
| `tikz` | `tikz` | `TikzAdapter` |
| `tikz-paused` | `tikz` | `TikzAdapter` |
| `graphviz` | `graphviz` | `GraphvizAdapter` |
| `d2` | `d2` | `D2Adapter` |
| `lilypond` | `lilypond` | `LilyPondAdapter` |
| `smiles` | `smiles` | `SMILESAdapter` |

`tikz-paused` canonicalizes to `tikz`, so pausing/unpausing a block does not
change the cache key.

## Dispatcher Rules

For each supported block, `process_file()`:

1. Looks up the adapter by canonical language.
2. Computes `preamble_hash = preamble_digest(adapter.preamble_text)`.
3. Computes `key = compute_key(source, language, attrs, preamble_hash)`.
4. Resolves the target path under `.obsidian/plugins/visual-blocks/cache/v1/`.
5. Renders when `--force` is set or the target SVG does not exist.
6. Applies SVG post-processing before writing the cache file.
7. Records block metadata in `index.json`.
8. Inserts or rewrites the following markdown ref:

```markdown
![[.obsidian/plugins/visual-blocks/cache/v1/.../<idx>__<hash>.svg|visual-blocks]]
```

If a renderer raises `RenderError`, the dispatcher records a block entry with
`lastError` and does not insert a successful image ref for that failed render.
The plugin uses that metadata to show an inline error block.

## Adapter Contract

Every renderer adapter subclasses `RendererAdapter`:

```python
class RendererAdapter(ABC):
    @property
    @abstractmethod
    def language(self) -> str: ...

    @property
    @abstractmethod
    def render_budget_seconds(self) -> int: ...

    @abstractmethod
    def render(
        self,
        source: str,
        attrs: dict[str, Any],
        workdir: Path,
    ) -> Path: ...

    @property
    def preamble_text(self) -> str:
        return ""
```

Adapter rules:

- Return the path to one SVG file inside `workdir`.
- Raise `RenderError` with a useful stderr/log snippet on failure.
- Keep side effects inside `workdir`; the dispatcher moves content into cache.
- Use `render_budget_seconds` as the subprocess timeout for shell renderers.
- Keep `preamble_text` stable because it participates in cache invalidation.

Current renderers:

- `TikzAdapter`: LuaLaTeX plus dvisvgm with Ghostscript libgs discovery.
- `GraphvizAdapter`: Graphviz `dot -Tsvg`.
- `D2Adapter`: D2 CLI with explicit ELK/layout/theme flags.
- `LilyPondAdapter`: LilyPond SVG backend with point-and-click disabled.
- `SMILESAdapter`: RDKit molecule drawing, no external subprocess.

## SVG Post-Processing

`postprocess.apply(svg_text, key)` runs three hardening rules:

1. `prefix_ids`
   - Prefixes SVG IDs and internal `href` references with the cache key prefix.
   - Prevents two diagrams on one Obsidian page from sharing IDs like `node1`.

2. `substitute_current_color`
   - Replaces hardcoded black fill/stroke values with `currentColor`.
   - Handles both attribute form and CSS-style `style="stroke:#000000"`.
   - Preserves white, `none`, and user-selected colors.

3. `enforce_viewbox`
   - Strips `pt` units from `width` and `height`.
   - Injects a `viewBox` if one is missing.
   - Prevents iOS WebKit zero-size SVG behavior.

Regexes are quote-agnostic because different renderers emit different quote
styles.

## Cache Layout

Canonical Phase 12+ paths are defined in `cache_paths.py`:

```text
.obsidian/plugins/visual-blocks/cache/
|-- index.json
`-- v1/
    `-- <vault-relative-note-path-without-.md>/
        `-- <zero-based-block-index>__<16-char-source-hash>.svg
```

The old `attachments/cache/tikz/` constants remain only for migration,
rollback, and debugging helpers.

## Commands

Render one note:

```bash
python resources/scripts/python_single/render_cache.py kn/math/concepts/example.md
```

Force-render one note:

```bash
python resources/scripts/python_single/render_cache.py kn/math/concepts/example.md --force
```

Render all supported blocks under `SCAN_ROOTS`:

```bash
python resources/scripts/python_single/render_cache.py --all
```

Limit a run to selected canonical language IDs:

```bash
python resources/scripts/python_single/render_cache.py --all --languages tikz,d2,smiles
```

The Visual Blocks plugin uses this filter for per-library settings. Direct CLI
runs without `--languages` still process all supported languages.

Sweep stale cache files:

```bash
python resources/scripts/python_single/render_cache.py --sweep
```

Dry-run where supported:

```bash
python resources/scripts/python_single/render_cache.py kn/math/concepts/example.md --dry-run
```

Before a bulk `--all --force` or migration-style operation, confirm scope with
the user. This vault has explicit safety rules for bulk markdown/cache changes.

## Adding A Language

Do the smallest complete slice:

1. Add `render_cache/adapters/<language>.py`.
2. Register it in `render_cache/adapters/__init__.py`.
3. Add the canonical language and fence aliases to `render_cache/languages.py`.
4. Add tests for adapter contract, markdown discovery, render success, render
   failure, and `--languages` filtering where relevant.
4. Add the fence to the plugin language list in
   `.obsidian/plugins/visual-blocks/src/main.ts`.
5. Add tests for adapter contract, markdown discovery, render success, render
   failure, and cache-index metadata.
6. Add or update Visual Blocks plugin hash fixtures if the language affects the
   cross-language key contract.
7. Run Python tests, plugin tests, and plugin build.

The fence list is currently duplicated between Python and TypeScript. Do not
hide that with an ad-hoc dynamic import; make a deliberate shared-contract
change if you remove the duplication.

## Tests

Preferred Python interpreter on this machine:

```bash
/opt/homebrew/Caskroom/miniconda/base/bin/python
```

Run the full Python renderer suite:

```bash
/opt/homebrew/Caskroom/miniconda/base/bin/python -m pytest \
  resources/scripts/python_single/tests -q
```

Run plugin tests and build:

```bash
cd .obsidian/plugins/visual-blocks
npm test -- --runInBand
npm run build
```

After plugin UI changes, use the Obsidian verification harness or canary from
`resources/tests/harness`.

## Known Limitations

- `SCAN_ROOTS` currently scans `kn/` only.
- The TypeScript plugin and Python package both maintain supported-language
  lists.
- Mobile is cache-only. It cannot spawn Python.
- Live mode re-renders in the background and may require a note reload to show
  the newest cache.
- Dark-mode adaptation through `currentColor` is limited by the current `<img>`
  embedding path; inline SVG would be a separate design change.
