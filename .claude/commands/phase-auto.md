# /phase-auto

Run a full phase end-to-end with no approval prompts: review until confident,
build, then test-and-fix until green. Stops only at the safety hatches below.

This is the autonomous replacement for running `/phase-review` → `/phase-run` →
`/phase-test` by hand. It chains all three, removes their human gates, and adds
retry loops with model escalation.

## Model

All three stages are delegated to sub-agents with fixed models. The session model
does not matter — `/phase-auto` is the pure orchestrator and does no build work itself.

| Role | Model | How |
|---|---|---|
| Reviewer | Opus | Agent tool (model: opus) invokes `/phase-review auto` |
| Builder | Sonnet | Agent tool (model: sonnet) invokes `/phase-run auto` |
| Tester | Haiku | Agent tool (model: haiku) invokes `/phase-test auto` |
| Fixer | Opus | Agent tool (model: opus), spawned on test failure |

---

## Design rules (read before running)

- **The orchestrator owns every loop and every stop-and-ask.** Sub-agents cannot
  prompt the user, so all escalation lives in this session.
- **Every stage boundary is crash-safe.** Each stage commits and writes its place
  to TASKS.md (the score comment, task checkboxes, `## Resume Here`). If the
  context is compacted mid-run, re-read position from TASKS.md — never from memory.
  There is no context-percentage gate; the harness compacts automatically and the
  on-disk state is the source of truth.
- **The task list is not frozen in auto mode.** The reviewer's task-list changes are
  auto-applied and committed so the run can continue unattended — that is the whole point
  of auto mode. Only a change that would delete the phase Goal or the entire Definition of
  Done stops and asks you (Hatch A). If you want a phase's task list held exactly as
  written, run `/phase-review` and `/phase-run` by hand instead.
- **No creative workarounds.** A stuck task escalates to Opus, then to you. It does
  not get "solved" by disabling a check or skipping the work.
- **Never ship.** This command stays on `{{DEV_BRANCH}}` and never runs
  `{{PROMOTION_COMMAND}}`, never rebuilds prod, never pushes. Promotion to prod is always a
  human decision.

---

## Stage 0 — Preflight (stop if any check fails)

1. Confirm git state:
   ```bash
   git branch --show-current
   git status --porcelain
   ```
   - Must be on `{{DEV_BRANCH}}`. If not, stop and ask.
   - Working tree should be clean. If dirty, show `git status` and ask whether to
     commit it into the pre-phase checkpoint or stop. Do not silently sweep
     unrelated changes into a checkpoint.
2. Read `TASKS.md` → `## Resume Here` → identify NEXT_PHASE number and name.
3. Print the run header:
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     /phase-auto — Phase [N]: [Name]
     Confidence target: 8.0   Branch: {{DEV_BRANCH}}
     Hatches: review×4 · build×3 · test-fix×3 · task-list-freeze
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

---

## Stage 1 — Review loop (target 8.0, cap 4)

**CRITICAL — use the Agent tool, NOT the Skill tool.** Invoking `/phase-review auto`
directly as a Skill takes over the conversation turn and the orchestrator never resumes.
Always spawn a sub-agent that runs the skill and returns the result.

Initialize `review_attempts = 0`.

Loop:

1. Spawn an **Opus** sub-agent (Agent tool, subagent_type: general-purpose, model: opus)
   with a prompt that instructs it to: run the `/phase-review auto` skill in
   `{{PROJECT_PATH}}`, execute it to completion, and return the full `PHASE_REVIEW_RESULT`
   block verbatim as its response (score, applied_edits, task_list_change_requested).
   Parse the block from the sub-agent's returned text.
2. `review_attempts += 1`.
3. **If `task_list_change_requested: yes`** → auto-apply the changes. Read what the
   reviewer wanted to change, apply them directly to the task file, commit:
   `phase-auto: review-loop task-list update — attempt [review_attempts]`, then
   **loop again** (do not stop and ask). Only escalate to the user (Hatch A) if the
   suggested change would delete the phase Goal or entire Definition of Done.
4. **If `score ≥ 8.0`** → review passed. Commit the stage boundary if anything is
   uncommitted (`phase-auto: review stage — Phase [N] @ [X.X]`) and go to Stage 2.
5. **If `score < 8.0` and `applied_edits: none`** → re-running will produce the same
   score (nothing changed). **STOP — Hatch B**: report the score and the
   unaddressed risks and ask the user how to proceed. Do not burn more passes.
