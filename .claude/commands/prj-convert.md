# /prj-convert

Convert an existing project (started before claude_dev) into the claude_dev format.
Analyzes what exists, creates the full file structure, and prepares the project for
/phase-review so the normal phase cycle can begin.

## Model

**Sonnet. Runs in the current session. Do not delegate to a sub-agent.**
Requires synthesizing an entire codebase, making architectural judgment calls, merging
existing content, and multiple interactive confirmation points. Too much judgment for Haiku.

---

To use this command in a project that doesn't have a .claude/ directory yet,
install it globally:

```bash
cp /path/to/claude_dev/.claude/commands/prj-convert.md ~/.claude/commands/
```

Then run `/prj-convert` from inside the target project directory.

---

## When to use

- Existing project with no CLAUDE.md, TASKS.md, or .claude/ directory
- Project started before claude_dev was set up
- You want to bring it into the phase/review/test workflow

---

## Step 1 — Read everything

Run: `pwd` — establish PROJECT_ROOT.

Find all readable files:

```bash
find . -maxdepth 3 \
  \( -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" \
     -o -name "*.txt" -o -name "*.toml" -o -name "Dockerfile" \
     -o -name ".env.example" \) \
  -not -path "./.git/*" \
  -not -path "./node_modules/*" \
  -not -path "./.venv/*" \
  | sort
```

Read every file found. Do not skip any.

Check for partial claude_dev structure:

```bash
ls -la .claude/ 2>/dev/null || echo "No .claude/ directory"
cat CLAUDE.md 2>/dev/null || echo "No CLAUDE.md"
cat TASKS.md 2>/dev/null || echo "No TASKS.md"
```

Check git history:

```bash
git log --oneline -20 2>/dev/null || echo "No git history"
git status 2>/dev/null || echo "Not a git repo"
```

---

## Step 2 — Extract understanding

From everything read in Step 1, extract:

**Project identity**
- Name (from README, package.json name field, docker-compose project name, or directory name)
- Purpose (from README intro or inferred from codebase structure)
- Current development state (what is already built and running?)

**Tech stack**
- Is it Docker-based? What services are defined?
- Language/runtime (Python, Node, Go, etc.)
- Databases, caches, queues
- Frameworks in use (FastAPI, Express, Django, etc.)

**What's already built**
- Completed work inferred from git log and source files
- What currently runs vs. what is planned

**Existing docs**
- What do existing .md files contain? Are they design docs, READMEs, or task lists?
- Is there an existing TASKS.md or CLAUDE.md? What does it say?

**Gaps vs. claude_dev template**

Build this table:

```
| File                              | Present? | Has real content? |
|-----------------------------------|----------|-------------------|
| CLAUDE.md                         |          |                   |
| TASKS.md                          |          |                   |
| docs/ARCHITECTURE.md              |          |                   |
| docs/PHASE_NOTES.md               |          |                   |
| docs/DECISIONS.md                 |          |                   |
| docs/ENV_VARS.md                  |          |                   |
| docs/INDEX.md                     |          |                   |
| docs/QUICK_REF.md                 |          |                   |
| docs/SYSTEM_STATE.md              |          |                   |
| .claude/settings.json             |          |                   |
| .claude/hooks/session-start.sh    |          |                   |
| .claude/commands/checkpoint.md    |          |                   |
| .claude/commands/phase-review.md  |          |                   |
| .claude/commands/phase-run.md     |          |                   |
| .claude/commands/phase-test.md    |          |                   |
| .claude/commands/phase-complete.md|          |                   |
| .claude/commands/status.md        |          |                   |
| .claude/commands/sync-issues.md   |          |                   |
| .claude/commands/prj-manage.md    |          |                   |
| .claude/commands/prj-convert.md   |          |                   |
```

**Architectural improvements**

