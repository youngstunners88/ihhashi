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
from app.database import get_collection
from pydantic import BaseModel
import logging
import secrets

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
    codes_col = get_collection("referral_codes")
    
    # Check if user already has a code for this type
    existing = await codes_col.find_one({
        "user_id": current_user.id,
        "referral_type": referral_type.value
    })
    
    if existing:
        # Return existing code
        base_url = settings.cors_origins.split(",")[0] if settings.cors_origins else "https://ihhashi.app"
        if referral_type == ReferralType.VENDOR:
            share_link = f"{base_url}/vendor/signup?ref={existing['code']}"
            message = "Share this link with vendors. You get 2 FREE DAYS for each vendor who signs up!"
        else:
            share_link = f"{base_url}/signup?ref={existing['code']}"
            message = "Share this link with friends. You BOTH earn iHhashi Coins!"
        
        return ReferralCodeResponse(
            code=existing["code"],
            referral_type=referral_type.value,
            share_link=share_link,
            message=message
        )
    
    prefix = "IH-V" if referral_type == ReferralType.VENDOR else "IH-C"
    code = ReferralCode.generate_code(prefix)
    
    # Create referral code record
    referral_code = ReferralCode(
        user_id=current_user.id,
        code=code,
        referral_type=referral_type
    )
    
    # Store in database
    await codes_col.insert_one(referral_code.model_dump())
    
    # Generate share link
    base_url = settings.cors_origins.split(",")[0] if settings.cors_origins else "https://ihhashi.app"
    if referral_type == ReferralType.VENDOR:
        share_link = f"{base_url}/vendor/signup?ref={code}"
        message = "Share this link with vendors. You get 2 FREE DAYS for each vendor who signs up!"
    else:
        share_link = f"{base_url}/signup?ref={code}"
        message = "Share this link with friends. You BOTH earn iHhashi Coins!"
    
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
    codes_col = get_collection("referral_codes")
    referrals_col = get_collection("referrals")
    users_col = get_collection("users")
    
    # Validate code format
    code = request.referral_code.upper()
    if not code.startswith("IH-"):
        raise HTTPException(status_code=400, detail="Invalid referral code format")
    
    # Validate code exists in database
    code_record = await codes_col.find_one({"code": code})
    if not code_record:
        raise HTTPException(status_code=400, detail="Invalid referral code")
    
    # Check code is active
    if code_record.get("status") == "expired":
        raise HTTPException(status_code=400, detail="Referral code has expired")
    
    # Check user hasn't already used a referral code
    existing_use = await referrals_col.find_one({"referee_id": current_user.id})
    if existing_use:
        raise HTTPException(status_code=400, detail="You have already used a referral code")
    
    # Can't use own referral code
    if code_record["user_id"] == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot use your own referral code")
    
    # Determine expected prefix
    expected_prefix = "IH-V" if request.referral_type == ReferralType.VENDOR else "IH-C"
    if not code.startswith(expected_prefix):
        raise HTTPException(
            status_code=400, 
            detail=f"This code is for {'vendors' if request.referral_type == ReferralType.CUSTOMER else 'customers'}"
        )
    
    # Create referral record
    referral = Referral(
        referrer_id=code_record["user_id"],
        referee_id=current_user.id,
        referral_code=code,
        referral_type=request.referral_type,
        status=ReferralStatus.COMPLETED,
        completed_at=datetime.utcnow()
    )
    
    await referrals_col.insert_one(referral.model_dump())
    
    # Award rewards
    rewards = ReferralReward(referral_type=request.referral_type)
    
    if request.referral_type == ReferralType.VENDOR:
        # Award bonus days to referrer
        await users_col.update_one(
            {"id": code_record["user_id"]},
            {"$inc": {"bonus_days": rewards.vendor_bonus_days_per_referral}}
        )
        
        return {
            "message": "Referral code applied successfully!",
            "referrer_reward": f"{rewards.vendor_bonus_days_per_referral} days added to free trial",
            "your_welcome_bonus": "Welcome to iHhashi! Your referrer helped you get started.",
            "referral_code": code
        }
    else:
        # Award iHhashi Coins to both parties
        await users_col.update_one(
            {"id": code_record["user_id"]},
            {"$inc": {"hashi_coins": rewards.customer_referrer_coins}}
        )
        await users_col.update_one(
            {"id": current_user.id},
            {"$inc": {"hashi_coins": rewards.customer_referee_coins}}
        )
        
        return {
            "message": "Referral code applied successfully!",
            "referrer_reward": f"{rewards.customer_referrer_coins} iHhashi Coins",
            "your_welcome_bonus": f"{rewards.customer_referee_coins} iHhashi Coins added to your account!",
            "referral_code": code,
            "hashi_coins": rewards.customer_referee_coins
        }


