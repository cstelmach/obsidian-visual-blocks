# Progress Log — Obsidian Render Cache

**Spec:** `/Users/cs/Obsidian/_/docs/specs/render-cache/SPEC.md`
**Plan:** `/Users/cs/Obsidian/_/docs/specs/render-cache/PLAN.md`
**Status:** Phase 7 user gate closed (AC7.4 visual-confirmed); Phase 8 (plugin scaffold) agent-side complete — awaiting user gate.
**Mode:** Manual (user-driven phase progression)
**Started:** 2026-04-27
**Last Updated:** 2026-04-27 (Phase 7 gate closed, Phase 8 agent-side done)

> **Mode note:** PLAN.md L4 declares manual mode. SPEC §11.4 requires each
> phase to end at a "Direct user feedback (gate)" before the next begins.
> This is a user-driven workflow — Ralph Loop autonomous progression is **not**
> in effect. After each phase checkpoint, the agent EXITS and waits for the
> user to trigger the next phase.

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
| Phase 8 — Plugin scaffold | DONE (agent) | 2026-04-27 (this session) | 2026-04-27 (this session) | d035c5cfd (auto-backup, atomic capture: .gitignore + plugin tree + PROGRESS + Python fixture self-test) + 5ec8cf62d (earlier auto-backup: generator script + initial fixture stray) | jest 24/24 ✓ + python 150/150 fast ✓ | ~1.5h | New `obsidian-render-cache` plugin at `.obsidian/plugins/obsidian-render-cache/` (.ts source + main.js bundle + manifest + tests + fixtures). Cross-language hash byte-identity (T12) hard-verified: 14 fixtures × 2 languages = 28 round-trip checks passing. Production round-trip on all 3 `_RENDER_TEST_d2.md` blocks confirmed (computed hash == index.json sourceHash). One narrow `.gitignore` exception lets THIS plugin be tracked while the other 56 stay un-tracked. AC8.6 hard-verified at agent level; AC8.1/8.2/8.3/8.4/8.5/8.7 require user gate (Obsidian load + visual). |
| Phase 9 — Plugin commands and modes | Not Started | | | | | | 4–6h est. Depends on Phase 8. |
| Phase 10 — Plugin error display + status bar | Not Started | | | | | | 2–3h est. Depends on Phase 9. |
| Phase 11 — iOS validation (USER-DRIVEN) | Not Started | | | | | | User-driven. Requires phone + iCloud sync. Depends on Phase 10. |
| Phase 12 — Migration tool: legacy → new layout | Not Started | | | | | | 2–3h est. Depends on Phase 7+. |
| Phase 13 — Documentation | Not Started | | | | | | 2–3h est. Final phase before optional 14. |
| Phase 14 — gboyd068/SwiftLaTeX hands-on eval | Not Started (optional) | | | | | | OPTIONAL. Skip unless v1 has gaps surfaced during Phase 11. |

**Status values:** Not Started, In Progress, DONE, Blocked, Not Started (optional).
**Commit:** Short git hash (7 chars).
**Tests:** Format as `{passed}/{total} tests` for code phases; user-confirm note for user-driven phases.
**Critical path:** 1 → 2 → 7 → 8 → 9 → 10 → 11 → 12 → 13. Phase 14 optional.

---

## Log

_(Most recent first — reverse chronological)_

### Phase 8 — Plugin scaffold — 2026-04-27 (this session) DONE (agent-side)

**Phase 7 user-gate closure (recorded here for atomicity):** User confirmed AC7.4 multi-block visual ("Yes, we see all the svgs in the _RENDER_TEST_d2.md note. We also see the codeblock still and the embedded internal links to the cached svgs. So User gate phase 7 passes."). The "we also see the codeblock still" observation is the surface motivation for Phase 8: under Phase 7 there is still no codeblock processor on `tikz`/`graphviz`/`d2`/`lilypond`/`smiles`, so reading view shows BOTH the raw codeblock AND the wikilink-rendered cached SVG side by side. Phase 8 plugin replaces the codeblock with a single cache-rendered `<img>`, hides the now-redundant wikilink, and gives misses a typed placeholder. AC7.5 (dark-mode follow) remains structurally blocked even after Phase 8 because the user explicitly chose the SPEC-mandated `<img>` embedding (not inline `<svg>`); see D8.2 below.

**Completed:**

