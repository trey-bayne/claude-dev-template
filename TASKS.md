# TASKS.md — {{PROJECT_NAME}} Build Tracker

> Claude Code: update this file after every completed task.
> Mark done tasks with [x] and the date: [x] {{TODAYS_DATE}}
> Add blockers as indented notes under the affected task.
> Keep "## Resume Here" current — any session should be able to pick up in 30 seconds.

---

## Resume Here

**Current phase:** 1 — {{PHASE_1_NAME}}
**Next task:** 1.1 — {{FIRST_TASK}}
**Notes:** {{STARTING_NOTES}}

---

## Phase Index

> One row per phase. `/phase-release` reads the **Release** column: a version number plus a
> plain-language tagline marks a phase as a shippable release; `—` means this phase is not a
> release boundary. Keep Status current — `/phase-release` only considers `Complete` rows.
>
> Projects that deploy from a single branch (no `/phase-release`) still benefit from this
> table as a phase map; just leave every Release cell as `—`.

| Phase | Name | Tasks file | Status | Release |
|---|---|---|---|---|
| 1 | {{PHASE_1_NAME}} | TASKS.md | Not started | — |
| 2 | {{PHASE_2_NAME}} | TASKS.md | Not started | — |
<!-- Tasks file is TASKS.md for every phase — the commands read the task list from
     this file directly and do not resolve per-phase files.
     Release example: **1.0** — first end-to-end working stack -->

---

## Phase 1 — {{PHASE_1_NAME}}

**Goal:** {{PHASE_1_GOAL}}

- [ ] 1.1 — {{TASK}}
- [ ] 1.2 — {{TASK}}

<!-- Do not add "commit the phase" or "advance Resume Here" tasks. /phase-run already makes
     the phase-complete commit, and /phase-test advances `## Resume Here` on a clean pass.
     A task that advances it early makes /phase-test test the NEXT phase's Definition of
     Done against code that was never written, and skip a phase. -->

---

## Phase 2 — {{PHASE_2_NAME}}

**Goal:** {{PHASE_2_GOAL}}

- [ ] 2.1 — {{TASK}}

---

<!-- Repeat pattern for all phases -->

---

## Decisions Log

> Record architectural decisions made during the build.
> Format: [date] decision — reason

- [pending] {{FIRST_PENDING_DECISION}}

---

## Blockers Log

> Record blockers encountered during the build.
> Format: [date] task X.Y — blocker description — resolution

(none yet)
