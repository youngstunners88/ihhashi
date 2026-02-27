from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = False  # Default to False for safety
    
    # Database
    mongodb_url: str = "mongodb://localhost:27017"
    db_name: str = "ihhashi"
    mongodb_max_pool_size: int = 100
    mongodb_min_pool_size: int = 10
    mongodb_timeout_ms: int = 30000
    
    # Security - REQUIRED in production
    secret_key: Optional[str] = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    auth_rate_limit: str = "5/minute"
    
    # South Africa Specific
    default_currency: str = "ZAR"
    supported_languages: list[str] = ["en", "zu", "xh", "af", "st", "tn", "so"]
    vat_rate: float = 0.15  # 15% VAT
    
    # Free Trial
    free_trial_days: int = 45
    free_trial_platform_fee_percent: float = 0.0  # No fees during trial
    standard_platform_fee_percent: float = 15.0  # 15% after trial
    
    # Supabase Configuration
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    
    # Payments - Paystack
    paystack_secret_key: str = ""
    paystack_public_key: str = ""
    paystack_webhook_secret: str = ""
    
    # Payments - Yoco (South Africa)
    yoco_secret_key: str = ""
    
    # Maps
    google_maps_api_key: str = ""
    
    # Firebase (Push Notifications)
    firebase_project_id: str = ""
    firebase_private_key_id: str = ""
    firebase_private_key: str = ""
    firebase_client_email: str = ""
    
    # Twilio (SMS)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # CORS (comma-separated origins for production)
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # Callback URLs (configurable)
    payment_callback_url: str = "https://ihhashi.app/payment/callback"
    
    # Monitoring - GlitchTip (Sentry-compatible)
    sentry_dsn: str = ""
    glitchtip_dsn: str = ""  # Alias for sentry_dsn
    posthog_api_key: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # CRITICAL: Fail fast if secret_key not set in production
        if self.environment == "production":
            if not self.secret_key:
                raise ValueError(
                    "CRITICAL: SECRET_KEY must be set in production environment. "
                    "Set the SECRET_KEY environment variable."
                )
            
            if self.secret_key and len(self.secret_key) < 32:
                raise ValueError(
                    "CRITICAL: SECRET_KEY must be at least 32 characters for security."
                )
            
            if "dev" in self.secret_key.lower() or "secret" in self.secret_key.lower():
                raise ValueError(
                    "CRITICAL: SECRET_KEY appears to be a default/placeholder value. "
                    "Generate a secure random key for production."
                )
        
        # Development fallback with warning
        if not self.secret_key:
            import secrets
            self.secret_key = secrets.token_urlsafe(32)
            if self.debug:
                print("WARNING: Using auto-generated SECRET_KEY. Set SECRET_KEY environment variable.")


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
