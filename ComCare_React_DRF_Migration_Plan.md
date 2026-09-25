# ComCare — Django+HTMX se React + DRF me Migration Plan

> **Current Stack:** Django (server-rendered templates + HTMX partials), SQLite, Session-based cart, Razorpay, WhiteNoise
> **Target Stack:** React (SPA, Vite) frontend + Django REST Framework (DRF) backend (JWT auth), Postgres, separate panels (Public / Customer / Admin), Dockerized, CI/CD ready

---

## 1. Current Project Analysis (jo maine zip me dekha)

| Django App | Responsibility | Key Models |
|---|---|---|
| `apps/accounts` | Auth (email-based CustomUser), profile | `CustomUser` |
| `apps/categories` | Product categories | `Category` |
| `apps/store` | Catalog | `Product`, `ProductGalleryImage`, `Wishlist`, `RecentlyViewedProduct`, `FailedSearchLog` |
| `apps/cart` | Cart, checkout, orders, address, shipping, Razorpay | `Cart`, `CartItem`, `UserAddress`, `Order`, `OrderItem`, `ShippingConfig` |
| `apps/coupons` | Discount coupons | `Coupon` |
| `apps/services` | Repair/service booking leads | `Service`, `ServiceRequest` |
| `apps/reviews` | Product ratings/reviews | `Review` |
| `apps/admin` (custom, HTMX-driven) | Internal ERP/admin panel | dashboard, orders, products, categories, inventory, customers, returns, coupons, services, reports |
| `apps/core` | Static/info pages, health check, search | — |

**Observation:** Business logic aur models already solid hain. Sirf presentation layer (Django templates + HTMX) ko React SPA se replace karna hai, aur admin panel ke HTMX endpoints ko proper DRF REST APIs me convert karna hai. Models/DB schema largely reusable rahega (thoda refactor + serializers add karenge).

---

## 2. Target Architecture (High Level)

```
┌─────────────────────┐        REST/JSON (JWT)        ┌──────────────────────────┐
│   React SPA (Vite)   │  <───────────────────────────>│   Django + DRF Backend    │
│  - Public Storefront │                                │  - apps/* (DRF-ified)    │
│  - Customer Panel    │                                │  - PostgreSQL             │
│  - Admin Panel       │                                │  - Redis (cache/celery)   │
│  Served via Nginx    │                                │  - Gunicorn/Uvicorn       │
└─────────────────────┘                                └──────────────────────────┘
```

- **1 Django backend**, split into **3 logical route groups**: Public API, Account (customer) API, Admin API — permission-based, not separate apps.
- **1 React codebase**, split into **3 route groups** with separate layouts: `/*` (public), `/account/*` (customer), `/admin/*` (staff) — code-split via `React.lazy`.
- Auth: `djangorestframework-simplejwt` (access + refresh token), role check via `is_staff`.

---

## 3. Backend — Proposed Folder Structure (Django + DRF)

```
comcare_backend/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   ├── urls.py                # includes /api/v1/... only
│   ├── asgi.py / wsgi.py
├── apps/
│   ├── accounts/
│   │   ├── models.py          # CustomUser (reused)
│   │   ├── serializers.py     # RegisterSerializer, LoginSerializer, ProfileSerializer
│   │   ├── views.py           # RegisterAPIView, ProfileViewSet, PasswordChange/Reset
│   │   ├── urls.py
│   │   ├── permissions.py
│   ├── categories/
│   │   ├── models.py / serializers.py / views.py (CategoryViewSet) / urls.py
│   ├── store/
│   │   ├── models.py          # Product, GalleryImage, Wishlist, RecentlyViewed (reused)
│   │   ├── serializers.py     # ProductListSerializer, ProductDetailSerializer
│   │   ├── views.py           # ProductViewSet (filters, search, ordering), WishlistViewSet
│   │   ├── filters.py         # django-filter FilterSet (brand, price range, category, in-stock)
│   │   ├── urls.py
│   ├── cart/
│   │   ├── models.py          # Cart, CartItem, UserAddress, Order, OrderItem, ShippingConfig
│   │   ├── serializers.py
│   │   ├── views.py           # CartViewSet, AddressViewSet, OrderViewSet, CheckoutAPIView
│   │   ├── services.py        # cart totals, order-number gen, invoice token logic (business logic layer)
│   │   ├── urls.py
│   ├── payments/              # NEW — split out of cart for clarity
│   │   ├── razorpay_client.py
│   │   ├── views.py           # CreateRazorpayOrder, VerifyPayment (webhook + signature verify)
│   │   ├── urls.py
│   ├── coupons/
│   │   ├── models.py / serializers.py / views.py (ApplyCoupon, RemoveCoupon) / urls.py
│   ├── services/
│   │   ├── models.py          # Service, ServiceRequest
│   │   ├── serializers.py / views.py (ServiceViewSet, ServiceRequestCreateAPIView) / urls.py
│   ├── reviews/
│   │   ├── models.py / serializers.py / views.py (ReviewViewSet) / urls.py
│   ├── dashboard_admin/       # replaces old HTMX-only apps/admin
│   │   ├── views.py           # AdminDashboardStats, AdminReportsAPIView
│   │   ├── serializers.py
│   │   ├── urls.py
│   ├── core/
│   │   ├── views.py           # health check, contact form, search, site-settings
│   │   ├── urls.py
├── common/                    # NEW shared package
│   ├── permissions.py         # IsAdminOrReadOnly, IsOwnerOrAdmin, IsStaffUser
│   ├── pagination.py          # StandardResultsPagination
│   ├── exceptions.py          # custom DRF exception handler → consistent JSON error shape
│   ├── mixins.py
│   ├── throttles.py
├── media/  (or S3/Cloudinary bucket in prod)
├── static/
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   ├── prod.txt
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── .env.example
```

