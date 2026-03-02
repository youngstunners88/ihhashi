"""
WebSocket routes with Redis pub/sub fanout for horizontal scaling.
"""
import json
import logging
from typing import Dict, List, Optional, Set
from enum import Enum

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.security import HTTPBearer

from app.config import settings
from app.services.pubsub_manager import PubSubManager

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


class ConnectionType(str, Enum):
    """Types of WebSocket connections."""
    USER = "user"
    RIDER = "rider"
    ADMIN = "admin"
    RESTAURANT = "restaurant"


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
    
    async def connect(
        self,
        websocket: WebSocket,
        conn_type: ConnectionType,
        entity_id: str
    ) -> None:
        """Accept and store a WebSocket connection."""
        await websocket.accept()
        self.active_connections[conn_type][entity_id] = websocket
        self.connection_metadata[entity_id] = {
            "type": conn_type.value,
            "id": entity_id,
        }
        logger.info(f"WebSocket connected: {conn_type.value}={entity_id}")
    
    def disconnect(self, conn_type: ConnectionType, entity_id: str) -> None:
        """Remove a WebSocket connection."""
        if entity_id in self.active_connections[conn_type]:
            del self.active_connections[conn_type][entity_id]
        if entity_id in self.connection_metadata:
            del self.connection_metadata[entity_id]
        logger.info(f"WebSocket disconnected: {conn_type.value}={entity_id}")
    
    async def send_personal_message(self, message: dict, entity_id: str) -> bool:
        """Send message to a specific entity across all connection types."""
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


# Global connection manager for this instance
manager = ConnectionManager()


async def notify_order_update(order_id: str, event_type: str, data: dict) -> None:
    """
    Notify about order updates via Redis pub/sub for horizontal scaling.
    
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
    
    # Also notify local connections immediately
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
    
    Args:
        websocket: The WebSocket connection
        conn_type: Type of connection (user, rider, admin, restaurant)
        entity_id: Unique identifier for the entity
        token: Authentication token
    """
    # TODO: Implement proper token validation
    # if token:
    #     await validate_token(token)
    
    await manager.connect(websocket, conn_type, entity_id)
    
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
                    pass
                elif action == "location_update":
                    # Handle location update from rider
                    if conn_type == ConnectionType.RIDER:
                        # Process rider location update
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
        "total_connections": sum(manager.get_stats().values())
    }
