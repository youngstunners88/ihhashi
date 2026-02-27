from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta, datetime, timezone
from app.services.auth import (
    authenticate_user, create_access_token, create_refresh_token,
    get_current_user, logout_user
)
from app.models import UserCreate, User
from app.config import settings
from app.middleware.rate_limit import limiter

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/register", status_code=201)
@limiter.limit("10/minute")
async def register(request: Request, user_data: UserCreate):
    """Register a new user. Rate limited to 10/minute per IP."""
    from app.services.auth import create_user
    user = await create_user(user_data)
    return {"message": "User created successfully", "user_id": user.id}


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """Login. Rate limited to 5/minute per IP to prevent brute force."""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive. Contact support.",
        )
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    refresh_token = create_refresh_token(data={"sub": user.id, "role": user.role})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": {
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "full_name": user.full_name,
            "role": user.role,
        },
    }


@router.post("/refresh")
@limiter.limit("20/minute")
async def refresh_token(request: Request, token: str):
    """Exchange a refresh token for a new access token."""
    from jose import JWTError, jwt
    from app.core.redis_client import TokenBlacklist

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    if await TokenBlacklist.is_blacklisted(token):
        raise credentials_exception
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if not user_id or token_type != "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    new_access = create_access_token(
        data={"sub": user_id, "role": payload.get("role")},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {
        "access_token": new_access,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
):
    """Logout and blacklist the current token."""
    await logout_user(token)
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "phone": current_user.phone,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
    }


@router.post("/password-reset/request")
@limiter.limit("3/minute")
async def request_password_reset(request: Request, email: str):
    """Request a password reset. Always returns 200 to prevent email enumeration."""
    import logging
    from app.database import get_collection
    from bson import ObjectId

    users_col = get_collection("users")
    user = await users_col.find_one({"email": email})
    if user:
        reset_token = create_access_token(
            data={"sub": str(user["_id"]), "type": "password_reset"},
            expires_delta=timedelta(hours=1),
        )
        # TODO: Send actual email via SendGrid/Twilio
        logging.getLogger(__name__).info(f"Password reset requested for {email}")
    return {"message": "If that email exists, a reset link has been sent."}


@router.post("/password-reset/confirm")
@limiter.limit("5/minute")
async def confirm_password_reset(request: Request, token: str, new_password: str):
    """Confirm password reset with token."""
    from jose import JWTError, jwt
    from app.services.auth import get_password_hash
    from app.database import get_collection
    from bson import ObjectId

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        if payload.get("type") != "password_reset" or not user_id:
            raise HTTPException(status_code=400, detail="Invalid reset token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if len(new_password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters")

    users_col = get_collection("users")
    await users_col.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "hashed_password": get_password_hash(new_password),
            "updated_at": datetime.now(timezone.utc),
        }},
    )
    return {"message": "Password reset successfully"}
