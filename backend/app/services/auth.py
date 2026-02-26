from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.models import User, UserCreate, UserRole
from app.database import get_collection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

async def create_user(user_data: UserCreate) -> User:
    users_col = get_collection("users")
    
    # Check if user exists
    existing = await users_col.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    now = datetime.utcnow()
    user_doc = {
        "email": user_data.email,
        "phone": user_data.phone,
        "full_name": user_data.full_name,
        "hashed_password": get_password_hash(user_data.password),
        "role": user_data.role,
        "is_active": True,
        "created_at": now,
        "updated_at": now
    }
    
    result = await users_col.insert_one(user_doc)
    user_doc["id"] = str(result.inserted_id)
    
    return User(**user_doc)

async def authenticate_user(email: str, password: str) -> Optional[User]:
    users_col = get_collection("users")
    user_doc = await users_col.find_one({"email": email})
    
    if not user_doc:
        return None
    if not verify_password(password, user_doc["hashed_password"]):
        return None
    
    user_doc["id"] = str(user_doc["_id"])
    return User(**user_doc)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    users_col = get_collection("users")
    user_doc = await users_col.find_one({"_id": user_id})
    if not user_doc:
        raise credentials_exception
    
    user_doc["id"] = str(user_doc["_id"])
    return User(**user_doc)
