"""
WebSocket routes with Redis pub/sub fanout for horizontal scaling.
Includes JWT authentication verification and connection rate limiting.
"""
import json
import logging
import time
from typing import Dict, List, Optional, Set
from enum import Enum
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status, HTTPException
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

from app.config import settings
from app.services.pubsub_manager import PubSubManager
from app.services.redis_cache import redis_cache

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


class ConnectionType(str, Enum):
    """Types of WebSocket connections."""
    USER = "user"
    RIDER = "rider"
    ADMIN = "admin"
    RESTAURANT = "restaurant"


class WebSocketRateLimiter:
    """Rate limiter for WebSocket connections per user."""
    
    def __init__(self, max_connections: int = 5, window_seconds: int = 60):
        self.max_connections = max_connections
        self.window_seconds = window_seconds
    
    async def is_allowed(self, user_id: str) -> bool:
        """Check if user can establish new WebSocket connection."""
        key = f"ws_rate_limit:{user_id}"
        now = time.time()
        window_start = now - self.window_seconds
        
        # Get current connection attempts
        attempts = await redis_cache.get(key) or []
        
        # Filter to window
        attempts = [t for t in attempts if t > window_start]
        
        if len(attempts) >= self.max_connections:
            return False
        
        # Add current attempt
        attempts.append(now)
        await redis_cache.set(key, attempts, expire=self.window_seconds)
        
        return True
    
    async def record_connection(self, user_id: str):
        """Record active connection for rate limiting."""
        key = f"ws_active:{user_id}"
        count = await redis_cache.get(key) or 0
        await redis_cache.set(key, count + 1, expire=3600)
    
    async def record_disconnection(self, user_id: str):
        """Record disconnection."""
        key = f"ws_active:{user_id}"
        count = await redis_cache.get(key) or 0
        if count > 0:
            await redis_cache.set(key, count - 1, expire=3600)
    
    async def get_active_count(self, user_id: str) -> int:
        """Get number of active connections for user."""
        key = f"ws_active:{user_id}"
        return await redis_cache.get(key) or 0


# Global rate limiter instance
ws_rate_limiter = WebSocketRateLimiter(max_connections=5, window_seconds=60)


class ConnectionManager:
    """
    Manages WebSocket connections for local instance.
    For horizontal scaling, messages are fanned out via Redis pub/sub.
    """
    
    def __init__(self):
        # Local connections: {connection_type: {entity_id: WebSocket}}
        self.active_connections: Dict[ConnectionType, Dict[str, WebSocket]] = {
            ConnectionType.USER: {},
            ConnectionType.RIDER: {},
            ConnectionType.ADMIN: {},
            ConnectionType.RESTAURANT: {},
        }
        # Track connection metadata
        self.connection_metadata: Dict[str, dict] = {}
        # Track authenticated users
        self.authenticated_users: Dict[str, dict] = {}
    
    async def connect(
        self,
        websocket: WebSocket,
        conn_type: ConnectionType,
        entity_id: str,
        user_data: dict
    ) -> None:
        """Accept and store a WebSocket connection."""
        await websocket.accept()
        self.active_connections[conn_type][entity_id] = websocket
        self.connection_metadata[entity_id] = {
            "type": conn_type.value,
            "id": entity_id,
            "connected_at": datetime.utcnow().isoformat(),
        }
        self.authenticated_users[entity_id] = user_data
        
        # Record for rate limiting
        await ws_rate_limiter.record_connection(entity_id)
        
        logger.info(f"WebSocket connected: {conn_type.value}={entity_id}")
        
        # Send auth success message
        await websocket.send_json({
            "type": "auth_success",
            "entity_id": entity_id,
            "entity_type": conn_type.value
        })
    
    def disconnect(self, conn_type: ConnectionType, entity_id: str) -> None:
        """Remove a WebSocket connection."""
        if entity_id in self.active_connections[conn_type]:
            del self.active_connections[conn_type][entity_id]
        if entity_id in self.connection_metadata:
            del self.connection_metadata[entity_id]
        if entity_id in self.authenticated_users:
            del self.authenticated_users[entity_id]
        
        # Record disconnection for rate limiting
        import asyncio
        asyncio.create_task(ws_rate_limiter.record_disconnection(entity_id))
        
        logger.info(f"WebSocket disconnected: {conn_type.value}={entity_id}")
    
    def is_authenticated(self, entity_id: str) -> bool:
        """Check if entity is authenticated."""
        return entity_id in self.authenticated_users
    
    async def send_personal_message(self, message: dict, entity_id: str) -> bool:
        """Send message to a specific entity across all connection types."""
        # Security check: Only send to authenticated users
        if not self.is_authenticated(entity_id):
            logger.warning(f"Attempted to send message to unauthenticated user: {entity_id}")
            return False
        
        for conn_type in ConnectionType:
            if entity_id in self.active_connections[conn_type]:
                try:
                    websocket = self.active_connections[conn_type][entity_id]
                    await websocket.send_json(message)
                    return True
                except Exception as e:
                    logger.error(f"Error sending message to {entity_id}: {e}")
        return False
    
    async def broadcast_to_type(self, message: dict, conn_type: ConnectionType) -> int:
        """Broadcast message to all connections of a specific type."""
        sent_count = 0
        disconnected = []
        
        for entity_id, websocket in self.active_connections[conn_type].items():
            # Security check: Only send to authenticated users
            if not self.is_authenticated(entity_id):
                continue
            
            try:
                await websocket.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.error(f"Error broadcasting to {entity_id}: {e}")
                disconnected.append(entity_id)
        
        # Clean up disconnected clients
        for entity_id in disconnected:
            self.disconnect(conn_type, entity_id)
        
        return sent_count
    
    def get_stats(self) -> dict:
        """Get connection statistics."""
        return {
            conn_type.value: len(connections)
            for conn_type, connections in self.active_connections.items()
        }
    
    def get_authenticated_count(self) -> int:
        """Get count of authenticated connections."""
        return len(self.authenticated_users)