6. **If `score < 8.0` and edits were applied** → something changed; loop again.
7. **If `review_attempts ≥ 4`** → **STOP — Hatch C**: report the score history and
   ask the user how to proceed.

---

## Stage 2 — Build

Spawn a **Sonnet** sub-agent (Agent tool, subagent_type: general-purpose, model: sonnet).
Give it: the phase number and name, the instruction to invoke `/phase-run auto`, and
the PROJECT_ROOT path. The sub-agent runs `/phase-run auto` as a skill in its own
session. It checkpoints, skips GO, and executes every task with per-task retry
(Sonnet → Opus on tries 2–3, 3-try cap).

If the Agent tool call fails before the sub-agent returns a result, report the error
and stop — do not continue to Stage 3.

- **If the sub-agent returns `TASK_FAILED`** → **STOP — Hatch D**: a task failed 3
  times. Print the task ID, try count, and final error, plus the checkpoint hash for
  rollback. Ask the user how to proceed. Do not continue to Stage 3.
- **If the sub-agent completes** → all tasks marked done and committed. Continue to
  Stage 3.

---

## Stage 3 — Test + fix loop (cap 3)

**CRITICAL — use the Agent tool, NOT the Skill tool.** Same reason as Stage 1.

Initialize `fix_attempts = 0`.

1. Spawn a **Haiku** sub-agent (Agent tool, subagent_type: general-purpose, model: haiku)
   instructed to: run the `/phase-test auto` skill in `{{PROJECT_PATH}}`, execute it to
   completion, and return the full test results (passed/failed/manual items) verbatim.
2. **If PASSED** → `/phase-test` advances `## Resume Here` and commits. Go to the
   Final Summary.
3. **If FAILED:**
   - Checkpoint before fixing: `git commit -am "phase-auto: pre-fix checkpoint — Phase [N] attempt [fix_attempts+1]"` (record the hash).
   - Spawn an **Opus** fixer sub-agent (Agent tool, general-purpose, model: opus).
     Give it: the failed test IDs and full error output, the phase Definition of
     Done, and the PROJECT_ROOT scope rule. It fixes the root cause — no disabling
     tests, no workarounds.
   - `fix_attempts += 1`.
   - Re-run **the full** `/phase-test auto` (not just the previously failed tests —
     a fix can regress a test that was passing).
   - If PASSED → done (step 2).
   - If `fix_attempts ≥ 3` → **STOP — Hatch E**: report remaining failures, the fix
     attempts made, and the checkpoint hashes. Ask the user how to proceed.
   - Otherwise loop.

---

## Final Summary (on success only)

Print:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Phase [N] — [Name] complete via /phase-auto
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What was done:
  [one line per task completed]

What worked:
  Review: [X.X/10] after [review_attempts] pass(es)
  Tests : [P] passed / [F] failed-then-fixed / [M] manual

What didn't (and how it was handled):
  [build task retries that needed Opus escalation, with task IDs]
  [test failures fixed, with test IDs and what the fix was]
  [if none: "Clean run — no retries needed."]

Manual verification you should do yourself:
  [each ⚠️ MANUAL item from /phase-test, with its steps]

State:
  Resume Here → Phase [N+1]: [name]
  Key commits: [stage hashes]
```

Do NOT run `{{PROMOTION_COMMAND}}`, rebuild prod, or push. Stop here.

---

## The stop-and-ask hatches (summary)

| Hatch | Trigger | Stage |
|---|---|---|
| A | Reviewer wants to delete the phase Goal or entire DoD (auto-apply all other task-list changes) | 1 |
| B | Review < 8.0 with nothing left to auto-apply | 1 |
| C | Review hits 4 passes without reaching 8.0 | 1 |
| D | A build task fails 3 times (after Opus escalation) | 2 |
| E | Test fixes fail 3 times | 3 |

Plus the Stage 0 preflight checks (wrong branch, dirty tree).

---

## Rules

- Session model does not matter — all stages run in fixed-model sub-agents.
- Stay on `{{DEV_BRANCH}}`. Never run `{{PROMOTION_COMMAND}}`, never rebuild prod, never push.
- Own every loop and every escalation in this session — sub-agents cannot ask the user.
- Confidence target is 8.0. The reviewer's own 7.0 block is a floor, not the target.
- Task-list changes are auto-applied and committed; only deleting the Goal or the whole Definition of Done escalates (Hatch A).
- No creative workarounds on stuck tasks. Escalate to Opus, then to the user.
- Re-run the FULL test suite after every fix, never just the failed tests.
- Treat TASKS.md on-disk state as the source of truth across any compaction.
