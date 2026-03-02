"""
Paystack Webhook Handler with signature verification, logging, and dead letter queue.
"""
import logging
import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, Optional, Callable
from enum import Enum
from dataclasses import dataclass

import httpx

from app.config import settings
from app.database import get_db
from app.services.redis_cache import redis_cache

logger = logging.getLogger(__name__)


class WebhookStatus(str, Enum):
    """Webhook processing status."""
    RECEIVED = "received"
    VERIFIED = "verified"
    INVALID_SIGNATURE = "invalid_signature"
    PROCESSED = "processed"
    FAILED = "failed"
    RETRYING = "retrying"
    DLQ = "dead_letter_queue"


@dataclass
class WebhookEvent:
    """Paystack webhook event data."""
    event_id: str
    event_type: str
    payload: Dict
    signature: str
    timestamp: datetime
    retry_count: int = 0


class PaystackWebhookService:
    """
    Paystack webhook service with:
    - Signature verification with detailed logging
    - Dead letter queue for failed webhooks
    - Automatic retry with exponential backoff
    - Alerting for repeated failures
    """
    
    # Max retries before sending to DLQ
    MAX_RETRIES = 3
    
    # Retry delays (seconds)
    RETRY_DELAYS = [60, 300, 900]  # 1min, 5min, 15min
    
    # Alert threshold: alert after this many consecutive failures
    ALERT_THRESHOLD = 10
    
    # Redis key for tracking failures
    FAILURE_COUNTER_KEY = "paystack:webhook:failures"
    
    # Redis key for DLQ
    DLQ_KEY = "paystack:webhook:dlq"
    
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY if hasattr(settings, 'PAYSTACK_SECRET_KEY') else None
        self.handlers: Dict[str, Callable] = {}
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register handler for specific event type."""
        self.handlers[event_type] = handler
        logger.info(f"Registered handler for event: {event_type}")
    
    async def verify_signature(
        self,
        payload: bytes,
        signature: str
    ) -> bool:
        """
        Verify Paystack webhook signature.
        Logs verification attempts for audit purposes.
        """
        if not self.secret_key:
            logger.warning("Paystack secret key not configured, skipping signature verification")
            return False
        
        try:
            # Compute expected signature
            expected_signature = hmac.new(
                self.secret_key.encode('utf-8'),
                payload,
                hashlib.sha512
            ).hexdigest()
            
            # Use constant-time comparison to prevent timing attacks
            is_valid = hmac.compare_digest(expected_signature, signature)
            
            # Log verification attempt
            await self._log_verification_attempt(
                signature=signature,
                expected_signature=expected_signature[:20] + "...",  # Truncate for security
                is_valid=is_valid
            )
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            await self._log_verification_attempt(
                signature=signature,
                error=str(e),
                is_valid=False
            )
            return False
    
    async def _log_verification_attempt(
        self,
        signature: str,
        is_valid: bool,
        expected_signature: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Log signature verification attempt."""
        db = get_db()
        
        log_entry = {
            "timestamp": datetime.utcnow(),
            "event": "signature_verification",
            "signature_prefix": signature[:20] if signature else None,
            "expected_prefix": expected_signature,
            "is_valid": is_valid,
            "error": error,
            "instance_id": settings.INSTANCE_ID,
        }
        
        await db.paystack_webhook_logs.insert_one(log_entry)
    
    async def process_webhook(
        self,
        payload: bytes,
        signature: str
    ) -> Dict:
        """
        Process incoming Paystack webhook.
        
        Returns:
            Dict with processing result
        """
        event_id = None
        
        try:
            # Parse payload
            data = json.loads(payload)
            event_id = data.get("event") + ":" + str(data.get("data", {}).get("id", "unknown"))
            event_type = data.get("event")
            
            # Log receipt
            await self._log_webhook_event(
                event_id=event_id,
                event_type=event_type,
                status=WebhookStatus.RECEIVED,
                payload=data
            )
            
            # Verify signature
            if not await self.verify_signature(payload, signature):
                logger.warning(f"Invalid signature for webhook: {event_id}")
                await self._log_webhook_event(
                    event_id=event_id,
                    event_type=event_type,
                    status=WebhookStatus.INVALID_SIGNATURE,
                    error="Signature verification failed"
                )
                return {"status": "error", "message": "Invalid signature"}
            
            await self._log_webhook_event(
                event_id=event_id,
                event_type=event_type,
                status=WebhookStatus.VERIFIED
            )
            
            # Process event
            result = await self._process_event(event_id, event_type, data)
            
            # Reset failure counter on success
            await self._reset_failure_counter()
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in webhook payload: {e}")
            return {"status": "error", "message": "Invalid JSON"}
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            
            # Send to retry queue
            if event_id:
                await self._queue_for_retry(event_id, payload, signature)
            
            return {"status": "error", "message": str(e)}
    
    async def _process_event(
        self,
        event_id: str,
        event_type: str,
        data: Dict
    ) -> Dict:
        """Process specific webhook event."""
        handler = self.handlers.get(event_type)
        
        if not handler:
            logger.warning(f"No handler registered for event type: {event_type}")
            return {"status": "ignored", "message": f"No handler for {event_type}"}
        
        try:
            await handler(data)
            
            await self._log_webhook_event(
                event_id=event_id,
                event_type=event_type,
                status=WebhookStatus.PROCESSED
            )
            
            return {"status": "success", "message": "Event processed"}
            
        except Exception as e:
            logger.error(f"Handler failed for {event_type}: {e}")
            await self._log_webhook_event(
                event_id=event_id,
                event_type=event_type,
                status=WebhookStatus.FAILED,
                error=str(e)
            )
            raise
    
    async def _queue_for_retry(
        self,
        event_id: str,
        payload: bytes,
        signature: str
    ):
        """Queue webhook for retry with exponential backoff."""
        retry_key = f"paystack:webhook:retry:{event_id}"
        
        # Get current retry count
        retry_data = await redis_cache.get_json(retry_key)
        retry_count = retry_data.get("retry_count", 0) if retry_data else 0
        
        if retry_count >= self.MAX_RETRIES:
            # Send to dead letter queue
            await self._send_to_dlq(event_id, payload, signature, retry_count)
            await redis_cache.delete(retry_key)
            return
        
        # Schedule retry
        delay = self.RETRY_DELAYS[retry_count] if retry_count < len(self.RETRY_DELAYS) else 3600
        
        await redis_cache.set_json(
            retry_key,
            {
                "event_id": event_id,
                "payload": payload.decode(),
                "signature": signature,
                "retry_count": retry_count + 1,
                "next_retry": (datetime.utcnow() + __import__('datetime').timedelta(seconds=delay)).isoformat()
            },
            expire=delay + 300  # Extra buffer
        )
        
        await self._log_webhook_event(
            event_id=event_id,
            event_type="unknown",
            status=WebhookStatus.RETRYING,
            retry_count=retry_count + 1
        )
        
        # Increment failure counter for alerting
        await self._increment_failure_counter()
    
    async def _send_to_dlq(
        self,
        event_id: str,
        payload: bytes,
        signature: str,
        retry_count: int
    ):
        """Send webhook to dead letter queue."""
        dlq_entry = {
            "event_id": event_id,
            "payload": payload.decode(),
            "signature": signature,
            "retry_count": retry_count,
            "failed_at": datetime.utcnow().isoformat(),
            "instance_id": settings.INSTANCE_ID,
        }
        
        # Add to Redis list
        await redis_cache._client.lpush(self.DLQ_KEY, json.dumps(dlq_entry))
        
        # Also log to MongoDB
        db = get_db()
        await db.paystack_webhook_dlq.insert_one({
            **dlq_entry,
            "received_at": datetime.utcnow()
        })
        
        await self._log_webhook_event(
            event_id=event_id,
            event_type="unknown",
            status=WebhookStatus.DLQ,
            retry_count=retry_count
        )
        
        logger.error(f"Webhook {event_id} sent to DLQ after {retry_count} retries")
    
    async def _log_webhook_event(
        self,
        event_id: str,
        event_type: str,
        status: WebhookStatus,
        payload: Optional[Dict] = None,
        error: Optional[str] = None,
        retry_count: Optional[int] = None
    ):
        """Log webhook event to database."""
        db = get_db()
        
        log_entry = {
            "event_id": event_id,
            "event_type": event_type,
            "status": status.value,
            "timestamp": datetime.utcnow(),
            "instance_id": settings.INSTANCE_ID,
        }
        
        if payload:
            log_entry["payload_summary"] = {
                "event": payload.get("event"),
                "reference": payload.get("data", {}).get("reference"),
                "amount": payload.get("data", {}).get("amount"),
            }
        
        if error:
            log_entry["error"] = error
        
        if retry_count is not None:
            log_entry["retry_count"] = retry_count
        
        await db.paystack_webhook_logs.insert_one(log_entry)
    
    async def _increment_failure_counter(self):
        """Increment failure counter for alerting."""
        count = await redis_cache.get(self.FAILURE_COUNTER_KEY) or 0
        count = int(count) + 1
        await redis_cache.set(self.FAILURE_COUNTER_KEY, count, expire=3600)
        
        # Check if alert threshold reached
        if count >= self.ALERT_THRESHOLD:
            await self._send_alert(
                f"Paystack webhook failure alert: {count} consecutive failures"
            )
    
    async def _reset_failure_counter(self):
        """Reset failure counter after successful processing."""
        await redis_cache.delete(self.FAILURE_COUNTER_KEY)
    
    async def _send_alert(self, message: str):
        """Send alert for repeated failures."""
        logger.error(f"ALERT: {message}")
        
        # TODO: Integrate with alerting service (PagerDuty, Slack, etc.)
        # await send_slack_alert(message)
        # await send_pagerduty_alert(message)
    
    async def get_failed_webhooks(
        self,
        hours: int = 24
    ) -> Dict:
        """Get statistics on failed webhooks."""
        db = get_db()
        
        since = datetime.utcnow() - __import__('datetime').timedelta(hours=hours)
        
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": since},
                    "status": {"$in": ["failed", "dead_letter_queue"]}
                }
            },
            {
                "$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1},
                    "latest": {"$max": "$timestamp"}
                }
            }
        ]
        
        cursor = db.paystack_webhook_logs.aggregate(pipeline)
        failures = await cursor.to_list(length=None)
        
        # Get DLQ count
        dlq_count = 0
        if redis_cache._client:
            dlq_count = await redis_cache._client.llen(self.DLQ_KEY)
        
        return {
            "period_hours": hours,
            "failures_by_type": failures,
            "dead_letter_queue_count": dlq_count,
            "total_failures": sum(f["count"] for f in failures),
            "current_failure_streak": await redis_cache.get(self.FAILURE_COUNTER_KEY) or 0
        }
    
    async def replay_dlq_webhook(self, event_id: str) -> bool:
        """Manually replay a webhook from DLQ."""
        db = get_db()
        
        entry = await db.paystack_webhook_dlq.find_one({"event_id": event_id})
        if not entry:
            return False
        
        try:
            payload = entry["payload"].encode()
            signature = entry["signature"]
            
            result = await self.process_webhook(payload, signature)
            
            if result["status"] == "success":
                # Remove from DLQ
                await db.paystack_webhook_dlq.update_one(
                    {"event_id": event_id},
                    {"$set": {"replayed": True, "replayed_at": datetime.utcnow()}}
                )
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to replay webhook {event_id}: {e}")
            return False


# Global service instance
paystack_webhook_service = PaystackWebhookService()
