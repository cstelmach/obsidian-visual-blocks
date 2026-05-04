# Standalone Verification

Last Updated: 2026-05-04
Version: 1.0

## Environment

- Repository under test:
  `/Volumes/external/temp/obsidian-visual-blocks-extract-20260504-075433/source-filter-work`
- Source vault for dry-runs: `/Users/cs/Obsidian/_`
- Node: `v25.9.0`
- npm: `11.12.1`
- Python: `/opt/homebrew/Caskroom/miniconda/base/bin/python` (`Python 3.11.8`)

The default `python3` on this shell is Homebrew Python 3.14 and does not have
`pytest` installed, so renderer verification uses the same conda Python that
the vault renderer has used successfully.

## Checks

| Check | Command | Result |
|-------|---------|--------|
| Install dependencies | `npm ci` | PASS; 296 packages installed, 1 moderate npm audit item reported |
| Plugin unit tests | `npm test -- --runInBand` | PASS; 102 tests / 7 suites |
| Plugin production build | `npm run build` | PASS |
| Python renderer tests | `/opt/homebrew/Caskroom/miniconda/base/bin/python -m pytest resources/scripts/python_single/tests -q` | PASS; 171 passed, 11 skipped |
| Migration dry-run | `/opt/homebrew/Caskroom/miniconda/base/bin/python resources/scripts/python_single/migrate_to_render_cache.py --dry-run --vault-root /Users/cs/Obsidian/_` | PASS; 0 moves, 0 markdown updates, 0 deletes, 0 missing refs |
| Renderer dry-run against real vault | `VISUAL_BLOCKS_VAULT_ROOT=/Users/cs/Obsidian/_ /opt/homebrew/Caskroom/miniconda/base/bin/python resources/scripts/python_single/render_cache.py kn/math/concepts/_RENDER_TEST_d2.md --dry-run --languages d2` | PASS; 3 D2 cache hits, no writes |
| Deploy dry-run | `scripts/deploy-to-vault.sh --dry-run /Users/cs/Obsidian/_` | PASS; copies runtime/renderer files only; protects cache, data.json, node_modules; no deletes |

The deploy dry-run output was also saved to:

```text
/tmp/visual-blocks-deploy-dry-run-phase6.txt
```

## Obsidian UI Verification

The `obsidian-verify` CLI was not available on PATH in this standalone
extraction environment. The repository still carries the same built plugin
bundle and tests as the vault-verified Visual Blocks implementation, and the
live-vault deploy phase must run a targeted Obsidian verification after the
real deploy is explicitly approved.

## Notes

- No cache SVGs are tracked in this repo.
- `package-lock.json` is tracked for reproducible `npm ci`.
- `VISUAL_BLOCKS_VAULT_ROOT` was verified for standalone renderer use.
- Relative note paths now resolve against the configured vault root, not the
  standalone repo cwd.
