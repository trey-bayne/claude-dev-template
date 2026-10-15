# /phase-release

Merge dev into stable, tag the release, deploy, and verify everything is running.

> **Requires the two-branch promotion workflow** and the **Phase Index table** in `TASKS.md`
> (the `Release` column is this command's input). If either is missing, this command was not
> installed — see `CLAUDE.md` → Promotion workflow.

## Model

**Haiku.** Delegate all steps to a Haiku sub-agent:
- Agent tool, subagent_type: general-purpose, model: haiku
- Pass the steps below as the complete prompt
- If the Agent tool call fails, execute in the current session

---

## Context

- Working directory: `{{PROJECT_PATH}}`
- Dev branch: `{{DEV_BRANCH}}`
- Stable branch: `{{STABLE_BRANCH}}`
- Release versions and taglines are in the Phase Index table in `TASKS.md` (Release column)
- Include `{{COMPOSE_PROFILE_ARGS}}` in every docker compose command (empty for most projects)
- Running this command IS the user's confirmation — do not ask for additional confirmation

---

## Steps

1. **Verify clean state**
   - Run `git -C {{PROJECT_PATH}} status --porcelain`
   - If there are uncommitted changes, list them and stop. Tell the user to commit or stash before releasing.

2. **Determine release version**
   - Read `{{PROJECT_PATH}}/TASKS.md`
   - Find all phases marked `Complete` in the Phase Index table
   - Extract their Release column values — skip any row where Release is `—` (a dash)
   - Valid release values look like `1.0`, `2.0`, `2.5` — ignore anything else
   - Run `git -C {{PROJECT_PATH}} tag | grep -E '^v[0-9]'` to list existing release tags
   - The new release version is the highest valid release value among completed phases that does NOT already have a corresponding git tag (e.g. `v1.0`)
   - If no completed phases have a valid version number, or all are already tagged, stop and tell the user: "Nothing to release — all completed phases are already tagged."

3. **Extract the release tagline**
   - From the TASKS.md Phase Index, find the row whose Release column matches the new version
   - Extract the tagline text (everything after the bold version number)
   - This will be used in the git tag annotation

4. **Merge dev into stable**
   - `git -C {{PROJECT_PATH}} checkout {{STABLE_BRANCH}}`
   - `git -C {{PROJECT_PATH}} merge --no-ff {{DEV_BRANCH}} -m "release v{version} — {tagline}"`
   - If merge conflicts occur: run `git -C {{PROJECT_PATH}} merge --abort`, then `git -C {{PROJECT_PATH}} checkout {{DEV_BRANCH}}`, then stop and report the conflict details to the user

5. **Tag the release**
   - `git -C {{PROJECT_PATH}} tag -a v{version} -m "v{version} — {tagline}"`

6. **Push stable and tag to origin**
   - `git -C {{PROJECT_PATH}} push origin {{STABLE_BRANCH}}`
   - `git -C {{PROJECT_PATH}} push origin v{version}`
   - If push is rejected (non-fast-forward), stop and report: "Push rejected — remote has diverged. Resolve before deploying."
   - If push fails due to network timeout, warn but continue — the local merge and tag are still valid

7. **Deploy from stable**
   - Still on `{{STABLE_BRANCH}}` at this point — deploy from here
   - `cd {{PROJECT_PATH}} && docker compose {{COMPOSE_PROFILE_ARGS}} up -d --build --wait --wait-timeout 180`
   - This rebuilds only changed images, starts all services, and waits until healthchecks pass (up to 3 minutes)
   - If the release includes a data migration, run it explicitly here, before verifying health

8. **Switch back to dev**
   - `git -C {{PROJECT_PATH}} checkout {{DEV_BRANCH}}`
   - Note: running containers were built from `{{STABLE_BRANCH}}` (the release). Running `docker compose up` again from `{{DEV_BRANCH}}` would rebuild from dev code — don't do that unless intentional.

9. **Verify health**
   - `cd {{PROJECT_PATH}} && docker compose {{COMPOSE_PROFILE_ARGS}} ps`
   - Check that all expected services show as `running` or `healthy`
   - If any service is not healthy, report which ones failed and show their last 20 log lines: `cd {{PROJECT_PATH}} && docker compose logs --tail=20 {service}`

10. **Report**
    - Success: "Released v{version}. All services healthy. {tagline}"
    - Partial failure: "Released v{version} but the following services need attention: {list}. The git tag and merge are committed. Run /phase-rollback to revert to the previous release, or investigate the logs above."
