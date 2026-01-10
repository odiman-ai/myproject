# backend/auth.py
"""
Complete Authentication Module for SPMS with Role-Based Access Control
Features: Admin/User login, Role-based access, Auto-authorization in Swagger

Usage:
    from backend.auth import router, get_current_user, require_admin
    app.include_router(router, prefix="/api/v1")
"""

import os
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr, Field

# -------------------------
# Configuration
# -------------------------

SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))  # 1 hour default
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
BCRYPT_MAX_BYTES = 72

logger = logging.getLogger("spms_auth")

# -------------------------
# Router Setup
# -------------------------

router = APIRouter()
# FIXED: Changed tokenUrl to match actual login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # This matches /login endpoint

# -------------------------
# Schemas
# -------------------------

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    role: str
    status: str
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Schema for creating new users"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    role: str = Field(default="user", pattern="^(admin|user)$")


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    checks: Dict[str, Any]


# -------------------------
# Password Utilities (bcrypt-safe)
# -------------------------

def ensure_bcrypt_safe(password: str) -> str:
    """
    Ensure password is safe for bcrypt (max 72 bytes).
    Truncates if needed to prevent errors.
    """
    encoded = password.encode('utf-8')
    if len(encoded) <= BCRYPT_MAX_BYTES:
        return password
    
    truncated = encoded[:BCRYPT_MAX_BYTES].decode('utf-8', errors='ignore')
    logger.warning("Password truncated to 72 bytes for bcrypt compatibility")
    return truncated


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt with 72-byte safety.
    """
    safe_password = ensure_bcrypt_safe(password)
    password_bytes = safe_password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against bcrypt hash with 72-byte safety.
    """
    try:
        safe_password = ensure_bcrypt_safe(plain_password)
        password_bytes = safe_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as exc:
        logger.error(f"Password verification error: {exc}")
        return False


# -------------------------
# JWT Token Utilities
# -------------------------

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# -------------------------
# Database Dependency
# -------------------------

def get_db():
    """
    Database session dependency.
    Override this in your main.py with your actual database session.
    """
    raise NotImplementedError(
        "Please implement get_db() in your main.py and override this dependency"
    )


# -------------------------
# Account Lockout Utilities
# -------------------------

def check_account_lock(user) -> None:
    """
    Check if account is locked and raise exception if needed.
    """
    if not user.account_locked_until:
        return
    
    now = datetime.now(timezone.utc)
    locked_until = user.account_locked_until
    
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)
    
    if now < locked_until:
        remaining = (locked_until - now).seconds // 60
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked. Try again in {remaining} minutes."
        )


def handle_failed_login(user, db: Session) -> None:
    """
    Handle failed login attempt with lockout logic.
    """
    user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
    
    if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
        user.account_locked_until = datetime.now(timezone.utc) + timedelta(
            minutes=LOCKOUT_MINUTES
        )
        db.commit()
        
        logger.warning(f"Account locked: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked due to too many failed attempts. "
                   f"Try again in {LOCKOUT_MINUTES} minutes."
        )
    
    db.commit()
    logger.warning(
        f"Failed login attempt for {user.username} "
        f"(Attempt {user.failed_login_attempts}/{MAX_LOGIN_ATTEMPTS})"
    )


def handle_successful_login(user, db: Session) -> None:
    """
    Handle successful login - reset counters and update timestamps.
    """
    user.failed_login_attempts = 0
    user.account_locked_until = None
    user.last_login = datetime.now(timezone.utc)
    db.commit()


# -------------------------
# Authentication Dependencies
# -------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user from JWT token.
    This is automatically applied to all protected endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        username: Optional[str] = payload.get("sub")
        
        if username is None:
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception
    
    from backend.models import User
    
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Ensure user account is active.
    """
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {current_user.status}"
        )
    
    return current_user


def require_admin(current_user = Depends(get_current_active_user)):
    """
    Require admin role for endpoint access.
    Use this dependency on admin-only endpoints.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required"
        )
    
    return current_user


def require_user_or_admin(current_user = Depends(get_current_active_user)):
    """
    Allow both user and admin roles.
    Use this for endpoints accessible to logged-in users.
    """
    if current_user.role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges"
        )
    
    return current_user


# -------------------------
# Authentication Endpoints
# -------------------------

