import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.auth.service import AuthService
from backend.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    require_admin,
    oauth2_scheme,
)
from backend.schemas.schemas import (
    LoginRequest,
    TokenResponse,
    UserResponse,
    MessageResponse,
    PasswordChangeRequest,
    RefreshTokenRequest,
    RegisterRequest,
)

# -------------------------
# Router & Config
# -------------------------
router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
logger = logging.getLogger("spms_auth_routes")

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

FAILED_ATTEMPTS = {}
LOCKED_ACCOUNTS = {}

# -------------------------
# Helpers
# -------------------------
def is_account_locked(username: str) -> bool:
    if username in LOCKED_ACCOUNTS:
        unlock_time = LOCKED_ACCOUNTS[username]
        if datetime.utcnow() < unlock_time:
            return True
        else:
            del LOCKED_ACCOUNTS[username]
    return False

def lock_account(username: str, duration_seconds: int = 900):
    LOCKED_ACCOUNTS[username] = datetime.utcnow() + timedelta(seconds=duration_seconds)

def increment_failed_attempts(username: str):
    FAILED_ATTEMPTS[username] = FAILED_ATTEMPTS.get(username, 0) + 1
    if FAILED_ATTEMPTS[username] >= 5:
        lock_account(username)

def reset_failed_attempts(username: str):
    FAILED_ATTEMPTS[username] = 0

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

# -------------------------
# Public Endpoints
# -------------------------
@router.post("/login", response_model=TokenResponse, summary="User Login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    request: Optional[Request] = None,
):
    username = form_data.username
    password = form_data.password

    if is_account_locked(username):
        raise HTTPException(status_code=403, detail="Account locked. Try again later.")

    # Example: hardcoded admin user (replace with DB lookup)
    if username != "admin" or password != "admin123":
        increment_failed_attempts(username)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    reset_failed_attempts(username)

    access_token = create_access_token(data={"sub": username})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

@router.post("/logout", response_model=MessageResponse, summary="User Logout")
def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    revoked = auth_service.logout_user(current_user, token)
    return MessageResponse(
        message="Successfully logged out" if revoked else "Logout processed",
        detail="Token has been revoked" if revoked else "Token may already be expired",
    )

@router.post("/refresh", response_model=TokenResponse, summary="Refresh Access Token")
def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    tokens = auth_service.refresh_access_token(refresh_data.refresh_token)
    return TokenResponse(**tokens)

# -------------------------
# Authenticated User Endpoints
# -------------------------
@router.get("/me", response_model=UserResponse, summary="Get Current User")
def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.post("/change-password", response_model=MessageResponse, summary="Change Password")
def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    auth_service.change_password(
        user=current_user,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
    )
    return MessageResponse(
        message="Password changed successfully",
        detail="Please login with your new password",
    )

# -------------------------
# Registration
# -------------------------
@router.post("/register", response_model=MessageResponse, summary="Register New User")
def register(
    register_data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    new_user = auth_service.register_user(
        username=register_data.username,
        password=register_data.password,
        full_name=register_data.full_name,
        email=register_data.email,
        role=register_data.role or "staff",
    )
    return MessageResponse(
        message=f"User '{new_user.username}' registered successfully",
        detail="Please verify your email if required",
    )

# -------------------------
# Admin Endpoints
# -------------------------
@router.post("/admin/unlock-account/{username}", response_model=MessageResponse)
def unlock_account(username: str, admin: User = Depends(require_admin), auth_service: AuthService = Depends(get_auth_service)):
    auth_service.unlock_account(username)
    return MessageResponse(message=f"Account unlocked for user: {username}", detail="User can now login")

@router.post("/admin/reset-password/{username}", response_model=MessageResponse)
def reset_password(username: str, new_password: str = Body(..., embed=True, min_length=8), admin: User = Depends(require_admin), auth_service: AuthService = Depends(get_auth_service)):
    auth_service.reset_password(username, new_password)
    return MessageResponse(message=f"Password reset for user: {username}", detail="User should change password on next login")

@router.post("/admin/activate-account/{username}", response_model=MessageResponse)
def activate_account(username: str, admin: User = Depends(require_admin), auth_service: AuthService = Depends(get_auth_service)):
    auth_service.activate_account(username)
    return MessageResponse(message=f"Account activated for user: {username}", detail="User can now login")

@router.post("/admin/deactivate-account/{username}", response_model=MessageResponse)
def deactivate_account(username: str, admin: User = Depends(require_admin), auth_service: AuthService = Depends(get_auth_service)):
    auth_service.deactivate_account(username)
    return MessageResponse(message=f"Account deactivated for user: {username}", detail="User cannot login until reactivated")