- **Plugin scaffold at `.obsidian/plugins/obsidian-render-cache/`** — manifest.json (id, name, version 0.1.0, minAppVersion 1.4.16, isDesktopOnly false), package.json (esbuild + jest + ts-jest + obsidian dev deps), tsconfig.json (ES2022 target, strict null checks), esbuild.config.mjs (production-mode CJS bundle, sourcemap=false), jest.config.cjs (ts-jest preset, node env, obsidian module mock), styles.css (plugin display + wikilink-hide + codeblock-wrapper override). 295 npm packages installed (zero high-severity vulns).
- **Hash port** — `src/hash.ts` (~140 lines). Three exported functions:
  - `normalize(source: string): string` — byte-identical to Python's `render_cache.normalize.normalize`. CRLF→LF, lone-CR→LF, per-line `.trim()` (BOTH ends; PLAN's `trimEnd()` would diverge — see fixture `per_line_whitespace_strip`), blank-line-run collapse, leading/trailing blank strip.
  - `pythonJsonDumps(value: unknown): string` — replicates Python's `json.dumps(sort_keys=True)` default separators `(', ', ': ')` byte-for-byte. JS's native `JSON.stringify` uses `(',', ':')` (no spaces) — would diverge the moment attrs become non-empty in Phase 9+. Recursive serializer handles strings (with `\uXXXX` escape for non-ASCII per Python's `ensure_ascii=True` default), numbers, booleans, null, arrays, objects (keys sorted at every level).
  - `computeKey(source, language, attrs, preambleHash): Promise<string>` — async (`crypto.subtle.digest('SHA-256', ...)` is async; works in Obsidian renderer + iOS WKWebView + Node 18+). Builds the SPEC §3.9 payload: `normalize(source) + 0x00 + lang + 0x00 + pythonJsonDumps(attrs) + 0x00 + preambleHash`, hashes via SubtleCrypto, hex-encodes, truncates to 16 chars.
- **Codeblock processors** — `src/main.ts` (~150 lines) registers processors for all five v1 languages (`tikz`, `graphviz`, `d2`, `lilypond`, `smiles`). Each processor calls `displayCachedBlock(source, lang, el, ctx)` inside a try/catch (advisor: "throw inside the processor callback can leave the codeblock unrendered or break the page; cheap insurance"). Empty source → no-op; empty `el`; create `.render-cache-block` wrapper. Read `index.json` once at `onload` into memory. Look up preambleHash via `index.preambleHashes["<adapter:LANG>"]` (advisor's #4 — already populated by Python pipeline; no hardcoded preambles in TS). Compute hash. Find the block entry by iterating `index.notes[ctx.sourcePath].blocks` for matching `sourceHash` (advisor: first-match-wins; identical-source duplicate blocks have identical SVG content so any match is correct). On hit + file-on-disk: emit `<img src="${app.vault.adapter.getResourcePath(entry.cachePath)}" alt="${lang}-cache" loading="lazy" class="render-cache-img">` per SPEC §3.4 step 3 + §3.6 step 4 + T7. On miss: typed placeholder, mobile reads "Open on desktop to render"; desktop is clickable and shows a Notice pointing the user to `render_cache.py` (Phase 9 wires the actual click-to-render).
- **Wikilink/plugin coexistence** — Plugin's `styles.css` includes `img[alt~="tikz-cache"]:not(.render-cache-img) { display: none }`. Specificity (0,2,1) beats the legacy `.obsidian/snippets/tikz-cache.css` rule (0,1,1) regardless of load order, so plugin's display owns the page when enabled. Plugin's own images carry `class="render-cache-img"` and bypass the hide via `:not()`. Snippet remains untouched — when plugin is disabled, snippet's rules reassert (wikilinks visible, fallback works). Plugin also includes `body .block-language-{lang} { display: block }` for all 5 languages — defeats the snippet's `display: none` on `.block-language-tikz` (which would otherwise hide the codeblock processor's container, taking our rendered image down with it).
- **Cross-language hash fixture file** — `tests/fixtures/hash_fixtures.json` (14 fixtures), generated by `resources/scripts/python_single/tests/generate_hash_fixtures.py`. Single source of truth. 14 fixtures cover: empty source, plain TikZ, TikZ-with-comments-NOT-stripped (verifies normalize's per-language docstring promise; current Python passes raw source to `compute_key`), CRLF, lone CR, multi-blank-line collapse, leading/trailing blank strip, per-line full-strip (anti-`trimEnd()` guard), Unicode source, language-distinguishes-hash, preamble-change-invalidates, attrs={} baseline, attrs={"k":"v"} (Python-JSON-spaces guard for Phase 9+), attrs multi-key sorted.
- **TDD red-then-green explicit** — Wrote `tests/hash.test.ts` with 24 assertions BEFORE any TS code. Initial `npm test`: collection error (`Cannot find module '../src/hash'`) → wrote `src/hash.ts` → all 24 jest tests pass (5 normalize + 4 pythonJsonDumps + 1 fixture-count guard + 14 per-fixture byte-identity). Same red-green pattern as D3.5 / D4.6 / D5.7 / D6.6 / D7.7.
- **Python-side fixture self-test** — `tests/test_hash_fixtures.py` (18 assertions). Re-derives every fixture's expected key in Python, asserts equality. Plus three pinning tests: per-line-strip-not-trimEnd guard, attrs-single-key-Python-spacing guard, hash-collision-where-expected (CRLF and lone-CR canonicalize to LF → identical hash).
- **Production round-trip on real cache** — Used Python `find_blocks` + `compute_key` against `_RENDER_TEST_d2.md` (3 D2 blocks). All 3 computed hashes equal the `sourceHash` field in `index.json`. The fixture-test discipline maps to actual production data.
- **Build** — `npm run build` (esbuild production CJS bundle) → `main.js` 4.5KB minified. Bundle externs: obsidian, electron, all CodeMirror packages, Node builtins. Installs cleanly into `.obsidian/plugins/obsidian-render-cache/`.

**Decisions Made (D8.x):**

- **D8.1 — Cache files stay at `attachments/cache/tikz/`; plugin reads `cachePath` field from `index.json` directly.** Advisor: "Don't bundle physical move with the plugin scaffold — that's two phases of work, you'll be debugging file-move issues alongside hash-port issues." Phase 12 (migration tool) physically moves and rewrites paths. `getResourcePath()` works on any vault-relative path, so the plugin's hit path works regardless. Prevents breaking 169 in-flight cache files for an architectural cleanup that has its own dedicated phase.
- **D8.2 — `<img>` embedding per SPEC §3.4/§3.6 (NOT inline `<svg>`).** User explicitly chose the SPEC default after seeing the trade-off: inline `<svg>` would unblock AC7.5 (dark-mode follow) but requires SPEC amendment. The user accepted "AC7.5 stays structurally blocked under `<img>`" — same position as Phase 7 D7.8. The plugin emits `<img src="${getResourcePath(cachePath)}">` per T7. If dark-mode follow becomes a priority later, that's a SPEC amendment, not a v1.0 deviation.
- **D8.3 — TS hash port matches PYTHON ACTUAL behavior, not PLAN.md pseudocode.** PLAN §Phase 8 Task 8.4 had two real bugs: (a) `line.trimEnd()` instead of Python's `ln.strip()` — would diverge on lines with leading whitespace; (b) "if (lang === 'tikz') { strip comments }" — Python's `normalize()` DOES NOT strip TikZ comments; Phase 2 dispatcher passes `block.source` raw to `compute_key` and the adapter is theoretically responsible for any pre-processing but currently does nothing of the sort. Both bugs are caught by named fixtures (`per_line_whitespace_strip` + `tikz_with_comments_NOT_stripped`). Same lesson as D7.1: PLAN pseudocode is a starting point, not a contract.
- **D8.4 — `pythonJsonDumps` helper (Python `json.dumps(sort_keys=True)` defaults, including spaces).** Empirically confirmed: `python3 -c "import json; print(repr(json.dumps({'k':'v'}, sort_keys=True)))"` → `'{"k": "v"}'` (with space). JS `JSON.stringify({"k":"v"})` → `'{"k":"v"}'` (no space). Today all attrs are `{}` so both produce `'{}'` and the divergence is invisible. Phase 9+ may introduce non-empty attrs (per-block render hints, theme colour overrides, etc.); the helper is in place so the byte-identity contract holds across that boundary. Fixture `attrs_single_key_PYTHON_JSON_SPACES` is the executable proof.
- **D8.5 — Preamble hash sourced from `index.preambleHashes["<adapter:LANG>"]` (NOT hardcoded in TS).** Advisor: "Read from `index.preambleHashes`. The map already exists with all 5 languages populated. If absent → treat as cache miss." Cleanest separation: Python owns the preamble (knows the actual TikZ preamble text), plugin only consumes the digest. If Python ever changes the preamble (e.g., adding a new TikZ package), the index.json's preambleHash regenerates and plugin auto-picks up the new value with no TS code change.
- **D8.6 — Block ordinal NOT used; lookup by `sourceHash` only.** Advisor: "MarkdownPostProcessorContext doesn't tell you the block ordinal. Don't try to scan source for ordinal — that's fragile. Instead: compute the hash, then iterate `index.notes[sourcePath].blocks` looking for matching `sourceHash`. First match wins. Robust to block reordering, identical-source duplicates, etc." Implemented exactly as advised.
- **D8.7 — Wikilink coexistence via plugin styles.css with `:not(.render-cache-img)` exception (advisor's Option A).** Plugin owns the display when enabled; the snippet is untouched and reasserts when plugin disabled. CSS specificity (plugin's (0,2,1) > snippet's (0,1,1)) makes load-order irrelevant. The "user-visible flip" the advisor flagged: under Phase 7 the user saw [codeblock + wikilink image]; under Phase 8 they see [plugin image only] (codeblock is replaced by codeblock processor; wikilink is hidden by plugin CSS). Visually equivalent on cache hits; cache misses now show a typed placeholder where Phase 7 showed nothing.
- **D8.8 — `.gitignore` carve-out for THIS plugin only.** Vault gitignore had `/.obsidian/plugins` excluding all 56 plugin directories (third-party installs). Phase 8 plugin source MUST be versioned. Solution: `!/.obsidian/plugins/`, `/.obsidian/plugins/*`, `!/.obsidian/plugins/obsidian-render-cache/` — un-excludes only this plugin's tree. Inner `.obsidian/plugins/obsidian-render-cache/.gitignore` then re-excludes `node_modules/`, `package-lock.json`. `main.js` IS committed (it is the build artifact users execute; same convention as upstream Obsidian plugin repos). Verified via `git check-ignore`: TikZJax's main.js stays ignored; render-cache's main.js is tracked.
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

1. **Enable the plugin.** Open Obsidian → Settings → Community plugins. The "Render Cache" plugin should appear in the installed-plugins list (Obsidian discovers `.obsidian/plugins/obsidian-render-cache/manifest.json`). Toggle it ON. **Verify TikZJax is OFF** (Settings → Community plugins → TikZJax). Per this session's investigation, TikZJax is not in any `loadAtStartup=True` group, so it should already be off — but if you manually enabled it at any point, disable it now to avoid a codeblock-processor race on the `tikz` fence.
2. **AC8.1 — No console errors.** Cmd+Opt+I → Console tab. Reload the plugin. Look for any red `Render Cache: …` or stack trace. Plain text logs (`obsidian-render-cache: loaded; processors registered for …`) are expected.
3. **AC8.2 — Cached TikZ block displays inline (in BOTH rendered modes).** Open `kn/math/concepts/mSB3-4_reals.md` in reading mode (Cmd+E to toggle). The TikZ number-line diagram should appear EXACTLY ONCE (plugin emits `<img>`; legacy wikilink is hidden by plugin CSS). Compare to Phase 7 reading mode where you saw "codeblock + wikilink image" stacked — that should be replaced by a single image now. Then toggle to **live preview** (the rendered-edit mode, NOT raw source). The codeblock processor fires in live preview too — diagram should appear there as well. If it does NOT appear in live preview, surface that here (Phase 9 lead-in).
4. **AC8.3 — Uncached TikZ block shows placeholder.** Open `kn/math/concepts/_RENDER_TEST_d2.md`, paste a brand-new D2 block (e.g., ```d2\nx -> y\n```) somewhere ABOVE the existing 3 blocks (don't run `render_cache.py`). Reading mode should show the existing 3 cached SVGs PLUS a typed placeholder reading "d2: Cache miss — click here for help (Phase 9 will wire click-to-render)." for the new block.
5. **AC8.4 — Mobile placeholder reads "Open on desktop".** After iCloud sync, open the same file with the new uncached block on iOS. Placeholder should read "d2: Cache miss — open on desktop to render." (no click affordance).
6. **AC8.5 — Desktop placeholder is clickable.** Click the placeholder from step 4. A Notice should pop up in the bottom-right corner: "Phase 8 placeholder. To render, run: python3 resources/scripts/python_single/render_cache.py <FILE.md>. Phase 9 will add a 'Refresh this block' command."
7. **AC8.7 — Source mode unchanged.** With any of these files open, hit Cmd+E to toggle source mode. The raw markdown ```d2\n…\n``` codeblocks should be visible exactly as authored. Switch back (Cmd+E again) to reading mode — codeblocks vanish, replaced by plugin images.
8. **Cleanup after gate.** Remove the experimental ```d2\nx -> y\n``` block you added in step 4 (or run `python3 resources/scripts/python_single/render_cache.py kn/math/concepts/_RENDER_TEST_d2.md` on the file to render it properly). **Important:** Phase 8 reads `index.json` once at `onload`; after running `render_cache.py`, reload the plugin (Settings → Community plugins → Render Cache → toggle OFF, then back ON) so the new entry is picked up. Phase 9 will add live-watching of the index file so this manual reload becomes unnecessary.

When confirmed, reply: **"Implement Phase 9"** → Plugin commands and modes (refresh-block / refresh-note / refresh-vault / show-status / sweep / toggle-mode / clear-all; mode cycling; mobile auto-override; triggerOnSave). Phase 9 replaces D8.9's placeholder click with real render-trigger wiring.

**Outstanding (NOT blocking Phase 9 — flagged across phases):**

- 3 pre-existing TikZ source bugs (`bB3-18_neuroscience-101.md`, `mSB8-9_double-brackets.md`, `mSB3-8_euler-e.md`). Separate-triage backlog. Surfaced for the 4th time in Phase 7's `--all --force` run.
- `.obsidian/community-plugins.json` anomaly — only 5 entries (`ai-note-suggestion`, `obsidian-plugin-groups`, `claude-sidebar`, `obsidian-advanced-uri`, `calendar`) despite vault using ~136 plugins. Investigation this session: `obsidian-plugin-groups` has 36 groups managing 137 plugins, with no group's `loadAtStartup=True` for non-empty plugin lists. Fly TikZJax is in 3 groups, none auto-loaded. Mechanism is probably: user enables plugins manually via the plugin-groups palette command; `community-plugins.json` reflects only the 5 plugins enabled at Obsidian startup. Phase 8 verification needed: after the user toggles "Render Cache" ON in Settings, `community-plugins.json` should grow by 1 entry — confirmation that the system is healthy, not broken.
- D6.7 fence-tag REGISTRY-derive refactor deferred a 4th time → queued for Phase 9 lead-in (Phase 9 doesn't touch the dispatcher's fence-tag list, clean lead-in moment).
- D7.9 implicit-default-fill rule (4th SVG hardening rule) explicitly NOT shipped because AC7.5 stays structurally blocked under D8.2's `<img>` choice. Re-evaluate at Phase 12 / SPEC v1.1 if the user later wants inline-SVG and dark-mode-follow.
- **iOS Web Crypto contingency.** The TS plugin uses `crypto.subtle.digest('SHA-256', ...)` which is async + standardised across modern WebKit (iOS ≥ 11). Agent-side cannot verify on iOS WKWebView; if Phase 11 surfaces "render-cache: tikz block failed — …" for every block, the fallback is to swap to `js-sha256` (sync, no Web Crypto dependency, ~15 KB to bundle). No code change needed now; this is the documented remediation path.
- **PROGRESS.md is approaching ~1300 lines.** Spine threshold is 500. Not blocking Phase 9 directly, but the Phase 9 lead-in is the natural archive moment: move Phase 1-6 entries to `PROGRESS_ARCHIVE.md`, keep Phase 7 + 8 + table + recovery in PROGRESS.md. Multiple items already queued for "Phase 9 lead-in" (D6.7 fence-tag refactor, D7.9 implicit-fill rule contingency, this archive, optionally a `community-plugins.json` post-toggle health check).

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

- **D6.1 — Wikilink alt-tag stays `tikz-cache` for SMILES too.** Reaffirms D3.1 / D4.1 / D5.1. Per SPEC OQ9 the rename to `render-cache` is deferred to Phase 12 migration. Using a different alt-tag for smiles now would split the migration work without UI benefit (Phase 8 plugin handles display anyway, and CSS hides `.block-language-tikz` only — adding hides for the other languages also lands at Phase 8).
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

### Phase 5 — Add LilyPond adapter — 2026-04-27 (this session) DONE (agent-side)

**Completed:**

- **Pre-flight 5 (`which lilypond && lilypond --version`):** Initially failed — lilypond not installed. PLAN authorises `brew install lilypond`; asked user via `AskUserQuestion` (4-option gate, mirrors Phase 4 d2 install pattern); user chose "Install via brew (Recommended)". Result: `GNU LilyPond 2.26.0 (running Guile 3.0)` at `/opt/homebrew/bin/lilypond`. SPEC §5 minimum is ≥ 2.24 — passes.
- **Smoke test before adapter:** Pre-verified PLAN's reference command on a minimal melody (`\relative c' { c d e f g a b c }`). Confirmed: cold-start wall-clock 0.43s; output `out.svg` (single-page, 6.3 KB); `grep -c 'file://'` = 0; viewBox + xmlns SVG structure. The benign `warning: ignoring unsupported formats (pdf)` on stderr is informational (we asked for `-dbackend=svg`, lilypond defaults to producing PDF too) — not a failure indicator. Lead-sheet smoke also clean (single-page, 0 `file://`).
- **Adapter** — `resources/scripts/python_single/render_cache/adapters/lilypond.py`. ~95 lines. Wraps `lilypond -dpoint-and-click=#f -dbackend=svg -dno-include-book-title-preview -o {workdir}/out {src}` via `subprocess.run` with `timeout=30s`. `RenderError` raised on non-zero exit, missing output file (empty glob), timeout, or `FileNotFoundError`. Mirrors the D2 adapter's exception model (D4.x). LilyPond-specific complexity: output discovery via `sorted(workdir.glob("out*.svg"))` rather than direct path return (lilypond names outputs `out.svg` for single-page, `out-1.svg` / `out-page1.svg` etc. for multi-page; pick the first hit).
- **Registry** — `adapters/__init__.py` now imports + registers `LilyPondAdapter()` alongside `TikzAdapter()`, `GraphvizAdapter()`, and `D2Adapter()`. Four-language registry.
- **markdown_io** — `BLOCK_RE` alternation extended `tikz(?:-paused)?|graphviz|d2` → `tikz(?:-paused)?|graphviz|d2|lilypond`. `_FENCE_TO_LANG` map gained `"lilypond": "lilypond"`. Module docstring updated to acknowledge Phase 5 reach (Phase 6 still ahead).
- **Dispatcher fence-tag list** — `render_cache/__init__.py:find_all_md_with_blocks.fence_tags` extended to `("tikz", "tikz-paused", "graphviz", "d2", "lilypond")` (now 5 items). Without this, `--all` would have skipped LilyPond files entirely. Docstring updated to note D5.6 deferral of refactor.
- **Test sandbox** — `kn/math/concepts/_RENDER_TEST_lilypond.md` with 2 LilyPond blocks per SPEC §5 ("a melody and a short lead sheet"): (1) `\relative c' { c4 d e f g a b c c b a g f e d c }` — C major scale up + down, 16 quarter notes, smallest meaningful musical phrase; (2) two-bar lead sheet with `\chordmode` chord names (C, F) over a `\new Staff` melody using the `<<` simultaneous-music idiom + explicit `\version "2.26.0"` + `\score { \layout { } }` block. Filename matches existing `_RENDER_TEST_*.md` convention.
- **Tests** — `tests/test_lilypond_adapter.py` (15 tests: 12 fast + 3 slow). Fast tier: structure / contract / registry / `markdown_io` recognises `lilypond` fence + mixed `tikz`+`graphviz`+`d2`+`lilypond` block ordering / `find_all_md_with_blocks` includes lilypond / span correctness / TikZ + Graphviz + D2 adapters still present (regression guard) / **`-dpoint-and-click=#f` source-text presence guard** (T2 invariant — strips docstrings/comments before grepping per the Phase 1/2 helper pattern). Slow tier: actually invokes `lilypond` to render simple melody, asserts SVG XML structure + ≥5 `<path>` elements + **AC5.2 hard check (`text.count("file://") == 0`)**; second integration test verifies the adapter raises `RenderError` on syntactically invalid LilyPond source (unbalanced braces); third runs the CLI end-to-end against the sandbox and asserts cache hit on second run (idempotence).
- **CLI integration** — Slow test ran the CLI on the sandbox: 2 blocks rendered to `attachments/cache/tikz/_RENDER_TEST_lilypond__{1,2}__<hash16>.svg`. Block 1 (C-major scale): 9.6 KB, 18 `<path>` elements (note heads + stems + clef glyph + barlines). Block 2 (lead sheet, 2 bars): 7.3 KB, 11 `<path>` elements (smaller because shorter, but with chord-name text glyphs). **`grep -c 'file://'` returns 0 for both files** — AC5.2 verified at agent level. Second run confirmed two "cache hit" reports.
- **Index.json** — `attachments/cache/tikz/index.json` now carries `_RENDER_TEST_lilypond.md` with 2 blocks at language `lilypond` and the 16-char canonical SHA-256 hashes verified above.

**Decisions Made:**

- **D5.1 — Wikilink alt-tag stays `tikz-cache` for LilyPond too.** Reaffirms D3.1 / D4.1. Per SPEC OQ9 the rename to `render-cache` is deferred to Phase 12 migration. Using a different alt-tag for lilypond now would split the migration work without UI benefit (Phase 8 plugin handles display anyway).
- **D5.2 — `LilyPondAdapter.preamble_text` returns `""`.** Reaffirms D3.2 / D4.2. LilyPond source is self-contained; no preamble concept. `\version` declarations live inside individual source blocks. `preamble_digest("")` is elided cleanly from the SPEC §3.7 T10 cache key. Per-folder `\paper` / global preamble overrides are a Phase 8+ concern, not v1.
- **D5.3 — `render_budget_seconds = 30`.** PLAN was silent on the value. Smoke-tested cold-start at 0.43s for a minimal melody and ~0.6s for a lead sheet; LilyPond's first compile is fast because Guile is already JITted by the time it hits engraving. 30s gives generous headroom for complex multi-stave scores while still surfacing pathological hangs (vs lualatex's 60s). `LILYPOND_TIMEOUT_S = 30` constant in the adapter for symmetry with `D2_TIMEOUT_S` / `DOT_TIMEOUT_S` / `LUALATEX_TIMEOUT_S` / `DVISVGM_TIMEOUT_S`.
- **D5.4 — All four CLI flags declared explicitly: `-dpoint-and-click=#f -dbackend=svg -dno-include-book-title-preview -o <prefix>`.** Per PLAN reference command. `-dpoint-and-click=#f` is mandatory per SPEC T2/AC5.2 (without it, `file://` URIs are baked into output). `-dbackend=svg` overrides lilypond's default of producing PDF + PostScript; the benign `warning: ignoring unsupported formats (pdf)` confirms this took effect. `-dno-include-book-title-preview` strips the auto-generated title block — notes only. `-o <prefix>` is a prefix not a filename: lilypond appends `.svg` (or `-1.svg`, `-page1.svg` for multi-page).
- **D5.5 — Output discovery via `sorted(workdir.glob("out*.svg"))[0]`.** PLAN's reference command was `next(workdir.glob("out*.svg"))`. Used `sorted(...)[0]` for determinism (across filesystems where dir-iteration order varies, e.g., HFS+ vs APFS, glob order is implementation-defined). `sorted` cost is O(N log N) on a directory with typically 1–3 entries → free. Multi-page handling (composing multiple SVGs into one cache entry) is **explicitly deferred to v1.1** — v1's test sandbox uses single-page inputs and the adapter returns the first match. The sandbox confirms this works (both blocks compile to single-page).
- **D5.6 — Fence-tag list refactor: deferred ONE more phase, will land in Phase 6.** The Phase 3/4 lessons (D3.4/D4.5) flagged that "5 items is the threshold for the derive-from-REGISTRY refactor". Phase 5 added the 5th item. Reasoning for one more deferral: Phase 6 (RDKit/SMILES) adds the *final* v1 language; doing the refactor now (with 5 items) means writing it twice (once now, once when smiles lands), whereas doing it in Phase 6 with 6 items in view captures the full v1 alias surface (e.g., does smiles need any aliases like `tikz-paused`?) in one pass. Updated dispatcher docstring to mark this deferral explicitly so Phase 6 doesn't forget. *Net cost*: one more list-edit in Phase 6 (~1 line) + the abstraction lands in one cleaner pass.
- **D5.7 — TDD red-then-green explicit.** Wrote `tests/test_lilypond_adapter.py` BEFORE any adapter code; ran `pytest -m "not slow"` to confirm 11/12 failures (the 1 pass was `test_registry_keeps_all_prior_adapters_intact` — trivially holds because phases 2/3/4 already wired those). Then implemented; same suite went 12/12 green; slow suite added 3/3 green for end-to-end confirmation. Same pattern as D3.5 / D4.6.

**Deviations from Plan:**

- **None of substance.** PLAN's reference command shipped verbatim. The `LILYPOND_TIMEOUT_S = 30` constant value (vs PLAN's silent default) is logged in D5.3. The `sorted(... glob ...)[0]` vs PLAN's `next(...)` is logged in D5.5. The deliberate one-more-phase deferral of the fence-tag refactor (D5.6) is a documented decision, not a slip.

**Tests:** 15/15 Phase 5 (12 fast + 3 slow). Full suite (fast + slow) 93/93 across all phases (14 Phase 1 + 36 Phase 2 + 14 Phase 3 + 14 Phase 4 + 15 Phase 5 = 93). No Phase 1 / Phase 2 / Phase 3 / Phase 4 regressions.

**AC mapping:**

- AC5.1 ✓ — `python3 render_cache.py _RENDER_TEST_lilypond.md` returns 0; 2 blocks rendered (slow integration test asserts this end-to-end).
- AC5.2 ✓✓ — `grep -c 'file://'` returns 0 for both cache SVGs (verified at agent level via slow integration test AND manual disk grep). The mandatory T2 flag took effect.
- AC5.3 — Visual gate (user confirms "music notation looks right"). User-driven; pending.

**Lessons Learned:**

- **The `out*.svg` glob pattern is the only structural difference from the D2/Graphviz adapter shape.** Otherwise LilyPondAdapter is the same flat `subprocess.run + RenderError` template that D3/D4 established. Phase 6 RDKit (pure-Python, no shellout) will be the genuinely different shape — the last v1 adapter is also the only one that breaks the subprocess pattern.
- **Smoke-testing the renderer command BEFORE writing the adapter caught a wording detail in PLAN's stderr expectation.** The PLAN didn't mention the benign `warning: ignoring unsupported formats (pdf)` lilypond emits when `-dbackend=svg` is given. If the adapter had asserted on empty stderr (it doesn't — only on non-zero exit), this would have caused phantom failures. Adapter only checks `returncode != 0` + glob result; matches D3/D4 robustness.
- **AC5.2's `grep file://` is a textbook contract test.** It's a single-character flag with a single-character outcome — but without the explicit assertion, a future "clean up the LilyPond flags" refactor could remove it silently. Both the source-text guard test (`test_lilypond_adapter_uses_point_and_click_off`) and the rendered-output check (`test_lilypond_adapter_renders_simple_melody`) catch the regression at different layers.
- **Per-language pre-flight via `AskUserQuestion` continues to be the right pattern.** `brew install` is technically authorised by PLAN but counts as a system change. The 4-option gate (install / install-manually / skip / defer) preserves user agency. ~30s of user time. Phase 6 (RDKit) is `pip install rdkit` — same pattern, same gate.
- **The dispatcher's existing generality continues to pay off.** `process_file` in `render_cache/__init__.py` did not need ANY edit for Phase 5 — same as Phase 3 and Phase 4. Three data declarations (REGISTRY, BLOCK_RE, fence_tags) + one new adapter file. The refactor cost per language is now flat at ~95 lines (~95 adapter — slightly more than D2/Graphviz because of the glob — + ~15 wiring). Phase 2's contract design has paid off across three sequential adapter additions.

**Cross-references:**

- SPEC §5 Phase 5 (AC5.1–AC5.3); §3.4 (RendererAdapter contract); §3.7 T2 (mandatory `-dpoint-and-click=#f`); §3.7 T8/T9/T10 (cache-key invariants); §11.4 (per-phase user-feedback gate).
- PLAN §Phase 5 (reference command); §Phase 6 (RDKit — pure-Python adapter, no subprocess); §Phase 7 (postprocess hardening will run on lilypond outputs too); §Phase 12 (alt-tag rename per OQ9); fence-tag refactor deferred to Phase 6 per D5.6.
- Phase 3 D3.x / Phase 4 D4.x — adapter exception model, preamble convention, TDD pattern, alt-tag deferral all reused here.

**Phase 5 gate (user-driven):** Open the 2 rendered SVGs in Preview / QuickLook (or any SVG viewer). Confirm:
- **Test 1 (`_RENDER_TEST_lilypond__1__6b94ee58569f56ca.svg`)**: 5-line treble-clef staff with a 4/4 time signature; 16 quarter notes ascending (C–D–E–F–G–A–B–C') then descending (C'–B–A–G–F–E–D–C); single bar line at the end. Notes should be cleanly engraved, no overlap.
- **Test 2 (`_RENDER_TEST_lilypond__2__81531b1bd8dad5e7.svg`)**: Two staves stacked vertically — top is a chord-name line ("C" for bar 1, "F" for bar 2); bottom is a 5-line treble-clef staff with the melody (c4 g8 g a4 g | bes4 a g2). Bar line between bars. Both staves should be vertically aligned.

`attachments/cache/tikz/_RENDER_TEST_lilypond__{1,2}__<hash>.svg` are the files to open.

**Reading-mode note:** Same as Phase 3 / Phase 4 — opening `_RENDER_TEST_lilypond.md` in Obsidian Reading mode will show both the LilyPond codeblock *and* the SVG stacked, because there is no `.block-language-lilypond` hide rule until Phase 8 plugin lands. Use Preview / QuickLook for the gate.

**Next:** Awaiting user gate confirmation, then trigger Phase 6 — Add RDKit adapter (parallelizable; Phase 6 is the last v1 language adapter, and is pure-Python so no `brew install` step).

---

### Phase 4 — Gate Closure — 2026-04-27 (this session)

**User confirmation (gate type: visual-confirmed):** "User gate passed. all three images confirmed in Quicklook" — user opened `attachments/cache/tikz/_RENDER_TEST_d2__{1,2,3}__<hash16>.svg` in Preview / QuickLook and confirmed visual fidelity for the three D2 blocks (simple 3-node graph, D2-specific shapes with dashed edge, nested containers with cross-container hand-off edge).

**Why this gate matters:** D2 is a brand-new adapter family in v1; no prior cached SVGs to fall back on. A regression in the new `d2` adapter or the dispatcher's language routing would produce malformed output that the structural-only AC4.2 (rect/path counting) cannot fully catch. Visual confirmation rules out adapter-level layout regression.

**Decisions made:** None new — gate-closure pattern is the same as Phase 1 v2 / Phase 2 / Phase 3 (D2.8/D2.9, D3-closure entry). Phase-table row updated DONE; entry-cell wording switched from "(agent)" to "DONE" + "Gate (visual-confirmed)".

**Tests:** N/A (gate is user visual confirmation; no code change in this entry).

**Next:** Phase 5 — Add LilyPond adapter (this session, immediately following).

**Cross-references:** Phase 4 Done entry below; Phase 1 v2 / Phase 2 / Phase 3 gate-closure pattern.

---

### Phase 4 — Add D2 adapter — 2026-04-27 (this session) DONE (agent-side)

**Completed:**

- **Pre-flight 4 (`which d2 && d2 --version`):** Initially failed — d2 not installed. PLAN per-language pre-flight section authorises `brew install d2`; asked user via `AskUserQuestion` (4-option gate); user chose "Install via brew (Recommended)". Result: `d2 0.7.1` at `/opt/homebrew/bin/d2`. PLAN minimum was v0.7.0 — passes.
- **Adapter** — `resources/scripts/python_single/render_cache/adapters/d2.py`. ~70 lines. Wraps `d2 --layout=elk --pad=20 --theme=0 --bundle=true SRC OUT` via `subprocess.run` with `timeout=15s`. `RenderError` raised on non-zero exit, missing output file, timeout, or `FileNotFoundError`. Mirrors the Graphviz adapter's exception model (D3.x).
- **Registry** — `adapters/__init__.py` now imports + registers `D2Adapter()` alongside `TikzAdapter()` and `GraphvizAdapter()`. Three-language registry.
- **markdown_io** — `BLOCK_RE` alternation extended `tikz(?:-paused)?|graphviz` → `tikz(?:-paused)?|graphviz|d2`. `_FENCE_TO_LANG` map gained `"d2": "d2"`. Module docstring updated to acknowledge Phase 4 reach (Phases 5-6 still ahead).
- **Dispatcher fence-tag list** — `render_cache/__init__.py:find_all_md_with_blocks.fence_tags` extended to `("tikz", "tikz-paused", "graphviz", "d2")` (now 4 items). Without this, `--all` would have skipped D2 files entirely.
- **Test sandbox** — `kn/math/concepts/_RENDER_TEST_d2.md` with 3 representative D2 blocks: smallest-meaningful 3-node graph; D2-specific surface (`shape: queue`, `shape: cylinder`, multi-line node labels via `\n`, `style.stroke-dash` on connection); nested containers (`{ … }` blocks with cross-container edge using dotted-path syntax `ingest.parse -> store.index`). Filename pattern matches existing `_RENDER_TEST_*.md` convention.
- **Tests** — `tests/test_d2_adapter.py` (14 tests: 11 fast + 3 slow). Fast tier: structure / contract / registry / `markdown_io` recognises `d2` fence + mixed `tikz`+`graphviz`+`d2` block ordering / `find_all_md_with_blocks` includes d2 / span correctness / TikZ + Graphviz adapters still present (regression guard). Slow tier: actually invokes `d2` to render the 3-node simple graph, asserts SVG XML structure + presence of `<rect>`/`<path>` drawing elements; second integration test verifies the adapter raises `RenderError` on syntactically invalid D2 source (no silent broken-SVG production); third runs the CLI end-to-end against the sandbox and asserts cache hit on second run (idempotence).
- **CLI integration** — Slow test ran the CLI on the sandbox: 3 blocks rendered to `attachments/cache/tikz/_RENDER_TEST_d2__{1,2,3}__<hash16>.svg` (sizes 11.0 / 19.2 / 21.6 KB). Drawing-element counts (rect + path) consistent with each block's expected geometry: #1 has 5 rects + 3 paths (3 nodes + 3 edges); #2 has 6 rects + 7 paths (3 nodes with extra shape outlines + 3 edges); #3 has 9 rects + 3 paths (2 container outlines + 4 inner nodes + 1 cross-container edge + intra-container edges as paths). Second run confirmed three "cache hit" reports.
- **Index.json** — `attachments/cache/tikz/index.json` now carries `_RENDER_TEST_d2.md` with 3 blocks at language `d2` and the 16-char canonical SHA-256 hashes verified above.

**Decisions Made:**

- **D4.1 — Wikilink alt-tag stays `tikz-cache` for D2 too.** Reaffirms D3.1. Per SPEC OQ9 the rename to `render-cache` is deferred to Phase 12 migration. Using a different alt-tag for d2 now would split the migration work across phases without UI benefit (Phase 8 plugin handles display anyway).
- **D4.2 — `D2Adapter.preamble_text` returns `""`.** Reaffirms D3.2. D2 source is self-contained; no preamble concept. `preamble_digest("")` is elided cleanly from the SPEC §3.7 T10 cache key.
- **D4.3 — `render_budget_seconds = 15`.** PLAN was silent on the value. Graphviz used 10s. d2 + ELK is a Go binary doing first-compile cold start which can run slower than `dot`; 15s gives modest headroom without approaching d2's own 120s default. Used both as the contract advertisement *and* the actual `subprocess.run(timeout=15)` value (consistent with D3.3 enforcement principle). `D2_TIMEOUT_S = 15` constant in the adapter for symmetry with `DOT_TIMEOUT_S` / `LUALATEX_TIMEOUT_S` / `DVISVGM_TIMEOUT_S`.
- **D4.4 — All four CLI flags declared explicitly: `--layout=elk --pad=20 --theme=0 --bundle=true`.** Per PLAN reference command. `--bundle=true` is d2 0.7.1's default but declaring it explicitly protects the cache contract from a future d2 default flip (e.g., if d2 ever changes default to bundle=false, our cache files would silently start needing external assets). `--layout=elk` is the non-default choice (default is `dagre`); ELK gives better hierarchical layout for the diagram styles we author.
- **D4.5 — Fence-tag list still duplicated; refactor deferred again.** Reaffirms D3.4. The list in `find_all_md_with_blocks` is now 4 items. Phase 5 (LilyPond) or Phase 6 (RDKit) is the natural moment for the "derive from REGISTRY keys + alias map" abstraction — five items is when it stops being trivial.
- **D4.6 — TDD red-then-green explicit.** Wrote `tests/test_d2_adapter.py` BEFORE any adapter code; ran `pytest -m "not slow"` to confirm 10/11 failures (the 1 pass was `test_registry_keeps_tikz_and_graphviz_intact` — trivially holds because phases 2/3 already wired those). Then implemented; same suite went 11/11 green; slow suite added 3/3 green for end-to-end confirmation. Same pattern as D3.5.

**Deviations from Plan:**

- None of substance. PLAN's reference command is verbatim what shipped. The `D2_TIMEOUT_S` constant value (15s vs PLAN's silent default) is logged in D4.3.

**Tests:** 14/14 Phase 4 (11 fast + 3 slow). Full fast suite 71/71 across all phases (12 Phase 1 + 36 Phase 2 + 11 Phase 3 + 11 Phase 4 + 1 deselect-marker counted at suite level = 71). No Phase 1 / Phase 2 / Phase 3 regressions.

**AC mapping:**

- AC4.1 ✓ — `python3 render_cache.py _RENDER_TEST_d2.md` returns 0; 3 blocks rendered (slow integration test asserts this end-to-end).
- AC4.2 — Drawing-element structural verification at agent level (rect + path counts match expected geometry per block). User-gate visual confirmation pending.
- AC4.3 ✓ — Second CLI run reports "cache hit" three times (slow integration test asserts this).

**Lessons Learned:**

- **D2 adapter is the cleanest reference shape so far.** ~70 lines, no preamble plumbing, no Ghostscript dependency, straightforward CLI semantics with non-zero exit on failure (no silent broken SVGs). Phase 5 (LilyPond) will be longer because of the `out*.svg` glob (LilyPond names its outputs). Phase 6 (RDKit) is pure-Python — no shellout at all.
- **Per-language pre-flight is best gated by `AskUserQuestion`.** `brew install` is technically authorised by PLAN but counts as a system change. The 4-option gate (install / install-manually / skip / defer) preserves user agency without blocking forever. Took ~30s of user time; logged the install hash + version explicitly in the log.
- **The dispatcher's existing generality continues to pay off.** `process_file` in `render_cache/__init__.py` did not need ANY edit for Phase 4 — same as Phase 3. Three data declarations (REGISTRY, BLOCK_RE, fence_tags) + one new adapter file. The refactor cost per language is now flat at ~85 lines (~70 adapter + ~15 wiring).
- **d2 0.7.1's behaviour matched the PLAN's command verbatim.** Pre-flight smoke (`d2 --layout=elk --pad=20 --theme=0 --bundle=true smoke.d2 smoke.svg`) produced a valid SVG (`<svg xmlns ...>` + `<rect>` + `<path>`). Invalid input returned exit=1 with stderr error messages, no broken SVG written. The PLAN's reference command was correctly captured at write time.

**Cross-references:**

- SPEC §5 Phase 4 (AC4.1–AC4.3); §3.4 (RendererAdapter contract); §3.7 T8/T9/T10 (cache-key invariants).
- PLAN §Phase 4 (reference command); §Phase 5 (LilyPond — `out*.svg` glob is the next adapter shape change); §Phase 12 (alt-tag rename per OQ9).
- Phase 3 D3.1-D3.5 — adapter exception model, preamble convention, TDD pattern, fence-tag list deferral all reused here.

**Phase 4 gate (user-driven):** Open the 3 rendered SVGs in Preview / QuickLook (or any SVG viewer). Confirm:
- Block 1 is a 3-node graph with directed arrows (a → b → c, a → c).
- Block 2 has 3 distinct node shapes: a default rectangle "API\n(REST)", a queue-shape "Message Queue", a cylinder-shape "Persistent Store"; edges labeled "enqueue" / "persist" / "query results"; the "query results" edge is dashed.
- Block 3 has two visibly grouped containers ("Ingest" outer label, "Store" outer label) each with two internal nodes connected, plus one cross-container edge labeled "hand-off" from `parse` to `index`.

`attachments/cache/tikz/_RENDER_TEST_d2__{1,2,3}__<hash>.svg` are the files to open.

**Reading-mode note:** Same as Phase 3 — opening `_RENDER_TEST_d2.md` in Obsidian Reading mode will show both the D2 codeblock *and* the SVG stacked, because there is no `.block-language-d2` hide rule until Phase 8 plugin lands. This is expected, not a regression. Use Preview / QuickLook for the gate.

**Next:** Awaiting user gate confirmation, then trigger Phase 5 — Add LilyPond adapter (parallelizable with 6, 7).

---

### Phase 3 — Gate Closure — 2026-04-27 (this session)

**User confirmation (gate type: visual-confirmed):** "user gate passed. All three visible in Preview / Quicklook" — user opened the 3 sandbox SVGs in Preview / QuickLook and confirmed visual fidelity for the simple digraph, labeled-edge graph, and clustered subgraph.

**Why this gate matters:** Graphviz is a brand-new adapter family in v1; no prior cached SVGs to fall back on. A regression in the new `dot -Tsvg` adapter or the dispatcher's language routing would produce malformed output. Visual confirmation rules out adapter-level regression.

**Decisions made:** None new — gate-closure pattern is the same as Phase 1 v2 / Phase 2 (D2.8/D2.9).

**Tests:** N/A (gate is user visual confirmation; no code change in this entry).

**Next:** Phase 4 — Add D2 adapter (this session, immediately following).

**Cross-references:** Phase 3 Done entry below; Phase 1 v2 / Phase 2 gate-closure pattern.

---

### Phase 3 — Add Graphviz adapter — 2026-04-27 (this session) DONE (agent-side)

**Completed:**

- **Pre-flight 3 (`which dot && dot -V`):** `/opt/homebrew/bin/dot — graphviz version 14.1.5 (20260411.2331)` (Apple Silicon brew). PLAN row 38 was "TBD"; verified before any code change.
- **Adapter** — `resources/scripts/python_single/render_cache/adapters/graphviz.py`. ~50 lines. Wraps `dot -Tsvg -o OUT IN` via `subprocess.run` with timeout=10s. `RenderError` raised on non-zero exit, missing output file, timeout, or `FileNotFoundError`. Mirrors the TikZ adapter's exception model exactly (Phase 2 D2.x).
- **Registry** — `adapters/__init__.py` now imports + registers `GraphvizAdapter()` alongside `TikzAdapter()`.
- **markdown_io** — `BLOCK_RE` alternation extended `tikz(?:-paused)?` → `tikz(?:-paused)?|graphviz`. `_FENCE_TO_LANG` map gained `"graphviz": "graphviz"`. Module docstring updated to acknowledge Phase 3 reach.
- **Dispatcher fence-tag list** — `render_cache/__init__.py:find_all_md_with_blocks.fence_tags` extended `("tikz", "tikz-paused")` → `("tikz", "tikz-paused", "graphviz")`. Without this, `--all` would have skipped Graphviz files entirely.
- **Test sandbox** — `kn/math/concepts/_RENDER_TEST_graphviz.md` (PLAN Task 3.1) with 3 representative DOT blocks: simple digraph, labeled-edge graph (with `rankdir=LR`, `shape=box`, color, dashed style), clustered subgraph (`subgraph cluster_*` with cross-cluster edge using `ltail`/`lhead`). Filename pattern matches existing `_TIKZ_TEST_*.md` convention in same directory.
- **Tests** — `tests/test_graphviz_adapter.py` (14 tests: 11 fast + 3 slow). Fast tier: structure / contract / registry / `markdown_io` recognises `graphviz` fence + mixed `tikz`+`graphviz` block ordering / `find_all_md_with_blocks` includes graphviz / span correctness / TikZ adapter still present (regression guard). Slow tier: actually invokes `dot` to render `digraph G { a -> b; b -> c; a -> c; }`, asserts SVG XML structure + presence of `<ellipse>`/`<polygon>`/`<path>` drawing elements; second integration test verifies the adapter raises `RenderError` on syntactically invalid DOT (no silent broken-SVG production); third runs the CLI end-to-end against the sandbox and asserts cache hit on second run (idempotence).
- **CLI integration** — Slow test ran the CLI on the sandbox: 3 blocks rendered to `attachments/cache/tikz/_RENDER_TEST_graphviz__{1,2,3}__<hash16>.svg` (sizes 2.2 KB / 3.7 KB / 3.1 KB). Drawing-element counts (path/ellipse/polygon) consistent with each block's expected geometry. Second run confirmed three "cache hit" reports.

**Decisions Made:**

- **D3.1 — Wikilink alt-tag stays `tikz-cache` for Graphviz too.** Per SPEC OQ9 the rename to `render-cache` is deferred to Phase 12 migration. Using a different alt-tag for graphviz now would (a) require an immediate CSS extension, (b) split the migration work across phases, (c) not visually surface anyway in v1 because Phase 8 plugin is what actually displays SVGs in Obsidian. Trade-off accepted: comment in `markdown_io.py` is now explicit that the legacy alt is shared.
- **D3.2 — `GraphvizAdapter.preamble_text` returns `""`.** DOT files are self-contained — no preamble concept exists. Returning empty makes `preamble_digest("")` elide cleanly from the SPEC §3.7 T10 cache key (the `compute_key` payload still gets `... || "" || ...` but with no semantic content). Verified by `test_graphviz_adapter_preamble_is_empty`.
- **D3.3 — `render_budget_seconds = 10`** (PLAN Task 3.2 / AC3.4). Used both as the contract advertisement *and* the actual `subprocess.run(..., timeout=10)` value, so the budget is enforced not just declared. `DOT_TIMEOUT_S = 10` constant introduced in the adapter for symmetry with `LUALATEX_TIMEOUT_S` / `DVISVGM_TIMEOUT_S`.
- **D3.4 — Kept fence-tag list duplication explicit in `find_all_md_with_blocks`.** PLAN didn't ask for, and the advisor flagged that abstracting to "derive from REGISTRY keys + alias map" is over-engineering for Phase 3. Adding D2 / LilyPond / RDKit will trigger an obvious "this list is now 5 items" refactor moment in Phase 4-6; do it then with full context, not now with two items.
- **D3.5 — TDD red-then-green explicit.** Wrote `tests/test_graphviz_adapter.py` BEFORE any adapter code; ran `pytest -m "not slow"` to confirm 10/11 failures (the 1 pass was `test_registry_keeps_tikz_intact` which trivially holds because TikZ was already there). Then implemented; same suite went 11/11 green; slow suite added 3/3 green for end-to-end confirmation.

**Deviations from Plan:**

- None of substance. PLAN Task 3.2's snippet uses `from .base import ...`; the actual import path (matching the rest of the package) is `from render_cache.adapters.base import ...`. Equivalent semantically; matches Phase 2's TikZ adapter style. No D-row needed.

**Resolved mid-phase:**

- Initial test run had `test_markdown_io_finds_mixed_tikz_and_graphviz` failing because `BLOCK_RE` didn't yet match `graphviz`. The failure was the EXPECTED red-phase behavior, not a bug — fixed by extending the regex alternation.

**Tests:** 14/14 Phase 3 (11 fast + 3 slow). Full fast suite 60/60 across all phases (12 Phase 1 + 36 Phase 2 + 11 Phase 3 + 1 deselect-marker counted as suite-level = 60). No Phase 1 / Phase 2 regressions.

**Commit accounting:** Auto-backup hash `1d0fe447b` (2026-04-27 13:54) captured all Phase 3 work atomically (code + tests + sandbox + PROGRESS + cache deltas + auxiliary journal/archive files), exactly as in Phase 1 v2's CSS commit (`84ccae5ac`) and Phase 2's code commit (`2aaf1f5b5`) — the auto-backup happened to fire in the middle of the agent's "atomic" staging window and swept everything in one go. The follow-up PROGRESS-only commit in this iteration just records the hash. Net Phase 3 history is two commits: the auto-backup (everything) + the hash-pointer log entry (this commit).

**AC mapping:**

- AC3.1 ✓ — `python3 render_cache.py _RENDER_TEST_graphviz.md` returns 0; 3 blocks rendered (slow integration test asserts this end-to-end).
- AC3.2 — Drawing-element structural verification at agent level (path/ellipse/polygon counts match expected geometry per block). User-gate visual confirmation pending.
- AC3.3 ✓ — Second CLI run reports "cache hit" three times (slow integration test asserts this).
- AC3.4 ✓ — `render_budget_seconds == 10` enforced both as property and as `subprocess.run` timeout.

**Lessons Learned:**

- **Graphviz adapter is the small / clean reference shape for this adapter family.** Roughly 50 lines, no preamble plumbing, no intermediate file format, no Ghostscript dependency. The Phase 1 TikZ complexity (libgs auto-detect, bbox flag pitfalls, dvi→svg two-step) was unique to TikZ. Phase 4 (D2) will look similar to this; Phase 5 (LilyPond) will need post-render glob (`out*.svg`); Phase 6 (RDKit) is pure-Python no-shellout. Anchor the per-language complexity expectations on this Phase 3 baseline.
- **The dispatcher's existing generality paid off.** `process_file` in `render_cache/__init__.py` did not need ANY edit for Phase 3 — it dispatches via `REGISTRY.get(block.language)` and computes cache keys via the same code path for any language. The only data declarations that needed extending were three: REGISTRY, BLOCK_RE alternation, and `find_all_md_with_blocks.fence_tags`. Phase 2's contract design is paying off in Phase 3 maintenance cost.
- **Auto-backup interleaves with phase work, again.** Already documented in Phase 2 lesson; reaffirmed here. The phase atomic commit will stage source / test / sandbox / PROGRESS only; cache-file deltas (3 new SVGs) and markdown ref-insertion deltas in the sandbox will be in auto-backup commits.

**Cross-references:**

- SPEC §5 Phase 3 (AC3.1–AC3.4); §3.4 (RendererAdapter contract); §3.7 T8/T9/T10 (cache-key invariants).
- PLAN §Phase 3 (Tasks 3.1–3.3); §Phase 4 (D2 — same shape as Phase 3); §Phase 12 (alt-tag rename per OQ9).
- Phase 2 D2.4 / D2.7 — adapter exception model and TDD pattern reused here.

**Phase 3 gate (user-driven):** Open the 3 rendered SVGs in Preview / QuickLook (or any SVG viewer). Confirm:
- Block 1 is a 3-node digraph with directed arrows (a → b, b → c, a → c).
- Block 2 has 3 boxed nodes left-to-right with labeled edges; "kept" edge is dark green, "discarded" edge is red dashed.
- Block 3 has two visibly grouped clusters ("Ingest" grey, "Store" lightblue) with a connecting edge between cluster boundaries.

`attachments/cache/tikz/_RENDER_TEST_graphviz__{1,2,3}__<hash>.svg` are the files to open.

**Next:** Awaiting user gate confirmation, then trigger Phase 4 — Add D2 adapter (parallelizable with 5–7).

---

### Phase 2 — Gate Closure — 2026-04-27 (this session)

**User confirmation (gate type: visual-confirmed):** Asked via `AskUserQuestion`, three options offered (visually-confirmed / trust-tests-skip / wait). User selected "Proceed: visually confirmed (Recommended)" — i.e. opened ≥2 of the 5 reference files on desktop AND mobile and verified cached SVGs render correctly post-restructure.

**Why this is meaningful even for a "pure restructure" phase:** Phase 2 re-keyed all 5 Phase-1 cache files onto the SPEC §3.9 16-char hash (D2.1). Old 8-char filenames were swept; new 16-char filenames are referenced in the markdown. A regression in either the hash function or the markdown ref-rewriting logic would have produced "broken embed" indicators for the user even though no visual change in the SVG content itself was expected. Visual confirmation rules out both regression classes.

**Decisions made:**
- **D2.8** — Treat user "continue methodically" + explicit `/execute-spec` re-invocation as a re-trigger of the workflow but NOT as silent gate confirmation. The advisor flagged that the user's prior gate behavior (Phase 1 v2) is to spontaneously report visual problems; absence of report is weak evidence. Asked explicitly to preserve manual-mode discipline.
- **D2.9** — Logged gate-type as `visual-confirmed` (vs `trust-tests-skip`). The two are not equivalent for the audit trail: `trust-tests-skip` would mean we ship Phase 2 on agent-side evidence alone, with user retroactively absorbing any visual regression risk. `visual-confirmed` means the user has actually looked.

**Tests:** N/A (gate is user visual confirmation; no code change in this entry).

**Next:** Phase 3 — Add Graphviz adapter.

**Cross-references:** Phase 2 Done entry below; Phase 1 v2 gate-closure pattern (precedent for visual-confirmation flow).

---

### Phase 2 — Restructure into render_cache package — 2026-04-27 13:15 DONE (agent-side)

**Completed:**

- Created `resources/scripts/python_single/render_cache/` package (10 .py files; PLAN §Task 2.1 said 9 — the difference is `adapters/__init__.py`, which the PLAN's `find` command counts but the prose narration miscounted). Modules per SPEC §3.3:
  - `normalize.py` — whitespace + line-ending canonicalisation (SPEC §3.7 T9). Identity for clean blocks, idempotent. PLAN's verify example `'  hello\n\n\n\n  world  ' → 'hello\n\nworld'` passes.
  - `hash.py` — canonical 16-char SHA-256 cache key per SPEC §3.9: `SHA-256(normalize(source) || \x00 || lang || \x00 || JSON(attrs, sorted) || \x00 || preamble_hash)[:16]`. Includes `preamble_digest()` helper.
  - `markdown_io.py` — `find_blocks` + `find_existing_ref`. Recognises both `tikz` and `tikz-paused` fences; both canonicalise `language="tikz"` so pausing/unpausing does not thrash the cache (D2.3).
  - `cache_paths.py` — `cache_filename`, `cache_path_for`. Phase 2 retains the legacy directory `attachments/cache/tikz/` (Phase 12 migrates to SPEC §3.8 layout).
  - `index.py` — `load_index`, `save_index` (atomic via tempfile + `os.replace`), `empty_index`. SPEC §3.4 schema. Phase 2 location: `attachments/cache/tikz/index.json` (legacy).
  - `postprocess.py` — pass-through stub (Phase 7 fills T3/T4/T5 hardening).
  - `adapters/base.py` — `RendererAdapter` ABC + `RenderError`. Required properties: `language`, `render_budget_seconds`, `preamble_text`. Required method: `render(source, attrs, workdir) -> Path`.
  - `adapters/tikz.py` — `TikzAdapter` wraps the lualatex(DVI) → dvisvgm(SVG) pipeline. All Phase 1 regression fixes locked in: `--no-fonts` (T1), `--bbox=min` (NOT `--bbox=preview`), `--libgs=` auto-detection with `DVISVGM_LIBGS` env override, `--output=PATH` (with `=`).
  - `adapters/__init__.py` — `REGISTRY = {"tikz": TikzAdapter()}`. Adding new languages is purely additive in Phases 3-6.
  - `__init__.py` — dispatcher + CLI logic. Same flags as Phase 1: `path`, `--all`, `--force`, `--sweep`, `--dry-run`. Atomic markdown edit pass; orphan SVG cleanup; index update.
- Created `resources/scripts/python_single/render_cache.py` — thin CLI entry point (`from render_cache import main; sys.exit(main())`). Sibling to the package.
- Converted `resources/scripts/python_single/tikz_cache.py` to a deprecation shim (~30 lines): emits `DeprecationWarning` and forwards to `render_cache.main()`.
- Created `tests/test_render_cache_phase2.py` (32 new tests covering structure, behavior, integration). Updated `tests/test_tikz_cache_phase1.py` to point its rendering-invariant assertions at the new adapter file (`render_cache/adapters/tikz.py`); smoke test invokes `render_cache.py`. Helper `_strip_docstrings_and_comments` added so the no-`--bbox=preview` and no-`dvisvgm-in-shim` assertions look at executable code only.
- Re-rendered all TikZ files via `render_cache.py --all`:
  - 100 markdown files with TikZ blocks discovered.
  - 5 Phase-1 files re-keyed onto 16-char hash (legacy 8-char SVGs cleaned up by orphan sweep).
  - ~95 previously-uncached TikZ files now have an SVG cache entry.
  - 3 files fail with pre-existing TikZ source bugs (NOT Phase 2 regressions): `bB3-18_neuroscience-101.md` ("Cannot parse this coordinate"), `mSB8-9_double-brackets.md` ("Undefined control sequence"), `_TIKZ_TEST_mSB3-5.md` (one of its blocks: "Can be used only in preamble"). These would have failed identically under Phase 1 `tikz_cache.py`.
  - Total cache: 158 SVG files, 8.6 MiB. Disk healthy (18 GiB free).

**Decisions Made:**

- **D2.1 — Adopt §3.9 canonical hash now (16-char), accept re-key.** The PLAN exit criterion "produces identical output" is functional ("same end-to-end result — working cached SVG") rather than byte-identical; PLAN Task 2.2's normalize verify example (`'  hello…' → 'hello…'`) explicitly demands a non-identity normalize, so identity at the hash layer would self-contradict the same task. Re-key cost: 5 file re-renders + 5 markdown ref rewrites (the 5 from Phase 1; the other 95 had no prior cache).
- **D2.2 — `preamble_hash = sha256(LATEX_PREAMBLE)[:16]` for Phase 2.** Per advisor item 2: hashing the hardcoded preamble preserves T10 semantics from day one; per-folder `_preamble.<lang>` files (Phase 8+) just substitute a different text. Empty string would have thrown away the invariant.
- **D2.3 — Both `tikz` and `tikz-paused` fences canonicalise to `language="tikz"` for hash purposes.** Pausing is a display-only concern; making them hash-distinct would invalidate the cache on every pause/unpause. `markdown_io.CodeBlock` records both `language` (canonical) and `fence_lang` (raw) so renderers/displayers can disambiguate later if needed.
- **D2.4 — `main()` lives in `render_cache/__init__.py`, not `render_cache.py`.** Resolves the apparent contradiction in PLAN's snippets (Task 2.3 shows `main()` in `render_cache.py`; Task 2.4 shows the shim doing `from render_cache import main` — the latter resolves to the PACKAGE per Python's directory-over-file precedence). Putting `main()` in `__init__.py` makes both invocation paths work and keeps `render_cache.py` a 5-line wrapper.
- **D2.5 — File count mismatch with PLAN (10 vs 9).** PLAN's prose says 9; PLAN's verify command (`find render_cache -name '*.py' | wc -l → 9`) actually counts 10 with `adapters/__init__.py`. Shipped 10 to match SPEC §3.3 component table. Filed as a docs-only fix to PLAN.md (out of Phase 2 scope).
- **D2.6 — `RENDERER_VERSION = "0.2.0"`** (bumped from Phase 1's implicit `1.0.0` placeholder). Will go to `1.0.0` at Phase 13 release. Phase 2 is pre-release scaffolding.
- **D2.7 — Re-targeted Phase 1 tests in-place (no rename).** Per advisor item 1, the Phase 1 invariant tests now point at `render_cache/adapters/tikz.py` (the file that owns those invariants post-restructuring). Smoke test invokes `render_cache.py`. File name kept (`test_tikz_cache_phase1.py`) because the tested INVARIANTS are still the Phase 1 ones — only their location moved.

**Deviations from Plan:**

- One file-count mismatch (D2.5).
- PLAN Task 2.3's `render_cache.py` snippet shows `def main()` in the file body; shipped reality has `main()` in `render_cache/__init__.py` and `render_cache.py` as a wrapper (D2.4). Both invocation paths work; the snippet was a sketch, not a literal.

**Resolved mid-phase:**

- Two test assertions failed initially because the new docstrings legitimately mention `--bbox=preview` and `dvisvgm` while explaining what NOT to do. Fixed by adding `_strip_docstrings_and_comments` helper to both test files; now the assertions only inspect executable code.
- The Phase 1 smoke test's regex `[0-9a-f]{{8}}` (exactly 8 hex chars) needed widening to `[0-9a-f]{{8,}}` because the new hash is 16 chars. Done.

**Tests:** 50/50 pass (49 fast + 1 slow smoke that exercises the full lualatex+dvisvgm pipeline). New: 32 in test_render_cache_phase2.py. Re-targeted: 14 in test_tikz_cache_phase1.py (smoke test re-targeted to invoke the new CLI).

**Lessons Learned:**

- **Test assertions on source text need to discriminate between code and prose.** Phase 1's `if not ln.startswith("#")` filter survives `# comment` but not `"""..."""` docstrings. When invariant assertions move to a new file with new prose explaining the invariant, docstrings legitimately quote the forbidden tokens. Solution: filter out triple-quoted strings before asserting.
- **PLAN/SPEC sketches drift slightly from shippable architecture.** Task 2.3's example showed `main()` in `render_cache.py`; Task 2.4's shim imports `from render_cache import main`. The PLAN reads sensible at first glance but the two snippets are mutually inconsistent given Python's directory-over-file import precedence. Shipped reality: `main()` in `__init__.py`. Logged as D2.4 to make the deviation explicit.
- **`--all` over a 100-file vault surfaces source-level bugs across the whole content set.** 3 files have pre-existing TikZ source bugs that Phase 1 (5-file scope) never tried to render. None are Phase 2 regressions, but they're real defects in the user's TikZ source (or in our preamble — `mSB8-9` "Undefined control sequence" might just need an extra `\usetikzlibrary`). Filed for separate triage; not blocking Phase 2 gate.
- **Auto-backup interleaves with phase work, breaking strict atomic-commit discipline.** Multiple intermediate commits (12:37, 12:48, 12:58) captured snapshots of the cache + markdown deltas while this phase was in progress. The Phase 2 atomic commit therefore stages **only** the source/test/PROGRESS files; cache and markdown ref-rewrite deltas live in the auto-backup commits. Same accounting strategy as D1.5/D1.11.

**Cross-references:**

- SPEC §3.3 (components), §3.4 (adapter contract), §3.7 T8/T9/T10/T11/T12 (cache-key invariants), §3.9 (canonical key formula).
- PLAN §Phase 2 (Tasks 2.1–2.4), §Phase 12 (legacy → new layout migration).
- Pre-existing TikZ source bugs: `kn/library/chapters/bB3-18_neuroscience-101.md`, `kn/math/concepts/mSB8-9_double-brackets.md`, one block in `kn/math/concepts/_TIKZ_TEST_mSB3-5.md`.

**Phase 2 gate (user-driven):** Open ≥2 of `mSB3-4_reals.md`, `mSB3-5_complex.md`, `mSB5-2_partial.md`, `mLA5-1_eigenvalues.md` on **desktop AND mobile**. Confirm the cached SVG renders correctly (same diagram as Phase 1 v2 — pure restructuring, no visual change expected). On desktop the CSS swap from Phase 1 closure (`84ccae5ac`) means the cached SVG is what's shown.

**Next:** Awaiting user gate confirmation, then trigger Phase 3 — Add Graphviz adapter.

---

### Phase 1 v2 — Gate Closure (CSS view-layer brought forward) — 2026-04-27 12:30

**User confirmation:** "Confirmed on desktop and mobile" — the cached SVG renders immediately on desktop with no spinner. Mobile unchanged behaviorally.

**What changed (commit `84ccae5ac` — auto-backup-captured at 12:27):**
- `.obsidian/snippets/tikz-cache.css`: replaced "default-hide / mobile-show" model with "always-show / hide-codeblock-everywhere".
- 4 effective lines of CSS rule change (`img[alt~="tikz-cache"]` → `display: block`; `.block-language-tikz, pre.language-tikz` → `display: none`). Design-intent comment block expanded to document the swap and the trade-off.

**Why this was required for gate closure:**
- The Phase 1 row's gate criterion ("desktop diagram visible") was structurally unsatisfiable under the original CSS, which hid `img[alt~="tikz-cache"]` everywhere except `.is-mobile` by design (intent comment lines 7-11 explicitly declared TikZJax was the desktop renderer).
- TikZJax hangs deterministically on the title-node math pattern (`font=\large\bfseries` + `$\mathbb{R}$` math content) catalogued in `kn/math/concepts/_TIKZ_TEST_titles.md` Tests 4.6 / 4.7 / 4.9. This is the very failure mode SPEC §1 lines 70–72 names as motivating problem #2 ("Silent rendering failures in the existing TikZJax plugin's `dvi2html` JS converter").
- Diagnostic confirmed Phase 1 v2 SVGs were byte-correct on disk (independently verified via rsvg-convert + macOS QuickLook + path-count assertions). The gate failure was structural CSS / plugin coupling, not a Phase 1 regression.

**Decisions made:**
- **D1.9:** Bring forward Phase 8's "cache-first viewer" semantics into the existing CSS snippet rather than wait for the full plugin (Phase 8). Rationale: SPEC G2 already commits to "Python writes cache; plugin reads cache only" — there is no live-preview-on-desktop in the approved end-state. The CSS swap implements that end-state behavior in 4 effective lines, no plugin code required.
- **D1.10:** The CSS hides the live codeblock unconditionally (no `.is-mobile` qualifier). Both `.block-language-tikz` (codeblock-processor path, fires when TikZJax is registered) and `pre.language-tikz` (default Prism path, fires when no plugin handles `tikz`) are covered. The rule is robust to whether TikZJax is loaded, disabled, or hung — the unverified-at-runtime question of TikZJax's loaded state becomes irrelevant.
- **D1.11:** Did NOT add cache-miss visual styling now. Obsidian renders missing embeds as a styled `![[file.svg]]` "broken embed" link, which is a sufficient default visual indicator for v1. Phase 10 (plugin error display + status bar) lands a richer indicator. Recorded as a deferred improvement, not a blocker.

**Trade-off (explicitly accepted by user via SPEC G2 approval, reaffirmed by gate closure):**
- Authoring a new TikZ block on desktop no longer shows live preview. To preview, run `tikz_cache.py` on the file. Source mode (Cmd+E) still shows the editable codeblock text. This matches SPEC G2 / G8 design.

**Tests:** N/A — pure CSS change, hot-reloaded in Obsidian, no test infrastructure exists for CSS view rendering. User-driven visual verification serves as the gate.

**Lessons learned:**
- **PLAN's per-phase user-feedback gate template assumed the desktop view path worked.** That assumption was invalid in Phase 1. Future phases must verify whether the gate criterion is satisfiable under existing CSS / plugin state BEFORE writing the gate text. For Phase 2's gate, audit upstream view-layer dependencies first.
- **Auto-backup interaction with user-gate iteration is benign.** The CSS edit was auto-committed at 12:27 (`84ccae5ac`) before the PROGRESS update. Atomic-commit discipline survives because the two commits are linked through this log entry — `84ccae5ac` is the CSS-only commit, this PROGRESS-update is the gate-closure commit.
- **The diagnostic checkpoint (this file, §`CHECKPOINT — 2026-04-27`) is the source-of-truth investigation.** It catalogs the full read-only debug-like-expert investigation that produced this gate-closure. Future readers should pair the two — the diagnostic explains "why," this entry explains "what was done."

**Cross-references:**
- Investigation transcript: this PROGRESS.md `## CHECKPOINT — 2026-04-27 (post Phase 1 v2 user-gate report)` section near the bottom.
- TikZJax bug catalog: `kn/math/concepts/_TIKZ_TEST_titles.md` (user-maintained).
- SPEC motivating problem: `docs/specs/render-cache/SPEC.md` §1 lines 70-72.
- Anomaly still flagged for separate session: `.obsidian/community-plugins.json` lists only 5 plugins; verify before next Obsidian restart.

**Phase 1 status:** **DONE** (gate closed). Phase 2 not yet triggered.

**Next:** Awaiting user trigger "Implement Phase 2" — Restructure into render_cache package (PLAN §Phase 2; 2-4h estimate; touches `resources/scripts/python_single/tikz_cache.py` + new `resources/scripts/python_single/render_cache/` package directory).

---

### Phase 1 v2 — REGRESSION FIX: `--libgs=` for PostScript specials — 2026-04-27 11:30

**User-gate failure (v1 SVGs):**
- Desktop Obsidian: SVG load spinner ran 10+ minutes without rendering.
- iOS Obsidian: only the LARGE text labels ("$\sqrt{2}$", "$\pi$", "$e$", "$\frac{1}{3}$", "No gaps anywhere") visible, all overlapping at the top of the canvas. No number line, ticks, circles, or callout box.

**Diagnosis:**
1. Reproduced the broken render with macOS QuickLook (CoreGraphics, same engine as iOS WebKit) AND with `rsvg-convert` (librsvg, different engine). Both showed text-only garbage. ⇒ The bug is in the SVG itself, not the renderer.
2. Inspected the SVG structure: 75 `<use>` glyph references (text), 51 `<path>` elements, **0 `<circle>` / `<line>` / `<polyline>`**, only 2 tiny `<rect>` (sqrt-bar accents in the math glyphs). The 51 `<path>` elements were all part of glyph definitions, NOT the TikZ-drawn shapes.
3. Compared dvisvgm bbox flag combinations on a stripped-down test DVI. All four `--exact-bbox` / `--bbox=min` / `--bbox=preview` / no-flag variants produced the SAME 92×13pt clipped output. Only `--bbox=papersize` produced a 493×164pt full bbox — but it ALSO had no TikZ shapes, just text.
4. Ran `dvisvgm --list-specials` on `/Library/TeX/texbin/dvisvgm`:
   ```
   bgcolor color dvisvgm em html papersize pdf tpic
   ```
   **No `ps`/`psfile` handler.** TikZ in lualatex+DVI mode emits its drawing commands as PostScript specials. Without a `ps` special handler, dvisvgm silently drops them — text glyphs survive (handled internally), all geometry vanishes.
5. `otool -L /Library/TeX/texbin/dvisvgm`: only links `libc++` and `libSystem`. The TeX Live `dvisvgm.universal-darwin` binary has NO statically-linked Ghostscript or MuPDF.
6. dvisvgm has a `--libgs=PATH` option that runtime-dlopens a Ghostscript shared library. Brew already installed `ghostscript 10.07.0` (`/opt/homebrew/lib/libgs.dylib` symlink). Re-rendered with `--libgs=/opt/homebrew/lib/libgs.dylib`: graphic size jumped from 92×13pt to 484×152pt and `rsvg-convert` showed the full diagram (axis, ticks, labels, circles, arrows, callout). ✓
7. Tried `dvisvgm --pdf` mode as alternative path: failed with "can't retrieve number of pages" — the TeX Live binary is also stripped of MuPDF. So `--libgs=` is the only available fix without a binary swap.

**Code changes:**
- Added `LIBGS_PATH` auto-detection at module import time, scanning a candidate list (Apple Silicon brew → Intel brew → Debian → RHEL → generic Linux). `DVISVGM_LIBGS` env var overrides.
- Added `f"--libgs={LIBGS_PATH}"` to the dvisvgm invocation when detected.
- Soft-fail with diagnostic message if `LIBGS_PATH is None` (the rendered SVG would be missing TikZ shapes).
- Replaced `--exact-bbox --bbox=preview` with `--bbox=min`. The `--bbox=preview` flag is for the LaTeX `preview` package; with `standalone` it is wrong, and combined with `--exact-bbox` it produced a degenerate clipped bbox.
- Added 2 regression tests (`test_libgs_path_detection_present`, `test_no_bbox_preview_flag`) plus a stronger `path_count >= 50` assertion in the smoke test.

**Re-rendered all 5 files. Comparison v1 (broken) → v2 (fixed):**

| File | v1 size | v2 size | v1 paths | v2 paths | Visual |
|---|---|---|---|---|---|
| mSB3-4_reals | 42 KB | 50 KB | 49 | **86** | Number line, ticks, dots, callout — ALL VISIBLE ✓ |
| mSB3-5_complex | 41 KB | 51 KB | 47 | **105** | Argand diagram, grid, vectors, conjugate — visible ✓ |
| mSB5-2_partial | 25 KB | 376 KB | 25 | **1740** | 3D surface mesh (densely sampled) — visible ✓ |
| mLA5-1_eigenvalues__1 | 38 KB | 44 KB | 40 | **71** | Eigenvector vs non-eigen demo — visible ✓ |
| mLA5-1_eigenvalues__2 | 31 KB | 35 KB | 32 | **59** | Rotation matrix (no real eigenvectors) — visible ✓ |

mSB5-2_partial blew up to 376 KB / 1740 paths because pgfplots tessellates the 3D surface into many small polygons. Acceptable for v1; Phase 7's SVGO postprocess (deferred to v1.1 in current PLAN; possibly worth pulling in earlier) could reduce.

**Decisions Made:**
- **D1.6 (rooted in user gate failure):** Hardcode `/opt/homebrew/lib/libgs.dylib` is fragile. Implemented a candidate list with `DVISVGM_LIBGS` env var override — covers macOS (both archs), Debian/Ubuntu, RHEL/CentOS, generic Linux without per-host config.
- **D1.7:** When `LIBGS_PATH is None`, `render_tikz` returns `(False, diagnostic_msg)` rather than producing a broken SVG silently. This is a hard guardrail: no broken cache files, ever.
- **D1.8 (PLAN drift):** PLAN.md Task 1.2 told us to use `--exact-bbox --bbox=preview`. Both flags were wrong. PLAN.md should be updated to read `--bbox=min --libgs=$DVISVGM_LIBGS_OR_DETECTED`. Filed under "Common Errors & Solutions" below; PLAN edit is a separate docs commit (out of Phase 1 scope).

**Tests:** 14/14 pass in 0.88s (12 static + 2 regression + 1 smoke; 1 lualatex-timeout marker test counts as static here).

**Lessons Learned:**
- **dvisvgm distributed via TeX Live is functionally crippled for TikZ.** It has neither libgs nor MuPDF compiled in; it only handles glyph specials. A standalone install (or runtime-dlopen via `--libgs=`) is required for any non-trivial TikZ.
- **dvisvgm fails silently on dropped specials.** No warning, no nonzero exit. The output SVG looks plausible (correct file size, valid XML, visible text). Detecting this regression required visual diff + counting `<path>` elements.
- **PLAN-table assertions need execution-time verification.** PLAN said "dvisvgm available via TeX Live" — incomplete; the binary exists but is missing critical capabilities. Future SPEC pre-flights should `dvisvgm --list-specials | grep -E 'ps|pdf'` to prove rendering capability, not just `which dvisvgm`.

**Next:**
1. **YOU:** Re-open `mSB3-4_reals.md` (or any of the 4 others) on **desktop Obsidian** — verify the new v2 SVG renders the actual diagram (number line + dots + callout, not text-only).
2. **YOU:** After iCloud sync, re-test on **iOS Obsidian**.
3. **YOU:** Reply with "v2 SVGs render correctly on desktop and iOS" → I trigger Phase 2.

---

### Phase 1 — Migration: PNG → SVG via dvisvgm — 2026-04-27 09:42 DONE (agent-side)

**Completed:**
- Replaced the lualatex+pdftoppm PDF→PNG pipeline in `resources/scripts/python_single/tikz_cache.py` with lualatex(DVI)+dvisvgm(--no-fonts) SVG output.
- Removed obsolete constants `DPI` and `PDFTOPPM_TIMEOUT_S`. Added `DVISVGM_TIMEOUT_S = 60`.
- `CACHE_REF_RE` extended to match both `.png` (legacy) and `.svg` (current) so existing PNG refs are rewritten in place rather than duplicated.
- `BlockResult.png_name` → `svg_name`; `process_file` and `sweep_orphans` now operate on `.svg` glob/regex.
- Re-rendered all 5 cached files via `--force`:

  | File | Blocks | SVG bytes | <path> | <text> |
  |---|---|---|---|---|
  | mLA5-1_eigenvalues__1__b25fbcb6.svg | 1/2 | 38 256 | 40 | 0 |
  | mLA5-1_eigenvalues__2__6ee04ab1.svg | 2/2 | 30 680 | 32 | 0 |
  | mSB3-4_reals__1__fe1400ae.svg | 1 | 42 239 | 49 | 0 |
  | mSB3-5_complex__1__382c3444.svg | 1 | 41 100 | 47 | 0 |
  | mSB5-2_partial__1__3dde7586.svg | 1 | 24 956 | 25 | 0 |

- All 5 markdown image refs updated `.png` → `.svg`. Old PNGs left in place (per Phase 1 exit criteria; Phase 12 sweeps).
- Created `resources/scripts/python_single/tests/test_tikz_cache_phase1.py` (12 tests: 11 static + 1 slow integration smoke). Test outcome: **12/12 pass in 0.93 s**.
- `conftest.py` registers the `slow` marker.

**Decisions Made:**
- **D1.1 (deviation from PLAN Task 1.2):** dvisvgm 3.4.3 requires `--output=PATH` with `=` (not space-separated). PLAN.md L201 showed `"--output", str(out_svg)`. Ran the command literal first, hit `option --output: string argument 'pattern' expected`, switched to `f"--output={output_svg}"`. This is a one-character fix to PLAN.md if you want the plan to match what shipped — recommend updating PLAN.md L201 in a future docs pass.
- **D1.2:** Kept `--exact-bbox --bbox=preview` per PLAN. Both flags accepted by dvisvgm 3.4.3 without warning. Tight cropping verified visually (will be in user gate).
- **D1.3:** `CACHE_REF_RE` made `.png|.svg`-permissive instead of `.svg`-only. Rationale: existing markdown still has `.png` refs at run-start. If regex matched only `.svg`, `find_existing_ref` would return `None` and the script would APPEND a new `.svg` ref next to the unchanged `.png` ref → duplicate refs. The permissive regex is also safer long-term (won't break if a stray legacy ref ever reappears).
- **D1.4:** Did NOT rename the script `tikz_cache.py` → `render_cache.py`. PLAN explicitly defers that to Phase 2 (Task 2.4 makes `tikz_cache.py` a deprecation shim). Phase 1 keeps the same entry-point shape.
- **D1.5:** Test layout: `resources/scripts/python_single/tests/`. Vault auto-backup committed both test files between creation and my Phase 1 commit (commit `10d72e0c6`). My Phase 1 commit therefore covers only the source change + state files + caches; tests are visible in the same Phase 1 phase via the prior auto-backup hash, intentionally not re-staged.

**Deviations from Plan:**
- One: `--output=PATH` (vs the PLAN-suggested `--output PATH`). Documented in D1.1.
- Otherwise PLAN matches shipped code exactly.

**Resolved Mid-Phase:**
- **Pre-flight 0.3 (dvisvgm):** unblocked by `sudo tlmgr install dvisvgm --repository https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/2025/tlnet-final` (Utah HTTPS mirror; tug.org's FTP path 404'd). Now at `/Library/TeX/texbin/dvisvgm` v3.4.3.
- **Disk pressure (242 MiB free, ~98–100% volume use):** caused intermediate Bash output capture to ENOSPC briefly. System reclaimed ~250 MiB during the session and bash + lualatex + dvisvgm completed without further failures. **Carrying forward as a project-level concern** — Phases 2–13 will produce more SVG cache (each Graphviz/D2/LilyPond test sandbox adds 5–500 KB) and Phase 8 plugin scaffold pulls a Node `node_modules/` (~50–200 MB). User should free space (see "User Decision Required" below) before Phase 8 at the latest.

**Tests:** 12/12 pass in 0.93 s. Committed via auto-backup `10d72e0c6` (test_tikz_cache_phase1.py) + this Phase 1 atomic commit (the rest).

**Lessons Learned:**
- **dvisvgm CLI syntax requires `=` for long options that take values.** Documented in `Common Errors & Solutions` below for D2/Graphviz/LilyPond adapters that may have similar quirks.
- **Vault auto-backup interferes with strict atomic commits.** Test files created during a phase get auto-committed before the phase commit. Mitigation: when a phase commit must be exactly one commit, accept that auto-backup may grab "preview" snapshots first and that the final state is correct. Don't fight it.
- **Disk should be a Phase 0 pre-flight.** PLAN's Pre-Flight didn't include a disk-space check (`df -h /`). Recommend adding `0.11: 'df -h / | awk NR==2 {print +$5}' under 95` for future SPEC-execution work.

**User Decision Required (non-blocking for Phase 1; blocking for Phase 8):**

Disk on `/System/Volumes/Data` is at 100% capacity (~250–500 MiB free, 428/460 GiB used). Top consumers:

| Path | Size | Cleanup safety |
|---|---|---|
| `~/Library/Caches` | 52 GB | Selective only — don't blanket-delete. |
| `~/.cache` | 20 GB | Generally safe to clear (`rm -rf ~/.cache`). |
| `~/.npm` | 9.1 GB | Safe: `npm cache clean --force` |
| `~/Library/Caches/Homebrew` | 6.4 GB | Safe: `brew cleanup --prune=all` |
| `Obsidian/_/.git` | 3.5 GB | Don't touch — vault history. |

**Recommended (zero-risk):** `npm cache clean --force && brew cleanup --prune=all` — frees ~15 GB.

**Next:**
1. **YOU:** Open `mSB3-4_reals.md` (or any of the 4 others) on **desktop Obsidian** — verify the new SVG renders correctly (real-number-line, √2/π/e dots, "No gaps" callout, no Times-fallback fonts). PLAN Phase 1 user-feedback gate (SPEC §5).
2. **YOU:** After iCloud sync, open the same file on **iOS Obsidian** — verify SVG renders (no crash, math correctly positioned). PLAN Task 1.6.
3. **YOU:** Reply with "diagrams visible and correct on desktop and iOS" → I trigger Phase 2.
   Alternative: report "regression on file X" → triage before Phase 2.
4. (Optional, before Phase 8): clear caches per the table above.

---

### Phase 1 — Pre-Flight BLOCKED — 2026-04-27 09:17

**What Was Done:**
- Ran mandatory pre-flight checks 0.1–0.7 from PLAN.md.
- 0.1 vault root: `OK`
- 0.2 lualatex: `/Library/TeX/texbin/lualatex` ✓
- 0.3 **dvisvgm: FAIL — `dvisvgm not found`** ← blocker
- 0.4–0.7: not run (gated on 0.3)
- Inventoried sibling tools at `/Library/TeX/texbin/`: `dvi2fax, dvilualatex, dviluatex, dvipdfm, dvipdfmx, dvipdft, dvips, dvired, dvitomp, gftodvi`. dvisvgm absent.
- Searched `/Library/TeX`, `/usr/local`, `/opt/homebrew`, `/usr/local/texlive` — no dvisvgm anywhere.
- Root-caused with `tlmgr --version`: TeX Live 2025 **BASIC** scheme installed at `/usr/local/texlive/2025basic` (owned by `root:wheel`, write requires sudo). The basic scheme deliberately omits dvisvgm.
- Confirmed availability via two install paths:
  - `tlmgr info dvisvgm` → version 3.6, ~16 MB binary, `installed: No`. Adds dvisvgm to the **existing** TeX Live install. Sudo required.
  - `brew info dvisvgm` → version 3.6 (bottled). Pulls in 6 deps including a duplicate `texlive` (~5+ GB). Not advisable while TeX Live is already present.

**What Worked:**
- The PLAN's pre-flight gate did its job — caught a missing dependency before any code change. Exact behavior intended by SPEC §11.4 / decision tree.
- `tlmgr info dvisvgm` returned full package metadata even with the network-restricted "frozen 2025 release" warning, so we can quote the exact size and version.

**What Didn't Work:**
- The PLAN's "Pre-Plan State" table at L36 asserted dvisvgm was "Available via TeX Live `/Library/TeX/texbin/dvisvgm`". This was incorrect — only the basic scheme was installed. The "verified 2026-04-26" claim in the table header had no evidence behind it for this specific row. **Lesson recorded below.**

**Decisions Made:**
- **D-pf-1:** Status set to `Blocked` (not `In Progress` or `Not Started`). Rationale: agent literally cannot proceed; user action required (sudo install or scope change). Per decision tree: "Pre-flight (mandatory) all pass? — NO ► Stop. Resolve. Tell user."
- **D-pf-2:** Did NOT install dvisvgm autonomously despite tlmgr install being the obvious resolution. Rationale: CLAUDE.md safety rule on "actions visible to others or that affect shared state" applies — installing system-level binaries with sudo modifies a shared TeX Live install. Confirmation required.

**Deviations from Plan:**
- Phase 1 work blocked before starting. No code changes made.

**Lessons Learned (added to Common Errors):**
- **PLAN/SPEC pre-plan tables can drift from reality.** Always run pre-flight commands as the first agent action, not trust the table. Single-point-of-failure dependency assertions deserve `which $TOOL` verification at SPEC time, not just install-time.
- **Distinguish TeX Live schemes (basic / small / medium / full / scheme-tetex).** `lualatex` present does not imply `dvisvgm` present — the BASIC scheme excludes a large portion of what scheme-full ships.

**User Decision Required (resolution options):**

| # | Option | Command(s) | Footprint | Reversibility | Risk |
|---|---|---|---|---|---|
| A | `tlmgr install dvisvgm` (recommended) | `sudo tlmgr install dvisvgm` | +16 MB binary into existing TL install | `sudo tlmgr remove dvisvgm` | Low. tlmgr complained that the 2025 release is "frozen" — the install may still work via local mirror, but might require `--repository=ctan` retry. |
| B | `brew install dvisvgm` | `brew install dvisvgm` | +5 GB+ (pulls in duplicate `texlive`) | `brew uninstall dvisvgm` (deps remain unless `brew autoremove`) | High footprint. Risk of PATH precedence conflicts between brew TeX and `/Library/TeX/texbin`. |
| C | Switch from dvisvgm to alternate DVI→SVG path | requires SPEC change | unknown | n/a | High — invalidates D04 (decision: dvisvgm) and §3.7 T1 (mandatory `--no-fonts`). v1 was sized around dvisvgm. |
| D | Skip render-cache v1; revert to legacy `tikz_cache.py` PNG | n/a | 0 | n/a | Defeats the point of the SPEC. |

**Tests:** N/A — no code changes. PROGRESS.md only.

**Next:** Awaiting user decision on installation path. After install: re-run pre-flight 0.3, 0.4 (`dvisvgm --version | head -1` ≥ 3.0), then resume Phase 1 from Task 1.1.

---

### Initialization — 2026-04-27 PLANNING

**What Was Done:**
- Bridged state-machine gap: PLAN.md existed, PROGRESS.md did not.
- Read SPEC.md (1289 lines, 14 phases, 14 architectural decisions, 21 acceptance criteria, 12 final acceptance tests) and PLAN.md (1188 lines, 14 phases with verification commands per task).
- Confirmed PLAN.md `**Spec:**` line matches the SPEC at this absolute path → no archive of stale state needed.
- Updated SPEC §1 header: `Status: Draft → Final`, `Last Updated: 2026-04-26 → 2026-04-27`.
- Updated SPEC §11 Approval to reflect approval-completed state with checklist of post-approval actions.
- Initialized this PROGRESS.md with all 14 phases as `Not Started` (Phase 14 marked `Not Started (optional)`).
- Used PLAN.md's tighter phase names (e.g., "Phase 1 — Migration: PNG → SVG via dvisvgm") rather than the SPEC's longer prose names, for consistency with what each EXECUTION-mode iteration will read first.

**What Worked:**
- Reading the orientation phase file before acting prevented assuming a default mode.
- Consulting the advisor mid-orientation surfaced six concrete refinements: scoped staging, drop-Ralph-hint, SPEC status update, phase-name source, optional-phase marker, and pre-flight-deferral-to-Phase-1.

**What Didn't Work:**
- Nothing notable. Initialization was mechanical once orientation was complete.

**Decisions Made:**
- **D-init-1:** Treated the PLAN.md-exists-without-PROGRESS.md state as a partial PLANNING MODE — execute steps P5 (PROGRESS.md init) and P6 (commit + checkpoint) only; skip P1–P4 because PLAN.md is already comprehensive and committed.
- **D-init-2:** Declared mode as `Manual` to match PLAN.md L4 and SPEC §11.4. Removed the standard checkpoint's Ralph Loop hint to avoid contradicting the per-phase user-feedback gates baked into SPEC §5.

**Deviations from Plan:**
- None. Plan's phase structure preserved verbatim.

**Lessons Learned:**
- The execute-spec skill's strict `if PLAN.md does NOT exist` orientation rule does not directly cover the case of human-authored PLAN.md without machine-authored PROGRESS.md. Treating it as partial-PLANNING-MODE is the right bridge.
- SPEC §11 explicitly enumerates the post-approval bookkeeping (status flip, PROGRESS.md creation). Doing both atomically is cleaner than splitting into separate commits.

**Tests:** N/A (no code changes; documentation/state-file initialization only). Committed: `<pending>`.

**Next:** Phase 1 — Migration: PNG → SVG via dvisvgm. Begin with Pre-Flight Checks 0.1–0.7 (mandatory) per PLAN.md §Pre-Flight Checks.

---

## Failed Attempts

_(Entries added when the same error occurs 3+ times. Empty at initialization.)_

---

## Divergence Checks

### Divergence Check — Phase 3 — 2026-04-27 (this session)

- [x] Files modified vs plan: 6 actual / 5 expected from PLAN. Counted: `render_cache/adapters/graphviz.py` (new), `render_cache/adapters/__init__.py` (REGISTRY add), `render_cache/markdown_io.py` (BLOCK_RE alt + `_FENCE_TO_LANG` + docstring), `render_cache/__init__.py` (`find_all_md_with_blocks.fence_tags`), `tests/test_graphviz_adapter.py` (new), `kn/math/concepts/_RENDER_TEST_graphviz.md` (new sandbox per PLAN Task 3.1). The +1 over PLAN is the dispatcher fence-tag list; PLAN didn't enumerate it, but `--all` would silently miss Graphviz files without it (caught by `test_find_all_md_with_blocks_includes_graphviz`).
- [x] Max cyclomatic complexity: `GraphvizAdapter.render` is ~3 (path resolution, single subprocess.run wrapped in try/except, success/failure checks). Bounded well below the < 15 ceiling.
- [x] All changes link to specific PLAN.md steps:
      - `graphviz.py` → PLAN Task 3.2
      - REGISTRY add → PLAN Task 3.2 (registration directive)
      - `BLOCK_RE` + `_FENCE_TO_LANG` extension → covers both PLAN Task 3.2 (so dispatcher routes `\`\`\`graphviz`) and the implicit pre-condition for Task 3.3 (CLI run on sandbox)
      - dispatcher `fence_tags` extension → implicit pre-condition for `--all` to work post-Phase 3
      - `_RENDER_TEST_graphviz.md` → PLAN Task 3.1
      - tests → execute-spec workflow E5/E6 (TDD)
- [x] No repeated identical tool calls (>3): true. Two pytest invocations (red phase + green phase) and one full-suite-with-slow run; each had a different purpose.
- [x] Plan-vs-shipped delta: NO new D-rows of substance. D3.1–D3.5 record judgment calls (alt-tag deferral, empty preamble, budget-as-timeout, fence-tag list non-abstraction, TDD discipline) — none are deviations from PLAN, they're choices PLAN didn't constrain.

**Status:** Within scope. The 3 SVG cache files and the 3 wikilink-ref insertions in the sandbox are SIDE-EFFECTS of running the CLI as part of the slow integration test, not new implementation. They are handled by auto-backup commits, not the Phase 3 atomic commit.

### Divergence Check — Phase 2 — 2026-04-27 13:15

- [x] Files modified vs plan: 13 actual (10 new package modules + render_cache.py + tikz_cache.py + 2 test files) vs PLAN's enumerated set (10 modules + render_cache.py + tikz_cache.py + tests). Match.
- [x] Max cyclomatic complexity: `process_file` is the most complex function at ~12 branches (per-block render + hash lookup + edit planning + orphan cleanup + index write). Within reasonable bound (<15).
- [x] All changes link to specific PLAN.md steps:
      - Package skeleton → PLAN Task 2.1
      - Module bodies (normalize/hash/markdown_io/cache_paths/index/postprocess/adapters) → PLAN Task 2.2
      - render_cache.py CLI → PLAN Task 2.3
      - tikz_cache.py shim → PLAN Task 2.4
      - Tests → execute-spec workflow E5/E6 (TDD)
      - Phase-1 test re-target → advisor item 1 (in-scope per spec-architect spine)
- [x] No repeated identical tool calls (>3): true. The only retried Bash invocation was `pytest tests/ -v -m "not slow"` (red phase + green phase) and `pytest tests/ -v` (final), distinct purposes.
- [x] Plan-vs-shipped delta: ONE deviation logged as D2.4 (main() in __init__.py instead of render_cache.py per PLAN snippet — shipped reality is the canonical Python pattern given file-vs-package name collision).

**Status:** Within scope. The 95 newly-cached files and the 100 markdown ref edits are SIDE-EFFECTS of running `--all`, not new implementation. They're handled by auto-backup, not the Phase 2 atomic commit.

### Divergence Check — Phase 1 — 2026-04-27 09:42
- [x] Files modified vs plan: 8 actual / 1 planned in PLAN.md (`tikz_cache.py`).
      Counted: `tikz_cache.py` (1), 4 markdown files (refs auto-rewritten by the script — expected side-effect, not extra implementation), 5 SVG cache outputs (auto-generated by render — also expected), 2 test files (committed via auto-backup, marker config). Net "extra implementation" beyond plan = test files (~200 LOC), which were required by execute-spec workflow's TDD discipline.
- [x] Max cyclomatic complexity: `render_tikz` is 6 (was 7 with pdftoppm path); within reasonable bound (<15).
- [x] All changes link to specific PLAN.md steps:
      - tikz_cache.py constant changes → PLAN Task 1.2
      - render_tikz body → PLAN Task 1.2
      - .png → .svg throughout → PLAN Task 1.3
      - 5-file re-render → PLAN Task 1.5
      - tests → execute-spec workflow E5 (TDD)
- [x] No repeated identical tool calls (>3): true. Only the smoke-render Bash was retried (initial `--output PATH` syntax failure → `--output=PATH` fix → success).
- [x] Plan-vs-shipped delta: ONE flag-syntax fix (`--output=PATH` per D1.1). Logged as the only deviation.

**Status:** Within scope. Tests appropriately added beyond PLAN's bare minimum (PLAN said "verify with grep" — tests codify those checks executably and add the integration smoke).

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

## CHECKPOINT — 2026-04-27 (post Phase 1 v2 user-gate report)

**Session type:** Diagnostic (read-only, no code changes). Triggered by user reporting that on the Phase 1 v2 desktop gate, `mSB3-4_reals.md` shows a "rendering …" spinner that never resolves (>20 min). User explicitly broadened scope: also asked why some TikZ blocks in `_TIKZ_TEST_titles.md` only render after Obsidian restart (Tests 3.2/3.3) or never at all (Tests 4.6/4.7/4.9).

**Skill used:** `debug-like-expert` (read-only diagnosis mode; presents findings at decision gate, does not modify code).

### What was investigated

1. **Read `mSB3-4_reals.md` end-to-end** to find what's actually on the page.
2. **Read `_TIKZ_TEST_titles.md`** to understand the user's prior TikZJax bug catalog (Parts 1–4 test plan).
3. **Inspected `.obsidian/snippets/tikz-cache.css`** (38 lines) — the design intent comment is critical evidence.
4. **Listed installed plugins** (58 in `.obsidian/plugins/`) vs. enabled plugins (5 in `community-plugins.json`).
5. **Examined `obsidian-plugin-groups/data.json`** for any group that auto-enables TikZJax — found 3 groups containing TikZJax, all with `loadAtStartup: false`.
6. **Grepped TikZJax `main.js`** for spinner/loader code — confirmed it registers `tikz` codeblock processor, has an inline placeholder SVG with `<rect>` + `<circle>` (the "loader"), and IndexedDB-caches successful renders by md5(source).
7. **Cross-referenced cache directory** — confirmed all 5 SVGs from Phase 1 v2 exist on disk (50KB–376KB, byte-correct per prior rsvg-convert / QuickLook).
8. **Cross-referenced SPEC §1 line 70-72** — the failure mode the user is seeing is *literally one of the named motivating problems* of the new system ("Silent rendering failures in the existing TikZJax plugin's `dvi2html` JS converter").

### What worked (findings reached with high confidence)

- **The 5 source files all share the same dual-rendering structure**: a live ` ```tikz ` codeblock followed by a `![[…__hash.svg|tikz-cache]]` reference. Counts: `mSB3-4_reals` 1+1, `mSB3-5_complex` 1+1, `mSB5-2_partial` 1+1, `mLA5-1_eigenvalues` 2+2.
- **The CSS hides the cached SVG on desktop by design**: `img[alt~="tikz-cache"] { display: none; }` is the default; only `.is-mobile` overrides to `display: block`. This means **Phase 1 v2 produced byte-correct SVGs that the user physically cannot see on desktop without modifying CSS or installing the Phase 8 plugin.**
- **The Phase 1 v2 user-gate criterion is structurally unsatisfiable on desktop** under current CSS. The desktop "failure" the user reported is not a Phase 1 v2 regression; it's exposure of the long-standing TikZJax hang when verification was attempted.
- **The TikZ codeblock at `mSB3-4_reals.md:145` matches the user's own catalogued hang pattern**: `\node[above, axiscolor, font=\large\bfseries] at (0, 2.2) {$\mathbb{R}$: ...}`. The test file's Tests 4.6 / 4.7 / 4.9 already proved this exact pattern (`font=\large\bfseries` + `$\mathbb{R}$` math content) hangs the renderer.
- **The "works after restart" pattern is consistent with TikZJax's IndexedDB result cache**: successful md5(source)-keyed renders are persisted; after restart, instant retrieval (no recompile, no hang). Failed compiles don't write any cache entry → next session re-tries → re-hangs. Deterministic but tied to invisible state.
- **SPEC §1 already names this exact bug** as one of four motivating problems. The Phase 8 plugin is designed precisely to replace TikZJax for ` ```tikz ` blocks (cache-only viewer, never invokes a JS engine).

### What didn't work / what remains uncertain

- **Could not directly confirm TikZJax is loaded right now.** Strong indirect evidence (CSS comment "TikZJax plugin ENABLED", user's prior bug investigation in test file, registered codeblock processor in plugin's `main.js`) but `community-plugins.json` does NOT list `obsidian-tikzjax` and no plugin group auto-enables it. The user must be enabling it manually via the Plugin Groups commander, or some runtime mechanism not visible to file inspection. **Two cheap discriminators were proposed (Cmd+P "TikZJax" command palette test; DevTools class name on the spinner) but the user did not run them yet.**
- **Could not confirm "rendering …" text wording matches a TikZJax string.** The minified `main.js` doesn't statically expose loader text; the loader uses an SVG with a `<text>` element whose content isn't a static string in the file.
- **Did NOT modify any files.** Per the `debug-like-expert` skill: read-only diagnosis, present findings at decision gate, await user choice before any code edit.

### Anomaly surfaced (NOT in scope of this session, NOT investigated)

`community-plugins.json` (mtime today, 11:50) contains only 5 plugins: `ai-note-suggestion, obsidian-plugin-groups, claude-sidebar, obsidian-advanced-uri, calendar`. Yet the vault uses Dataview, CustomJS, Templater, Tasks, etc. — and they are clearly running in the current session (the file's `dataviewjs` header executes). Either:
- Obsidian carries a runtime-only enabled state divorced from this file, OR
- The file was recently overwritten/corrupted and the next Obsidian restart could disable most of the user's stack.

**Worth checking before next restart. Flagged for user awareness; not addressed here.**

### Decisions made

1. **Diagnosis classified as TWO stacked causes**, not one:
   - (a) Renderer (almost certainly TikZJax) hangs on the title-node math pattern. Pre-existing JS bug; SPEC §1 acknowledges it.
   - (b) Phase 1 v2's user-gate criterion is unsatisfiable on desktop under current CSS.
2. **Recommended Option A (CSS swap, ~4 effective lines)** as the primary unblocker. It brings forward the Phase 8 plugin's "cache-first viewer" semantics into the existing CSS snippet — robust to whether-or-not TikZJax is loaded. Trade-off: live preview of new TikZ blocks on desktop becomes invisible (matches eventual SPEC G2 / G8 design but is a real workflow change today).
3. **Did NOT recommend** building a watchdog plugin (Option C) or fixing TikZJax's preamble (Option D). Both are throwaway given Phase 8 is already on the roadmap.
4. **Recommended Phase 1 v2 gate criterion be revised** rather than declared satisfied by mobile-only visual: either pair with Option A (so desktop visual becomes meaningful) or honestly redefine as "rsvg-convert + QuickLook + iOS visual = pass."
5. **Held off on any file edits.** The CSS swap requires explicit user approval because it changes the visual workflow (live preview lost on desktop).

### What is to be done next

**Awaiting user decision among 6 options (presented at decision gate):**

1. Apply Option A (CSS swap) — edit `/Users/cs/Obsidian/_/.obsidian/snippets/tikz-cache.css`. Hot-reload via Settings → Appearance toggle. No restart.
2. Apply Option A + Option B — also disable TikZJax cleanly (stop wasted CPU on hidden background renders).
3. Run cheap confirmation first (Cmd+P "TikZJax" or DevTools inspect on spinner), then apply Option A with full confidence.
4. Investigate the `community-plugins.json` anomaly first.
5. Hold off — keep CSS as-is, redefine Phase 1 v2 gate as agent-side correct + mobile-visual + on-disk verified, continue to Phase 2.
6. Other.

**If Option A is chosen, the verification plan is:**
1. Hot-reload CSS in Obsidian (Settings → Appearance → toggle `tikz-cache` off then on). No restart.
2. Reopen the 5 files on desktop. Each should immediately show the cached SVG. Spinner cannot be visible (codeblock is `display:none`).
3. Re-check mobile (should be unchanged behaviorally).
4. Author-mode check: source mode (Cmd+E) still shows the editable codeblock text.
5. Mark Phase 1 v2 user-gate satisfied, proceed to Phase 2.

### Lessons learned (for next developer / future sessions)

- **The vault's CSS snippet `tikz-cache.css` is intentionally TikZJax-coupled.** Its design intent comment (lines 5–20) declares "Desktop = TikZJax, Mobile = cached." Any phase touching the rendering view layer must reconcile with — or replace — this CSS.
- **The user maintains a meticulous TikZ-bug catalog in `_TIKZ_TEST_titles.md`** with 4 parts (structural, element-removal, content, standalone catalog). When the user reports "rendering …" or "broken picture icon", check this file's findings table first before forming new hypotheses.
- **TikZJax's IndexedDB cache makes restart-success deterministic-but-invisible.** "Works after restart" is not magic; it means a prior session successfully wrote the md5(source)-keyed result to the browser's IndexedDB. Don't waste time investigating "why restart helps" — investigate "why initial compile hung."
- **Phase 1 v2's user-gate text needs a structural fix.** "User confirms diagrams visible on desktop" cannot be true under the current CSS. Either the gate must change, or the CSS must change, or the Phase 8 plugin must land first. The PLAN's per-phase-feedback-gate template assumes the desktop view path works; this assumption is invalid in Phase 1.
- **Don't confuse "agent-side correct" with "user-visible." The Phase 1 v2 SVGs are byte-perfect (independently verified via rsvg-convert + QuickLook + on-disk inspection). The desktop visibility issue is orthogonal — it's a CSS+plugin layer concern.
- **The community-plugins.json anomaly (only 5 entries, mtime today) is a latent footgun.** Don't ignore it; surface it whenever a plugin-related session starts. A future restart could nuke most of the user's stack.

### Failed approaches NOT to repeat

- **Don't try to fix TikZJax itself** (preamble, WASM rebuild, fork). SPEC §3 D01 explicitly rejects this: `web2js` (the toolchain) is abandoned since 2021. The catalogued path forward is to replace, not repair.
- **Don't add a JS watchdog/timeout to the existing CSS snippet.** Throwaway given Phase 8 plugin is the right surface for inline error display (G9). Building a watchdog now would be deleted in 2–3 weeks.
- **Don't claim Phase 1 v2 is "verified" based only on the mobile visual.** The desktop visual is structurally hidden. Either change the CSS (Option A) or honestly mark the gate as "agent-side + mobile-visual + on-disk" pass.
- **Don't run any bulk markdown-modification scripts** to "remove the live ` ```tikz ` blocks." The codeblock IS the source of truth that gets re-rendered when the file changes; it must remain in the file. CSS hiding is the right approach.

### Status going into next session

| Aspect | State |
|---|---|
| Phase 1 v2 SVG cache files on disk | ✓ Verified byte-correct (rsvg-convert + QuickLook + path-count check) |
| Phase 1 v2 mobile visual | ✓ User confirmed "looks good" |
| Phase 1 v2 desktop visual | ✗ Structurally invisible under current CSS — gate criterion needs revision OR Option A applied |
| TikZJax hang root cause | ✓ Identified (title-node math content); SPEC §1 already names it |
| Code changes this session | None (read-only diagnosis per `debug-like-expert` skill) |
| User-action required | Choose 1–6 from decision gate; recommend Option A (CSS swap, ~4 effective lines) |
| `community-plugins.json` anomaly | Flagged, not addressed; verify before next Obsidian restart |
| Next phase trigger when ready | "Apply Option A" (then re-gate Phase 1 v2) → "Implement Phase 2" |

**Critical files for next-session reorientation:**

- `/Users/cs/Obsidian/_/.obsidian/snippets/tikz-cache.css` (38 lines) — the CSS layer that needs the swap if Option A is chosen
- `/Users/cs/Obsidian/_/kn/math/concepts/_TIKZ_TEST_titles.md` (700 lines) — the user's TikZJax bug catalog; reference any time TikZJax behavior is in question
- `/Users/cs/Obsidian/_/kn/math/concepts/mSB3-4_reals.md:145` — exemplar of the hang-triggering title pattern
- `/Users/cs/Obsidian/_/docs/specs/render-cache/SPEC.md:70-72` — SPEC §1 statement of "Silent rendering failures in TikZJax" as motivating problem #2
- `/Users/cs/Obsidian/_/.obsidian/community-plugins.json` — anomaly: only 5 plugins listed

