# iHhashi Project Memory

## ⚠️ PIVOT HISTORY

**iHhashi evolved from Boober** (a ride-hailing app like Uber/Bolt):
- **Boober** was the original project - taxi/ride-hailing for South Africa
- **Pivot Date**: 2026-02-25
- **Why**: Food delivery has lower regulatory barriers, faster path to revenue in SA market
- **What Changed**: Same tech stack, same team, different use case
- **Legacy Files**: Old Boober files exist in `/home/workspace/Boober/` - these are archived, NOT the current project

**Current Project: iHhashi** (food delivery like Uber Eats/Order.in)
- Repository: `/home/workspace/iHhashi/`
- Focus: Food delivery, not ride-hailing

---

## Project Overview
Delivery platform for South Africa, inspired by Ele.me.
- **Started**: 2026-02-25
- **Tech Stack**: FastAPI + MongoDB (backend), React + Tailwind (frontend)
- **Version**: 0.2.0

## Architecture

### Three User Types
1. **Customers** - Browse merchants, order, track delivery
2. **Vendors/Merchants** - Manage menu, receive orders, analytics
3. **Delivery Servicemen** - Accept deliveries, navigate, earn

### Database Models
- User (email, phone, role, location)
- Merchant (name, category, menu, hours, location)
- Order (items, status, delivery address, tracking)
- Rider (vehicle, status, location, earnings)
- Verification (Blue Horse system)
- Account (warnings, suspension, termination)

## South Africa Specific
- Currency: ZAR (R)
- Local food: Kota, Bunny Chow, Gatsby, Braai
- All 9 provinces supported
- **Languages**: English, Zulu, Sotho, Afrikaans, Tswana, Xhosa
- VAT: 15%

---

## ✅ FEATURES IMPLEMENTED (v0.2.0)

### Blue Horse Verification System
- **Vendor Verification**: ID, company registration, business license, proof of address
- **Delivery Serviceman Verification**: ID, license, vehicle registration, number plate
- **Customer Light KYC**: ID verification
- **Verification Levels**: 0=unverified, 1=basic, 2=full (Blue Horse), 3=premium
- **Ranking Boost**: Verified vendors appear higher in search

### Multi-Modal Delivery
- **Transport Options**: Car, Motorcycle, Scooter, Bicycle, On-foot
- **Competitive Pricing**: Delivery servicemen set their own rates
- **Inclusive**: Supports those without vehicles (bicycle, walking)

### Account Management
- **45-Day Free Trial**: All new users get free access
- **Warning System**: 3 warnings = automatic suspension
- **Termination Rules**: Criminal activity = permanent termination
- **Suspension Appeals**: 30-day window

### Tipping System
- **0% Platform Fee**: 100% of tips go to delivery servicemen
- Optional tipping on delivery completion

### Product Template
- Up to 5 images per product
- Price with VAT inclusive
- Description, category, availability
- Ratings and reviews

### Reviews & Comments
- All users can read and comment
- Vendors can respond to reviews
- Star ratings (1-5)

### Error Tracking
- **GlitchTip Integration**: Open-source Sentry alternative
- **DSN**: https://25a5585d096a411495f93126742fbf73@app.glitchtip.com/20760
- **Security Endpoint**: https://app.glitchtip.com/api/20760/security/?glitchtip_key=25a5585d096a411495f93126742fbf73

### Language Support
- English (en)
- Zulu/isiZulu (zu)
- Sotho/Sesotho (st)
- Afrikaans (af)
- Tswana/Setswana (tn)
- Xhosa/isiXhosa (xh)

### Infrastructure
- **Docker Compose**: Full stack with MongoDB, Redis, GlitchTip
- **GitHub Actions**: CI/CD pipeline with lint, test, build, deploy
- **Rate Limiting**: slowapi for API protection
- **Analytics**: PostHog integration

---

## 📁 KEY FILES

### Backend
- `backend/app/main.py` - FastAPI app with GlitchTip
- `backend/app/config.py` - Settings with all new features
- `backend/app/models/verification.py` - Blue Horse system
- `backend/app/models/account.py` - Warning/termination logic
- `backend/app/models/delivery.py` - Multi-modal delivery, tipping
- `backend/app/routes/vendors.py` - Vendor verification routes
- `backend/app/routes/delivery_servicemen.py` - Serviceman routes

