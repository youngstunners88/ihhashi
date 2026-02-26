from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TransportMode(str, Enum):
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"
    CAR = "car"
    SCOOTER = "scooter"
    ON_FOOT = "on_foot"  # Walking

class DeliveryPricingBase(BaseModel):
    """Rider-set pricing for their services"""
    base_fee: float  # Minimum fee for any delivery
    per_km_rate: float  # Rate per kilometer
    per_kg_rate: Optional[float] = None  # Rate per kg (optional)
    min_order_value: float = 0.0  # Minimum order value they'll accept
    max_distance_km: float = 10.0  # Maximum delivery radius

class DeliveryPricingCreate(DeliveryPricingBase):
    transport_mode: TransportMode

class DeliveryPricing(DeliveryPricingBase):
    id: str
    rider_id: str
    transport_mode: TransportMode
    is_active: bool = True
    surge_multiplier: float = 1.0  # Rider can increase during peak times
    created_at: datetime
    updated_at: datetime

class RiderAvailability(BaseModel):
    rider_id: str
    is_available: bool
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    service_area: Optional[str] = None  # City/suburb
    last_location_update: Optional[datetime] = None

class DeliveryQuote(BaseModel):
    """Quote shown to customer before ordering"""
    rider_id: str
    rider_name: str
    rider_rating: float
    transport_mode: TransportMode
    estimated_delivery_minutes: int
    base_fee: float
    distance_fee: float
    total_fee: float
    is_blue_horse: bool  # Verified rider badge
