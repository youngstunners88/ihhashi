from fastapi import APIRouter, Depends
from app.services.auth import get_current_user
from app.models import Rider, RiderCreate, RiderStatus
from app.models import User

router = APIRouter()

@router.get("/profile")
async def get_rider_profile(current_user: User = Depends(get_current_user)):
    # TODO: Fetch rider profile
    return {"rider": None}

@router.put("/status")
async def update_rider_status(
    status: RiderStatus,
    lat: float,
    lng: float,
    current_user: User = Depends(get_current_user)
):
    # TODO: Update rider status and location
    return {"message": "Status updated", "status": status}

@router.get("/orders/available")
async def get_available_orders(
    current_user: User = Depends(get_current_user)
):
    # TODO: Fetch orders ready for pickup near rider
    return {"orders": []}

@router.post("/orders/{order_id}/accept")
async def accept_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    # TODO: Accept delivery order
    return {"message": "Order accepted", "order_id": order_id}

@router.get("/earnings")
async def get_earnings(current_user: User = Depends(get_current_user)):
    # TODO: Calculate rider earnings
    return {
        "today": 0.0,
        "this_week": 0.0,
        "this_month": 0.0,
        "total": 0.0
    }
