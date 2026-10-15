# /checkpoint

Snapshot the current state of the session before making significant changes.

## Model

**Haiku.** Delegate all steps to a Haiku sub-agent:
- Agent tool, subagent_type: general-purpose, model: haiku
- Pass the steps below as the complete prompt
- If the Agent tool call fails, execute in the current session

---

1. Run `git status` and show the output
2. Run `git diff --stat` to show what's changed
3. Commit all current changes with message: "checkpoint: [brief description of current state]"
4. Confirm commit succeeded
5. Report: "Checkpoint saved. Safe to proceed."

Use this before any operation that touches multiple files, restructures the project,
or makes changes that would be difficult to reverse.
