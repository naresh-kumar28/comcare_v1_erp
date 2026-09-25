# ComCare

E-commerce platform for IT equipment sales and repair services, built with Django & Django REST Framework (DRF).

**Live site:** https://comcare.cc

## Stack

- **Django 6.0.7** & **Django REST Framework 3.18.1**
- **SimpleJWT** authentication & **drf-spectacular** OpenAPI/Swagger docs
- **PostgreSQL** (Neon) via `DATABASE_URL` (SQLite fallback in local dev)
- **Gunicorn → Nginx** on a Hostinger VPS (systemd: `comcare.service`)
- **Cloudinary** media storage · **WhiteNoise** static files
- **Razorpay** payments · **Gmail SMTP** email
- **python-decouple** / **django-environ** environment configuration

## Quick start (local dev)

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.example .env          # fill in DJANGO_SECRET_KEY, DJANGO_DEBUG=True
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Tests:

```bash
.venv/bin/python manage.py test
```

Checks:

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py collectstatic --noinput
```

Admin: create a superuser with `python manage.py createsuperuser`.

## How to run Phase 1 backend locally + test the Swagger docs

### 1. Run the Development Server
```bash
# Windows
.\.venv\Scripts\python.exe manage.py runserver

# Linux/macOS
.venv/bin/python manage.py runserver
```
The server will start at `http://127.0.0.1:8000/`.

### 2. Interactive API Documentation (Swagger & ReDoc)
- **Swagger UI**: Visit `http://127.0.0.1:8000/api/schema/swagger-ui/` to test endpoints interactively.
- **ReDoc**: Visit `http://127.0.0.1:8000/api/schema/redoc/`.
- **OpenAPI Schema (JSON)**: `http://127.0.0.1:8000/api/schema/`.

### 3. Phase 1 DRF Endpoints Overview (`/api/v1/`)

#### JWT Authentication (`/api/v1/auth/`)
- `POST /api/v1/auth/register/` - Register new user account.
- `POST /api/v1/auth/login/` - Login & get access/refresh JWT tokens.
- `POST /api/v1/auth/refresh/` - Obtain new access token using refresh token.
- `POST /api/v1/auth/logout/` - Blacklist refresh token.
- `GET | PATCH /api/v1/auth/me/` - Retrieve & update current profile.
- `POST /api/v1/auth/password/change/` - Change account password.
- `POST /api/v1/auth/password/reset/` - Request password reset token.
- `POST /api/v1/auth/password/reset/confirm/` - Confirm password reset.

#### Categories API (`/api/v1/categories/`)
- `GET /api/v1/categories/` - List categories (filter by `is_active`, search by `name`, `description`).
- `GET /api/v1/categories/{slug}/` - Retrieve category details.

#### Products API (`/api/v1/products/`)
- `GET /api/v1/products/` - List active products (supports `category`, `brand`, `min_price`, `max_price`, `in_stock` filters; `search` by title/brand/cpu/sku; `ordering`).
- `GET /api/v1/products/{slug}/` - Retrieve detailed product info with gallery images.
- `GET /api/v1/products/featured/` - Featured products collection.
- `GET /api/v1/products/new-arrivals/` - New arrivals collection.
- `GET /api/v1/products/best-sellers/` - Best sellers collection.

### 4. Running Phase 1 Test Suite
```bash
# Windows
.\.venv\Scripts\python.exe manage.py test apps.accounts.tests apps.categories.tests apps.store.tests common.tests --keepdb

# Linux/macOS
.venv/bin/python manage.py test apps.accounts.tests apps.categories.tests apps.store.tests common.tests --keepdb
```

## Phase 3: React Frontend Integration

The modern React Single Page Application (SPA) resides in the `frontend/` directory and connects to the DRF API foundation.

### Frontend Tech Stack
- **React 18** + **Vite 8**
- **Tailwind CSS** + **Lucide Icons**
- **Axios** (Centralized client with automatic JWT token refresh & `X-Guest-Cart-Key` tracking)
- **React Router v6** (Protected & Public Route Guards)
- **Razorpay Checkout SDK** (Client modal integration with backend signature verification)
- **React Hot Toast** (Toast notifications)

### 1. Environment Configuration (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_RAZORPAY_KEY_ID=rzp_test_YourKeyHere
```

### 2. Development Setup & Commands
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite development server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview
```

## Project layout

```
frontend/        React SPA (components, pages, context, API layer, routes, Vite config)
config/          Django settings split (base, development, production), URLs, WSGI/ASGI
common/          Shared permissions, pagination, and standardized exception handling
apps/            accounts, cart, categories, coupons, orders, payments, store, etc.
templates/       Shared Django HTML/HTMX templates (retained for parallel operation)
docs/            audit, security, deployment, environment, CI/CD
```

## Database Migration Config (PostgreSQL Ready)

Production & staging environments connect to PostgreSQL via `DATABASE_URL` (e.g. `postgres://user:pass@ep-host.region.aws.neon.tech/dbname?sslmode=require`).
In local development, if `DATABASE_URL` is omitted and `DJANGO_DEBUG=True`, it falls back cleanly to `db.sqlite3`.