# Documentation Index — {{PROJECT_NAME}}

> Claude Code: this is your navigation map. When you need detail beyond CLAUDE.md,
> start here to find the right file rather than scanning the whole repo.

---

## I need to understand the overall system

→ `PROJECT_BRIEF.md` — What this is, why it's built this way, what it is not
→ `docs/ARCHITECTURE.md` — Data flows, service relationships, ownership model

## I'm starting a new session

→ `CLAUDE.md` — Critical constraints, port map, standards, session checklists
→ `TASKS.md` → `## Resume Here` — Exactly where to pick up

## I'm working on Phase [N]

→ `TASKS.md` → Phase N section — Checklist of tasks
→ `docs/PHASE_NOTES.md` → Phase N section — Implementation notes and gotchas

## I want to run a whole phase without babysitting it

→ `/phase-auto` — Chains review → build → test-and-fix with no approval prompts.
  Stops only at its five safety hatches. Never ships, never pushes, never touches prod.
→ `.claude/commands/phase-auto.md` — The hatch table and design rules, if you want to
  know exactly when it will stop and ask you something.

## I need a command or quick reference

→ `docs/QUICK_REF.md` — All service commands, secret generation, tunnel setup
→ `/prj-manage` — Audit Docker image ages and dependency versions; create Phase M tasks
→ `/prj-drift` — Compare this project's commands against the claude_dev template
→ `/prj-convert` — Convert an existing project to claude_dev format (global install for non-claude_dev projects)

## I need to review the whole codebase, not just one phase

→ `/codebase-review` — Parallel Opus audit, one agent per domain; saves a dated report
  to `docs/`. Expensive — budget ~50k tokens per domain.

## I need to deploy, or undo a deploy

→ `CLAUDE.md` → Promotion workflow — the branch model and which command does what
→ `/dev-build` → `/ship` — promote to prod · `/phase-release` — the tagged variant
→ `/phase-rollback` — reset stable to the previous release tag

## I need to understand an architecture or tech decision

→ `docs/ARCHITECTURE.md` — Full diagrams and service interaction maps
→ `docs/DECISIONS.md` — Why each technology was chosen; do not relitigate

## I need to check environment variables

→ `docs/ENV_VARS.md` — Full variable listing with descriptions
→ `.env.example` — The authoritative key list for the project

## I hit a blocker or something unexpected happened

→ `TASKS.md` → `## Blockers Log` — Record it there
→ `docs/PHASE_NOTES.md` — Check if it was anticipated in the phase notes

## I need to understand permissions / what commands I can run

→ `PERMISSIONS.md` — Human rationale for all allow/deny rules
→ `.claude/settings.json` — The actual enforced ruleset

## I'm adding a new feature to a completed system
→ docs/SYSTEM_STATE.md — established patterns, current state, what exists
→ docs/DECISIONS.md — why things were built the way they were
→ docs/ARCHITECTURE.md — how services connect
