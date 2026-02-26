from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"

class ProductCategory(str, Enum):
    FOOD = "food"
    GROCERY = "grocery"
    PHARMACY = "pharmacy"
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    OTHER = "other"

class ProductImage(BaseModel):
    id: str
    url: str
    alt_text: Optional[str] = None
    is_primary: bool = False
    uploaded_at: datetime

class ProductVariant(BaseModel):
    id: str
    name: str  # e.g., "Small", "Large", "500ml"
    price: float
    stock: int
    sku: Optional[str] = None

class ProductBase(BaseModel):
    name: str
    description: str
    category: ProductCategory
    base_price: float

class ProductCreate(ProductBase):
    merchant_id: str
    images: Optional[List[str]] = None  # Image URLs
    variants: Optional[List[ProductVariant]] = None
    preparation_time_minutes: int = 15
    is_available: bool = True

class Product(ProductBase):
    id: str
    merchant_id: str
    slug: str  # URL-friendly name
    images: List[ProductImage] = []
    variants: List[ProductVariant] = []
    preparation_time_minutes: int = 15
    is_available: bool = True
    status: ProductStatus = ProductStatus.ACTIVE
    rating: float = 0.0
    total_reviews: int = 0
    total_orders: int = 0
    created_at: datetime
    updated_at: datetime

class ProductTemplate(BaseModel):
    """Standardized template for merchants to create products"""
    category: ProductCategory
    required_fields: List[str]
    recommended_fields: List[str]
    image_guidelines: str
    price_guidelines: str
    description_template: str

class ProductReview(BaseModel):
    id: str
    product_id: str
    customer_id: str
    rating: int  # 1-5
    comment: Optional[str] = None
    images: List[str] = []
    is_verified_purchase: bool = True
    helpful_count: int = 0
    created_at: datetime

# Pre-defined templates for South African market
PRODUCT_TEMPLATES = {
    ProductCategory.FOOD: ProductTemplate(
        category=ProductCategory.FOOD,
        required_fields=["name", "description", "price", "preparation_time"],
        recommended_fields=["images", "allergens", "nutritional_info", "variants"],
        image_guidelines="High-quality photos of the actual dish. Include multiple angles.",
        price_guidelines="Price in ZAR. Include VAT in displayed price.",
        description_template="{name} - {description}. Prep time: {prep_time} mins."
    ),
    ProductCategory.GROCERY: ProductTemplate(
        category=ProductCategory.GROCERY,
        required_fields=["name", "description", "price", "unit", "stock"],
        recommended_fields=["images", "brand", "expiry_date", "variants"],
        image_guidelines="Clear product packaging photo. Show quantity/weight.",
        price_guidelines="Price per unit. Bulk discounts encouraged.",
        description_template="{name} ({quantity}{unit}) - {brand}"
    ),
    ProductCategory.PHARMACY: ProductTemplate(
        category=ProductCategory.PHARMACY,
        required_fields=["name", "description", "price", "dosage", "requires_prescription"],
        recommended_fields=["images", "manufacturer", "expiry_date", "side_effects"],
        image_guidelines="Product packaging. Include dosage information visible.",
        price_guidelines="Price per unit. Clearly mark prescription requirements.",
        description_template="{name} {dosage} - {manufacturer}"
    )
}