# Global connection manager for this instance
manager = ConnectionManager()


async def verify_websocket_token(token: str, expected_entity_id: str, expected_type: ConnectionType) -> dict:
    """
    Verify JWT token for WebSocket connection.
    
    Args:
        token: JWT token from client
        expected_entity_id: Entity ID from URL path
        expected_type: Expected connection type
        
    Returns:
        Decoded token data
        
    Raises:
        HTTPException: If token is invalid or mismatched
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        
        if user_id is None:
            raise credentials_exception
        
        # Verify entity ID matches token
        if user_id != expected_entity_id:
            logger.warning(f"Entity ID mismatch: token={user_id}, path={expected_entity_id}")
            raise credentials_exception
        
        # Verify user type matches connection type
        if user_type and user_type != expected_type.value:
            logger.warning(f"User type mismatch: token={user_type}, expected={expected_type.value}")
            raise credentials_exception
        
        return payload
        
    except JWTError:
        raise credentials_exception


async def notify_order_update(order_id: str, event_type: str, data: dict) -> None:
    """
    Notify about order updates via Redis pub/sub for horizontal scaling.
    Only authenticated users receive notifications.
    
    Args:
        order_id: The order ID
        event_type: Type of order event (created, updated, assigned, etc.)
        data: Event payload
    """
    message = {
        "type": "order_update",
        "order_id": order_id,
        "event": event_type,
        "data": data,
        "instance_id": settings.INSTANCE_ID,
    }
    
    # Publish to Redis for other instances
    await PubSubManager.publish(settings.PUBSUB_ORDER_CHANNEL, message)
    
    # Also notify local connections immediately (only authenticated)
    await _handle_order_update_locally(message)
    
    logger.debug(f"Order update published: {order_id} - {event_type}")


async def notify_rider(rider_id: str, event_type: str, data: dict) -> None:
    """
    Notify a rider via Redis pub/sub for horizontal scaling.
    
    Args:
        rider_id: The rider ID
        event_type: Type of rider event (new_order, location_update, etc.)
        data: Event payload
    """
    message = {
        "type": "rider_notification",
        "rider_id": rider_id,
        "event": event_type,
        "data": data,
        "instance_id": settings.INSTANCE_ID,
    }
    
    # Publish to Redis for other instances
    await PubSubManager.publish(settings.PUBSUB_RIDER_CHANNEL, message)
    
    # Also notify local connections immediately
    await _handle_rider_notification_locally(message)
    
    logger.debug(f"Rider notification published: {rider_id} - {event_type}")


async def notify_user(user_id: str, event_type: str, data: dict) -> None:
    """
    Notify a user via Redis pub/sub for horizontal scaling.
    
    Args:
        user_id: The user ID
        event_type: Type of user event (order_status, promotion, etc.)
        data: Event payload
    """
    message = {
        "type": "user_notification",
        "user_id": user_id,
        "event": event_type,
        "data": data,
        "instance_id": settings.INSTANCE_ID,
    }
    
    # Publish to Redis for other instances
    await PubSubManager.publish(settings.PUBSUB_USER_CHANNEL, message)
    
    # Also notify local connections immediately
    await _handle_user_notification_locally(message)
    
    logger.debug(f"User notification published: {user_id} - {event_type}")


# Local message handlers (called both for local and pubsub-received messages)
async def _handle_order_update_locally(message: dict) -> None:
    """Handle order update message locally."""
    # Notify connected users about their order
    user_id = message["data"].get("user_id")
    rider_id = message["data"].get("rider_id")
    restaurant_id = message["data"].get("restaurant_id")
    
    if user_id:
        await manager.send_personal_message(message, user_id)
    if rider_id:
        await manager.send_personal_message(message, rider_id)
    if restaurant_id:
        await manager.send_personal_message(message, restaurant_id)


async def _handle_rider_notification_locally(message: dict) -> None:
    """Handle rider notification locally."""
    rider_id = message.get("rider_id")
    if rider_id:
        await manager.send_personal_message(message, rider_id)


async def _handle_user_notification_locally(message: dict) -> None:
    """Handle user notification locally."""
    user_id = message.get("user_id")
    if user_id:
        await manager.send_personal_message(message, user_id)


# Message handlers registry for pubsub consumer
PUBSUB_HANDLERS = {
    settings.PUBSUB_ORDER_CHANNEL: _handle_order_update_locally,
    settings.PUBSUB_RIDER_CHANNEL: _handle_rider_notification_locally,
    settings.PUBSUB_USER_CHANNEL: _handle_user_notification_locally,
}


@router.websocket("/ws/{conn_type}/{entity_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conn_type: ConnectionType,
    entity_id: str,
    token: Optional[str] = None
):
    """
    WebSocket endpoint for real-time updates.
    Requires valid JWT token for authentication.
    Implements connection rate limiting.
    
    Args:
        websocket: The WebSocket connection
        conn_type: Type of connection (user, rider, admin, restaurant)
        entity_id: Unique identifier for the entity
        token: Authentication token (required)
    """
    # Check rate limiting
    if not await ws_rate_limiter.is_allowed(entity_id):
        logger.warning(f"Rate limit exceeded for entity: {entity_id}")
        await websocket.close(code=1008, reason="Rate limit exceeded")
        return
    
    # Verify token is provided
    if not token:
        logger.warning(f"WebSocket connection attempt without token: {entity_id}")
        await websocket.close(code=1008, reason="Authentication required")
        return
    
    # Verify JWT token
    try:
        user_data = await verify_websocket_token(token, entity_id, conn_type)
    except HTTPException:
        logger.warning(f"Invalid token for WebSocket connection: {entity_id}")
        await websocket.close(code=1008, reason="Invalid authentication")
        return
    
    # Accept connection
    await manager.connect(websocket, conn_type, entity_id, user_data)
    
    try:
        while True:
            # Receive and process client messages
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "ping":
                    await websocket.send_json({"type": "pong"})
                elif action == "subscribe_order":
                    # Client subscribing to order updates
                    # Could add order-specific auth checks here
                    pass
                elif action == "location_update":
                    # Handle location update from rider
                    if conn_type == ConnectionType.RIDER:
                        # Process rider location update
                        # TODO: Add location update logic
                        pass
                else:
                    logger.warning(f"Unknown action: {action}")
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(conn_type, entity_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(conn_type, entity_id)


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return {
        "instance_id": settings.INSTANCE_ID,
        "connections": manager.get_stats(),
        "authenticated_connections": manager.get_authenticated_count(),
        "total_connections": sum(manager.get_stats().values())
    }
