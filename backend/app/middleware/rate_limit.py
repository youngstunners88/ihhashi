from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

def setup_rate_limiting(app):
    """Attach rate limiter to FastAPI app"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def auth_rate_limit(limit: str = "5/minute"):
    """Rate limiting decorator for auth endpoints"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

def api_rate_limit(limit: str = "100/minute"):
    """Rate limiting decorator for general API endpoints"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator
