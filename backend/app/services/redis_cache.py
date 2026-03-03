"""Redis cache service."""
import json
import pickle
from typing import Any, Optional, Union
import redis.asyncio as redis

from app.config import settings


class RedisCache:
    """Redis cache manager."""
    
    _instance: Optional["RedisCache"] = None
    _client: Optional[redis.Redis] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Connect to Redis."""
        if self._client is None:
            self._client = redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                decode_responses=False  # For binary data
            )
        return self._client
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            self._client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self._client is None:
            await self.connect()
        data = await self._client.get(key)
        if data is None:
            return None
        try:
            return pickle.loads(data)
        except:
            return data.decode() if isinstance(data, bytes) else data
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ):
        """Set value in cache."""
        if self._client is None:
            await self.connect()
        
        if not isinstance(value, (str, bytes)):
            value = pickle.dumps(value)
        
        await self._client.set(key, value, ex=expire)
    
    async def delete(self, key: str):
        """Delete key from cache."""
        if self._client is None:
            await self.connect()
        await self._client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if self._client is None:
            await self.connect()
        return await self._client.exists(key) > 0
    
    async def expire(self, key: str, seconds: int):
        """Set expiration on key."""
        if self._client is None:
            await self.connect()
        await self._client.expire(key, seconds)
    
    async def zadd(self, key: str, mapping: dict):
        """Add to sorted set."""
        if self._client is None:
            await self.connect()
        await self._client.zadd(key, mapping)
    
    async def zremrangebyscore(self, key: str, min_score: float, max_score: float):
        """Remove from sorted set by score."""
        if self._client is None:
            await self.connect()
        await self._client.zremrangebyscore(key, min_score, max_score)
    
    async def zcard(self, key: str) -> int:
        """Get sorted set cardinality."""
        if self._client is None:
            await self.connect()
        return await self._client.zcard(key)
    
    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value from cache."""
        data = await self.get(key)
        if data is None:
            return None
        if isinstance(data, dict):
            return data
        try:
            return json.loads(data) if isinstance(data, str) else json.loads(data.decode())
        except:
            return None
    
    async def set_json(self, key: str, value: dict, expire: Optional[int] = None):
        """Set JSON value in cache."""
        await self.set(key, json.dumps(value), expire)


# Global cache instance
redis_cache = RedisCache()
redis_client = redis_cache  # Alias for compatibility
