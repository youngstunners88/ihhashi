"""User schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    full_name: str = Field(..., min_length=2, max_length=100)
    is_active: bool = True
    is_verified: bool = False


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """User in database schema."""
    id: str = Field(..., alias="_id")
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    profile_image: Optional[str] = None
    default_address: Optional[dict] = None

    class Config:
        populate_by_name = True


class User(UserBase):
    """User response schema."""
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime
    profile_image: Optional[str] = None

    class Config:
        populate_by_name = True


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str


class UserPasswordReset(BaseModel):
    """Password reset schema."""
    email: EmailStr


class UserPasswordChange(BaseModel):
    """Password change schema."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
