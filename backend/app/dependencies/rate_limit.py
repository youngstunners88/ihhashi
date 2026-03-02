"""Rate limiting dependency using Redis."""
import time
from fastapi import HTTPException, Request
from app.services.redis_cache import redis_client


class RateLimiter:
    """Rate limiter using sliding window algorithm."""
    
    def __init__(self, requests: int, window: int):
        """
        Initialize rate limiter.
        
        Args:
            requests: Number of requests allowed
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
    
    async def is_allowed(self, key: str) -> bool:
        """Check if request is allowed."""
        now = time.time()
        window_start = now - self.window
        
        # Remove old entries
        await redis_client.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current = await redis_client.zcard(key)
        
        if current >= self.requests:
            return False
        
        # Add current request
        await redis_client.zadd(key, {str(now): now})
        await redis_client.expire(key, self.window)
        
        return True


# Rate limiter instances
rate_limit_general = RateLimiter(requests=100, window=60)  # 100 req/min
rate_limit_auth = RateLimiter(requests=5, window=60)  # 5 req/min for auth
rate_limit_api = RateLimiter(requests=1000, window=60)  # 1000 req/min for API


async def rate_limit(request: Request, limiter: RateLimiter = rate_limit_general):
    """Rate limiting dependency."""
    # Use IP address + path as key
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}:{request.url.path}"
    
    if not await limiter.is_allowed(key):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )


async def rate_limit_auth_endpoint(request: Request):
    """Strict rate limiting for auth endpoints."""
    await rate_limit(request, rate_limit_auth)
