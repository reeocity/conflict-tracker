from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
from auth import (
    create_user,
    get_user_by_email,
    verify_password,
    create_access_token,
    verify_token,
    get_user_by_id,
    save_user_subscription,
    get_user_subscriptions,
    delete_user_subscription,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# ─── Request/Response Models ──────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: Optional[str] = None


class SubscriptionRequest(BaseModel):
    country: Optional[str] = None
    category: Optional[str] = None


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    country: Optional[str] = None
    category: Optional[str] = None
    created_at: Optional[str] = None


# ─── Helper function to extract user from token ────────────────────────────────
def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Extract user from authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = parts[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload


# ─── Endpoints ────────────────────────────────────────────────────────────────
@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest):
    """Register a new user"""
    # Check if user already exists
    existing_user = get_user_by_email(req.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate email format (basic)
    if "@" not in req.email or "." not in req.email.split("@")[1]:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Validate password length
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Create user
    user = create_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    # Create access token
    token = create_access_token(user["id"], user["email"])
    
    return AuthResponse(
        access_token=token,
        user={
            "id": user["id"],
            "email": user["email"],
            "created_at": user["created_at"],
        }
    )


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest):
    """Login user with email and password"""
    user = get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    token = create_access_token(user["id"], user["email"])
    
    return AuthResponse(
        access_token=token,
        user={
            "id": user["id"],
            "email": user["email"],
            "created_at": str(user["created_at"]),
        }
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user"""
    user = get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(**user)


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user (invalidate token on client side)"""
    return {"message": "Logout successful"}


# ─── Subscription Endpoints ───────────────────────────────────────────────────
@router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(
    req: SubscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a user alert subscription"""
    subscription = save_user_subscription(
        current_user["user_id"],
        country=req.country,
        category=req.category
    )
    if not subscription:
        raise HTTPException(status_code=500, detail="Failed to save subscription")
    
    return SubscriptionResponse(**subscription)


@router.get("/subscriptions")
async def list_subscriptions(current_user: dict = Depends(get_current_user)):
    """List all subscriptions for current user"""
    subscriptions = get_user_subscriptions(current_user["user_id"])
    return {"subscriptions": subscriptions}


@router.delete("/subscriptions/{subscription_id}")
async def delete_subscription(
    subscription_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a subscription"""
    success = delete_user_subscription(subscription_id, current_user["user_id"])
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return {"message": "Subscription deleted"}
