# CLAUDE.md — iHhashi Codebase Guide

This file provides context for AI assistants (Claude, Copilot, etc.) working in this repository.

---

## Project Overview

**iHhashi** is a South African delivery platform (food, groceries, fresh produce, courier) inspired by Ele.me and built for Mzansi. It supports all 9 provinces, ZAR currency, and multiple local languages.

**Production URL:** https://ihhashi.co.za
**Current version:** 0.4.2

---

## Architecture

```
ihhashi/
├── backend/          # FastAPI + MongoDB + Redis API
├── frontend/         # React + Vite + TypeScript + Capacitor (Android PWA)
├── deployment/       # Render, Docker Compose (prod), Nginx, Vercel configs
├── docs/             # Play Store listing, Terms of Service, screenshots
└── docker-compose.yml  # Local development compose
```

### Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11, FastAPI, Motor (async MongoDB), Redis |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Mobile | Capacitor 8 (Android), PWA |
| Database | MongoDB 7.0 |
| Cache / Rate Limiting | Redis 7 |
| Auth | Supabase (Phone OTP) + JWT (HS256) |
| Payments | Paystack (primary), Yoco |
| Maps | Google Maps API |
| AI Chatbot | Groq LLM — the "Nduna" assistant |
| Analytics | PostHog |
| Error Tracking | GlitchTip (Sentry-compatible) |
| State Management | Zustand, TanStack React Query |

---

## Backend (`backend/`)

### Entry Point

`backend/app/main.py` — FastAPI app with lifespan hooks that connect MongoDB and Redis on startup.

### Directory Layout

```
backend/app/
├── main.py              # App factory, middleware, route mounting
├── config.py            # Pydantic Settings (env vars, validators)
├── db.py                # Motor database helper
├── supabase_client.py   # Supabase client initialisation
├── core/
│   ├── config.py        # Secondary config helpers
│   └── redis_client.py  # Redis connection management
├── database/
│   ├── __init__.py      # connect_db / close_db / ensure_indexes
│   └── indexes.py       # MongoDB index definitions
├── middleware/
│   ├── rate_limit.py    # slowapi rate limiting setup
│   └── security.py      # Security headers middleware
├── models/              # MongoDB document models (Motor/PyMongo dicts)
│   ├── user.py, buyer.py, driver.py, order.py, product.py
│   ├── delivery.py, trip.py, account.py, verification.py
│   ├── refund.py, referral.py, customer_rewards.py
├── routes/              # FastAPI routers — one file per domain
│   ├── auth.py          # /api/v1/auth/*
│   ├── orders.py        # /api/v1/orders/*
│   ├── merchants.py     # /api/v1/merchants/*
│   ├── riders.py        # /api/v1/riders/*
│   ├── vendors.py       # /api/v1/vendors/*
│   ├── delivery_servicemen.py  # /api/v1/delivery-servicemen/*
│   ├── trips.py         # /api/v1/trips/*
│   ├── payments.py      # /api/v1/payments/*
│   ├── refunds.py       # (mounted separately)
│   ├── referrals.py     # /api/v1/referrals/*
│   ├── customer_rewards.py
│   ├── tracking.py
│   ├── users.py
│   ├── websocket.py     # /ws/* — real-time delivery tracking
│   └── nduna.py         # /api/nduna/* — Groq-powered AI chatbot
├── services/            # Business logic
│   ├── auth.py          # JWT helpers, password hashing
│   ├── matching.py      # Rider–order matching algorithm
│   ├── delivery_fee.py  # Fee calculation (base R20 + R5/km, SA market rates)
│   ├── paystack.py      # Paystack API wrapper
│   ├── payout_scheduler.py  # Weekly payout background worker
│   ├── file_upload.py
│   └── telegram_bot.py
├── utils/
│   └── validation.py    # Input validation helpers
└── i18n/                # Internationalisation stubs
```

### API Routes

All standard routes are under `/api/v1`. Exceptions:

- WebSocket: `/ws/*`
- Nduna chatbot: `/api/nduna/*`
- Health check: `/health`
- Root info: `/`

### Configuration (`backend/app/config.py`)

Settings are loaded via `pydantic-settings` from environment variables (or `.env`).
Import the singleton: `from app.config import settings`

Key validators enforce:
- `SECRET_KEY` must be ≥32 chars and non-default in `production`
- `DEBUG=True` is rejected in `production`
- Paystack test keys warn in production
- CORS localhost origins warn in production

