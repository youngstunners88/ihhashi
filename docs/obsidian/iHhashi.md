# iHhashi

> Food delivery platform for South Africa, inspired by Ele.me

**Started**: 2026-02-25
**Status**: Development
**Repository**: `/home/workspace/iHhashi`

---

## Quick Links

- [[Architecture Overview]] - System architecture and tech stack
- [[User Types]] - Customers, Merchants, Riders
- [[API Reference]] - Backend API endpoints
- [[Sprint Backlog]] - Current and planned work
- [[Daily Log]] - Development log

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + TypeScript + Tailwind CSS |
| Backend | FastAPI (Python) |
| Database | MongoDB |
| Mobile | Capacitor (Android) |
| Auth | Supabase + JWT |
| Analytics | PostHog |

---

## Project Structure

```
iHhashi/
├── frontend/          # React + Capacitor app
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── lib/
│   └── android/
├── backend/           # FastAPI server
│   ├── app/
│   │   ├── routes/
│   │   ├── models/
│   │   └── services/
│   └── tests/
└── docs/              # Documentation
```

---

## Current Status

- ✅ Project scaffolded
- ✅ Models defined
- ✅ Routes stubbed
- ✅ Frontend UI started
- ✅ Debug APK built
- ⏳ Database connection
- ⏳ Auth implementation
- ⏳ Real functionality

---

## South Africa Specific

- **Currency**: ZAR (R)
- **Local foods**: Kota, Bunny Chow, Gatsby, Braai
- **Coverage**: All 9 provinces

---

## Next Steps

1. Set up MongoDB (Atlas or local)
2. Implement JWT auth fully
3. Add geolocation (Google Maps/OpenStreetMap)
4. Integrate Stripe payments
5. Push notifications
6. Testing
7. Deployment

---

#iHhashi #project