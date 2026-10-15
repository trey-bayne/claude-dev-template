# Environment Variables — {{PROJECT_NAME}}

> Full variable reference. The authoritative key list is `.env.example`.
> Never put real values in any committed file.
> Add a row here whenever you add a variable to .env.example.

---

## Infrastructure

| Variable | Description | Example |
|---|---|---|
| `COMPOSE_PROJECT_NAME` | Docker compose project namespace | `{{PROJECT_SLUG}}` |

## Volume Paths

| Variable | Description | Storage tier |
|---|---|---|
| `{{VOLUME_VAR}}` | {{VOLUME_DESCRIPTION}} | {{STORAGE_TIER}} |

## Service Credentials

| Variable | Description | Generate with |
|---|---|---|
| `{{CRED_VAR}}` | {{CRED_DESCRIPTION}} | `openssl rand -hex 32` |

## External APIs

| Variable | Description | Where to get it |
|---|---|---|
| `{{API_VAR}}` | {{API_DESCRIPTION}} | {{API_SOURCE}} |

## Application Config

| Variable | Description | Default |
|---|---|---|
| `{{CONFIG_VAR}}` | {{CONFIG_DESCRIPTION}} | `{{DEFAULT}}` |

---

## .env.example

```
{{ENV_EXAMPLE_BLOCK}}
```
