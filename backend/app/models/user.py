from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class UserRole(str, Enum):
    BUYER = "buyer"
    MERCHANT = "merchant"
    DRIVER = "driver"
    ADMIN = "admin"


class User(BaseModel):
    """User model for authentication"""
    id: str
    email: EmailStr
    phone: Optional[str] = None
    full_name: Optional[str] = None
    role: UserRole = UserRole.BUYER
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Create new user"""
    email: EmailStr
    phone: Optional[str] = None
    full_name: Optional[str] = None
    password: str
    role: UserRole = UserRole.BUYER


class UserLogin(BaseModel):
    """Login credentials"""
    email: str
    password: str


class UserUpdate(BaseModel):
    """Update user profile"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
