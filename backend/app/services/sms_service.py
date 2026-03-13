"""SMS service with Twilio integration."""
import logging
from typing import Optional
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioRestException

from app.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """SMS service using Twilio."""
    
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID if hasattr(settings, 'TWILIO_ACCOUNT_SID') else None
        self.auth_token = settings.TWILIO_AUTH_TOKEN if hasattr(settings, 'TWILIO_AUTH_TOKEN') else None
        self.from_number = settings.TWILIO_PHONE_NUMBER if hasattr(settings, 'TWILIO_PHONE_NUMBER') else None
        
        if self.account_sid and self.auth_token:
            self.client = TwilioClient(self.account_sid, self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials not configured")
    
    async def send_sms(self, to_number: str, message: str) -> bool:
        """
        Send SMS message.
        
        Args:
            to_number: Recipient phone number
            message: Message body
            
        Returns:
            True if sent successfully
        """
        if not self.client:
            logger.warning("SMS service not configured, message not sent")
            return False
        
        try:
            # Format phone number (add + if missing)
            if not to_number.startswith('+'):
                to_number = '+' + to_number
            
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            logger.info(f"SMS sent successfully. SID: {message.sid}")
            return True
            
        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    async def send_otp(self, to_number: str, otp_code: str) -> bool:
        """
        Send OTP code via SMS.
        
        Args:
            to_number: Recipient phone number
            otp_code: OTP code
            
        Returns:
            True if sent successfully
        """
        message = f"Your verification code is: {otp_code}. Valid for 10 minutes."
        return await self.send_sms(to_number, message)
    
    async def send_order_update(self, to_number: str, order_id: str, status: str) -> bool:
        """
        Send order status update via SMS.
        
        Args:
            to_number: Recipient phone number
            order_id: Order ID
            status: New order status
            
        Returns:
            True if sent successfully
        """
        message = f"Your order #{order_id} is now {status}. Track your order in the app."
        return await self.send_sms(to_number, message)
    
    async def send_delivery_notification(self, to_number: str, rider_name: str) -> bool:
        """
        Send delivery arrival notification.
        
        Args:
            to_number: Recipient phone number
            rider_name: Rider name
            
        Returns:
            True if sent successfully
        """
        message = f"Your delivery is here! {rider_name} is waiting at your location."
        return await self.send_sms(to_number, message)


# Alternative: Termii for Africa
class TermiiService:
    """SMS service using Termii (for African markets)."""
    
    def __init__(self):
        self.api_key = settings.TERMII_API_KEY if hasattr(settings, 'TERMII_API_KEY') else None
        self.sender_id = settings.TERMII_SENDER_ID if hasattr(settings, 'TERMII_SENDER_ID') else "DeliveryApp"
    
    async def send_sms(self, to_number: str, message: str) -> bool:
        """Send SMS via Termii API."""
        if not self.api_key:
            logger.warning("Termii not configured")
            return False
        
        import httpx
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.ng.termii.com/api/sms/send",
                    json={
                        "to": to_number,
                        "from": self.sender_id,
                        "sms": message,
                        "type": "plain",
                        "channel": "generic",
                        "api_key": self.api_key
                    }
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Termii SMS error: {e}")
            return False
    
    async def send_otp(self, to_number: str, otp_code: str) -> bool:
        """Send OTP via Termii."""
        message = f"Your verification code is {otp_code}. Valid for 10 minutes."
        return await self.send_sms(to_number, message)


# M-Pesa Integration (Africa)
class MPesaService:
    """M-Pesa mobile money service."""
    
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY if hasattr(settings, 'MPESA_CONSUMER_KEY') else None
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET if hasattr(settings, 'MPESA_CONSUMER_SECRET') else None
        self.passkey = settings.MPESA_PASSKEY if hasattr(settings, 'MPESA_PASSKEY') else None
        self.shortcode = settings.MPESA_SHORTCODE if hasattr(settings, 'MPESA_SHORTCODE') else None
    
    async def stk_push(self, phone_number: str, amount: float, account_reference: str) -> dict:
        """
        Initiate STK Push payment.
        
        Args:
            phone_number: Customer phone (format: 254712345678)
            amount: Amount to charge
            account_reference: Order/payment reference
            
        Returns:
            Payment response
        """
        # TODO: Implement M-Pesa Daraja API integration
        logger.info(f"M-Pesa STK Push initiated: {phone_number}, {amount}")
        return {
            "status": "pending",
            "merchant_request_id": "pending_implementation",
            "checkout_request_id": "pending_implementation"
        }