### SA-Specific Business Rules

- Currency: ZAR (R)
- VAT: 15%
- Delivery fee: R20 base + R5/km, R7/km after 15 km
- Free trial: 45 days at 0% platform fee; standard fee 15%
- Tips: 0% platform fee
- Payouts: Every Sunday at 11:11 AM SAST (09:11 UTC), minimum R100
- Supported languages: en, zu, xh, af, st, tn, so, nso, ts, ve, nr

---

## Frontend (`frontend/`)

### Tech Stack Details

- **Vite 5** + **TypeScript 5** + **React 18**
- **Tailwind CSS 3** — brand colours black & yellow (`#FF6B35` accent)
- **React Router 6** — SPA routing
- **TanStack React Query 5** — server state, `staleTime: 30s`, `retry: 2`
- **Zustand 5** — client state (cart)
- **Axios** — HTTP client with interceptors for auth + offline handling
- **Capacitor 8** — Android native wrapper

### Directory Layout

```
frontend/src/
├── App.tsx              # Root: AuthContext, QueryClient, Router
├── main.tsx             # Vite entry point
├── lib/
│   ├── api.ts           # Axios instance + all API call helpers
│   ├── supabase.ts      # Supabase client
│   └── posthog.ts       # PostHog analytics init
├── pages/
│   ├── Home.tsx         # Landing / merchant discovery
│   ├── auth/Auth.tsx    # Login / Register
│   ├── catalog/Products.tsx  # Product browsing with function-calling support
│   ├── CartPage.tsx
│   ├── orders/Orders.tsx
│   └── profile/Profile.tsx  # (protected route)
├── components/
│   ├── Header.tsx
│   ├── CategoryBar.tsx
│   ├── MerchantCard.tsx
│   ├── SplashScreen.tsx     # 1.8s brand splash on first load
│   ├── PaymentSelector.tsx
│   ├── LanguageSelector.tsx / LanguageToggle.tsx
│   └── common/ErrorBoundary.tsx
├── hooks/
│   ├── useCart.ts           # Cart state via Zustand
│   ├── useSupabase.ts       # Supabase auth helpers
│   ├── useDataSaver.ts      # Data-saver mode for SA low-bandwidth users
│   ├── useLoadShedding.ts   # Loadshedding UX (SA-specific offline degradation)
│   └── usePostHog.ts
└── styles/globals.css
```

### Authentication Flow

1. Supabase Phone OTP → JWT issued by backend
2. Token stored in `localStorage` as `access_token`
3. `AuthContext` (in `App.tsx`) is the single source of truth — exposes `user`, `isAuthenticated`, `login()`, `logout()`
4. Axios interceptor attaches `Authorization: Bearer <token>` to every request
5. 401 responses clear tokens and redirect to `/auth?session_expired=1`

### API Client (`frontend/src/lib/api.ts`)

Base URL: `VITE_API_URL` env var (defaults to `http://localhost:8000`), auto-appends `/api/v1`.

Named export groups:

| Export | Purpose |
|--------|---------|
| `authAPI` | login, register, logout, me, password reset |
| `ordersAPI` | CRUD + cancel + rate |
| `merchantsAPI` | list, get, products, nearby |
| `productsAPI` | get, search, categories |
| `tripsAPI` | active, history, location, accept, complete |
| `paymentsAPI` | initialize, verify, banks, methods |
| `usersAPI` | profile, update, location, language, delete |
| `addressesAPI` | CRUD + setDefault |
| `vendorAPI` | dashboard, orders, products, analytics |
| `riderAPI` | profile, status, earnings, available orders |

---

## Development Workflow

### Running Locally (Docker — Recommended)

```bash
# Start MongoDB + Redis + Backend + Frontend
docker-compose up -d

# Watch logs
docker-compose logs -f

# Stop
docker-compose down
```

Services after startup:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

### Running Without Docker

```bash
# Backend
cd backend
cp .env.example .env   # edit with real values
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
cp .env.example .env   # edit with real values
npm install
npm run dev
```

### Environment Files

| File | Purpose |
|------|---------|
| `.env.example` | Root-level minimal template (MongoDB + Redis defaults) |
| `backend/.env.example` | Full backend config reference |
| `frontend/.env.example` | Frontend Vite vars reference |

Never commit `.env` files. Always use the `.env.example` as the template.

---

## Testing

### Backend

