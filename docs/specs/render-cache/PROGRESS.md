# Progress Log — Obsidian Render Cache

**Spec:** `/Users/cs/Obsidian/_/docs/specs/render-cache/SPEC.md`
**Plan:** `/Users/cs/Obsidian/_/docs/specs/render-cache/PLAN.md`
**Status:** Blocked at Phase 1 pre-flight (dvisvgm not installed — user decision required)
**Mode:** Manual (user-driven phase progression)
**Started:** 2026-04-27
**Last Updated:** 2026-04-27 09:17

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
| Phase 1 — Migration: PNG → SVG via dvisvgm | Blocked | 2026-04-27 09:17 | | | | | **BLOCKED** at pre-flight 0.3: dvisvgm not installed. TeX Live BASIC scheme. User decision required. |
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

_(Entries added after each phase completion. Empty at initialization.)_

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
