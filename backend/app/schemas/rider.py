"""Rider schemas."""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RiderStatus(str, Enum):
    """Rider status enum."""
    OFFLINE = "offline"
    ONLINE = "online"
    BUSY = "busy"
    ON_DELIVERY = "on_delivery"


class VehicleType(str, Enum):
    """Vehicle type enum."""
    BICYCLE = "bicycle"
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    VAN = "van"


class RiderBase(BaseModel):
    """Base rider schema."""
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    email: str
    vehicle_type: VehicleType
    vehicle_plate: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False


class RiderCreate(RiderBase):
    """Rider creation schema."""
    password: str = Field(..., min_length=8, max_length=100)
    license_number: Optional[str] = None


class RiderUpdate(BaseModel):
    """Rider update schema."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    vehicle_plate: Optional[str] = None
    is_active: Optional[bool] = None
    status: Optional[RiderStatus] = None
    current_location: Optional[dict] = None


class RiderInDB(RiderBase):
    """Rider in database schema."""
    id: str = Field(..., alias="_id")
    hashed_password: str
    status: RiderStatus = RiderStatus.OFFLINE
    current_location: Optional[dict] = None
    rating: Decimal = Field(default=Decimal("5.0"), ge=0, le=5)
    total_deliveries: int = 0
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    license_number: Optional[str] = None
    profile_image: Optional[str] = None

    class Config:
        populate_by_name = True


class Rider(RiderBase):
    """Rider response schema."""
    id: str = Field(..., alias="_id")
    status: RiderStatus
    current_location: Optional[dict] = None
    rating: Decimal
    total_deliveries: int
    created_at: datetime

    class Config:
        populate_by_name = True


class RiderLocationUpdate(BaseModel):
    """Rider location update schema."""
    rider_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None
