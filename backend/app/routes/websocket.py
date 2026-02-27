"""
WebSocket routes for real-time order tracking with JWT authentication
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, List, Optional
from datetime import datetime
import json
import asyncio
import jwt

from app.database import get_collection
from app.core.config import settings

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # order_id -> list of connections watching this order
        self.order_connections: Dict[str, List[WebSocket]] = {}
        # rider_id -> connection (for rider location updates)
        self.rider_connections: Dict[str, WebSocket] = {}
        # user_id -> connection (for user notifications)
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect_order_tracker(self, websocket: WebSocket, order_id: str, user_id: str):
        """Connect a client to track an order"""
        await websocket.accept()
        if order_id not in self.order_connections:
            self.order_connections[order_id] = []
        self.order_connections[order_id].append((websocket, user_id))
    
    async def connect_rider(self, websocket: WebSocket, rider_id: str):
        """Connect a rider for location updates"""
        await websocket.accept()
        self.rider_connections[rider_id] = websocket
    
    async def connect_user(self, websocket: WebSocket, user_id: str):
        """Connect a user for notifications"""
        await websocket.accept()
        self.user_connections[user_id] = websocket
    
    def disconnect(self, websocket: WebSocket, order_id: str = None, rider_id: str = None, user_id: str = None):
        """Remove a connection"""
        if order_id and order_id in self.order_connections:
            self.order_connections[order_id] = [
                (ws, uid) for ws, uid in self.order_connections[order_id] if ws != websocket
            ]
        if rider_id and rider_id in self.rider_connections:
            if self.rider_connections[rider_id] == websocket:
                del self.rider_connections[rider_id]
        if user_id and user_id in self.user_connections:
            if self.user_connections[user_id] == websocket:
                del self.user_connections[user_id]
    
    async def broadcast_order_update(self, order_id: str, message: dict):
        """Broadcast update to all clients tracking an order"""
        if order_id in self.order_connections:
            dead_connections = []
            for connection in self.order_connections[order_id]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.append(connection)
            
            # Clean up dead connections
            for dc in dead_connections:
                self.order_connections[order_id].remove(dc)
    
    async def send_to_rider(self, rider_id: str, message: dict):
        """Send message to a specific rider"""
        if rider_id in self.rider_connections:
            try:
                await self.rider_connections[rider_id].send_json(message)
            except:
                del self.rider_connections[rider_id]
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to a specific user"""
        if user_id in self.user_connections:
            try:
                await self.user_connections[user_id].send_json(message)
            except:
                del self.user_connections[user_id]


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


