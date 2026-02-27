"""
Redis client for caching, rate limiting, and token blacklist
"""
import redis.asyncio as redis
from typing import Optional, Any
import json
from datetime import timedelta

from app.config import settings


class RedisClient:
    """Async Redis client for various caching and session needs"""
    
    _pool: Optional[redis.ConnectionPool] = None
    _client: Optional[redis.Redis] = None
    
    @classmethod
    async def get_client(cls) -> redis.Redis:
        """Get or create Redis client"""
        if cls._client is None:
            cls._pool = redis.ConnectionPool.from_url(
                settings.redis_url,
                decode_responses=True,
                max_connections=50
            )
            cls._client = redis.Redis(connection_pool=cls._pool)
        return cls._client
    
    @classmethod
    async def close(cls):
        """Close Redis connection"""
        if cls._client:
            await cls._client.close()
            cls._client = None
        if cls._pool:
            await cls._pool.disconnect()
            cls._pool = None


class TokenBlacklist:
    """Redis-based token blacklist for logout/revocation"""
    
    PREFIX = "blacklist:"
    
    @classmethod
    async def add(cls, token: str, expires_in_seconds: int = 86400 * 7):
        """
        Add token to blacklist.
        
        Args:
            token: JWT token to blacklist
            expires_in_seconds: How long to keep in blacklist (default 7 days)
        """
        client = await RedisClient.get_client()
        key = f"{cls.PREFIX}{token}"
        await client.setex(key, expires_in_seconds, "1")
    
    @classmethod
    async def is_blacklisted(cls, token: str) -> bool:
        """Check if token is blacklisted"""
        client = await RedisClient.get_client()
        key = f"{cls.PREFIX}{token}"
        return await client.exists(key) > 0
    
    @classmethod
    async def remove(cls, token: str):
        """Remove token from blacklist (rarely needed)"""
        client = await RedisClient.get_client()
        key = f"{cls.PREFIX}{token}"
        await client.delete(key)


class CacheManager:
    """Redis cache manager for frequently accessed data"""
    
    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        """Get cached value"""
        client = await RedisClient.get_client()
        value = await client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    @classmethod
    async def set(cls, key: str, value: Any, ttl_seconds: int = 300):
        """Set cached value with TTL"""
        client = await RedisClient.get_client()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await client.setex(key, ttl_seconds, value)
    
    @classmethod
    async def delete(cls, key: str):
        """Delete cached value"""
        client = await RedisClient.get_client()
        await client.delete(key)
    
    @classmethod
    async def delete_pattern(cls, pattern: str):
        """Delete all keys matching pattern"""
        client = await RedisClient.get_client()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)


class RiderLocationCache:
    """Cache for real-time rider locations"""
    
    PREFIX = "rider:location:"
    TTL = 300  # 5 minutes
    
    @classmethod
    async def update(cls, rider_id: str, lat: float, lng: float, heading: float = None):
        """Update rider location"""
        client = await RedisClient.get_client()
        key = f"{cls.PREFIX}{rider_id}"
        data = {"lat": lat, "lng": lng, "heading": heading}
        await client.setex(key, cls.TTL, json.dumps(data))
    
    @classmethod
    async def get(cls, rider_id: str) -> Optional[dict]:
        """Get rider location"""
        client = await RedisClient.get_client()
        key = f"{cls.PREFIX}{rider_id}"
        data = await client.get(key)
        if data:
            return json.loads(data)
        return None
    
    @classmethod
    async def find_nearby(cls, lat: float, lng: float, radius_km: float = 5.0):
        """Find nearby riders using Redis geospatial (requires Redis 3.2+)"""
        client = await RedisClient.get_client()
        # This would use GEORADIUS in production
        # For now, return empty list - implement with proper geo index
        return []


class PubSubManager:
    """Redis Pub/Sub for WebSocket scaling"""
    
    CHANNEL_ORDER_UPDATES = "order_updates"
    CHANNEL_RIDER_UPDATES = "rider_updates"
    CHANNEL_USER_NOTIFICATIONS = "user_notifications"
    
    @classmethod
    async def publish(cls, channel: str, message: dict):
        """Publish message to channel"""
        client = await RedisClient.get_client()
        await client.publish(channel, json.dumps(message))
    
    @classmethod
    async def subscribe(cls, channel: str):
        """Subscribe to channel - returns pubsub object"""
        client = await RedisClient.get_client()
        pubsub = client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub
    
    @classmethod
    async def broadcast_order_update(cls, order_id: str, update_type: str, data: dict):
        """Broadcast order update to all instances"""
        await cls.publish(cls.CHANNEL_ORDER_UPDATES, {
            "order_id": order_id,
            "type": update_type,
            "data": data
        })
    
    @classmethod
    async def broadcast_rider_location(cls, rider_id: str, location: dict):
        """Broadcast rider location update"""
        await cls.publish(cls.CHANNEL_RIDER_UPDATES, {
            "rider_id": rider_id,
            "location": location
        })


# Convenience functions
async def get_redis():
    """Get Redis client"""
    return await RedisClient.get_client()


async def close_redis():
    """Close Redis connection"""
    await RedisClient.close()


# Missing functions expected by app/core/__init__.py

async def init_redis():
    """Initialize Redis connection"""
    return await RedisClient.get_client()


async def cache_get(key: str) -> Optional[Any]:
    """Get cached value"""
    return await CacheManager.get(key)


async def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> bool:
    """Set cached value with TTL"""
    await CacheManager.set(key, value, ttl_seconds)
    return True


async def cache_delete(key: str) -> bool:
    """Delete cached value"""
    await CacheManager.delete(key)
    return True


async def cache_exists(key: str) -> bool:
    """Check if key exists in cache"""
    client = await RedisClient.get_client()
    return await client.exists(key) > 0


class LockManager:
    """Distributed lock manager using Redis"""
    
    @classmethod
    async def acquire(cls, lock_name: str, timeout_seconds: int = 10) -> bool:
        """Acquire a distributed lock"""
        client = await RedisClient.get_client()
        key = f"lock:{lock_name}"
        result = await client.set(key, "1", nx=True, ex=timeout_seconds)
        return result
    
    @classmethod
    async def release(cls, lock_name: str) -> bool:
        """Release a distributed lock"""
        client = await RedisClient.get_client()
        key = f"lock:{lock_name}"
        await client.delete(key)
        return True


async def acquire_lock(lock_name: str, timeout_seconds: int = 10) -> bool:
    """Acquire a distributed lock"""
    return await LockManager.acquire(lock_name, timeout_seconds)


async def release_lock(lock_name: str) -> bool:
    """Release a distributed lock"""
    return await LockManager.release(lock_name)


async def publish_message(channel: str, message: dict) -> int:
    """Publish message to a channel"""
    return await PubSubManager.publish(channel, message)


async def subscribe_channel(channel: str):
    """Subscribe to a channel"""
    return await PubSubManager.subscribe(channel)


async def unsubscribe_channel(pubsub, channel: str):
    """Unsubscribe from a channel"""
    await pubsub.unsubscribe(channel)


async def publish_delivery_update(delivery_id: str, update_type: str, data: dict):
    """Publish delivery update"""
    await PubSubManager.broadcast_order_update(delivery_id, update_type, data)


async def publish_rider_location(rider_id: str, location: dict):
    """Publish rider location update"""
    await PubSubManager.broadcast_rider_location(rider_id, location)


async def publish_order_update(order_id: str, update_type: str, data: dict):
    """Publish order update"""
    await PubSubManager.broadcast_order_update(order_id, update_type, data)