@router.post("/login", response_model=TokenResponse, tags=["Authentication"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    **User/Admin Login Endpoint**
    
    Authenticate and receive JWT access token that works automatically 
    with Swagger's "Authorize" button.
    
    **Usage in Swagger:**
    1. Click "Authorize" button (lock icon) at top of Swagger UI
    2. Enter username and password
    3. Click "Authorize"
    4. All subsequent requests will automatically include the token
    
    **Features:**
    - Works for both admin and user roles
    - Automatic token inclusion after authorization
    - Account lockout after 5 failed attempts (15 min)
    - Token expires in 60 minutes (configurable)
    
    **Form Data:**
    - username: Your username
    - password: Your password
    
    **Returns:**
    - access_token: JWT token (automatically used by Swagger)
    - token_type: "bearer"
    - expires_in: Token validity in seconds
    """
    from backend.models import User
    
    # Find user (case-insensitive)
    user = db.query(User).filter(
        User.username == form_data.username.lower()
    ).first()
    
    if not user:
        logger.warning(f"Login attempt for non-existent user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is locked
    check_account_lock(user)
    
    # Verify password
    if not verify_password(form_data.password, user.password_hash):
        handle_failed_login(user, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if user.status != "active":
        logger.warning(f"Login attempt for {user.status} account: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status}. Please contact administrator."
        )
    
    # Successful login
    handle_successful_login(user, db)
    
    # Create access token with role information
    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role,
            "user_id": user.id
        }
    )
    
    logger.info(f"Successful login: {user.username} (role: {user.role})")
    
    return TokenResponse(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
def get_current_user_info(current_user = Depends(get_current_active_user)):
    """
    Get current authenticated user information.
    
    **Requires:** Valid JWT token (automatically included after authorization)
    
    **Returns:** Complete user profile including role
    """
    return current_user


@router.post("/auth/logout", tags=["Authentication"])
def logout(current_user = Depends(get_current_user)):
    """
    Logout current user.
    
    **Note:** Token remains valid until expiration.
    To fully logout, click "Authorize" button and click "Logout".
    """
    logger.info(f"User logged out: {user.username} (role: {current_user.role})")
    return {
        "message": "Successfully logged out",
        "note": "Click 'Authorize' button in Swagger and logout to clear token"
    }


# -------------------------
# User Management Endpoints (Admin Only)
# -------------------------

@router.post("/auth/users", response_model=UserResponse, tags=["User Management"])
def create_user(
    user_data: UserCreate,
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    **Create New User (Admin Only)**
    
    Create a new user account with specified role.
    
    **Requires:** Admin authentication
    
    **Roles:**
    - `admin`: Full access to all endpoints including user management
    - `user`: Access to regular user endpoints only
    
    **Request Body:**
    ```json
    {
      "username": "johndoe",
      "password": "securepassword123",
      "full_name": "John Doe",
      "email": "john@example.com",
      "role": "user"
    }
    ```
    
    **Returns:** Created user information (without password)
    """
    from backend.models import User
    
    # Check if username already exists
    existing_user = db.query(User).filter(
        User.username == user_data.username.lower()
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_data.username}' already exists"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(
        User.email == user_data.email.lower()
    ).first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_data.email}' already registered"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username.lower(),
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        email=user_data.email.lower(),
        role=user_data.role,
        status="active",
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user created by {admin.username}: {new_user.username} (role: {new_user.role})")
    
    return new_user


@router.get("/auth/users", response_model=list[UserResponse], tags=["User Management"])
def list_users(
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    **List All Users (Admin Only)**
    
    Get a list of all users in the system.
    
    **Requires:** Admin authentication
    
    **Returns:** List of all users with their details
    """
    from backend.models import User
    
    users = db.query(User).all()
    return users


@router.get("/auth/users/{user_id}", response_model=UserResponse, tags=["User Management"])
def get_user(
    user_id: int,
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    **Get User Details (Admin Only)**
    
    Get detailed information about a specific user.
    
    **Requires:** Admin authentication
    """
    from backend.models import User
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.delete("/auth/users/{user_id}", tags=["User Management"])
def delete_user(
    user_id: int,
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    **Delete User (Admin Only)**
    
    Permanently delete a user account.
    
    **Requires:** Admin authentication
    
    **Note:** Cannot delete your own account
    """
    from backend.models import User
    
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    username = user.username
    db.delete(user)
    db.commit()
    
    logger.info(f"User deleted by {admin.username}: {username}")
    
    return {"message": f"User '{username}' deleted successfully"}


# -------------------------
# Admin Endpoints
# -------------------------

@router.post("/auth/admin/unlock-account/{username}", tags=["Admin"])
def unlock_account(
    username: str,
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    **Unlock User Account (Admin Only)**
    
    Unlock a locked user account and reset failed login attempts.
    
    **Requires:** Admin authentication
    """
    from backend.models import User
    
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.failed_login_attempts = 0
    user.account_locked_until = None
    db.commit()
    
    logger.info(f"Account unlocked by {admin.username}: {username}")
    
    return {"message": f"Account unlocked: {username}"}


@router.patch("/auth/admin/change-role/{user_id}", tags=["Admin"])
def change_user_role(
    user_id: int,
    new_role: str = Field(..., pattern="^(admin|user)$"),
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    **Change User Role (Admin Only)**
    
    Change a user's role between 'admin' and 'user'.
    
    **Requires:** Admin authentication
    
    **Note:** Cannot change your own role
    """
    from backend.models import User
    
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    old_role = user.role
    user.role = new_role
    db.commit()
    
    logger.info(f"Role changed by {admin.username}: {user.username} from {old_role} to {new_role}")
    
    return {
        "message": f"User '{user.username}' role changed from '{old_role}' to '{new_role}'"
    }


# -------------------------
# Health Check Endpoint
# -------------------------

@router.get("/health", response_model=HealthResponse, tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """
    System health check endpoint.
    
    **No authentication required**
    """
    health_data = {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("SPMS_ENV", "development"),
        "checks": {}
    }
    
    # Database connectivity check
    try:
        db.execute(text("SELECT 1"))
        health_data["checks"]["database"] = {
            "status": "connected",
            "type": "sqlite"
        }
    except Exception as exc:
        logger.error(f"Database health check failed: {exc}")
        health_data["status"] = "degraded"
        health_data["checks"]["database"] = {
            "status": "disconnected",
            "error": str(exc)
        }
    
    # Application check
    health_data["checks"]["application"] = {
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    return health_data


# -------------------------
# Utility Functions (Export)
# -------------------------

__all__ = [
    "router",
    "get_current_user",
    "get_current_active_user",
    "require_admin",
    "require_user_or_admin",
    "hash_password",
    "verify_password",
]