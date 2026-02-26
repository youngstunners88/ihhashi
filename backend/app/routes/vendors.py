from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional, List
from datetime import datetime, timedelta
from app.services.auth import get_current_user
from app.models.verification import (
    VendorVerification, VerificationStatus, DocumentType, VerificationDocument
)
from app.models.account import AccountStatus, AccountRecord
from app.config import settings
from pydantic import BaseModel

router = APIRouter()


class VendorApplication(BaseModel):
    """Initial vendor application"""
    business_name: str
    business_address: str
    business_city: str
    business_province: str
    business_lat: Optional[float] = None
    business_lng: Optional[float] = None
    phone: str
    email: str
    description: str
    category: str


class DocumentUpload(BaseModel):
    """Document upload result"""
    document_type: DocumentType
    file_url: str


@router.post("/apply")
async def apply_as_vendor(
    application: VendorApplication,
    current_user = Depends(get_current_user)
):
    """Apply to become a vendor - starts 45-day free trial"""
    # Create account record with free trial
    trial_ends = datetime.utcnow() + timedelta(days=settings.free_trial_days)
    
    account = AccountRecord(
        user_id=current_user.id,
        status=AccountStatus.FREE_TRIAL,
        trial_started_at=datetime.utcnow(),
        trial_ends_at=trial_ends
    )
    
    # Create vendor verification record
    verification = VendorVerification(
        vendor_id=current_user.id,
        business_name=application.business_name,
        business_address=application.business_address,
        business_city=application.business_city,
        business_province=application.business_province,
        business_coordinates={
            "lat": application.business_lat,
            "lng": application.business_lng
        } if application.business_lat else None,
        status=VerificationStatus.UNVERIFIED
    )
    
    return {
        "message": "Vendor application submitted",
        "trial_ends": trial_ends.isoformat(),
        "trial_days_remaining": settings.free_trial_days,
        "verification_status": "unverified",
        "next_steps": [
            "Upload ID document",
            "Upload company registration (if applicable)",
            "Upload proof of business address",
            "Complete Blue Horse verification for higher ranking"
        ]
    }


@router.post("/documents")
async def upload_verification_document(
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Upload a verification document for Blue Horse status"""
    # TODO: Implement file upload to S3/Supabase storage
    # For now, return a placeholder URL
    
    file_url = f"https://storage.ihhashi.co.za/documents/{current_user.id}/{file.filename}"
    
    document = VerificationDocument(
        document_type=document_type,
        file_url=file_url
    )
    
    return {
        "message": "Document uploaded successfully",
        "document_type": document_type.value,
        "file_url": file_url,
        "status": "pending_review"
    }


@router.get("/verification-status")
async def get_verification_status(current_user = Depends(get_current_user)):
    """Get current verification status and Blue Horse progress"""
    # TODO: Fetch from database
    
    return {
        "vendor_id": current_user.id,
        "status": VerificationStatus.UNVERIFIED.value,
        "blue_horse": {
            "is_verified": False,
            "verification_level": 0,
            "has_blue_horse": False
        },
        "documents": {
            "id_document": False,
            "company_registration": False,
            "business_license": False,
            "proof_of_address": False
        },
        "verification_percentage": 0,
        "ranking_boost": 0,
        "next_steps": [
            "Upload South African ID document",
            "Upload company registration (CIPC)",
            "Upload proof of business address"
        ]
    }


@router.get("/account-status")
async def get_account_status(current_user = Depends(get_current_user)):
    """Get account status including trial and warnings"""
    # TODO: Fetch from database
    
    return {
        "user_id": current_user.id,
        "status": AccountStatus.FREE_TRIAL.value,
        "trial_active": True,
        "trial_days_remaining": 45,
        "warnings_count": 0,
        "is_suspended": False,
        "is_terminated": False
    }


@router.post("/submit-verification")
async def submit_for_verification(current_user = Depends(get_current_user)):
    """Submit all documents for Blue Horse verification review"""
    # TODO: Check all required documents are uploaded
    # TODO: Update verification status to PENDING
    
    return {
        "message": "Verification submitted for review",
        "estimated_review_time": "2-3 business days",
        "status": VerificationStatus.PENDING.value
    }


@router.get("/{vendor_id}")
async def get_vendor_profile(vendor_id: str):
    """Get public vendor profile with Blue Horse status"""
    # TODO: Fetch from database
    
    return {
        "vendor_id": vendor_id,
        "business_name": "Sample Business",
        "description": "Sample vendor description",
        "rating": 4.5,
        "total_reviews": 25,
        "blue_horse_verified": False,
        "verification_level": 0,
        "products": [],
        "reviews": []
    }


@router.get("/{vendor_id}/products")
async def get_vendor_products(vendor_id: str):
    """Get vendor's product listing"""
    # TODO: Implement product listing
    
    return {
        "vendor_id": vendor_id,
        "products": [],
        "total": 0
    }


@router.get("/{vendor_id}/reviews")
async def get_vendor_reviews(vendor_id: str):
    """Get vendor reviews and ratings"""
    # TODO: Implement review listing
    
    return {
        "vendor_id": vendor_id,
        "average_rating": 0,
        "total_reviews": 0,
        "reviews": []
    }
