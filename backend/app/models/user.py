from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class UserRole(str, Enum):
    CUSTOMER = "customer"
    MERCHANT = "merchant"
    RIDER = "rider"
    ADMIN = "admin"


class UserLocation(BaseModel):
    """User's location data"""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    area: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    updated_at: Optional[datetime] = None


class User(BaseModel):
    """Core user model"""
    id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    email: Optional[EmailStr] = None
    phone: str = Field(..., unique=True, index=True)
    full_name: Optional[str] = None
    hashed_password: Optional[str] = None
    
    # Role and status
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True
    is_verified: bool = False
    
    # Location
    location: Optional[UserLocation] = None
    
    # Profile
    profile_photo: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: Optional[EmailStr] = None
    phone: str
    full_name: Optional[str] = None
    password: str
    role: UserRole = UserRole.CUSTOMER


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user info"""
    full_name: Optional[str] = None
    profile_photo: Optional[str] = None
    location: Optional[UserLocation] = None