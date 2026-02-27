# Security middleware for iHhashi
from fastapi import Request, HTTPException
from fastapi.middleware import Middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import hashlib
import hmac
from typing import Optional
from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = settings.x_frame_options
        response.headers["X-Content-Type-Options"] = settings.x_content_type_options
        
        # HTTPS only in production
        if settings.environment == "production":
            response.headers["Strict-Transport-Security"] = settings.strict_transport_security
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = settings.content_security_policy
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


# NOTE: RequestValidationMiddleware has been removed.
# FastAPI/Pydantic + Motor (MongoDB ORM) already provide robust protection against
# SQL injection and XSS through:
# - Pydantic validation and sanitization of all input
# - Motor's parameterized queries (MongoDB operations are injection-safe by design)
# - FastAPI's automatic request validation
# Adding naive pattern matching causes false positives and doesn't improve security.


class TimingMiddleware(BaseHTTPMiddleware):
    """Add request timing for performance monitoring"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.3f}s"
        
        # Log slow requests (over 2 seconds - bad for SA networks)
        if process_time > 2.0:
            print(f"SLOW REQUEST: {request.method} {request.url.path} took {process_time:.3f}s")
        
        return response


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signatures (Paystack, Yoco, etc.)"""
    expected_signature = hmac.new(
        secret.encode(), 
        payload, 
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)


def get_client_ip(request: Request) -> Optional[str]:
    """Get real client IP (handles proxies)"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None
