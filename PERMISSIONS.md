# Claude Code Permissions — {{PROJECT_NAME}}

The JSON block below goes into `.claude/settings.json` (already placed there by bootstrap).
This file serves as the human-readable rationale for every rule.
Update both this file and `.claude/settings.json` together if rules change.

---

## What Is Allowed and Why

**git** — Full git access. Commits, branches, pushes throughout the build.

**docker / docker compose** — Full Docker access. Primary build and run tool.
Claude Code will bring services up/down, check health, run init containers.

**File operations (ls, cat, find, grep, mkdir, cp, mv, rm, touch)** — Standard
navigation and manipulation within the project directory.

**chmod / chown** — Setting permissions on Docker volumes and init scripts.

**openssl rand** — Secret generation during initial setup only.

**curl to localhost** — Health checks and API testing against local services.
External curl is blocked — Claude Code should not fetch arbitrary URLs.

**jq** — Parsing JSON from health checks and API responses.

**python3 (limited)** — Running init scripts from designated paths only.

**Agent tool (sub-agents at Opus, Sonnet and Haiku)** — The Agent tool uses the
session's existing credentials. No ANTHROPIC_API_KEY required. Sub-agents run within
the same permission context as the current session — they cannot do anything this
file does not already allow, and they cannot prompt the user.

Which commands spawn sub-agents, and at which model:

| Command | Sub-agents |
|---|---|
| `/phase-review` | Opus — the reviewer |
| `/phase-run` | Opus — fix escalation on tries 2–3 of a failed task |
| `/phase-auto` | Opus reviewer, Sonnet builder, Haiku tester, Opus fixer |
| `/codebase-review` | one Opus agent per review domain, launched in parallel |
| `/phase-complete`, `/phase-test`, `/phase-release`, `/phase-rollback`, `/prj-drift` | Haiku |

Because `/codebase-review` launches one agent per domain simultaneously, a full audit
is the most token-expensive operation in the toolchain. That is a cost consideration,
not a permission one — it cannot exceed the session's own access.

**git push --force-with-lease (in /phase-rollback only)** — This is the one command in
the toolchain that rewrites published history, and it is allowed deliberately: rolling
a broken release back off the stable branch requires it. Two guards make it safe enough
to allow rather than block:

- It is **never a bare `--force`**. `--force-with-lease` aborts if the remote moved since
  the last fetch, so it cannot silently discard someone else's push.
- It only ever targets the **stable branch**, resetting it to an existing release tag.
  The dev branch is never touched, so no in-progress work is at risk.

Every other force-push remains denied. If a rollback needs more than this, it is a
human decision, not a command.

**GitHub CLI (gh) — scoped to issue operations only** — Reading and writing GitHub
Issues for the /sync-issues workflow and session hook display. Specifically allowed:
`gh issue list`, `gh issue view`, `gh issue comment`, `gh issue close`,
`gh issue edit` (label changes only), `gh issue create`, `gh label list`,
`gh milestone list`, `gh auth status`.

Broader gh surface is explicitly denied: `gh repo`, `gh api`, `gh pr`,
`gh release`, `gh run`, `gh workflow`. This prevents Claude Code from
touching repository settings, pull requests, Actions workflows, or making
arbitrary API calls through gh.

**Standard text tools (sed, awk, tr, cut, sort, etc.)** — Config manipulation and
log parsing.

**Diagnostic tools (df, du, ps, ss)** — Read-only observation of system state.

**Registered hooks** — `.claude/settings.json` also carries a `hooks` block registering
`SessionStart` → `.claude/hooks/session-start.sh`. This is not a permission, but it lives
in the same file and is easy to lose in an edit: **Claude Code only runs hooks a settings
file registers.** There is no discovery by filename or directory, so deleting that block
does not disable a feature loudly — it makes the session hook silently never run, while
`CLAUDE.md` still tells Claude the hook reported service health. The command path is
absolute because a relative one resolves against the session's working directory.

---

## What Is Blocked and Why

**sudo / su** — No privilege escalation. Root operations belong in Dockerfiles.

**Package managers (apt, npm, pip, brew, etc.)** — Nothing installs on the host.
All dependencies go inside Docker containers.

**wget / curl -o to filesystem** — No downloading binaries to the host.

**systemctl / service** — No managing host services.

**crontab / at / nohup / screen** — No background jobs on the host.
Scheduling lives inside the stack (n8n, cron containers, etc.).

**tmux new-session** — Claude Code runs inside tmux already. No new sessions.

**kill / killall / pkill** — Use docker compose stop instead.

**Reboot / shutdown** — Shared server with other services running.

**Disk operations (mkfs, fdisk, mount, dd)** — No touching disk layout.

**scp / rsync / ssh** — Claude Code operates on this host only.

**Firewall tools** — Network rules are out of scope.

**Direct DB CLI tools** — Use docker compose exec equivalents for debugging.

**rm -rf on system paths** — Project-scoped rm is fine; system-wide is not.

**chmod 777** — Use specific permission values only.

---

## Project-Specific Additions

<!-- Add any rules specific to this project's stack or constraints -->

{{PROJECT_SPECIFIC_PERMISSION_NOTES}}
