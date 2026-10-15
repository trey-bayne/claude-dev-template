# /phase-rollback

Roll back the stable branch to the previous release tag and redeploy. Use this when a release is broken and you need to restore the last known-good state.

> **Requires the two-branch promotion workflow.** If this project builds and deploys from a
> single branch, this command was not installed — see `CLAUDE.md` → Promotion workflow.

## Model

**Haiku.** Delegate all steps to a Haiku sub-agent:
- Agent tool, subagent_type: general-purpose, model: haiku
- Pass the steps below as the complete prompt
- If the Agent tool call fails, execute in the current session

---

## Context

- Working directory: `{{PROJECT_PATH}}`
- Dev branch: `{{DEV_BRANCH}}` — never touched by this command. Dev retains all your work.
- Stable branch: `{{STABLE_BRANCH}}` — this is what gets rolled back
- Tags follow the format `v{version}` (e.g. `v1.0`, `v2.0`) — only consider tags matching `v[0-9]`
- Include `{{COMPOSE_PROFILE_ARGS}}` in every docker compose command (empty for most projects)
- Running this command IS the user's confirmation — do not ask for additional confirmation
- ⚠️ **Rolling back code does NOT roll back the database.** If this project uses schema
  migrations and the broken release included one, the schema stays migrated while the code
  reverts. Check that before rolling back. If the release added a migration, stop and report
  that a schema rollback decision is required — a forward-fix is usually safer than a
  down-migration. Projects with no migrations can ignore this.

---

## Steps

1. **List available release tags**
   - Run `git -C {{PROJECT_PATH}} tag --sort=-version:refname | grep -E '^v[0-9]'`
   - This gives release tags only, sorted newest first (e.g. `v2.0`, `v1.0`)
   - If zero tags found: stop and report "No release tags found — nothing to roll back to."
   - If only one tag found: stop and report "Only one release exists (v{tag}) — nothing to roll back to."

2. **Identify current and target release**
   - Current release = first tag in the sorted list
   - Target (rollback) release = second tag in the sorted list
   - Report: "Rolling back from v{current} → v{target}. The {{DEV_BRANCH}} branch is untouched."

3. **Bring services down**
   - `cd {{PROJECT_PATH}} && docker compose {{COMPOSE_PROFILE_ARGS}} down`
   - Ensures no file locks or stale containers during the reset

4. **Reset stable to target tag**
   - `git -C {{PROJECT_PATH}} checkout -f {{STABLE_BRANCH}}`
   - (`-f` handles any dirty working tree — safe since we're doing emergency recovery)
   - `git -C {{PROJECT_PATH}} reset --hard v{target}`

5. **Delete the broken release tag**
   - `git -C {{PROJECT_PATH}} tag -d v{current}`
   - `git -C {{PROJECT_PATH}} push origin :refs/tags/v{current}`
   - This removes the broken tag so future `/phase-release` and `/phase-rollback` runs won't see it as a valid release
   - If the remote tag push fails, warn but continue — the local tag deletion is what matters for command logic

6. **Force-push stable to origin**
   - `git -C {{PROJECT_PATH}} push --force-with-lease origin {{STABLE_BRANCH}}`
   - `--force-with-lease` (never a bare `--force`) so the push aborts if someone else moved the branch
   - If push fails, warn the user but continue — local reset is valid and services will run from the correct code

7. **Redeploy**
   - `cd {{PROJECT_PATH}} && docker compose {{COMPOSE_PROFILE_ARGS}} up -d --build --wait --wait-timeout 180 --remove-orphans`
   - `--remove-orphans` cleans up any containers from the broken release that no longer exist in the rolled-back compose file
   - `--wait` blocks until all healthchecks pass (up to 3 minutes)
   - Note: `--build` rebuilds from the rolled-back source — expected to take a few minutes

8. **Switch back to dev**
   - `git -C {{PROJECT_PATH}} checkout {{DEV_BRANCH}}`
   - Dev is unchanged — all phase work is still here
   - Warning: do not run `docker compose up` from `{{DEV_BRANCH}}` without `--build` from `{{STABLE_BRANCH}}` — it would deploy dev code over the rolled-back release

9. **Verify health**
   - `cd {{PROJECT_PATH}} && docker compose {{COMPOSE_PROFILE_ARGS}} ps`
   - Check that all expected services show as `running` or `healthy`
   - If any service is still not healthy, report which ones failed and show their last 20 log lines: `cd {{PROJECT_PATH}} && docker compose logs --tail=20 {service}`

10. **Report**
    - Success: "Rolled back to v{target}. All services healthy. The {{DEV_BRANCH}} branch is untouched — diagnose the issue and run /phase-release when ready to try again."
    - Partial failure: "Rolled back to v{target} but some services need attention: {list}. Check logs above."
