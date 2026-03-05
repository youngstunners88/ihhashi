"""
WebSocket routes for real-time order tracking with JWT authentication
SECURITY: Authentication required for all endpoints, input validation
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, List, Optional, Set
from datetime import datetime
from enum import Enum
import json
import asyncio
import jwt
import math

from app.database import get_collection
from app.core.config import settings

router = APIRouter()


# =============================================================================
# Constants for validation
# =============================================================================
MIN_LATITUDE = -90.0
MAX_LATITUDE = 90.0
MIN_LONGITUDE = -180.0
MAX_LONGITUDE = 180.0
MAX_SPEED = 200.0  # km/h - reasonable max for delivery vehicles
HEARTBEAT_INTERVAL = 30.0  # seconds
PONG_TIMEOUT = 10.0  # seconds to wait for pong response
MAX_RECONNECT_ATTEMPTS = 3


# =============================================================================
# WebSocket Event Types
# =============================================================================
class WebSocketEventType(str, Enum):
    # Order Events
    ORDER_CREATED = "order_created"
    ORDER_STATUS_UPDATED = "order_status_updated"
    ORDER_ASSIGNED = "order_assigned"
    ORDER_CANCELLED = "order_cancelled"
    
    # Driver Events
    DRIVER_LOCATION_UPDATE = "driver_location_update"
    DRIVER_STATUS_UPDATE = "driver_status_update"
    DRIVER_ASSIGNED = "driver_assigned"
    
    # Delivery Events
    DELIVERY_COMPLETED = "delivery_completed"
    DELIVERY_FAILED = "delivery_failed"
    ESTIMATED_ARRIVAL = "estimated_arrival"
    
    # Messaging Events
    NEW_MESSAGE = "new_message"
    MESSAGE_READ = "message_read"
    
    # System Events
    PING = "ping"
    PONG = "pong"
    HEARTBEAT = "heartbeat"
    AUTHENTICATED = "authenticated"
    ERROR = "error"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


# =============================================================================
# Room Types
# =============================================================================
class RoomType(str, Enum):
    ORDER = "order"
    DRIVER = "driver"
    MERCHANT = "merchant"
    USER = "user"
    ADMIN = "admin"


def validate_coordinates(lat: Optional[float], lng: Optional[float]) -> bool:
    """Validate latitude and longitude are within valid ranges"""
    if lat is None or lng is None:
        return False
    try:
        lat = float(lat)
        lng = float(lng)
        return MIN_LATITUDE <= lat <= MAX_LATITUDE and MIN_LONGITUDE <= lng <= MAX_LONGITUDE
    except (TypeError, ValueError):
        return False


def validate_location_data(location: dict) -> Optional[dict]:
    """Validate and sanitize location data from rider"""
    if not location:
        return None
    
    lat = location.get("latitude")
    lng = location.get("longitude")
    
    if not validate_coordinates(lat, lng):
        return None
    
    # Validate optional fields
    heading = location.get("heading")
    if heading is not None:
        try:
            heading = float(heading)
            if not (0 <= heading <= 360):
                heading = None
        except (TypeError, ValueError):
            heading = None
    
    speed = location.get("speed")
    if speed is not None:
        try:
            speed = float(speed)
            if speed < 0 or speed > MAX_SPEED:
                speed = None
        except (TypeError, ValueError):
            speed = None
    
    return {
        "latitude": float(lat),
        "longitude": float(lng),
        "heading": heading,
        "speed": speed,
        "last_updated": datetime.utcnow().isoformat()
    }


# =============================================================================
# WebSocket Connection Manager with Room Support
# =============================================================================
class ConnectionManager:
    """
    Manages WebSocket connections with room-based messaging support.
    Supports multiple room types: orders, drivers, merchants, users
    """
    
    def __init__(self):
        # Room-based connections: room_type -> room_id -> set of (websocket, metadata)
        self.rooms: Dict[str, Dict[str, Set[tuple]]] = {
            RoomType.ORDER: {},
            RoomType.DRIVER: {},
            RoomType.MERCHANT: {},
            RoomType.USER: {},
            RoomType.ADMIN: {},
        }
        
        # Track all active connections with their metadata
        self.connections: Dict[WebSocket, dict] = {}
        
        # Quick lookups for specific connection types
        self.driver_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, WebSocket] = {}
        self.merchant_connections: Dict[str, WebSocket] = {}
    
    async def connect(
        self, 
        websocket: WebSocket, 
        room_type: RoomType, 
        room_id: str,
        user_id: str,
        metadata: Optional[dict] = None
    ):
        """Connect a client to a specific room"""
        await websocket.accept()
        
        # Initialize room if not exists
        if room_id not in self.rooms[room_type]:
            self.rooms[room_type][room_id] = set()
        
        # Store connection metadata
        conn_metadata = {
            "user_id": user_id,
            "room_type": room_type,
            "room_id": room_id,
            "connected_at": datetime.utcnow().isoformat(),
            "last_ping": datetime.utcnow(),
            **(metadata or {})
        }
        
        self.rooms[room_type][room_id].add((websocket, conn_metadata))
        self.connections[websocket] = conn_metadata
        
        # Update quick lookup dictionaries
        if room_type == RoomType.DRIVER:
            self.driver_connections[room_id] = websocket
        elif room_type == RoomType.USER:
            self.user_connections[room_id] = websocket
        elif room_type == RoomType.MERCHANT:
            self.merchant_connections[room_id] = websocket
        
        # Send connection confirmation
        try:
            await websocket.send_json({
                "type": WebSocketEventType.CONNECTED,
                "room_type": room_type,
                "room_id": room_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        except:
            pass
    
    def disconnect(self, websocket: WebSocket):
        """Remove a connection from all rooms"""
        if websocket not in self.connections:
            return
        
        metadata = self.connections[websocket]
        room_type = metadata.get("room_type")
        room_id = metadata.get("room_id")
        user_id = metadata.get("user_id")
        
        # Remove from room
        if room_type and room_id and room_id in self.rooms.get(room_type, {}):
            self.rooms[room_type][room_id] = {
                (ws, meta) for ws, meta in self.rooms[room_type][room_id] 
                if ws != websocket
            }
            
            # Clean up empty rooms
            if not self.rooms[room_type][room_id]:
                del self.rooms[room_type][room_id]
        
        # Remove from quick lookups
        if room_type == RoomType.DRIVER and room_id in self.driver_connections:
            del self.driver_connections[room_id]
        elif room_type == RoomType.USER and room_id in self.user_connections:
            del self.user_connections[room_id]
        elif room_type == RoomType.MERCHANT and room_id in self.merchant_connections:
            del self.merchant_connections[room_id]
        
        # Remove from connections
        del self.connections[websocket]
    
    async def broadcast_to_room(
        self, 
        room_type: RoomType, 
        room_id: str, 
        message: dict,
        exclude: Optional[WebSocket] = None
    ):
        """Broadcast message to all connections in a room"""
        if room_id not in self.rooms.get(room_type, {}):
            return
        
        dead_connections = []
        
        for websocket, metadata in self.rooms[room_type][room_id]:
            if websocket == exclude:
                continue
            
            try:
                # Filter sensitive data based on connection type
                safe_message = self._filter_message(message, metadata)
                await websocket.send_json(safe_message)
            except Exception:
                dead_connections.append(websocket)
        
        # Clean up dead connections
        for ws in dead_connections:
            self.disconnect(ws)
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to a specific user"""
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_json(message)
            except:
                self.disconnect(self.user_connections[user_id])
    
    async def send_to_driver(self, driver_id: str, message: dict):
        """Send message to a specific driver"""
        if driver_id in self.driver_connections:
            try:
                await self.driver_connections[driver_id].send_json(message)
            except:
                self.disconnect(self.driver_connections[driver_id])
    
    async def send_to_merchant(self, merchant_id: str, message: dict):
        """Send message to a specific merchant"""
        if merchant_id in self.merchant_connections:
            try:
                await self.merchant_connections[merchant_id].send_json(message)
            except:
                self.disconnect(self.merchant_connections[merchant_id])
    
    def _filter_message(self, message: dict, metadata: dict) -> dict:
        """Filter sensitive data from message based on connection metadata"""
        filtered = message.copy()
        
        # Remove sensitive fields for non-owners
        is_owner = metadata.get("is_owner", False)
        if not is_owner:
            filtered.pop("recipient_phone", None)
            filtered.pop("delivery_instructions", None)
            filtered.pop("customer_notes", None)
        
        return filtered
    
    def update_ping(self, websocket: WebSocket):
        """Update last ping time for a connection"""
        if websocket in self.connections:
            self.connections[websocket]["last_ping"] = datetime.utcnow()
    
    def get_connection_count(self, room_type: Optional[RoomType] = None) -> int:
        """Get total connection count, optionally filtered by room type"""
        if room_type:
            return sum(len(conns) for conns in self.rooms[room_type].values())
        return len(self.connections)


