# Google Play Store Listing

This document contains the listing information and go-live checklist for the Google Play Store deployment.

## App Information

| Field | Value |
|-------|-------|
| **App Name** | Delivery App |
| **Short Description** | Fast, reliable food and package delivery at your fingertips |
| **Full Description** | Get your favorite meals and packages delivered quickly and reliably. Track your orders in real-time, communicate with riders, and enjoy seamless payment options. |

## Store Assets

- **App Icon**: 512x512 PNG
- **Feature Graphic**: 1024x500 PNG
- **Screenshots**: 
  - Phone: 16:9 or 9:16 (minimum 320px)
  - Tablet: 16:9 or 9:16 (minimum 320px)
- **Promo Video**: Optional 30-120 seconds

## Content Rating

- **Category**: Food & Drink / Shopping
- **Content Rating**: PEGI 3 / ESRB Everyone
- **Target Audience**: General

## Pricing & Distribution

- **Price**: Free
- **In-app Purchases**: Yes (delivery fees, tips)
- **Countries**: All countries

---

## Go-Live Audit Checklist

Use this checklist to verify all requirements are met before publishing to the Google Play Store.

### Environment Configuration

| Item | Status | Notes |
|------|--------|-------|
| ☑️ VITE_API_URL prod set | ⬜ PASS / ⬜ FAIL | Must point to production API: `https://api.yourapp.com` |
| ☑️ Environment variables configured | ⬜ PASS / ⬜ FAIL | All `.env.production` values set |
| ☑️ Debug mode disabled | ⬜ PASS / ⬜ FAIL | `DEBUG=false` in production |

### Security

| Item | Status | Notes |
|------|--------|-------|
| ☑️ Release signing key created | ⬜ PASS / ⬜ FAIL | Generate with `keytool` |
| ☑️ Signing key backup verified | ⬜ PASS / ⬜ FAIL | Store in secure location (password manager, HSM) |
| ☑️ Key alias and passwords documented | ⬜ PASS / ⬜ FAIL | Never commit to version control |
| ☑️ ProGuard/R8 enabled | ⬜ PASS / ⬜ FAIL | Code obfuscation for release builds |
| ☑️ Network security config valid | ⬜ PASS / ⬜ FAIL | No cleartext traffic allowed |

### Legal & Compliance

| Item | Status | Notes |
|------|--------|-------|
| ☑️ Privacy policy URL works | ⬜ PASS / ⬜ FAIL | `https://yourapp.com/privacy` must be accessible |
| ☑️ Terms of service URL works | ⬜ PASS / ⬜ FAIL | `https://yourapp.com/terms` must be accessible |
| ☑️ Data safety section completed | ⬜ PASS / ⬜ FAIL | Disclose all data collection practices |
| ☑️ GDPR compliance verified | ⬜ PASS / ⬜ FAIL | Data deletion, export functionality |
| ☑️ COPPA compliance (if applicable) | ⬜ PASS / ⬜ FAIL | No ads to users under 13 |

### Monitoring & Crash Reporting

| Item | Status | Notes |
|------|--------|-------|
| ☑️ Crash reporting DSN set for prod | ⬜ PASS / ⬜ FAIL | Sentry/Firebase Crashlytics configured |
| ☑️ Error tracking enabled | ⬜ PASS / ⬜ FAIL | Uncaught exceptions captured |
| ☑️ Analytics configured | ⬜ PASS / ⬜ FAIL | User events tracked (with consent) |
| ☑️ Performance monitoring enabled | ⬜ PASS / ⬜ FAIL | App startup, screen load times |

### Backend & Infrastructure

| Item | Status | Notes |
|------|--------|-------|
| ☑️ Health/monitoring checks green | ⬜ PASS / ⬜ FAIL | `/health` endpoint returns 200 |
| ☑️ Database backups configured | ⬜ PASS / ⬜ FAIL | Automated daily backups |
| ☑️ SSL certificate valid | ⬜ PASS / ⬜ FAIL | TLS 1.2+ required |
| ☑️ Rate limiting enabled | ⬜ PASS / ⬜ FAIL | DDoS protection active |
| ☑️ CDN configured for static assets | ⬜ PASS / ⬜ FAIL | Images, JS, CSS served via CDN |

