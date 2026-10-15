# /prj-drift

Report toolchain drift between this project's `.claude/commands/` and the claude_dev
template. Toolchain age is the same class of problem `/prj-manage` audits for Docker
images and dependencies — this covers the commands themselves.

## Model

**Haiku.** The work is a directory diff and a summary; no judgment calls that need a
larger model. Delegate to a Haiku sub-agent (Agent tool, subagent_type: general-purpose,
model: haiku), or run in-session if the Agent tool call fails.

---

## Steps

1. **Get the template**, in this order of preference. Whichever you use, call the result
   `TEMPLATE_DIR` for the rest of these steps:
   - `.template/` already present in this project → use it, no download needed
   - clone it somewhere disposable (needs access to the repo):
     ```bash
     git clone --depth 1 https://github.com/trey-bayne/claude-dev-template.git /tmp/claude_dev-drift
     ```
   - a local copy of the template folder → use its path directly, and skip the cleanup
     in step 5

   If you have neither repo access nor a local copy, **stop and say so.** Do not guess at
   what the template contains — a drift report built on a guess is worse than no report.

2. **Run the drift report:**
   ```bash
   TEMPLATE_DIR/scripts/check-drift.sh {{PROJECT_PATH}} TEMPLATE_DIR
   ```
   (substituting the real path). If the template copy you have predates
   `scripts/check-drift.sh`, compare the two command directories directly instead:
   ```bash
   diff -rq TEMPLATE_DIR/.claude/commands {{PROJECT_PATH}}/.claude/commands
   ```
   The script prints one row per command: `in sync`, `DIFFERS` (with +/- line counts),
   `PROJECT-ONLY`, or `MISSING`. Exit code 1 means drift was found.

3. **Interpret each row — drift runs in both directions.** This is the part a bare diff
   cannot do, so do not skip it:
   - **MISSING** — the template has a command this project doesn't. Usually worth
     installing. Check it for `{{PLACEHOLDER}}` values this project must fill first.
   - **PROJECT-ONLY** — this project invented a command. Decide which it is: genuinely
     project-specific (leave it), or generally useful and a **candidate to port upstream
     to the template** so the next project gets it for free.
   - **DIFFERS** — read the actual diff before concluding anything:
     ```bash
     diff -u TEMPLATE_DIR/.claude/commands/<file> .claude/commands/<file>
     ```
     Expected and fine: filled-in placeholders (paths, branches, URLs, rebuild commands),
     and stack-specific test or review blocks. Real drift: the project's copy is missing
     a section the template has gained, or the project's copy has improved behavior the
     template never got. Say which of the three each DIFFERS file is.

4. **Report** in this shape:
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     TOOLCHAIN DRIFT — [project] vs claude_dev
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Install from template : [commands, or none]
   Port upstream         : [project commands worth generalizing, or none]
   Behind template       : [files missing a section the template gained]
   Ahead of template     : [files with improvements the template lacks]
   Expected differences  : [N files — filled placeholders / stack-specific blocks]
   ```

5. **Clean up** the clone if you made one. Note that a project's own permission ruleset
   denies `rm -rf` against an absolute path, so this may be refused — if it is, say so and
   leave the clone in place rather than working around the rule:
   ```bash
   cd /tmp && rm -rf ./claude_dev-drift
   ```
   Never delete a local template folder you were given or a `.template/` you did not create.

6. **Offer, do not act.** If anything should change, propose it as tasks — a `Phase M`
   style block in TASKS.md, same as `/prj-manage` — and require explicit confirmation
   before writing files. Installing a template command or porting one upstream goes
   through the normal `/phase-review` → `/phase-run` → `/phase-test` cycle.

---

## Rules

- Never overwrite a project command file with the template's copy automatically. A project
  file that differs may be *ahead* of the template, and overwriting it destroys work.
- Never push to the template repo from inside a project. Porting upstream is a separate
  session in the template repo itself.
- Filled-in placeholders are not drift. Do not report them as findings.
- Report honestly when there is no drift. "No drift" is a useful answer.
