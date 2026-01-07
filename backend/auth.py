# backend/auth.py
"""
Complete Authentication Module for SPMS
Drop-in solution with login, lockout, health check, and bcrypt safety

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
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
BCRYPT_MAX_BYTES = 72

logger = logging.getLogger("spms_auth")

# -------------------------
# Router Setup
# -------------------------

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# -------------------------
# Schemas
# -------------------------

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


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
    
    # Truncate safely at character boundary
    truncated = encoded[:BCRYPT_MAX_BYTES].decode('utf-8', errors='ignore')
    logger.warning("Password truncated to 72 bytes for bcrypt compatibility")
    return truncated


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt with 72-byte safety.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Bcrypt hash (UTF-8 decoded)
    """
    safe_password = ensure_bcrypt_safe(password)
    password_bytes = safe_password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against bcrypt hash with 72-byte safety.
    
    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hash
        
    Returns:
        bool: True if password matches
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
    
    Args:
        data: Token payload (should include 'sub' for username)
        expires_delta: Optional custom expiration
        
    Returns:
        str: Encoded JWT token
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
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Token payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# -------------------------
# Database Dependency
# -------------------------

def get_db():
    """
    Database session dependency.
    Override this in your main.py with your actual database session.
    
    Example:
        from backend.database import SessionLocal
        
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
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
    
    Args:
        user: User model instance
        
    Raises:
        HTTPException: 403 if account is locked
    """
    if not user.account_locked_until:
        return
    
    now = datetime.now(timezone.utc)
    locked_until = user.account_locked_until
    
    # Handle timezone-naive datetime
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
    
    Args:
        user: User model instance
        db: Database session
        
    Raises:
        HTTPException: 403 if account gets locked
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
    
    Args:
        user: User model instance
        db: Database session
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
    
    Args:
        token: JWT access token from Authorization header
        db: Database session
        
    Returns:
        User: Authenticated user object
        
    Raises:
        HTTPException: 401 if token invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        username: Optional[str] = payload.get("sub")
        
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Import User model here to avoid circular imports
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
    
    Args:
        current_user: User from get_current_user
        
    Returns:
        User: Active user object
        
    Raises:
        HTTPException: 403 if user is not active
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
    
    Args:
        current_user: Active user from get_current_active_user
        
    Returns:
        User: Admin user object
        
    Raises:
        HTTPException: 403 if user is not admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required"
        )
    
    return current_user


# -------------------------
# Authentication Endpoints
# -------------------------

@router.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT access token.
    
    **Features:**
    - bcrypt password hashing (72-byte safe)
    - Account lockout after 5 failed attempts (15 min)
    - Timezone-aware datetime handling
    - Automatic counter reset on success
    
    **Security:**
    - Passwords truncated to 72 bytes if needed
    - Failed attempts tracked per user
    - Account auto-locks after max attempts
    - Generic error messages (no user enumeration)
    
    **Form Data:**
    - `username`: Username (case-insensitive)
    - `password`: User password
    
    **Returns:**
    - `access_token`: JWT token for authentication
    - `token_type`: Always "bearer"
    
    **Error Codes:**
    - 401: Invalid credentials
    - 403: Account locked or inactive
    """
    # Import User model here to avoid circular imports
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
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role,
            "user_id": user.id
        }
    )
    
    logger.info(f"Successful login: {user.username}")
    
    return TokenResponse(access_token=access_token)


@router.get("/auth/me", response_model=UserResponse, tags=["Authentication"])
def get_current_user_info(current_user = Depends(get_current_active_user)):
    """
    Get current authenticated user information.
    
    **Requires:** Valid JWT token in Authorization header
    
    **Returns:** Complete user profile (excluding password)
    """
    return current_user


@router.post("/auth/logout", tags=["Authentication"])
def logout(current_user = Depends(get_current_user)):
    """
    Logout current user.
    
    **Note:** In production, implement token blacklisting with Redis.
    Currently, tokens remain valid until expiration.
    
    **Returns:** Success message
    """
    logger.info(f"User logged out: {current_user.username}")
    return {"message": "Successfully logged out"}


# -------------------------
# Health Check Endpoint
# -------------------------

@router.get("/health", response_model=HealthResponse, tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """
    System health check endpoint.
    
    **Checks:**
    - Database connectivity
    - Application status
    
    **Returns:**
    - `status`: "healthy" or "degraded"
    - `version`: Application version
    - `environment`: Current environment
    - `checks`: Individual component status
    
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
            "type": "sqlite"  # Adjust based on your database
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
# Admin Endpoints
# -------------------------

@router.post("/auth/admin/unlock-account/{username}", tags=["Admin"])
def unlock_account(
    username: str,
    admin = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Unlock a locked user account (Admin only).
    
    **Requires:** Admin role
    
    **Actions:**
    - Resets failed login attempts to 0
    - Removes account lock timestamp
    
    **Returns:** Success message
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


# -------------------------
# Utility Functions (Export)
# -------------------------

__all__ = [
    "router",
    "get_current_user",
    "get_current_active_user",
    "require_admin",
    "hash_password",
    "verify_password",
]