# =============================================================================
# Global Connection Manager
# =============================================================================
manager = ConnectionManager()


# =============================================================================
# Authentication
# =============================================================================
async def verify_websocket_token(token: str) -> Optional[dict]:
    """
    Verify JWT token for WebSocket authentication.
    Returns user payload if valid, None otherwise.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def authenticate_websocket(websocket: WebSocket, token: Optional[str]) -> Optional[dict]:
    """
    Authenticate WebSocket connection.
    Returns user payload if authenticated, None otherwise.
    """
    if not token:
        await websocket.close(code=4001, reason="Authentication required. Pass ?token=xxx")
        return None
    
    payload = await verify_websocket_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return None
    
    return payload


# =============================================================================
# Heartbeat Manager
# =============================================================================
class HeartbeatManager:
    """Manages heartbeat/ping-pong for WebSocket connections"""
    
    def __init__(self):
        self.pending_pongs: Dict[WebSocket, asyncio.Task] = {}
    
    async def send_heartbeat(self, websocket: WebSocket) -> bool:
        """Send heartbeat and wait for pong. Returns True if pong received."""
        try:
            await websocket.send_json({
                "type": WebSocketEventType.HEARTBEAT,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Wait for pong with timeout
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=PONG_TIMEOUT
                )
                return data.get("type") == WebSocketEventType.PONG
            except asyncio.TimeoutError:
                return False
        except:
            return False
    
    def cancel_pending(self, websocket: WebSocket):
        """Cancel pending pong wait for a connection"""
        if websocket in self.pending_pongs:
            self.pending_pongs[websocket].cancel()
            del self.pending_pongs[websocket]


heartbeat_manager = HeartbeatManager()


# =============================================================================
# WebSocket Endpoints
# =============================================================================

@router.websocket("/ws")
async def general_websocket(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    General WebSocket endpoint for real-time updates.
    Clients can subscribe to multiple rooms after connection.
    """
    # Authenticate
    payload = await authenticate_websocket(websocket, token)
    if not payload:
        return
    
    user_id = payload.get("sub")
    user_role = payload.get("role", "customer")
    
    # Track subscribed rooms
    subscribed_rooms: List[tuple] = []
    
    try:
        await websocket.accept()
        
        # Send authentication confirmation
        await websocket.send_json({
            "type": WebSocketEventType.AUTHENTICATED,
            "user_id": user_id,
            "role": user_role,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=HEARTBEAT_INTERVAL
                )
                
                event_type = data.get("type")
                
                # Handle ping
                if event_type == WebSocketEventType.PING:
                    await websocket.send_json({
                        "type": WebSocketEventType.PONG,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                # Handle subscribe to room
                elif event_type == "subscribe":
                    room_type = data.get("room_type")
                    room_id = data.get("room_id")
                    
                    if room_type and room_id:
                        # Validate access
                        has_access = await validate_room_access(
                            user_id, user_role, room_type, room_id
                        )
                        
                        if has_access:
                            metadata = {"is_owner": data.get("is_owner", False)}
                            await manager.connect(
                                websocket, 
                                RoomType(room_type), 
                                room_id, 
                                user_id,
                                metadata
                            )
                            subscribed_rooms.append((room_type, room_id))
                            
                            await websocket.send_json({
                                "type": "subscribed",
                                "room_type": room_type,
                                "room_id": room_id
                            })
                        else:
                            await websocket.send_json({
                                "type": WebSocketEventType.ERROR,
                                "message": "Access denied to this room"
                            })
                
                # Handle unsubscribe from room
                elif event_type == "unsubscribe":
                    room_type = data.get("room_type")
                    room_id = data.get("room_id")
                    
                    if (room_type, room_id) in subscribed_rooms:
                        manager.disconnect(websocket)
                        subscribed_rooms.remove((room_type, room_id))
                        
                        await websocket.send_json({
                            "type": "unsubscribed",
                            "room_type": room_type,
                            "room_id": room_id
                        })
                
                # Handle message
                elif event_type == WebSocketEventType.NEW_MESSAGE:
                    await handle_chat_message(user_id, data)
                
            except asyncio.TimeoutError:
                # Send heartbeat
                pong_received = await heartbeat_manager.send_heartbeat(websocket)
                if not pong_received:
                    break
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Cleanup
        heartbeat_manager.cancel_pending(websocket)
        manager.disconnect(websocket)
        
        # Update user/driver status if needed
        await update_offline_status(user_id)


@router.websocket("/track/{order_id}")
async def track_order_websocket(
    websocket: WebSocket, 
    order_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time order tracking with JWT auth
    
    Clients connect to receive:
    - Order status updates
    - Rider location updates
    - Delivery estimates
    
    Authentication: Pass JWT token as query parameter ?token=xxx
    SECURITY: Token required - validates user has access to order
    """
    # Authenticate
    payload = await authenticate_websocket(websocket, token)
    if not payload:
        return
    
    user_id = payload.get("sub")
    
    # Verify user has access to this order
    orders_col = get_collection("orders")
    order = None
    
    try:
        order = await orders_col.find_one({"id": order_id})
    except:
        pass
    
    if not order:
        await websocket.close(code=4004, reason="Order not found")
        return
    
    # Check if user is buyer, rider, merchant, or admin
    is_owner = (
        order.get("buyer_id") == user_id or
        order.get("rider_id") == user_id or
        order.get("store_id") == user_id
    )
    
    # Check role for admin access
    user_role = payload.get("role")
    if not is_owner and user_role != "admin":
        await websocket.close(code=4003, reason="Access denied to this order")
        return
    
    # Connect to order room
    await manager.connect(
        websocket, 
        RoomType.ORDER, 
        order_id, 
        user_id,
        {"is_owner": is_owner, "order_status": order.get("status")}
    )
    
    try:
        # Send initial order status
        riders_col = get_collection("riders")
        
        initial_message = {
            "type": WebSocketEventType.CONNECTED,
            "event": "initial",
            "order_id": order_id,
            "status": order.get("status"),
            "created_at": order.get("created_at"),
            "rider_id": order.get("rider_id"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if order.get("rider_id"):
            rider = await riders_col.find_one({"id": order["rider_id"]})
            if rider and rider.get("current_location"):
                initial_message["rider_location"] = rider["current_location"]
                initial_message["rider_name"] = rider.get("full_name")
                initial_message["rider_phone"] = rider.get("phone") if is_owner else None
        
        await websocket.send_json(initial_message)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=HEARTBEAT_INTERVAL
                )
                
                event_type = data.get("type")
                
                # Handle ping/pong
                if event_type == WebSocketEventType.PING:
                    manager.update_ping(websocket)
                    await websocket.send_json({
                        "type": WebSocketEventType.PONG,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif event_type == "get_location":
                    # Client requests current rider location
                    if order.get("rider_id"):
                        rider = await riders_col.find_one({"id": order["rider_id"]})
                        if rider and rider.get("current_location"):
                            await websocket.send_json({
                                "type": WebSocketEventType.DRIVER_LOCATION_UPDATE,
                                "rider_location": rider["current_location"],
                                "timestamp": datetime.utcnow().isoformat()
                            })
                
                elif event_type == "get_status":
                    # Client requests current order status
                    current_order = await orders_col.find_one({"id": order_id})
                    if current_order:
                        await websocket.send_json({
                            "type": WebSocketEventType.ORDER_STATUS_UPDATED,
                            "order_id": order_id,
                            "status": current_order.get("status"),
                            "status_history": current_order.get("status_history", []),
                            "timestamp": datetime.utcnow().isoformat()
                        })
            
            except asyncio.TimeoutError:
                # Send heartbeat
                pong_received = await heartbeat_manager.send_heartbeat(websocket)
                if not pong_received:
                    break
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)


@router.websocket("/rider/{rider_id}")
async def rider_websocket(
    websocket: WebSocket, 
    rider_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for riders to send location updates with JWT auth
    
    Riders connect to:
    - Send their location updates
    - Receive new order notifications
    - Receive order status changes
    
    Authentication: Pass JWT token as query parameter ?token=xxx
    """
    # Authenticate
    payload = await authenticate_websocket(websocket, token)
    if not payload:
        return
    
    # Verify the token belongs to this rider
    token_user_id = payload.get("sub")
    if token_user_id != rider_id:
        await websocket.close(code=4003, reason="Unauthorized for this rider")
        return
    
    # Connect to driver room
    await manager.connect(
        websocket, 
        RoomType.DRIVER, 
        rider_id, 
        rider_id,
        {"status": "available"}
    )
    
    riders_col = get_collection("riders")
    
    try:
        # Update rider as online
        await riders_col.update_one(
            {"id": rider_id},
            {"$set": {"status": "available", "last_online": datetime.utcnow()}}
        )
        
        # Send connection confirmation
        await websocket.send_json({
            "type": WebSocketEventType.CONNECTED,
            "message": "Connected as rider",
            "rider_id": rider_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=HEARTBEAT_INTERVAL
                )
                
                event_type = data.get("type")
                
                if event_type == WebSocketEventType.DRIVER_LOCATION_UPDATE:
                    # SECURITY: Validate location data before storing
                    location = data.get("location", {})
                    validated_location = validate_location_data(location)
                    
                    if validated_location:
                        # Update rider location in database
                        await riders_col.update_one(
                            {"id": rider_id},
                            {"$set": {"current_location": validated_location}}
                        )
                        
                        # Broadcast to all orders this rider is delivering
                        orders_col = get_collection("orders")
                        active_orders = await orders_col.find({
                            "rider_id": rider_id,
                            "status": {"$in": ["picked_up", "in_transit"]}
                        }).to_list(length=10)
                        
                        for active_order in active_orders:
                            await manager.broadcast_to_room(
                                RoomType.ORDER,
                                active_order["id"],
                                {
                                    "type": WebSocketEventType.DRIVER_LOCATION_UPDATE,
                                    "order_id": active_order["id"],
                                    "rider_location": {
                                        "latitude": validated_location["latitude"],
                                        "longitude": validated_location["longitude"],
                                        "heading": validated_location.get("heading"),
                                        "speed": validated_location.get("speed"),
                                        "last_updated": validated_location["last_updated"]
                                    },
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                            )
                        
                        # Send confirmation
                        await websocket.send_json({
                            "type": "location_updated",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    else:
                        await websocket.send_json({
                            "type": WebSocketEventType.ERROR,
                            "message": "Invalid location data"
                        })
                
                elif event_type == WebSocketEventType.PING:
                    manager.update_ping(websocket)
                    await websocket.send_json({
                        "type": WebSocketEventType.PONG,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif event_type == WebSocketEventType.DRIVER_STATUS_UPDATE:
                    new_status = data.get("status")
                    if new_status in ["available", "busy", "offline", "break"]:
                        await riders_col.update_one(
                            {"id": rider_id},
                            {"$set": {"status": new_status}}
                        )
                        await websocket.send_json({
                            "type": "status_confirmed",
                            "status": new_status,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                
                elif event_type == "accept_order":
                    # Rider accepts an order
                    order_id = data.get("order_id")
                    if order_id:
                        await handle_order_accepted(rider_id, order_id)
                        await websocket.send_json({
                            "type": "order_accepted",
                            "order_id": order_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                
                elif event_type == "complete_delivery":
                    # Rider marks delivery as complete
                    order_id = data.get("order_id")
                    if order_id:
                        await handle_delivery_completed(rider_id, order_id)
                        await websocket.send_json({
                            "type": WebSocketEventType.DELIVERY_COMPLETED,
                            "order_id": order_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })
            
            except asyncio.TimeoutError:
                pong_received = await heartbeat_manager.send_heartbeat(websocket)
                if not pong_received:
                    break
    
    except WebSocketDisconnect:
        pass
    finally:
        # Update rider as offline
        await riders_col.update_one(
            {"id": rider_id},
            {"$set": {"status": "offline"}}
        )
        manager.disconnect(websocket)


@router.websocket("/merchant/{merchant_id}")
async def merchant_websocket(
    websocket: WebSocket,
    merchant_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for merchants to receive order notifications
    
    Merchants connect to receive:
    - New order notifications
    - Order status updates
    - Customer messages
    """
    # Authenticate
    payload = await authenticate_websocket(websocket, token)
    if not payload:
        return
    
    user_id = payload.get("sub")
    user_role = payload.get("role")
    
    # Verify access
    if user_id != merchant_id and user_role != "admin":
        await websocket.close(code=4003, reason="Unauthorized for this merchant")
        return
    
    # Connect to merchant room
    await manager.connect(
        websocket,
        RoomType.MERCHANT,
        merchant_id,
        user_id,
        {"is_owner": True}
    )
    
    try:
        await websocket.send_json({
            "type": WebSocketEventType.CONNECTED,
            "message": "Connected as merchant",
            "merchant_id": merchant_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=HEARTBEAT_INTERVAL
                )
                
                event_type = data.get("type")
                
                if event_type == WebSocketEventType.PING:
                    manager.update_ping(websocket)
                    await websocket.send_json({
                        "type": WebSocketEventType.PONG,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif event_type == WebSocketEventType.ORDER_STATUS_UPDATED:
                    # Merchant updates order status
                    order_id = data.get("order_id")
                    new_status = data.get("status")
                    if order_id and new_status:
                        await handle_order_status_update(merchant_id, order_id, new_status)
                
                elif event_type == WebSocketEventType.NEW_MESSAGE:
                    # Merchant sends message to customer
                    await handle_chat_message(user_id, data)
            
            except asyncio.TimeoutError:
                pong_received = await heartbeat_manager.send_heartbeat(websocket)
                if not pong_received:
                    break
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)


@router.websocket("/user/{user_id}")
async def user_websocket(
    websocket: WebSocket, 
    user_id: str,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for user notifications with JWT auth
    
    Users connect to receive:
    - Order status updates
    - Delivery notifications
    - Chat messages from rider/merchant
    
    Authentication: Pass JWT token as query parameter ?token=xxx
    """
    # Authenticate
    payload = await authenticate_websocket(websocket, token)
    if not payload:
        return
    
    # Verify the token belongs to this user
    token_user_id = payload.get("sub")
    if token_user_id != user_id:
        await websocket.close(code=4003, reason="Unauthorized for this user")
        return
    
    # Connect to user room
    await manager.connect(
        websocket,
        RoomType.USER,
        user_id,
        user_id
    )
    
    try:
        await websocket.send_json({
            "type": WebSocketEventType.CONNECTED,
            "message": "Connected for notifications",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=HEARTBEAT_INTERVAL
                )
                
                event_type = data.get("type")
                
                if event_type == WebSocketEventType.PING:
                    manager.update_ping(websocket)
                    await websocket.send_json({
                        "type": WebSocketEventType.PONG,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif event_type == WebSocketEventType.NEW_MESSAGE:
                    # User sends message
                    await handle_chat_message(user_id, data)
            
            except asyncio.TimeoutError:
                pong_received = await heartbeat_manager.send_heartbeat(websocket)
                if not pong_received:
                    break
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)


# =============================================================================
# Helper Functions
# =============================================================================

async def validate_room_access(
    user_id: str, 
    user_role: str, 
    room_type: str, 
    room_id: str
) -> bool:
    """Validate if user has access to a specific room"""
    if user_role == "admin":
        return True
    
    if room_type == RoomType.ORDER:
        orders_col = get_collection("orders")
        order = await orders_col.find_one({"id": room_id})
        if order:
            return (
                order.get("buyer_id") == user_id or
                order.get("rider_id") == user_id or
                order.get("store_id") == user_id
            )
    
    elif room_type == RoomType.DRIVER:
        return room_id == user_id
    
    elif room_type == RoomType.MERCHANT:
        return room_id == user_id
    
    elif room_type == RoomType.USER:
        return room_id == user_id
    
    return False


async def update_offline_status(user_id: str):
    """Update user/driver status when they disconnect"""
    # Update rider status if applicable
    riders_col = get_collection("riders")
    await riders_col.update_one(
        {"id": user_id},
        {"$set": {"status": "offline", "last_offline": datetime.utcnow()}}
    )


async def handle_order_accepted(rider_id: str, order_id: str):
    """Handle when a rider accepts an order"""
    orders_col = get_collection("orders")
    
    # Update order
    await orders_col.update_one(
        {"id": order_id},
        {
            "$set": {
                "rider_id": rider_id,
                "status": "confirmed",
                "confirmed_at": datetime.utcnow()
            },
            "$push": {
                "status_history": {
                    "status": "confirmed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "actor": rider_id
                }
            }
        }
    )
    
    # Notify order room
    await manager.broadcast_to_room(
        RoomType.ORDER,
        order_id,
        {
            "type": WebSocketEventType.DRIVER_ASSIGNED,
            "order_id": order_id,
            "rider_id": rider_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def handle_delivery_completed(rider_id: str, order_id: str):
    """Handle when a rider completes a delivery"""
    orders_col = get_collection("orders")
    
    # Update order
    await orders_col.update_one(
        {"id": order_id},
        {
            "$set": {
                "status": "delivered",
                "delivered_at": datetime.utcnow()
            },
            "$push": {
                "status_history": {
                    "status": "delivered",
                    "timestamp": datetime.utcnow().isoformat(),
                    "actor": rider_id
                }
            }
        }
    )
    
    # Notify order room
    await manager.broadcast_to_room(
        RoomType.ORDER,
        order_id,
        {
            "type": WebSocketEventType.DELIVERY_COMPLETED,
            "order_id": order_id,
            "rider_id": rider_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    # Get order details to notify user
    order = await orders_col.find_one({"id": order_id})
    if order:
        await manager.send_to_user(
            order.get("buyer_id"),
            {
                "type": WebSocketEventType.DELIVERY_COMPLETED,
                "order_id": order_id,
                "message": "Your order has been delivered!",
                "timestamp": datetime.utcnow().isoformat()
            }
        )


async def handle_order_status_update(merchant_id: str, order_id: str, new_status: str):
    """Handle merchant updating order status"""
    orders_col = get_collection("orders")
    
    # Update order
    await orders_col.update_one(
        {"id": order_id},
        {
            "$set": {"status": new_status},
            "$push": {
                "status_history": {
                    "status": new_status,
                    "timestamp": datetime.utcnow().isoformat(),
                    "actor": merchant_id
                }
            }
        }
    )
    
    # Notify order room
    await manager.broadcast_to_room(
        RoomType.ORDER,
        order_id,
        {
            "type": WebSocketEventType.ORDER_STATUS_UPDATED,
            "order_id": order_id,
            "status": new_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    # Notify user
    order = await orders_col.find_one({"id": order_id})
    if order:
        await manager.send_to_user(
            order.get("buyer_id"),
            {
                "type": WebSocketEventType.ORDER_STATUS_UPDATED,
                "order_id": order_id,
                "status": new_status,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


async def handle_chat_message(sender_id: str, data: dict):
    """Handle chat messages between users"""
    message_data = {
        "type": WebSocketEventType.NEW_MESSAGE,
        "sender_id": sender_id,
        "order_id": data.get("order_id"),
        "message": data.get("message"),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Send to order room
    order_id = data.get("order_id")
    if order_id:
        await manager.broadcast_to_room(
            RoomType.ORDER,
            order_id,
            message_data
        )


# =============================================================================
# Public API for other routes to send WebSocket messages
# =============================================================================

async def notify_order_update(order_id: str, update_type: str, data: dict):
    """
    Call this from other routes to notify connected clients of order updates
    """
    message = {
        "type": update_type,
        "order_id": order_id,
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }
    await manager.broadcast_to_room(RoomType.ORDER, order_id, message)


async def notify_order_created(order_id: str, order_data: dict):
    """Notify when a new order is created"""
    await manager.broadcast_to_room(
        RoomType.MERCHANT,
        order_data.get("store_id"),
        {
            "type": WebSocketEventType.ORDER_CREATED,
            "order_id": order_id,
            "order": order_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def notify_rider(rider_id: str, notification_type: str, data: dict):
    """Send notification to a rider"""
    await manager.send_to_driver(rider_id, {
        "type": notification_type,
        "timestamp": datetime.utcnow().isoformat(),
        **data
    })


async def notify_user(user_id: str, notification_type: str, data: dict):
    """Send notification to a user"""
    await manager.send_to_user(user_id, {
        "type": notification_type,
        "timestamp": datetime.utcnow().isoformat(),
        **data
    })


async def notify_merchant(merchant_id: str, notification_type: str, data: dict):
    """Send notification to a merchant"""
    await manager.send_to_merchant(merchant_id, {
        "type": notification_type,
        "timestamp": datetime.utcnow().isoformat(),
        **data
    })


async def broadcast_driver_location(order_id: str, location: dict, rider_id: str):
    """Broadcast driver location update to order room"""
    await manager.broadcast_to_room(
        RoomType.ORDER,
        order_id,
        {
            "type": WebSocketEventType.DRIVER_LOCATION_UPDATE,
            "order_id": order_id,
            "rider_id": rider_id,
            "rider_location": location,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
