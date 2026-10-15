# /codebase-review

Full codebase audit using parallel Opus agents. Reviews every configured domain across the
entire {{PROJECT_NAME}} codebase.

**Token warning:** A full audit spawns one parallel Opus agent per domain and reads many
files. Budget roughly 50k tokens per domain. Targeted reviews cost proportionally less.

## Usage

```
/codebase-review                  → full audit (all domains in parallel)
/codebase-review <domain>         → that domain only
```

The domain list for this project is defined in **Step 3** below.

## Model

All review agents use Opus via the Agent tool. Never substitute a smaller model —
shallow reviews miss subtle bugs in this codebase.

---

## Step 1 — Parse scope and warn

Read the skill argument (if any) to determine which domains to run.

Valid domains: the domain names defined in Step 3.

If no argument: run all domains.

If the argument is unrecognized, print:
```
Unknown domain: <arg>. Valid options: <the domain names from Step 3>
(no argument = full audit)
```
and stop.

Before proceeding, print:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CODEBASE REVIEW — <DOMAINS>
  Token estimate: <50k per domain × N domains>
  This will use your Claude Code session tokens.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 2 — Gather shared context

Read these files once and hold them in context for all agents:

- `CLAUDE.md` — full file (critical constraints, architecture snapshot)
- `docs/ARCHITECTURE.md` — full file
- `docs/DECISIONS.md` — full file

Run these commands:
```bash
git log --oneline -20
git diff HEAD~1 HEAD --stat 2>/dev/null || echo "(single commit — no previous revision to diff)"
docker compose ps
{{SOURCE_FILE_LISTING_COMMANDS}}
```

---

## Step 3 — Spawn parallel Opus agents

For each domain in scope, launch one Agent tool call. All in-scope domains launch
**simultaneously** in a single message (parallel, not sequential).

Use these parameters for every agent:
- subagent_type: general-purpose
- model: opus

Do NOT await one before launching the next. All parallel agents get the shared
context from Step 2 plus the domain-specific files and instructions below.

### Review domains for this project

{{REVIEW_DOMAINS}}

<!--
  BOOTSTRAP: replace {{REVIEW_DOMAINS}} with one block per domain, in this shape:

  ### Domain: <name>

  **Files to read before reviewing:**
  - <path>
  - <path>

  **Agent prompt:**
  ```
  You are a <role> auditing the <project> codebase.
  <2–5 lines of runtime context this reviewer cannot infer from the files —
   the constraints, invariants, and known footguns of this stack.>

  Review for:
  1. <specific class of defect, named concretely for this stack>
  2. ...

  For every issue found:
  - Severity: CRITICAL / HIGH / MEDIUM / LOW
  - File and line number
  - What the problem is and when it would trigger
  - Concrete fix

  [paste shared context: CLAUDE.md constraints, ARCHITECTURE.md, file contents]
  ```

  START FROM THESE FIVE, which apply to almost any project:

    security      — auth gaps, authorization/ownership gaps, injection, secrets exposure,
                    credential handling, cross-user access, input validation at boundaries
    architecture  — violations of the project's data/ownership model, phase drift, service
                    boundary violations, container/network compliance
    correctness   — logic bugs, async/await correctness, race conditions, error handling
                    gaps, edge cases (empty, None, expired, timeout)
    dead-code     — orphaned tables/collections, unused endpoints, dead env vars, stale
                    services, unreachable paths, duplicate logic, stale comments
    frontend      — framework-specific pattern violations, state/store correctness, API
                    call errors, race conditions, accessibility (omit if no frontend)

  THEN ADD DOMAINS SPECIFIC TO THIS PROJECT'S CORE RISK. The generic five do not cover
  the thing a given project would most regret shipping broken. Make that its own domain.
  Worked example: a document-rendering project added a sixth domain, `render`, auditing
  the editor↔PDF fidelity guarantee — the one invariant its whole product rests on, and
  the one thing no generic domain checks.

  Each domain prompt must name concrete defect classes for THIS stack, not generic advice.
  A reviewer told "check for async bugs" finds nothing; one told "truthiness checks on this
  driver's objects raise TypeError — always compare with `is None`" finds real bugs.
-->

---

## Step 4 — Synthesize findings

After all parallel agents complete, synthesize their reports into a single
prioritized finding list.

Format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CODEBASE REVIEW — <date>
  Domains reviewed: <list>
  Total findings: <N> (<C> critical, <H> high, <M> medium, <L> low)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## CRITICAL
[list all critical findings with file:line, domain tag, and one-line description]

## HIGH
[list all high findings]

## MEDIUM
[list all medium findings]

## LOW
[list all low findings — collapsed, just titles]

## What looks good
[3–5 bullets on well-built areas]
```

Save the full report (including each agent's raw output) to:
`docs/codebase-review-<YYYY-MM-DD>.md`

Print a summary to the terminal. Offer to fix critical and high findings.

---

## Step 5 — Offer fixes

After displaying the synthesis:

```
Found <C> critical and <H> high severity issues.

Fix all critical + high now? [yes / no / show me each one]
```

- **yes** → fix all in sequence, commit: `codebase-review: fix critical+high findings <date>`
- **no** → leave the report in docs/ and stop
- **show me each one** → step through one at a time, fix or skip

After fixing, note which issues were fixed vs. skipped in the saved report.

---

## Rules

- Always use the Agent tool with model=opus for all domain agents.
- All in-scope domain agents launch in parallel — never await one before starting another.
- Do not fabricate findings. If an agent returns no issues for a domain, say so.
- Do not make file changes without confirming with the user first.
- Save the full report to docs/ before offering fixes.
- Never read or write outside `{{PROJECT_PATH}}`. Other projects on this host are reference only.