**Backend libraries to add:**
`djangorestframework`, `djangorestframework-simplejwt`, `django-cors-headers`, `django-filter`, `drf-spectacular` (Swagger/OpenAPI docs), `django-storages` + `boto3` (S3 media in prod), `celery` + `redis` (async emails/reports — optional but recommended), `sentry-sdk` (error monitoring), `gunicorn`.

---

## 4. Frontend — Proposed Folder Structure (React + Vite)

```
comcare-frontend/
├── public/
├── src/
│   ├── main.jsx
│   ├── App.jsx                       # root providers wrap
│   ├── api/
│   │   ├── axiosClient.js            # base axios + interceptors (JWT refresh)
│   │   ├── endpoints/
│   │   │   ├── authApi.js
│   │   │   ├── productApi.js
│   │   │   ├── cartApi.js
│   │   │   ├── orderApi.js
│   │   │   ├── couponApi.js
│   │   │   ├── serviceApi.js
│   │   │   ├── reviewApi.js
│   │   │   ├── adminApi.js
│   ├── app/
│   │   ├── store.js                  # Redux Toolkit store (or Zustand)
│   │   ├── queryClient.js            # TanStack React Query client
│   ├── features/                     # RTK slices / domain state
│   │   ├── auth/authSlice.js
│   │   ├── cart/cartSlice.js
│   │   ├── wishlist/wishlistSlice.js
│   │   ├── ui/uiSlice.js             # toasts, modals, loaders
│   ├── routes/
│   │   ├── index.jsx                 # createBrowserRouter — combines 3 groups
│   │   ├── PublicRoutes.jsx
│   │   ├── AccountRoutes.jsx
│   │   ├── AdminRoutes.jsx
│   │   ├── ProtectedRoute.jsx        # auth-required guard
│   │   ├── AdminRoute.jsx            # is_staff guard
│   ├── layouts/
│   │   ├── PublicLayout.jsx          # header, footer, cart drawer
│   │   ├── AccountLayout.jsx         # account sidebar nav (mobile subnav too)
│   │   ├── AdminLayout.jsx           # admin sidebar + topbar
│   ├── pages/
│   │   ├── public/
│   │   │   ├── Home.jsx
│   │   │   ├── Shop.jsx
│   │   │   ├── ProductDetail.jsx
│   │   │   ├── Categories.jsx
│   │   │   ├── SearchResults.jsx
│   │   │   ├── Services.jsx
│   │   │   ├── About.jsx / Contact.jsx
│   │   │   ├── PrivacyPolicy.jsx / Terms.jsx / RefundPolicy.jsx
│   │   │   ├── Login.jsx / Register.jsx
│   │   │   ├── ForgotPassword.jsx / ResetPassword.jsx
│   │   │   ├── Cart.jsx / Checkout.jsx / OrderSuccess.jsx
│   │   │   ├── NotFound.jsx / ServerError.jsx
│   │   ├── account/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Orders.jsx / OrderDetail.jsx / Invoice.jsx
│   │   │   ├── Wishlist.jsx
│   │   │   ├── Addresses.jsx
│   │   │   ├── Profile.jsx
│   │   │   ├── ChangePassword.jsx
│   │   ├── admin/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── orders/OrderList.jsx, OrderDetail.jsx
│   │   │   ├── products/ProductList.jsx, ProductForm.jsx
│   │   │   ├── categories/CategoryList.jsx, CategoryForm.jsx
│   │   │   ├── inventory/InventoryList.jsx
│   │   │   ├── customers/CustomerList.jsx, CustomerDetail.jsx
│   │   │   ├── returns/ReturnsList.jsx
│   │   │   ├── coupons/CouponList.jsx, CouponForm.jsx
│   │   │   ├── services/ServiceLeadsList.jsx
│   │   │   ├── reports/Reports.jsx
│   ├── components/
│   │   ├── common/ (Button, Modal, DataTable, Pagination, Loader, Toast, ConfirmDialog)
│   │   ├── product/ (ProductCard, ProductGrid, ProductGallery, RatingStars)
│   │   ├── cart/ (CartLineItem, CartSummary, CouponBox)
│   │   ├── reviews/ (ReviewForm, ReviewList)
│   │   ├── admin/ (Sidebar, StatCard, StatusBadge, ImageUploader)
│   ├── hooks/                        # useAuth, useCart, useDebounce, usePagination
│   ├── utils/                        # formatCurrency, formatDate, validators
│   ├── constants/                    # order statuses, roles, routes map
│   ├── assets/
│   ├── styles/                       # tailwind.css, globals.css
├── .env.example
├── package.json
├── vite.config.js
├── tailwind.config.js
├── Dockerfile
├── nginx.conf
```

