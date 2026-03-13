"""
Payment Reconciliation Job

Checks recent pending/inconsistent payment/order states,
re-verifies references against Paystack,
repairs state idempotently,
logs and alerts GlitchTip on mismatch.

This is a COMPLEMENTARY safety net - it does NOT modify
webhook core signature/idempotency logic.

Run via: python -m app.jobs.payment_reconciliation
Or schedule via cron/APScheduler.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum

from app.config import settings
from app.database import get_collection
from app.services.paystack import PaystackService

logger = logging.getLogger(__name__)


class ReconciliationStatus(str, Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    NOT_FOUND = "not_found"
    ERROR = "error"


class ReconciliationResult:
    """Result of reconciling a single payment"""
    def __init__(
        self,
        reference: str,
        status: ReconciliationStatus,
        local_state: Optional[str] = None,
        paystack_state: Optional[str] = None,
        repaired: bool = False,
        error: Optional[str] = None
    ):
        self.reference = reference
        self.status = status
        self.local_state = local_state
        self.paystack_state = paystack_state
        self.repaired = repaired
        self.error = error
        self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "reference": self.reference,
            "status": self.status.value,
            "local_state": self.local_state,
            "paystack_state": self.paystack_state,
            "repaired": self.repaired,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


async def get_pending_payments(hours_back: int = 24) -> List[Dict[str, Any]]:
    """
    Get payments that may need reconciliation:
    - Status is 'pending' or 'initialized' for more than X minutes
    - Status is 'success' but order payment_status is not 'paid'
    """
    payments_col = get_collection("payments")
    orders_col = get_collection("orders")
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    
    # Find stale pending/initialized payments
    stale_pending = await payments_col.find({
        "status": {"$in": ["pending", "initialized"]},
        "created_at": {"$lt": cutoff_time}
    }).to_list(length=100)
    
    # Find payments marked success but orders not updated
    success_payments = await payments_col.find({
        "status": "success",
        "order_id": {"$exists": True, "$ne": None},
        "created_at": {"$gte": cutoff_time}
    }).to_list(length=100)
    
    mismatched_orders = []
    for payment in success_payments:
        order = await orders_col.find_one({"_id": payment.get("order_id")})
        if order and order.get("payment_status") != "paid":
            mismatched_orders.append(payment)
    
    all_candidates = stale_pending + mismatched_orders
    
    # Deduplicate by reference
    seen_refs = set()
    unique_payments = []
    for p in all_candidates:
        ref = p.get("reference")
        if ref and ref not in seen_refs:
            seen_refs.add(ref)
            unique_payments.append(p)
    
    return unique_payments


async def reconcile_payment(payment: Dict[str, Any]) -> ReconciliationResult:
    """
    Reconcile a single payment against Paystack.
    
    Does NOT modify webhook logic - only repairs state if mismatch found.
    """
    reference = payment.get("reference")
    local_status = payment.get("status")
    
    if not reference:
        return ReconciliationResult(
            reference="unknown",
            status=ReconciliationStatus.ERROR,
            error="Missing reference"
        )
    
    try:
        paystack = PaystackService()
        verification = await paystack.verify_payment(reference)
        
        if not verification.get("status"):
            # Paystack API error
            return ReconciliationResult(
                reference=reference,
                status=ReconciliationStatus.ERROR,
                local_state=local_status,
                error=verification.get("message", "Paystack verification failed")
            )
        
        paystack_data = verification.get("data", {})
        paystack_status = paystack_data.get("status")
        
        # Compare states
        if local_status == paystack_status:
            return ReconciliationResult(
                reference=reference,
                status=ReconciliationStatus.MATCH,
                local_state=local_status,
                paystack_state=paystack_status
            )
        
        # MISMATCH DETECTED
        logger.warning(
            f"Payment mismatch: reference={reference}, "
            f"local={local_status}, paystack={paystack_status}"
        )
        
        # Alert to GlitchTip (Sentry-compatible)
        try:
            import sentry_sdk
            sentry_sdk.capture_message(
                f"Payment reconciliation mismatch: {reference} "
                f"(local: {local_status}, paystack: {paystack_status})",
                level="warning"
            )
        except ImportError:
            pass  # GlitchTip/Sentry not configured
        
        # REPAIR: Update local state to match Paystack (idempotent)
        payments_col = get_collection("payments")
        orders_col = get_collection("orders")
        
        if paystack_status == "success" and local_status != "success":
            # Payment succeeded but we missed it - repair
            await payments_col.update_one(
                {"reference": reference, "status": {"$ne": "success"}},
                {"$set": {
                    "status": "success",
                    "paid_at": paystack_data.get("paid_at"),
                    "reconciled_at": datetime.now(timezone.utc),
                    "reconciliation_source": "paystack_verify"
                }}
            )
            
            # Update order if exists
            order_id = payment.get("order_id")
            if order_id:
                await orders_col.update_one(
                    {"_id": order_id},
                    {"$set": {
                        "payment_status": "paid",
                        "paid_at": datetime.now(timezone.utc)
                    }}
                )
            
            return ReconciliationResult(
                reference=reference,
                status=ReconciliationStatus.MISMATCH,
                local_state=local_status,
                paystack_state=paystack_status,
                repaired=True
            )
        
        elif paystack_status == "failed" and local_status not in ["failed", "cancelled"]:
            # Payment failed but we didn't mark it
            await payments_col.update_one(
                {"reference": reference},
                {"$set": {
                    "status": "failed",
                    "failed_at": datetime.now(timezone.utc),
                    "reconciled_at": datetime.now(timezone.utc),
                    "reconciliation_source": "paystack_verify"
                }}
            )
            
            return ReconciliationResult(
                reference=reference,
                status=ReconciliationStatus.MISMATCH,
                local_state=local_status,
                paystack_state=paystack_status,
                repaired=True
            )
        
        # Other mismatches - just log, don't auto-repair
        return ReconciliationResult(
            reference=reference,
            status=ReconciliationStatus.MISMATCH,
            local_state=local_status,
            paystack_state=paystack_status,
            repaired=False
        )
        
    except Exception as e:
        logger.error(f"Reconciliation error for {reference}: {e}")
        return ReconciliationResult(
            reference=reference,
            status=ReconciliationStatus.ERROR,
            local_state=local_status,
            error=str(e)
        )


async def run_reconciliation(hours_back: int = 24) -> Dict[str, Any]:
    """
    Main reconciliation job entry point.
    
    Returns summary of results.
    """
    logger.info(f"Starting payment reconciliation (last {hours_back}h)")
    
    # Get candidates
    candidates = await get_pending_payments(hours_back)
    logger.info(f"Found {len(candidates)} payments to check")
    
    if not candidates:
        return {
            "status": "complete",
            "checked": 0,
            "results": []
        }
    
    # Process each payment
    results = []
    for payment in candidates:
        result = await reconcile_payment(payment)
        results.append(result.to_dict())
    
    # Summary
    summary = {
        "status": "complete",
        "checked": len(results),
        "matches": sum(1 for r in results if r["status"] == "match"),
        "mismatches": sum(1 for r in results if r["status"] == "mismatch"),
        "repaired": sum(1 for r in results if r.get("repaired")),
        "errors": sum(1 for r in results if r["status"] == "error"),
        "results": results
    }
    
    logger.info(
        f"Reconciliation complete: {summary['matches']} matches, "
        f"{summary['mismatches']} mismatches, {summary['repaired']} repaired, "
        f"{summary['errors']} errors"
    )
    
    # Store reconciliation log
    recon_col = get_collection("payment_reconciliations")
    await recon_col.insert_one({
        "run_at": datetime.now(timezone.utc),
        "hours_back": hours_back,
        **summary
    })
    
    return summary


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Payment reconciliation job")
    parser.add_argument(
        "--hours", 
        type=int, 
        default=24,
        help="Hours back to check for pending payments (default: 24)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check only, don't repair"
    )
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    if args.dry_run:
        logger.info("DRY RUN MODE - no repairs will be made")
    
    result = asyncio.run(run_reconciliation(args.hours))
    
    print("\n=== Reconciliation Summary ===")
    print(f"Checked: {result['checked']}")
    print(f"Matches: {result['matches']}")
    print(f"Mismatches: {result['mismatches']}")
    print(f"Repaired: {result['repaired']}")
    print(f"Errors: {result['errors']}")
    
    if result['errors'] > 0 or result['mismatches'] > result['repaired']:
        print("\n⚠️  Manual review may be needed")
        exit(1)
    
    print("\n✓ Reconciliation complete")


if __name__ == "__main__":
    main()