# Global connection manager
manager = ConnectionManager()


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
    """
    # AUTH: Verify JWT token
    user_id = None
    if token:
        payload = await verify_websocket_token(token)
        if payload:
            user_id = payload.get("sub")
    
    # Accept connection (with or without auth - some updates are public)
    await manager.connect_order_tracker(websocket, order_id, user_id or "anonymous")
    
    try:
        # Send initial order status
        orders_col = get_collection("orders")
        riders_col = get_collection("riders")
        
        order = await orders_col.find_one({"id": order_id})
        if order:
            initial_message = {
                "type": "initial",
                "order_id": order_id,
                "status": order.get("status"),
                "created_at": order.get("created_at"),
                "rider_id": order.get("rider_id")
            }
            
            if order.get("rider_id"):
                rider = await riders_col.find_one({"id": order["rider_id"]})
                if rider and rider.get("current_location"):
                    initial_message["rider_location"] = rider["current_location"]
                    initial_message["rider_name"] = rider.get("full_name")
                    initial_message["rider_phone"] = rider.get("phone")
            
            await websocket.send_json(initial_message)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for any message from client (ping/pong or requests)
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=30.0
                )
                
                # Handle different message types
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                
                elif data.get("type") == "get_location":
                    # Client requests current rider location
                    order = await orders_col.find_one({"id": order_id})
                    if order and order.get("rider_id"):
                        rider = await riders_col.find_one({"id": order["rider_id"]})
                        if rider and rider.get("current_location"):
                            await websocket.send_json({
                                "type": "location_update",
                                "rider_location": rider["current_location"]
                            })
            
            except asyncio.TimeoutError:
                # Send heartbeat
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except:
                    break
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, order_id=order_id)


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
    # AUTH: Verify JWT token - riders MUST be authenticated
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return
    
    payload = await verify_websocket_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return
    
    # Verify the token belongs to this rider
    token_user_id = payload.get("sub")
    if token_user_id != rider_id:
        await websocket.close(code=4003, reason="Unauthorized for this rider")
        return
    
    await manager.connect_rider(websocket, rider_id)
    
    riders_col = get_collection("riders")
    
    try:
        # Update rider as online
        await riders_col.update_one(
            {"id": rider_id},
            {"$set": {"status": "available", "last_online": datetime.utcnow()}}
        )
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=30.0
                )
                
                if data.get("type") == "location_update":
                    # Update rider location in database
                    location = data.get("location", {})
                    await riders_col.update_one(
                        {"id": rider_id},
                        {"$set": {
                            "current_location": {
                                "latitude": location.get("latitude"),
                                "longitude": location.get("longitude"),
                                "heading": location.get("heading"),
                                "speed": location.get("speed"),
                                "last_updated": datetime.utcnow()
                            }
                        }}
                    )
                    
                    # Broadcast to all orders this rider is delivering
                    orders_col = get_collection("orders")
                    active_orders = await orders_col.find({
                        "rider_id": rider_id,
                        "status": {"$in": ["picked_up", "in_transit"]}
                    }).to_list(length=10)
                    
                    for order in active_orders:
                        await manager.broadcast_order_update(order["id"], {
                            "type": "location_update",
                            "rider_location": location
                        })
                
                elif data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                
                elif data.get("type") == "status_update":
                    # Rider changing their status
                    new_status = data.get("status")
                    if new_status in ["available", "busy", "offline", "break"]:
                        await riders_col.update_one(
                            {"id": rider_id},
                            {"$set": {"status": new_status}}
                        )
                        await websocket.send_json({
                            "type": "status_confirmed",
                            "status": new_status
                        })
            
            except asyncio.TimeoutError:
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except:
                    break
    
    except WebSocketDisconnect:
        pass
    finally:
        # Update rider as offline
        await riders_col.update_one(
            {"id": rider_id},
            {"$set": {"status": "offline"}}
        )
        manager.disconnect(websocket, rider_id=rider_id)


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
    # AUTH: Verify JWT token - users MUST be authenticated
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return
    
    payload = await verify_websocket_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return
    
    # Verify the token belongs to this user
    token_user_id = payload.get("sub")
    if token_user_id != user_id:
        await websocket.close(code=4003, reason="Unauthorized for this user")
        return
    
    await manager.connect_user(websocket, user_id)
    
    try:
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=60.0
                )
                
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            
            except asyncio.TimeoutError:
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except:
                    break
    
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, user_id=user_id)


# Helper function to broadcast order updates from other parts of the app
async def notify_order_update(order_id: str, update_type: str, data: dict):
    """
    Call this from other routes to notify connected clients of order updates
    """
    message = {
        "type": update_type,
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }
    await manager.broadcast_order_update(order_id, message)


async def notify_rider(rider_id: str, notification_type: str, data: dict):
    """
    Send notification to a rider
    """
    await manager.send_to_rider(rider_id, {
        "type": notification_type,
        "timestamp": datetime.utcnow().isoformat(),
        **data
    })


async def notify_user(user_id: str, notification_type: str, data: dict):
    """
    Send notification to a user
    """
    await manager.send_to_user(user_id, {
        "type": notification_type,
        "timestamp": datetime.utcnow().isoformat(),
        **data
    })
