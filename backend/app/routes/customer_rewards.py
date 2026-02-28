from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from app.services.auth import get_current_user
from app.models.customer_rewards import (
    CustomerRewardAccount, CustomerTier, CoinValues, RewardRedemption
)
from app.models.referral import ReferralCode, Referral, ReferralType, ReferralStatus
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class ReferralLinkResponse(BaseModel):
    """Response for customer referral link"""
    referral_code: str
    share_link: str
    message: str
    coins_for_referrer: int
    coins_for_friend: int


class RewardsDashboardResponse(BaseModel):
    """Full rewards dashboard for customer"""
    tier: str
    tier_name: str
    tier_icon: str
    tier_color: str
    hashi_coins_balance: int
    total_referrals: int
    referral_code: str
    free_delivery_credits: int
    discount_credits: float
    tier_progress: dict
    next_tier: Optional[str]
    referrals_to_next_tier: int
    tier_benefits: dict
    referral_history: list
    coin_history: list


class RedeemResponse(BaseModel):
    """Response for coin redemption"""
    success: bool
    message: str
    coins_spent: int
    new_balance: int
    reward_type: str
    reward_value: float
    expires_at: Optional[str]


@router.get("/referral-link", response_model=ReferralLinkResponse)
async def get_referral_link(current_user = Depends(get_current_user)):
    """Get your unique referral link to share with friends"""
    # TODO: Fetch or create referral code from database
    
    code = ReferralCode.generate_code("IH-C")
    
    return ReferralLinkResponse(
        referral_code=code,
        share_link=f"https://ihhashi.app/signup?ref={code}",
        message="Share this link with friends! You BOTH get Hashi Coins when they sign up!",
        coins_for_referrer=CoinValues.REFERRAL_BONUS_REFERRER,
        coins_for_friend=CoinValues.REFERRAL_BONUS_REFEREE
    )


@router.get("/dashboard", response_model=RewardsDashboardResponse)
async def get_rewards_dashboard(current_user = Depends(get_current_user)):
    """Get your full rewards dashboard with tier, coins, and benefits"""
    # TODO: Fetch from database
    
    # Mock data for now
    total_referrals = 0
    current_tier = CustomerTier.BRONZE
    tier_benefits = CustomerRewardAccount.get_tier_benefits(current_tier)
    
    # Calculate next tier
    next_tier = None
    referrals_to_next = 0
    if total_referrals < CoinValues.BRONZE_MIN:
        next_tier = "Bronze"
        referrals_to_next = CoinValues.BRONZE_MIN - total_referrals
    elif total_referrals < CoinValues.SILVER_MIN:
        next_tier = "Silver"
        referrals_to_next = CoinValues.SILVER_MIN - total_referrals
    elif total_referrals < CoinValues.GOLD_MIN:
        next_tier = "Gold"
        referrals_to_next = CoinValues.GOLD_MIN - total_referrals
    elif total_referrals < CoinValues.PLATINUM_MIN:
        next_tier = "Platinum"
        referrals_to_next = CoinValues.PLATINUM_MIN - total_referrals
    
    return RewardsDashboardResponse(
        tier=current_tier.value,
        tier_name=tier_benefits["name"],
        tier_icon=tier_benefits["icon"],
        tier_color=tier_benefits["color"],
        hashi_coins_balance=0,
        total_referrals=total_referrals,
        referral_code="IH-C-PLACEHOLDER",
        free_delivery_credits=0,
        discount_credits=0.0,
        tier_progress={
            "current_referrals": total_referrals,
            "bronze": {"min": 1, "achieved": total_referrals >= 1},
            "silver": {"min": 6, "achieved": total_referrals >= 6},
            "gold": {"min": 16, "achieved": total_referrals >= 16},
            "platinum": {"min": 51, "achieved": total_referrals >= 51}
        },
        next_tier=next_tier,
        referrals_to_next_tier=referrals_to_next,
        tier_benefits=tier_benefits,
        referral_history=[],
        coin_history=[]
    )


