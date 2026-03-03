"""Restaurant schemas."""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class RestaurantBase(BaseModel):
    """Base restaurant schema."""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    phone: str = Field(..., min_length=10, max_length=20)
    email: str
    address: dict
    cuisine_type: List[str] = []
    is_active: bool = True
    is_open: bool = False


class RestaurantCreate(RestaurantBase):
    """Restaurant creation schema."""
    password: str = Field(..., min_length=8, max_length=100)
    business_hours: dict


class RestaurantUpdate(BaseModel):
    """Restaurant update schema."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[str] = None
    address: Optional[dict] = None
    cuisine_type: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_open: Optional[bool] = None
    business_hours: Optional[dict] = None


class RestaurantInDB(RestaurantBase):
    """Restaurant in database schema."""
    id: str = Field(..., alias="_id")
    hashed_password: str
    rating: Decimal = Field(default=Decimal("0.0"), ge=0, le=5)
    total_reviews: int = 0
    minimum_order: Decimal = Field(default=Decimal("0.0"), ge=0)
    delivery_fee: Decimal = Field(default=Decimal("0.0"), ge=0)
    estimated_delivery_time: int = 30  # minutes
    business_hours: dict
    created_at: datetime
    updated_at: datetime
    logo_image: Optional[str] = None
    banner_image: Optional[str] = None

    class Config:
        populate_by_name = True


class Restaurant(RestaurantBase):
    """Restaurant response schema."""
    id: str = Field(..., alias="_id")
    rating: Decimal
    total_reviews: int
    minimum_order: Decimal
    delivery_fee: Decimal
    estimated_delivery_time: int
    created_at: datetime
    logo_image: Optional[str] = None

    class Config:
        populate_by_name = True
