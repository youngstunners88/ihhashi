from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Database
    mongodb_url: str = "mongodb://localhost:27017"
    db_name: str = "ihhashi"
    
    # Security
    secret_key: str  # Required - must be set in .env (no default!)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    auth_rate_limit: str = "5/minute"

    # South Africa Specific
    default_currency: str = "ZAR"
    supported_languages: list[str] = ["en", "zu", "xh", "af", "st", "tn", "so"]
    # en=English, zu=Zulu, xh=Xhosa, af=Afrikaans, st=Sotho, tn=Tswana, so=Sotho(Southern)
    vat_rate: float = 0.15  # 15% VAT

    # Free Trial
    free_trial_days: int = 45
    free_trial_platform_fee_percent: float = 0.0  # No fees during trial
    standard_platform_fee_percent: float = 15.0  # 15% after trial

    # Supabase Configuration
    supabase_url: str = "https://tehxyuhsyqzroklplvcf.supabase.co"
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    
    # Payments - Paystack
    paystack_secret_key: str = ""
    paystack_public_key: str = ""
    
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
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # CORS (comma-separated origins for production)
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Monitoring - GlitchTip (Sentry-compatible)
    sentry_dsn: str = "https://25a5585d096a411495f93126742fbf73@app.glitchtip.com/20760"
    posthog_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
