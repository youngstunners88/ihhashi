"""Order schemas."""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    """Order status enum."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    """Order item schema."""
    item_id: str
    name: str
    quantity: int = Field(..., ge=1)
    unit_price: Decimal = Field(..., ge=0)
    total_price: Decimal = Field(..., ge=0)
    special_instructions: Optional[str] = None


class OrderBase(BaseModel):
    """Base order schema."""
    user_id: str
    restaurant_id: str
    items: List[OrderItem]
    delivery_address: dict
    delivery_notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Order creation schema."""
    payment_method: str


class OrderUpdate(BaseModel):
    """Order update schema."""
    status: Optional[OrderStatus] = None
    rider_id: Optional[str] = None
    delivery_notes: Optional[str] = None


class OrderInDB(OrderBase):
    """Order in database schema."""
    id: str = Field(..., alias="_id")
    status: OrderStatus
    rider_id: Optional[str] = None
    total_amount: Decimal
    delivery_fee: Decimal
    service_fee: Decimal
    payment_status: str
    created_at: datetime
    updated_at: datetime
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    tracking_history: List[dict] = []

    class Config:
        populate_by_name = True


class Order(OrderBase):
    """Order response schema."""
    id: str = Field(..., alias="_id")
    status: OrderStatus
    rider_id: Optional[str] = None
    total_amount: Decimal
    delivery_fee: Decimal
    service_fee: Decimal
    payment_status: str
    created_at: datetime
    updated_at: datetime
    estimated_delivery_time: Optional[datetime] = None

    class Config:
        populate_by_name = True


class OrderTrackingUpdate(BaseModel):
    """Order tracking update schema."""
    order_id: str
    status: OrderStatus
    location: Optional[dict] = None
    note: Optional[str] = None
