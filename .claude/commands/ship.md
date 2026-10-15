# /ship

Promote tested dev changes to prod: merge `{{DEV_BRANCH}}` → `{{STABLE_BRANCH}}`, push to GitHub, rebuild the prod stack.

Run this only after you have tested changes at `{{DEV_URL}}` and confirmed they work.

> **Requires the two-branch promotion workflow.** If this project builds and deploys from a
> single branch, this command was not installed — see `CLAUDE.md` → Promotion workflow.

---

## Steps

### 1 — Pre-flight checks

Run these in parallel:
- `git branch --show-current` — must be on `{{DEV_BRANCH}}`
- `git status` — must be a clean working tree (nothing uncommitted)
- `git log --oneline origin/{{STABLE_BRANCH}}..{{DEV_BRANCH}}` — show what's about to be promoted

If not on `{{DEV_BRANCH}}`: stop. Tell the user to run `/dev-build` first (that skill ensures we're on the dev branch).
If there are uncommitted changes: stop. Tell the user to run `/dev-build` first to commit them.

If this project has repo preflight checks (a deploy-gate or cross-file-sync script), run them
now and **stop on failure.** Show the output and do not merge — a failing preflight means a
constraint the merge would violate. Resolve it, or have the user explicitly clear the block
first. Projects without such a script skip this.

### 2 — Confirm with user

Show the list of commits about to be merged and ask:
```
The commits above will be merged to {{STABLE_BRANCH}} and deployed to prod.
Prod will rebuild and serve at {{PROD_URL}}.

Confirm? (yes / no)
```

Stop if the user says no.

### 3 — Merge dev → stable

```bash
git checkout {{STABLE_BRANCH}}
git pull origin {{STABLE_BRANCH}}
git merge {{DEV_BRANCH}} --no-ff -m "merge: promote {{DEV_BRANCH}} to prod"
```

If merge has conflicts: stop, report the conflict files, switch back to `{{DEV_BRANCH}}`, and tell the user to resolve conflicts manually.

### 4 — Push stable

```bash
git push origin {{STABLE_BRANCH}}
```

If push is rejected: stop and report. Do not force-push `{{STABLE_BRANCH}}`.

### 5 — Rebuild prod

```bash
{{PROD_REBUILD_COMMAND}}
```

Show the output. If the rebuild fails, report the error. The code is safely on
`{{STABLE_BRANCH}}` even if the container rebuild fails.

### 6 — Return to dev

```bash
git checkout {{DEV_BRANCH}}
git merge --ff-only {{STABLE_BRANCH}}
git push origin {{DEV_BRANCH}}
```

This brings the merge commit that just landed on `{{STABLE_BRANCH}}` back onto
`{{DEV_BRANCH}}`, so the next promotion is a clean fast-forward rather than a merge of
diverged histories. `git pull origin {{DEV_BRANCH}}` does **not** do this — it fetches
`origin/{{DEV_BRANCH}}`, which never contains the stable-side merge commit.

If the fast-forward is refused, the branches have genuinely diverged: stop and report it
rather than forcing anything.

### 7 — Done — prompt to verify

Print:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SHIPPED TO PROD
  Verify at: {{PROD_URL}}

  Back on {{DEV_BRANCH}} branch — ready for the next change.
  If something went wrong → see /phase-rollback for options.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Rules

- Never skip the user confirmation in step 2.
- Never force-push `{{STABLE_BRANCH}}`.
- If in doubt about what's being promoted, run `git log --oneline origin/{{STABLE_BRANCH}}..{{DEV_BRANCH}}` and show the user before proceeding.
- Never run data migrations implicitly. If the merge includes new migrations, run them
  explicitly after step 5 and say so in the summary.
