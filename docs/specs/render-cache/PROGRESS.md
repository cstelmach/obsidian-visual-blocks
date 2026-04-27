# Progress Log — Obsidian Render Cache

**Spec:** `/Users/cs/Obsidian/_/docs/specs/render-cache/SPEC.md`
**Plan:** `/Users/cs/Obsidian/_/docs/specs/render-cache/PLAN.md`
**Status:** Phase 1 agent-side complete; awaiting USER iOS gate (Task 1.6) before Phase 2
**Mode:** Manual (user-driven phase progression)
**Started:** 2026-04-27
**Last Updated:** 2026-04-27 09:42

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
| Phase 1 — Migration: PNG → SVG via dvisvgm | DONE (agent) | 2026-04-27 09:24 | 2026-04-27 09:42 | _pending_ | 12/12 ✓ | ~18 min | Agent-side complete. **USER iOS gate (Task 1.6) pending before Phase 2.** |
| Phase 2 — Restructure into render_cache package | Not Started | | | | | | 2–4h est. Depends on Phase 1. |
| Phase 3 — Add Graphviz adapter | Not Started | | | | | | 1–2h est. Parallelizable with 4–7 after Phase 2. |
| Phase 4 — Add D2 adapter | Not Started | | | | | | 1–2h est. Parallelizable with 3,5–7. |
| Phase 5 — Add LilyPond adapter | Not Started | | | | | | 2–3h est. Parallelizable. |
| Phase 6 — Add RDKit adapter | Not Started | | | | | | 2–3h est. Parallelizable. |
| Phase 7 — Apply SVG postprocessing hardening | Not Started | | | | | | 4–6h est. Depends on Phase 2. |
| Phase 8 — Plugin scaffold | Not Started | | | | | | 4–6h est. Parallelizable with 3–7. Node ≥18 required. |
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
