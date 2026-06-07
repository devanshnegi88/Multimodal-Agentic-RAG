"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from bson import ObjectId

from app.config import settings
from app.database.mongodb import get_database
from app.database.schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.utils.logger import logger

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + expires_delta
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db=Depends(get_database)):
    existing = await db["users"].find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "_id": str(ObjectId()),
        "email": payload.email,
        "username": payload.username,
        "hashed_password": hash_password(payload.password),
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "settings": {},
    }
    await db["users"].insert_one(user_doc)
    logger.info(f"New user registered: {payload.email}")

    access_token = create_token(
        {"sub": user_doc["_id"], "email": payload.email},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_token(
        {"sub": user_doc["_id"], "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db=Depends(get_database)):
    user = await db["users"].find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.get("is_active"):
        raise HTTPException(status_code=403, detail="Account disabled")

    access_token = create_token(
        {"sub": user["_id"], "email": user["email"]},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_token(
        {"sub": user["_id"], "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    logger.info(f"User logged in: {payload.email}")
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(db=Depends(get_database)):
    # Simplified for demo — in prod use get_current_user dependency
    raise HTTPException(status_code=501, detail="Attach auth dependency")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db=Depends(get_database)):
    try:
        payload = jwt.decode(
            refresh_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        user_id = payload.get("sub")
        user = await db["users"].find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        new_access = create_token(
            {"sub": user["_id"], "email": user["email"]},
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        new_refresh = create_token(
            {"sub": user["_id"], "type": "refresh"},
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        return TokenResponse(access_token=new_access, refresh_token=new_refresh)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
