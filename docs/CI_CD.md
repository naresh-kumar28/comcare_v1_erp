# ComCare — CI/CD Guide

## 1. Overview

- **CI** — `.github/workflows/ci.yml`
  - Triggers: `push` to `main`/`develop`, and every `pull_request`.
  - Jobs:
    1. **test** — pip install → `manage.py check` → `manage.py test` → `collectstatic`.
    2. **deploy-check** — `manage.py check --deploy` + `manage.py migrate --plan`
       under production-like settings (dummy credentials, never real ones).
  - The pipeline **fails** if any check, test, or collect fails.

- **CD** — `.github/workflows/deploy.yml`
  - Triggers: `push` to **`main` only** (+ manual `workflow_dispatch`).
  - Runs on the VPS via SSH and performs pull → deps → check → migrate →
    collectstatic → restart → health check.

## 2. Flow

```
feature/*  --PR-->  develop/main  --CI-->  merge to main  --CD-->  VPS production
```

Production only ever deploys `main`. Feature branches never auto-deploy.

## 3. GitHub Secrets required

| Secret | Value |
|--------|-------|
| `VPS_HOST` | Hostinger VPS IP / hostname |
| `VPS_USER` | SSH user (must be able to `git` in `/ComCare`) |
| `VPS_SSH_KEY` | Private SSH key (deploy key / user key) |
| `VPS_PORT` | SSH port (default 22) |
| `VPS_DEPLOY_PATH` | Deploy dir — default `/ComCare` |

Store secrets at **repository → Settings → Secrets and variables → Actions**.
Use an SSH key (not a password). Recommended: a dedicated deploy key restricted
to read access + the sudoers rule in DEPLOYMENT.md section 3.

### Optional extra
- `VPS_HEALTH_PORT` — only if Gunicorn is not on 8080.

## 4. Failure handling in CD

Every step uses `set -e` semantics and explicit guards:

| Failure | Consequence |
|---------|-------------|
| `.env` missing a required key | Deploy stops before touching code. |
| `pip install` fails | Stops. |
| `check --deploy` fails | Stops. |
| `migrate` fails | Stops **before** service restart (old service stays up). |
| `collectstatic` fails | Stops **before** service restart. |
| `systemctl restart` fails | Prints status + `journalctl -u comcare -n 100`, exit 1. |
| Health check fails | Prints logs, exit 1. |

## 5. SSH authentication

`appleboy/ssh-action` uses the private key from `VPS_SSH_KEY`, connecting as
`VPS_USER@VPS_HOST:VPS_PORT`. No passwords are used. The **production `.env`
stays on the VPS** and is never copied from or to GitHub.

## 6. Adding CI secrets to a local copy

```bash
gh secret set VPS_HOST
gh secret set VPS_USER
gh secret set VPS_PORT
gh secret set VPS_DEPLOY_PATH
gh secret set VPS_SSH_KEY --body "$(cat ~/.ssh/id_ed25519)"
```

## 7. Local CI simulation

```bash
pip install -r requirements.txt
python manage.py check
python manage.py test
DJANGO_DEBUG=False python manage.py check --deploy   # with valid prod-like env
python manage.py collectstatic --noinput
```