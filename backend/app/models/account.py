from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class WarningType(str, Enum):
    """Types of warnings for policy violations"""
    ORDER_FRAUD = "order_fraud"
    LATE_DELIVERY = "late_delivery"
    ORDER_CANCELLATION = "order_cancellation"
    CUSTOMER_COMPLAINT = "customer_complaint"
    INAPPROPRIATE_BEHAVIOUR = "inappropriate_behaviour"
    FAKE_LISTING = "fake_listing"
    PRICE_MANIPULATION = "price_manipulation"
    DELIVERY_DAMAGE = "delivery_damage"
    NO_SHOW = "no_show"
    HARASSMENT = "harassment"


class SuspensionReason(str, Enum):
    """Reasons for account suspension"""
    EXCESSIVE_WARNINGS = "excessive_warnings"
    SUSPECTED_FRAUD = "suspected_fraud"
    PAYMENT_ISSUES = "payment_issues"
    POLICY_VIOLATION = "policy_violation"
    INVESTIGATION = "investigation"


class TerminationReason(str, Enum):
    """Reasons for permanent account termination"""
    CRIMINAL_ACTIVITY = "criminal_activity"
    FRAUD = "fraud"
    THEFT = "theft"
    VIOLENCE = "violence"
    REPEATED_VIOLATIONS = "repeated_violations"
    ILLEGAL_SUBSTANCES = "illegal_substances"
    MONEY_LAUNDERING = "money_laundering"
    IDENTITY_FRAUD = "identity_fraud"


class UserWarning(BaseModel):
    """A warning issued to a user"""
    id: str = Field(default_factory=lambda: str(__import__("uuid").uuid4()))
    warning_type: WarningType
    description: str
    order_id: Optional[str] = None
    reported_by: Optional[str] = None  # User ID who reported
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None


class AccountStatus(str, Enum):
    ACTIVE = "active"
    FREE_TRIAL = "free_trial"  # 45-day free trial
    WARNING = "warning"  # Has active warnings
    SUSPENDED = "suspended"  # Temporarily suspended
    TERMINATED = "terminated"  # Permanent ban


class AccountRecord(BaseModel):
    """User account status and history"""
    user_id: str
    status: AccountStatus = AccountStatus.FREE_TRIAL
    
    # Free trial tracking
    trial_started_at: datetime = Field(default_factory=datetime.utcnow)
    trial_ends_at: Optional[datetime] = None  # 45 days from trial_started_at
    
    # Warning system
    warnings: List[UserWarning] = []
    warning_count: int = 0
    max_warnings: int = 3  # Auto-suspend after 3 warnings
    
    # Suspension tracking
    suspended_at: Optional[datetime] = None
    suspension_reason: Optional[SuspensionReason] = None
    suspension_ends_at: Optional[datetime] = None
    
    # Termination
    terminated_at: Optional[datetime] = None
    termination_reason: Optional[TerminationReason] = None
    
    # Stats
    total_orders: int = 0
    completed_orders: int = 0
    cancelled_orders: int = 0
    total_spent: float = 0.0
    
    @property
    def is_trial_active(self) -> bool:
        if self.status != AccountStatus.FREE_TRIAL:
            return False
        if self.trial_ends_at is None:
            return True
        return datetime.utcnow() < self.trial_ends_at
    
    @property
    def trial_days_remaining(self) -> int:
        if not self.is_trial_active:
            return 0
        if self.trial_ends_at is None:
            return 45
        delta = self.trial_ends_at - datetime.utcnow()
        return max(0, delta.days)
    
    def issue_warning(self, warning: UserWarning) -> bool:
        """Issue a warning and check if suspension needed"""
        self.warnings.append(warning)
        self.warning_count = len([w for w in self.warnings if not w.acknowledged])
        
        if self.warning_count >= self.max_warnings:
            self.status = AccountStatus.SUSPENDED
            self.suspended_at = datetime.utcnow()
            self.suspension_reason = SuspensionReason.EXCESSIVE_WARNINGS
            return True  # Suspended
        return False
    
    def terminate(self, reason: TerminationReason):
        """Permanently terminate account"""
        self.status = AccountStatus.TERMINATED
        self.terminated_at = datetime.utcnow()
        self.termination_reason = reason
