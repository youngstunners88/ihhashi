# 🟢 BugHunter Security Report
## iHhashi Backend - Vulnerability Assessment

**Date:** 2026-02-26  
**Updated:** 2026-02-27 07:05 UTC  
**Scope:** `/home/workspace/iHhashi/backend/`  
**Severity Key:** 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low | ✅ Fixed

---

## 🚨 CRITICAL: Import Error - Backend Won't Start!

**Issue:** The backend cannot start due to broken imports.

**Details:**
- `app/models/user.py` is EMPTY (0 lines)
- Actual models are in `models/user.py` (not `app/models/`)
- Import `from app.models import UserCreate` in `app/routes/auth.py` fails

**Reproduction:**
```bash
cd backend && python3 -c "from app.models import UserCreate"
# ImportError: cannot import name 'User' from 'app.models.user'
```

**Impact:** Backend completely non-functional. This is a blocker - the app cannot start.

**Fix:** Either:
1. Copy contents from `models/user.py` to `app/models/user.py`, OR
2. Change imports in `auth.py` and other files to use `from models.user import ...`

---

## ✅ Fixed Issues

### 1. JWT User ID Type Confusion → ✅ FIXED
**File:** `app/services/auth.py`  
**Lines:** 8, 70

**Status:** ✅ FIXED - ObjectId is imported and used correctly in `get_current_user()`

### 2. Webhook Signature Verification → ✅ ALREADY FIXED
**File:** `app/routes/payments.py`  
**Lines:** 336-358

**Status:** ✅ VERIFIED - HMAC SHA512 signature verification in place

### 3. Payout Endpoint Authentication → ✅ ALREADY FIXED
**File:** `app/routes/payments.py`  
**Lines:** 198-210

**Status:** ✅ VERIFIED - Requires `get_current_user` dependency

---

## 🟠 High Findings (Still Present)

### 4. No Rate Limiting on Auth Endpoints
**File:** `app/routes/auth.py`

**Issue:** Login endpoint has no rate limiting despite config specifying `auth_rate_limit: "5/minute"`.

**Impact:** Brute force attacks on login possible.

**Status:** NOT FIXED

### 5. Password Strength Not Enforced
**File:** `models/user.py` (note: separate from app/models)

**Issue:** No minimum password length or complexity requirements.

**Status:** NOT FIXED

### 6. Debug Mode Exposes Sensitive Info
**File:** `app/config.py`  
**Line:** 12

```python
debug: bool = True
```

**Impact:** Stack traces exposed in production.

**Status:** NOT FIXED

### 7. Supabase Keys Not Validated
**File:** `app/config.py`  
**Lines:** 29-31

**Issue:** Empty keys will cause silent failures.

**Status:** NOT FIXED

---

## 🟡 Medium Findings

### 8. Hardcoded Callback URL (Still Accepts Client Input)
**File:** `app/routes/payments.py`  
**Line:** 87

```python
callback_url = payment.callback_url or "https://ihhashi.app/payment/callback"
```

**Issue:** Client can override callback URL - should whitelist allowed domains.

**Status:** NOT FIXED

### 9. No CORS Restriction for Production
**File:** `app/config.py`  
**Line:** 57

```python
cors_origins: str = "http://localhost:5173,http://localhost:3000"
```

**Status:** NOT FIXED

---

## 📊 Summary

| Severity | Original | Fixed | Remaining |
|----------|----------|-------|-----------|
| 🔴 Critical | 3 | 2 | 2 (Import bug + callback URL) |
| 🟠 High | 5 | 0 | 4 |
| 🟡 Medium | 5 | 1 | 4 |
| 🟢 Low | 2 | 0 | 2 |

### Priority Actions
1. **FIX IMMEDIATELY:** Import error (blocker - app won't start)
2. **FIX BEFORE PRODUCTION:** Debug mode, CORS origins, Supabase keys validation
3. **SECURE BEFORE PRODUCTION:** Rate limiting, password strength, callback URL whitelist