"""
Application configuration with environment-driven MongoDB settings.
"""
import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with env-driven configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
    # Application settings
    APP_NAME: str = "Delivery App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = Field(default="change-me-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["*"]
    
    # MongoDB settings - all env-driven
    MONGODB_URL: str = Field(default="mongodb://localhost:27017/delivery_app")
    MONGODB_DB_NAME: str = Field(default="delivery_app")
    
    # MongoDB connection pool settings (all env-driven)
    MONGODB_MAX_POOL_SIZE: int = Field(default=100, description="Maximum number of connections in the pool")
    MONGODB_MIN_POOL_SIZE: int = Field(default=10, description="Minimum number of connections in the pool")
    MONGODB_MAX_IDLE_TIME_MS: int = Field(default=60000, description="Maximum time a connection can remain idle in ms")
    MONGODB_WAIT_QUEUE_TIMEOUT_MS: int = Field(default=5000, description="Maximum time to wait for a connection from the pool in ms")
    MONGODB_CONNECT_TIMEOUT_MS: int = Field(default=10000, description="Maximum time to establish a connection in ms")
    MONGODB_SOCKET_TIMEOUT_MS: int = Field(default=30000, description="Maximum time for socket operations in ms")
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = Field(default=30000, description="Maximum time to select a server in ms")
    
    # Redis settings
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_PASSWORD: Optional[str] = Field(default=None)
    
    # WebSocket settings
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_PING_TIMEOUT: int = 10
    
    # Instance identification for horizontal scaling
    INSTANCE_ID: str = Field(default_factory=lambda: os.getenv("INSTANCE_ID", "default"))
    
    # Pub/Sub channels
    PUBSUB_ORDER_CHANNEL: str = "order_updates"
    PUBSUB_RIDER_CHANNEL: str = "rider_updates"
    PUBSUB_USER_CHANNEL: str = "user_updates"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # External services
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_PRIVATE_KEY: Optional[str] = None
    FIREBASE_CLIENT_EMAIL: Optional[str] = None
    
    # Sentry/Crash reporting
    SENTRY_DSN: Optional[str] = None
    
    # Payment processing
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    @property
    def mongodb_connection_options(self) -> dict:
        """Get MongoDB connection options with all configured settings."""
        return {
            "maxPoolSize": self.MONGODB_MAX_POOL_SIZE,
            "minPoolSize": self.MONGODB_MIN_POOL_SIZE,
            "maxIdleTimeMS": self.MONGODB_MAX_IDLE_TIME_MS,
            "waitQueueTimeoutMS": self.MONGODB_WAIT_QUEUE_TIMEOUT_MS,
            "connectTimeoutMS": self.MONGODB_CONNECT_TIMEOUT_MS,
            "socketTimeoutMS": self.MONGODB_SOCKET_TIMEOUT_MS,
            "serverSelectionTimeoutMS": self.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
        }
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
