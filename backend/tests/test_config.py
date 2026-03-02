"""Tests for configuration module."""
import pytest
from app.config import Settings, get_settings


def test_settings_default_values():
    """Test default settings values."""
    settings = Settings()
    
    assert settings.APP_NAME == "Delivery App"
    assert settings.MONGODB_MAX_POOL_SIZE == 100
    assert settings.MONGODB_MIN_POOL_SIZE == 10
    assert settings.MONGODB_MAX_IDLE_TIME_MS == 60000
    assert settings.MONGODB_WAIT_QUEUE_TIMEOUT_MS == 5000
    assert settings.MONGODB_CONNECT_TIMEOUT_MS == 10000
    assert settings.MONGODB_SOCKET_TIMEOUT_MS == 30000
    assert settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS == 30000


def test_mongodb_connection_options():
    """Test MongoDB connection options generation."""
    settings = Settings()
    options = settings.mongodb_connection_options
    
    assert options["maxPoolSize"] == 100
    assert options["minPoolSize"] == 10
    assert options["maxIdleTimeMS"] == 60000
    assert options["waitQueueTimeoutMS"] == 5000
    assert options["connectTimeoutMS"] == 10000
    assert options["socketTimeoutMS"] == 30000
    assert options["serverSelectionTimeoutMS"] == 30000


def test_get_settings_cached():
    """Test that get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2