### App Functionality

| Item | Status | Notes |
|------|--------|-------|
| ☑️ Push notifications working | ⬜ PASS / ⬜ FAIL | FCM integration tested |
| ☑️ Deep linking configured | ⬜ PASS / ⬜ FAIL | Universal links verified |
| ☑️ Offline mode tested | ⬜ PASS / ⬜ FAIL | Graceful degradation without network |
| ☑️ Battery optimization checked | ⬜ PASS / ⬜ FAIL | No excessive background drain |
| ☑️ Memory leaks tested | ⬜ PASS / ⬜ FAIL | Profile with Android Studio |

### Testing

| Item | Status | Notes |
|------|--------|-------|
| ☑️ Unit tests passing | ⬜ PASS / ⬜ FAIL | `npm test` or equivalent |
| ☑️ E2E tests passing | ⬜ PASS / ⬜ FAIL | Critical user flows tested |
| ☑️ Tested on physical devices | ⬜ PASS / ⬜ FAIL | Minimum 3 different devices |
| ☑️ Android version compatibility | ⬜ PASS / ⬜ FAIL | API 26+ (Android 8.0) |
| ☑️ Screen sizes tested | ⬜ PASS / ⬜ FAIL | Phone, tablet, foldable |

### Store Listing

| Item | Status | Notes |
|------|--------|-------|
| ☑️ Screenshots up to date | ⬜ PASS / ⬜ FAIL | Reflect current app UI |
| ☑️ App description reviewed | ⬜ PASS / ⬜ FAIL | No typos, accurate features |
| ☑️ Release notes prepared | ⬜ PASS / ⬜ FAIL | What's new in this version |
| ☑️ Contact email verified | ⬜ PASS / ⬜ FAIL | Support email responsive |
| ☑️ Content rating questionnaire | ⬜ PASS / ⬜ FAIL | Accurate answers provided |

---

## Pre-Launch Commands

Run these commands before each release:

```bash
# Backend validation
cd backend && python -m compileall app scripts
cd backend && pytest -q

# Frontend validation
cd frontend && npm run typecheck
cd frontend && npm run build

# Security scan
trivy fs --severity HIGH,CRITICAL .

# Build release APK/AAB
cd frontend/android
./gradlew assembleRelease
./gradlew bundleRelease
```

---

## Release Checklist

1. [ ] Update version in `package.json` and `app.config.ts`
2. [ ] Update `CHANGELOG.md`
3. [ ] Merge release branch to `main`
4. [ ] Tag release: `git tag -a v1.0.0 -m "Release v1.0.0"`
5. [ ] Push tag: `git push origin v1.0.0`
6. [ ] Build signed release AAB
7. [ ] Upload to Google Play Console
8. [ ] Complete store listing review
9. [ ] Rollout to internal testing
10. [ ] Monitor crash reports for 24 hours
11. [ ] Promote to production (staged rollout)

---

## Post-Launch Monitoring

- [ ] Check crash-free rate > 99%
- [ ] Monitor ANR rate < 0.5%
- [ ] Track user retention (Day 1, Day 7, Day 30)
- [ ] Monitor API error rates
- [ ] Check app store ratings and reviews

---

## Emergency Rollback Procedure

If critical issues are detected post-launch:

1. **Immediate**: Halt rollout in Play Console
2. **Within 1 hour**: Assess issue severity
3. **If needed**: Promote previous stable version
4. **Communicate**: Notify users via in-app message or email
5. **Fix**: Deploy hotfix following normal release process

---

## Contact Information

| Role | Contact |
|------|---------|
| Technical Lead | tech-lead@yourapp.com |
| DevOps | devops@yourapp.com |
| Product Owner | product@yourapp.com |
| Support | support@yourapp.com |

---

**Last Updated**: 2026-03-02
**Version**: 1.0.0
