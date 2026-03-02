"""
Payment Reconciliation Service with APScheduler integration.
Runs every 5 minutes to reconcile payment statuses.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.database import get_db
from app.services.payment_service import PaymentService
from app.services.redis_cache import redis_cache

logger = logging.getLogger(__name__)


class ReconciliationStatus(str, Enum):
    """Reconciliation attempt status."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


class PaymentReconciliationService:
    """
    Service for reconciling payment statuses.
    Runs periodically to sync payment states with payment processors.
    """
    
    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.payment_service = PaymentService()
        self.is_running = False
    
    def start_scheduler(self):
        """Start the APScheduler for reconciliation."""
        if self.scheduler is None:
            self.scheduler = AsyncIOScheduler()
            
            # Add job to run every 5 minutes
            self.scheduler.add_job(
                func=self.run_reconciliation,
                trigger=IntervalTrigger(minutes=5),
                id="payment_reconciliation",
                name="Payment Reconciliation",
                replace_existing=True,
                max_instances=1,  # Prevent concurrent runs
            )
            
            self.scheduler.start()
            logger.info("Payment reconciliation scheduler started (every 5 minutes)")
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        if self.scheduler:
            self.scheduler.shutdown()
            self.scheduler = None
            logger.info("Payment reconciliation scheduler stopped")
    
    async def run_reconciliation(self):
        """Main reconciliation method called by scheduler."""
        if self.is_running:
            logger.warning("Reconciliation already running, skipping this run")
            await self._log_reconciliation_attempt(
                status=ReconciliationStatus.SKIPPED,
                reason="Previous run still in progress"
            )
            return
        
        self.is_running = True
        start_time = datetime.utcnow()
        
        try:
            logger.info("Starting payment reconciliation run")
            
            # Get pending payments that need reconciliation
            pending_payments = await self._get_pending_payments()
            
            if not pending_payments:
                logger.info("No pending payments to reconcile")
                await self._log_reconciliation_attempt(
                    status=ReconciliationStatus.SUCCESS,
                    processed_count=0,
                    duration_ms=0
                )
                return
            
            # Process each pending payment
            results = await self._reconcile_payments(pending_payments)
            
            # Calculate statistics
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            await self._log_reconciliation_attempt(
                status=results["status"],
                processed_count=results["processed"],
                success_count=results["success"],
                failed_count=results["failed"],
                duration_ms=int(duration),
                details=results["details"]
            )
            
            logger.info(
                f"Reconciliation completed: {results['success']}/{results['processed']} "
                f"successful in {duration:.2f}ms"
            )
            
        except Exception as e:
            logger.error(f"Reconciliation run failed: {e}")
            await self._log_reconciliation_attempt(
                status=ReconciliationStatus.FAILED,
                error=str(e)
            )
        finally:
            self.is_running = False
    
    async def _get_pending_payments(self) -> List[Dict]:
        """Get payments that need reconciliation."""
        db = get_db()
        
        # Get payments that are:
        # 1. Status = 'processing' and created > 5 minutes ago
        # 2. Status = 'pending' and created > 10 minutes ago
        # 3. Any status mismatch between our DB and payment processor
        
        cutoff_processing = datetime.utcnow() - timedelta(minutes=5)
        cutoff_pending = datetime.utcnow() - timedelta(minutes=10)
        
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {
                            "status": "processing",
                            "created_at": {"$lt": cutoff_processing}
                        },
                        {
                            "status": "pending",
                            "created_at": {"$lt": cutoff_pending}
                        }
                    ]
                }
            },
            {"$sort": {"created_at": 1}},
            {"$limit": 100}  # Process max 100 per run
        ]
        
        cursor = db.payments.aggregate(pipeline)
        return await cursor.to_list(length=100)
    
    async def _reconcile_payments(self, payments: List[Dict]) -> Dict:
        """Reconcile a batch of payments."""
        success_count = 0
        failed_count = 0
        details = []
        
        for payment in payments:
            try:
                result = await self._reconcile_single_payment(payment)
                
                if result["success"]:
                    success_count += 1
                else:
                    failed_count += 1
                
                details.append({
                    "payment_id": str(payment.get("_id")),
                    "processor_id": payment.get("transaction_id"),
                    "success": result["success"],
                    "old_status": payment.get("status"),
                    "new_status": result.get("new_status"),
                    "error": result.get("error")
                })
                
            except Exception as e:
                failed_count += 1
                details.append({
                    "payment_id": str(payment.get("_id")),
                    "success": False,
                    "error": str(e)
                })
        
        total = len(payments)
        status = ReconciliationStatus.SUCCESS
        if failed_count == total:
            status = ReconciliationStatus.FAILED
        elif failed_count > 0:
            status = ReconciliationStatus.PARTIAL
        
        return {
            "status": status,
            "processed": total,
            "success": success_count,
            "failed": failed_count,
            "details": details
        }
    
    async def _reconcile_single_payment(self, payment: Dict) -> Dict:
        """Reconcile a single payment with its processor."""
        processor = payment.get("payment_processor")
        processor_id = payment.get("transaction_id")
        
        if not processor_id:
            return {
                "success": False,
                "error": "No transaction_id found"
            }
        
        try:
            # Check status with payment processor
            if processor == "stripe":
                payment_intent = await self.payment_service.confirm_payment(processor_id)
                new_status = self.payment_service.map_stripe_status_to_payment_status(
                    payment_intent["status"]
                )
            elif processor == "paystack":
                # Implement Paystack status check
                new_status = await self._check_paystack_status(processor_id)
            else:
                return {
                    "success": False,
                    "error": f"Unknown processor: {processor}"
                }
            
            # Update payment if status changed
            current_status = payment.get("status")
            if new_status.value != current_status:
                await self._update_payment_status(
                    payment_id=str(payment["_id"]),
                    old_status=current_status,
                    new_status=new_status.value,
                    processor_data=payment_intent if processor == "stripe" else {}
                )
                
                # Invalidate cache
                await redis_cache.delete(f"payment:{payment['_id']}")
                
                return {
                    "success": True,
                    "new_status": new_status.value,
                    "status_changed": True
                }
            
            return {
                "success": True,
                "status_changed": False
            }
            
        except Exception as e:
            logger.error(f"Failed to reconcile payment {payment['_id']}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_paystack_status(self, transaction_id: str) -> any:
        """Check payment status with Paystack."""
        # TODO: Implement actual Paystack API call
        from app.schemas.payment import PaymentStatus
        return PaymentStatus.PENDING
    
    async def _update_payment_status(
        self,
        payment_id: str,
        old_status: str,
        new_status: str,
        processor_data: Dict
    ):
        """Update payment status in database."""
        db = get_db()
        
        await db.payments.update_one(
            {"_id": payment_id},
            {
                "$set": {
                    "status": new_status,
                    "updated_at": datetime.utcnow(),
                    "reconciled_at": datetime.utcnow(),
                    "reconciliation_data": processor_data
                },
                "$push": {
                    "status_history": {
                        "from": old_status,
                        "to": new_status,
                        "timestamp": datetime.utcnow(),
                        "source": "reconciliation"
                    }
                }
            }
        )
    
    async def _log_reconciliation_attempt(self, **kwargs):
        """Log reconciliation attempt to dedicated collection."""
        db = get_db()
        
        log_entry = {
            "timestamp": datetime.utcnow(),
            "instance_id": settings.INSTANCE_ID,
            **kwargs
        }
        
        await db.reconciliation_logs.insert_one(log_entry)
        
        # Also cache latest status for quick checks
        await redis_cache.set_json(
            "reconciliation:latest",
            {
                "timestamp": datetime.utcnow().isoformat(),
                "status": kwargs.get("status"),
                "processed_count": kwargs.get("processed_count", 0)
            },
            expire=600  # 10 minutes
        )
    
    async def get_reconciliation_stats(
        self,
        hours: int = 24
    ) -> Dict:
        """Get reconciliation statistics."""
        db = get_db()
        
        since = datetime.utcnow() - timedelta(hours=hours)
        
        pipeline = [
            {"$match": {"timestamp": {"$gte": since}}},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                    "total_processed": {"$sum": "$processed_count"},
                    "avg_duration": {"$avg": "$duration_ms"}
                }
            }
        ]
        
        cursor = db.reconciliation_logs.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        return {
            "period_hours": hours,
            "breakdown": results,
            "latest": await redis_cache.get_json("reconciliation:latest")
        }


# Global service instance
reconciliation_service = PaymentReconciliationService()