@router.get("/tiers")
async def get_tier_info():
    """Get information about all reward tiers and their benefits"""
    tiers = []
    for tier in CustomerTier:
        benefits = CustomerRewardAccount.get_tier_benefits(tier)
        thresholds = {
            CustomerTier.BRONZE: {"min": 1, "max": 5},
            CustomerTier.SILVER: {"min": 6, "max": 15},
            CustomerTier.GOLD: {"min": 16, "max": 50},
            CustomerTier.PLATINUM: {"min": 51, "max": "∞"}
        }
        tiers.append({
            "tier": tier.value,
            **benefits,
            "referral_range": thresholds[tier]
        })
    
    return {
        "tiers": tiers,
        "how_to_level_up": "Refer friends to iHhashi! Each successful referral moves you closer to the next tier.",
        "referral_reward": f"{CoinValues.REFERRAL_BONUS_REFERRER} Hashi Coins for you, {CoinValues.REFERRAL_BONUS_REFEREE} for your friend!"
    }


@router.post("/redeem/free-delivery", response_model=RedeemResponse)
async def redeem_free_delivery(current_user = Depends(get_current_user)):
    """Redeem Hashi Coins for a free delivery voucher"""
    # TODO: Check balance and process redemption
    
    return RedeemResponse(
        success=False,
        message=f"You need {CoinValues.FREE_DELIVERY_COST} Hashi Coins for free delivery",
        coins_spent=0,
        new_balance=0,
        reward_type="free_delivery",
        reward_value=0.0,
        expires_at=None
    )


@router.post("/redeem/discount/{amount}", response_model=RedeemResponse)
async def redeem_discount(
    amount: int,  # 15 or 30
    current_user = Depends(get_current_user)
):
    """Redeem Hashi Coins for a discount voucher (R15 or R30)"""
    if amount not in [15, 30]:
        raise HTTPException(status_code=400, detail="Discount must be R15 or R30")
    
    coins_required = CoinValues.DISCOUNT_15_COST if amount == 15 else CoinValues.DISCOUNT_30_COST
    
    # TODO: Check balance and process redemption
    
    return RedeemResponse(
        success=False,
        message=f"You need {coins_required} Hashi Coins for R{amount} discount",
        coins_spent=0,
        new_balance=0,
        reward_type=f"discount_{amount}",
        reward_value=float(amount),
        expires_at=None
    )


@router.get("/coin-history")
async def get_coin_history(
    limit: int = Query(20, le=100),
    current_user = Depends(get_current_user)
):
    """Get your Hashi Coin transaction history"""
    # TODO: Fetch from database
    
    return {
        "transactions": [],
        "total_earned": 0,
        "total_spent": 0,
        "current_balance": 0
    }


@router.get("/referral-history")
async def get_referral_history(
    limit: int = Query(20, le=100),
    current_user = Depends(get_current_user)
):
    """Get your referral history"""
    # TODO: Fetch from database
    
    return {
        "referrals": [],
        "total_referrals": 0,
        "completed_referrals": 0,
        "pending_referrals": 0,
        "coins_earned_from_referrals": 0
    }


# === SPECIAL PROMOTIONS ===

@router.get("/promotions")
async def get_active_promotions():
    """Get active special promotions for Hashi Coins"""
    return {
        "promotions": [
            {
                "id": "double-referral-weekend",
                "title": "Double Referral Weekend!",
                "description": "This weekend only: Get DOUBLE Hashi Coins for every referral!",
                "bonus_multiplier": 2,
                "starts_at": "2026-03-01T00:00:00Z",
                "ends_at": "2026-03-02T23:59:59Z",
                "is_active": True
            },
            {
                "id": "first-order-bonus",
                "title": "First Order Bonus",
                "description": f"Get {CoinValues.FIRST_ORDER_BONUS} bonus Hashi Coins on your first order!",
                "bonus_coins": CoinValues.FIRST_ORDER_BONUS,
                "is_active": True
            }
        ]
    }


@router.post("/apply-referral")
async def apply_referral_code(
    referral_code: str,
    current_user = Depends(get_current_user)
):
    """Apply a friend's referral code during signup to get bonus coins"""
    # TODO: Validate and process
    
    code = referral_code.upper()
    if not code.startswith("IH-C"):
        raise HTTPException(status_code=400, detail="Invalid customer referral code")
    
    return {
        "success": True,
        "message": f"Welcome to iHhashi! {CoinValues.REFERRAL_BONUS_REFEREE} Hashi Coins added to your account!",
        "coins_received": CoinValues.REFERRAL_BONUS_REFEREE,
        "referral_code": code
    }
