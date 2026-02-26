from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class TipStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class TipBase(BaseModel):
    amount: float  # In ZAR
    message: Optional[str] = None

class TipCreate(TipBase):
    rider_id: str
    order_id: str

class Tip(TipBase):
    id: str
    customer_id: str
    rider_id: str
    order_id: str
    status: TipStatus = TipStatus.PENDING
    platform_fee: float = 0.0  # iHhashi takes NO fee from tips
    rider_receives: float  # Full amount
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None

class TipStats(BaseModel):
    total_tips_received: float
    total_tips_given: float
    average_tip: float
    tip_count: int
