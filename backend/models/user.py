from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    CUSTOMER = "customer"
    MERCHANT = "merchant"
    RIDER = "rider"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    phone: str
    full_name: str

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.CUSTOMER

class User(UserBase):
    id: str
    role: UserRole
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class UserLocation(BaseModel):
    latitude: float
    longitude: float
    address: str
    city: str
    province: str

class UserWithLocation(User):
    location: Optional[UserLocation] = None
