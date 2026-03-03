"""Payment schemas."""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    """Payment status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    """Payment method enum."""
    CARD = "card"
    MOBILE_MONEY = "mobile_money"
    CASH = "cash"
    WALLET = "wallet"


class PaymentBase(BaseModel):
    """Base payment schema."""
    order_id: str
    user_id: str
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    payment_method: PaymentMethod


class PaymentCreate(PaymentBase):
    """Payment creation schema."""
    payment_token: Optional[str] = None  # Stripe token, etc.
    save_payment_method: bool = False


class Payment(PaymentBase):
    """Payment response schema."""
    id: str = Field(..., alias="_id")
    status: PaymentStatus
    transaction_id: Optional[str] = None
    payment_processor: Optional[str] = None
    processor_fee: Decimal = Decimal("0.0")
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None

    class Config:
        populate_by_name = True


class PaymentIntent(BaseModel):
    """Payment intent schema."""
    client_secret: str
    amount: Decimal
    currency: str
    order_id: str


class RefundRequest(BaseModel):
    """Refund request schema."""
    payment_id: str
    amount: Optional[Decimal] = None  # Partial refund if specified
    reason: str
