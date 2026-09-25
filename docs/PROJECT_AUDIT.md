# ComCare — Project Audit Report

Generated: 2026-09-19

## 1. Project Overview

ComCare is a Django e-commerce platform (IT equipment sales + repair services)
running in production at **https://comcare.cc** on a Hostinger VPS
(Ubuntu 24.04, project path `/ComCare`).

Repository: `github.com/naresh-kumar28/comcare_v1`

## 2. Technology Stack

| Layer        | Technology |
|--------------|-----------|
| Backend      | Django 6.0.7, Python 3.14 (local) / 3.x (VPS) |
| WWW server   | Nginx (reverse proxy, TLS, Let's Encrypt) |
| App server   | Gunicorn 26.0.0 (bound to 127.0.0.1:8080) |
| Process      | systemd service `comcare.service` |
| WSGI         | config/wsgi.py |
| Database     | PostgreSQL (Neon) via `DATABASE_URL` |
| Media        | Cloudinary (`django-cloudinary-storage`) |
| Static       | WhiteNoise (`CompressedManifestStaticFilesStorage`) |
| Payments     | Razorpay (`razorpay==2.0.1`) |
| Config       | `python-decouple` (`.env`) |
| Templates    | Django templates + Tailwind CDN + HTMX + Alpine + Lucide |

## 3. Project Structure

```
ComCare/
├── manage.py
├── requirements.txt
├── build.sh                  # pip install + collectstatic + migrate
├── config/
│   ├── settings.py           # env-based configuration
│   ├── urls.py
│   ├── wsgi.py / asgi.py
│   └── static/               # source static files (git-tracked)
├── apps/
│   ├── accounts/             # CustomUser (email login), profile, addresses, wishlist
│   ├── admin/                # staff dashboard, product/order/customer CRUD (app_label custom_admin)
│   ├── cart/                 # Cart, CartItem, Order, OrderItem, UserAddress, ShippingConfig + payment views
│   ├── categories/           # Category
│   ├── core/                 # home, search, policy pages, health
│   ├── coupons/              # Coupon
│   ├── reviews/              # Review + rating signals
│   ├── services/             # Service, ServiceRequest
│   └── store/                # Product, ProductGalleryImage, Wishlist, RecentlyViewedProduct
├── templates/                # shared templates
├── static/                   # collectstatic output (git-ignored)
├── media/                    # legacy local media (Cloudinary is the real store)
└── docs/                     # documentation (this set)
```

## 4. Django Apps

- **accounts** — custom user model (`AUTH_USER_MODEL = accounts.CustomUser`, email-based auth), profile, addresses, wishlist, invoice.
- **admin** — staff-only panel (`staff_member_required` on all views): dashboard KPIs, product/category/coupon/order/customer/service management.
- **cart** — guest+user carts linked by `session_key`, checkout, Razorpay payments, COD, order success, shipping config singleton.
- **categories** — product categories.
- **core** — landing/search/policy pages + `/health/`.
- **coupons** — fixed/percentage coupons with usage limits and expiry.
- **reviews** — verified-purchase reviews; signals keep `Product.rating`/`reviews_count` in sync.
- **services** — repair service catalogue + customer ServiceRequest (lead) intake.
- **store** — product catalogue with inventory, sale pricing, recent views, wishlist.

## 5. Database

- Production: **PostgreSQL via Neon** using `dj_database_url.parse(DATABASE_URL)`. SSL is handled by the URL (`?sslmode=require`).
- 42 migrations across all apps, all applied. No custom SQL.
- Local development (this phase): SQLite fallback when `DATABASE_URL` is empty and `DEBUG=True`.
- DB state transitions are standard Django/model-layer; no migration auto-generation performed.

## 6. Authentication

- `CustomUser` (email as `USERNAME_FIELD`), `AccountManager` with `create_user`/`create_superuser`.
- Django auth views for login/logout/password change/reset.
- `LoginRequiredMixin`/`@login_required` on account pages; `staff_member_required` on the admin panel.
- Guest carts/orders/addresses/wishlists link to accounts on login via the `user_logged_in` signal (`apps/cart/signals.py`).
- **Google OAuth is NOT implemented** in this codebase (no `allauth`, no Google-specific package). GOOGLE_* environment variables are reserved but unused.

## 7. Payment Integration (Razorpay)

- `apps/cart/views.py`: `place_order` creates the order server-side (server-computed prices) and creates a Razorpay order. `verify_payment` validates the signature.
- Security fixes applied this session (see SECURITY_AUDIT.md):
  - Signatureless "sandbox" auto-verify now only allowed when `DEBUG=True`.
  - Verification now requires the submitted `razorpay_order_id` to match the one the server created for that order.
  - Already-paid orders are idempotent (not re-processed / not downgraded to failed).
  - `order_success` now scoped to the order owner/session.

## 8. Media Storage (Cloudinary)

- `CLOUDINARY_STORAGE` dict + `MediaCloudinaryStorage` as default storage when credentials are present.
- Local dev (DEBUG, no creds) falls back to `FileSystemStorage` under `MEDIA_ROOT`.

## 9. Deployment Architecture

```
Internet
   ↓  https://comcare.cc  (Let's Encrypt TLS, Nginx redirects HTTP→HTTPS)
Nginx
   ↓  proxy_pass http://127.0.0.1:8080
Gunicorn  (systemd: comcare.service)
   ↓
Django  (+ WhiteNoise static, Cloudinary media, Neon PostgreSQL)
```

## 10. Current Risks (pre-audit, now partially fixed)

| Risk | Status |
|------|--------|
| `ALLOWED_HOSTS = ['*']` | Fixed (env-driven) |
| Commented-out DB password in settings.py | Removed |
| `requirements.txt` UTF-16 encoded | Fixed (UTF-8) |
| `verify_payment` IDOR + sandbox auto-verify | Fixed |
| `order_success` unauthenticated PII leak | Fixed |
| Open redirect via `HTTP_REFERER` (wishlist, admin coupon) | Fixed |
| `mysqlclient`/`PyMySQL` unused (MySQL leftovers) | Removed from requirements |
| `_cart_id` returned `None` on fresh sessions | Fixed |
| `Product.final_price` referencing missing `.price` | Fixed |
| Review rating not range-clamped | Fixed |
| No CI/CD | Added (GitHub Actions) |
| No tests | Added (34 tests) |
| No logging config | Added (console → journalctl) |
| No health endpoint | Added `/health/` |
| No .env.example | Added |
| Google OAuth not implemented | Not implemented (documented) |
| GET state-change endpoints (cart/wishlist) | Documented residual risk |
| Guest-phone order linkage unverified | Documented residual risk |
| Order number 5-digit predictable | Documented residual risk |
| Unrestricted file uploads (no type/size validation) | Documented residual risk |

## 11. Missing Production Configuration

- VPS `.env` must add (see `PRODUCTION ACTION REQUIRED`):
  - `ALLOWED_HOSTS=comcare.cc,www.comcare.cc`
  - `CSRF_TRUSTED_ORIGINS=https://comcare.cc,https://www.comcare.cc`
  - `DJANGO_DEBUG=False`
  - Optionally `DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_HSTS_SECONDS`.
- systemd `Restart` policy hardened (see DEPLOYMENT.md).
- Nginx `proxy_set_header X-Forwarded-Proto $scheme;` (needed for secure cookies/HSTS).

## 12. Missing CI/CD (pre-audit)

- No `.github/workflows` at all. Added `ci.yml` and `deploy.yml`.

## 13. Recommended Improvements (deferred, not required to run)

1. Migrate GET-based cart/wishlist mutations to POST (requires frontend changes).
2. Add file type/size validation on all uploads (profile pic, products, service photos).
3. Strengthen order numbers (`secrets`, longer alphabet) + collision retry.
4. Server-side stock decrement + transaction on order placement.
5. Protect coupon `used_count` with row lock / atomic transition.
6. Add Google OAuth properly (django-allauth) when required.
7. Add `SENTRY`/error tracking for production visibility.
8. Rate-limit the public service-lead form.

No changes were made to the UI, business rules, models, or migrations during this audit.