# ComCare — Environment Reference

Every runtime value is read from environment variables via `python-decouple`
(`config/settings.py`). A `.env` file in the project root supplies them locally
and on the VPS (systemd `EnvironmentFile=/ComCare/.env`).

## Required everywhere

| Variable | Purpose | Notes |
|----------|---------|-------|
| `DJANGO_SECRET_KEY` | Signing/security | Required always; `ImproperlyConfigured` if missing. Long random string. Never commit. |

## Local development (DEBUG=True)

| Variable | Required? | Default |
|----------|-----------|---------|
| `DJANGO_DEBUG` | no | `True` (auto-detected when not in production mode) |
| `DATABASE_URL` | no (dev) | empty → SQLite `db.sqlite3` |
| `CLOUDINARY_*` | no (dev) | empty → local `FileSystemStorage` |

Local `.env` (git-ignored) example:

```
DJANGO_SECRET_KEY=<generated random>
DJANGO_DEBUG=True
```

When running `DEBUG=True`, the project behaves "safe-for-dev": SQLite,
local media, granular console logs, lazy session/CSRF/sec flags, AI-development
flag settings.

## Production (DEBUG=False)

| Variable | Required? | Notes |
|----------|-----------|-------|
| `DJANGO_SECRET_KEY` | **yes** | |
| `DJANGO_DEBUG` | yes | must be `False` for prod hardening |
| `ALLOWED_HOSTS` | **yes** | comma-separated, e.g. `comcare.cc,www.comcare.cc` |
| `CSRF_TRUSTED_ORIGINS` | **yes** | comma-separated, https scheme |
| `DATABASE_URL` | **yes** | e.g. `postgres://user:pass@host/db?sslmode=require` |
| `CLOUDINARY_CLOUD_NAME` | **yes** | |
| `CLOUDINARY_API_KEY` | **yes** | |
| `CLOUDINARY_API_SECRET` | **yes** | |

If any required production var is missing the app raises `ImproperlyConfigured`
at startup (fail-fast, no silent misconfiguration).

## All variables (full list)

| Variable | Required (prod) | Default | Used for |
|----------|-----------------|---------|----------|
| `DJANGO_DEBUG` | yes | `True` | DEBUG + automatic dev mode |
| `DJANGO_SECRET_KEY` | yes | — | cryptography, sessions |
| `ALLOWED_HOSTS` | yes | `localhost,127.0.0.1,[::1]` | host allowlist |
| `CSRF_TRUSTED_ORIGINS` | yes | — | CSRF origin allowlist |
| `DATABASE_URL` | yes | sqlite (dev) | DB connection |
| `DJANGO_CONN_MAX_AGE` | no | `0` | DB persistent connections |
| `DJANGO_SESSION_COOKIE_SECURE` | no | `not DEBUG` | secure session cookie |
| `DJANGO_CSRF_COOKIE_SECURE` | no | `not DEBUG` | secure CSRF cookie |
| `DJANGO_SECURE_SSL_REDIRECT` | no | `False` | HTTPS redirect (Nginx handles) |
| `DJANGO_HSTS_SECONDS` | no | `31536000` | HSTS max-age; `0` disables |
| `DJANGO_HSTS_PRELOAD` | no | `False` | HSTS preload opt-in |
| `DJANGO_SECURE_REFERRER_POLICY` | no | `strict-origin-when-cross-origin` | Referrer-Policy header |
| `EMAIL_BACKEND` | no | SMTP | email backend |
| `EMAIL_HOST` | no | `smtp.gmail.com` | SMTP host |
| `EMAIL_PORT` | no | `587` | SMTP port |
| `EMAIL_USE_TLS` | no | `True` | SMTP TLS |
| `EMAIL_HOST_USER` | no | — | SMTP user |
| `EMAIL_HOST_PASSWORD` | no | — | SMTP password |
| `DEFAULT_FROM_EMAIL` | no | `EMAIL_HOST_USER` | from address |
| `RAZORPAY_KEY_ID` | no | — | Razorpay |
| `RAZORPAY_KEY_SECRET` | no | — | Razorpay |
| `RAZORPAY_MODE` | no | `test` | gateway mode prompt |
| `GOOGLE_CLIENT_ID` | no (unused) | — | reserved for OAuth |
| `GOOGLE_CLIENT_SECRET` | no (unused) | — | reserved for OAuth |
| `CLOUDINARY_CLOUD_NAME` | yes | — | media storage |
| `CLOUDINARY_API_KEY` | yes | — | media storage |
| `CLOUDINARY_API_SECRET` | yes | — | media storage |

## Secure-cookie & HSTS behavior in production

When `DJANGO_DEBUG=False` and not overridden, the settings automatically:
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_HSTS_SECONDS = DJANGO_HSTS_SECONDS`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
- `SECURE_HSTS_PRELOAD = DJANGO_HSTS_PRELOAD` (default False)
- `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`
- `X_FRAME_OPTIONS = 'SAMEORIGIN'` (always)

## .env handling rules (safety)

1. `.env` is git-ignored — never commit it.
2. `chmod 600 .env` on shared systems.
3. Format: `KEY=value`, one per line; no spaces around `=`; CSV values are
   comma-separated; comments with `#`.
4. VPS `.env` is the single source of truth for production secrets.
5. `.env.example` in the repo lists variables with blank values for reference —
   never fill real secrets into `.env.example`.

## Tips

- Generate a secret: `python -c "import secrets; print(secrets.token_urlsafe(60))"`.
- Check what the app thinks is configured:
  ```bash
  .venv/bin/python manage.py shell -c "from django.conf import settings; print(settings.DEBUG)"
  ```