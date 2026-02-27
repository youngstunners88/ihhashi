# iHhashi

**Delivery platform for South Africa** - Food, groceries, fruits & vegetables, and personal courier services.

Inspired by Ele.me, built for Mzansi. 🇿🇦

## Features

- 🍽️ **Food Delivery** - Restaurants, takeaways, local SA food (Kota, Bunny Chow, Gatsby)
- 🛒 **Groceries** - Supermarkets, spaza shops
- 🥬 **Fresh Produce** - Fruits & vegetables
- 📦 **Courier Services** - Packages, documents, parcels
- 🚗 **Multi-Modal Delivery** - Car, motorcycle, scooter, bicycle, on-foot
- 🔵 **Blue Horse Verification** - Trust system for vendors and delivery partners
- 🇿🇦 **South African** - All 9 provinces, ZAR currency, local languages

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI, MongoDB, Redis |
| **Frontend** | React, Tailwind CSS, Capacitor |
| **Mobile** | Android (Capacitor), PWA |
| **Auth** | Supabase (Phone OTP) |
| **Payments** | Paystack, Yoco |
| **Maps** | Google Maps |
| **Analytics** | PostHog |
| **Errors** | GlitchTip |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB 7.0
- Redis 7

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourorg/ihhashi.git
cd ihhashi

# Backend setup
cd backend
cp .env.example .env
# Edit .env with your values
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
cp .env.example .env
# Edit .env with your values
npm install
npm run dev
```

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Project Structure

```
ihhashi/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── models/        # Database models
│   │   ├── routes/        # Route handlers
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── middleware/    # Rate limiting, security
│   ├── scripts/
│   │   ├── migrations/    # Database migrations
│   │   └── seed_database.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom hooks
│   │   ├── lib/           # API client, utilities
│   │   └── styles/        # CSS/Tailwind
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── deployment/
│   ├── vercel.json        # Vercel configuration
│   ├── render.yaml        # Render blueprint
│   ├── docker-compose.prod.yml
│   └── nginx/             # Nginx configs
├── docs/
│   ├── PLAY_STORE_LISTING.md
│   ├── TERMS_OF_SERVICE.md
│   └── screenshots/
└── docker-compose.yml     # Development compose
```

## Deployment

### Option 1: Render (Recommended)

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Connect your GitHub repository

3. **Deploy using Blueprint**
   - Create a new Blueprint
   - Select your repository
   - Render will detect `deployment/render.yaml`

4. **Set Environment Variables**
   - Set all `sync: false` variables in Render dashboard
   - See `backend/.env.example` for full list

5. **Deploy Frontend to Vercel** (see Option 2)

### Option 2: Vercel + Render

**Frontend (Vercel):**

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

**Backend (Render):**
Follow Option 1 steps, or deploy manually:
1. Create a new Web Service
2. Connect GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Option 3: Self-Hosted (Docker)

```bash
# Copy environment file
cp backend/.env.example .env

# Edit with production values
nano .env

# Deploy with Docker Compose
docker-compose -f deployment/docker-compose.prod.yml up -d

# View logs
docker-compose -f deployment/docker-compose.prod.yml logs -f

# Run migrations
docker-compose -f deployment/docker-compose.prod.yml exec backend \
  python -m scripts.migrations.migrate --up
```

### SSL Certificates (Let's Encrypt)

```bash
# Initial certificate request
docker-compose -f deployment/docker-compose.prod.yml run --rm certbot \
  certonly --webroot --webroot-path /var/www/certbot \
  -d ihhashi.co.za -d www.ihhashi.co.za -d api.ihhashi.co.za

# Certificates auto-renew via certbot container
```

## Environment Setup

### Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | JWT signing key | ✅ |
| `MONGODB_URL` | MongoDB connection string | ✅ |
| `REDIS_URL` | Redis connection string | ✅ |
| `SUPABASE_URL` | Supabase project URL | ✅ |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | ✅ |
| `PAYSTACK_SECRET_KEY` | Paystack secret key | ✅ |
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | ✅ |

### Optional Environment Variables

| Variable | Description |
|----------|-------------|
| `GLITCHTIP_DSN` | Error tracking DSN |
| `POSTHOG_API_KEY` | Analytics key |
| `FIREBASE_*` | Push notifications |
| `TWILIO_*` | SMS notifications |
| `TELEGRAM_BOT_TOKEN` | Telegram bot |

See `backend/.env.example` and `frontend/.env.example` for complete lists.

## Database Migrations

```bash
# View migration status
python -m scripts.migrations.migrate --status

# Apply pending migrations
python -m scripts.migrations.migrate --up

# Rollback last migration
python -m scripts.migrations.migrate --down

# Create a new migration
python -m scripts.migrations.migrate --create "add_new_field"
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run e2e tests
npm run test:e2e
```

### Type Checking

```bash
# Backend
cd backend
mypy app

# Frontend
cd frontend
npm run typecheck
```

## API Documentation

Once the backend is running, access the API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Mobile App (Android)

### Build Debug APK

```bash
cd frontend
npm run build
npx cap sync android
cd android
./gradlew assembleDebug
```

### Build Release APK

```bash
# Build and sign release
cd frontend/android
./gradlew assembleRelease

# APK location: frontend/android/app/build/outputs/apk/release/
```

### Play Store

See `docs/PLAY_STORE_LISTING.md` for store listing details.

## Monitoring

### Health Endpoints

- `GET /health` - Basic health check
- `GET /` - API info

### Error Tracking

Errors are tracked via GlitchTip:
- DSN: Configure `GLITCHTIP_DSN` environment variable
- Dashboard: https://app.glitchtip.com

### Analytics

User behavior tracked via PostHog:
- Configure `POSTHOG_API_KEY`
- Dashboard: https://app.posthog.com

## Security

- **Rate Limiting**: API protected with slowapi
- **CORS**: Configurable allowed origins
- **JWT**: Secure token-based authentication
- **Input Validation**: Pydantic schemas
- **Helmet Headers**: Security headers in responses

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Proprietary - All rights reserved.

## Support

- **Website**: https://ihhashi.co.za
- **Email**: support@ihhashi.co.za
- **Play Store**: [iHhashi - Food Delivery SA](https://play.google.com/store/apps/details?id=za.co.ihhashi)

---

Built with ❤️ in South Africa
