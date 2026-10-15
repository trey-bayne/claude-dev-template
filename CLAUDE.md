# CLAUDE.md — {{PROJECT_NAME}}

> **Read this file first, every session. Then check TASKS.md for current phase and first
> incomplete task. Do not begin work until you know where you are.**

---

## Project Identity

**Project name:** {{PROJECT_NAME}}
**Location:** {{PROJECT_PATH}}
**Owner:** {{GITHUB_USER}}
**GitHub repo:** {{GITHUB_REPO}}
**Purpose:** {{PURPOSE_ONE_PARAGRAPH}}

---

## Critical Constraints

<!-- These are the non-negotiables. Claude Code must not violate these under any
     circumstances. If a task seems to require violating one, stop and ask. -->

1. {{CONSTRAINT_1}}
2. {{CONSTRAINT_2}}
3. {{CONSTRAINT_3}}
<!-- Add/remove as needed. Keep these short, absolute, and action-oriented. -->

---

## Architecture Snapshot

<!-- 3–5 lines max. The full architecture lives in docs/ARCHITECTURE.md.
     This is only what Claude needs to remember between every single task. -->

{{ARCHITECTURE_SNAPSHOT}}

**Full architecture:** `docs/ARCHITECTURE.md`

---

## Technology Decisions — Do Not Relitigate

| Component | Decision | Reason |
|---|---|---|
| {{COMPONENT}} | {{DECISION}} | {{REASON}} |

**Full decision log:** `docs/DECISIONS.md`

---

## Phase Overview

| Phase | Name | Goal |
|---|---|---|
| 1 | {{PHASE_1_NAME}} | {{PHASE_1_GOAL}} |
| 2 | {{PHASE_2_NAME}} | {{PHASE_2_GOAL}} |
<!-- Extend as needed -->

**Current phase tasks:** `TASKS.md`
**Phase implementation notes:** `docs/PHASE_NOTES.md`

---

## Promotion workflow

<!-- BOOTSTRAP: this project answered YES to the two-branch promotion question.
     If it answered NO, delete this whole section — and /dev-build, /ship,
     /phase-release and /phase-rollback were not installed. -->

**Dev branch:** `{{DEV_BRANCH}}` — all work happens here. Never build prod from it.
**Stable branch:** `{{STABLE_BRANCH}}` — only ever reached by a promotion command.

```
  work on {{DEV_BRANCH}}
      │
      ├── /phase-auto ──────── review → build → test, all on {{DEV_BRANCH}}
      │                        never pushes, never touches prod
      │
      ├── /dev-build ───────── commit + push {{DEV_BRANCH}}, rebuild dev stack
      │                        test at {{DEV_URL}}
      │
      ├── /ship ────────────── asks you to confirm, merges {{DEV_BRANCH}} → {{STABLE_BRANCH}},
      │                        rebuilds prod at {{PROD_URL}}, returns to {{DEV_BRANCH}}
      │
      ├── /phase-release ───── the tagged variant of /ship: reads the version and tagline
      │                        from the Phase Index table in TASKS.md, tags v{version},
      │                        pushes both, deploys, verifies health
      │
      └── /phase-rollback ──── emergency only: resets {{STABLE_BRANCH}} to the previous
                               release tag, force-pushes with --force-with-lease,
                               redeploys. {{DEV_BRANCH}} is never touched.
```

Rules that hold regardless of what a command says:
- Promotion to prod is always a human decision. `/phase-auto` never ships.
- `{{STABLE_BRANCH}}` is never force-pushed except by `/phase-rollback`, and only
  with `--force-with-lease`.
- Rolling back code does not roll back data. If a release included a schema migration,
  a forward-fix is usually safer than a rollback.

---

## Coding Standards

<!-- Keep this to the non-obvious rules that Claude would not infer from the stack itself.
     Language conventions Claude already knows don't belong here. -->

- {{STANDARD_1}}
- {{STANDARD_2}}

---

## Port / Service Map

| Service | Internal port | Dev/tunnel port |
|---|---|---|
| {{SERVICE}} | {{PORT}} | {{TUNNEL_PORT}} |

---

## Command Usage Rules

<!-- Rules specific to this project's allowlist. See .claude/settings.json for the
     full permission set. -->

- {{COMMAND_RULE_1}}
- {{COMMAND_RULE_2}}

---

## Session Startup Checklist

The session-start hook runs automatically and shows service health + git status.
After the hook output, do this before any other action:

1. Read this file completely
2. Read TASKS.md → find current phase → find first incomplete task
3. Begin work on that task

## Session End Checklist

Before ending any session:

1. Mark completed tasks in TASKS.md with today's date
2. Note any blockers, decisions, or deviations in TASKS.md under the relevant phase
3. Commit all changes with a descriptive message
4. Confirm services still healthy (hook output or manual check)
5. Update `## Resume Here` in TASKS.md to the next task
