# ComCare — Production Deployment Guide

Covers VPS architecture, systemd, Gunicorn, Nginx, SSL, the deployment process,
rollback, logs, and troubleshooting.

## 1. Architecture

```
Internet
  ↓  https://comcare.cc  (Let's Encrypt TLS; Nginx 301 for HTTP→HTTPS, www)
Nginx   (listen 80/443, proxy to 127.0.0.1:8080)
  ↓  proxy_pass http://127.0.0.1:8080;
Gunicorn (comcare.service, WorkingDirectory=/ComCare)
  ↓
Django / WhiteNoise (static) / Cloudinary (media) / Neon PostgreSQL
```

Gunicorn binds **127.0.0.1:8080 only** — never exposed publicly.

## 2. systemd (`comcare.service`)

Reference unit (already running on the VPS — do not recreate from scratch):

```ini
[Unit]
Description=Gunicorn instance for ComCare
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/ComCare
EnvironmentFile=/ComCare/.env
ExecStart=/ComCare/.venv/bin/gunicorn --bind 127.0.0.1:8080 --workers 3 config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5
KillMode=mixed

[Install]
WantedBy=multi-user.target
```

Checks:

```bash
sudo systemctl status comcare --no-pager
sudo systemctl is-enabled comcare
sudo systemctl is-active comcare
journalctl -u comcare -n 100 --no-pager
journalctl -u comcare -f
```

> Note: `EnvironmentFile=/ComCare/.env` loads vars into the process.
> Add `Environment=PYTHONUNBUFFERED=1` for real-time logs if desired.

## 3. Nginx

User blocks (do not overwrite working files blindly; verify first):

```nginx
server {
    listen 80;
    server_name comcare.cc www.comcare.cc;
    location /.well-known/acme-challenge/ { root /var/www/letsencrypt; }
    location / { return 301 https://$host$request_uri; }
}

server {
    listen 443 ssl http2;
    server_name comcare.cc www.comcare.cc;

    ssl_certificate     /etc/letsencrypt/live/comcare.cc/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/comcare.cc/privkey.pem;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;   # required for secure cookies/HSTS
    }
}
```

Verify with `sudo nginx -t` before reloading.

**(Optional, recommended)** give deploy user passwordless systemd access so the
CD pipeline can restart without prompting:

```bash
sudo tee /etc/sudoers.d/comcare-deploy <<'EOF'
deployuser ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart comcare, /usr/bin/systemctl status comcare, /usr/bin/systemctl is-active comcare
EOF
sudo chmod 440 /etc/sudoers.d/comcare-deploy
```

## 4. SSL / HTTPS

- Certificates: Let's Encrypt via certbot, domain `comcare.cc` + `www.comcare.cc`.
- HTTP is redirected to HTTPS by Nginx (`return 301`).
- Django serves `Strict-Transport-Security` (31536000s, includeSubDomains) when
  `DEBUG=False`.
- **Renewal** — certbot cron/timer:
  ```bash
  sudo certbot renew --dry-run        # verify
  systemctl list-timers | grep certbot
  ```
  Standard renewal hook reloads nginx automatically.

## 5. Production `.env` (VPS ONLY — never in git)

Required keys on the VPS (edit `/ComCare/.env`):

```
DJANGO_SECRET_KEY=<real value>
DJANGO_DEBUG=False
ALLOWED_HOSTS=comcare.cc,www.comcare.cc
CSRF_TRUSTED_ORIGINS=https://comcare.cc,https://www.comcare.cc
DATABASE_URL=postgres://...?...sslmode=require
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<real value>
EMAIL_HOST_PASSWORD=<real value>
DEFAULT_FROM_EMAIL=<real value>
RAZORPAY_KEY_ID=<live key>
RAZORPAY_KEY_SECRET=<live secret>
RAZORPAY_MODE=live
CLOUDINARY_CLOUD_NAME=<real value>
CLOUDINARY_API_KEY=<real value>
CLOUDINARY_API_SECRET=<real value>
```

Permissions: `chmod 600 .env`.

## 6. Automated Deployment (CD)

`.github/workflows/deploy.yml` runs on every push/merge to `main` and manually
via `workflow_dispatch`. Steps executed on the VPS:

1. `git checkout main && git pull --ff-only`
2. Verify `.env` prerequisites (fails fast, prints no secrets)
3. `pip install -r requirements.txt`
4. `python manage.py check --deploy`
5. `python manage.py migrate --noinput`
6. `python manage.py collectstatic --noinput`
7. `sudo -n systemctl restart comcare`
8. Health check on `http://127.0.0.1:8080/health/`

**Guarantees:** if migrate or collectstatic fails, the service is never
restarted and the workflow exits non-zero (old process keeps serving).
If systemd restart or health fails, logs are printed and the job fails.

GitHub Secrets required: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, `VPS_PORT`
(default 22), `VPS_DEPLOY_PATH` (default `/ComCare`).

## 7. Manual Deployment

```bash
ssh user@VPS
cd /ComCare
git fetch --all && git checkout main && git pull --ff-only origin main
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py check --deploy
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py collectstatic --noinput
sudo -n systemctl restart comcare
curl -fsS http://127.0.0.1:8080/health/
```

## 8. Health Check

`GET /health/` returns `{"status": "ok", "database": "ok"}` (HTTP 200). It does
a `SELECT 1` and exposes no configuration or secrets. External monitoring can
poll `https://comcare.cc/health/`.

## 9. Rollback Plan

Rolling back **code**:

1. Find the last good commit:
   ```bash
   cd /ComCare
   git log --oneline -10
   GOOD=<sha-1>
   git checkout main && git reset --hard "$GOOD"      # or: git revert
   ```
2. Install + validate the previous environment:
   ```bash
   .venv/bin/pip install -r requirements.txt
   .venv/bin/python manage.py check --deploy
   ```
3. Restart and verify:
   ```bash
   sudo -n systemctl restart comcare
   sleep 5
   sudo -n systemctl status comcare --no-pager
   curl -fsS http://127.0.0.1:8080/health/
   ```
4. If still broken, show logs:
   ```bash
   journalctl -u comcare -n 200 --no-pager
   tail -n 100 /ComCare/.env 2>/dev/null  # sanity only
   ```

**Database migrations:** do NOT automatically roll back migrations. If a deploy
with a new migration fails application code, either:
- Keep the DB migrated and roll back only code (new columns are typically
  backward compatible), or
- Re-run the app against migrated schema and hotfix forward.

Only reverse a migration if its reverse operation is explicitly written and the
data risk is understood: `python manage.py migrate <app> <previous_migration> --noinput`,
then restart. Treat this as a manual, deliberate decision.

## 10. Logs & Troubleshooting

| Symptom | Commands |
|---------|----------|
| App errors | `journalctl -u comcare -n 200 --no-pager` |
| Follow live | `journalctl -u comcare -f` |
| Gunicorn config | `sudo systemctl cat comcare` |
| Service not starting | `sudo systemctl status comcare --no-pager` then logs |
| Nginx problems | `sudo nginx -t && sudo systemctl reload nginx` |
| DB connection | `python manage.py check` / check `DATABASE_URL` SSL params |
| HTTPS | `sudo certbot certificates` |
| Static missing | `python manage.py collectstatic --noinput` |

**Log hygiene:** logging is console-only (captured by journald). Passwords,
tokens, API keys, and payment secrets are never logged.