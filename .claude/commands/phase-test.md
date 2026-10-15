# /phase-test

Verify that a completed phase actually works as expected.
Run this manually after reviewing /phase-run output.
Runs all tests before reporting — you get the full picture in one pass.

On a clean pass, advances ## Resume Here to the next phase.
On failure, reports all failures together and stops.

## Model

**Haiku.** Delegate all steps to a Haiku sub-agent:
- Agent tool, subagent_type: general-purpose, model: haiku
- Pass all steps and rules below as the complete prompt
- If the Agent tool call fails, execute in the current session

---

## The intended workflow

```
/phase-run           → completes the phase, then stops
                     → review the output
/phase-test          → you invoke this when ready
                     → all tests run, all results collected
                     → PASSED: ## Resume Here advances, ready for next /phase-review
                     → FAILED: failures reported, you fix, re-run /phase-test
```

---

## Auto mode (invoked as `/phase-test auto`)

When the argument `auto` is present, this command is being driven by `/phase-auto`
as one bounded unit of work. When invoked WITHOUT `auto`, ignore this entire
section and behave exactly as documented below.

In auto mode:

- **Never prompt and never wait.** The orchestrator owns every stop-and-ask;
  sub-agents cannot reach the user.
- **Run the full suite every time.** Do not narrow to previously-failed tests — a
  fix can regress a test that was passing. The orchestrator re-invokes this command
  after each fix attempt and depends on full coverage.
- **On PASS, behave exactly as in manual mode:** advance `## Resume Here` to the
  next phase and commit. That commit is the stage boundary the orchestrator relies
  on for crash safety.
- **On FAIL, do not attempt fixes.** Fixing is the orchestrator's Opus fixer, not
  this command. Report and return.
- **Never disable, skip, or weaken a test to make it pass.** A test that cannot pass
  is a FAIL to be reported, not an obstacle to route around.
- **⚠️ MANUAL items are not failures.** Report them separately so the orchestrator
  can surface them in its final summary for the user to perform by hand.
- **Return a compact result block** to the caller, in addition to the normal
  full report:

  ```
  PHASE_TEST_RESULT
  status: [PASSED | FAILED]
  passed: [N]
  failed: [N]
  manual: [N]
  failures:
    - [test id] — [one-line reason] — [key error output]
  ```

Everything else — building the plan from the Definition of Done, running every test
before reporting, the PASS/FAIL determination rules — happens exactly as in normal
mode.

---

## Step 1 — Identify what to test

Read:
- `TASKS.md` → CURRENT_PHASE number and name (what was just run)
- `docs/PHASE_NOTES.md` → CURRENT_PHASE Definition of Done — this is the primary
  test specification. Every condition stated here must have a corresponding test.
- `CLAUDE.md` → port map, critical constraints
- `docker compose ps` → which services are currently running

Build the test plan from the Definition of Done before running anything.

---

