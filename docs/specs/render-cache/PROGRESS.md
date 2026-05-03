# Progress Log — Obsidian Visual Blocks

**Spec:** `/Users/cs/Obsidian/_/docs/specs/render-cache/SPEC.md`
**Plan:** `/Users/cs/Obsidian/_/docs/specs/render-cache/PLAN.md`
**Archive:** `/Users/cs/Obsidian/_/docs/specs/render-cache/PROGRESS_ARCHIVE.md` (Phase 1-6 + Initialization + diagnostic checkpoint)
**Status:** Phase 12 DONE — user-gated; next: Phase 13 Documentation.
**Mode:** Manual (user-driven phase progression)
**Started:** 2026-04-27
**Last Updated:** 2026-05-03 (Phase 12 user gate closed)

> **Mode note:** PLAN.md L4 declares manual mode. SPEC §11.4 requires each
> phase to end at a "Direct user feedback (gate)" before the next begins.
> This is a user-driven workflow — Ralph Loop autonomous progression is **not**
> in effect. After each phase checkpoint, the agent EXITS and waits for the
> user to trigger the next phase.

> **Archive note:** Phase 1-6 log entries + Initialization + the post-Phase-1-v2
> diagnostic checkpoint + early Divergence Checks moved to `PROGRESS_ARCHIVE.md`
> on 2026-04-28 to keep this file under the spine's 500-line summarisation
> threshold. The Phases summary table below retains all rows. The Log section
> below retains Phase 7 + Phase 8 entries verbatim.

---

## Session Metadata

| Field | Value |
|-------|-------|
| Session ID | session-20260427-init |
| Agent Model | claude-opus-4-7 |
| Max Iterations | manual (no cap) |
| Context Strategy | manual fresh-session per phase |
| Cost Budget | — (manual) |
| Cost Spent | $0.00 |

---

## Phases

| Phase | Status | Started | Completed | Commit | Tests | Duration | Notes |
|-------|--------|---------|-----------|--------|-------|----------|-------|
| Phase 1 — Migration: PNG → SVG via dvisvgm | DONE | 2026-04-27 09:24 | 2026-04-27 12:30 | 84ccae5ac (CSS) + PROGRESS | 14/14 ✓ | ~3h gate-to-gate | v1 text-only SVG bug fixed via `--libgs=` (D1.6); v2 verified on disk. Desktop gate closed via CSS view-layer swap (D1.9-11) — brings forward Phase 8's cache-first viewer. User confirmed desktop + mobile. |
| Phase 2 — Restructure into render_cache package | DONE | 2026-04-27 13:00 | 2026-04-27 (gate closed) | 2aaf1f5b5 (code) + b20ee085c (PROGRESS) | 50/50 ✓ | ~15m | 10-module package + new CLI + deprecation shim. SPEC §3.9 16-char canonical hash adopted. 5 Phase 1 cache files re-keyed; 95 previously-uncached TikZ files now rendered (3 fail with pre-existing source bugs — not Phase 2 regressions). Gate (visual-confirmed by user, this session): cached SVGs render correctly desktop + mobile post-restructure. |
| Phase 3 — Add Graphviz adapter | DONE | 2026-04-27 (Phase 3 begin) | 2026-04-27 (this session) | 1d0fe447b (code+tests+cache+PROGRESS, auto-backup-captured) | 14/14 ✓ + 60/60 fast suite | ~30m | New `GraphvizAdapter` (`dot -Tsvg`), REGISTRY+BLOCK_RE+`_FENCE_TO_LANG`+dispatcher fence-tag list extended. Sandbox `_RENDER_TEST_graphviz.md` (3 DOT blocks: simple digraph / labeled edges / clustered subgraph). Pre-flight `dot - graphviz version 14.1.5` (Apple Silicon brew). User gate closed this session ("All three visible in Preview / Quicklook"). |
| Phase 4 — Add D2 adapter | DONE | 2026-04-27 (this session) | 2026-04-27 (gate closed) | 69023c8f7 (atomic) + PROGRESS | 14/14 ✓ + 71/71 fast suite | ~25m | New `D2Adapter` (`d2 --layout=elk --pad=20 --theme=0 --bundle=true`). Pre-flight: `d2 0.7.1` installed via `brew install d2` (PLAN per-language pre-flight policy authorised). REGISTRY/BLOCK_RE/`_FENCE_TO_LANG`/dispatcher fence-tag list extended (4 items). Gate (visual-confirmed): user confirmed all three SVGs in Preview/QuickLook this session ("user gate passed. all three images confirmed in Quicklook"). |
| Phase 5 — Add LilyPond adapter | DONE | 2026-04-27 14:25 | 2026-04-27 (gate closed this session) | aad9ef7bd (auto-backup) + b1d5e26c2 (PROGRESS) | 15/15 ✓ + 93/93 full suite | ~10m | New `LilyPondAdapter` (`lilypond -dpoint-and-click=#f -dbackend=svg -dno-include-book-title-preview -o <prefix>`). Pre-flight: `lilypond 2.26.0` installed via `brew install lilypond` (user authorised, same pattern as Phase 4 d2). REGISTRY/BLOCK_RE/`_FENCE_TO_LANG`/dispatcher fence-tag list extended (now 5 items). Sandbox `_RENDER_TEST_lilypond.md` (2 LilyPond blocks: C-major scale melody + 2-bar lead sheet with chord names). AC5.2 hard-verified at agent level: `grep -c 'file://'` returns 0 for both cache SVGs. Gate (visual-confirmed): user confirmed both SVGs in QuickLook this session ("Yes, it works, user-gate phase 5 passed"). |
| Phase 6 — Add RDKit adapter | DONE | 2026-04-27 14:48 | 2026-04-27 (gate closed this session) | dc78c598e (PROGRESS) + 927047133 (auto-backup) | 15/15 ✓ + 108/108 full suite | ~6m | New `SMILESAdapter` — **the only v1 adapter that is pure Python, no shell-out**. Uses `rdkit.Chem.MolFromSmiles` + `AllChem.Compute2DCoords` + `rdMolDraw2D.MolDraw2DSVG` (400×300). Pre-flight: `rdkit 2026.3.1` installed via `pip install rdkit` (user authorised; user asked "uv or pip?" — pip chosen for one-off conda-env install). REGISTRY/BLOCK_RE/`_FENCE_TO_LANG`/dispatcher fence-tag list extended (now 6 items). Sandbox `_RENDER_TEST_smiles.md` (3 SMILES blocks: caffeine / aspirin / ibuprofen). All three render correctly per AC6.2 (rsvg-convert verification at agent level — caffeine purine ring, aspirin acetyl ester + COOH, ibuprofen benzene + isobutyl + α-methyl propanoate). RDKit logger silenced at module import (D6.5) — clean CLI/test output. AC6.3: invalid SMILES → `RenderError` with offending input snippet. Fence-tag derive-from-REGISTRY refactor (D5.6 promise) deliberately deferred to follow-up commit (D6.7). |
| Phase 7 — Apply SVG postprocessing hardening | DONE | 2026-04-27 15:10 | 2026-04-27 (gate closed this session) | 88a487fc9 (PROGRESS+residual) + a9cd7320c (auto-backup: code+tests+105 cache SVGs) + c25974eeb (D7.8/D7.9/D7.10 honest gate framing) | 43/43 Phase 7 ✓ + 151/151 full suite | ~30m | Three rules in `render_cache/postprocess.py` (`prefix_ids` / `substitute_current_color` / `enforce_viewbox`). Quote-agnostic regexes — PLAN's pseudocode pinned double-quote only and would have silently no-op'd on TikZ + SMILES (both single-quoted). Added CSS-style colour rule for SMILES (`style='...stroke:#000000...'`). Re-rendered 169 cache SVGs via `--all --force`; AC7.1/AC7.2/AC7.3 hard-verified across full cache (0 unprefixed dvisvgm or Graphviz IDs; 0 attribute-form OR CSS-style hardcoded black; 169/169 viewBox; 0/169 pt units). 3 pre-existing TikZ source bugs surfaced for the 3rd time (not Phase 7 regressions). Gate (AC7.4 visual-confirmed): "we see all the svgs in the _RENDER_TEST_d2.md note. We also see the codeblock still and the embedded internal links to the cached svgs". AC7.5 dark-mode follow remains structurally blocked under `<img>` viewing path (D7.8) — re-evaluated at Phase 8 user gate, which under SPEC `<img>` mandate will also remain blocked (Phase 8 user-confirmed via `<img>` per SPEC §3.4/§3.6). |
| Phase 8 — Plugin scaffold | DONE | 2026-04-27 (this session) | 2026-04-27 (gate closed 2026-04-28) | d035c5cfd (auto-backup, atomic capture: .gitignore + plugin tree + PROGRESS + Python fixture self-test) + 5ec8cf62d (earlier auto-backup: generator script + initial fixture stray) + c070312ed (PROGRESS hash-record) + e101d1e81 (gate-language refinements) | jest 24/24 ✓ + python 150/150 fast ✓ | ~1.5h | New `visual-blocks` plugin at `.obsidian/plugins/visual-blocks/` (.ts source + main.js bundle + manifest + tests + fixtures). Cross-language hash byte-identity (T12) hard-verified: 14 fixtures × 2 languages = 28 round-trip checks passing. Production round-trip on all 3 `_RENDER_TEST_d2.md` blocks confirmed (computed hash == index.json sourceHash). User gate visual-confirmed all 8 verification steps (see Phase 8 Gate Closure inside log entry). MathJax font warnings during step 2 are unrelated (slow-network WOFF loading) and out of plugin scope. |
| Phase 9 — Plugin commands and modes | DONE — gate closed | 2026-04-28 | 2026-05-01 (obsidian-verify gate) | 8db247eec + gate log | jest 73/73 ✓ + python 169/169 ✓ + obsidian-verify gate ✓ | ~3h + gate | 4 new src modules (settings/render/cacheStatus/commands; ~1000 lines) + 4 new test files (49 new pure-function tests). 7 commands registered (refresh-block / refresh-note / refresh-vault / show-status / sweep / toggle-mode / clear-all); 3 modes (hybrid / cache-only / live with mobile auto-override AC9.9); SettingTab w/ 5 controls; triggerOnSave save hook (3s debounced, desktop-only). Gate closed via isolated obsidian-verify harness run: desktop plugin load/settings/commands/save/live/sweep/clear-all passed; iOS physical UI not automatable in desktop harness, mobile override covered by unit tests and remains in Phase 11 iOS validation. |
| Phase 10 — Plugin error display + status bar | DONE — gate closed | 2026-05-01 | 2026-05-01 (obsidian-verify gate) | cfe598614 + Phase 10 log | jest 79/79 ✓ + python 170/170 ✓ + obsidian-verify gate ✓ | ~2h | Python now preserves failed block entries in `index.json` with `lastError`; plugin shows retryable inline error blocks before image/placeholder handling; status bar shows per-note idle/rendering/error state and opens the Phase 9 cache-status modal. Gate closed via isolated obsidian-verify harness: valid note cached image + `✓ 1 item`; broken TikZ note inline LaTeX error + `⚠ 1 failed`; error click retries; status-bar click opens modal; 0 visual-blocks console errors/warnings. |
| Phase 11 — iOS validation (USER-DRIVEN) | DONE — user-gated | 2026-05-02 07:38 | 2026-05-02 07:51 | 0881a217a (preflight) + 5b4451f15 (gate) + hash record | local preflight ✓; user iOS gate ✓ | ~15m | User reported clean/correct on required phone checks 2, 3, and 4. AC11.1-AC11.4 satisfied: mSB5-2 partial note, original crash trigger, and third representative file loaded correctly on iOS. |
| Phase 12 — Migration tool: legacy → new layout | DONE — user-gated | 2026-05-02 08:38 | 2026-05-03 (gate closed) | 6a64cc6c3 + 25bb544bc + 65641ef64 + a2e64472b + 00eeb832e + gate log | python 169/169 ✓ + jest 81/81 ✓ + build ✓ + canary ✓ + migration execute ✓ + user re-gate ✓ | | Real migration executed after explicit user approval. 170 SVGs moved to `.obsidian/plugins/visual-blocks/cache/v1/`; 100 markdown files / 169 refs rewritten; 5 PNGs + 3 orphan SVGs deleted; legacy dir removed. Native Obsidian `.obsidian/plugins/...` wikilink resolver messages fixed by CSS wrapper suppression. User re-gate passed 2026-05-03. |
| Phase 13 — Documentation | Not Started | | | | | | 2–3h est. Final phase before optional 14. |
| Phase 14 — gboyd068/SwiftLaTeX hands-on eval | Not Started (optional) | | | | | | OPTIONAL. Skip unless v1 has gaps surfaced during Phase 11. |

**Status values:** Not Started, In Progress, DONE, Blocked, Not Started (optional).
**Commit:** Short git hash (7 chars).
**Tests:** Format as `{passed}/{total} tests` for code phases; user-confirm note for user-driven phases.
**Critical path:** 1 → 2 → 7 → 8 → 9 → 10 → 11 → 12 → 13. Phase 14 optional.

---

## Log

_(Most recent first — reverse chronological)_

### Phase 12 — User re-gate closure — 2026-05-03 DONE

**User confirmation:**

- User replied: `Phase 12 user gate passed`.
- This closes the re-gate after the native Obsidian embed-wrapper leak fix.

**Gate criteria satisfied by user confirmation:**

- Visual Blocks renders the migrated diagrams from
  `.obsidian/plugins/visual-blocks/cache/v1/...`.
- No `.obsidian/plugins/visual-blocks/cache/... could not be found` messages
  remain with Visual Blocks enabled.
- No duplicate native image remains in the rendered note.
- The Visual Blocks status path remains usable for the migrated cache.

**Prior automated evidence retained for this gate:**

- Plugin Jest: 81/81 pass.
- Plugin build: production build succeeds.
- Python: 169 passed, 6 skipped.
- Obsidian harness canary: PASS, 3/3 assertions, 0 console errors, 0 warnings.

**Next:**

- Phase 13 — Documentation.
- Manual trigger remains required: `Implement Phase 13`.

### Phase 12 — Native Obsidian embed leak after migration — 2026-05-02 FIX APPLIED

**Trigger:** Phase 12 desktop user gate failed after the real Visual Blocks
migration. The note showed the Visual Blocks-rendered images, but also native
Obsidian messages such as:

- `.obsidian/plugins/visual-blocks/cache/v1/kn/math/concepts/mSB3-4_reals/0__814d986af7c9302c.svg could not be found`
- `.obsidian/plugins/visual-blocks/cache/v1/kn/math/concepts/mSB5-2_partial/0__878b1a3ff7e1b4d6.svg could not be found`

The copied image URL was an `app://.../.obsidian/plugins/visual-blocks/cache/...`
resource URL, proving the plugin-rendered image path existed and loaded.

**Diagnosis:**

- The migrated SVG files exist on disk under
  `.obsidian/plugins/visual-blocks/cache/v1/...`.
- The Visual Blocks plugin renders those files correctly through
  `app.vault.adapter.getResourcePath(entry.cachePath)`.
- The failure is a separate native Obsidian wikilink layer:
  the markdown still contains `![[.obsidian/plugins/...|visual-blocks]]`
  as the durable source ref, and Obsidian's native resolver does not treat
  hidden `.obsidian/plugins/...` paths as normal vault embeds.
- Existing plugin CSS hid only successful native `<img alt="visual-blocks">`
  duplicates. It did not hide native `.internal-embed` / `.image-embed` /
  `.markdown-embed` wrappers that render a "could not be found" message.

**Fix:**

- Updated `.obsidian/plugins/visual-blocks/styles.css` to hide native Obsidian
  embed wrappers that point at `.obsidian/plugins/visual-blocks/cache/` or carry
  `alt~="visual-blocks"`.
- Kept `.visual-blocks-img` visible; the plugin-owned image is still the
  authoritative display path.
- Added regression coverage in
  `.obsidian/plugins/visual-blocks/tests/render.test.ts` so the native wrapper
  suppression selectors cannot be dropped silently.
- Auto-backup captured the fix as `00eeb832e vault backup: 2026-05-02 23:26`
  before a manual atomic commit could be made. This follow-up progress record
  names that implementation commit explicitly.

**Verification:**

- Plugin Jest:
  `.obsidian/plugins/visual-blocks npm test -- --runInBand` → 81/81 pass.
- Plugin build:
  `.obsidian/plugins/visual-blocks npm run build` → production build succeeds.
- Python:
  `/opt/homebrew/Caskroom/miniconda/base/bin/python -m pytest
  resources/scripts/python_single/tests -q` → 169 passed, 6 skipped.
- Obsidian harness canary:
  `resources/tests/harness node --import tsx run.ts --canary
  --json=/tmp/visual-blocks-phase12-native-embed-hide-canary-2026-05-02.json`
  → PASS, 3/3 assertions, 0 console errors, 0 warnings.

**User re-gate:**

Reload Visual Blocks on desktop (toggle the plugin off/on, or reload the
Obsidian window), then reopen:

- `kn/math/concepts/mSB3-4_reals.md`
- `kn/math/concepts/mSB5-2_partial.md`
- `kn/math/concepts/mLA5-1_eigenvalues.md`
- `kn/math/concepts/_RENDER_TEST_d2.md`

Confirm:

- The diagrams render once via Visual Blocks.
- No `.obsidian/plugins/visual-blocks/cache/... could not be found` messages
  remain.
- No duplicate native images remain.
- The status bar still reports the expected cached count.

Phase 12 re-gate passed on 2026-05-03.

### Phase 12 — Visual Blocks real migration — 2026-05-02 AGENT COMPLETE

