"""
Order Service with atomic state transitions and audit logging.
"""
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from motor.motor_asyncio import AsyncIOMotorClientSession

from app.config import settings
from app.database import get_db
from app.services.redis_cache import redis_cache
from app.routes.websocket import notify_order_update

logger = logging.getLogger(__name__)


class OrderStatus(str, Enum):
    """Order status enum with valid transitions."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


# Valid state transitions map
VALID_TRANSITIONS = {
    OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.CANCELLED],
    OrderStatus.PREPARING: [OrderStatus.READY, OrderStatus.CANCELLED],
    OrderStatus.READY: [OrderStatus.PICKED_UP, OrderStatus.CANCELLED],
    OrderStatus.PICKED_UP: [OrderStatus.IN_TRANSIT],
    OrderStatus.IN_TRANSIT: [OrderStatus.DELIVERED],
    OrderStatus.DELIVERED: [],  # Terminal state
    OrderStatus.CANCELLED: [],  # Terminal state
}


@dataclass
class StatusTransition:
    """Status transition data."""
    from_status: str
    to_status: str
    timestamp: datetime
    actor_id: str
    actor_type: str
    reason: Optional[str] = None


class OrderService:
    """Order service with atomic operations and audit logging."""
    
    @staticmethod
    def is_valid_transition(from_status: str, to_status: str) -> bool:
        """Check if status transition is valid."""
        try:
            current = OrderStatus(from_status)
            next_status = OrderStatus(to_status)
            return next_status in VALID_TRANSITIONS.get(current, [])
        except ValueError:
            return False
    
    @staticmethod
    async def log_status_change(
        order_id: str,
        transition: StatusTransition,
        session: Optional[AsyncIOMotorClientSession] = None
    ):
        """Log status change to audit collection."""
        db = get_db()
        
        audit_entry = {
            "order_id": order_id,
            "from_status": transition.from_status,
            "to_status": transition.to_status,
            "timestamp": transition.timestamp,
            "actor_id": transition.actor_id,
            "actor_type": transition.actor_type,
            "reason": transition.reason,
            "instance_id": settings.INSTANCE_ID,
        }
        
        await db.order_audit_logs.insert_one(audit_entry, session=session)
        
        # Also add to order's status history
        await db.orders.update_one(
            {"_id": order_id},
            {
                "$push": {
                    "status_history": {
                        "from": transition.from_status,
                        "to": transition.to_status,
                        "timestamp": transition.timestamp,
                        "actor_id": transition.actor_id,
                        "actor_type": transition.actor_type,
                        "reason": transition.reason,
                    }
                }
            },
            session=session
        )
    
    @classmethod
    async def update_order_status(
        cls,
        order_id: str,
        new_status: str,
        actor_id: str,
        actor_type: str,
        reason: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Update order status with atomic check and audit logging.
        
        Returns:
            Tuple of (success, message)
        """
        db = get_db()
        
        # Start transaction session
        async with await db.client.start_session() as session:
            try:
                with session.start_transaction():
                    # Get current order with lock
                    order = await db.orders.find_one(
                        {"_id": order_id},
                        session=session
                    )
                    
                    if not order:
                        return False, "Order not found"
                    
                    current_status = order.get("status")
                    
                    # Validate transition
                    if not cls.is_valid_transition(current_status, new_status):
                        return False, (
                            f"Invalid status transition: {current_status} -> {new_status}. "
                            f"Valid transitions from {current_status}: "
                            f"{[s.value for s in VALID_TRANSITIONS.get(OrderStatus(current_status), [])]}"
                        )
                    
                    # Perform atomic update
                    result = await db.orders.update_one(
                        {
                            "_id": order_id,
                            "status": current_status  # Ensure status hasn't changed
                        },
                        {
                            "$set": {
                                "status": new_status,
                                "updated_at": datetime.utcnow(),
                                "status_updated_at": datetime.utcnow(),
                                "status_updated_by": actor_id,
                            }
                        },
                        session=session
                    )
                    
                    if result.modified_count == 0:
                        # Another process changed the status
                        return False, "Order status changed by another process. Please retry."
                    
                    # Log the status change
                    transition = StatusTransition(
                        from_status=current_status,
                        to_status=new_status,
                        timestamp=datetime.utcnow(),
                        actor_id=actor_id,
                        actor_type=actor_type,
                        reason=reason
                    )
                    
                    await cls.log_status_change(order_id, transition, session)
                    
                    # Invalidate cache
                    await redis_cache.delete(f"order:{order_id}")
                    
                    # Send WebSocket notification
                    await notify_order_update(
                        order_id=order_id,
                        event_type="status_changed",
                        data={
                            "order_id": order_id,
                            "old_status": current_status,
                            "new_status": new_status,
                            "updated_by": actor_id,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    )
                    
                    logger.info(
                        f"Order {order_id} status updated: {current_status} -> {new_status} "
                        f"by {actor_type}:{actor_id}"
                    )
                    
                    return True, "Status updated successfully"
                    
            except Exception as e:
                logger.error(f"Failed to update order status: {e}")
                return False, f"Transaction failed: {str(e)}"
    
    @classmethod
    async def assign_rider(
        cls,
        order_id: str,
        rider_id: str,
        assigned_by: str
    ) -> Tuple[bool, str]:
        """
        Atomically assign rider to order.
        Uses find_one_and_update to prevent race conditions.
        
        Returns:
            Tuple of (success, message)
        """
        db = get_db()
        
        async with await db.client.start_session() as session:
            try:
                with session.start_transaction():
                    # Atomically check and update
                    order = await db.orders.find_one_and_update(
                        {
                            "_id": order_id,
                            "rider_id": None,  # Ensure no rider assigned
                            "status": {"$in": ["confirmed", "preparing", "ready"]}  # Valid states for assignment
                        },
                        {
                            "$set": {
                                "rider_id": rider_id,
                                "rider_assigned_at": datetime.utcnow(),
                                "rider_assigned_by": assigned_by,
                                "updated_at": datetime.utcnow(),
                                "status": "picked_up" if (await db.orders.find_one({"_id": order_id})).get("status") == "ready" else None
                            }
                        },
                        session=session,
                        return_document=True
                    )
                    
                    if not order:
                        # Check why assignment failed
                        existing = await db.orders.find_one(
                            {"_id": order_id},
                            session=session
                        )
                        if not existing:
                            return False, "Order not found"
                        if existing.get("rider_id"):
                            return False, f"Order already assigned to rider {existing['rider_id']}"
                        return False, f"Order status {existing.get('status')} does not allow rider assignment"
                    
                    # Log the assignment
                    transition = StatusTransition(
                        from_status=order.get("status", "unknown"),
                        to_status="picked_up" if order.get("status") == "ready" else order.get("status"),
                        timestamp=datetime.utcnow(),
                        actor_id=assigned_by,
                        actor_type="system",
                        reason=f"Rider {rider_id} assigned"
                    )
                    
                    await cls.log_status_change(order_id, transition, session)
                    
                    # Notify rider
                    from app.routes.websocket import notify_rider
                    await notify_rider(
                        rider_id=rider_id,
                        event_type="order_assigned",
                        data={
                            "order_id": order_id,
                            "pickup_address": order.get("pickup_address"),
                            "delivery_address": order.get("delivery_address"),
                            "assigned_at": datetime.utcnow().isoformat()
                        }
                    )
                    
                    # Invalidate cache
                    await redis_cache.delete(f"order:{order_id}")
                    
                    logger.info(f"Rider {rider_id} assigned to order {order_id}")
                    
                    return True, "Rider assigned successfully"
                    
            except Exception as e:
                logger.error(f"Failed to assign rider: {e}")
                return False, f"Assignment failed: {str(e)}"
    
    @staticmethod
    async def get_order_audit_trail(order_id: str) -> List[Dict]:
        """Get complete audit trail for an order."""
        db = get_db()
        
        cursor = db.order_audit_logs.find(
            {"order_id": order_id}
        ).sort("timestamp", 1)
        
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def get_status_transitions_report(
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Generate status transition report."""
        db = get_db()
        
        pipeline = [
            {
                "$match": {
                    "timestamp": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "from": "$from_status",
                        "to": "$to_status"
                    },
                    "count": {"$sum": 1},
                    "avg_duration": {"$avg": "$processing_duration_ms"}
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        cursor = db.order_audit_logs.aggregate(pipeline)
        transitions = await cursor.to_list(length=None)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "transitions": transitions,
            "total_transitions": sum(t["count"] for t in transitions)
        }


# Global service instance
order_service = OrderService()