**Frontend libraries:** `react-router-dom v6`, `@reduxjs/toolkit` + `react-redux` (ya lightweight `zustand`), `@tanstack/react-query` (server-state caching), `axios`, `react-hook-form` + `zod`/`yup` (form validation), `tailwindcss`, `lucide-react` (icons — templates already use Lucide names), `react-hot-toast`, `recharts` (admin reports charts), `react-razorpay` or direct Razorpay checkout.js.

---

## 5. Route Mapping (Old HTMX Pages → New React Routes)

### Public (no auth)
| Old Django URL | New React Route |
|---|---|
| `/` | `/` |
| `/store/` | `/shop` |
| `/store/product/<slug>/` | `/shop/:slug` |
| `/categories/` | `/categories` |
| `/search/` | `/search?q=` |
| `/services/` | `/services` |
| `/about/`, `/contact/` | `/about`, `/contact` |
| `/privacy-policy/`, `/terms/`, `/refund-policy/` | same |
| `/cart/` | `/cart` |
| `/cart/checkout/` | `/checkout` |
| `/cart/order-success/` | `/order-success/:orderNumber` |
| `/account/login/`, `/register/` | `/login`, `/register` |
| `/account/forgot-password/`, `/reset/<uid>/<token>/` | `/forgot-password`, `/reset-password/:uid/:token` |

### Customer Account panel (JWT auth required)
| Old | New |
|---|---|
| `/account/dashboard/` | `/account` |
| `/account/orders/` | `/account/orders` |
| `/account/orders/<id>/invoice/` | `/account/orders/:id/invoice` |
| `/account/wishlist/` | `/account/wishlist` |
| `/account/addresses/` | `/account/addresses` |
| `/account/profile/` | `/account/profile` |
| `/account/change-password/` | `/account/change-password` |

### Admin panel (JWT + `is_staff` required)
| Old | New |
|---|---|
| `/admin-panel/` | `/admin` |
| `/admin-panel/orders/` | `/admin/orders`, `/admin/orders/:id` |
| `/admin-panel/products/` | `/admin/products`, `/admin/products/new`, `/admin/products/:id/edit` |
| `/admin-panel/categories/` | `/admin/categories` |
| `/admin-panel/inventory/` | `/admin/inventory` |
| `/admin-panel/customers/` | `/admin/customers`, `/admin/customers/:id` |
| `/admin-panel/returns/` | `/admin/returns` |
| `/admin-panel/coupons/` | `/admin/coupons` |
| `/admin-panel/services/` | `/admin/services` |
| `/admin-panel/reports/` | `/admin/reports` |

> Note: Purane HTMX partial-swap endpoints (`admin_product_row.html`, `table_body.html`, etc.) ab zaroorat nahi — React state + `PATCH/DELETE` API calls se table row update/delete hoga, page reload/swap ke bina.

---

## 6. REST API Design (`/api/v1/...`)