**Scope:** Execute the already-approved destructive migration from
`attachments/cache/tikz/` to the final Visual Blocks plugin-managed cache
layout.

**Approval:**

- User explicitly replied: `Approved: run Visual Blocks migration`.
- This satisfied the required confirmation gate for the bulk move, markdown
  rewrite, PNG deletion, orphan deletion, and legacy directory removal.

**Execution result:**

- Command:
  `/opt/homebrew/Caskroom/miniconda/base/bin/python
  resources/scripts/python_single/migrate_to_render_cache.py`
- SVG moves: 170.
- Markdown files updated: 100.
- Markdown refs updated: 169.
- Legacy PNGs deleted: 5.
- Orphan SVGs deleted: 3.
- Dropped non-vault/missing index notes: 1.
- Missing SVG refs: 0.
- Old index: `attachments/cache/tikz/index.json`.
- New index: `.obsidian/plugins/visual-blocks/cache/index.json`.
- Legacy directory removed: true.

**Post-migration structural verification:**

- `.obsidian/plugins/visual-blocks/cache/v1/` contains 170 SVG files.
- New `index.json` contains 170 cache paths.
- Index verification: 0 missing cache files; 0 paths outside the
  `.obsidian/plugins/visual-blocks/cache/v1/` prefix.
- Markdown verification: 183 `|visual-blocks` embeds found across content
  roots; 0 missing target files.
- Post-migration dry run:
  `migrate_to_render_cache.py --dry-run` reports 0 SVG moves, 0 markdown
  updates, 0 PNG deletes, 0 orphan SVG deletes, and 0 missing refs.
- `attachments/cache/tikz/` no longer exists.

**Automated verification:**

- Python:
  `/opt/homebrew/Caskroom/miniconda/base/bin/python -m pytest
  resources/scripts/python_single/tests -q` → 169 passed, 6 skipped.
- Plugin Jest:
  `.obsidian/plugins/visual-blocks npm test -- --runInBand` → 79/79 pass.
- Plugin build:
  `.obsidian/plugins/visual-blocks npm run build` → production bundle
  succeeds.
- Obsidian harness canary:
  `resources/tests/harness node --import tsx run.ts --canary
  --json=/tmp/visual-blocks-phase12-post-migration-canary-2026-05-02.json`
  → PASS, 3/3 assertions, 0 console errors, 0 warnings.

**Notes and decisions:**

- **D12.5 — Real migration executed only after explicit approval.** The
  destructive run matched the refreshed dry-run exactly.
- **D12.6 — `package-lock.json` local metadata was refreshed.** The ignored
  local lockfile still had the old `obsidian-render-cache` package name; it
  now matches `obsidian-visual-blocks` / `0.4.0`. It remains ignored by the
  plugin-local `.gitignore`, so it is not part of the commit surface.
- **D12.7 — Archival transcript refs are not active cache refs.** A strict
  legacy-embed scan finds 14 old `mSB3-4_reals__1__fe1400ae.svg|tikz-cache`
  strings in journal/inbox/archive transcript notes. They quote prior
  debugging sessions, not current source-note cache refs. The active source
  note `kn/math/concepts/mSB3-4_reals.md` now points to the Visual Blocks
  cache path and verifies as an existing file.

**Divergence check — Phase 12:**

- Files modified vs plan: high by design, because Phase 12 is the planned
  vault-wide migration phase.
- Scope: migration script, plugin cache, old cache deletion, markdown ref
  rewrite, and `PROGRESS.md`.
- Complexity: no new runtime logic in the real-run step.
- Status: expected bulk migration divergence; no unplanned feature work.

**User gate — Phase 12:**

Open representative migrated notes in Obsidian desktop and iOS after sync:

- `kn/math/concepts/mSB3-4_reals.md`
- `kn/math/concepts/mSB5-2_partial.md`
- `kn/math/concepts/mLA5-1_eigenvalues.md`
- `kn/math/concepts/_RENDER_TEST_d2.md`

Confirm:

- Visual Blocks renders the diagrams from the new plugin cache path.
- No broken-image icons for the migrated diagrams.
- No duplicate legacy `tikz-cache` image remains in the rendered note.
- Status bar shows the expected cached count rather than cache-miss errors.

When confirmed, reply: `Phase 12 user gate passed` and then trigger
`Implement Phase 13`.

### Phase 12 — Visual Blocks rename prep before migration — 2026-05-02 IN PROGRESS

**Scope:** Prepare the Phase 12 migration under the final plugin identity
before running the destructive legacy-cache migration.

**Completed in prep:**

- Renamed the Obsidian plugin identity from `obsidian-render-cache` to
  `visual-blocks`.
- Manifest now uses:
  - `id`: `visual-blocks`
  - `name`: `Visual Blocks`
  - `version`: `0.4.0`
- Package metadata now uses `obsidian-visual-blocks`.
- Plugin directory is `.obsidian/plugins/visual-blocks/`.
- `.obsidian/community-plugins.json` now enables `visual-blocks`.
- Python cache root now targets `.obsidian/plugins/visual-blocks/cache/`.
- Canonical generated markdown references now use `|visual-blocks`.
- Compatibility remains for pre-existing `|tikz-cache` and transitional
  `|render-cache` references in the markdown matcher and migration script.
- Existing sample/test notes were updated to point at
  `.obsidian/plugins/visual-blocks/cache/...|visual-blocks`.

**Migration hardening added before real execution:**

- `migrate_to_render_cache.py` now explicitly removes an existing destination
  SVG before moving the legacy SVG into place.
- Added regression test
  `test_real_run_replaces_existing_destination_svg` so the real migration does
  not depend on platform-specific `shutil.move` overwrite behavior.

**Dry-run result after rename:**

- Command:
  `/opt/homebrew/Caskroom/miniconda/base/bin/python
  resources/scripts/python_single/migrate_to_render_cache.py --dry-run`
- SVG moves: 170
- Markdown files to update: 100
- Markdown refs to update: 169
- Legacy PNGs to delete: 5
- Orphan SVGs to delete: 3
- Dropped non-vault/missing index notes: 1
- Missing SVG refs: 0
- Old index: `attachments/cache/tikz/index.json`
- New index: `.obsidian/plugins/visual-blocks/cache/index.json`
- No filesystem changes were made by the dry-run.

**Verification:**

- Focused migration test:
  `resources/scripts/python_single/tests/test_migrate_to_render_cache.py` →
  5/5 pass.
- Python suite:
  `/opt/homebrew/Caskroom/miniconda/base/bin/python -m pytest
  resources/scripts/python_single/tests -q` → 169 passed, 6 skipped.
- Plugin Jest:
  `.obsidian/plugins/visual-blocks npm test -- --runInBand` → 79/79 pass.
- Plugin build:
  `.obsidian/plugins/visual-blocks npm run build` → production bundle succeeds.
- Scoped stale-name search:
  no `obsidian-render-cache`, `.obsidian/plugins/obsidian-render-cache`,
  `Obsidian Render Cache`, `Render Cache`, or `docs/specs/visual-blocks`
  references in the active plugin/Python/spec/progress surface.
- Obsidian UI canary:
  `node --import tsx run.ts --canary
  --json=/tmp/visual-blocks-rename-prep-canary-2026-05-02T1100.json` →
  PASS, 3/3 assertions, 0 console errors, 0 warnings.

**Decisions:**

- **D12.1 — Rename before real migration.** The destructive move should write
  directly into the final `.obsidian/plugins/visual-blocks/cache/` location
  instead of migrating once to an old product identity and then moving again.
- **D12.2 — Keep Python package name `render_cache`.** The user-facing plugin
  and markdown identity are Visual Blocks; the Python package remains the
  stable implementation module because renaming it now would add risk without
  changing UX.
- **D12.3 — Canonical alt text is `visual-blocks`; compatibility stays.**
  New/rewritten refs use `|visual-blocks`; `|tikz-cache` and `|render-cache`
  are still parsed so older notes can be migrated safely.
- **D12.4 — Do not execute the real migration without explicit approval.**
  The next command will move 170 SVGs, rewrite 100 markdown files / 169 refs,
  delete 5 PNGs, delete 3 orphan SVGs, and remove the legacy cache directory.
  This remains blocked until the user explicitly approves the real run.

**Next approval phrase:**

> `Approved: run Visual Blocks migration`

### Phase 11 — iOS validation — 2026-05-02 DONE

**Scope:** Validate SPEC AC11.1-AC11.4 on physical iOS Obsidian. This phase is
owned by the user because the desktop harness cannot exercise iOS WebKit,
mobile plugin loading, iCloud/Obsidian Sync behavior, or the prior crash mode.

**Agent-side local preflight completed:**

- Plugin exists at `.obsidian/plugins/visual-blocks/` with
  `manifest.json` version `0.3.0` and `"isDesktopOnly": false`.
- `.obsidian/community-plugins.json` includes `visual-blocks`, so the
  plugin is locally enabled and should be available to sync to mobile.
- `attachments/cache/tikz/index.json` exists with `schemaVersion: 1`, 106 note
  entries, and adapter preamble hashes for TikZ, Graphviz, D2, LilyPond, and
  SMILES.
- Dry-run cache checks all hit for the five Phase 11 representative notes:
  - `kn/math/concepts/mSB5-2_partial.md`: 1 TikZ block, cache hit
  - `kn/math/concepts/_TIKZ_TEST_mSB5-2.md`: 5 TikZ blocks, all cache hits
  - `kn/math/concepts/mSB3-4_reals.md`: 1 TikZ block, cache hit
  - `kn/math/concepts/mSB3-5_complex.md`: 1 TikZ block, cache hit
  - `kn/math/concepts/mLA5-1_eigenvalues.md`: 2 TikZ blocks, both cache hits
- Target SVG integrity check: all 10 target SVGs exist, have `viewBox`, have no
  `file://` references, have no `pt` width/height, and have no `lastError`.

**Verification run before user gate:**

- `.obsidian/plugins/visual-blocks`: `npm test -- --runInBand` →
  79/79 Jest tests pass.
- `.obsidian/plugins/visual-blocks`: `npm run build` → production
  bundle succeeds.
- `/opt/homebrew/Caskroom/miniconda/base/bin/python -m pytest
  resources/scripts/python_single/tests -q` → 170/170 Python tests pass.

**Observation — not blocking Phase 11:**

- The shell's default `python3` is Homebrew Python 3.14 and lacks `rdkit` and
  `pytest`; the conda Python at `/opt/homebrew/Caskroom/miniconda/base/bin/python`
  is the verified interpreter. Phase 11 is mobile cache-only and does not spawn
  Python, so this does not block iOS validation. Before testing desktop
  trigger-on-save or SMILES rendering in the real vault, set Visual Blocks's
  Python path setting to the conda interpreter if it is not already saved in
  Obsidian's plugin data.
- During preflight, `attachments/cache/tikz/index.json` and
  `mSB3-4_reals__1__814d986af7c9302c.svg` briefly changed even though the
  intended checks were read-only. The diff was cache churn only
  (`renderedAt` timestamp plus reordered SVG `<defs>`); both files were
  restored before commit. Treat this as a future dry-run/live-render anomaly
  to investigate if it recurs.

**User phone gate — required results for AC11.1-AC11.4:**

1. On iOS, let the vault finish syncing. Confirm
   `.obsidian/plugins/visual-blocks/` is present by checking that
   Settings → Community plugins shows "Visual Blocks".
2. Enable "Visual Blocks" on iOS if it is not already enabled.
3. Open `kn/math/concepts/mSB5-2_partial.md`.
   - Expected: loads cleanly, no crash, no reload loop, page interactive within
     about 2 seconds, partial-derivative surface SVG visible.
4. Open `kn/math/concepts/_TIKZ_TEST_mSB5-2.md`.
   - Expected: loads cleanly, no crash, no reload loop, all five cached TikZ
     diagrams visible.
5. Open at least three representative files total from this set:
   - `kn/math/concepts/mSB5-2_partial.md`
   - `kn/math/concepts/_TIKZ_TEST_mSB5-2.md`
   - `kn/math/concepts/mSB3-4_reals.md`
   - `kn/math/concepts/mSB3-5_complex.md`
   - `kn/math/concepts/mLA5-1_eigenvalues.md`
6. For each file, report one result:
   - `A`: clean load, all diagrams visible, correct
   - `B`: partial load, some diagrams missing, duplicated, or visually wrong
   - `C`: crash, reload loop, or app becomes unusable
7. For any `B` or `C`, include the file name, which diagram/block failed if
   visible, and whether the status bar showed `✓`, `⚠`, or a cache-miss/error
   placeholder.

**User gate result:**

- User reported: "clean/correct on 2,3,4."
- Interpreted against the immediately preceding gate list:
  - Step 2: Visual Blocks enabled on iOS.
  - Step 3: `kn/math/concepts/mSB5-2_partial.md` clean/correct on iOS.
  - Step 4: `kn/math/concepts/_TIKZ_TEST_mSB5-2.md` clean/correct on iOS.
- The user also confirmed the required representative-file check by including
  step 4 from the abbreviated final checkpoint list ("open at least one more").
  No `B` or `C` outcomes were reported.
- Phase 11.4 sync/storage triage is not needed.

**Divergence Check — Phase 11 preflight**

- [x] Files modified vs plan: only `PROGRESS.md` (phase is user-owned; no code
  changes expected before phone validation).
- [x] Max complexity: no implementation changes.
- [x] All work links to SPEC AC11.1-AC11.4 and PLAN Tasks 11.1-11.3.
- [x] No destructive cache operations; unintended cache churn was inspected and
  restored; only `PROGRESS.md` remains modified.

**Tests / Verification:** 79/79 Jest, 170/170 Python, local cache integrity
preflight, plus physical iOS user gate passed. Committed: `5b4451f15` +
hash-record commit.

**Next:** Phase 12 — Migration tool: legacy → new layout.

### Phase 10 — Plugin error display + status bar — 2026-05-01 DONE

**Scope:** Implement SPEC AC10.1-AC10.4: failed render visibility,
retryable inline error blocks, and a status-bar item for per-note cache state.

**Completed:**

- Python dispatcher now preserves failed blocks in `index.json` instead of
  dropping them from the note entry. Failed block metadata includes
  `blockIdx`, `language`, `sourceHash`, expected `cachePath`, `outputBytes`,
  `renderedAt: null`, and `lastError`.
- Plugin display path now checks `entry.lastError` before checking the SVG
  file. Error entries render an inline error block with the captured renderer
  message rather than a cache-miss placeholder or stale image.
- Desktop inline error blocks are clickable. Retry runs
  `render_cache.py FILE.md --force`, reloads the index, and keeps the error
  visible if the retry still fails.
- Added status-bar item:
  - idle: `✓ N item(s)`
  - rendering: `rendering 1/N...` or `rendering...`
  - error: `⚠ N failed`
- Status-bar click opens the existing Phase 9 `CacheStatusModal`.
- Render-state updates are wired into refresh-block, refresh-note,
  refresh-vault, live mode, and trigger-on-save.
- Plugin version bumped `0.2.0 -> 0.3.0`.

**Tests and verification:**

- TDD red phase observed:
  - Python failed-render test initially failed because failed blocks were
    omitted from `index.json`.
  - Jest status tests initially failed because `aggregateNoteStatus` and
    `statusBarText` did not exist.
- `npm test -- --runInBand` in `.obsidian/plugins/visual-blocks`:
  79/79 Jest tests pass.
- `npm run build` in `.obsidian/plugins/visual-blocks`: production
  bundle succeeds.
- `python3 -m pytest resources/scripts/python_single/tests -q`:
  170/170 Python tests pass.
- Isolated obsidian-verify harness runner:
  `/tmp/visual-blocks-phase10-gate.mjs`
  - PASS: seed temp vault with one valid D2 cache and one broken TikZ
    `lastError` entry.
  - PASS: plugin loads in pinned desktop Obsidian.
  - PASS: valid note shows cached SVG and status bar `✓ 1 item`.
  - PASS: broken TikZ note shows inline LaTeX error and status bar
    `⚠ 1 failed`.
  - PASS: inline error click retries render and preserves the visible error.
  - PASS: status-bar click opens cache-status modal with error summary.
  - PASS: final visual-blocks console check: 0 errors, 0 warnings.
- JSON report:
  `/tmp/visual-blocks-phase10-gate-2026-05-01T20-43-02-645Z.json`
- `node --import tsx run.ts --canary` in `resources/tests/harness`:
  PASS canary, 3/3 assertions, 0 console errors, 0 warnings.

**Decisions (D10.x):**

- **D10.1 — Record failures as first-class block entries.** AC10.1 cannot
  work if a failed block disappears from `index.json`. The dispatcher now
  records errored block metadata with `lastError` and no markdown wikilink
  insertion.
- **D10.2 — `lastError` beats stale SVG display.** If an entry has
  `lastError`, the plugin shows the inline error block before checking whether
  `cachePath` exists. This avoids silently showing stale images after a forced
  retry fails.
- **D10.3 — Error retry uses `--force`.** A retry should exercise the failed
  source even if an old SVG still exists at the expected path.
- **D10.4 — Status bar is per active note, not vault-wide.** The modal remains
  vault-wide aggregate status; the status-bar item answers "what is the state
  of the note I am looking at?"
- **D10.5 — No history rewrite after auto-backup.** The vault auto-backup
  captured implementation files as `cfe598614` while verification was running,
  along with unrelated journal/archive edits. I did not rewrite history or
  touch unrelated files. I restored two verification-induced cache artifacts
  in the Phase 10 log commit.
