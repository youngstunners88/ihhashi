from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class TripStatus(str, Enum):
    REQUESTED = "requested"  # Customer requested, looking for driver
    DRIVER_ASSIGNED = "driver_assigned"  # Driver matched, heading to pickup
    DRIVER_ARRIVED = "driver_arrived"  # Driver at pickup location
    IN_PROGRESS = "in_progress"  # Trip underway
    COMPLETED = "completed"  # Trip finished
    CANCELLED = "cancelled"  # Trip cancelled


class VehicleType(str, Enum):
    STANDARD = "standard"  # Regular taxi
    LUXURY = "luxury"  # Premium vehicle
    DELIVERY = "delivery"  # Delivery vehicle


class Location(BaseModel):
    """GPS location"""
    latitude: float
    longitude: float
    address: Optional[str] = None


class TripFare(BaseModel):
    """Fare breakdown"""
    base_fare: float
    distance_km: float
    distance_cost: float
    time_cost: float = 0.0
    surge_multiplier: float = 1.0
    total: float
    currency: str = "ZAR"


class Trip(BaseModel):
    """Trip model for taxi/delivery rides"""
    id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    
    # Parties
    customer_id: str
    driver_id: Optional[str] = None
    
    # Locations
    pickup_location: Location
    dropoff_location: Location
    
    # Trip details
    vehicle_type: VehicleType = VehicleType.STANDARD
    status: TripStatus = TripStatus.REQUESTED
    
    # Fare
    fare: Optional[TripFare] = None
    payment_method: str = "cash"
    payment_status: str = "pending"
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    driver_assigned_at: Optional[datetime] = None
    pickup_time: Optional[datetime] = None
    dropoff_time: Optional[datetime] = None
    
    # Status tracking
    cancel_reason: Optional[str] = None
    
    # Safety features
    emergency_contact_notified: bool = False
    trip_shared_with: List[str] = []  # Emergency contact IDs
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "customer-123",
                "pickup_location": {
                    "latitude": -26.2041,
                    "longitude": 28.0473,
                    "address": "123 Main Street, Johannesburg"
                },
                "dropoff_location": {
                    "latitude": -26.1951,
                    "longitude": 28.0339,
                    "address": "456 Oak Avenue, Johannesburg"
                },
                "vehicle_type": "standard"
            }
        }


class TripRequest(BaseModel):
    """Request to create a new trip"""
    pickup_latitude: float
    pickup_longitude: float
    pickup_address: Optional[str] = None
    dropoff_latitude: float
    dropoff_longitude: float
    dropoff_address: Optional[str] = None
    vehicle_type: VehicleType = VehicleType.STANDARD
    payment_method: str = "cash"


class TripLocationUpdate(BaseModel):
    """Driver location update during trip"""
    latitude: float
    longitude: float


# Alias for backwards compatibility
TripCreate = TripRequest