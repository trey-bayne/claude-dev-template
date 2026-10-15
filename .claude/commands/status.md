# /status

Report the current project state in a structured summary.

## Model

**Haiku.** Delegate all steps to a Haiku sub-agent:
- Agent tool, subagent_type: general-purpose, model: haiku
- Pass the steps below as the complete prompt
- If the Agent tool call fails, execute in the current session

---

1. Read TASKS.md ## Resume Here — report current phase and next task
2. Run `docker compose ps` — report which services are healthy/unhealthy
3. Run `git status` — report uncommitted changes
4. Count completed vs total tasks across all phases in TASKS.md
5. Report any entries in ## Blockers Log

Output format:
---
Phase: [N] — [Phase Name]
Next task: [X.Y] — [task description]
Services: [N healthy / M total]
Git: [clean / N uncommitted changes]
Progress: [X of Y total tasks complete]
Blockers: [none / list]
---
