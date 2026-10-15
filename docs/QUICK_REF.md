# Quick Reference — {{PROJECT_NAME}}

> One-page cheat sheet. Commands you'll run repeatedly.
> Full context lives in docs/PHASE_NOTES.md and docs/ARCHITECTURE.md.

---

## Stack Control

```bash
# Start full stack
docker compose up -d

# Start single service
docker compose up -d {{SERVICE_NAME}}

# Stop full stack
docker compose down

# Rebuild a service after code change
docker compose up -d --build {{SERVICE_NAME}}

# View logs (live)
docker compose logs -f {{SERVICE_NAME}}

# Check all service health
docker compose ps
```

---

## Health Checks

```bash
# Check each service endpoint
{{HEALTH_CHECK_COMMANDS}}
```

---

## Secret Generation

```bash
# Standard secret (hex)
openssl rand -hex 32

# Standard secret (base64)
openssl rand -base64 32
```

---

## Init / One-Shot Operations

```bash
# Run DB init scripts
{{INIT_COMMANDS}}
```

---

## Git Workflow

```bash
# Standard commit
git add -A && git commit -m "description"

# Check what's changed
git status && git diff --stat
```

---

## SSH Tunnel Reference

```bash
# Open tunnel to {{SERVICE}} on port {{PORT}}
ssh -L {{PORT}}:localhost:{{PORT}} {{HOST}}

# Full tunnel (all services at once)
{{FULL_TUNNEL_COMMAND}}
```

---

## Common Fixes

| Problem | Fix |
|---|---|
| {{PROBLEM_1}} | {{FIX_1}} |
| {{PROBLEM_2}} | {{FIX_2}} |

---

## Critical Rules (Never Break)

- {{RULE_1}}
- {{RULE_2}}
- {{RULE_3}}