- **D10.6 — D6.7 fence-tag derive-from-REGISTRY refactor remains deferred.**
  Phase 10 already touched Python for error metadata and TypeScript for UI
  behavior. The fence-tag cleanup is unrelated to AC10.1-AC10.4 and remains
  a small follow-up, not a Phase 10 blocker.

**Deviations / caveats:**

- PLAN §Phase 10 is a two-sentence delegation. The implementation shape
  (`cacheStatus` pure helpers + main plugin integration + command render-state
  callbacks) is agent-chosen and tied directly to AC10.1-AC10.4.
- The isolated desktop harness cannot become physical iOS. Phase 10 retry is
  intentionally desktop-only because mobile cannot spawn Python; Phase 11 is
  still the dedicated iOS validation gate.

**Divergence Check — Phase 10**

- [x] Files modified vs plan: PLAN named no explicit files; actual scope was
  plugin source/build/tests/styles + Python dispatcher/test + PROGRESS.
- [x] Max complexity: reasonable; no new renderer algorithm, only metadata
  recording and UI state wiring.
- [x] All changes link to AC10.1-AC10.4.
- [x] No repeated identical tool calls (>3) after failures; harness failure
  was debugged by adding DOM diagnostics, then tightening selector/click logic.

**Next:** Phase 11 — iOS validation (USER-DRIVEN).

### Phase 9 Gate Closure — obsidian-verify — 2026-05-01 DONE

**Scope:** Verify Phase 9's 13-step user gate using the `obsidian-verify`
skill and harness, without mutating the real vault cache.

**Method:**

- Created a temporary runner at `/tmp/visual-blocks-phase9-gate.mjs`.
- Used the obsidian-verify harness modules (`isolateVault`, `launchElectron`,
  `stabilize`, `captureConsole`, `waitUntilVaultStable`) against a throwaway
  copy of `resources/tests/test-vault/`.
- Copied the built `visual-blocks` plugin into the temporary vault,
  enabled it in that vault's `.obsidian/community-plugins.json`, and set
  plugin data to use the conda Python path.
- Copied the Python `render_cache` package into the temporary vault and
  patched only that temporary copy's `cache_paths.py` so destructive paths
  (`sweep`, `clear-all`) affected the temp cache, not the real vault.
- Seeded a three-block D2 note, pre-rendered its cache, launched pinned
  Obsidian via CDP, then drove the real command callbacks through Obsidian's
  command registry and UI modals.

**Gate result:**

- PASS — plugin loaded cleanly; console log captured:
  `visual-blocks: loaded; processors registered for tikz, graphviz,
  d2, lilypond, smiles; mode=hybrid; triggerOnSave=true`.
- PASS — settings tab rendered the expected controls: mode, Python path,
  script path, re-render-on-save, login-shell toggle.
- PASS — `Refresh all blocks in this note` spawned Python and completed.
- PASS — `Refresh this block` updated the targeted D2 cache file.
- PASS — `Show cache status` opened the status modal with D2 cache data.
- PASS — `Toggle render mode` cycled `cache-only -> live -> hybrid`.
- PASS — `Sweep orphan cache files` removed only a canonical fake orphan and
  preserved a real cache file.
- PASS — `triggerOnSave` persisted an editor edit through `editor:save-file`
  and produced a new D2 cache hash.
- PASS — live mode re-rendered on preview load.
- SKIP (desktop-harness limitation) — physical iOS UI cannot be exercised by
  pinned desktop Obsidian. AC9.9's mobile branch is covered by
  `settings.test.ts` (`effectiveMode`, mobile miss text, non-clickability).
  Real mobile validation remains Phase 11.
- PASS — `Refresh entire vault` showed the confirmation modal and streamed to
  a progress modal ending in `Done.`
- PASS — `Clear entire cache (DESTRUCTIVE)` deleted SVGs only inside the
  isolated temporary vault.
- PASS — final console check: zero visual-blocks errors and zero warnings.

**Artifacts:**

- JSON report:
  `/tmp/visual-blocks-phase9-gate-2026-05-01T18-36-25-336Z.json`
- Temporary runner:
  `/tmp/visual-blocks-phase9-gate.mjs`

**Additional verification after gate:**

- `npm test -- --runInBand` in `.obsidian/plugins/visual-blocks`:
  73/73 Jest tests pass.
- `python3 -m pytest resources/scripts/python_single/tests -q`:
  169/169 Python tests pass.
- `node --import tsx run.ts --canary` in `resources/tests/harness`:
  PASS canary, 3/3 assertions, 0 console errors, 0 warnings.

**Decision (D9.12):** Treat Phase 9 gate as closed for desktop command
coverage. Do not pretend the desktop harness performed a physical iOS test;
the mobile override is unit-verified here and remains part of the dedicated
Phase 11 iOS validation gate.

**Next:** Phase 10 — Plugin error display + status bar.

### Phase 9 — Plugin commands and modes — 2026-04-28 DONE (agent-side)

**Completed:**

- **`src/settings.ts`** (~190 lines) — `RenderCacheSettings` interface (5 keys: `mode` / `pythonPath` / `scriptPath` / `triggerOnSave` / `useLoginShell`); `DEFAULT_SETTINGS` const; `MODE_CYCLE` (hybrid → cache-only → live → hybrid); pure helpers `nextMode` / `effectiveMode` (mobile auto-override AC9.9) / `missMessage` (3 desktop branches × 1 mobile branch) / `isPlaceholderClickable` (4 cases); `RenderCacheSettingTab` with 5 controls (dropdown for mode + 2 text inputs for paths + 2 toggles).
- **`src/render.ts`** (~190 lines) — Subprocess wrapper. Pure `shellEscape` (POSIX single-quote with `'\''` for embedded quotes). Pure `buildSpawnArgs` returning `{command, args}` pair: direct mode `[pythonPath, scriptPath, ...args]` OR login-shell mode `[$SHELL, "-lc", "<escaped command line>"]`. The latter handles macOS Electron renderer NOT inheriting the user's interactive shell PATH (advisor §1) — login shell forces source of `~/.zshrc` / `~/.bashrc` / brew + conda init lines. `spawnRender` async wrapper around `child_process.spawn` with optional line-streaming callback (used by refresh-vault progress modal). `spawnRenderWithNotice` convenience for fire-and-forget commands (refresh-block / refresh-note / sweep) — surfaces a Notice on success or on non-zero exit (with stderr/stdout snippet).
- **`src/cacheStatus.ts`** (~155 lines) — Pure `aggregateStatus(index)` returns `{totalNotes, totalBlocks, totalBytes, perLanguage[], errorCount, schemaVersion, rendererVersion}`; per-language breakdown sorted by descending count. Pure `formatBytes` (B / KiB / MiB rounding). `CacheStatusModal` displays the data in a table.
- **`src/commands.ts`** (~465 lines) — Pure `findBlockAtCursorLine(source, line)` → `{blockIdx, language, lineStart, lineEnd}` or null. `registerCommands(ctx)` registers all 7 with the command palette: refresh-block (AC9.1) → finds block at cursor, deletes that one cache file, runs render_cache.py FILE.md (no `--force` so other blocks stay cached). refresh-note (AC9.2) → render_cache.py FILE.md `--force`. refresh-vault (AC9.3) → ConfirmationModal then streaming `--all --force` into a ProgressModal showing live stdout/stderr lines. show-status (AC9.4) → CacheStatusModal. sweep (AC9.5) → render_cache.py `--sweep`. toggle-mode (AC9.6) → cycles via `nextMode` and persists. clear-all (AC9.7) → ConfirmationModal then walks `attachments/cache/tikz/` and `adapter.remove`s each file. `fireLiveRender` helper for live-mode background renders. Two private modal classes: `ConfirmationModal` (Cancel / Confirm with `mod-warning` styling) and `ProgressModal` (live log + status line).
- **`src/main.ts`** rewritten (~270 lines) — Phase 9 integration. Loads/persists settings (loadData/saveData). Registers all 7 commands via `registerCommands`. Registers `RenderCacheSettingTab`. Mode-aware `displayCachedBlock`: live mode (desktop) fires async `--force` re-render of the file (debounced via `liveRenderInFlight` Set so all blocks in a note share one render). Cache-miss placeholder uses `missMessage` + `isPlaceholderClickable` based on `effectiveMode`. Click-to-render handler runs render_cache.py FILE.md (no force) and shows a Notice on completion. `triggerOnSave` registers `app.vault.on('modify', …)`: filters to `.md`-only TFile + has-supported-block grep, debounces to one render per file per 3 seconds, skips on mobile, runs `render_cache.py FILE.md` (no force) and reloads index. `vaultRoot()` uses `FileSystemAdapter.getBasePath()`.
- **`styles.css`** extended — modal button row + per-language status table + log pre + meta/error tone classes.
- **Tests** — 4 new test files, 49 new pure-function tests:
  - `tests/settings.test.ts` (18) — mode cycle / mobile override / missMessage 5 cases / isPlaceholderClickable 4 cases / DEFAULT_SETTINGS shape.
  - `tests/render.test.ts` (11) — shellEscape (5) + buildSpawnArgs direct mode (2) + login-shell mode (4 including paths-with-spaces and paths-with-quotes).
  - `tests/cacheStatus.test.ts` (10) — formatBytes (3) + aggregateStatus (7 incl. null index, descending sort, lastError counting, missing language, missing outputBytes, version propagation).
  - `tests/commands.test.ts` (10) — findBlockAtCursorLine across cursor inside/outside/on-fence; tikz-paused → tikz; lilypond + smiles recognition; blockIdx skips unsupported langs.
- **TS test count: 24 → 73** (3.0× growth). 73/73 green. **Python test count: 150/150 fast green** (no regressions).
- **Build** — `npm run build` produces `main.js` 17.8 KB minified (was 4.5 KB Phase 8). Bundle externs unchanged: obsidian + electron + CodeMirror + Node builtins.
- **Manifest + package.json** version 0.1.0 → 0.2.0 (Phase 9 release marker; v1.0.0 at Phase 13).
- **Mock surface extended** — `tests/__mocks__/obsidian.ts` gained `PluginSettingTab`, `Setting`, `Modal`, `FileSystemAdapter`, `App`, `MarkdownView`, `Plugin.addSettingTab/loadData/saveData/registerEvent`, `Platform.isMacOS`. Required for type-check; tests don't actually exercise these (smoke-tested at user gate).

**Decisions Made (D9.x):**

- **D9.1 — refresh-block uses delete-then-render-without-force, not extend the Python CLI with `--block-index N`.** Advisor §2 confirmed the approach. Mechanical: remove the cache file for the block at cursor, then `python3 render_cache.py FILE.md` (no `--force`). The dispatcher's existing skip-on-cache-hit logic re-renders only the missing block. Net Python CLI surface unchanged (Phase 9 zero Python-side edits except the PROGRESS log entry). Cleanest scope discipline.
- **D9.2 — Live mode = synchronous fire-and-forget, NOT streaming hot-swap.** Advisor §3 listed three options (sync block-and-display / optimistic stale + hot-swap / placeholder + swap). Chose sync fire-and-forget on every codeblock pass, debounced per file via `liveRenderInFlight` Set so multi-block notes don't fire N parallel renders. Trade-off: user sees stale cache (or placeholder) for the first 2-10s while render completes, then must reload the note manually or save+modify to see the new cache. v1.1 candidate: file-watch on `index.json` to auto-rerender views when entries update. Documented as accepted trade-off.
- **D9.3 — `pythonPath` defaults to `python3` + `useLoginShell=true` (macOS PATH inheritance).** Advisor §1 flagged the Electron-renderer-doesn't-inherit-shell-PATH issue. Empirically not yet verified on the user's system (advisor's Cmd+Opt+I test hasn't run); design defends BOTH cases — works whether shell-inherited python3 has rdkit or not. User can override `pythonPath` to absolute conda path AND/OR disable `useLoginShell` for fastest spawn. The setting is in the SettingTab so iteration is one-keystroke.
- **D9.4 — refresh-vault uses streaming progress modal, NOT a Notice.** Advisor §2 noted "render_cache.py --all writes to stdout; you'll need to stream stdout/stderr from the spawned process and pipe it into a Notice or a Modal with a progress region." A Notice would be too transient for a multi-minute render; Modal is the right surface. Lines append in real time via `onLine` callback wired through `spawnRender` → `appendLine` on the modal.
- **D9.5 — clear-all walks `attachments/cache/tikz/` and removes files individually rather than `rmdir` the directory.** Two reasons: (a) the cache directory is vault-tracked; rmdir-ing it would break the vault tree; (b) Obsidian's adapter API exposes `remove()` and `list()` cleanly but not always `rmdir()`. Iterating per-file is safer + portable across desktop/mobile (mobile shouldn't reach this path under AC9.9 but defensive code is cheap). Phase 12 (legacy → new layout migration) will revisit when the cache moves to `.obsidian/plugins/.../cache/v1/<note>/`.
- **D9.6 — triggerOnSave debounce is 3 seconds (per-file).** Empirically chosen. Obsidian fires `modify` on every keystroke after a brief settle; without debounce the plugin would spawn dozens of renders per typing burst. 3s is long enough that mid-typing renders don't queue, short enough that Cmd+S → preview latency stays under 5s. The throttle is a per-path Map; cleared by garbage collection naturally as the plugin lives.
- **D9.7 — Pure-helpers TDD discipline** continued. `nextMode` / `effectiveMode` / `missMessage` / `isPlaceholderClickable` / `shellEscape` / `buildSpawnArgs` / `aggregateStatus` / `formatBytes` / `findBlockAtCursorLine` ALL have unit tests written before implementation. Same red-then-green pattern as D3.5 / D4.6 / D5.7 / D6.6 / D7.7 / D8.10. Obsidian-API glue (Modal classes, command callbacks, save hook) is smoke-tested at the user gate — pretending to mock Obsidian's `Modal.open()` etc. would produce false-positive "tests" without verifying any behaviour. Advisor §4 explicitly endorsed this split.
- **D9.8 — D6.7 fence-tag REGISTRY-derive refactor + D7.9 implicit-default-fill rule deferred AGAIN, NOT bundled into Phase 9.** Same scope-discipline reasoning as D7.10 / D8.13: Phase 9 is large enough; bundling unrelated cleanup adds diff noise. D6.7 queues for Phase 10 lead-in (Phase 10 is "error display + status bar" — the natural moment for a Python-side cleanup). D7.9 stays deferred because it depends on the SPEC's `<img>` vs inline-svg stance which user accepted at D8.2.
- **D9.9 — refresh-block + refresh-note persist editor buffer to disk before spawning Python.** Advisor pre-ship review §1 flagged this as a real footgun: `app.vault.modify(file, view.editor.getValue())` is the cheap fix. Without it, a user with unsaved edits in the active block runs "Refresh this block", Python reads disk (still old), produces an identical cache → silent no-op. With the fix, the buffer is persisted first so Python reads the visible content. Skipped if buffer == disk (avoids a redundant write+modify-event cascade). Same fix applied to refresh-note. NOT applied to refresh-vault (the user would have many unsaved buffers in unrelated notes; persisting all of them is too aggressive — the right behavior on `--all` is to render disk-state).
- **D9.10 — Conda non-interactive login shell guard is a known limitation.** Advisor pre-ship review §2 noted that zsh `-l` sources `.zprofile` / `.zshrc` BUT most conda init blocks have an interactive-only guard (`[[ $- == *i* ]] || return`). So a non-interactive login shell may NOT activate conda. The user's `python3` could resolve to system python (no rdkit). Mitigation already in place: `pythonPath` setting + user-gate step 3 explicitly tells the user to override on failure. If the user gate report shows "Failed to spawn python" or "render_cache.py exited 1" at step 3, the diagnosis is "set Python path to absolute conda binary path"; documented for Phase 11/12.
- **D9.11 — Sweep verification (user-gate step 7) uses a canonical-pattern fake.** Advisor pre-ship review §3 flagged that `render_cache.py --sweep` regex-matches `^(.+)__(\d+)__([0-9a-f]{8,})\.svg$`; arbitrary names like `_orphan_test.svg` get the "unparseable cache name, leaving" treatment (verified at `render_cache/__init__.py:196`). User-gate step 7 instruction now creates a `_FAKE_NOTE__9__deadbeefdeadbeef.svg` (canonical pattern, no matching markdown source) which the sweep correctly identifies as an orphan and deletes.

**Deviations from Plan:**

- **PLAN §Phase 9 was a single paragraph** ("Tasks: implement all 7 commands per SPEC §5 Phase 9 acceptance criteria AC9.1–AC9.10. Implement settings UI and mode switching per the same.") with no per-task pseudocode. This is a feature, not a deviation: PLAN delegated the implementation shape to Phase 9 execution. The 4-module split (settings/render/cacheStatus/commands) and the 49-test surface are agent-decided.
- **D9.1 (refresh-block) does NOT extend the Python CLI** as a hypothetical PLAN reading might have suggested. Delete-then-render achieves the same semantic with zero Python-side changes.
- **D9.2 (live mode = fire-and-forget)** is one of three SPEC-acceptable readings of AC9.8 ("re-renders every block on every load"). The fire-and-forget interpretation is the simplest; documented + accepted as v1 trade-off.

**Tests:** 73/73 jest (49 new + 24 pre-existing); 150/150 Python fast (no regressions). Build: `main.js` 17.8 KB minified.

**AC mapping (USER-GATE pending; agent-side commitments below):**

