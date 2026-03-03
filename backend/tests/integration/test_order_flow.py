"""
Integration tests for complete order flow.
Tests: create → assign → pickup → deliver
"""
import pytest
import asyncio
from datetime import datetime
from decimal import Decimal

from app.services.order_service import OrderService, OrderStatus
from app.database import get_db


@pytest.mark.integration
@pytest.mark.asyncio
class TestOrderFlow:
    """Test complete order lifecycle."""
    
    async def test_complete_order_flow(self):
        """Test full order flow from creation to delivery."""
        db = get_db()
        
        # 1. Create order
        order_data = {
            "user_id": "test_user_123",
            "restaurant_id": "test_restaurant_456",
            "items": [
                {
                    "item_id": "item_1",
                    "name": "Test Item",
                    "quantity": 2,
                    "unit_price": Decimal("10.00"),
                    "total_price": Decimal("20.00")
                }
            ],
            "delivery_address": {
                "street": "123 Test St",
                "city": "Test City"
            },
            "total_amount": Decimal("25.00"),
            "delivery_fee": Decimal("5.00"),
            "status": OrderStatus.PENDING,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.orders.insert_one(order_data)
        order_id = str(result.inserted_id)
        
        assert order_id is not None
        print(f"✓ Order created: {order_id}")
        
        # 2. Confirm order
        success, message = await OrderService.update_order_status(
            order_id=order_id,
            new_status=OrderStatus.CONFIRMED,
            actor_id="restaurant_456",
            actor_type="restaurant"
        )
        
        assert success, f"Confirm failed: {message}"
        print("✓ Order confirmed")
        
        # 3. Start preparing
        success, message = await OrderService.update_order_status(
            order_id=order_id,
            new_status=OrderStatus.PREPARING,
            actor_id="restaurant_456",
            actor_type="restaurant"
        )
        
        assert success, f"Preparing failed: {message}"
        print("✓ Order preparation started")
        
        # 4. Mark ready
        success, message = await OrderService.update_order_status(
            order_id=order_id,
            new_status=OrderStatus.READY,
            actor_id="restaurant_456",
            actor_type="restaurant"
        )
        
        assert success, f"Ready failed: {message}"
        print("✓ Order ready for pickup")
        
        # 5. Assign rider
        success, message = await OrderService.assign_rider(
            order_id=order_id,
            rider_id="rider_789",
            assigned_by="system"
        )
        
        assert success, f"Rider assignment failed: {message}"
        print("✓ Rider assigned")
        
        # 6. Mark picked up
        success, message = await OrderService.update_order_status(
            order_id=order_id,
            new_status=OrderStatus.PICKED_UP,
            actor_id="rider_789",
            actor_type="rider"
        )
        
        assert success, f"Pickup failed: {message}"
        print("✓ Order picked up")
        
        # 7. In transit
        success, message = await OrderService.update_order_status(
            order_id=order_id,
            new_status=OrderStatus.IN_TRANSIT,
            actor_id="rider_789",
            actor_type="rider"
        )
        
        assert success, f"Transit failed: {message}"
        print("✓ Order in transit")
        
        # 8. Delivered
        success, message = await OrderService.update_order_status(
            order_id=order_id,
            new_status=OrderStatus.DELIVERED,
            actor_id="rider_789",
            actor_type="rider"
        )
        
        assert success, f"Delivery failed: {message}"
        print("✓ Order delivered")
        
        # Verify final state
        order = await db.orders.find_one({"_id": order_id})
        assert order["status"] == OrderStatus.DELIVERED
        assert order["rider_id"] == "rider_789"
        
        # Verify audit trail
        audit_trail = await OrderService.get_order_audit_trail(order_id)
        assert len(audit_trail) >= 7  # All status changes
        
        print(f"✓ Audit trail verified: {len(audit_trail)} events")
        
        # Cleanup
        await db.orders.delete_one({"_id": order_id})
        await db.order_audit_logs.delete_many({"order_id": order_id})
    
    async def test_invalid_status_transition(self):
        """Test that invalid status transitions are rejected."""
        db = get_db()
        
        # Create pending order
        order_data = {
            "user_id": "test_user",
            "restaurant_id": "test_restaurant",
            "items": [],
            "delivery_address": {},
            "total_amount": Decimal("10.00"),
            "status": OrderStatus.PENDING,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.orders.insert_one(order_data)
        order_id = str(result.inserted_id)
        
        # Try invalid transition: pending -> delivered (should fail)
        success, message = await OrderService.update_order_status(
            order_id=order_id,
            new_status=OrderStatus.DELIVERED,
            actor_id="test",
            actor_type="test"
        )
        
        assert not success, "Invalid transition should fail"
        assert "Invalid status transition" in message
        print(f"✓ Invalid transition correctly rejected: {message}")
        
        # Cleanup
        await db.orders.delete_one({"_id": order_id})
    
    async def test_rider_assignment_race_condition(self):
        """Test atomic rider assignment prevents race conditions."""
        db = get_db()
        
        # Create ready order
        order_data = {
            "user_id": "test_user",
            "restaurant_id": "test_restaurant",
            "items": [],
            "delivery_address": {},
            "total_amount": Decimal("10.00"),
            "status": OrderStatus.READY,
            "rider_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.orders.insert_one(order_data)
        order_id = str(result.inserted_id)
        
        # Simulate concurrent assignments
        async def assign_rider(rider_id):
            return await OrderService.assign_rider(
                order_id=order_id,
                rider_id=rider_id,
                assigned_by="system"
            )
        
        # Run two assignments concurrently
        results = await asyncio.gather(
            assign_rider("rider_1"),
            assign_rider("rider_2"),
            return_exceptions=True
        )
        
        # Only one should succeed
        successes = [r for r in results if isinstance(r, tuple) and r[0]]
        failures = [r for r in results if isinstance(r, tuple) and not r[0]]
        
        assert len(successes) == 1, f"Expected 1 success, got {len(successes)}"
        assert len(failures) == 1, f"Expected 1 failure, got {len(failures)}"
        
        print("✓ Race condition handled correctly")
        
        # Cleanup
        await db.orders.delete_one({"_id": order_id})