@router.get("/stats", response_model=ReferralStatsResponse)
async def get_referral_stats(
    referral_type: ReferralType = Query(ReferralType.VENDOR),
    current_user = Depends(get_current_user)
):
    """Get referral statistics for the current user"""
    codes_col = get_collection("referral_codes")
    referrals_col = get_collection("referrals")
    
    # Get user's code
    code_record = await codes_col.find_one({
        "user_id": current_user.id,
        "referral_type": referral_type.value
    })
    
    if not code_record:
        # Generate one if doesn't exist
        prefix = "IH-V" if referral_type == ReferralType.VENDOR else "IH-C"
        code = ReferralCode.generate_code(prefix)
        code_record = {
            "user_id": current_user.id,
            "code": code,
            "referral_type": referral_type.value
        }
        await codes_col.insert_one(code_record)
    
    # Get referral stats
    total_referrals = await referrals_col.count_documents({
        "referral_code": code_record["code"]
    })
    
    completed_referrals = await referrals_col.count_documents({
        "referral_code": code_record["code"],
        "status": ReferralStatus.COMPLETED.value
    })
    
    pending_referrals = await referrals_col.count_documents({
        "referral_code": code_record["code"],
        "status": ReferralStatus.PENDING.value
    })
    
    if referral_type == ReferralType.VENDOR:
        bonus_days = completed_referrals * 2  # 2 days per referral
        return ReferralStatsResponse(
            referral_code=code_record["code"],
            total_referrals=total_referrals,
            completed_referrals=completed_referrals,
            pending_referrals=pending_referrals,
            rewards_earned={
                "bonus_days": bonus_days,
                "max_bonus_days": 90
            }
        )
    else:
        # Calculate hashi coins earned
        completed_refs = await referrals_col.find({
            "referrer_id": current_user.id,
            "referral_type": ReferralType.CUSTOMER.value,
            "status": ReferralStatus.COMPLETED.value
        }).to_list(length=100)
        
        hashi_coins = len(completed_refs) * 100  # 100 coins per referral
        
        return ReferralStatsResponse(
            referral_code=code_record["code"],
            total_referrals=total_referrals,
            completed_referrals=completed_referrals,
            pending_referrals=pending_referrals,
            rewards_earned={
                "hashi_coins": hashi_coins,
                "free_deliveries": hashi_coins // 200,
                "discount_credits": (hashi_coins // 150) * 15
            }
        )


@router.get("/customer/rewards", response_model=CustomerRewardsResponse)
async def get_customer_rewards(current_user = Depends(get_current_user)):
    """Get detailed customer rewards, tier status, and benefits"""
    codes_col = get_collection("referral_codes")
    referrals_col = get_collection("referrals")
    users_col = get_collection("users")
    
    # Get user data
    user = await users_col.find_one({"id": current_user.id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's referral code
    code_record = await codes_col.find_one({
        "user_id": current_user.id,
        "referral_type": ReferralType.CUSTOMER.value
    })
    
    referral_code = code_record["code"] if code_record else "Not generated"
    
    # Get referral count
    total_referrals = await referrals_col.count_documents({
        "referrer_id": current_user.id,
        "referral_type": ReferralType.CUSTOMER.value,
        "status": ReferralStatus.COMPLETED.value
    })
    
    # Determine tier
    tier = "bronze"
    if total_referrals >= 20:
        tier = "platinum"
    elif total_referrals >= 10:
        tier = "gold"
    elif total_referrals >= 5:
        tier = "silver"
    
    # Calculate tier progress
    tier_thresholds = {"bronze": 0, "silver": 5, "gold": 10, "platinum": 20}
    tier_order = ["bronze", "silver", "gold", "platinum"]
    current_tier_index = tier_order.index(tier)
    next_tier = tier_order[min(current_tier_index + 1, 3)]
    referrals_to_next = max(0, tier_thresholds[next_tier] - total_referrals)
    
    return CustomerRewardsResponse(
        referral_code=referral_code,
        tier=tier,
        hashi_coins_balance=user.get("hashi_coins", 0),
        total_referrals=total_referrals,
        free_delivery_credits=user.get("free_delivery_credits", 0),
        discount_credits=user.get("discount_credits", 0.0),
        tier_progress={
            "current_tier": tier.capitalize(),
            "referrals_to_next_tier": referrals_to_next,
            "next_tier": next_tier.capitalize()
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
    """Redeem iHhashi Coins for a free delivery"""
    rewards = ReferralReward(referral_type=ReferralType.CUSTOMER)
    users_col = get_collection("users")
    
    user = await users_col.find_one({"id": current_user.id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_balance = user.get("hashi_coins", 0)
    can_redeem = current_balance >= rewards.coins_for_free_delivery
    
    if can_redeem:
        # Deduct coins and add free delivery credit
        await users_col.update_one(
            {"id": current_user.id},
            {
                "$inc": {
                    "hashi_coins": -rewards.coins_for_free_delivery,
                    "free_delivery_credits": 1
                }
            }
        )
        current_balance -= rewards.coins_for_free_delivery
    
    return {
        "message": f"Redeem {rewards.coins_for_free_delivery} iHhashi Coins for free delivery",
        "coins_required": rewards.coins_for_free_delivery,
        "current_balance": current_balance,
        "can_redeem": can_redeem,
        "redeemed": can_redeem
    }


@router.post("/redeem/discount/{amount}")
async def redeem_discount(
    amount: int,  # 10 or 25
    current_user = Depends(get_current_user)
):
    """Redeem iHhashi Coins for a discount coupon"""
    rewards = ReferralReward(referral_type=ReferralType.CUSTOMER)
    users_col = get_collection("users")
    
    if amount not in [10, 25]:
        raise HTTPException(status_code=400, detail="Discount amount must be 10 or 25")
    
    coins_required = rewards.coins_for_discount_10 if amount == 10 else rewards.coins_for_discount_25
    discount_value = amount * 1.5  # R15 or R37.50
    
    user = await users_col.find_one({"id": current_user.id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_balance = user.get("hashi_coins", 0)
    can_redeem = current_balance >= coins_required
    
    if can_redeem:
        # Deduct coins and add discount credit
        await users_col.update_one(
            {"id": current_user.id},
            {
                "$inc": {
                    "hashi_coins": -coins_required,
                    "discount_credits": discount_value
                }
            }
        )
        current_balance -= coins_required
    
    return {
        "message": f"Redeem {coins_required} iHhashi Coins for R{discount_value:.2f} discount",
        "coins_required": coins_required,
        "discount_amount": discount_value,
        "current_balance": current_balance,
        "can_redeem": can_redeem,
        "redeemed": can_redeem
    }


# === ADMIN ENDPOINTS ===

@router.post("/admin/process-pending")
async def process_pending_referrals():
    """Process pending referrals and award bonuses (called by cron job)"""
    referrals_col = get_collection("referrals")
    users_col = get_collection("users")
    
    # Fetch all pending referrals older than 24 hours
    cutoff = datetime.utcnow() - timedelta(hours=24)
    pending = await referrals_col.find({
        "status": ReferralStatus.PENDING.value,
        "created_at": {"$lt": cutoff}
    }).to_list(length=1000)
    
    processed_count = 0
    awards_given = 0
    
    for ref in pending:
        # Mark as completed
        await referrals_col.update_one(
            {"id": ref["id"]},
            {"$set": {"status": ReferralStatus.COMPLETED.value, "completed_at": datetime.utcnow()}}
        )
        
        # Award bonuses
        if ref["referral_type"] == ReferralType.VENDOR.value:
            await users_col.update_one(
                {"id": ref["referrer_id"]},
                {"$inc": {"bonus_days": 2}}
            )
        else:
            await users_col.update_one(
                {"id": ref["referrer_id"]},
                {"$inc": {"hashi_coins": 100}}
            )
            await users_col.update_one(
                {"id": ref["referee_id"]},
                {"$inc": {"hashi_coins": 50}}
            )
        
        processed_count += 1
        awards_given += 1
    
    return {
        "message": "Pending referrals processed",
        "processed_count": processed_count,
        "awards_given": awards_given
    }


@router.get("/admin/stats")
async def get_admin_referral_stats():
    """Get overall referral program statistics"""
    codes_col = get_collection("referral_codes")
    referrals_col = get_collection("referrals")
    
    total_codes = await codes_col.count_documents({})
    total_referrals = await referrals_col.count_documents({})
    vendor_referrals = await referrals_col.count_documents({"referral_type": ReferralType.VENDOR.value})
    customer_referrals = await referrals_col.count_documents({"referral_type": ReferralType.CUSTOMER.value})
    
    # Calculate totals
    completed_vendor = await referrals_col.find({
        "referral_type": ReferralType.VENDOR.value,
        "status": ReferralStatus.COMPLETED.value
    }).to_list(length=10000)
    
    completed_customer = await referrals_col.find({
        "referral_type": ReferralType.CUSTOMER.value,
        "status": ReferralStatus.COMPLETED.value
    }).to_list(length=10000)
    
    total_bonus_days = len(completed_vendor) * 2
    total_hashi_coins = len(completed_customer) * 150  # 100 + 50
    
    # Tier distribution (approximate)
    all_customer_refs = await referrals_col.aggregate([
        {"$match": {"referral_type": ReferralType.CUSTOMER.value}},
        {"$group": {"_id": "$referrer_id", "count": {"$sum": 1}}}
    ]).to_list(length=10000)
    
    tier_distribution = {"bronze": 0, "silver": 0, "gold": 0, "platinum": 0}
    for ref in all_customer_refs:
        count = ref["count"]
        if count >= 20:
            tier_distribution["platinum"] += 1
        elif count >= 10:
            tier_distribution["gold"] += 1
        elif count >= 5:
            tier_distribution["silver"] += 1
        else:
            tier_distribution["bronze"] += 1
    
    return {
        "total_referral_codes": total_codes,
        "total_referrals": total_referrals,
        "vendor_referrals": vendor_referrals,
        "customer_referrals": customer_referrals,
        "total_bonus_days_awarded": total_bonus_days,
        "total_hashi_coins_awarded": total_hashi_coins,
        "tier_distribution": tier_distribution
    }
