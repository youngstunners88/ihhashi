from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class VerificationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class VerificationLevel(str, Enum):
    BASIC = "basic"          # Email/phone verified
    STANDARD = "standard"    # ID document uploaded
    VERIFIED = "verified"    # Full KYC (ID + business docs for merchants)
    BLUE_HORSE = "blue_horse"  # Premium verified - blue tick equivalent

class DocumentType(str, Enum):
    SA_ID = "sa_id"              # South African ID
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    BUSINESS_REG = "business_registration"
    TAX_CLEARANCE = "tax_clearance"
    VEHICLE_REG = "vehicle_registration"
    PROOF_OF_ADDRESS = "proof_of_address"

class VerificationDocument(BaseModel):
    id: str
    document_type: DocumentType
    file_url: str
    status: VerificationStatus = VerificationStatus.PENDING
    uploaded_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None  # Admin user ID
    rejection_reason: Optional[str] = None

class VehicleInfo(BaseModel):
    vehicle_type: str  # motorcycle, bicycle, car, scooter, on_foot
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    license_plate: Optional[str] = None
    registration_doc_url: Optional[str] = None

class VerificationBase(BaseModel):
    user_id: str
    level: VerificationLevel = VerificationLevel.BASIC

class VerificationCreate(BaseModel):
    documents: List[VerificationDocument]
    vehicle_info: Optional[VehicleInfo] = None

class Verification(VerificationBase):
    id: str
    status: VerificationStatus = VerificationStatus.PENDING
    documents: List[VerificationDocument] = []
    vehicle_info: Optional[VehicleInfo] = None
    blue_horse_badge: bool = False
    warnings: int = 0
    suspension_count: int = 0
    permanently_banned: bool = False
    created_at: datetime
    updated_at: datetime

class WarningReason(str, Enum):
    LATE_DELIVERY = "late_delivery"
    ORDER_CANCELLATION = "order_cancellation"
    CUSTOMER_COMPLAINT = "customer_complaint"
    INAPPROPRIATE_BEHAVIOR = "inappropriate_behavior"
    POLICY_VIOLATION = "policy_violation"
    FRAUD_SUSPICION = "fraud_suspicion"
    QUALITY_ISSUE = "quality_issue"

class Warning(BaseModel):
    id: str
    user_id: str
    reason: WarningReason
    description: str
    related_order_id: Optional[str] = None
    created_at: datetime
    acknowledged: bool = False

class Suspension(BaseModel):
    id: str
    user_id: str
    reason: str
    start_date: datetime
    end_date: Optional[datetime] = None  # None = permanent
    created_by: str  # Admin user ID
    is_permanent: bool = False
