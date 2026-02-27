from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings

# Redis-backed rate limiter for production scaling
# Falls back to in-memory if Redis is not available
def get_storage_uri():
    """Get Redis storage URI for distributed rate limiting"""
    if settings.redis_url:
        return settings.redis_url
    return None  # Falls back to in-memory

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=get_storage_uri(),
    enabled=True
)

def setup_rate_limiting(app):
    """Attach rate limiter to FastAPI app"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def auth_rate_limit(limit: str = "5/minute"):
    """Rate limiting decorator for auth endpoints (stricter)"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

def api_rate_limit(limit: str = "100/minute"):
    """Rate limiting decorator for general API endpoints"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

def payment_rate_limit(limit: str = "10/minute"):
    """Rate limiting decorator for payment endpoints (moderate)"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

def webhook_rate_limit(limit: str = "100/minute"):
    """Rate limiting decorator for webhook endpoints (allow high volume from trusted sources)"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator
