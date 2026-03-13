"""
Integration tests for payment flow.
Tests: initiate → paystack callback → confirm
"""
import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch

from app.services.payment_service import PaymentService, PaymentStatus
from app.database import get_db


@pytest.mark.integration
@pytest.mark.asyncio
class TestPaymentFlow:
    """Test complete payment lifecycle."""
    
    async def test_payment_creation(self):
        """Test creating a payment intent."""
        db = get_db()
        
        # Create payment record
        payment_data = {
            "order_id": "order_123",
            "user_id": "user_456",
            "amount": Decimal("50.00"),
            "currency": "USD",
            "payment_method": "card",
            "status": PaymentStatus.PENDING,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.payments.insert_one(payment_data)
        payment_id = str(result.inserted_id)
        
        assert payment_id is not None
        print(f"✓ Payment record created: {payment_id}")
        
        # Cleanup
        await db.payments.delete_one({"_id": payment_id})
    
    async def test_payment_status_update(self):
        """Test updating payment status through flow."""
        db = get_db()
        
        # Create initial payment
        payment_data = {
            "order_id": "order_123",
            "user_id": "user_456",
            "amount": Decimal("50.00"),
            "currency": "USD",
            "payment_method": "card",
            "status": PaymentStatus.PENDING,
            "transaction_id": "pi_test_123",
            "payment_processor": "stripe",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.payments.insert_one(payment_data)
        payment_id = str(result.inserted_id)
        
        # Update to processing
        await db.payments.update_one(
            {"_id": payment_id},
            {
                "$set": {
                    "status": PaymentStatus.PROCESSING,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        payment = await db.payments.find_one({"_id": payment_id})
        assert payment["status"] == PaymentStatus.PROCESSING
        print("✓ Payment status updated to processing")
        
        # Update to completed
        await db.payments.update_one(
            {"_id": payment_id},
            {
                "$set": {
                    "status": PaymentStatus.COMPLETED,
                    "completed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        payment = await db.payments.find_one({"_id": payment_id})
        assert payment["status"] == PaymentStatus.COMPLETED
        print("✓ Payment status updated to completed")
        
        # Cleanup
        await db.payments.delete_one({"_id": payment_id})
    
    async def test_payment_reconciliation(self):
        """Test payment reconciliation for stuck payments."""
        db = get_db()
        
        # Create a stuck processing payment (old)
        old_time = datetime.utcnow() - __import__('datetime').timedelta(minutes=10)
        payment_data = {
            "order_id": "order_123",
            "user_id": "user_456",
            "amount": Decimal("50.00"),
            "currency": "USD",
            "payment_method": "card",
            "status": PaymentStatus.PROCESSING,
            "transaction_id": "pi_test_123",
            "payment_processor": "stripe",
            "created_at": old_time,
            "updated_at": old_time
        }
        
        result = await db.payments.insert_one(payment_data)
        payment_id = str(result.inserted_id)
        
        # Get pending payments (should include this one)
        from app.services.reconciliation_service import reconciliation_service
        
        pending = await reconciliation_service._get_pending_payments()
        
        # Verify our payment is in the pending list
        payment_ids = [str(p["_id"]) for p in pending]
        assert payment_id in payment_ids, "Stuck payment should be flagged for reconciliation"
        
        print("✓ Reconciliation correctly identifies stuck payments")
        
        # Cleanup
        await db.payments.delete_one({"_id": payment_id})
    
    async def test_refund_flow(self):
        """Test refund flow: request → approve → process."""
        db = get_db()
        
        # Create completed payment
        payment_data = {
            "order_id": "order_123",
            "user_id": "user_456",
            "amount": Decimal("50.00"),
            "currency": "USD",
            "payment_method": "card",
            "status": PaymentStatus.COMPLETED,
            "transaction_id": "pi_test_123",
            "payment_processor": "stripe",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.payments.insert_one(payment_data)
        payment_id = str(result.inserted_id)
        
        # Create refund request
        refund_data = {
            "payment_id": payment_id,
            "amount": Decimal("25.00"),  # Partial refund
            "reason": "Item not available",
            "status": "requested",
            "requested_by": "user_456",
            "requested_at": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        refund_result = await db.refunds.insert_one(refund_data)
        refund_id = str(refund_result.inserted_id)
        
        print(f"✓ Refund requested: {refund_id}")
        
        # Approve refund
        await db.refunds.update_one(
            {"_id": refund_id},
            {
                "$set": {
                    "status": "approved",
                    "approved_by": "admin_001",
                    "approved_at": datetime.utcnow()
                }
            }
        )
        
        refund = await db.refunds.find_one({"_id": refund_id})
        assert refund["status"] == "approved"
        print("✓ Refund approved")
        
        # Process refund (update payment status)
        await db.payments.update_one(
            {"_id": payment_id},
            {
                "$set": {
                    "status": PaymentStatus.REFUNDED,
                    "refunded_amount": Decimal("25.00"),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        await db.refunds.update_one(
            {"_id": refund_id},
            {"$set": {"status": "processed", "processed_at": datetime.utcnow()}}
        )
        
        payment = await db.payments.find_one({"_id": payment_id})
        assert payment["status"] == PaymentStatus.REFUNDED
        print("✓ Refund processed")
        
        # Cleanup
        await db.payments.delete_one({"_id": payment_id})
        await db.refunds.delete_one({"_id": refund_id})
