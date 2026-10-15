# /phase-run

Execute the next phase autonomously. Stops cleanly at phase end — does not
chain into the next phase, does not run /phase-test automatically.
You review the output, then invoke /phase-test yourself.

Hard-blocked if /phase-review has not been run for this phase or scored below 7.0.

## Model

**Manual mode: Sonnet. Runs in the current session. Do not delegate to a sub-agent.**
Task execution requires judgment on error output, failure recovery, and sequential
decision-making. A sub-agent mistake here could leave TASKS.md in an inconsistent
state that is confusing to untangle, even with the checkpoint safety net.

**Auto mode: runs as a Sonnet sub-agent spawned by `/phase-auto`.**
When invoked via `/phase-run auto`, this skill is called inside a sub-agent that
`/phase-auto` spawned with `model: sonnet`. All behavior below is unchanged — from
the sub-agent's perspective it is the in-session model.

---

## The intended workflow

```
/phase-review        → must score ≥ 7.0 before this command will execute
/phase-run           → executes this phase only, then stops
                     → review output
/phase-test          → you invoke manually
                     → fix any failures
/phase-review        → start the cycle for the next phase
```

---

## Auto mode (invoked as `/phase-run auto`)

When the argument `auto` is present, this command is being driven by `/phase-auto`.
When invoked WITHOUT `auto`, ignore this entire section and behave exactly as
documented below.

In auto mode:

- **Step 2 gate still applies.** A phase-review score must exist. The orchestrator
  guarantees it ran first, but do not skip the hard block — if no PROCEED score is
  found, stop and report. (The orchestrator only proceeds past review at ≥ 8.0, so
  the ≥ 7.0 block here will already be satisfied.)
- **Step 3 checkpoint still runs.** Never skip it — it is the rollback point.
- **Step 4 GO prompt is skipped.** Do not print the task list and wait. Print the
  same header for the record, then proceed directly to Step 5. There is no `GO`.
- **Step 5 task failure becomes retry-with-escalation instead of hard-stop:**
  - Maintain a per-task try counter, reset to 0 when a task succeeds.
  - **Try 1:** execute the task in-session (Sonnet) as normal.
  - **Tries 2–3:** on failure, delegate the fix to a fresh **Opus** sub-agent
    (Agent tool, subagent_type: general-purpose, model: opus). Give it the task
    text, the full error output, and the scope rule (PROJECT_ROOT only). Then
    verify the task succeeded.
  - Do NOT invent creative workarounds, disable checks, or skip the task to make
    an error disappear. Fix the root cause or escalate.
  - **After 3 failed tries** on the same task: stop the phase. Log to TASKS.md
    Blockers Log as today. Return the marker `TASK_FAILED` with the task ID, the
    try count, and the final error. The orchestrator escalates to the user.
- **Step 6 stays the same** — commit the phase-complete commit, print the summary,
  do NOT advance `## Resume Here`, do NOT invoke `/phase-test`. Return control to
  the orchestrator.

The PROJECT_ROOT scope rule and the commit cadence are unchanged in auto mode.

---

## Step 1 — Establish scope

Read:
- `TASKS.md` → identify NEXT_PHASE number and name from ## Resume Here
- `TASKS.md` → read the full NEXT_PHASE task list
- `docs/PHASE_NOTES.md` → read NEXT_PHASE section

Establish PROJECT_ROOT:
```bash
pwd
```

Every file operation in this session must stay within PROJECT_ROOT.
If any task would require writing outside PROJECT_ROOT, stop on that task and report
it rather than executing.

---

## Step 2 — Phase-review gate (hard block)

Search TASKS.md NEXT_PHASE section for:
```
<!-- phase-review: score=X.X timestamp=... status=... -->
```

**If not found:**
```
🛑 /phase-run blocked.

   /phase-review has not been run for Phase [N].
   Run /phase-review first. /phase-run requires a score ≥ 7.0 to proceed.
```
Stop. Do not proceed.

**If found with status=BLOCKED (score < 7.0):**
```
🛑 /phase-run blocked.

   Phase [N] review score: [X.X/10] — below the 7.0 threshold.
   Last reviewed: [timestamp]

   To unblock:
   1. Run /phase-review
   2. Address the risks identified
   3. Re-run /phase-review until score ≥ 7.0
```
Stop. Do not proceed.

**If found with status=PROCEED (score ≥ 7.0):**
Continue to Step 3. Print:
```
✅ Phase review score: [X.X/10] — cleared to proceed.
```

---

## Step 3 — Checkpoint

```bash
git add -A
git commit -m "checkpoint: pre-phase [N] run — $(date +%Y-%m-%d_%H:%M)"
```

If nothing to commit, print the status and continue.

Print:
```
✅ Checkpoint: [git hash]
   Recovery:   git reset --hard [git hash]
```

Hold this hash. Print it again if the phase fails.

---

## Step 4 — Show task list and wait for GO

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  /phase-run — Phase [N]: [Name]
  Review score: [X.X/10]
  Checkpoint:   [git hash]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tasks:
[N.1]  [full task text]
[N.2]  [full task text]
...
[N.N]  [full task text]

Total: [N] tasks
Scope: [PROJECT_ROOT] only
Mode:  autonomous after GO — no further prompts until phase complete or failure

Type GO to begin, or anything else to cancel.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Wait. Only proceed on exact input `GO`.
On anything else:
```
Cancelled. Checkpoint commit remains at [hash]. No changes made.
```

---

## Step 5 — Execute the phase

Work through every task in order. For each task:

1. Print: `▶ [N.X] — [task description]`
2. Execute
3. Verify success before moving on
4. Update TASKS.md immediately: change `[ ]` to `[x] YYYY-MM-DD`
5. Print: `✅ [N.X] done`

**Scope rule:** all file reads and writes within PROJECT_ROOT only.
If a task implies reaching outside PROJECT_ROOT, stop, print the concern, and wait
for explicit confirmation before proceeding.

**Commit cadence:**
- After each service brought up and verified healthy
- After each logical group of related file changes
- Never more than 5 tasks without a commit
- Message format: `phase [N]: [brief description of what was just completed]`

**On task failure:**
```
❌ [N.X] FAILED
[full error output]

Recovery: git reset --hard [checkpoint hash]
```

Log to TASKS.md Blockers Log:
```
[date] task [N.X] — [error summary] — checkpoint: [hash]
```

Stop. Do not execute remaining tasks. Do not attempt to continue past a failure.

---

## Step 6 — Phase complete, then stop

When all tasks are marked done:

```bash
git add -A
git commit -m "phase [N] complete — [phase name]"
```

Print:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Phase [N] complete — [phase name]

  All [N] tasks executed and marked done in TASKS.md.
  Final commit: [hash]

  Next steps (your call):
    1. Run /phase-test to verify everything works as expected
    2. Fix any failures /phase-test surfaces
    3. Run /phase-review to assess Phase [N+1]

  ## Resume Here has NOT been advanced.
  It will be advanced by /phase-test on a clean pass.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Stop. Do not invoke /phase-test. Do not advance ## Resume Here.
You decide what happens next.

---

## Rules

- Hard-block if no phase-review score ≥ 7.0 exists in TASKS.md. No exceptions.
- Never operate outside PROJECT_ROOT.
- Never skip the checkpoint in Step 3.
- Never skip the GO confirmation in Step 4.
- Stop completely on any task failure. Never skip ahead.
- Update TASKS.md task status in real time, not at the end.
- Do not invoke /phase-test automatically.
- Do not advance ## Resume Here. That is /phase-test's job on a clean pass.
- The checkpoint hash is the safety net. Print it prominently. Print it again on failure.
