# /phase-complete

Mark the current phase done and set up the next phase.

## Model

**Haiku.** Delegate all steps to a Haiku sub-agent:
- Agent tool, subagent_type: general-purpose, model: haiku
- Pass the steps below as the complete prompt
- If the Agent tool call fails, execute in the current session

---

1. Read TASKS.md and identify the current phase number (N) from ## Resume Here
2. Verify all tasks in Phase N are marked [x] — if any are unchecked, list them and stop
3. Confirm services are healthy: `docker compose ps`
4. Commit with message: "phase N complete — [phase name]"
5. Update TASKS.md ## Resume Here to point at Phase N+1, first task
6. Commit TASKS.md with message: "update TASKS.md — phase N complete, ready for phase N+1"
7. Push to origin: `git -C {{PROJECT_PATH}} push origin {{DEV_BRANCH}}`
   - If push is rejected (non-fast-forward), report: "Push rejected — remote has diverged. Check origin/{{DEV_BRANCH}} before continuing."
   - If push fails due to network timeout, warn but continue — local commits are safe.
8. Report: "Phase N complete. {{DEV_BRANCH}} pushed to origin. Resuming at Phase N+1 task [X.1]."