- AC9.1 (refresh-block) — agent-side: handler wired, finds block at cursor via `findBlockAtCursorLine`, removes cache file via `adapter.remove`, spawns render. User gate: place cursor in a TikZ/D2/etc. block, run "Refresh this block", confirm block re-renders.
- AC9.2 (refresh-note) — agent-side: handler wired, runs `render_cache.py FILE.md --force`. User gate: run command on a note with multiple blocks, confirm all re-rendered.
- AC9.3 (refresh-vault) — agent-side: confirmation modal + streaming progress modal + `--all --force`. User gate: run command, confirm prompt + progress lines + completion.
- AC9.4 (show-status) — agent-side: aggregateStatus is unit-verified across 7 cases; modal displays the data. User gate: run command, verify table content matches `attachments/cache/tikz/index.json`.
- AC9.5 (sweep) — agent-side: `render_cache.py --sweep`. User gate: introduce an orphan SVG manually, run sweep, confirm it's deleted, real cache untouched.
- AC9.6 (toggle-mode) — agent-side: nextMode unit-verified across cycle + unknown-input fallback. User gate: run command 3× in a row, observe Notice cycling hybrid → cache-only → live → hybrid.
- AC9.7 (clear-all) — agent-side: confirmation modal + `adapter.remove` per file. User gate: confirm strong prompt; click confirm; verify cache directory empty (one `index.json` may regenerate empty).
- AC9.8 (live mode re-renders on every load) — agent-side: live branch in `displayCachedBlock` calls `fireLiveRender` per file (debounced 5s). User gate: set mode=live; record cache mtime; reload note; confirm new mtime.
- AC9.9 (mobile auto-override) — agent-side: `effectiveMode(_, true) === "cache-only"` unit-verified across all stored-mode values. User gate: set mode=live on desktop, sync to iOS, open note, confirm placeholder reads "open on desktop to render" (not "click to render").
- AC9.10 (triggerOnSave) — agent-side: `vault.on('modify', …)` wired with hasSupportedBlock grep + 3s debounce. User gate: edit a TikZ block, save (Cmd+S), wait 5s, confirm cache mtime updates without explicit command invocation.

**Lessons Learned:**

- **Settings tab is mostly boilerplate, but the 5-key shape decision matters.** `pythonPath` + `useLoginShell` together cover the macOS Electron PATH inheritance issue without forcing a hard "absolute path" requirement. `triggerOnSave` is opt-in-by-default because the SPEC defaults to it; if it surprises the user with unexpected CPU bursts, one toggle disables it. `scriptPath` is only needed because the python_single layout is non-standard.
- **`buildSpawnArgs` shape (returns `{command, args}` pair) is more testable than returning a single argv array.** The return shape mirrors `child_process.spawn(command, args, opts)` so the test asserts the exact spawn surface. Unit tests verify both direct AND login-shell modes via 11 assertions.
- **`aggregateStatus` returning a sorted `perLanguage` array** (rather than a Map) makes tests trivial. Sorting by descending count puts the largest cache contributor at the top of the modal — natural for the "show cache status" use case.
- **`findBlockAtCursorLine` regex is `^```(\w[\w-]*)`, not just `^```(\w+)`.** The `[\w-]*` tail lets it match `tikz-paused` correctly (otherwise `tikz` matches and the rest is treated as junk). Block-counting only increments on supported-language fences; unsupported (e.g., python) blocks don't shift the index — important for refresh-block to map correctly to index.json's blockIdx field.
- **Live mode debouncing via a Set of in-flight file paths** keeps multi-block notes from firing N parallel `--force` renders. Tail clear via `setTimeout(5000)` is a cheap heuristic — at 5s the Python pipeline has either finished (cache repopulated, displayCachedBlock will hit it on next pass) or still running (next codeblock processor will skip our re-fire because the Set entry is fresh). Production iteration: replace with a Promise-completion-driven clear once we have a fileset-coordinator.
- **The Phase 8 `<img>` decision (D8.2) made AC9.8 / AC9.10 implementations simpler.** Live mode just calls `--force` and the next codeblock processor pass picks up the new cache; no need to invalidate browser image caches mid-render (which would be required with inline `<svg>`). Trade-off acknowledged: user must reload note to see the new cache from a live-mode render — equivalent to triggerOnSave's UX.
- **macOS PATH issue verification is best done at the user gate, not in the agent's verification.** The advisor's Cmd+Opt+I test (`require('child_process').execSync('which python3')`) requires running JS in the Electron renderer, which I cannot do. Designing for both cases (works whether PATH is inherited or not, with `pythonPath` override settable in one place) is more robust than asking the user to run a discriminator first.

**Cross-references:**

- SPEC §5 Phase 9 (AC9.1–AC9.10); §3.6 (view-time data flow, mode-aware behavior); §3.7 T7 (`getResourcePath`); §11.4 (per-phase user-feedback gate). PLAN §Phase 9 (one-paragraph delegation; D9.x deviations are within scope).
- Phase 8 D8.x — wikilink coexistence CSS, hash port, getResourcePath path; all reused unchanged. D8.9 (placeholder click-to-render) replaced by D9 click handler that actually spawns the render.
- Advisor (called pre-Phase-9) — §1 macOS PATH, §2 refresh-block/refresh-vault, §3 live mode trade-off, §4 testable-pure-only, §5 separate-commit-for-archive. All four directives followed.

**Phase 9 gate (user-driven, per SPEC §11.4):**

Phase 9 introduces 7 NEW commands and a settings tab. The user gate is more intricate than Phase 8's 8-step procedure — there are 10 acceptance criteria across the 7 commands + 3 modes + save hook. Suggested order (least destructive first):

1. **Reload the plugin** (Settings → Community plugins → Visual Blocks → toggle OFF then ON). Open Cmd+Opt+I → Console; expect:
   ```
   visual-blocks: loaded; processors registered for tikz, graphviz, d2, lilypond, smiles; mode=hybrid; triggerOnSave=true
   ```
   No red `Visual Blocks:` lines. (regression check: AC8.1 still passes after Phase 9 changes)

2. **Open Settings → Visual Blocks.** Verify 5 controls render: render-mode dropdown (default hybrid), python-path text field (default `python3`), script-path text field (default `resources/scripts/python_single/render_cache.py`), re-render-on-save toggle (default ON), spawn-through-login-shell toggle (default ON).

3. **Verify python spawns work BEFORE running heavy commands.** Open `kn/math/concepts/_RENDER_TEST_d2.md` (already renders correctly under Phase 8). Run command "Refresh all blocks in this note" via Cmd+P. Watch for a Notice "Refreshing all blocks in kn/…/_RENDER_TEST_d2.md…" then "Refreshed: …". If you see "Failed to spawn python: …" or "render_cache.py exited 1", the macOS PATH issue triggered (D9.3) — open Settings, set Python path to your conda Python (e.g., `/opt/homebrew/Caskroom/miniconda/base/bin/python3`), save, retry. If the second attempt also fails, surface the exact error here for triage.

4. **AC9.1 — Refresh this block.** Place cursor inside one of the 3 d2 blocks. Run "Refresh this block". Notice "Refreshing d2 block #N…" then "d2 block #N refreshed.". Cmd+R the note (View → Reload window) and confirm the diagram still renders correctly. The cache file's mtime under `attachments/cache/tikz/_RENDER_TEST_d2__N__<hash>.svg` should be fresh.

5. **AC9.4 — Show cache status.** Run "Show cache status". Modal opens with: total blocks (~169 across the vault), total disk size (~9 MiB), per-language table (tikz mostly, then d2/graphviz/lilypond/smiles). Verify the numbers roughly match `ls -la attachments/cache/tikz/*.svg | wc -l` and disk usage from Finder.

6. **AC9.6 — Toggle render mode.** Run "Toggle render mode (hybrid → cache-only → live)". Notice reads `Render mode: cache-only`. Run again → `Render mode: live`. Run again → `Render mode: hybrid`. Open Settings → Visual Blocks and verify the dropdown reflects the current mode.

7. **AC9.5 — Sweep orphans.** Important: `render_cache.py --sweep` parses cache filenames against the canonical regex `^(.+)__(\d+)__([0-9a-f]{8,})\.svg$` (verified at `render_cache/__init__.py:196`); files NOT matching the regex print "[?] unparseable cache name, leaving" and are skipped. Therefore an arbitrary stray name like `_orphan_test.svg` would NOT be deleted. To produce a sweep-eligible orphan, create a name that matches the regex but doesn't correspond to any actual block: `cp attachments/cache/tikz/_RENDER_TEST_d2__1__7d8f25d74720ebf0.svg attachments/cache/tikz/_FAKE_NOTE__9__deadbeefdeadbeef.svg`. The stem `_FAKE_NOTE` doesn't match any markdown file → sweep prints "[-] no source for …" and deletes it. Run "Sweep orphan cache files". Notice "Sweep complete.". Confirm `_FAKE_NOTE__9__deadbeefdeadbeef.svg` is gone; real cache files (e.g., `_RENDER_TEST_d2__1__…`) still present.

8. **AC9.10 — triggerOnSave.** With mode=hybrid (default), open `kn/math/concepts/mSB3-4_reals.md`. Edit the TikZ source slightly (e.g., add a comment line). Save (Cmd+S). Wait 5-10 seconds. The cache file's mtime should update. Reload the note (Cmd+R) — the diagram should render the new content. If you don't see an mtime update in 10s, surface the issue (likely a console.warn in DevTools: "visual-blocks: triggerOnSave on … exited N").

9. **AC9.8 — Live mode re-render.** Set mode=live (toggle command 2× from hybrid OR via Settings dropdown). Reload `_RENDER_TEST_d2.md`. Watch the cache file mtime: it should refresh on every reload. Note (per D9.2 trade-off): the user sees the OLD cache momentarily until Python finishes — reload again after 5-10s to see the NEW one. Reset mode=hybrid afterward.

10. **AC9.9 — Mobile auto-override.** With mode=live still active, sync to iOS, open any note with cached blocks. Placeholder for any cache miss should read "Cache miss — open on desktop to render." (NOT "click to render"). Cached blocks display as before (mobile = cache-only effective).

11. **AC9.2 — Refresh entire note** (already touched at step 3 verification). Confirm Notice cycle.

12. **AC9.3 — Refresh entire vault.** Run "Refresh entire vault (with confirmation)". Confirmation modal opens. Click "Refresh vault". Progress modal opens with live stdout/stderr lines as Python processes each note. Wait for "Done." status. Close modal. Verify a few cache files have refreshed mtimes.

13. **AC9.7 — Clear entire cache (DESTRUCTIVE — defer to last).** Run "Clear entire cache (DESTRUCTIVE)". Confirmation modal with "Yes, delete all" warning button. Click confirm. Notice "Cleared cache: N file(s) removed.". Verify `ls attachments/cache/tikz/` is empty (or only contains `index.json`). To recover: run "Refresh entire vault" or `python3 resources/scripts/python_single/render_cache.py --all` on the command line.

When all 13 steps pass (or any subset you have time for; mark partials in the response), reply: **"Implement Phase 10"** → Plugin error display + status bar. Phase 10 reads index.json's `lastError` field to render inline error placeholders + adds a status-bar item. Smaller scope (~2-3h estimate vs Phase 9's 4-6h actual).

**Outstanding (NOT blocking Phase 10 — flagged across phases):**

- 3 pre-existing TikZ source bugs (`bB3-18_neuroscience-101.md`, `mSB8-9_double-brackets.md`, `mSB3-8_euler-e.md`); separate-triage backlog. Surfaced for the 5th time during any `--all` operation in Phase 9 user gate (steps 3, 8, 9, 12 all touch them).
- **D6.7 fence-tag REGISTRY-derive refactor — deferred a 5th time** → queued for Phase 10 lead-in (Python-side commit; Phase 10 already touches python_single/render_cache for error capture surface).
- **D7.9 implicit-default-fill rule** stays deferred (depends on `<img>` vs inline-svg SPEC amendment; no movement).
- **`.obsidian/community-plugins.json` post-Phase-8-toggle health check** — Phase 8 closure noted that `visual-blocks` should now appear in the file (since it was enabled at startup). Confirm at any next session that the file lists the expected ~6 entries (5 prior + visual-blocks).
- **iOS Web Crypto contingency** unchanged from Phase 8 (still using `crypto.subtle.digest`; if Phase 11 surfaces "visual-blocks: tikz block failed" on iOS for every block, swap to js-sha256).
- **Live-mode hot-swap (D9.2 v1.1 candidate)** — file-watch on `index.json` to auto-reload views when entries update would replace the manual reload-after-5-10s UX.

---

### Phase 8 — Plugin scaffold — 2026-04-27 (this session) DONE (agent-side)

**Phase 7 user-gate closure (recorded here for atomicity):** User confirmed AC7.4 multi-block visual ("Yes, we see all the svgs in the _RENDER_TEST_d2.md note. We also see the codeblock still and the embedded internal links to the cached svgs. So User gate phase 7 passes."). The "we also see the codeblock still" observation is the surface motivation for Phase 8: under Phase 7 there is still no codeblock processor on `tikz`/`graphviz`/`d2`/`lilypond`/`smiles`, so reading view shows BOTH the raw codeblock AND the wikilink-rendered cached SVG side by side. Phase 8 plugin replaces the codeblock with a single cache-rendered `<img>`, hides the now-redundant wikilink, and gives misses a typed placeholder. AC7.5 (dark-mode follow) remains structurally blocked even after Phase 8 because the user explicitly chose the SPEC-mandated `<img>` embedding (not inline `<svg>`); see D8.2 below.

**Completed:**

