from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from app.services.auth import get_current_user
from app.models import Merchant, MerchantCreate, MerchantCategory
from app.models import User

router = APIRouter()

@router.get("/")
async def get_merchants(
    category: Optional[MerchantCategory] = None,
    city: Optional[str] = None,
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius_km: float = Query(5.0),
    limit: int = Query(20),
    offset: int = Query(0)
):
    # TODO: Implement merchant search with geolocation
    return {
        "merchants": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }

@router.get("/{merchant_id}")
async def get_merchant(merchant_id: str):
    # TODO: Fetch single merchant
    return {"merchant": None}

@router.get("/{merchant_id}/menu")
async def get_merchant_menu(merchant_id: str):
    # TODO: Fetch merchant menu
    return {"menu": []}

@router.post("/")
async def create_merchant(
    merchant_data: MerchantCreate,
    current_user: User = Depends(get_current_user)
):
    # TODO: Create merchant (requires merchant role)
    return {"message": "Merchant created", "merchant_id": "new_id"}
