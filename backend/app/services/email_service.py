"""Email service with SendGrid integration."""
import logging
from typing import Optional, Dict, Any
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from python_http_client.exceptions import HTTPError

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service using SendGrid."""
    
    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY if hasattr(settings, 'SENDGRID_API_KEY') else None
        self.from_email = settings.FROM_EMAIL if hasattr(settings, 'FROM_EMAIL') else "noreply@deliveryapp.com"
        
        if self.api_key:
            self.client = SendGridAPIClient(self.api_key)
        else:
            self.client = None
            logger.warning("SendGrid API key not configured")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send email.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML content
            text_content: Plain text content
            
        Returns:
            True if sent successfully
        """
        if not self.client:
            logger.warning("Email service not configured")
            return False
        
        try:
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content) if html_content else None,
                plain_text_content=Content("text/plain", text_content) if text_content else None
            )
            
            response = self.client.send(message)
            
            if response.status_code in [200, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.warning(f"Email send returned status {response.status_code}")
                return False
                
        except HTTPError as e:
            logger.error(f"SendGrid HTTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    async def send_welcome_email(self, to_email: str, name: str) -> bool:
        """Send welcome email to new users."""
        subject = "Welcome to Delivery App!"
        html_content = f"""
        <html>
        <body>
            <h1>Welcome to Delivery App, {name}!</h1>
            <p>Thank you for joining us. Start ordering delicious food from your favorite restaurants.</p>
            <p>Download our mobile app for the best experience:</p>
            <ul>
                <li><a href="#">Download for iOS</a></li>
                <li><a href="#">Download for Android</a></li>
            </ul>
        </body>
        </html>
        """
        return await self.send_email(to_email, subject, html_content)
    
    async def send_order_confirmation(self, to_email: str, order_details: Dict[str, Any]) -> bool:
        """Send order confirmation email."""
        subject = f"Order Confirmation - #{order_details.get('order_id')}"
        html_content = f"""
        <html>
        <body>
            <h1>Order Confirmed!</h1>
            <p>Thank you for your order. Here are the details:</p>
            <p><strong>Order ID:</strong> {order_details.get('order_id')}</p>
            <p><strong>Total:</strong> ${order_details.get('total')}</p>
            <p><strong>Estimated Delivery:</strong> {order_details.get('estimated_delivery')}</p>
            <p>Track your order in the app.</p>
        </body>
        </html>
        """
        return await self.send_email(to_email, subject, html_content)
    
    async def send_password_reset(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email."""
        reset_url = f"https://yourapp.com/reset-password?token={reset_token}"
        subject = "Password Reset Request"
        html_content = f"""
        <html>
        <body>
            <h1>Password Reset</h1>
            <p>You requested a password reset. Click the link below to reset your password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link expires in 1 hour.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
        </html>
        """
        return await self.send_email(to_email, subject, html_content)


# Alternative: SMTP for self-hosted email
class SMTPEmailService:
    """Email service using SMTP (for self-hosted)."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST if hasattr(settings, 'SMTP_HOST') else None
        self.smtp_port = settings.SMTP_PORT if hasattr(settings, 'SMTP_PORT') else 587
        self.smtp_user = settings.SMTP_USER if hasattr(settings, 'SMTP_USER') else None
        self.smtp_password = settings.SMTP_PASSWORD if hasattr(settings, 'SMTP_PASSWORD') else None
        self.from_email = settings.FROM_EMAIL if hasattr(settings, 'FROM_EMAIL') else "noreply@deliveryapp.com"
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email via SMTP."""
        import aiosmtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        if not self.smtp_host:
            logger.warning("SMTP not configured")
            return False
        
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject
            
            if text_content:
                message.attach(MIMEText(text_content, "plain"))
            if html_content:
                message.attach(MIMEText(html_content, "html"))
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )
            
            logger.info(f"Email sent via SMTP to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"SMTP error: {e}")
            return False
