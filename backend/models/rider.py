from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RiderStatus(str, Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    BUSY = "busy"

class VehicleType(str, Enum):
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"
    CAR = "car"
    SCOOTER = "scooter"

class RiderLocation(BaseModel):
    latitude: float
    longitude: float
    last_updated: datetime

class RiderBase(BaseModel):
    phone: str
    full_name: str
    vehicle_type: VehicleType

class RiderCreate(RiderBase):
    pass

class Rider(RiderBase):
    id: str
    user_id: str
    status: RiderStatus = RiderStatus.OFFLINE
    current_location: Optional[RiderLocation] = None
    rating: float = 0.0
    total_deliveries: int = 0
    total_earnings: float = 0.0
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

class RiderEarnings(BaseModel):
    today: float
    this_week: float
    this_month: float
    total: float