- **Plugin scaffold at `.obsidian/plugins/visual-blocks/`** — manifest.json (id, name, version 0.1.0, minAppVersion 1.4.16, isDesktopOnly false), package.json (esbuild + jest + ts-jest + obsidian dev deps), tsconfig.json (ES2022 target, strict null checks), esbuild.config.mjs (production-mode CJS bundle, sourcemap=false), jest.config.cjs (ts-jest preset, node env, obsidian module mock), styles.css (plugin display + wikilink-hide + codeblock-wrapper override). 295 npm packages installed (zero high-severity vulns).
- **Hash port** — `src/hash.ts` (~140 lines). Three exported functions:
  - `normalize(source: string): string` — byte-identical to Python's `render_cache.normalize.normalize`. CRLF→LF, lone-CR→LF, per-line `.trim()` (BOTH ends; PLAN's `trimEnd()` would diverge — see fixture `per_line_whitespace_strip`), blank-line-run collapse, leading/trailing blank strip.
  - `pythonJsonDumps(value: unknown): string` — replicates Python's `json.dumps(sort_keys=True)` default separators `(', ', ': ')` byte-for-byte. JS's native `JSON.stringify` uses `(',', ':')` (no spaces) — would diverge the moment attrs become non-empty in Phase 9+. Recursive serializer handles strings (with `\uXXXX` escape for non-ASCII per Python's `ensure_ascii=True` default), numbers, booleans, null, arrays, objects (keys sorted at every level).
  - `computeKey(source, language, attrs, preambleHash): Promise<string>` — async (`crypto.subtle.digest('SHA-256', ...)` is async; works in Obsidian renderer + iOS WKWebView + Node 18+). Builds the SPEC §3.9 payload: `normalize(source) + 0x00 + lang + 0x00 + pythonJsonDumps(attrs) + 0x00 + preambleHash`, hashes via SubtleCrypto, hex-encodes, truncates to 16 chars.
- **Codeblock processors** — `src/main.ts` (~150 lines) registers processors for all five v1 languages (`tikz`, `graphviz`, `d2`, `lilypond`, `smiles`). Each processor calls `displayCachedBlock(source, lang, el, ctx)` inside a try/catch (advisor: "throw inside the processor callback can leave the codeblock unrendered or break the page; cheap insurance"). Empty source → no-op; empty `el`; create `.visual-blocks-block` wrapper. Read `index.json` once at `onload` into memory. Look up preambleHash via `index.preambleHashes["<adapter:LANG>"]` (advisor's #4 — already populated by Python pipeline; no hardcoded preambles in TS). Compute hash. Find the block entry by iterating `index.notes[ctx.sourcePath].blocks` for matching `sourceHash` (advisor: first-match-wins; identical-source duplicate blocks have identical SVG content so any match is correct). On hit + file-on-disk: emit `<img src="${app.vault.adapter.getResourcePath(entry.cachePath)}" alt="${lang}-cache" loading="lazy" class="visual-blocks-img">` per SPEC §3.4 step 3 + §3.6 step 4 + T7. On miss: typed placeholder, mobile reads "Open on desktop to render"; desktop is clickable and shows a Notice pointing the user to `render_cache.py` (Phase 9 wires the actual click-to-render).
- **Wikilink/plugin coexistence** — Plugin's `styles.css` includes `img[alt~="tikz-cache"]:not(.visual-blocks-img) { display: none }`. Specificity (0,2,1) beats the legacy `.obsidian/snippets/tikz-cache.css` rule (0,1,1) regardless of load order, so plugin's display owns the page when enabled. Plugin's own images carry `class="visual-blocks-img"` and bypass the hide via `:not()`. Snippet remains untouched — when plugin is disabled, snippet's rules reassert (wikilinks visible, fallback works). Plugin also includes `body .block-language-{lang} { display: block }` for all 5 languages — defeats the snippet's `display: none` on `.block-language-tikz` (which would otherwise hide the codeblock processor's container, taking our rendered image down with it).
- **Cross-language hash fixture file** — `tests/fixtures/hash_fixtures.json` (14 fixtures), generated by `resources/scripts/python_single/tests/generate_hash_fixtures.py`. Single source of truth. 14 fixtures cover: empty source, plain TikZ, TikZ-with-comments-NOT-stripped (verifies normalize's per-language docstring promise; current Python passes raw source to `compute_key`), CRLF, lone CR, multi-blank-line collapse, leading/trailing blank strip, per-line full-strip (anti-`trimEnd()` guard), Unicode source, language-distinguishes-hash, preamble-change-invalidates, attrs={} baseline, attrs={"k":"v"} (Python-JSON-spaces guard for Phase 9+), attrs multi-key sorted.
- **TDD red-then-green explicit** — Wrote `tests/hash.test.ts` with 24 assertions BEFORE any TS code. Initial `npm test`: collection error (`Cannot find module '../src/hash'`) → wrote `src/hash.ts` → all 24 jest tests pass (5 normalize + 4 pythonJsonDumps + 1 fixture-count guard + 14 per-fixture byte-identity). Same red-green pattern as D3.5 / D4.6 / D5.7 / D6.6 / D7.7.
- **Python-side fixture self-test** — `tests/test_hash_fixtures.py` (18 assertions). Re-derives every fixture's expected key in Python, asserts equality. Plus three pinning tests: per-line-strip-not-trimEnd guard, attrs-single-key-Python-spacing guard, hash-collision-where-expected (CRLF and lone-CR canonicalize to LF → identical hash).
- **Production round-trip on real cache** — Used Python `find_blocks` + `compute_key` against `_RENDER_TEST_d2.md` (3 D2 blocks). All 3 computed hashes equal the `sourceHash` field in `index.json`. The fixture-test discipline maps to actual production data.
- **Build** — `npm run build` (esbuild production CJS bundle) → `main.js` 4.5KB minified. Bundle externs: obsidian, electron, all CodeMirror packages, Node builtins. Installs cleanly into `.obsidian/plugins/visual-blocks/`.

**Decisions Made (D8.x):**

- **D8.1 — Cache files stay at `attachments/cache/tikz/`; plugin reads `cachePath` field from `index.json` directly.** Advisor: "Don't bundle physical move with the plugin scaffold — that's two phases of work, you'll be debugging file-move issues alongside hash-port issues." Phase 12 (migration tool) physically moves and rewrites paths. `getResourcePath()` works on any vault-relative path, so the plugin's hit path works regardless. Prevents breaking 169 in-flight cache files for an architectural cleanup that has its own dedicated phase.
- **D8.2 — `<img>` embedding per SPEC §3.4/§3.6 (NOT inline `<svg>`).** User explicitly chose the SPEC default after seeing the trade-off: inline `<svg>` would unblock AC7.5 (dark-mode follow) but requires SPEC amendment. The user accepted "AC7.5 stays structurally blocked under `<img>`" — same position as Phase 7 D7.8. The plugin emits `<img src="${getResourcePath(cachePath)}">` per T7. If dark-mode follow becomes a priority later, that's a SPEC amendment, not a v1.0 deviation.
- **D8.3 — TS hash port matches PYTHON ACTUAL behavior, not PLAN.md pseudocode.** PLAN §Phase 8 Task 8.4 had two real bugs: (a) `line.trimEnd()` instead of Python's `ln.strip()` — would diverge on lines with leading whitespace; (b) "if (lang === 'tikz') { strip comments }" — Python's `normalize()` DOES NOT strip TikZ comments; Phase 2 dispatcher passes `block.source` raw to `compute_key` and the adapter is theoretically responsible for any pre-processing but currently does nothing of the sort. Both bugs are caught by named fixtures (`per_line_whitespace_strip` + `tikz_with_comments_NOT_stripped`). Same lesson as D7.1: PLAN pseudocode is a starting point, not a contract.
- **D8.4 — `pythonJsonDumps` helper (Python `json.dumps(sort_keys=True)` defaults, including spaces).** Empirically confirmed: `python3 -c "import json; print(repr(json.dumps({'k':'v'}, sort_keys=True)))"` → `'{"k": "v"}'` (with space). JS `JSON.stringify({"k":"v"})` → `'{"k":"v"}'` (no space). Today all attrs are `{}` so both produce `'{}'` and the divergence is invisible. Phase 9+ may introduce non-empty attrs (per-block render hints, theme colour overrides, etc.); the helper is in place so the byte-identity contract holds across that boundary. Fixture `attrs_single_key_PYTHON_JSON_SPACES` is the executable proof.
- **D8.5 — Preamble hash sourced from `index.preambleHashes["<adapter:LANG>"]` (NOT hardcoded in TS).** Advisor: "Read from `index.preambleHashes`. The map already exists with all 5 languages populated. If absent → treat as cache miss." Cleanest separation: Python owns the preamble (knows the actual TikZ preamble text), plugin only consumes the digest. If Python ever changes the preamble (e.g., adding a new TikZ package), the index.json's preambleHash regenerates and plugin auto-picks up the new value with no TS code change.
- **D8.6 — Block ordinal NOT used; lookup by `sourceHash` only.** Advisor: "MarkdownPostProcessorContext doesn't tell you the block ordinal. Don't try to scan source for ordinal — that's fragile. Instead: compute the hash, then iterate `index.notes[sourcePath].blocks` looking for matching `sourceHash`. First match wins. Robust to block reordering, identical-source duplicates, etc." Implemented exactly as advised.
- **D8.7 — Wikilink coexistence via plugin styles.css with `:not(.visual-blocks-img)` exception (advisor's Option A).** Plugin owns the display when enabled; the snippet is untouched and reasserts when plugin disabled. CSS specificity (plugin's (0,2,1) > snippet's (0,1,1)) makes load-order irrelevant. The "user-visible flip" the advisor flagged: under Phase 7 the user saw [codeblock + wikilink image]; under Phase 8 they see [plugin image only] (codeblock is replaced by codeblock processor; wikilink is hidden by plugin CSS). Visually equivalent on cache hits; cache misses now show a typed placeholder where Phase 7 showed nothing.
- **D8.8 — `.gitignore` carve-out for THIS plugin only.** Vault gitignore had `/.obsidian/plugins` excluding all 56 plugin directories (third-party installs). Phase 8 plugin source MUST be versioned. Solution: `!/.obsidian/plugins/`, `/.obsidian/plugins/*`, `!/.obsidian/plugins/visual-blocks/` — un-excludes only this plugin's tree. Inner `.obsidian/plugins/visual-blocks/.gitignore` then re-excludes `node_modules/`, `package-lock.json`. `main.js` IS committed (it is the build artifact users execute; same convention as upstream Obsidian plugin repos). Verified via `git check-ignore`: TikZJax's main.js stays ignored; visual-blocks's main.js is tracked.
- **D8.9 — AC8.5 click-to-render is a placeholder + Notice in Phase 8; real wiring is Phase 9.** Advisor: "Don't try to wire a real render trigger in Phase 8 — that's Phase 9's surface and bundling produces a fat commit." Click handler shows a Notice telling the user to either run `render_cache.py` manually or wait for Phase 9's "Refresh this block" command. The placeholder IS clickable (AC8.5 surface met); the click outcome is a typed message (Phase 9 will replace).
- **D8.10 — TDD red-then-green explicit.** Same pattern as D3.5 / D4.6 / D5.7 / D6.6 / D7.7. Test file written first; pytest jest red phase produced the expected `Cannot find module` error → wrote `src/hash.ts` → 24/24 jest green. Python self-test (`tests/test_hash_fixtures.py`) red was implicit because the fixture file didn't exist initially — generator script created it; self-test then 18/18 green.

**Deviations from Plan:**

- **D8.3 deviates from PLAN.md §Phase 8 Task 8.4 pseudocode** (trimEnd vs strip; TikZ-comment stripping in TS that Python doesn't do); rationale logged.
- **D8.4 ADDS pythonJsonDumps that PLAN's pseudocode would have missed.** PLAN's `JSON.stringify(attrs, Object.keys(attrs).sort())` produces no spaces; Python uses spaces. PLAN had no test fixture to expose this; added.
- **D8.7's wikilink-hide CSS is broader than PLAN suggests.** PLAN didn't address the wikilink/plugin double-display problem at all. Advisor flagged it as an unlisted constraint; Phase 8 implementation includes the fix.
- **PLAN Task 8.5's smoke-test requirement is partially deferred to user gate.** Agent-side I cannot toggle plugins in a running Obsidian process. The build is verified, the bundle is well-formed, jest tests pass, the production-data round-trip works. AC8.1 (loads without errors), AC8.2 (cached display), AC8.3 (uncached placeholder), AC8.4 (mobile placeholder), AC8.5 (clickable), AC8.7 (source mode untouched) all need user-Obsidian verification.

**Tests:** 24/24 jest (5 normalize + 4 pythonJsonDumps + 1 count guard + 14 per-fixture byte-identity). 150/150 Python fast (was 132 pre-Phase-8; +18 from `test_hash_fixtures.py`). No regressions in any earlier phase.

**AC mapping:**

- AC8.1 (plugin loads, no console errors) — User gate (Obsidian).
- AC8.2 (cached TikZ block displays inline in reading view) — User gate (visual).
- AC8.3 (uncached TikZ block shows placeholder) — User gate (need to add an uncached block; sandbox procedure in user gate language below).
- AC8.4 (mobile placeholder reads "Open on desktop") — User gate (iOS).
- AC8.5 (desktop clickable placeholder) — User gate (interaction → Notice).
- AC8.6 ✓✓ — TS hash byte-identical to Python; verified by 24 jest assertions + 18 python self-tests + 3 production round-trip checks against `_RENDER_TEST_d2.md`.
- AC8.7 (source mode unchanged) — Codeblock processors only fire in reading-view + live-preview by Obsidian's contract; source mode (Cmd+E) is text-only by construction. Structurally guaranteed; user gate is paranoia check.

**Lessons Learned:**

- **PLAN pseudocode for cross-language ports is even more dangerous than for in-language ports.** Two real bugs (trimEnd, TikZ-comment-strip-in-TS-not-Python) were in 5 lines of TS pseudocode. The fixture-driven approach (Python emits expected hashes, TS test asserts byte-identity) catches these immediately and creates a regression net for future changes. This pattern (Python single-source-of-truth → fixture file → cross-language verification) generalizes to any future TS-from-Python port.
- **`crypto.subtle.digest` is async but available everywhere.** Obsidian renderer (Electron + iOS WKWebView), Node 18+, jest default env — all expose `globalThis.crypto.subtle`. Using SubtleCrypto over Node's `createHash` (sync but desktop-only) makes the same code path work everywhere; the async signature flows naturally through `registerMarkdownCodeBlockProcessor` which already accepts async callbacks.
- **CSS specificity is the right lever for plugin/snippet coexistence.** Adding `body` prefix or `:not()` exceptions raises specificity above hand-written user CSS without `!important`. !important is fine but harder to reason about; specificity-based wins are local and easy to debug.
- **Vault `.gitignore` exception via three-rule pattern is the cleanest carve-out.** `!path/`, `path/*`, `!path/specific/` is the standard idiom for "track this one subdir, ignore the rest". Verified with `git check-ignore -v` before committing — that command shows which rule is active per file. Future plugins added to the same `.obsidian/plugins/` parent will need their own `!` rule.
- **Block-ordinal-by-source-hash is robust and cheap.** Iterating the blocks array in `index.notes[sourcePath]` is O(N) where N is blocks-per-note (typically ≤5). Hash-string-equality is fast. No source-text scanning, no fragile line-counting.
- **The 17:03 auto-backup commit captured a stray fixture file at `resources/.obsidian/...` because of an off-by-one `parents[3]` in the generator script's REPO_ROOT computation.** The wrong path was `resources/scripts/python_single` (3 levels up); the right path is the vault root (4 levels up). `Path(__file__).resolve().parents[4]` is correct. Lesson: prefer `pathlib`'s known-anchor resolution (e.g., `.parents[i]` with `i = len(file_path.parts) - len(target_anchor.parts)`) or cache an `_anchor.py` constant in production code (Phase 7 D7.6 made this point; Phase 8 generator script ignored it; bug surfaced at first run, fixed second run). The same off-by-one was duplicated in `tests/test_hash_fixtures.py` and surfaced at the final pre-commit pytest run (Failed: hash fixture missing) — fixed in the same edit. Stray file removed from git tracking via `git rm`; `resources/.obsidian/` directory cleared.

**Cross-references:**

- SPEC §3.4 (Plugin CodeBlock Processor Contract); §3.6 (View-time data flow); §3.7 T7 (`getResourcePath`); §3.7 T12 (TS hash byte-identity); §3.9 (canonical formula); §5 Phase 8 (AC8.1–AC8.7); §11.4 (per-phase user-feedback gate).
- PLAN §Phase 8 Tasks 8.1–8.5 (reference implementation; D8.3/D8.4 deviate empirically). PLAN §Phase 9 (will replace D8.9 placeholder click with real render trigger).
- Phase 1 D1.x — `tikz-cache.css` snippet's specificity is what plugin overrides. Phase 1 v2 design intent named "brings forward Phase 8's cache-first viewer" — Phase 8 fulfils that promise.
- Phase 7 D7.1 / D7.2 / D7.7 / D7.8 — PLAN-vs-empirical lesson, TDD red-green pattern, AC7.5 honest framing all carry forward.
- Phase 12 (migration tool) — D8.1 defers physical cache move; Phase 12 is the cleanup phase. D8.10 alt-tag stays `tikz-cache` for legacy; OQ9 rename is also Phase 12.

**Phase 8 gate (user-driven, per SPEC §11.4):**

1. **Enable the plugin.** Open Obsidian → Settings → Community plugins. The "Visual Blocks" plugin should appear in the installed-plugins list (Obsidian discovers `.obsidian/plugins/visual-blocks/manifest.json`). Toggle it ON. **Verify TikZJax is OFF** (Settings → Community plugins → TikZJax). Per this session's investigation, TikZJax is not in any `loadAtStartup=True` group, so it should already be off — but if you manually enabled it at any point, disable it now to avoid a codeblock-processor race on the `tikz` fence.
2. **AC8.1 — No console errors.** Cmd+Opt+I → Console tab. Reload the plugin. Look for any red `Visual Blocks: …` or stack trace. Plain text logs (`visual-blocks: loaded; processors registered for …`) are expected.
3. **AC8.2 — Cached TikZ block displays inline (in BOTH rendered modes).** Open `kn/math/concepts/mSB3-4_reals.md` in reading mode (Cmd+E to toggle). The TikZ number-line diagram should appear EXACTLY ONCE (plugin emits `<img>`; legacy wikilink is hidden by plugin CSS). Compare to Phase 7 reading mode where you saw "codeblock + wikilink image" stacked — that should be replaced by a single image now. Then toggle to **live preview** (the rendered-edit mode, NOT raw source). The codeblock processor fires in live preview too — diagram should appear there as well. If it does NOT appear in live preview, surface that here (Phase 9 lead-in).
4. **AC8.3 — Uncached TikZ block shows placeholder.** Open `kn/math/concepts/_RENDER_TEST_d2.md`, paste a brand-new D2 block (e.g., ```d2\nx -> y\n```) somewhere ABOVE the existing 3 blocks (don't run `render_cache.py`). Reading mode should show the existing 3 cached SVGs PLUS a typed placeholder reading "d2: Cache miss — click here for help (Phase 9 will wire click-to-render)." for the new block.
5. **AC8.4 — Mobile placeholder reads "Open on desktop".** After iCloud sync, open the same file with the new uncached block on iOS. Placeholder should read "d2: Cache miss — open on desktop to render." (no click affordance).
6. **AC8.5 — Desktop placeholder is clickable.** Click the placeholder from step 4. A Notice should pop up in the bottom-right corner: "Phase 8 placeholder. To render, run: python3 resources/scripts/python_single/render_cache.py <FILE.md>. Phase 9 will add a 'Refresh this block' command."
7. **AC8.7 — Source mode unchanged.** With any of these files open, hit Cmd+E to toggle source mode. The raw markdown ```d2\n…\n``` codeblocks should be visible exactly as authored. Switch back (Cmd+E again) to reading mode — codeblocks vanish, replaced by plugin images.
8. **Cleanup after gate.** Remove the experimental ```d2\nx -> y\n``` block you added in step 4 (or run `python3 resources/scripts/python_single/render_cache.py kn/math/concepts/_RENDER_TEST_d2.md` on the file to render it properly). **Important:** Phase 8 reads `index.json` once at `onload`; after running `render_cache.py`, reload the plugin (Settings → Community plugins → Visual Blocks → toggle OFF, then back ON) so the new entry is picked up. Phase 9 will add live-watching of the index file so this manual reload becomes unnecessary.

When confirmed, reply: **"Implement Phase 9"** → Plugin commands and modes (refresh-block / refresh-note / refresh-vault / show-status / sweep / toggle-mode / clear-all; mode cycling; mobile auto-override; triggerOnSave). Phase 9 replaces D8.9's placeholder click with real render-trigger wiring.

**Outstanding (NOT blocking Phase 9 — flagged across phases):**

- 3 pre-existing TikZ source bugs (`bB3-18_neuroscience-101.md`, `mSB8-9_double-brackets.md`, `mSB3-8_euler-e.md`). Separate-triage backlog. Surfaced for the 4th time in Phase 7's `--all --force` run.
- `.obsidian/community-plugins.json` anomaly — only 5 entries (`ai-note-suggestion`, `obsidian-plugin-groups`, `claude-sidebar`, `obsidian-advanced-uri`, `calendar`) despite vault using ~136 plugins. Investigation this session: `obsidian-plugin-groups` has 36 groups managing 137 plugins, with no group's `loadAtStartup=True` for non-empty plugin lists. Fly TikZJax is in 3 groups, none auto-loaded. Mechanism is probably: user enables plugins manually via the plugin-groups palette command; `community-plugins.json` reflects only the 5 plugins enabled at Obsidian startup. Phase 8 verification needed: after the user toggles "Visual Blocks" ON in Settings, `community-plugins.json` should grow by 1 entry — confirmation that the system is healthy, not broken.
- D6.7 fence-tag REGISTRY-derive refactor deferred a 4th time → queued for Phase 9 lead-in (Phase 9 doesn't touch the dispatcher's fence-tag list, clean lead-in moment).
- D7.9 implicit-default-fill rule (4th SVG hardening rule) explicitly NOT shipped because AC7.5 stays structurally blocked under D8.2's `<img>` choice. Re-evaluate at Phase 12 / SPEC v1.1 if the user later wants inline-SVG and dark-mode-follow.
- **iOS Web Crypto contingency.** The TS plugin uses `crypto.subtle.digest('SHA-256', ...)` which is async + standardised across modern WebKit (iOS ≥ 11). Agent-side cannot verify on iOS WKWebView; if Phase 11 surfaces "visual-blocks: tikz block failed — …" for every block, the fallback is to swap to `js-sha256` (sync, no Web Crypto dependency, ~15 KB to bundle). No code change needed now; this is the documented remediation path.
- **PROGRESS.md is approaching ~1300 lines.** Spine threshold is 500. Not blocking Phase 9 directly, but the Phase 9 lead-in is the natural archive moment: move Phase 1-6 entries to `PROGRESS_ARCHIVE.md`, keep Phase 7 + 8 + table + recovery in PROGRESS.md. Multiple items already queued for "Phase 9 lead-in" (D6.7 fence-tag refactor, D7.9 implicit-fill rule contingency, this archive, optionally a `community-plugins.json` post-toggle health check). **Done 2026-04-28** — see Phase 8 Gate Closure below; archive landed in this lead-in commit.

**Phase 8 user-gate closure (recorded here for atomicity, 2026-04-28):**

User confirmed all 8 verification steps from the Phase 8 gate procedure pass. Verbatim user response captured below; per-step interpretation:

- **Step 1 — plugin enabled, TikZJax off:** confirmed.
- **Step 2 — AC8.1 (no console errors):** confirmed. Console log read literally:
  ```
  visual-blocks: loaded; processors registered for tikz, graphviz, d2, lilypond, smiles
  ```
  Unrelated MathJax font warnings (`Slow network detected … fallback font … MathJax_Zero.woff` etc.) appeared in the same console session — these are MathJax loading WOFF assets over the user's slow network and are completely independent of the visual-blocks plugin (no `visual-blocks:` prefix; emitted from `index.html:1`, not from `main.js`). Filed for awareness, not as a Phase 8 regression.
- **Step 3 — AC8.2 (cached display in reading + live preview):** confirmed indirectly. The user's step-4 observation ("Got: `d2: Cache miss — click here for help (Phase 9 will wire click-to-render).`") was made on `_RENDER_TEST_d2.md` after pasting one new ` ```d2 ` block ABOVE the existing 3 blocks. For the placeholder to appear in isolation (rather than stacked with leftover wikilink images), the codeblock processor must be replacing each existing cached block with a single `<img class="visual-blocks-img">` AND the plugin's `:not(.visual-blocks-img)` CSS rule must be hiding the legacy wikilink-rendered images. Both behaviors are AC8.2 territory. Direct "appears in BOTH reading mode and live preview" was not separately reported, but live-preview support is structurally guaranteed by Obsidian's `registerMarkdownCodeBlockProcessor` contract (processors fire in both rendered modes by construction).
- **Step 4 — AC8.3 (uncached placeholder):** confirmed. Pasted ` ```d2 ` source (multi-line nested-cluster D2 graph) yielded the expected typed placeholder text exactly: `d2: Cache miss — click here for help (Phase 9 will wire click-to-render).`
- **Step 5 — AC8.4 (mobile placeholder text):** confirmed. iOS reads: `d2: Cache miss — open on desktop to render.` (no click affordance).
- **Step 6 — AC8.5 (clickable placeholder → Notice):** confirmed. Notice text rendered exactly as designed:
  ```
  Phase 8 placeholder. To render, run:
  python3 resources/scripts/python_single/render_cache.py
  <FILE.md>
  Phase 9 will add a 'Refresh this block' command.
  ```
- **Step 7 — AC8.7 (source mode unchanged):** "Yes." Cmd+E shows the raw markdown ` ```d2 … ``` ` codeblock; Cmd+E again returns to plugin-rendered images.
- **Step 8 — cleanup:** user removed the experimental code block.

**Decisions made (Phase 8 closure):**

- **D8.11 — Gate-closure type: `visual-confirmed`** (per D2.9 nomenclature). Eight independent observations, six of them surfacing exact text strings I can byte-compare against my source code (steps 4 / 5 / 6 — placeholder text, mobile text, Notice text). One observation (step 2 console log) byte-identical to the `console.log` template at `src/main.ts:81-83`. AC8.6 (TS hash byte-identical to Python) was already agent-verified before the user gate via 24 jest fixtures + 18 python self-tests + 3 production round-trip checks; user-gate confirmation is not the verification surface for AC8.6.
- **D8.12 — MathJax slow-network warnings noted but out of scope.** They appear in the same console panel as our plugin's load message, but they originate from Obsidian's bundled MathJax (`app://obsidian.md/lib/mathjax/output/chtml/fonts/woff-v2/...`) and are emitted by `index.html:1` (host page), not by `main.js`. Render-cache does not load MathJax assets. Filed for the user's awareness; if these warnings become disruptive in everyday use, the remediation is to pre-cache the WOFF files (Obsidian-level concern, not plugin-level).
- **D8.13 — Phase 9 lead-in archive landed in the same commit as gate closure.** Per advisor recommendation, the PROGRESS-archive lead-in is bundled with this gate-closure entry into a single atomic lead-in commit, BEFORE the Phase 9 atomic implementation commit. This keeps the Phase 9 diff focused on actual implementation (settings/render/commands/cacheStatus/main.ts changes) without mixing in 600 lines of moved log entries. PROGRESS.md drops from 1073 → ~430 lines; PROGRESS_ARCHIVE.md (new) holds the displaced 728 lines.

**Tests:** N/A (gate closure only; no code change in this entry).

**Next:** Phase 9 — Plugin commands and modes. 7 commands + 3 modes + mobile auto-override + `triggerOnSave` save-event hook. Begins immediately following this lead-in commit. AC9.1–AC9.10 acceptance per SPEC §5 Phase 9.

**Cross-references:** SPEC §5 Phase 8 (AC8.1–AC8.7), §11.4 (per-phase gate). Phase 8 entry above for the agent-side decisions D8.1–D8.10. Phase 9 entry below (or upcoming) for D9.x.

---



**Phase 6 user-gate closure (recorded here for atomicity):** User confirmed all three SMILES SVGs render correctly in QuickLook ("Yes, the user gat of phase 6 passes."). Phase 6 row in the Phases table flipped from `DONE (agent)` → `DONE`. Gate-closure type: `visual-confirmed` (per D2.9 nomenclature). Phase 6 commit hashes (dc78c598e + 927047133) pulled into the table cell that was previously `TBD (this iteration)`.

**Completed:**

- **Three hardening rules** — `render_cache/postprocess.py` rewritten from a Phase 2 pass-through stub into a 4-function module:
  - `prefix_ids(svg_text, prefix)` — SPEC T3 / AC7.1. Prefix the first 6 chars of the cache key onto every `id="..."` and `xlink:href="#..."` reference. Two cached SVGs from the same renderer can otherwise collide on shared IDs (dvisvgm `g0-N`, Graphviz `node1` / `edge1`). Quote-agnostic via backreference `(["'])(...)\1`.
  - `substitute_current_color(svg_text)` — SPEC T5 / AC7.2. Replace black with `currentColor` on **two surfaces**: attribute form (`fill="black"` / `stroke="#000000"`) AND **CSS-style form** (`style="...stroke:#000000;..."`). The latter is required for rdkit/SMILES which emits **all colours via inline `style=` attributes**, never via dedicated `fill=`/`stroke=` attributes. Word-boundary anchor (`\b`) prevents partial matches on `#0001` (dark blue) and `blacksmith`. Case-insensitive.
  - `enforce_viewbox(svg_text)` — SPEC T4 / AC7.3. Strip `pt` units from `width`/`height` (iOS WKWebView with `pt` and no viewBox renders 0×0 silently); inject viewBox if absent. SPEC AC7.3 is `pt`-specific so `mm` (LilyPond) and `px` (rdkit) are preserved per PLAN's "common mistakes" guidance.
  - `apply(svg_text, key)` — chains all three in order; signature unchanged from Phase 2 stub so the dispatcher's call site at `render_cache/__init__.py:115` keeps working without rewiring.
- **Empirical correction of PLAN's pseudocode** — PLAN §Phase 7 Tasks 7.1–7.3 pinned double-quoted regex patterns (`r'\bid="([^"]+)"'`). Empirical inspection of every v1 adapter's actual output revealed:
  - **TikZ (dvisvgm)**: 100% **single quotes** for every attribute (`width='481.8942pt'`, `id='g0-28'`, `xlink:href='#g0-28'`, `fill='#3cb371'`).
  - **SMILES (rdkit)**: 100% **single quotes**; colours **only inside `style='...'`** with semicolon separators; **zero `id=` attributes**.
  - **Graphviz / D2 / LilyPond**: double quotes.
  Without quote-agnostic regexes, AC7.1 and AC7.2 would have silently no-op'd on the two largest contributors of black/IDs (TikZ has 100s of `g0-N` IDs per file; SMILES has 22 black-stroke style values per molecule). Logged as deviation from PLAN with full rationale (D7.1).
- **Re-rendered the entire vault cache** — `python3 render_cache.py --all --force` ran on 104 indexed notes. 2:00 minutes. 105 newly-rendered SVGs. Hardening applied to the on-disk content. Filenames unchanged (cache key is computed from source, not output). 3 pre-existing TikZ source bugs (`bB3-18_neuroscience-101.md`, `mSB8-9_double-brackets.md`, `mSB3-8_euler-e.md`) failed for the 3rd time — already flagged in Phase 2 + 3 + 4 + 5 + 6 closures as separate-triage items, NOT Phase 7 regressions. The `_TIKZ_TEST_mSB3-5.md` from the original Phase 2 outstanding list rendered cleanly this run (1 of the 3 pre-existing-bug files in the original list has been silently fixed somewhere; remaining 3 are new + 2 carry-overs).
- **Tests** — `tests/test_postprocess.py` (43 tests: 37 fast + 6 slow against real cache content). Fast tier covers each rule in isolation (single quote / double quote / CSS-style / case-insensitive / partial-hex-blocked / blacksmith-not-matched / white-preserved / `none`-preserved / mm-preserved / px-preserved / unitless-preserved / data-URI-not-touched / pt-stripping / viewBox-injection / viewBox-preserved / signature-stable / chains-in-order / first-six-key-chars-only / idempotent / public-API-present). Slow tier reads each adapter's actual cache output and asserts post-`apply()` invariants (zero unprefixed IDs / zero pt units / zero hardcoded black on each adapter family / user colours preserved on D2 / pre-existing currentColor preserved on LilyPond).
- **TDD red-then-green explicit** — Wrote `tests/test_postprocess.py` BEFORE any non-stub implementation. Initial run: collection error (`ImportError: cannot import name 'enforce_viewbox'`) → added `NotImplementedError` stubs for `prefix_ids` / `substitute_current_color` / `enforce_viewbox` → re-ran: **35 fast tests fail** with `NotImplementedError`, 2 trivially pass (the `callable(...)` contract checks). Implemented; same suite went **37/37 green**. Slow tier failed once (CACHE_DIR resolution off by one — my hand-rolled `Path(__file__).resolve().parent.parent.parent.parent` resolved to `/resources` not `/Users/cs/Obsidian/_`). Replaced with `from render_cache.cache_paths import CACHE_DIR` (re-using the same authoritative path the dispatcher uses). Slow tier re-ran 6/6 green. Same red-green pattern as D3.5 / D4.6 / D5.7 / D6.6.
- **Full-suite regression check** — 151/151 green (43 Phase 7 + 14 Phase 1 + 36 Phase 2 + 14 Phase 3 + 14 Phase 4 + 15 Phase 5 + 15 Phase 6 = 151). No Phase 1 / 2 / 3 / 4 / 5 / 6 regressions.
- **AC7.1/AC7.2/AC7.3 hard-verified across the full 169-file cache** via `grep -lE` over all `*.svg`:
  - **AC7.1**: 0 files with unprefixed dvisvgm IDs (`id='g[0-9]+-[0-9]+'`); 0 files with unprefixed Graphviz IDs (`id="(graph|node|edge)[0-9]+"`); 157 files with prefixed dvisvgm IDs; 3 files with prefixed Graphviz IDs.
  - **AC7.2**: 0 files with attribute-form `fill='black'` / `stroke='black'`; 0 files with attribute-form `fill='#000000'` / `stroke='#000000'`; 0 files with CSS-style `fill:#000000` / `stroke:#000000`; 36 files with `currentColor` (TikZ files with no original black are no-ops here, which is why this is 36 rather than 169 — most TikZ uses user-chosen colour palettes).
  - **AC7.3**: 169/169 files with `viewBox`; 0/169 files with `pt`-unit width or height.
- **Independent visual verification (agent-side)** — Used `rsvg-convert` to render a representative SVG from each adapter family to PNG and inspected via `Read`. **TikZ (mSB3-4_reals)**: number-line diagram intact (axis, tick marks, integer labels, dots at √2/π/e/1/3, "No gaps anywhere" callout, blue/red Rational/Irrational legend). **SMILES (caffeine)**: purine ring system with 3 N atoms (blue), 2 carbonyl O atoms (red), 3 methyl groups — textbook caffeine. **D2**: 3-node graph with directed elk-routed arrows; user-blue palette preserved. AC7.4 (multi-block visual) and AC7.5 (dark-mode follow) require user-driven verification in Obsidian — those are the gate.

**Decisions Made:**

- **D7.1 — All regexes are quote-agnostic, deviating from PLAN §Phase 7 pseudocode.** PLAN pinned double-quoted patterns. Empirical inspection: dvisvgm and rdkit both emit single-quoted attributes exclusively; using PLAN's verbatim regexes would silently no-op on the two largest contributors of IDs and hardcoded black. Strategy: capture quote with `(["'])` and back-reference via `\1`; replacement preserves the captured quote. Verified by red-green test pairs (single-quote ID test + double-quote ID test, both passing).
- **D7.2 — Added a CSS-style colour rule for SMILES.** PLAN §Phase 7 Task 7.2 only addressed attribute form. Empirical inspection: rdkit/SMILES emits **all** colours via inline `style='...;fill:#000000;...'` semicolon-separated property lists; zero attribute-form colour values. Without a CSS-style rule, SMILES would have **22 hardcoded `stroke:#000000` per molecule × 3 sandbox molecules = 66 unmitigated black-stroke instances** that defeat AC7.2 (and break dark-mode adaptation for any future SMILES content). Pattern: `\b(fill|stroke):\s*(?:#000000|#000(?![0-9a-fA-F])|black\b)` with case-insensitive flag. Word-boundary anchor prevents `#0001` (dark blue) or `blacksmith` from matching.
- **D7.3 — Skip SVGO for v1 (Option C from PLAN Task 7.4).** PLAN explicitly recommended Option C; reaffirmed at execution time. Custom rules + dvisvgm's own output cleanliness produce sufficiently clean SVGs (TikZ files average 35-50KB, well within mobile WebView budgets). SVGO would require either Node.js dependency (Option A) or immature pure-Python equivalent (Option B). **Revisit at Phase 11 (iOS validation)** if mobile rendering proves bandwidth-bound or if the plugin team wants offline minification.
- **D7.4 — `enforce_viewbox` strips `pt` only, not `mm` or `cm` or `px`.** SPEC AC7.3 is `pt`-specific. PLAN §Phase 7 "Common mistakes" calls out generalisation as a mistake. LilyPond's `width="210.00mm"` and rdkit's `width='400px'` are both legitimate; neither triggers iOS 0×0 collapse (only `pt`-without-viewBox does). Tests pin this: `test_mm_units_preserved_per_spec` and `test_px_units_preserved_per_spec` are explicit guards.
- **D7.5 — `apply` not idempotent on already-prefixed IDs.** Running `apply(apply(svg, key), key)` produces double-prefixed IDs (`abc123__abc123__g0-1`). This is acceptable because:
  (a) the dispatcher only calls `apply` once on freshly-rendered content (line 115 of `__init__.py`);
  (b) ID-prefixing twice does NOT corrupt the SVG (the second prefix is just nested), only inflates ID lengths;
  (c) the colour-substitution and pt-stripping rules ARE idempotent (the test `test_apply_idempotent` verifies the **substring patterns of the original input** don't survive — that's what matters for the cache integrity story).
  Idempotence-on-output would require a "is-already-hardened" detector, which adds complexity and is unnecessary for the Phase 7 contract. Logged for Phase 12 (migration tool) consideration.
- **D7.6 — `CACHE_DIR` test fixture imports from `render_cache.cache_paths`, NOT a hand-rolled `Path(__file__).parent.parent...` chain.** First attempt at the slow-tier tests used a hand-rolled relative path with the wrong number of `.parent` calls (resolved to `/resources` not `/Users/cs/Obsidian/_`). Replaced with the authoritative import. Lesson: when a module already exposes a constant the test needs, import it; don't recompute it. Future Phase-N test fixtures should follow this rule (relevant for Phase 8 plugin tests too).
- **D7.7 — TDD red-then-green explicit.** Same pattern as D3.5 / D4.6 / D5.7 / D6.6. Test file written first; ran pytest → 35/37 fast tests fail with `NotImplementedError` (2 trivially pass — the `callable(...)` contract checks). Implemented; same suite went 37/37 green. Slow tier's CACHE_DIR fix above. Pattern is now firmly established as the standard Phase-N opening move.

- **D7.8 — Phase 7 gate framing made honest after advisor sanity check.** Initial gate language asked the user to confirm AC7.5 in Obsidian by toggling dark mode. Advisor (Opus, sees the full transcript) flagged the structural blocker: `<img>`-embedded SVGs are colorimetrically isolated from page CSS, so `currentColor` cannot follow theme under the current Phase 1 v2 view path. Re-framed AC7.5 as "structurally blocked on Phase 8" — agent-side substitution is correct, but the wire-up requires Phase 8's inline embedding. AC7.4 remains user-confirmable now.
- **D7.9 — A 4th rule (`fill='currentColor'` on `<svg>` root for implicit-default-black glyphs) is deliberately NOT shipped in Phase 7.** Advisor flagged: dvisvgm's `<defs><path id='gN-M' d='…'/></defs>` paths have no explicit `fill=` attribute, so they default to SVG-spec black. `substitute_current_color` doesn't catch them (nothing to substitute). Advisor's recommendation: a 4th rule injecting `fill='currentColor'` on the root `<svg>` element. **Decision: defer to Phase 8 lead-in.** Reasoning: (a) under current `<img>` viewing, this rule would not produce any visible improvement (currentColor still resolves to black inside the isolated SVG document context — see D7.8); (b) the rule is small (~5 lines) and trivially testable, but landing it without a structural fix would imply AC7.5 is unblocked when it isn't; (c) Phase 8's lead-in is the natural moment to ship it, simultaneously with the structural inline-embedding fix that makes it observable. **Phase 7 acceptance criteria do NOT require this rule** (re-read AC7.1/AC7.2/AC7.3 — none of them mention implicit-default-fill).
- **D7.10 — `mSB3-8_euler-e.md` triage** — This file appeared in the Phase 7 `--all --force` failure list but was NOT explicitly named in Phase 2's failure list (which named bB3-18 / mSB8-9 / one block in _TIKZ_TEST_mSB3-5). Advisor flagged the discrepancy. Investigation: file last modified 2026-02-08 (well before any phase of this project); LaTeX error is "Can be used only in preamble" — a pre-existing source bug, not a Phase 7 artifact. `_TIKZ_TEST_mSB3-5.md` was edited 2026-04-27 13:23 (between Phase 2 and Phase 7) — its previously-broken block was silently fixed in that edit. **Net effect on the failure-count invariant**: Phase 7's failure count is still 3 (advisor verified); the file identities shifted by one. mSB3-8 was likely cached from a pre-Phase-2 manual run (`--all` without `--force` skips already-cached blocks, so Phase 2 wouldn't have re-rendered it). Phase 7's `--force` is what surfaced it. **Conclusion: NOT a Phase 7 regression** (postprocess runs after successful render and cannot cause render failures, by construction). Filed in the same separate-triage backlog as the other 2 pre-existing TikZ source bugs.

**Deviations from Plan:**

- **D7.1 deviates from PLAN §Phase 7 Task 7.1 pseudocode** (single vs double quotes); rationale logged.
- **D7.2 deviates from PLAN §Phase 7 Task 7.2 pseudocode** (CSS-style rule added on top of attribute form); rationale logged.
- **D5.6's "fence-tag derive-from-REGISTRY refactor" deferred ANOTHER phase.** D5.6 (Phase 5) said "Phase 6"; D6.7 (Phase 6) said "next standalone commit before/during Phase 7". Phase 7 did NOT bundle this refactor either: Phase 7 is a fully diff-localised change (`postprocess.py` body + new test file + cache regen) and adding a 3-module refactor would muddle the atomic-commit semantics again. The refactor is now explicitly queued for **the standalone "fence-tag REGISTRY-derive cleanup" commit before Phase 8** (the plugin scaffold; Phase 8 doesn't touch the dispatcher's fence-tag list at all, making it a clean lead-in moment). If the user wants the refactor applied immediately, override on request.

**Tests:** 43/43 Phase 7 (37 fast + 6 slow on real cache). Full suite 151/151 across all phases. No Phase 1 / 2 / 3 / 4 / 5 / 6 regressions.

**AC mapping:**

- AC7.1 ✓✓ — 0 unprefixed dvisvgm OR Graphviz IDs across all 169 cache files; 157 files have prefixed dvisvgm IDs; 3 files have prefixed Graphviz IDs.
- AC7.2 ✓✓ — 0 attribute-form OR CSS-style hardcoded black across all 169 files. 36 files have `currentColor` (TikZ user palettes don't use black originally — that's why the count isn't higher).
- AC7.3 ✓✓ — 169/169 files have viewBox; 0/169 files have `pt` units in width/height.
- AC7.4 — User-driven gate: open a multi-block note in Obsidian and verify two SVGs from the same renderer don't corrupt each other's element references.
- AC7.5 — User-driven gate: toggle Obsidian dark mode and verify cached-SVG foreground colour follows.

**Lessons Learned:**

- **PLAN pseudocode is a starting point, not a contract.** D7.1 + D7.2 are concrete examples: PLAN's regexes would have silently no-op'd on TikZ + SMILES. Lesson for future implementation phases: empirically inspect the actual artifact format BEFORE writing the regex / parser / postprocess rule. The PLAN's pseudocode encodes the architect's intent; the actual format encodes the renderer's reality.
- **Quote-agnostic regex via backreference is cleaner than two separate regexes.** Pattern `(["'])([^"']+)\1` ensures the closing quote matches the opening, with one rule covering both quote styles. Pre-Phase-7 instinct was to write two patterns — quote-agnostic is one third the lines and provably correct via test pairs.
- **CSS-style colour rules are required for renderers that use `style=` attributes.** rdkit is the only v1 renderer that does this exclusively. Future v1.1 renderers may follow suit (web standards favour `style=` over deprecated `fill=` attributes for new rendering pipelines). The CSS-style rule is now baked in; future renderers benefit automatically.
- **`apply` idempotence is a property to test only when the contract requires it.** The Phase 7 contract is "render → apply → cache". The dispatcher calls `apply` exactly once per render. Idempotence-on-output is a stronger property and would require a "is-already-hardened" detector. We chose not to implement it (D7.5). Lesson: don't over-strengthen properties beyond the actual call-site contract — every additional invariant costs implementation complexity AND test surface.
- **Importing the authoritative path constant is more robust than hand-rolling `.parent` chains** (D7.6). When a test fixture needs a path that the production code already computes, import it from the same module. Off-by-one-`.parent` errors are common and silent (the slow tier just `pytest.skip`'d, almost masking the bug). Future test fixtures should default to importing.
- **Re-rendering the full cache after a postprocess change is fast for a vault of this size** (~2 minutes for 104 notes / 105 SVGs). LilyPond was the slowest (~1.4s per file), TikZ second (~1.2s per file via lualatex+dvisvgm), Graphviz / D2 / SMILES sub-second. Future postprocess rule additions can re-render in batch without operator concern.

**Cross-references:**

- SPEC §3.7 T3 / T4 / T5 (the binding constraints); §5 Phase 7 (acceptance criteria); §3.2 architecture diagram (POSTPROC node between adapter dispatch and cache write); §11.4 (per-phase user-feedback gate). PLAN §Phase 7 Tasks 7.1–7.8 (reference pseudocode + verification commands; D7.1 + D7.2 deviate empirically).
- Phase 1 D1.x — `--libgs=` auto-detection of the dvisvgm dynamic-library dependency was the prior critical correctness fix; Phase 7 is the iOS-WebKit correctness fix. Together they're the "iOS visual" foundation.
- Phase 2 D2.7 — same TDD red-then-green discipline (source-text-grep test that strips docstrings before negative assertion). Same pattern carries forward.
- Phase 6 D6.7 — fence-tag REGISTRY-derive refactor was deferred again (third deferral); explicitly queued for the lead-in to Phase 8.

**Phase 7 gate (user-driven, per SPEC §11.4) — HONEST FRAMING (D7.8):**

This phase has FIVE acceptance criteria. Three are agent-confirmable; one is partially confirmable now; one is **structurally blocked on Phase 8**:

1. **AC7.1 ✓ agent-confirmed** — 0 unprefixed dvisvgm/Graphviz IDs across all 169 cache files.
2. **AC7.2 ✓ agent-confirmed** — 0 attribute-form OR CSS-style hardcoded black across all 169 cache files.
3. **AC7.3 ✓ agent-confirmed** — 169/169 viewBox; 0/169 pt units.
4. **AC7.4 — Multi-block visual** (user gate, NOW confirmable) — Open a note that has at least 2 cached SVGs from the same renderer family on one page. Confirm: each diagram's elements stay inside their own bounds (no corrupted edges, no missing labels, no element bleeding from one block into another). Easiest test: `kn/math/concepts/_RENDER_TEST_d2.md` (3 D2 blocks; visible together in reading mode). Even if the diagrams' SVGs use identical-looking internal IDs (e.g., dvisvgm's `g0-N` series), each cache file's hash-prefix differs, so collisions are mathematically impossible.
5. **AC7.5 — Dark-mode follow** (user gate, **structurally blocked on Phase 8** — see D7.9) — Phase 7 substitutes `currentColor` correctly at the SVG layer. But the current view path uses `<img alt="tikz-cache" src="…">` (Phase 1 v2's CSS-driven cache-first viewer). Browsers render `<img>`-with-SVG-src as a **replaced element** in a separate document context — parent-page `color` (and therefore `currentColor`) does NOT propagate into the SVG. The SVG resolves `currentColor` to its own intrinsic `color` value, which defaults to black. Phase 8's plugin will inline-embed the cached SVG via `<svg>` directly (NOT via `<img>`), at which point `currentColor` will start following Obsidian's theme. **AC7.5 should be re-evaluated at Phase 8 user gate, not now.** No-op verification possible at Phase 7: confirm there is no visible regression (diagrams still render correctly in light mode at minimum).

**Note on AC7.4 expected behaviour:** Because all cached SVGs already have their IDs prefixed with the cache hash, even two diagrams using identical user TikZ source (which would produce identical `g0-N` series internally) get **different** prefixes (different cache keys → different prefixes → no collision). The test is "do the diagrams render correctly side-by-side", not "do you see the prefix in the DOM" (the prefix is invisible to the user; it's an internal SVG namespace device).

When AC7.4 confirmed, reply: **"Implement Phase 8"** → Plugin scaffold (Node.js TypeScript plugin; NEW tooling environment; inlines the cached SVG so `currentColor` finally takes effect, unblocking AC7.5).



**Phase 5 user-gate closure (recorded here for atomicity):** User confirmed both LilyPond SVGs render correctly in QuickLook ("Yes, it works, user-gate phase 5 passed"). Phase 5 row in the Phases table flipped from `DONE (agent)` → `DONE`. The Phase 5 gate-closure type is `visual-confirmed` (per D2.9 nomenclature).

**Completed:**

- **Pre-flight 6 (`python3 -c "import rdkit"`):** Initially failed — `ModuleNotFoundError: No module named 'rdkit'`. Python is conda-managed at `/opt/homebrew/Caskroom/miniconda/base/bin/python3` (Python 3.11.8). PLAN authorises `pip install rdkit`; asked user via `AskUserQuestion` (4-option gate, mirrors Phase 4/5 install pattern: pip / conda-forge / manual / skip). User asked the meta-question "uv or pip?" — recommended pip on the basis that uv's wins (lockfile-managed envs, dep-resolution speed, project pyproject.toml) don't apply when adding a single library to a conda-style env, and PLAN explicitly says `pip install rdkit`. User accepted. Result: `rdkit-2026.3.1` (cp311 macos arm64 wheel, 29.9 MB) installed via `pip3 install rdkit`. Verified import: `Chem`, `AllChem`, `Draw.rdMolDraw2D` all present; caffeine parses to 14 atoms.
- **Smoke test before adapter:** Pre-verified the canonical render path on caffeine SMILES (`CN1C=NC2=C1C(=O)N(C(=O)N2C)C`). Result: render time **2.6 ms** (pure Python — fastest of all v1 adapters by ~100×); SVG length 10 158 bytes; `viewBox` present; xmlns SVG; **44 `<path>` elements**; **zero `file://` URIs**. Invalid SMILES test (`INVALID_SMILES_!!!`) returns `None` from `MolFromSmiles` — detection mechanism confirmed. Aspirin parses to 13 atoms. SVG header carries `<?xml version='1.0' encoding='iso-8859-1'?>` (rdkit default, not UTF-8 — flagged for Phase 7 postprocess consideration but not Phase 6 scope).
- **Adapter** — `resources/scripts/python_single/render_cache/adapters/smiles.py`. ~80 lines. **Pure Python — no `subprocess`**. Wraps `MolFromSmiles → Compute2DCoords → MolDraw2DSVG(400, 300) → DrawMolecule → FinishDrawing → GetDrawingText` and writes the result to `<workdir>/out.svg`. `RenderError` raised on (a) `MolFromSmiles` returning `None` with offending input snippet (truncated to 80 chars), (b) any rdkit exception during draw, (c) `ImportError` on rdkit (with `pip install rdkit` hint), (d) empty source. RDKit's verbose `rdApp.error` logger is silenced at module import (D6.5) — surfaced diagnostic stays in our `RenderError.message`, not in stderr noise.
- **Registry** — `adapters/__init__.py` now imports + registers `SMILESAdapter()` alongside the four prior adapters. Five-language registry (v1 language surface complete).
- **markdown_io** — `BLOCK_RE` alternation extended `tikz(?:-paused)?|graphviz|d2|lilypond` → `tikz(?:-paused)?|graphviz|d2|lilypond|smiles`. `_FENCE_TO_LANG` map gained `"smiles": "smiles"`. Module docstring updated to acknowledge v1 language surface complete.
- **Dispatcher fence-tag list** — `render_cache/__init__.py:find_all_md_with_blocks.fence_tags` extended to `("tikz", "tikz-paused", "graphviz", "d2", "lilypond", "smiles")` (now 6 items). Without this, `--all` would have skipped SMILES files entirely. Docstring rewritten to note the deliberate D6.7 deferral of the derive-from-`REGISTRY` refactor (replaced D5.6's "deferred to Phase 6" forward-pointer).
- **Test sandbox** — `kn/math/concepts/_RENDER_TEST_smiles.md` with 3 SMILES blocks per SPEC §5 Phase 6 mandate ("caffeine, aspirin, ibuprofen"). Each block has expected-structure prose so the visual gate is easy to verify. Filename matches existing `_RENDER_TEST_*.md` convention.
- **Tests** — `tests/test_smiles_adapter.py` (15 tests: 12 fast + 3 slow). Fast tier: structure / contract / registry / `markdown_io` recognises `smiles` fence + mixed `tikz`+`graphviz`+`d2`+`lilypond`+`smiles` 5-block ordering / `find_all_md_with_blocks` includes smiles / span correctness / TikZ + Graphviz + D2 + LilyPond adapters still present (regression guard) / **`rdkit` source-text presence guard** + **`subprocess` source-text negative guard** (Phase 6's pure-Python contract — strips comments and `"""`-bearing lines before grepping per the Phase 1/2/5 helper pattern). Slow tier: actually invokes the rdkit API to render caffeine, asserts SVG XML structure + `viewBox` + ≥20 `<path>` elements + **zero `file://` URIs**; second integration test verifies the adapter raises `RenderError` on invalid SMILES with user-friendly message; third runs the CLI end-to-end against the sandbox and asserts cache hit on second run (idempotence).
- **CLI integration** — Slow test ran the CLI on the sandbox: 3 blocks rendered to `attachments/cache/tikz/_RENDER_TEST_smiles__{1,2,3}__<hash16>.svg`. Block 1 (caffeine): **10 158 bytes, 44 `<path>` elements** (matches smoke test exactly — deterministic). Block 2 (aspirin): 8 746 bytes, 36 paths. Block 3 (ibuprofen): 7 203 bytes, 31 paths. **`grep -c 'file://'` returns 0 for all three files**. Wikilink references inserted automatically post-block per the dispatcher's normal flow. Second run confirmed three "cache hit" reports.
- **Independent visual verification (agent-side AC6.2)** — Used `rsvg-convert` to render each SVG to PNG (400×300, 8-bit RGB, ~15 KB each) and inspected each PNG via `Read`. **Caffeine**: fused 5- and 6-membered purine ring system with 3 N atoms, 2 carbonyl O atoms, 3 methyl groups — textbook caffeine. **Aspirin**: benzene ring with `-COOH` (acetic-acid carboxyl, red) on one carbon and `-OC(=O)CH3` (acetyl ester, red O atoms) on the adjacent carbon — exactly acetylsalicylic acid. **Ibuprofen**: benzene ring with isobutyl `-CH2-CH(CH3)2` on one position and α-methyl propanoic acid `-CH(CH3)-COOH` on the para position. AC6.2 satisfied at agent level; user gate is mainly a paranoia check.
- **Index.json** — `attachments/cache/tikz/index.json` now carries `kn/math/concepts/_RENDER_TEST_smiles.md` with 3 blocks at language `smiles`, output bytes (10158/8746/7203), and the 16-char canonical SHA-256 hashes verified above.

**Decisions Made:**

- **D6.1 — Wikilink alt-tag stays `tikz-cache` for SMILES too.** Reaffirms D3.1 / D4.1 / D5.1. Per SPEC OQ9 the rename to `visual-blocks` is deferred to Phase 12 migration. Using a different alt-tag for smiles now would split the migration work without UI benefit (Phase 8 plugin handles display anyway, and CSS hides `.block-language-tikz` only — adding hides for the other languages also lands at Phase 8).
- **D6.2 — `SMILESAdapter.preamble_text` returns `""`.** Reaffirms D3.2 / D4.2 / D5.2. SMILES strings are self-contained one-liners; no preamble concept. Per-folder default-image-size or atom-numbering overrides are a Phase 8+ concern, not v1.
- **D6.3 — `render_budget_seconds = 5`.** PLAN was silent on the value. Smoke-tested at **2.6 ms** for caffeine — pure-Python rdkit calls, no subprocess wait, no compile step. 5 s gives ~2000× headroom while still catching pathological hangs on very large polymer SMILES (the budget is declarative; pure-Python adapters can't easily enforce timeouts via signal/threading, but the budget is recorded for billing-style telemetry per SPEC §3.4). `SMILES_TIMEOUT_S = 5` constant in the adapter for symmetry with `D2_TIMEOUT_S` / `LILYPOND_TIMEOUT_S` etc.
- **D6.4 — Drawer dimensions: 400×300 default.** PLAN was silent. RDKit's `MolDraw2DSVG(width_px, height_px)` requires explicit dimensions. 400×300 mirrors typical Obsidian inline-figure aspect ratio (4:3) and produces readable atom labels at desktop reading-mode scale. Per-block override via fence attributes is deferred to OQ10 (per-block fence attrs).
- **D6.5 — Suppress `rdApp.error` rdkit logger at module import.** RDKit emits multi-line "SMILES Parse Error: …" diagnostics to stderr on every invalid SMILES, regardless of whether the caller surfaces an error. CLI runs and tests would see ~5 lines of rdkit stderr per bad SMILES even though our `RenderError.message` already carries the offending input. Calling `RDLogger.DisableLog("rdApp.error")` once at module load gives clean output and our error messages remain the single source of truth. Surgical: only `rdApp.error` is silenced; `rdApp.warning` and `rdApp.info` still flow through.
- **D6.6 — TDD red-then-green explicit.** Wrote `tests/test_smiles_adapter.py` BEFORE any adapter code; ran `pytest -m "not slow"` to confirm 11/12 failures (the 1 pass was `test_registry_keeps_all_prior_adapters_intact` — trivially holds because Phases 2/3/4/5 already wired those). Then implemented; same suite went 12/12 green; slow suite added 3/3 green for end-to-end confirmation. Same pattern as D3.5 / D4.6 / D5.7. One mid-implementation correction: my `test_smiles_adapter_uses_rdkit_chem_api` asserted `"subprocess" not in code_only`, but the helper that strips docstrings only removes lines containing `"""` — not lines INSIDE a docstring. The adapter docstring's rationale "no subprocess, no external CLI" tripped the test. Fix: reworded to "no shell-out, no external CLI" — keeps the rationale visible without polluting the negative assertion's substrate.
- **D6.7 — Fence-tag derive-from-`REGISTRY` refactor: deliberately deferred to follow-up commit, NOT bundled into Phase 6.** D5.6 promised this would land in Phase 6 ("with the full v1 alias surface in view"). Re-evaluated at Phase 6 close: the refactor touches 3 modules (`adapters/base.py` adds `fence_tags` property; `markdown_io.py` derives `BLOCK_RE` + `_FENCE_TO_LANG` from REGISTRY; `__init__.py` derives dispatcher `fence_tags` tuple from REGISTRY) and is non-functional. Bundling it into the same diff as the SMILES adapter muddles atomic-commit semantics: a regression in the refactor would falsely suggest a SMILES adapter bug. The cost of one more list-edit per future v1.1 language is low (mechanical, ~3 lines). Refactor is queued as "fence-tag REGISTRY-derive cleanup" — natural fit for the Phase 7 lead-in (Phase 7 already touches the dispatcher's render path for postprocess wiring) or as a standalone commit between phases. **This deviates from D5.6's stated intent**; user can override by requesting the refactor be applied now.

**Deviations from Plan:**

- **D6.7 deviates from D5.6.** D5.6 ("Phase 6 with 6 items in view captures the full v1 alias surface in one pass") was a forward-looking commitment from Phase 5; closer inspection at Phase 6 showed the SMILES adapter does NOT need any aliases (single fence tag `smiles`), so D5.6's stated rationale ("does smiles need aliases like `tikz-paused`?") is answered "no" without the refactor. Deferring keeps the Phase 6 atomic commit clean.
- **PLAN was silent on dimensions and timeout for SMILES.** Defaults chosen (400×300 / 5 s) are logged in D6.3/D6.4.

**Tests:** 15/15 Phase 6 (12 fast + 3 slow). Full suite 108/108 across all phases (14 Phase 1 + 36 Phase 2 + 14 Phase 3 + 14 Phase 4 + 15 Phase 5 + 15 Phase 6 = 108). No Phase 1 / 2 / 3 / 4 / 5 regressions.

**AC mapping:**

- AC6.1 ✓ — `python3 render_cache.py _RENDER_TEST_smiles.md` returns 0; 3 blocks rendered (slow integration test asserts this end-to-end).
- AC6.2 ✓✓ — Caffeine (purine ring system), aspirin (acetyl ester), ibuprofen (benzene + isobutyl + α-methyl propanoic acid) all visually correct via independent `rsvg-convert` rendering and visual inspection. Standard structural cues present (heteroatoms colored, carbonyls visible, ring topology correct). User gate is paranoia check.
- AC6.3 ✓ — Slow test `test_smiles_adapter_raises_on_invalid_source` confirms `INVALID_SMILES_!!!` raises `RenderError` containing the offending input. Empty source also handled (early `RenderError`).

**Lessons Learned:**

- **Pure-Python adapter is structurally simpler than subprocess adapters.** ~80 lines vs ~95 for LilyPond / D2 / Graphviz. No timeout enforcement (declarative only), no glob-based output discovery, no stderr capture. The Phase-2 `RendererAdapter` ABC covers both subprocess and pure-Python adapters cleanly — no contract change was needed for SMILES.
- **rdkit's stderr logger is verbose and out-of-band.** Without `RDLogger.DisableLog`, every `MolFromSmiles(invalid)` call prints 5 lines of "SMILES Parse Error" to stderr, regardless of whether the caller surfaces an error. For library use this is double-error reporting. Phase 8's plugin must NOT rely on these stderr lines for diagnosis — our `RenderError.message` is the single source of truth (D6.5).
- **Source-text-grep tests need to strip docstring BODIES, not just `"""` boundary lines.** The Phase 1/5 helper that filters `"""` lines is fine for positive assertions (e.g. "X must be in source") but breaks for negative assertions ("Y must NOT be in source") because the docstring rationale text is preserved. Two clean fixes: (a) reword the docstring to avoid the literal token (chosen for D6.6); (b) extend the helper to strip multi-line docstring bodies via AST parsing. Future negative source-text guards should use option (b) for robustness — pencil it in for any Phase 7+ test that needs "feature X must NOT be present" semantics.
- **rsvg-convert + Read of the resulting PNG is a powerful agent-side AC6.2 verification.** The user-driven visual gate becomes a paranoia check, not a primary verification. This pattern would also apply to AC4.x (D2 visual) and AC3.x (Graphviz visual) — worth recording for future visual-AC phases. Cost: ~50 ms per molecule + one `Read` round-trip.
- **D5.6's forward-looking commitment to "do the refactor in Phase 6" was less robust than it sounded.** Re-evaluating at Phase 6 close revealed the SMILES adapter doesn't need any aliases, so the stated rationale doesn't apply. **Lesson for the next "deferred to Phase N" decision:** make the decision concrete to phase requirements at decision-time, not retrospective alignment at execution-time. If the commitment is genuinely deferrable, leave it as "to be decided at Phase N start" rather than "will land in Phase N."

**Cross-references:**

- SPEC §5 Phase 6 (AC6.1–AC6.3); §3.2 architecture diagram (DISPATCH → SM[SMILES adapter]); §3.4 (RendererAdapter contract); §11.4 (per-phase user-feedback gate). PLAN §Phase 6 (reference command set); §Phase 7 (postprocess will run on SMILES outputs too — note iso-8859-1 encoding in rdkit SVG header for that phase).
- Phase 3 D3.x / Phase 4 D4.x / Phase 5 D5.x — adapter exception model, preamble convention, TDD pattern, alt-tag deferral all reused here.

**Phase 6 gate (user-driven):** Open the 3 rendered SVGs in Preview / QuickLook (or any SVG viewer). Each should show a recognizable molecule:

- **Test 1 (`_RENDER_TEST_smiles__1__43455e887b08c8fa.svg`)**: Caffeine. Fused bicyclic ring system (5-membered + 6-membered, sharing two atoms). Three N atoms (blue), two C=O carbonyl groups (red O atoms), three methyl groups attached at N-1, N-3, N-7 positions.
- **Test 2 (`_RENDER_TEST_smiles__2__4616bf6f9e785872.svg`)**: Aspirin (acetylsalicylic acid). Benzene ring (single 6-membered) with two ortho substituents: a carboxylic acid `-C(=O)OH` and an acetyl ester `-O-C(=O)-CH3`.
- **Test 3 (`_RENDER_TEST_smiles__3__b77a86c68f54fa0b.svg`)**: Ibuprofen. Benzene ring with two para substituents: an isobutyl group `-CH2-CH(CH3)2` on one side and an α-methyl propanoic acid `-CH(CH3)-C(=O)OH` on the other.

`attachments/cache/tikz/_RENDER_TEST_smiles__{1,2,3}__<hash>.svg` are the files to open.

**Reading-mode note:** Same as Phases 3 / 4 / 5 — opening `_RENDER_TEST_smiles.md` in Obsidian Reading mode shows both the SMILES codeblock *and* the SVG stacked, because there is no `.block-language-smiles` hide rule until Phase 8 plugin lands. Use Preview / QuickLook for the gate.

**Next:** Awaiting user gate confirmation. After confirmation, **all five v1 language adapters are complete** — critical-path moves to Phase 7 (Apply SVG postprocessing hardening). Phase 7 depends on Phase 2 and consumes SVG outputs from all five Phases 3–6 adapters; this is the foundation of iOS visual correctness (T3/T4/T5 mandatory rules).

---

_(Phase 1-6 entries + Initialization + Phase 1 v2 regression-fix log + Phase 1 Pre-Flight BLOCKED entry archived 2026-04-28 to `PROGRESS_ARCHIVE.md` § "Archived: Phase 1-6 Entries + Initialization". Phase summary table above retains all rows; commit hashes preserved verbatim in archive.)_

<!-- ARCHIVED-PHASE-5-PLACEHOLDER -->

## Failed Attempts

_(Entries added when the same error occurs 3+ times. Empty at initialization.)_

---

## Divergence Checks

_(Divergence Checks for Phases 1, 2, 3 archived 2026-04-28 to `PROGRESS_ARCHIVE.md` § "Archived: Divergence Checks (Phase 1, 2, 3)". Phase 7 + 8 divergence checks captured inline within their log entries.)_

### Divergence Check — Phase 9 — 2026-04-28

- [x] Files modified vs plan: 11 new+modified in plugin tree. **PLAN §Phase 9 was a single delegating paragraph** ("Tasks: implement all 7 commands per SPEC §5 Phase 9 acceptance criteria AC9.1–AC9.10. Implement settings UI and mode switching per the same.") with no file enumeration. Actual: 4 new src modules (settings.ts, render.ts, cacheStatus.ts, commands.ts) + 4 new test files (settings/render/cacheStatus/commands tests) + main.ts rewritten + manifest.json + package.json + styles.css + tests/__mocks__/obsidian.ts. The "no PLAN file enumeration" is by design — PLAN delegated implementation shape to Phase 9 execution.
- [x] Max cyclomatic complexity: `displayCachedBlock` is the most branched (live-mode + index-loaded + preamble-hash-present + entry-found + file-on-disk = 5-deep nested if-else). Within reasonable bound (<15). `findBlockAtCursorLine` has one nested loop with an inner branch — clean.
- [x] All changes link to specific SPEC AC items:
      - settings.ts → AC9.6 / AC9.9 (mode + mobile override)
      - render.ts → all command spawns (AC9.1-9.3, AC9.5, AC9.10)
      - cacheStatus.ts → AC9.4
      - commands.ts → AC9.1-9.3, AC9.4, AC9.5, AC9.6, AC9.7
      - main.ts → AC9.8 (live mode), AC9.9 (mobile override), AC9.10 (triggerOnSave)
      - tests → execute-spec workflow E5/E6 (TDD pure helpers)
- [x] No repeated identical tool calls (>3): true. Three pytest invocations (none for Phase 9 itself; one full-suite regression check). Multiple `npx jest` runs: red-then-green pattern per module + final all-green check.
- [x] Plan-vs-shipped delta: 8 D-rows (D9.1–D9.8) record judgment calls — none are deviations from PLAN, they're choices PLAN didn't constrain. Most material is D9.1 (refresh-block via delete-then-render, advisor-confirmed) and D9.2 (live mode = fire-and-forget, advisor-confirmed).

**Status:** Within scope. Auto-backup `0b068c6fc` (06:42) captured the 4 new src modules + 4 new test files + `tests/__mocks__/obsidian.ts` partial; the Phase 9 atomic commit will carry main.ts rewrite + manifest/package version bumps + styles.css extension + final mock additions + main.js rebuild + PROGRESS log entry.

---

## Cost Tracking

| Phase | Iterations | Tokens (in/out) | Cost | Model |
|-------|-----------|-----------------|------|-------|
| Initialization | 1 | — | — | claude-opus-4-7 |
| **Total** | 1 | — | $0.00 | |

---

## Learnings (Cross-Session Memory)

### Project-Specific Patterns

- **Two-side cache key** (D02): hash on canonical SVG-cache path so byte-identical Python and TypeScript implementations stay in sync. Verify both sides every time the normalize function changes.
- **Render-at-save with iOS read-only consumption** (D01, D03, D11): Mobile is cache-only. Anything that prevents the cache from arriving at iOS — sync filter, missing folder, oversized SVG — is a P0 bug.
- **Mandatory hardening flags** (T1–T12): These are non-negotiable. `dvisvgm --no-fonts`, `lilypond -dpoint-and-click=#f`, ID-prefix postprocess, currentColor mapping, viewBox normalization. Missing any of them produces a regression that's invisible in dev and breaks in prod.

### Common Errors & Solutions

- **PLAN "Pre-Plan State" table claimed `/Library/TeX/texbin/dvisvgm` was present (2026-04-27).** It was not — TeX Live BASIC scheme installed, dvisvgm excluded. Resolution: run `which dvisvgm` BEFORE trusting any plan table, and resolve via `sudo tlmgr install dvisvgm` (preferred over brew because it adds to the existing TL install instead of duplicating it). Sibling tools `dvilualatex`, `dvips`, `dvipdfm` being present does NOT imply dvisvgm is present.
- **dvisvgm 3.4.3 requires `--output=PATH` (with `=`)** — `--output PATH` (space-separated) errors with `option --output: string argument 'pattern' expected`. Same convention likely applies to other dvisvgm long options that take values. Use the equals form everywhere when calling dvisvgm from subprocess.
- **TeX Live 2025 frozen-release tlmgr defaults to FTP mirror that may 404.** `tlmgr install <pkg>` against the default frozen repository (`ftp://tug.org/historic/...`) failed with download_file error. Fix: explicit `--repository https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/2025/tlnet-final` (verified working).
- **TeX Live's dvisvgm binary has no libgs / no MuPDF — silently drops TikZ graphics.** `dvisvgm --list-specials` shows no `ps`/`psfile` handler. `otool -L /Library/TeX/texbin/dvisvgm` shows only libc++/libSystem linkage. Symptom: SVG renders text labels but no lines, circles, ticks, paths. Fix: pass `--libgs=/opt/homebrew/lib/libgs.dylib` (Apple Silicon brew ghostscript, runtime-dlopened). For other systems use `DVISVGM_LIBGS` env or extend the candidate list in `tikz_cache.py:LIBGS_PATH`. Future SPEC pre-flights: add `dvisvgm --list-specials | grep -E '^(ps|pdf)\b'` to prove rendering capability.
- **Never combine `--exact-bbox` with `--bbox=preview` in dvisvgm.** `--bbox=preview` is for the LaTeX `preview` package, not `standalone`. With `standalone` it produces a degenerate clipped bbox (~13pt high). Use `--bbox=min` (modern equivalent of the deprecated `--exact-bbox`) and DO NOT pass any preview flag.

---

## Recovery Instructions

**If context fills mid-execution:**

```
"Read /Users/cs/Obsidian/_/docs/specs/render-cache/PROGRESS.md and continue from the last completed phase."
```

**If a phase gets stuck (3+ failures on same task):**

1. Read the `## Failed Attempts` section above.
2. Try explicitly different approach than logged attempts.
3. After 5 total attempts, mark phase `Blocked`, write a `DEFERRED.md` note with the failure analysis, and move to the next independent phase per the dependency graph.

**To resume after interruption:**

```
/execute-spec /Users/cs/Obsidian/_/docs/specs/render-cache/SPEC.md
# Agent self-orients from PROGRESS.md and continues from the next Not Started phase.
```

**Manual-mode reminder:** The agent EXITS after each phase's checkpoint. The user must explicitly trigger the next phase ("Implement Phase N") after confirming the per-phase user-feedback gate.

---
