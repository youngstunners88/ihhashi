# iHhashi Play Store Listing

## App Information

**App Name:** iHhashi - Food Delivery SA

**Short Description:** Order food from local South African restaurants

**Full Description:**
> 🍔 Hungry? Order your favorite food with iHhashi!
> 
> iHhashi is South Africa's fastest-growing food delivery platform, connecting you with the best local restaurants, takeaways, and delivery riders in your area.
> 
> 🥡 Order from hundreds of local restaurants
> 🚴 Track your delivery in real-time
> 💳 Secure online payments with card or cash
> ⭐ Rate and review your favorite spots
> 
> Whether you're craving a Kota, Bunny Chow, Gatsby, pizza, sushi, or international cuisine — iHhashi delivers fresh to your door.
> 
> Download now and satisfy your hunger!

## Keywords
```
delivery, food, restaurant, takeout, eat, hungry, pizza, burger, south africa, sa, Johannesburg, Cape Town, Durban, Pretoria, local food, braai, kota, bunny chow, gatsby, uber eats alternative, foodpanda alternative
```

## Category
- **Primary:** Food & Drink
- **Tags:** Food delivery, Restaurants, Online ordering

## Age Rating
- Everyone

## Build Outputs

### Debug APK (Testing)
- **File:** `ihhashi-debug.apk`
- **Size:** 3.6MB
- **Location:** `/home/workspace/iHhashi/ihhashi-debug.apk`
- **Use:** For testing on device

### Release APK (For Play Store Submission)
- **File:** `ihhashi-release-unsigned.apk`
- **Size:** 2.9MB  
- **Location:** `/home/workspace/iHhashi/ihhashi-release-unsigned.apk`
- **Status:** ✅ Signed - see `ihhashi-release-signed.apk` below

### Signed Release APK (Ready for Play Store)
- **File:** `ihhashi-release-signed.apk`
- **Size:** 2.9MB
- **Location:** `/home/workspace/iHhashi/ihhashi-release-signed.apk`
- **Status:** ✅ Ready for Play Store submission
- **Certificate:** SHA-256: c0ca0fed6c3da128616834e0a160aecc615b5f805e3dee495bb927c54388a383

### To sign the release APK:
```bash
# Option 1: Create a new keystore (one-time)
keytool -genkey -v -keystore ihhashi.keystore -alias ihhashi -keyalg RSA -keysize 2048 -validity 10000

# Option 2: Sign the APK
apksigner sign --ks ihhashi.keystore --out ihhashi-release-signed.apk ihhashi-release-unsigned.apk
```

## Graphic Assets

### App Icon ✅
- Configured in Android (`android/app/src/main/res/mipmap-*/`)

### Screenshots ✅ (4 images, 2160x3840 each - Play Store ready)
1. `home-screenshot.png` - Home screen with categories
2. `cart-screenshot.png` - Cart/Checkout
3. `orders-screenshot.png` - Order tracking
4. `profile-screenshot.png` - User profile
- Location: `/home/workspace/iHhashi/docs/screenshots/`

### Feature Graphic ✅
- 1024 x 500px hero image
- Location: `/home/workspace/iHhashi/docs/screenshots/feature-graphic.png`

## URLs Required

### Privacy Policy URL ✅
- URL: https://kofi.zo.space/privacy-policy

### Support URL ✅  
- Email: teacherchris37@gmail.com

## Play Store Submission Checklist

| Item | Status |
|------|--------|
| App name with keywords | ✅ |
| Short description | ✅ |
| Full description | ✅ |
| Keywords | ✅ |
| Screenshots (4) | ✅ |
| App icon | ✅ |
| Privacy policy URL | ✅ |
| Support URL | ✅ |
| Category (Food & Drink) | ✅ |
| Age rating (Everyone) | ✅ |
| Release APK (unsigned) | ✅ |
| Signed release APK | ✅ Complete |
| Feature Graphic | ✅ |
| App preview video | ❌ Optional |

## Next Steps for Submission

1. **Create Google Play Console account** (if not already) - https://play.google.com/console
2. **Create app listing** in Play Console using:
   - App name: iHhashi - Food Delivery SA
   - Category: Food & Drink
   - Age rating: Everyone
   - Use the 4 screenshots from `/home/workspace/iHhashi/docs/screenshots/`
3. **Upload signed APK** (`ihhashi-release-signed.apk`)
4. **Complete store listing details**
5. **Submit for review**