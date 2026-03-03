"""Push notification service with Firebase Cloud Messaging."""
import logging
from typing import List, Optional, Dict, Any
import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError

from app.config import settings

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Firebase Cloud Messaging push notification service."""
    
    _initialized = False
    
    def __init__(self):
        if not self._initialized:
            self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        try:
            # Check if already initialized
            firebase_admin.get_app()
            self._initialized = True
        except ValueError:
            # Initialize with credentials
            cred_path = settings.FIREBASE_CREDENTIALS_PATH if hasattr(settings, 'FIREBASE_CREDENTIALS_PATH') else None
            
            if cred_path:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self._initialized = True
                logger.info("Firebase initialized successfully")
            else:
                logger.warning("Firebase credentials not configured")
    
    async def send_to_token(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> bool:
        """
        Send push notification to a single device.
        
        Args:
            token: FCM device token
            title: Notification title
            body: Notification body
            data: Custom data payload
            image_url: Image URL for notification
            
        Returns:
            True if sent successfully
        """
        if not self._initialized:
            logger.warning("Firebase not initialized")
            return False
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url
                ),
                data=data or {},
                token=token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='default_channel'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(sound='default')
                    )
                )
            )
            
            response = messaging.send(message)
            logger.info(f"Push notification sent: {response}")
            return True
            
        except FirebaseError as e:
            logger.error(f"Firebase error sending notification: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return False
    
    async def send_to_tokens(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> messaging.BatchResponse:
        """
        Send push notification to multiple devices.
        
        Args:
            tokens: List of FCM device tokens
            title: Notification title
            body: Notification body
            data: Custom data payload
            
        Returns:
            Batch response with success/failure counts
        """
        if not self._initialized:
            logger.warning("Firebase not initialized")
            return messaging.BatchResponse(responses=[])
        
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=tokens
            )
            
            response = messaging.send_multicast(message)
            logger.info(
                f"Multicast sent: {response.success_count} successful, "
                f"{response.failure_count} failed"
            )
            return response
            
        except Exception as e:
            logger.error(f"Error sending multicast: {e}")
            return messaging.BatchResponse(responses=[])
    
    async def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send push notification to a topic.
        
        Args:
            topic: FCM topic name
            title: Notification title
            body: Notification body
            data: Custom data payload
            
        Returns:
            True if sent successfully
        """
        if not self._initialized:
            logger.warning("Firebase not initialized")
            return False
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                topic=topic
            )
            
            response = messaging.send(message)
            logger.info(f"Topic notification sent: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending topic notification: {e}")
            return False
    
    async def subscribe_to_topic(self, tokens: List[str], topic: str) -> bool:
        """
        Subscribe tokens to a topic.
        
        Args:
            tokens: List of FCM tokens
            topic: Topic name
            
        Returns:
            True if successful
        """
        if not self._initialized:
            return False
        
        try:
            response = messaging.subscribe_to_topic(tokens, topic)
            logger.info(f"Subscribed to topic {topic}: {response.success_count} successful")
            return True
        except Exception as e:
            logger.error(f"Error subscribing to topic: {e}")
            return False
    
    async def unsubscribe_from_topic(self, tokens: List[str], topic: str) -> bool:
        """Unsubscribe tokens from a topic."""
        if not self._initialized:
            return False
        
        try:
            response = messaging.unsubscribe_from_topic(tokens, topic)
            logger.info(f"Unsubscribed from topic {topic}: {response.success_count} successful")
            return True
        except Exception as e:
            logger.error(f"Error unsubscribing from topic: {e}")
            return False
    
    # Convenience methods for common notifications
    
    async def notify_order_status(
        self,
        token: str,
        order_id: str,
        status: str
    ) -> bool:
        """Send order status update notification."""
        return await self.send_to_token(
            token=token,
            title="Order Update",
            body=f"Your order #{order_id} is now {status}",
            data={"order_id": order_id, "status": status, "type": "order_update"}
        )
    
    async def notify_delivery_arrival(self, token: str, rider_name: str) -> bool:
        """Send delivery arrival notification."""
        return await self.send_to_token(
            token=token,
            title="Delivery Arrived!",
            body=f"{rider_name} has arrived with your order",
            data={"type": "delivery_arrival"}
        )
    
    async def notify_new_order_to_rider(self, token: str, order_details: Dict) -> bool:
        """Send new order notification to rider."""
        return await self.send_to_token(
            token=token,
            title="New Order Available!",
            body=f"Pickup from {order_details.get('restaurant_name')}",
            data={
                "type": "new_order",
                "order_id": order_details.get('order_id'),
                "pickup_address": order_details.get('pickup_address'),
                "delivery_address": order_details.get('delivery_address')
            }
        )
    
    async def notify_promotion(
        self,
        tokens: List[str],
        title: str,
        body: str,
        promo_code: str
    ) -> messaging.BatchResponse:
        """Send promotional notification to multiple users."""
        return await self.send_to_tokens(
            tokens=tokens,
            title=title,
            body=body,
            data={"type": "promotion", "promo_code": promo_code}
        )
