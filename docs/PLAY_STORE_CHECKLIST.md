# iHhashi Google Play Store Launch Checklist

## ✅ COMPLETED

### Design & UI
- [x] Splash screen with branded image (`/assets/splash.jpg`)
- [x] Yellow (#FFD700) and black (#1A1A1A) color theme applied
- [x] Blue Horse verification badge component
- [x] Transport options with custom images (walking, skateboard, bicycle, motorbike)
- [x] Merchant cards with verification badges
- [x] Rider dashboard with full functionality

### Core Features
- [x] Multi-modal delivery transport options
- [x] Blue Horse verification system
- [x] 45-day free trial for delivery servicemen
- [x] 0% platform fee on tips
- [x] Competitive pricing (servicemen set own rates)
- [x] Multi-language support (English, Zulu, Sotho, Afrikaans, Tswana, Xhosa)

---

## 📋 PRE-LAUNCH REQUIREMENTS

### 1. Legal & Compliance (CRITICAL)

#### Privacy Policy
- [ ] Create `PRIVACY_POLICY.md` in `/docs/`
- [ ] Must include:
  - Data collection (location, phone, ID for verification)
  - Data usage (delivery matching, payments)
  - Third-party sharing (payment processors, maps)
  - User rights (access, delete, export)
  - Contact information
- [ ] Host privacy policy on website (ihhashi.co.za/privacy)
- [ ] Link in app Settings → Privacy

#### Terms of Service
- [ ] Review existing `TERMS_OF_SERVICE.md`
- [ ] Add:
  - Delivery serviceman independent contractor clause
  - 45-day trial terms
  - Account termination policies
  - Dispute resolution
- [ ] Host at ihhashi.co.za/terms

#### Content Rating
- [ ] Complete Google Play Content Rating questionnaire
- [ ] Expected rating: **Everyone** (no violence, no mature content)

### 2. App Assets (CRITICAL)

#### App Icon
- [ ] Create adaptive icon (Android API 26+)
  - Foreground: iHhashi horse logo
  - Background: #FFD700 (yellow)
- [ ] Sizes needed:
  - 48x48 mdpi
  - 72x72 hdpi
  - 96x96 xhdpi
  - 144x144 xxhdpi
  - 192x192 xxxhdpi
- [ ] Location: `/frontend/android/app/src/main/res/mipmap-*/`

#### Feature Graphic (Play Store)
- [ ] 1024x500px banner showing:
  - App name: "iHhashi - Food Delivery SA"
  - Tagline: "Your Delivery Horse"
  - Yellow/black theme
  - Food delivery imagery

#### Screenshots (Phone)
- [ ] Need 4-8 screenshots (min 320px, max 3840px)
- [ ] Required dimensions: 16:9 or 9:16 aspect ratio
- [ ] Recommended: 1080x1920 (Portrait)
- [ ] Screens to capture:
  1. Home screen with merchants
  2. Search results
  3. Cart/Checkout
  4. Order tracking
  5. Rider dashboard
  6. Profile/Settings

#### Screenshots (Tablet) - Optional
- [ ] 7-inch tablet screenshots (if optimizing for tablets)
- [ ] 10-inch tablet screenshots

### 3. App Configuration

#### Android Manifest
```xml
<!-- Check these are set correctly -->
<manifest>
    <application
        android:label="@string/app_name"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:theme="@style/AppTheme">
        
        <!-- Required permissions -->
        <uses-permission android:name="android.permission.INTERNET" />
        <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
        <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
        <uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
        <uses-permission android:name="android.permission.CAMERA" />
        <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
        
        <!-- Feature declarations -->
        <uses-feature android:name="android.hardware.location.gps" android:required="true" />
        <uses-feature android:name="android.hardware.camera" android:required="false" />
    </application>
</manifest>
```

#### Version Information
```gradle
// In build.gradle (Module: app)
android {
    defaultConfig {
        applicationId "com.ihhashi.app"
        minSdk 24        // Android 7.0
        targetSdk 34     // Android 14
        versionCode 1
        versionName "1.0.0"
    }
}
```

### 4. Backend Requirements

#### API Endpoints
- [ ] Production API URL configured
- [ ] HTTPS enforced
- [ ] Rate limiting active
- [ ] GlitchTip error monitoring enabled

#### Database
- [ ] MongoDB indexes created
- [ ] Database backups scheduled
- [ ] Data retention policies set

#### Security
- [ ] JWT secret rotated
- [ ] API keys stored securely
- [ ] CORS origins restricted to production domains

### 5. Testing

#### Device Testing
- [ ] Test on Android 7.0 (API 24) - minimum
- [ ] Test on Android 14 (API 34) - latest
- [ ] Test on Samsung device (most common in SA)
- [ ] Test on budget device (performance check)
- [ ] Test location services
- [ ] Test camera (for verification uploads)

#### Functional Testing
- [ ] User registration flow
- [ ] Login with phone OTP
- [ ] Browse merchants
- [ ] Add to cart
- [ ] Checkout with Paystack
- [ ] Track order
- [ ] Become a rider flow
- [ ] Upload verification documents
- [ ] Switch transport modes
- [ ] Go online/offline as rider

#### Edge Cases
- [ ] No internet connection
- [ ] GPS disabled
- [ ] Camera permission denied
- [ ] Payment failure
- [ ] App backgrounding during order

### 6. Performance

#### App Size
- [ ] Target: < 50MB APK
- [ ] Enable ProGuard/R8 minification
- [ ] Compress images
- [ ] Remove debug symbols

#### Performance Metrics
- [ ] Cold start < 3 seconds
- [ ] Warm start < 1.5 seconds
- [ ] List scrolling 60fps
- [ ] Memory usage < 150MB average

### 7. Store Listing

#### App Information
```
Title: iHhashi - Food Delivery South Africa
Short description: Your Delivery Horse - Fast food, groceries & more
Full description: |
  iHhashi is South Africa's delivery platform connecting you with local 
  restaurants, grocery stores, and fresh produce markets.
  
  🚀 FAST DELIVERY
  Get your food delivered in 25-45 minutes from verified local merchants.
  
  🏪 BLUE HORSE VERIFIED
  All our merchants are verified for quality and reliability.
  
  💰 FAIR PRICING
  Delivery servicemen set their own competitive rates.
  
  🌍 SUPPORTING LOCAL
  We partner with township businesses and local entrepreneurs.
  
  🐴 BECOME A DELIVERY HERO
  Earn money delivering with walking, bicycle, skateboard, or motorbike.
  45-day free trial. You set your own rates!
  
  Available in: English, isiZulu, Sesotho, Afrikaans, Setswana, isiXhosa
  
  Download iHhashi today - Your Delivery Horse is ready!
```

#### Categories
- Primary: Food & Drink
- Secondary: Shopping

#### Contact Details
- [ ] Developer name: iHhashi Technologies
- [ ] Website: ihhashi.co.za
- [ ] Email: support@ihhashi.co.za
- [ ] Phone: +27 XX XXX XXXX

### 8. Pre-Launch Marketing

#### App Store Optimization (ASO)
- [ ] Keyword research ("food delivery South Africa", "Soweto delivery", etc.)
- [ ] Optimized title and description
- [ ] Screenshots with callouts
- [ ] Promo video (optional but recommended)

#### Social Media
- [ ] Facebook page created
- [ ] Instagram account created
- [ ] Twitter/X account created
- [ ] TikTok account (optional)

#### Press Kit
- [ ] App icon (high-res)
- [ ] Screenshots
- [ ] Brand guidelines
- [ ] Press release template

### 9. Post-Launch Monitoring

#### Analytics
- [ ] Google Analytics configured
- [ ] Firebase Crashlytics enabled
- [ ] Custom events tracking:
  - Order completed
  - Rider signup
  - Verification submission
  - App crashes

#### Support
- [ ] Support email monitored
- [ ] FAQ page created
- [ ] In-app feedback mechanism

---

## 🚀 LAUNCH SEQUENCE

### Week 1: Final Preparation
- Day 1-2: Complete legal documents
- Day 3-4: Final testing on devices
- Day 5: Create store listing content
- Day 6: Generate signed release APK
- Day 7: Internal testing track

### Week 2: Soft Launch
- Day 1: Release to Closed Testing (100 users)
- Day 2-3: Monitor crashes and feedback
- Day 4-5: Fix critical issues
- Day 6-7: Prepare for production

### Week 3: Production Launch
- Day 1: Release to Production (South Africa only)
- Day 2-3: Monitor metrics closely
- Day 4-5: Respond to reviews
- Day 6-7: Plan first update

---

## 📊 SUCCESS METRICS

### Week 1 Targets
- Downloads: 500+
- Active users: 200+
- Orders: 50+
- Crash-free rate: > 99%

### Month 1 Targets
- Downloads: 5,000+
- Active riders: 100+
- Merchants onboarded: 50+
- Average rating: 4.0+

---

## 🔧 IMMEDIATE ACTION ITEMS

### Before Next Week
1. [ ] Create privacy policy page
2. [ ] Generate app icons (all densities)
3. [ ] Take 8 screenshots on Android device
4. [ ] Create feature graphic
5. [ ] Test on physical Android device
6. [ ] Set up Google Play Console
7. [ ] Create signed release build

### Nice to Have
- [ ] Promo video (30 seconds)
- [ ] Influencer partnerships
- [ ] Launch promotion (R50 off first order)
- [ ] Referral program

---

**Last Updated:** March 2026
**Next Review:** Before launch
