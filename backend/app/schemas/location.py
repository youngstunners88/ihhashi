"""Location schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Location(BaseModel):
    """Location schema."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str
    city: str
    state: Optional[str] = None
    country: str
    postal_code: Optional[str] = None
    formatted_address: Optional[str] = None


class LocationUpdate(BaseModel):
    """Location update schema."""
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address: Optional[str] = None
    city: Optional[str] = None


class GeocodeRequest(BaseModel):
    """Geocode request schema."""
    address: str


class GeocodeResponse(BaseModel):
    """Geocode response schema."""
    latitude: float
    longitude: float
    formatted_address: str
    place_id: Optional[str] = None


class DistanceRequest(BaseModel):
    """Distance calculation request."""
    origin: Location
    destination: Location


class DistanceResponse(BaseModel):
    """Distance calculation response."""
    distance_meters: int
    duration_seconds: int
    distance_text: str
    duration_text: str
