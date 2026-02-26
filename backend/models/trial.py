from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class TrialStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CONVERTED = "converted"  # User became paying user
    CANCELLED = "cancelled"

class UserTrialBase(BaseModel):
    user_id: str
    role: str  # "customer", "merchant", "rider"

class UserTrial(UserTrialBase):
    id: str
    status: TrialStatus = TrialStatus.ACTIVE
    started_at: datetime
    expires_at: datetime
    days_remaining: int
    platform_fees_waived: bool = True
    converted_at: Optional[datetime] = None

class PlatformFee(BaseModel):
    """Track platform fees - 0% during trial, 15% after"""
    order_id: str
    user_id: str
    is_trial_user: bool
    fee_percent: float
    fee_amount: float
    order_total: float
    created_at: datetime

class TrialExtension(BaseModel):
    """Extensions granted for promotions"""
    id: str
    user_id: str
    additional_days: int
    reason: str
    granted_by: str  # Admin or system
    created_at: datetime
