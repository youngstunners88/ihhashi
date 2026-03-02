"""
Redis Pub/Sub Manager for horizontal WebSocket scaling.
"""
import asyncio
import json
import logging
from typing import Any, Awaitable, Callable, Dict, Optional

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class PubSubManager:
    """
    Manages Redis pub/sub for horizontal scaling of WebSocket connections.
    Messages are published to Redis and fanned out to all server instances.
    """
    
    _instance: Optional["PubSubManager"] = None
    _redis_client: Optional[redis.Redis] = None
    _pubsub: Optional[redis.client.PubSub] = None
    _subscribed_channels: set = set()
    _message_handlers: Dict[str, Callable[[dict], Awaitable[None]]] = {}
    _consumer_task: Optional[asyncio.Task] = None
    _running: bool = False
    
    @classmethod
    async def get_instance(cls) -> "PubSubManager":
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    async def initialize(cls) -> None:
        """Initialize Redis connection."""
        instance = await cls.get_instance()
        await instance._connect()
    
    @classmethod
    async def shutdown(cls) -> None:
        """Shutdown Redis connection."""
        if cls._instance:
            await cls._instance._disconnect()
            cls._instance = None
    
    async def _connect(self) -> None:
        """Establish Redis connection."""
        if self._redis_client is not None:
            return
        
        try:
            self._redis_client = redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
            self._pubsub = self._redis_client.pubsub()
            await self._redis_client.ping()
            logger.info("Redis pub/sub connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def _disconnect(self) -> None:
        """Close Redis connection."""
        self._running = False
        
        if self._consumer_task and not self._consumer_task.done():
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
        
        if self._pubsub:
            await self._pubsub.close()
            self._pubsub = None
        
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None
        
        logger.info("Redis pub/sub disconnected")
    
    @classmethod
    async def publish(cls, channel: str, message: dict) -> None:
        """
        Publish a message to a Redis channel.
        
        Args:
            channel: The channel to publish to
            message: The message to publish (will be JSON encoded)
        """
        instance = await cls.get_instance()
        
        if instance._redis_client is None:
            logger.error("Cannot publish: Redis not connected")
            return
        
        try:
            await instance._redis_client.publish(channel, json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to publish message to {channel}: {e}")
    
    @classmethod
    def register_handler(cls, channel: str, handler: Callable[[dict], Awaitable[None]]) -> None:
        """
        Register a handler for a specific channel.
        
        Args:
            channel: The channel to handle
            handler: Async function to handle messages
        """
        if cls._instance is None:
            cls._message_handlers[channel] = handler
        else:
            cls._instance._message_handlers[channel] = handler
    
    async def start_consumer(
        self,
        channels: list[str],
        message_handler: Optional[Callable[[str, dict], Awaitable[None]]] = None
    ) -> None:
        """
        Start the pub/sub consumer task.
        
        Args:
            channels: List of channels to subscribe to
            message_handler: Optional custom message handler
        """
        if self._running:
            logger.warning("Pub/sub consumer already running")
            return
        
        if self._pubsub is None:
            raise RuntimeError("Redis pub/sub not initialized")
        
        await self._pubsub.subscribe(*channels)
        self._subscribed_channels.update(channels)
        self._running = True
        
        self._consumer_task = asyncio.create_task(
            self._consume_messages(message_handler)
        )
        
        logger.info(f"Started pub/sub consumer for channels: {channels}")
    
    async def stop_consumer(self) -> None:
        """Stop the pub/sub consumer task."""
        self._running = False
        
        if self._consumer_task and not self._consumer_task.done():
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
        
        if self._pubsub:
            await self._pubsub.unsubscribe(*self._subscribed_channels)
            self._subscribed_channels.clear()
        
        logger.info("Pub/sub consumer stopped")
    
    async def _consume_messages(
        self,
        message_handler: Optional[Callable[[str, dict], Awaitable[None]]] = None
    ) -> None:
        """
        Consume messages from subscribed channels.
        
        Args:
            message_handler: Optional custom message handler
        """
        try:
            async for message in self._pubsub.listen():
                if not self._running:
                    break
                
                if message["type"] != "message":
                    continue
                
                channel = message["channel"]
                data = message["data"]
                
                try:
                    payload = json.loads(data)
                    
                    # Skip messages from the same instance
                    if payload.get("instance_id") == settings.INSTANCE_ID:
                        continue
                    
                    logger.debug(f"Received message on {channel}: {payload}")
                    
                    # Use custom handler if provided
                    if message_handler:
                        await message_handler(channel, payload)
                    # Otherwise use registered handler
                    elif channel in self._message_handlers:
                        await self._message_handlers[channel](payload)
                    else:
                        logger.warning(f"No handler for channel: {channel}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Pub/sub consumer cancelled")
            raise
        except Exception as e:
            logger.error(f"Pub/sub consumer error: {e}")
    
    @classmethod
    async def get_connection_info(cls) -> dict:
        """Get Redis connection information."""
        instance = cls._instance
        if instance is None or instance._redis_client is None:
            return {"status": "disconnected"}
        
        try:
            info = await instance._redis_client.info()
            return {
                "status": "connected",
                "version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


# Convenience function for publishing
async def publish_message(channel: str, message: dict) -> None:
    """Publish a message to a Redis channel."""
    await PubSubManager.publish(channel, message)