```
# Auth
POST   /api/v1/auth/register/
POST   /api/v1/auth/login/                 → access + refresh JWT
POST   /api/v1/auth/refresh/
POST   /api/v1/auth/logout/                → blacklist refresh token
POST   /api/v1/auth/password/change/
POST   /api/v1/auth/password/reset/
POST   /api/v1/auth/password/reset/confirm/
GET    /api/v1/auth/me/                    → profile
PATCH  /api/v1/auth/me/

# Catalog
GET    /api/v1/categories/
GET    /api/v1/products/?category=&brand=&min_price=&max_price=&search=&ordering=
GET    /api/v1/products/{slug}/
GET    /api/v1/products/featured/  /new-arrivals/  /best-sellers/
GET    /api/v1/products/{slug}/reviews/
POST   /api/v1/products/{slug}/reviews/
PATCH|DELETE /api/v1/reviews/{id}/
GET    /api/v1/recently-viewed/

# Wishlist
GET    /api/v1/wishlist/
POST   /api/v1/wishlist/toggle/{product_id}/
DELETE /api/v1/wishlist/{product_id}/

# Cart & Checkout
GET    /api/v1/cart/
POST   /api/v1/cart/items/                 → add item
PATCH  /api/v1/cart/items/{id}/            → update qty
DELETE /api/v1/cart/items/{id}/
POST   /api/v1/coupons/apply/
POST   /api/v1/coupons/remove/
GET    /api/v1/shipping-config/
GET|POST /api/v1/addresses/
PATCH|DELETE /api/v1/addresses/{id}/
POST   /api/v1/addresses/{id}/set-default/
POST   /api/v1/orders/                     → place order (COD)
GET    /api/v1/orders/                     → my orders
GET    /api/v1/orders/{order_number}/
POST   /api/v1/orders/{id}/cancel/
GET    /api/v1/orders/{order_number}/invoice/?token=

# Payments (Razorpay)
POST   /api/v1/payments/razorpay/create-order/
POST   /api/v1/payments/razorpay/verify/

# Services
GET    /api/v1/services/
POST   /api/v1/service-requests/           → booking lead

# Admin (permission: IsAdminUser)
GET    /api/v1/admin/dashboard/stats/
GET    /api/v1/admin/orders/  + PATCH /status/
GET|POST /api/v1/admin/products/  + PATCH|DELETE /{id}/
GET|POST /api/v1/admin/categories/ + PATCH|DELETE /{id}/
GET    /api/v1/admin/inventory/  + PATCH /{id}/stock/
GET    /api/v1/admin/customers/  + GET /{id}/
GET    /api/v1/admin/returns/
GET|POST /api/v1/admin/coupons/ + PATCH|DELETE /{id}/  + PATCH /{id}/toggle/
GET    /api/v1/admin/service-requests/ + PATCH /{id}/status/ + DELETE
GET    /api/v1/admin/reports/
```

All list endpoints: DRF pagination + `django-filter` + search + ordering. Error responses standardized: `{ "success": false, "message": "...", "errors": {...} }`.

---

## 7. Auth & Permission Strategy

- **JWT** via `simplejwt`: access token (short-lived, ~15 min) in memory/Redux, refresh token (7 days) in **httpOnly cookie** (XSS-safe) — axios interceptor auto-refreshes on 401.
- Roles: `is_staff=True` → Admin panel access; regular authenticated user → Account panel; anonymous → Public + guest cart (`session_key` header or localStorage cart-id, merged into user cart on login — same logic as current `GuestSessionMiddleware`, adapted to API).
- React guards: `<ProtectedRoute>` (any logged-in user) and `<AdminRoute>` (`user.is_staff`) wrapping route groups.

---

## 8. Migration Phases (Suggested Timeline)

| Phase | Scope | Est. Duration |
|---|---|---|
| **1. Backend foundation** | DRF setup, JWT auth, CORS, serializers for accounts/categories/store, Postgres migration | 3–4 days |
| **2. Core commerce APIs** | Cart, addresses, coupons, orders, Razorpay integration, shipping config | 4–5 days |
| **3. Services + Reviews APIs** | Service booking, reviews CRUD | 2 days |
| **4. Admin APIs** | Dashboard stats, product/category/inventory/customer/coupon/service management endpoints, reports | 4–5 days |
| **5. Frontend scaffold** | Vite+React setup, routing skeleton, layouts, axios/JWT wiring, Tailwind theme (match existing UI) | 2–3 days |
| **6. Public storefront pages** | Home, Shop, Product detail, Categories, Search, Services, Static pages | 4–5 days |
| **7. Cart/Checkout/Auth pages** | Cart, checkout, Razorpay UI, login/register/password flows | 4 days |
| **8. Customer account panel** | Dashboard, orders, invoice, wishlist, addresses, profile | 3 days |
| **9. Admin panel UI** | Dashboard, orders, products (CRUD+image upload), categories, inventory, customers, coupons, service leads, reports/charts | 6–7 days |
| **10. QA, SEO, perf, polish** | Meta tags/SSR consideration, responsive QA, loading/error states, accessibility | 3–4 days |
| **11. Production hardening & deploy** | Docker, CI/CD, env separation, monitoring | 2–3 days |

