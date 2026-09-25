# ComCare — Security Audit

Date: 2026-09-19

This document records the Django security audit, every finding, and the
disposition (fixed / by design / documented risk). Validation commands used:
`manage.py check`, `manage.py check --deploy`.

## Summary of `check --deploy` after fixes (production-like env)

Only two intentional warnings remain:

1. `security.W008` — `SECURE_SSL_REDIRECT` off. **By design**: Nginx already
   redirects HTTP→HTTPS at the edge. Enabling it in Django risks redirect loops
   unless the proxy passes `X-Forwarded-Proto`.
2. `security.W021` — `SECURE_HSTS_PRELOAD` off. **By design**: opt-in, requires
   cert authority registration. HSTS is served (31536000s, include subdomains).

## Findings & Fixes

### CRITICAL — Fixed

1. **Payment verification was forgeable**
   - `apps/cart/views.py::verify_payment` looked an order up by number without
     owner/session checks AND treated a missing `RAZORPAY_KEY_SECRET` as
     "verified = True" (sandbox fallback). If production had no secret set,
     anyone could mark any guessable order paid without paying.
   - **Fix:**
     - Signature-less verification allowed only when `settings.DEBUG` is True
       (local development). In production with no keys, verification fails.
     - The submitted `razorpay_order_id` must equal the order id the server
       stored at `place_order` time (prevents replay of a payment made against
       a different order).
     - Signature verified through the official `razorpay.Client.utility.verify_payment_signature`.
     - Already-paid orders are treated as idempotent successes and are never
       downgraded to `failed` by a later bad request.

2. **Full PII exposure via order-success page**
   - `order_success` returned any order by number with **no authentication**.
     Order numbers are 5-digit guesses; this exposed name, address, phone, and
     the invoice access token (which unlocks the full invoice).
   - **Fix:** added `_can_access_order(request, order)` — allowed only for
     staff, the owning user, a matching order email for the logged-in user, or
     a matching `session_key`. Otherwise a 200 page is rendered with no order
     data (no existence leak).

### HIGH — Fixed

3. **Open redirect via `HTTP_REFERER`**
   - `ToggleWishlistView` and `admin_coupon_save` redirected to
     `request.META['HTTP_REFERER']` untrusted.
   - **Fix:** new helper `apps/cart/utils.py::safe_referer(request, default)`
     returns the referer only when it is same-origin, else the default URL.
     Used in both views.

4. **`ALLOWED_HOSTS = ['*']`**
   - Enabled host-header attacks (password-reset link poisoning).
   - **Fix:** env-driven `ALLOWED_HOSTS`, default `localhost,127.0.0.1,[::1]`.

5. **Hard-coded database password committed**
   - `config/settings.py` contained a commented-out MySQL block with a real
     password (`Root@123`).
   - **Fix:** removed the block entirely. *(Recommendation: if that MySQL/UDB
     account still exists anywhere, rotate it — the value is in git history.)*

### MEDIUM — Fixed

6. **`requirements.txt` was UTF-16 encoded** — broke `pip install` and any CI.
   Converted to UTF-8 (content unchanged).

7. **Fresh-session guest cart association bug** (`_cart_id` returned the return
   value of `request.session.create()`, which is `None`). This silently created
   carts with no `session_key`. Fixed in `apps/cart/views.py`.
8. **`Product.final_price`** referenced a non-existent `self.price`. Now aliases
   `selling_price`. (Dead code, fixed for correctness.)
9. **Review rating not range-checked** — now clamped to 1–5 in
   `apps/reviews/views.py`.
10. **No production logging strategy** — added Django `LOGGING` (console handler
    → captured by systemd/journalctl). Keys, tokens, passwords are never logged.
11. **No `/health/` endpoint** — added (HTTP 200; returns only `status`/`database`,
    no secrets).

### By design / documentation (no code change)

12. **GET-based state changes** (cart add/remove, wishlist toggle, buy-now) are
    CSRF-exposed because they are idempotent-ish session mutations triggered via
    GET (the frontend uses plain links/HTMX GET). Converting to POST requires UI
    changes. **Recommended follow-up.**
13. **File uploads unrestricted** (profile picture, product/gallery images,
    service device photo) — Django does not validate model-field uploads on
    `.save()`. Risk: crafted files served from storage. **Recommended follow-up.**
14. **Order numbers are 5-digit** (`BIT-ORD-#####`, `random.randint`). Low
    entropy for an order ID; mitigated now that order-success/invoice access is
    scoped. **Recommended follow-up: `secrets` + longer alphabet + retry.**
15. **Guest→user data linking by unverified phone/email** on login
    (`apps/cart/utils.py::link_guest_orders`). A later user claiming the same
    phone inherits earlier guest orders. **Recommended follow-up: verify contact
    before linking, or scope linking to `session_key` only.**
16. **Unused/removed deps**: `mysqlclient`, `PyMySQL` removed (never imported).
17. **`FailedSearchLog`** stores raw queries + IPs indefinitely — GDPR/retention
    note. **Recommended follow-up.**
18. **DUO coupon `used_count` increment is not atomic-locked** — race could
    exceed `usage_limit`. **Recommended follow-up.**

## What is already correct (unchanged)

- No `csrf_exempt` anywhere; POST flows use Django CSRF + HTMX `X-CSRFToken`.
- `SecurityMiddleware`, `WhiteNoiseMiddleware`, `XFrameOptionsMiddleware` present
  and ordered correctly.
- Password validators: all four Django defaults are configured.
- `SECRET_KEY`, DB URL, email password, Razorpay keys, Cloudinary secrets all
  come from environment variables (no hard-coded secrets after cleanup).
- Staff-only admin panel; order/address/review access is scoped; `CancelOrderView`
  ownership-checked.
- Prices are computed server-side in `place_order` (no client price injection).
- `.env` is git-ignored.

## Secrets hygiene

- `grep` for `password=`, `SECRET_KEY=`, `API_KEY=`, `DATABASE_URL=`,
  `CLIENT_SECRET=` across tracked files returned only the (now removed) MySQL
  comment in settings.py. Cloudinary/Razorpay/Gmail values are never committed.
- The real `SECRET_KEY`, `DATABASE_URL`, `RAZORPAY_KEY_SECRET`,
  `CLOUDINARY_API_SECRET`, `EMAIL_HOST_PASSWORD` live **only** in the VPS `.env`.

## PRODUCTION ACTION REQUIRED (VPS, before deploying this code)

Add to `/ComCare/.env` (do NOT commit; edit on the VPS):

```
DJANGO_DEBUG=False
ALLOWED_HOSTS=comcare.cc,www.comcare.cc
CSRF_TRUSTED_ORIGINS=https://comcare.cc,https://www.comcare.cc
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
```

If Nginx does not already forward the scheme, add to the server block:
`proxy_set_header X-Forwarded-Proto $scheme;` then `sudo nginx -t && sudo systemctl reload nginx`.

If `RAZORPAY_KEY_SECRET` is not set in production `.env`, Razorpay payments will
now **fail verification** (they previously auto-passed). If the site takes live
Razorpay money, confirm the live keys are present; otherwise place
`RAZORPAY_MODE=test` explicitly and treat gateway as dev-only.