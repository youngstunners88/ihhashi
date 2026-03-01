from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from app.services.auth import get_current_user
from app.models import User, UserLocation
from app.database import get_collection
from app.utils.validation import safe_object_id
from app.middleware.rate_limit import limiter

router = APIRouter()


class FCMTokenUpdate(BaseModel):
    token: str = Field(..., min_length=1, max_length=4096, description="FCM device registration token")


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


@router.post("/fcm-token", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def register_fcm_token(
    request: Request,
    body: FCMTokenUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Store or refresh the caller's FCM device token so the backend can send
    push notifications for order and delivery status updates.

    Tokens are stored per-user in the `users` collection under `fcm_token`.
    A user may only have one active token at a time (last-write wins).
    """
    users_col = get_collection("users")
    user_id = safe_object_id(str(current_user.id))
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")

    await users_col.update_one(
        {"_id": user_id},
        {"$set": {"fcm_token": body.token}},
    )