*(Total ≈ 6–7 weeks for one full-stack dev; parallelizable with 2 devs to ~3–4 weeks.)*

---

## 9. Production-Readiness Checklist

**Backend**
- [ ] Postgres (not SQLite) with connection pooling
- [ ] `django-environ` / `.env` based settings split (`base/dev/prod`)
- [ ] `DEBUG=False`, `ALLOWED_HOSTS`, `SECURE_*` headers, HTTPS redirect, HSTS
- [ ] `django-cors-headers` — whitelist only frontend domain
- [ ] Media files → S3/Cloudinary (not local disk) in prod
- [ ] Static files → WhiteNoise or CDN
- [ ] Gunicorn + Nginx reverse proxy (or Uvicorn if async views needed)
- [ ] Celery + Redis for emails (order confirmation, password reset) — async, non-blocking
- [ ] Rate limiting on auth & checkout endpoints (DRF throttling)
- [ ] Sentry for error tracking
- [ ] `drf-spectacular` → auto-generated API docs (`/api/schema/swagger-ui/`)
- [ ] DB backups + migrations run via CI/CD before deploy
- [ ] Reuse existing `.github/workflows/ci.yml` & `deploy.yml` — extend for DRF tests + frontend build

**Frontend**
- [ ] Environment-based API base URL (`VITE_API_BASE_URL`)
- [ ] Code-splitting per route group (public/account/admin bundles lazy-loaded)
- [ ] Image lazy-loading + responsive `srcset`
- [ ] Global error boundary + 404/500 pages
- [ ] SEO: `react-helmet-async` for meta tags per page (product pages especially)
- [ ] Lighthouse pass (perf/accessibility/SEO ≥ 90)
- [ ] Build via Vite → static bundle served by Nginx (Dockerized), or Vercel/Netlify
- [ ] Sentry/LogRocket for frontend error monitoring

**DevOps**
- [ ] `docker-compose.yml`: `backend`, `frontend` (nginx), `db` (postgres), `redis`
- [ ] Separate `docker-compose.prod.yml`
- [ ] CI: lint + test (pytest for DRF, vitest/jest for React) on PR
- [ ] CD: build → push image → deploy (Render/Railway/AWS/DigitalOcean)

---

## 10. Key Risks / Things to Decide Upfront

1. **Guest cart & guest checkout** — currently session-based; in SPA world, decide: require login before checkout, OR issue an anonymous device/cart token stored in localStorage and merge on login.
2. **Image uploads (product gallery, profile pic, service request photo)** — move to `multipart/form-data` API uploads with client-side preview; consider direct-to-S3 presigned URLs for large scale.
3. **Invoice PDF** (`templates/invoice.html`) — either generate PDF server-side (`weasyprint`/`xhtml2pdf`) and serve via a signed download API, or render an equivalent printable React page.
4. **Razorpay webhook** — must remain a **server-to-server** endpoint (not called from React) for reliable payment confirmation, independent of client-side `verify-payment` call.
5. **SEO** — pure SPA hurts SEO for product pages; consider Next.js (SSR/SSG) later if organic search traffic matters a lot (not required for this task's scope, but worth flagging).

---

## 11. Deliverables Summary

- ✅ New `comcare_backend/` (DRF) — reuses existing models, adds serializers/viewsets/permissions
- ✅ New `comcare-frontend/` (React + Vite) — 3 route groups: Public, `/account`, `/admin`
- ✅ Dockerized both, docker-compose for local + prod
- ✅ CI/CD pipeline extended (tests + build + deploy)
- ✅ Swagger API docs
- ✅ Feature parity with current HTMX app + cleaner, faster, app-like UX

---

**Next step:** Is plan par confirm karne ke baad main phase-wise implementation start kar sakta hoon — pehle DRF backend (accounts + store + cart APIs) se shuru karna best rahega, taaki frontend turant real APIs ke against build ho sake.