### Frontend
- `frontend/src/App.tsx` - Splash screen, GlitchTip init
- `frontend/src/components/SplashScreen.tsx` - Logo display
- `frontend/src/components/LanguageSelector.tsx` - Language switcher
- `frontend/public/logo.png` - iHhashi logo

### Infrastructure
- `docker-compose.yml` - Full stack deployment
- `.github/workflows/ci-cd.yml` - GitHub Actions pipeline

### Documentation
- `docs/TERMS_OF_SERVICE.md` - Full ToS with rules
- `backend/.env.example` - Environment template

---

## Play Store Preparation (2026-02-26)

### Build Outputs
- ✅ Debug APK: `ihhashi-debug.apk` (3.6MB)
- ✅ Release APK (unsigned): `ihhashi-release-unsigned.apk` (2.9MB)
- ✅ Signed release APK: `ihhashi-release-signed.apk` (2.9MB) - Ready for Play Store

### Listing Status (All Complete)
- ✅ App name: iHhashi - Food Delivery SA
- ✅ Short description
- ✅ Full description  
- ✅ Keywords
- ✅ Screenshots (4 images, 2160x3840 each)
- ✅ App icon
- ✅ Privacy policy URL
- ✅ Support URL
- ✅ Category: Food & Drink
- ✅ Age rating: Everyone
- ✅ Signed release APK (2.9MB) - Ready for Play Store

### Files
- APKs: `/home/workspace/iHhashi/*.apk`
- Screenshots: `/home/workspace/iHhashi/docs/screenshots/`
- Listing docs: `/home/workspace/iHhashi/docs/PLAY_STORE_LISTING.md`

## ✅ FEATURES IMPLEMENTED (v0.3.0)

### Payment Scheduling (v0.3.0)
- **Payout Day**: Every Sunday at 11:11 AM SAST
- **Who Gets Paid**: All verified delivery servicemen and drivers
- **Minimum Payout**: R100 (accumulated weekly earnings)
- **Automatic Processing**: Background scheduler handles all payouts
- **Bank Integration**: Paystack transfer to SA banks (FNB, Capitec, Standard Bank, etc.)

### Inclusive Delivery Transport (v0.3.0)
- **Standard Options**: Car, Motorcycle, Scooter, Bicycle, On-foot
- **Inclusive Options**:
  - Wheelchair - Users with wheelchairs are welcome delivery partners
  - Running - For fitness enthusiasts
  - Rollerblade - Alternative eco-friendly transport
- **Competitive Pricing**: Each serviceman sets their own rates

### Database Seeding (v0.3.0)
- **Script**: `backend/scripts/seed_database.py`
- **Sample Data**: Admin user, 7 delivery servicemen (all transport types), 3 merchants
- **Run**: `cd backend && python -m scripts.seed_database`

---

## 🔧 INFRASTRUCTURE

### Error Tracking
- **GlitchTip** (NOT Sentry): Open-source error tracking
- **DSN**: https://25a5585d096a411495f93126742fbf73@app.glitchtip.com/20760

### Authentication
- **Supabase**: Phone OTP authentication
- **Hook**: `useSupabase.ts` for auth state management

### Language Support (i18n)
- **Package**: react-i18next
- **Languages**: English, Zulu, Sotho, Afrikaans, Tswana, Xhosa

---

## 🤖 AGENT SYNCHRONIZATION

### Keeping Agents Updated
When iHhashi is updated, run the sync skill to update all agent knowledge bases:
```bash
bun /home/workspace/Skills/ihhashi-sync/scripts/sync.ts
```

This automatically updates:
1. **Nduna Bot** - Telegram bot knowledge base (`/home/workspace/mosta-agent/knowledge-base.json`)
2. **Marketing OpenClaw** - Marketing prompts (`/home/workspace/mosta-agent/prompts/marketing-prompts.md`)

### When to Sync
- New features added/removed
- Business logic changes (pricing, payments, verification)
- New user types or roles
- Marketing messaging updates
- Any significant app update

### Rule
Zo has a rule to automatically run this sync whenever iHhashi is updated.