From reading the codebase, identify things that should be addressed:
- Inconsistent patterns (e.g. some services have health checks, others don't)
- Hardcoded values that should be in environment variables
- Missing .env.example, missing .gitignore, etc.
- Anything the architecture would benefit from improving

These become tasks in TASKS.md — in the first incomplete phase, or a new Phase 1.

---

## Step 3 — Present findings and wait for confirmation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  /prj-convert — Project Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Project  : [name]
Purpose  : [one paragraph]
Stack    : [summary]

What's already built:
  [list from git history and source files]

claude_dev gaps:
  [gap table from Step 2]

Files that will be CREATED (missing entirely):
  [list]

Files that will be POPULATED (exist as template placeholders):
  [list]

Files with existing content — will prompt before touching:
  [list]

Architectural improvements to add as tasks:
  1. [improvement description]
  2. [improvement description]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Please confirm this analysis before I create any files.
Correct anything wrong. Add any constraints I should know.
What phase number should this project start at?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Wait for explicit confirmation. Do not create or modify any files until confirmed.**

Acknowledge every correction. Ask about any remaining genuine gaps (don't ask what
is already clear from the code).

---

## Step 4 — Get current template files

Clone the template repo to a temporary folder:

```bash
git clone [TEMPLATE_REPO_URL] .claude_dev_template
```

If you have no access to that repo but you do have the template as a local folder, copy
it instead:

```bash
cp -r /path/to/claude_dev .claude_dev_template
```

TEMPLATE_REPO_URL is documented in this project's BOOTSTRAP.md or README.md.

If neither works: stop and report it. Do not proceed without real template files.
Do not substitute command text from memory — the real template files are the source of truth
for settings.json, session-start.sh, and all command files.

---

## Step 5 — Create directory structure

Create any missing directories. Never remove existing ones.

```bash
mkdir -p docs
mkdir -p .claude/commands
mkdir -p .claude/hooks
```

---

## Step 6 — Process each file

### Rule for files with existing real content

Show the file's current content (first 30 lines if long) and the proposed replacement.
Ask: `Overwrite, merge, or skip? [overwrite / merge / skip]`

- **overwrite** → replace entirely
- **merge** → show both, construct a merged version, confirm before writing
- **skip** → leave untouched, note it in the final report

### Rule for missing files or empty/placeholder-only files

Create or populate without prompting.

### Processing order

1. `.claude/settings.json` — copy from template
2. `.claude/hooks/session-start.sh` — copy from template; fill in PROJECT_NAME and
   PROJECT_DIR from the project identity identified in Step 2; detect services and
   ports from docker-compose.yml to populate the check_service() calls.
   After writing: `chmod +x .claude/hooks/session-start.sh`
3. `.claude/commands/` — copy all 9 command files from template
   (checkpoint, phase-complete, phase-review, phase-run, phase-test,
    status, sync-issues, prj-manage, prj-convert)
4. `CLAUDE.md` — populate from template using extracted project info.
   Must stay under 200 lines. Phase detail, env vars, and architecture diagrams
   belong in docs/, not here.
5. `TASKS.md` — see special handling below
6. `docs/ARCHITECTURE.md` — populate from existing architecture docs and README
7. `docs/PHASE_NOTES.md` — populate from any existing phase notes; add Phase 1 section
8. `docs/DECISIONS.md` — populate from any existing decision records
9. `docs/ENV_VARS.md` — populate from .env.example and docker-compose.yml env sections
10. `docs/INDEX.md` — copy from template, adapt navigation entries to this project
11. `docs/QUICK_REF.md` — populate from template with this project's actual stack commands
12. `docs/SYSTEM_STATE.md` — populate with what is currently running and built
13. `PROJECT_BRIEF.md` — populate from README and any other design or planning docs
14. `PERMISSIONS.md` — copy from template; note any project-specific additions

### TASKS.md special handling

TASKS.md is the most critical file. Handle it carefully:

a. If TASKS.md has existing content: read every task.
b. From git log: identify which phases/tasks are clearly complete → mark `[x] YYYY-MM-DD`
   using the date from the relevant commit.
c. For the in-progress phase: preserve existing task states.
d. Insert architectural improvement tasks (from Step 2) into the appropriate phase.
e. Ensure `## Resume Here` points to the current phase and the correct next task.
f. Add `## Decisions Log` and `## Blockers Log` sections if not present.
g. **Always show the full proposed TASKS.md before writing it.**
   Get explicit confirmation before writing.

---

## Step 7 — Validate

1. **CLAUDE.md line count**: if over 200 lines, identify what overflows and move it to docs/
2. **Unfilled placeholders**:
   ```bash
   grep -r "{{" . \
     --include="*.md" --include="*.sh" --include="*.json" \
     --exclude-dir=".git" --exclude-dir=".claude_dev_template" \
     --exclude-dir="node_modules" --exclude-dir=".venv"
   ```
   List any found. Fill them or flag them explicitly.
3. **settings.json validity**:
   ```bash
   python3 -c "import json; json.load(open('.claude/settings.json')); print('valid')"
   ```
4. **session-start.sh is executable**:
   ```bash
   ls -la .claude/hooks/session-start.sh
   ```
5. **Command count**:
   ```bash
   ls .claude/commands/ | wc -l
   ```
   Should show 9.

---

## Step 8 — Commit and cleanup

If the project is not yet a git repo:

```bash
git init
```

Then:

```bash
git add -A
git commit -m "prj-convert: initialize claude_dev structure"
```

Print the commit hash.

Clean up the template clone:

```bash
rm -rf .claude_dev_template
```

---

## Step 9 — Final report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  /prj-convert complete

  Project  : [name]
  Location : [path]
  Phases   : N phases (M complete, K remaining)
  CLAUDE.md: N lines (limit: 200)

  Files created  : N
  Files merged   : N
  Files skipped  : N

  Skipped (existing content preserved):
    [list of skipped files and why]

  Architectural improvements added as tasks:
    [list with task number and phase]

  Commit: [hash]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run /phase-review to validate Phase [N].
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Rules

- Read everything before creating anything.
- Never overwrite a file with real content without explicit user confirmation.
- Show TASKS.md before writing — it is the most critical file.
- CLAUDE.md must be under 200 lines when done.
- All `{{PLACEHOLDER}}` values must be filled before committing.
- If you cannot get real template files, stop. Do not install command files from memory.
- session-start.sh must be executable after writing.
- Architectural improvement tasks are additions, never replacements of existing tasks.
- The final output must say "Run /phase-review to validate Phase [N]."
