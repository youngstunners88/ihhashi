from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from app.services.auth import get_current_user
from app.models.referral import (
    ReferralCode, Referral, ReferralStatus, ReferralType,
    VendorReferralStats, CustomerReferralStats, ReferralReward
)
from app.models.account import AccountRecord, AccountStatus
from app.config import settings
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class ReferralCodeResponse(BaseModel):
    """Response for referral code generation"""
    code: str
    referral_type: str
    share_link: str
    message: str


class ApplyReferralRequest(BaseModel):
    """Request to apply a referral code during signup"""
    referral_code: str
    referral_type: ReferralType


class ReferralStatsResponse(BaseModel):
    """Referral statistics response"""
    referral_code: str
    total_referrals: int
    completed_referrals: int
    pending_referrals: int
    rewards_earned: dict


class CustomerRewardsResponse(BaseModel):
    """Customer rewards and tier status"""
    referral_code: str
    tier: str
    hashi_coins_balance: int
    total_referrals: int
    free_delivery_credits: int
    discount_credits: float
    tier_progress: dict
    tier_benefits: dict


@router.post("/generate/{referral_type}", response_model=ReferralCodeResponse)
async def generate_referral_code(
    referral_type: ReferralType,
    current_user = Depends(get_current_user)
):
    """Generate a unique referral code for the current user"""
    # TODO: Check if user already has a code for this type
    # TODO: Store in database
    
    prefix = "IH-V" if referral_type == ReferralType.VENDOR else "IH-C"
    code = ReferralCode.generate_code(prefix)
    
    # Create referral code record
    referral_code = ReferralCode(
        user_id=current_user.id,
        code=code,
        referral_type=referral_type
    )
    
    # Generate share link
    base_url = "https://ihhashi.app"  # TODO: Use config
    if referral_type == ReferralType.VENDOR:
        share_link = f"{base_url}/vendor/signup?ref={code}"
        message = "Share this link with vendors. You get 2 FREE DAYS for each vendor who signs up!"
    else:
        share_link = f"{base_url}/signup?ref={code}"
        message = "Share this link with friends. You BOTH earn Hashi Coins!"
    
    return ReferralCodeResponse(
        code=code,
        referral_type=referral_type.value,
        share_link=share_link,
        message=message
    )


@router.post("/apply", status_code=200)
async def apply_referral_code(
    request: ApplyReferralRequest,
    current_user = Depends(get_current_user)
):
    """Apply a referral code during signup - awards bonuses to both parties"""
    # TODO: Validate code exists in database
    # TODO: Check code is active and not expired
    # TODO: Check user hasn't already used a referral code
    
    # Validate code format
    code = request.referral_code.upper()
    if not code.startswith("IH-"):
        raise HTTPException(status_code=400, detail="Invalid referral code format")
    
    # Determine expected prefix
    expected_prefix = "IH-V" if request.referral_type == ReferralType.VENDOR else "IH-C"
    if not code.startswith(expected_prefix):
        raise HTTPException(
            status_code=400, 
            detail=f"This code is for {'vendors' if request.referral_type == ReferralType.CUSTOMER else 'customers'}"
        )
    
    # TODO: Create referral record in database
    referral = Referral(
        referrer_id="PLACEHOLDER",  # Will be fetched from DB
        referee_id=current_user.id,
        referral_code=code,
        referral_type=request.referral_type,
        status=ReferralStatus.COMPLETED
    )
    
    rewards = ReferralReward(referral_type=request.referral_type)
    
    if request.referral_type == ReferralType.VENDOR:
        # Vendor referral: +2 days per referral
        return {
            "message": "Referral code applied successfully!",
            "referrer_reward": f"{rewards.vendor_bonus_days_per_referral} days added to free trial",
            "your_welcome_bonus": "Welcome to iHhashi! Your referrer helped you get started.",
            "referral_code": code
        }
    else:
        # Customer referral: Hashi Coins for both
        return {
            "message": "Referral code applied successfully!",
            "referrer_reward": f"{rewards.customer_referrer_coins} Hashi Coins",
            "your_welcome_bonus": f"{rewards.customer_referee_coins} Hashi Coins added to your account!",
            "referral_code": code,
            "hashi_coins": rewards.customer_referee_coins
        }


