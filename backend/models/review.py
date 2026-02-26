from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ReviewTargetType(str, Enum):
    MERCHANT = "merchant"
    RIDER = "rider"
    PRODUCT = "product"
    CUSTOMER = "customer"  # Riders can rate customers too

class ReviewBase(BaseModel):
    rating: int  # 1-5 stars
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    target_id: str
    target_type: ReviewTargetType
    order_id: Optional[str] = None

class Review(ReviewBase):
    id: str
    reviewer_id: str
    reviewer_type: str  # "customer", "rider", "merchant"
    target_id: str
    target_type: ReviewTargetType
    order_id: Optional[str] = None
    is_verified_purchase: bool = True
    helpful_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

class ReviewResponse(BaseModel):
    """Merchant/Rider response to a review"""
    id: str
    review_id: str
    responder_id: str
    response: str
    created_at: datetime

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    review_id: str

class Comment(CommentBase):
    id: str
    review_id: str
    author_id: str
    author_type: str  # "customer", "rider", "merchant", "admin"
    created_at: datetime
