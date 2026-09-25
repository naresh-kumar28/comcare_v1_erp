# ComCare — Changelog

Date format: YYYY-MM-DD. Projects follows the rule **one entry per meaningful
change**; docs/audit summaries count.

## 2026-09-19 — Security, DevOps & QA overhaul

### Security / correctness
- Removed a commented-out MySQL block containing a live database password from
  `config/settings.py` (credentials must never be committed).
- Fixed `verify_payment` in `apps/cart/views.py`:
  - sandbox/signature-less auto-verify is now allowed **only** in `DEBUG=True`;
  - submitted `razorpay_order_id` must match the server-created order id;
  - idempotent for already-paid orders; paid→failed downgrade is impossible.
- Scoped `order_success` data access via `_can_access_order(request, order)`
  (staff / owner user / matching order-email / matching session) — no more
  unauthenticated PII disclosure.
- Fixed open redirects (`HTTP_REFERER`) in `ToggleWishlistView`
  (`apps/accounts/views.py`) and `admin_coupon_save` (`apps/admin/views.py`)
  via new `safe_referer()` helper (`apps/cart/utils.py`).
- `ALLOWED_HOSTS` now env-driven (previously `['*']`).
- Review rating clamped to 1–5 in `apps/reviews/views.py`.
- `Product.final_price` now returns `selling_price` (was broken, missing attr).
- Fixed `_cart_id` returning `None` for fresh sessions (guest carts could get
  `session_key=None`).

### Configuration
- Rewrote `config/settings.py` around `python-decouple`:
  - `DJANGO_SECRET_KEY` required everywhere; `ImproperlyConfigured` if missing.
  - Production requires `DATABASE_URL`, `CLOUDINARY_*`, `ALLOWED_HOSTS`,
    `CSRF_TRUSTED_ORIGINS`; no silent fallbacks when `DEBUG=False`.
  - Auto security hardening when not DEBUG: secure session/CSRF cookies, HSTS,
    `SECURE_PROXY_SSL_HEADER`; `X_FRAME_OPTIONS=SAMEORIGIN` always.
  - Static backend: manifest in production, `CompressedStaticFilesStorage` in dev.
  - Added console `LOGGING` (systemd/journald friendly).
- Added `/health/` endpoint (`apps/core/views.py`, `config/urls.py`) returning
  `{"status": "ok", "database": "ok"}`.

### Dependencies
- Converted `requirements.txt` from UTF-16 to UTF-8 (content unchanged).
- Removed unused `mysqlclient==2.2.8` and `PyMySQL==1.2.0` (never imported;
  blocked pip installs).

### Hygiene
- Added `apps/__init__.py` (applications were namespace packages).
- Added `.env.example`; `.gitignore` now excludes `/static/` and `.DS_Store`.
- Local development `.env` created (git-ignored, random secret, `DEBUG=True`).

### Tests (new)
- `apps/store/tests.py` — product model properties; shared `make_image()` helper.
- `apps/cart/tests.py` — order model, cart views, checkout flow, payment
  verification security suite (incl. `DEBUG=False` + mocked Razorpay).
- `apps/coupons/tests.py`, `apps/reviews/tests.py`, `apps/services/tests.py` —
  model/property tests.
- `apps/core/tests.py` — health endpoint + public page smoke tests.
- **34 tests, all pass.**

### CI/CD
- `.github/workflows/ci.yml` — checks + full test suite + prod-mode
  `check --deploy` on every push/PR.
- `.github/workflows/deploy.yml` — SSH deploy to production on `main`:
  git pull → pre-deploy `.env` validation → deps → `check --deploy` → migrate →
  collectstatic → restart → health check.

### Documentation
- `README.md`; `docs/PROJECT_AUDIT.md`, `docs/SECURITY_AUDIT.md`,
  `docs/DEPENDENCY_AUDIT.md`, `docs/ENVIRONMENT.md`, `docs/DEPLOYMENT.md`
  (incl. rollback plan), `docs/CI_CD.md`.

### Production required
- VPS `.env` must add `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`; confirm
  `DJANGO_DEBUG=False`; optional secure-cookie flags. See
  `docs/SECURITY_AUDIT.md` → "PRODUCTION ACTION REQUIRED".

### Not implemented (documented)
- Google OAuth (reserved `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`).