```bash
cd backend

# Run all tests
pytest

# With coverage report
pytest --cov=app --cov-report=html

# Single file
pytest tests/test_auth.py -v

# Type check
mypy app
```

Test files live in `backend/tests/`: `test_auth.py`, `test_orders.py`, `test_payments.py`, `test_matching.py`, `test_concurrent_matching.py`, `test_webhook_replay.py`.

### Frontend

```bash
cd frontend

# Run unit tests (Vitest)
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage

# End-to-end (Playwright)
npm run test:e2e

# Type check
npm run typecheck

# Lint
npm run lint
npm run lint:fix
```

### Pre-commit

Husky + lint-staged runs ESLint + Prettier automatically on staged `*.ts`, `*.tsx`, `*.json`, `*.md` files before each commit.

---

## Building & Mobile

### Frontend Production Build

```bash
cd frontend
npm run build        # tsc + vite build → dist/
npm run preview      # Serve the built output locally
```

### Android (Capacitor)

```bash
cd frontend
npm run android:build    # build + cap sync android
npm run android:open     # open in Android Studio
npm run android:debug    # assembleDebug via Gradle
npm run android:release  # assembleRelease via Gradle
```

APK output: `frontend/android/app/build/outputs/apk/`

---

## Database

- **Engine:** MongoDB 7.0 (Motor async driver)
- **Database name:** `ihhashi` (configurable via `DB_NAME`)

### Collections

| Collection | Description |
|-----------|-------------|
| `users` | All users (buyers, merchants, riders) |
| `orders` | Delivery orders |
| `merchants` | Merchant/vendor profiles |
| `products` | Product catalog |
| `trips` | Rider delivery trips |
| `payments` | Payment records |
| `refunds` | Refund requests |
| `referrals` | Referral tracking |
| `customer_rewards` | Hashi Coins loyalty points |
| `verifications` | Blue Horse verification records |

### Migrations

```bash
cd backend

# Check migration status
python -m scripts.migrations.migrate --status

# Apply pending
python -m scripts.migrations.migrate --up

# Rollback last
python -m scripts.migrations.migrate --down

# Create new migration
python -m scripts.migrations.migrate --create "add_new_field"
```

### Indexes

Defined in `backend/app/database/indexes.py` and created at startup via `ensure_indexes()`. Key indexes include compound indexes on `(buyer_id, status)`, `(store_id, status)`, geospatial on user location, and unique index on `users.email`.

---

## Deployment

### Render (Primary — `deployment/render.yaml`)

Services deployed:
- `ihhashi-api` — FastAPI web service (2 instances)
- `ihhashi-worker` — Payout scheduler background worker
- `ihhashi-redis` — Redis private service
- `ihhashi-mongodb` — Managed MongoDB 7.0
- `weekly-payouts` — Cron job (Sunday 09:11 UTC)
- `daily-cleanup` — Cron job (03:00 UTC daily)

### Vercel (Frontend — `deployment/vercel.json`)

The React SPA is deployed to Vercel and configured to rewrite all routes to `index.html`.

### Docker Production (`deployment/docker-compose.prod.yml`)

Includes Nginx reverse proxy and Certbot for Let's Encrypt SSL.

---

## Key Conventions

### Backend (Python)

- Pydantic v2 for all schemas; settings loaded via `pydantic-settings`
- Async everywhere — use `async def` for all route handlers and DB calls
- MongoDB access via `Motor` (never blocking PyMongo in async context)
- Import the settings singleton: `from app.config import settings`
- Never hardcode secrets; always read from `settings.*`
- Rate limiting applied globally via `slowapi`; auth endpoints limited to 5/minute
- Error responses use FastAPI's `HTTPException` with meaningful `detail` strings
- GlitchTip (Sentry SDK) is initialized at startup if `GLITCHTIP_DSN` is set

### Frontend (TypeScript / React)

- All API calls go through `frontend/src/lib/api.ts` — never use raw `fetch` or a new Axios instance
- `AuthContext` (`App.tsx`) is the single auth state source — consume with `useAuth()`
- Server state: TanStack React Query; client state: Zustand
- Tailwind for styling; avoid inline styles except for dynamic values
- Brand accent colour: `#FF6B35` (orange); primary theme: black & yellow
- Feature flags: `VITE_ENABLE_CHATBOT`, `VITE_ENABLE_NOTIFICATIONS`, `VITE_ENABLE_ANALYTICS`
- Respect `useDataSaver` hook when fetching heavy assets (images, etc.) — SA users are often on limited data
- The `useLoadShedding` hook should degrade the UX gracefully when network is flaky

