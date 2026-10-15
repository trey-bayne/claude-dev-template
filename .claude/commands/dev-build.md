# /dev-build

Commit all pending changes to the `{{DEV_BRANCH}}` branch, push to GitHub, and rebuild the dev stack so the user can test at `{{DEV_URL}}`.

> **Requires the two-branch promotion workflow.** If this project builds and deploys from a
> single branch, this command was not installed — see `CLAUDE.md` → Promotion workflow.

## Arguments

Optional: a commit message passed directly after `/dev-build`. If omitted, derive one from the staged changes.

---

## Steps

### 1 — Branch check

Run `git branch --show-current`.

- If on `{{DEV_BRANCH}}`: proceed.
- If on `{{STABLE_BRANCH}}` with **no** uncommitted changes: run `git checkout {{DEV_BRANCH}}` and proceed.
- If on `{{STABLE_BRANCH}}` with **uncommitted changes**: stop. Tell the user:
  ```
  ⚠️  You have uncommitted changes on {{STABLE_BRANCH}} — new work should go on {{DEV_BRANCH}} first.
  Run: git checkout {{DEV_BRANCH}}
  Then re-run /dev-build.
  ```
- If on any other branch: stop and report which branch we're on. Ask the user how to proceed.

### 2 — Show pending changes

Run `git status` and `git diff --stat HEAD`. Show the output so the user can see what's being committed.

If there are **no changes at all** (clean tree), skip steps 3–4 and jump directly to step 5 (rebuild only). Tell the user: "Nothing to commit — rebuilding dev stack with current code."

### 3 — Commit message

If the user passed a message as an argument, use it.
If not, write a concise one-line commit message that describes the changes (same standards as always — focus on the why, not the what). Show it to the user before committing.

### 4 — Commit and push

```bash
git add -A
git commit -m "<message>"
git push origin {{DEV_BRANCH}}
```

If push is rejected (non-fast-forward), stop and report. Do not force-push.

### 5 — Rebuild dev stack

```bash
{{DEV_REBUILD_COMMAND}}
```

Show the output. If the rebuild fails, stop and report the error.

If the dev stack does not exist yet (the command or compose file is missing because the phase
that builds it has not run), stop here and report: "Code is committed and pushed to
{{DEV_BRANCH}}. The dev stack does not exist yet." Do not improvise a deployment.

### 6 — Done — prompt to test

Print:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DEV BUILD COMPLETE
  Test your changes at: {{DEV_URL}}
  Prod is untouched.

  When it looks good → run {{PROMOTION_COMMAND}} to promote to prod.
  If something's broken → fix it and run /dev-build again.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Rules

- Never push to `{{STABLE_BRANCH}}` or rebuild the prod stack from this skill.
- Never force-push to `{{DEV_BRANCH}}`.
- If the rebuild fails, leave the commit in place — the code is safe, only the container rebuild failed.
