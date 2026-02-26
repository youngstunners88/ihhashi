from fastapi import APIRouter, Depends, HTTPException
from app.services.auth import get_current_user
from app.models import User, UserLocation

router = APIRouter()

@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile")
async def update_profile(
    location: UserLocation,
    current_user: User = Depends(get_current_user)
):
    # TODO: Update user location
    return {"message": "Profile updated", "location": location}

@router.get("/orders")
async def get_user_orders(current_user: User = Depends(get_current_user)):
    # TODO: Fetch user's orders
    return {"orders": []}
