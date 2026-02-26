# iHhashi Project Memory

## Project Overview
Delivery platform for South Africa, inspired by Ele.me.
- **Started**: 2026-02-25
- **Tech Stack**: FastAPI + MongoDB (backend), React + Tailwind (frontend)

## Architecture

### Three User Types
1. **Customers** - Browse merchants, order, track delivery
2. **Merchants** - Manage menu, receive orders, analytics
3. **Riders** - Accept deliveries, navigate, earn

### Database Models
- User (email, phone, role, location)
- Merchant (name, category, menu, hours, location)
- Order (items, status, delivery address, tracking)
- Rider (vehicle, status, location, earnings)

## South Africa Specific
- Currency: ZAR (R)
- Local food: Kota, Bunny Chow, Gatsby, Braai
- All 9 provinces supported

## Next Steps
1. Set up MongoDB (Atlas or local)
2. Implement JWT auth fully
3. Add geolocation (Google Maps/OpenStreetMap)
4. Integrate Stripe payments
5. Push notifications
6. Testing
7. Deployment

## Status
- ✅ Project scaffolded
- ✅ Models defined
- ✅ Routes stubbed
- ✅ Frontend UI started
- ⏳ Database connection
- ⏳ Auth implementation
- ⏳ Real functionality

## Play Store Preparation (2026-02-25)
- ✅ Capacitor installed (@capacitor/core, @capacitor/cli, @capacitor/android)
- ✅ Android project initialized (app-id: com.ihhashi.delivery)
- ✅ Frontend builds successfully
- ✅ Android platform added with splash screens and icons
- ✅ Debug APK built successfully (3.6MB)
  - Location: `frontend/android/app/build/outputs/apk/debug/app-debug.apk`
- 🔄 Play Store listing in progress

### To build APK:
```bash
cd /home/workspace/iHhashi/frontend/android
./gradlew assembleDebug
```

### Play Store Listing Status:
- [x] Privacy policy URL - https://kofi.zo.space/privacy-policy
- [x] Support URL - teacherchris37@gmail.com
- [ ] App title with keywords (iHhashi - Food Delivery SA)
- [ ] Subtitle (Order food from local restaurants)
- [ ] App description (hook in first 2 lines)
- [x] Keywords - Researched and ready
- [ ] Screenshots (need 2-8 screenshots)
- [ ] App preview video (optional)
- [ ] App category selected (Food & Drink)
- [ ] Age rating completed

### Next steps for Play Store:
1. Add Google Sign-In (optional but recommended)
2. Set up Firebase for push notifications
3. Configure ProGuard for release builds
4. Generate signed APK/AAB for release
5. Create Play Store listing (screenshots, description)