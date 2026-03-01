"""
Firebase Cloud Messaging (FCM) service for iHhashi push notifications.

Initialisation reads Firebase credentials from environment variables
(same keys defined in .env.example under FIREBASE_*).

Usage:
    from app.services.fcm import send_notification, send_multicast

    await send_notification(token="<device_fcm_token>", title="…", body="…")
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy Firebase Admin initialisation
# ---------------------------------------------------------------------------
_firebase_initialised = False


def _init_firebase() -> bool:
    """Initialise the Firebase Admin SDK once. Returns True on success."""
    global _firebase_initialised
    if _firebase_initialised:
        return True

    project_id = os.getenv("FIREBASE_PROJECT_ID")
    private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
    client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
    private_key_id = os.getenv("FIREBASE_PRIVATE_KEY_ID")

    if not all([project_id, private_key, client_email]):
        logger.warning(
            "Firebase credentials not fully configured — push notifications disabled. "
            "Set FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY, and FIREBASE_CLIENT_EMAIL."
        )
        return False

    try:
        import firebase_admin
        from firebase_admin import credentials

        if not firebase_admin._apps:
            cred_dict = {
                "type": "service_account",
                "project_id": project_id,
                "private_key_id": private_key_id or "",
                "private_key": private_key,
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)

        _firebase_initialised = True
        logger.info("Firebase Admin SDK initialised for project: %s", project_id)
        return True

    except Exception as exc:
        logger.error("Failed to initialise Firebase Admin SDK: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

async def send_notification(
    token: str,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
    image_url: str | None = None,
) -> bool:
    """
    Send a push notification to a single device token.

    Returns True on success, False if FCM is unconfigured or the send fails.
    All values in `data` must be strings (FCM requirement).
    """
    if not _init_firebase():
        return False

    try:
        from firebase_admin import messaging

        notification = messaging.Notification(title=title, body=body, image=image_url)
        android_config = messaging.AndroidConfig(
            priority="high",
            notification=messaging.AndroidNotification(
                sound="default",
                channel_id="ihhashi_orders",
            ),
        )
        apns_config = messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(sound="default", badge=1)
            )
        )

        message = messaging.Message(
            token=token,
            notification=notification,
            data=data or {},
            android=android_config,
            apns=apns_config,
        )

        message_id = messaging.send(message)
        logger.debug("FCM message sent: %s", message_id)
        return True

    except Exception as exc:
        logger.error("FCM send_notification failed: %s", exc)
        return False


async def send_multicast(
    tokens: list[str],
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> int:
    """
    Send a notification to multiple device tokens.

    Returns the number of successful sends.
    """
    if not tokens:
        return 0
    if not _init_firebase():
        return 0

    try:
        from firebase_admin import messaging

        message = messaging.MulticastMessage(
            tokens=tokens,
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            android=messaging.AndroidConfig(priority="high"),
        )
        response = messaging.send_each_for_multicast(message)
        success_count: int = response.success_count
        if response.failure_count:
            logger.warning(
                "FCM multicast: %d sent, %d failed",
                success_count,
                response.failure_count,
            )
        return success_count

    except Exception as exc:
        logger.error("FCM send_multicast failed: %s", exc)
        return 0


# ---------------------------------------------------------------------------
# Order-event notification helpers
# ---------------------------------------------------------------------------

async def notify_rider_new_delivery(
    token: str,
    delivery_id: str,
    pickup_address: str = "",
) -> bool:
    return await send_notification(
        token=token,
        title="New Delivery Request!",
        body=f"Pickup: {pickup_address or 'Tap to view details'}",
        data={"type": "delivery_request", "delivery_id": delivery_id},
    )


async def notify_customer_order_update(
    token: str,
    order_id: str,
    status: str,
    message: str,
) -> bool:
    status_titles = {
        "confirmed": "Order Confirmed",
        "preparing": "Preparing Your Order",
        "ready": "Order Ready for Pickup",
        "picked_up": "Rider Has Your Order",
        "in_transit": "Order On the Way",
        "delivered": "Order Delivered!",
        "cancelled": "Order Cancelled",
    }
    title = status_titles.get(status, "Order Update")
    return await send_notification(
        token=token,
        title=title,
        body=message,
        data={"type": "order_update", "order_id": order_id, "status": status},
    )


async def notify_merchant_new_order(
    token: str,
    order_id: str,
    item_summary: str,
) -> bool:
    return await send_notification(
        token=token,
        title="New Order Received!",
        body=item_summary or "Tap to view and confirm",
        data={"type": "new_order", "order_id": order_id},
    )
