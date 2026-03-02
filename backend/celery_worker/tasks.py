"""Celery background tasks."""
import logging
from datetime import datetime, timedelta
from celery import Celery

from app.config import settings
from app.services.email_service import EmailService
from app.services.sms_service import SMSService
from app.services.push_notification import PushNotificationService
from app.database import get_db

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "delivery_app",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["celery_worker.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Initialize services
email_service = EmailService()
sms_service = SMSService()
push_service = PushNotificationService()


@celery_app.task(bind=True, max_retries=3)
def send_email_task(self, to_email: str, subject: str, html_content: str, text_content: str = None):
    """Send email in background."""
    try:
        import asyncio
        asyncio.run(email_service.send_email(to_email, subject, html_content, text_content))
        logger.info(f"Email task completed for {to_email}")
        return {"status": "sent", "to": to_email}
    except Exception as exc:
        logger.error(f"Email task failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def send_sms_task(self, to_number: str, message: str):
    """Send SMS in background."""
    try:
        import asyncio
        asyncio.run(sms_service.send_sms(to_number, message))
        logger.info(f"SMS task completed for {to_number}")
        return {"status": "sent", "to": to_number}
    except Exception as exc:
        logger.error(f"SMS task failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def send_push_notification_task(self, token: str, title: str, body: str, data: dict = None):
    """Send push notification in background."""
    try:
        import asyncio
        asyncio.run(push_service.send_to_token(token, title, body, data))
        logger.info(f"Push notification task completed")
        return {"status": "sent"}
    except Exception as exc:
        logger.error(f"Push notification task failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task
def process_order_confirmation(order_id: str, user_email: str, user_phone: str, fcm_token: str = None):
    """Process order confirmation notifications."""
    logger.info(f"Processing order confirmation for {order_id}")
    
    # Send email
    if user_email:
        send_email_task.delay(
            to_email=user_email,
            subject=f"Order Confirmed - #{order_id}",
            html_content=f"<h1>Order #{order_id} Confirmed!</h1><p>Thank you for your order.</p>"
        )
    
    # Send SMS
    if user_phone:
        send_sms_task.delay(
            to_number=user_phone,
            message=f"Your order #{order_id} has been confirmed and is being prepared."
        )
    
    # Send push notification
    if fcm_token:
        send_push_notification_task.delay(
            token=fcm_token,
            title="Order Confirmed!",
            body=f"Your order #{order_id} is being prepared",
            data={"order_id": order_id, "type": "order_confirmed"}
        )
    
    return {"status": "completed", "order_id": order_id}


@celery_app.task
def notify_delivery_arrival(order_id: str, user_phone: str, fcm_token: str = None, rider_name: str = "Your rider"):
    """Notify customer that delivery has arrived."""
    logger.info(f"Notifying delivery arrival for {order_id}")
    
    message = f"{rider_name} has arrived with your order #{order_id}!"
    
    if user_phone:
        send_sms_task.delay(to_number=user_phone, message=message)
    
    if fcm_token:
        send_push_notification_task.delay(
            token=fcm_token,
            title="Delivery Arrived!",
            body=message,
            data={"order_id": order_id, "type": "delivery_arrival"}
        )
    
    return {"status": "completed", "order_id": order_id}


@celery_app.task
def cleanup_expired_otp_codes():
    """Clean up expired OTP codes from database."""
    logger.info("Cleaning up expired OTP codes")
    # Implementation depends on OTP storage
    return {"status": "completed"}


@celery_app.task
def generate_daily_report():
    """Generate daily order/delivery report."""
    logger.info("Generating daily report")
    # Implementation for analytics/reporting
    return {"status": "completed"}


@celery_app.task
def backup_database():
    """Trigger database backup."""
    logger.info("Starting database backup")
    # Implementation for MongoDB backup
    return {"status": "completed"}


# Scheduled tasks configuration
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Set up periodic tasks."""
    # Clean up expired OTPs every hour
    sender.add_periodic_task(
        3600.0,
        cleanup_expired_otp_codes.s(),
        name="cleanup-expired-otps"
    )
    
    # Daily report at midnight
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        generate_daily_report.s(),
        name="daily-report"
    )
    
    # Database backup daily at 2 AM
    sender.add_periodic_task(
        crontab(hour=2, minute=0),
        backup_database.s(),
        name="daily-backup"
    )


def crontab(hour, minute):
    """Create crontab schedule."""
    from celery.schedules import crontab as c
    return c(hour=hour, minute=minute)
