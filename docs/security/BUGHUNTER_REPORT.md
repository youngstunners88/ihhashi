# 🔴 BugHunter Security Report
## iHhashi Backend - Vulnerability Assessment

**Date:** 2026-02-26  
**Scope:** `/home/workspace/iHhashi/backend/`  
**Severity Key:** 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low

---

## 🔴 Critical Findings

### 1. JWT User ID Type Confusion
**File:** `app/services/auth.py`  
**Lines:** 62-71  

```python
user_doc = await users_col.find_one({"_id": user_id})
```

**Issue:** The JWT payload stores `user_id` as a string, but MongoDB `_id` is an ObjectId. Querying with a string will never match.

**Impact:** `get_current_user()` always fails for valid tokens → All protected endpoints broken in production.

**Fix:**
```python
from bson import ObjectId
user_doc = await users_col.find_one({"_id": ObjectId(user_id)})
```

---

### 2. No Webhook Signature Verification
**File:** `app/routes/payments.py`  
**Lines:** 150-175

```python
@router.post("/webhook")
async def paystack_webhook(request: Request):
    payload = await request.json()
    event = payload.get("event")
    # No signature verification!
```

**Issue:** Paystack webhooks are accepted without verifying the `x-paystack-signature` header.

**Impact:** Attacker can fake payment success events → Free orders, fake payouts to themselves.

**Fix:** Verify signature before processing:
```python
from app.services.paystack import verify_webhook_signature
signature = request.headers.get("x-paystack-signature")
if not verify_webhook_signature(signature, await request.body()):
    raise HTTPException(status_code=401, detail="Invalid signature")
```

---

### 3. Payout Endpoint Missing Authentication
**File:** `app/routes/payments.py`  
**Lines:** 108-145

```python
@router.post("/payout", response_model=PaymentResponse)
async def create_payout(payout: PayoutRequest):
    # No current_user dependency!
```

**Issue:** Payout endpoint has no authentication. Anyone can drain the merchant/driver wallet.

**Fix:**
```python
async def create_payout(
    payout: PayoutRequest,
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.MERCHANT]:
        raise HTTPException(status_code=403, detail="Unauthorized")
```

---

## 🟠 High Findings

### 4. Email Not Validated Before Registration
**File:** `app/services/auth.py`  
**Lines:** 29-34

**Issue:** No email format validation. Could register `test@test` or invalid emails.

**Impact:** Spammers could create accounts; database pollution.

**Fix:** Add Pydantic email validator:
```python
from pydantic import EmailStr
email: EmailStr
```

---

### 5. No Rate Limiting on Auth Endpoints
**File:** `app/routes/auth.py`  

**Issue:** Login endpoint has no rate limiting despite config specifying `auth_rate_limit: "5/minute"`.

**Impact:** Brute force attacks on login.

**Fix:** Apply rate limiter:
```python
from app.middleware.rate_limit import rate_limit_dependency

@router.post("/login", dependencies=[Depends(rate_limit_dependency)])
```

---

### 6. Password Strength Not Enforced
**File:** `app/services/auth.py`  

**Issue:** No minimum password length or complexity requirements.

**Impact:** Weak passwords susceptible to dictionary attacks.

**Fix:** Validate on registration:
```python
if len(user_data.password) < 8:
    raise HTTPException(status_code=400, detail="Password too short")
```

---

### 7. Debug Mode Exposes Sensitive Info
**File:** `app/config.py`  
**Line:** 53

```python
debug: bool = True
```

**Issue:** Default is debug mode, exposing stack traces in production errors.

**Impact:** Information disclosure about internal architecture.

---

### 8. Supabase Keys in Config
**File:** `app/config.py`  
**Lines:** 27-29

```python
supabase_anon_key: str = ""
supabase_service_role_key: str = ""
```

**Issue:** Empty keys will cause silent failures. No validation that required keys are set.

**Impact:** Supabase features fail silently.

---

## 🟡 Medium Findings

### 9. No Input Sanitization on User Fields
**Files:** `app/routes/auth.py`, `app/services/auth.py`

**Issue:** User `full_name`, `phone`, `email` stored without sanitization.

**Impact:** Stored XSS if displayed in admin panel; NoSQL injection potential.

---

### 10. Payment Amount Not Trusted
**File:** `app/routes/payments.py`  
**Lines:** 38-60

```python
result = await paystack.initialize_payment(
    email=payment.email,
    amount=payment.amount,  # Client-controlled!
```

**Issue:** Amount comes from client. Attacker could set `amount: 0.01` for expensive orders.

**Impact:** Underpayment attacks.

**Fix:** Calculate amount server-side from order_id:
```python
order = await get_order(payment.order_id)
amount = order.total
```

---

### 11. Hardcoded Callback URL
**File:** `app/routes/payments.py`  
**Line:** 50

```python
callback_url = payment.callback_url or f"https://ihhashi.app/payment/callback"
```

**Issue:** Client can override callback URL → Payment redirect to attacker-controlled site.

**Impact:** Phishing attacks on users.

**Fix:** Only allow whitelisted domains.

---

### 12. No CORS Restriction for Production
**File:** `app/config.py`  
**Line:** 59

```python
cors_origins: str = "http://localhost:5173,http://localhost:3000"
```

**Issue:** No production domains configured. Will fail when deployed.

---

### 13. Pydantic Secret Key
**File:** `app/config.py`  
**Line:** 12

```python
secret_key: str  # Required - must be set in .env (no default!)
```

**Issue:** App will crash if secret_key not set. No helpful error message.

---

## 🟢 Low Findings

### 14. TODO Comments in Webhook Handler
**File:** `app/routes/payments.py`  
**Lines:** 162-175

**Issue:** Webhook events logged but not actually processed (TODO comments).

**Impact:** Payment confirmation doesn't update database.

---

### 15. No Logging of Security Events
**Files:** Multiple

**Issue:** Failed login attempts, unusual API calls not logged.

**Impact:** Cannot detect attacks.

---

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | 3 |
| 🟠 High | 5 |
| 🟡 Medium | 5 |
| 🟢 Low | 2 |

**Immediate Actions Required:**
1. Fix JWT ObjectId lookup (breaks auth)
2. Verify webhook signatures (financial fraud risk)
3. Add authentication to payout endpoint (funds theft risk)