## Step 2 — Print the test plan

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  /phase-test — Phase [N]: [Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Definition of done:
[paste from PHASE_NOTES.md]

Test plan:
[T01] [description of what will be tested]
[T02] [description]
...

Running all tests. All results collected before reporting.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 3 — Run all test categories

Run every applicable category. Skip categories that don't apply to this phase.
Print each test ID as it runs but collect pass/fail status — do not stop on failure.

The categories are universal; the commands inside them are project-specific. Categories
A, F and G are stack-independent and written out below. Categories B–E come from
`{{STACK_SPECIFIC_TESTS}}`, filled in at bootstrap from this project's actual stack.

### Category A: Service health

For every service brought up in this phase:
```bash
docker compose ps [service]
```

Prefer Docker's own healthcheck status. It works for every service, including
`expose`-only ones that are not bound to a host port — a common and correct pattern
when a reverse proxy reaches containers by service name:
```bash
docker compose ps --format json \
  | jq -rs '.[] | "\(.Service)\t\(.Health // "none")\t\(.State)"'
```

A service with a healthcheck reports `healthy`; one without reports `none` and is judged
on `.State` alone. (`docker inspect --format` can read the same field, but its Go template
braces collide with this template's `{{PLACEHOLDER}}` convention and with the Category F
placeholder scan — prefer the JSON form above.)

Do **not** reach for `curl http://localhost:[PORT]/health` as the default — it fails for
every service without a host port binding, which looks like a broken service when the
service is fine. Use it only for services this project actually publishes to the host.

`[T0N] ✅ [service] healthy` or `[T0N] ❌ [service] unhealthy — [error]`

### Categories B–E: Stack-specific tests

{{STACK_SPECIFIC_TESTS}}

<!--
  BOOTSTRAP: replace {{STACK_SPECIFIC_TESTS}} with this project's real commands, keeping
  these four category headings. Every command must run against a service this project
  actually has. Run each one once while filling it in — a test that cannot execute is
  worse than no test, because it reports as a phase failure forever.

  ### Category B: Data layer
    For each datastore touched this phase: verify the expected schema objects exist
    (tables / collections / indexes / buckets / constraints), and verify the project's
    data-ownership invariant is enforced by the STORE, not by convention — attempt the
    write that must be rejected and assert it fails. If the project has migrations,
    verify re-running a fully-applied set is a no-op, not an error.
    Reach datastores through `docker compose exec <service>`, never a host DB client.

  ### Category C: API endpoints
    The unauthenticated liveness endpoint answers with a real body, not a bare 200.
    Each endpoint built this phase returns what it should with valid credentials.
    An unauthenticated request to a protected endpoint returns 401, not data.
    For `expose`-only services, call from inside the container
    (`docker compose exec <svc> wget -qO- http://localhost:<port>/...`) or through the
    proxy — never `localhost:<port>` from the host.

  ### Category D: Authorization enforcement
    MANDATORY whenever auth or data access was touched this phase. Never skipped.
    Assert the project's isolation rule positively AND negatively: the authorized
    caller can read its own data, and a caller from another owner/tenant CANNOT —
    returning the project's chosen not-found/forbidden status, never data. Prefer 404
    over 403 where existence itself is sensitive.

  ### Category E: Frontend build / UI
    If there is no test runner, a successful production build IS the verification:
    `docker compose run --rm <web> npm run build` (in the container — nothing installs
    on the host). If the project has a fidelity or snapshot guarantee, run that suite
    here and treat any delta as a FAIL, not a warning.

  Omit any category this project genuinely does not have (e.g. E for a headless
  service), and say so in the file rather than leaving a stub that silently passes.
-->

### Category F: Git hygiene

Always run:
```bash
# .env not committed
git ls-files .env 2>/dev/null | wc -l

# .env.example is committed
git ls-files .env.example

# CLAUDE.md and TASKS.md ARE tracked — the phase workflow depends on it
git ls-files --error-unmatch CLAUDE.md TASKS.md >/dev/null 2>&1 \
  && echo "PASS: context files tracked" \
  || echo "FAIL: CLAUDE.md or TASKS.md is untracked — check .gitignore"

# No unfilled placeholders left in committed files
git grep -nE '\{\{[A-Z][A-Z0-9_]*\}\}' \
    -- '*.md' '*.json' '*.yml' '*.yaml' '*.sh' 2>/dev/null \
  | grep -vE '\{\{PLACEHOLDERS?\}\}' | head -10
```
Any committed `.env`, untracked context file, or unfilled placeholder is a test failure.

> The pattern deliberately matches only an UPPER_SNAKE name wrapped in double braces.
> A bare search for two open braces also hits Go template syntax that is *supposed* to
> survive bootstrap — the `.Names` format string in the session hook, `.Repository` and
> `.Tag` in `/prj-manage` — and the literal word PLACEHOLDER used in prose by
> `/prj-drift` and `/prj-convert`. Those are excluded, so this test reports real
> findings instead of failing on every run.
>
> Note for whoever edits this file: do not write an example placeholder literally here.
> This test greps its own command files, so a sample token in this prose becomes a
> permanent false failure. That has happened twice.

### Category G: Definition of done — line by line

After the above, go through the Definition of Done statement condition by condition.
For each condition that cannot be verified non-interactively, print:
```
[T0N] ⚠️  MANUAL — [condition text]
           Steps: [exact steps to verify this manually]
```
Manual items are not counted as failures.

---

## Step 4 — Collect and report all results

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  /phase-test Results — Phase [N]: [Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Automated tests:
[T01] ✅ [description]
[T02] ❌ [description] — [error]
[T03] ✅ [description]
...

Manual verification required:
[T0N] ⚠️  [condition] — [steps]

Summary:
  Passed : [N]
  Failed : [N]
  Manual : [N]
  Total  : [N]

Overall: [PASSED / FAILED]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Overall is PASSED only if zero automated tests failed.
Manual items do not affect the determination.

---

## Step 5 — On failure

For each failure, print the full error output.

Log each to TASKS.md Blockers Log:
```
[date] phase-test phase [N] — [T0N] [description]: [error summary]
```

Print:
```
Fix the failures above and re-run /phase-test.
## Resume Here has not been advanced.
Do not run /phase-review for Phase [N+1] until this passes.
```

Stop. Do not advance ## Resume Here.

---

## Step 6 — On pass

Advance TASKS.md ## Resume Here:
```
## Resume Here

**Current phase:** [N+1] — [Phase N+1 Name]
**Next task:** [N+1].1 — [first task]
**Notes:** Phase [N] complete and tested [date]. Starting fresh.
```

Commit:
```bash
git add -A
git commit -m "phase [N] verified — /phase-test passed — advancing to phase [N+1]"
```

Print:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Phase [N] verified — all tests passed

  ## Resume Here advanced to Phase [N+1]: [name]

  Next steps:
    Run /phase-review to assess Phase [N+1] before /phase-run
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Rules

- Run ALL tests before reporting. Never stop on first failure.
- The authorization enforcement test (Category D) is mandatory if auth was built. Never skip it.
- Manual items are surfaced clearly, never silently dropped.
- Log all failures to TASKS.md Blockers Log.
- Advance ## Resume Here only on a clean pass.
- Overall PASSED requires zero automated failures.
- Do not invoke /phase-review or /phase-run. You decide what comes next.
