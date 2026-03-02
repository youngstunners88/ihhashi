"""Payment service with Stripe integration."""
import logging
from decimal import Decimal
from typing import Optional, Dict, Any
import stripe

from app.config import settings
from app.schemas.payment import PaymentStatus, PaymentMethod

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    """Payment processing service."""
    
    @staticmethod
    async def create_payment_intent(
        amount: Decimal,
        currency: str = "usd",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe PaymentIntent.
        
        Args:
            amount: Amount to charge
            currency: Currency code (default: usd)
            metadata: Additional metadata
            
        Returns:
            Dictionary with client_secret and payment_intent_id
        """
        try:
            # Convert Decimal to cents for Stripe
            amount_cents = int(amount * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                metadata=metadata or {},
                automatic_payment_methods={"enabled": True}
            )
            
            logger.info(f"Created PaymentIntent: {intent.id}")
            
            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": amount,
                "currency": currency
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating payment intent: {e}")
            raise
    
    @staticmethod
    async def confirm_payment(payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirm a payment intent.
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            
        Returns:
            Payment status information
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                "status": intent.status,
                "payment_intent_id": intent.id,
                "amount": Decimal(intent.amount) / 100,
                "currency": intent.currency
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving payment: {e}")
            raise
    
    @staticmethod
    async def create_refund(
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a refund.
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            amount: Amount to refund (None for full refund)
            reason: Reason for refund
            
        Returns:
            Refund information
        """
        try:
            refund_data = {"payment_intent": payment_intent_id}
            
            if amount:
                refund_data["amount"] = int(amount * 100)
            
            if reason:
                refund_data["reason"] = "requested_by_customer"
                refund_data["metadata"] = {"refund_reason": reason}
            
            refund = stripe.Refund.create(**refund_data)
            
            logger.info(f"Created refund: {refund.id} for PaymentIntent: {payment_intent_id}")
            
            return {
                "refund_id": refund.id,
                "status": refund.status,
                "amount": Decimal(refund.amount) / 100 if refund.amount else None
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating refund: {e}")
            raise
    
    @staticmethod
    async def process_webhook(payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Process Stripe webhook.
        
        Args:
            payload: Raw request body
            signature: Stripe signature header
            
        Returns:
            Event data
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            
            logger.info(f"Received webhook event: {event.type}")
            
            return {
                "type": event.type,
                "data": event.data.object
            }
            
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            raise
    
    @staticmethod
    def map_stripe_status_to_payment_status(stripe_status: str) -> PaymentStatus:
        """Map Stripe status to our PaymentStatus."""
        status_map = {
            "requires_payment_method": PaymentStatus.PENDING,
            "requires_confirmation": PaymentStatus.PENDING,
            "requires_action": PaymentStatus.PROCESSING,
            "processing": PaymentStatus.PROCESSING,
            "requires_capture": PaymentStatus.PROCESSING,
            "succeeded": PaymentStatus.COMPLETED,
            "canceled": PaymentStatus.CANCELLED,
        }
        return status_map.get(stripe_status, PaymentStatus.FAILED)


# Mobile Money Support (for regions like Africa)
class MobileMoneyService:
    """Mobile money payment service (Flutterwave/M-Pesa)."""
    
    @staticmethod
    async def charge_mobile_money(
        phone_number: str,
        amount: Decimal,
        provider: str = "mpesa"
    ) -> Dict[str, Any]:
        """
        Charge via mobile money.
        
        Args:
            phone_number: Customer phone number
            amount: Amount to charge
            provider: Mobile money provider (mpesa, airtel, etc.)
            
        Returns:
            Transaction details
        """
        # TODO: Implement Flutterwave or direct M-Pesa integration
        logger.info(f"Mobile money charge initiated: {phone_number}, {amount}, {provider}")
        
        return {
            "status": "pending",
            "transaction_id": "pending_implementation",
            "provider": provider,
            "amount": amount,
            "phone_number": phone_number
        }