@router.get("/stats", response_model=ReferralStatsResponse)
async def get_referral_stats(
    referral_type: ReferralType = Query(ReferralType.VENDOR),
    current_user = Depends(get_current_user)
):
    """Get referral statistics for the current user"""
    # TODO: Fetch from database
    
    if referral_type == ReferralType.VENDOR:
        return ReferralStatsResponse(
            referral_code="IH-V-PLACEHOLDER",
            total_referrals=0,
            completed_referrals=0,
            pending_referrals=0,
            rewards_earned={
                "bonus_days": 0,
                "max_bonus_days": 90
            }
        )
    else:
        return ReferralStatsResponse(
            referral_code="IH-C-PLACEHOLDER",
            total_referrals=0,
            completed_referrals=0,
            pending_referrals=0,
            rewards_earned={
                "hashi_coins": 0,
                "free_deliveries": 0,
                "discount_credits": 0.0
            }
        )


@router.get("/customer/rewards", response_model=CustomerRewardsResponse)
async def get_customer_rewards(current_user = Depends(get_current_user)):
    """Get detailed customer rewards, tier status, and benefits"""
    # TODO: Fetch from database
    
    return CustomerRewardsResponse(
        referral_code="IH-C-PLACEHOLDER",
        tier="bronze",
        hashi_coins_balance=0,
        total_referrals=0,
        free_delivery_credits=0,
        discount_credits=0.0,
        tier_progress={
            "current_tier": "Bronze",
            "referrals_to_next_tier": 5,
            "next_tier": "Silver"
        },
        tier_benefits={
            "bronze": ["5% off first order", "Priority support"],
            "silver": ["10% off orders", "Free delivery once/month", "Priority support"],
            "gold": ["15% off orders", "Free delivery twice/month", "VIP support", "Early access to promos"],
            "platinum": ["20% off orders", "Unlimited free delivery", "Dedicated account manager", "Exclusive events"]
        }
    )


@router.post("/redeem/free-delivery")
async def redeem_free_delivery(current_user = Depends(get_current_user)):
    """Redeem Hashi Coins for a free delivery"""
    rewards = ReferralReward(referral_type=ReferralType.CUSTOMER)
    
    # TODO: Check user's coin balance
    # TODO: Deduct coins and apply free delivery credit
    
    return {
        "message": f"Redeem {rewards.coins_for_free_delivery} Hashi Coins for free delivery",
        "coins_required": rewards.coins_for_free_delivery,
        "current_balance": 0,  # TODO: Fetch from DB
        "can_redeem": False
    }


@router.post("/redeem/discount/{amount}")
async def redeem_discount(
    amount: int,  # 10 or 25
    current_user = Depends(get_current_user)
):
    """Redeem Hashi Coins for a discount coupon"""
    rewards = ReferralReward(referral_type=ReferralType.CUSTOMER)
    
    if amount not in [10, 25]:
        raise HTTPException(status_code=400, detail="Discount amount must be 10 or 25")
    
    coins_required = rewards.coins_for_discount_10 if amount == 10 else rewards.coins_for_discount_25
    discount_value = amount * 1.5  # R15 or R37.50
    
    # TODO: Check user's coin balance
    # TODO: Deduct coins and create discount coupon
    
    return {
        "message": f"Redeem {coins_required} Hashi Coins for R{discount_value:.2f} discount",
        "coins_required": coins_required,
        "discount_amount": discount_value,
        "current_balance": 0,  # TODO: Fetch from DB
        "can_redeem": False
    }


# === ADMIN ENDPOINTS ===

@router.post("/admin/process-pending")
async def process_pending_referrals():
    """Process pending referrals and award bonuses (called by cron job)"""
    # TODO: Fetch all pending referrals
    # TODO: Check if referee has completed required action
    # TODO: Award bonuses to both parties
    # TODO: Update referral status
    
    return {
        "message": "Pending referrals processed",
        "processed_count": 0,
        "awards_given": 0
    }


@router.get("/admin/stats")
async def get_admin_referral_stats():
    """Get overall referral program statistics"""
    # TODO: Aggregate stats from database
    
    return {
        "total_referral_codes": 0,
        "total_referrals": 0,
        "vendor_referrals": 0,
        "customer_referrals": 0,
        "total_bonus_days_awarded": 0,
        "total_hashi_coins_awarded": 0,
        "tier_distribution": {
            "bronze": 0,
            "silver": 0,
            "gold": 0,
            "platinum": 0
        }
    }
