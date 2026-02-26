from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem(BaseModel):
    menu_item_id: str
    name: str
    quantity: int
    price: float
    notes: Optional[str] = None

class DeliveryAddress(BaseModel):
    latitude: float
    longitude: float
    address: str
    city: str
    province: str
    contact_phone: str
    notes: Optional[str] = None

class OrderBase(BaseModel):
    merchant_id: str
    items: List[OrderItem]
    delivery_address: DeliveryAddress

class OrderCreate(OrderBase):
    notes: Optional[str] = None

class Order(OrderBase):
    id: str
    customer_id: str
    rider_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    subtotal: float
    delivery_fee: float
    total: float
    notes: Optional[str] = None
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: Optional[str] = None
