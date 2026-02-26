from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class ProductCategory(str, Enum):
    UTENSILS = "utensils"
    STATIONERY = "stationery"
    HOUSEHOLD = "household"
    ELECTRONICS = "electronics"
    GROCERIES = "groceries"
    OTHER = "other"


class ProductStatus(str, Enum):
    ACTIVE = "active"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


class Product(BaseModel):
    """Product available for purchase"""
    id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    store_id: str  # Reference to store
    
    # Basic info
    name: str
    description: Optional[str] = None
    category: ProductCategory
    
    # Pricing
    price: float
    currency: str = "ZAR"
    
    # Inventory
    stock_quantity: int = 0
    status: ProductStatus = ProductStatus.ACTIVE
    
    # Images
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    # Discovery
    tags: List[str] = []  # For search
    is_featured: bool = False
    is_popular: bool = False
    
    # Metrics
    times_ordered: int = 0
    avg_rating: Optional[float] = None
    review_count: int = 0
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Stainless Steel Spork",
                "description": "Durable 3-in-1 utensil",
                "category": "utensils",
                "price": 45.00,
                "stock_quantity": 50,
                "tags": ["camping", "eco-friendly", "utensils"]
            }
        }


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: ProductCategory
    price: float
    stock_quantity: int = 0
    image_url: Optional[str] = None
    tags: List[str] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    status: Optional[ProductStatus] = None