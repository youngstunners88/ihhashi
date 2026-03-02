"""Tests for WebSocket functionality."""
import pytest
from app.routes.websocket import ConnectionType


def test_connection_type_enum():
    """Test ConnectionType enum values."""
    assert ConnectionType.USER.value == "user"
    assert ConnectionType.RIDER.value == "rider"
    assert ConnectionType.ADMIN.value == "admin"
    assert ConnectionType.RESTAURANT.value == "restaurant"
