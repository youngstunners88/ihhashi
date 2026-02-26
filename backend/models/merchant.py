from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MerchantCategory(str, Enum):
    RESTAURANT = "restaurant"
    GROCERY = "grocery"
    PHARMACY = "pharmacy"
    RETAIL = "retail"
    OTHER = "other"

class BusinessHours(BaseModel):
    open: str  # "08:00"
    close: str  # "20:00"
    days: List[str] = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

class MerchantLocation(BaseModel):
    latitude: float
    longitude: float
    address: str
    city: str
    province: str

class MerchantBase(BaseModel):
    name: str
    description: str
    category: MerchantCategory
    phone: str
    email: str

class MerchantCreate(MerchantBase):
    location: MerchantLocation
    business_hours: BusinessHours

class MenuItem(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    is_available: bool = True

class Merchant(MerchantBase):
    id: str
    owner_id: str
    location: MerchantLocation
    business_hours: BusinessHours
    menu: List[MenuItem] = []
    rating: float = 0.0
    total_reviews: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