### Naming Conventions

- Backend: `snake_case` for Python identifiers, MongoDB field names, and API query params
- Frontend: `camelCase` for JS/TS variables and functions; `PascalCase` for React components
- API route kebab-case: `/delivery-servicemen`, `/customer-rewards`
- Git branches: `feature/<name>`, `fix/<name>`, `chore/<name>`

### Security Rules (Do Not Violate)

- Never disable `DEBUG=False` enforcement in production config
- Never bypass CORS validators or widen CORS to `*` in production
- Never log or return raw `SECRET_KEY`, payment secrets, or private keys
- All payment webhook handlers must verify Paystack/Yoco signatures before processing
- File uploads: max 5 MB, allowed types: JPEG, PNG, WebP only
- Input validation: always go through Pydantic schemas, never raw dicts from request body
- Auth tokens: HS256 JWT, 30-minute access + 7-day refresh

---

## Nduna AI Chatbot

`/api/nduna/*` — Groq LLM-powered multilingual assistant.

- Supports SA languages: en, zu, xh, af, st, tn, so
- Integrates product browsing with function calling
- Supports voice input (audio upload endpoint)
- API keys rotated from `GROQ_API_KEY_1`, `GROQ_API_KEY_2`, … env vars

---

## Monitoring & Observability

| Tool | Purpose | Config |
|------|---------|--------|
| GlitchTip | Error tracking (Sentry-compatible) | `GLITCHTIP_DSN` |
| PostHog | Analytics + feature flags | `POSTHOG_API_KEY` |
| `/health` endpoint | MongoDB + Redis liveness | No auth required |
| Render dashboard | Service logs & metrics | Render account |

---

## CI/CD Pipeline (`.github/workflows/ci.yml`)

Runs on every push and pull request:

1. **Backend Tests** — Python 3.11, ruff lint, pytest with coverage, Codecov upload
2. **Frontend Tests** — Node 20, ESLint, TypeScript check, Vitest, Vite build
3. **Security Scan** — Trivy FS scan + Snyk (HIGH severity threshold, non-blocking)
4. **Docker Build** — Build + push `ihhashi-backend:latest` / `ihhashi-frontend:latest` to Docker Hub (main branch only)
5. **Smoke Test** — Pull image and call `GET /health` (main branch only)
6. **Deploy** — Placeholder webhooks for staging (develop) and production (main)

---

## Code Quality Tools

### Backend

```bash
cd backend

# Linting (Ruff — fast, replaces flake8)
ruff check app

# Formatting (Black)
black app

# Import sorting (isort)
isort app

# Type checking (mypy)
mypy app
```

Pytest markers: `unit`, `integration`, `slow`, `auth`, `payment`

### Frontend

```bash
cd frontend

# Lint + auto-fix
npm run lint:fix

# Format (Prettier, runs via lint-staged on commit)
npx prettier --write src/
```

Husky pre-commit hook runs ESLint + Prettier on all staged `.ts`, `.tsx`, `.json`, `.md` files.

---

## Load & Security Testing

```bash
# k6 load test (requires k6 installed)
k6 run load-testing/k6-stress-test.js

# Fraud detection simulation
node security-tests/fraud-simulation-test.js
```

Security audit reports live in `docs/security/` (ShieldGuard report, BugHunter report, Remediation plan).

---

## Other Root-Level Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Project memory, pivot history, architectural decisions |
| `CHANGELOG.md` | Version history (current: v0.5.0) |
| `docs/PIVOT.md` | History of the pivot from Boober (ride-hailing) to iHhashi (delivery) |
| `docs/SA_LAUNCH_PLAYBOOK.md` | South Africa market launch strategy |
| `docs/scaling/100k-users-roadmap.md` | Scaling roadmap for 100k users |

---

## Common Tasks Cheat Sheet

```bash
# Generate a secure SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check backend health
curl http://localhost:8000/health

# Seed the database
cd backend && python scripts/seed_database.py

# View API documentation
open http://localhost:8000/docs

# Add a new backend route
# 1. Create backend/app/routes/<domain>.py with APIRouter
# 2. Mount in backend/app/main.py under api_v1
# 3. Add corresponding API helpers to frontend/src/lib/api.ts

# Add a new Pydantic model/schema
# Place in backend/app/models/ (MongoDB shape) or create schemas/ if needed
```
