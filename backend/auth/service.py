# backend/auth/service.py
"""
Authentication service layer for business logic.
Separates business logic from route handlers.
"""
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from backend.models import User
from backend.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    needs_rehash,
    PasswordValidationError,
)

# Logging
logger = logging.getLogger("spms_auth_service")

# Configuration
MAX_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_MINUTES = 15


class AuthService:
    """Service class for authentication operations."""
    
    def __init__(self, db: Session):
        """
        Initialize auth service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    # -------------------------
    # Authentication Methods
    # -------------------------
    
    def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Tuple[User, Dict[str, str]]:
        """
        Authenticate user and return user + tokens.
        
        Args:
            username: Username
            password: Plain password
            
        Returns:
            Tuple of (User, tokens_dict)
            
        Raises:
            HTTPException: If authentication fails
        """
        # Find user (case-insensitive)
        user = self.db.query(User).filter(
            User.username == username.lower()
        ).first()
        
        if not user:
            logger.warning(f"Login attempt for non-existent user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if account is locked
        self._check_account_lock(user)
        
        # Verify password
        if not verify_password(password, user.password_hash):
            self._handle_failed_login(user)
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
                detail=f"Account is {user.status}. Please contact administrator.",
            )
        
        # Successful login
        self._handle_successful_login(user, password)
        
        # Generate tokens
        tokens = self._generate_tokens(user)
        
        logger.info(f"Successful login for user: {user.username}")
        
        return user, tokens
    
    def logout_user(self, user: User, token: str) -> bool:
        """
        Logout user and revoke token.
        
        Args:
            user: User object
            token: Access token to revoke
            
        Returns:
            bool: True if logout successful
        """
        from backend.auth.utils import revoke_token
        
        revoked = revoke_token(token)
        
        if revoked:
            logger.info(f"User logged out: {user.username}")
        else:
            logger.warning(f"Failed to revoke token for user: {user.username}")
        
        return revoked
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            Dict with new access_token
            
        Raises:
            HTTPException: If refresh token is invalid
        """
        from backend.auth.utils import decode_refresh_token
        from jose import JWTError
        
        try:
            payload = decode_refresh_token(refresh_token)
            username = payload.get("sub")
            
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            user = self.db.query(User).filter(User.username == username).first()
            if not user or user.status != "active":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Create new access token
            token_data = {
                "sub": user.username,
                "role": user.role,
                "user_id": user.id,
            }
            new_access_token = create_access_token(token_data)
            
            logger.info(f"Token refreshed for user: {user.username}")
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer"
            }
            
        except JWTError as exc:
            logger.warning(f"Invalid refresh token: {exc}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
    
    # -------------------------
    # Password Management
    # -------------------------
    
    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str
    ) -> None:
        """
        Change user password.
        
        Args:
            user: User object
            current_password: Current password
            new_password: New password
            
        Raises:
            HTTPException: If current password is wrong or new password invalid
        """
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            logger.warning(f"Failed password change attempt for user: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Validate and hash new password
        try:
            new_hash = hash_password(new_password, validate_policy=True)
        except PasswordValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc)
            )
        
        # Update password
        user.password_hash = new_hash
        user.password_changed_at = datetime.now(timezone.utc)
        self.db.commit()
        
        logger.info(f"Password changed for user: {user.username}")
    
    def reset_password(
        self,
        username: str,
        new_password: str
    ) -> None:
        """
        Reset user password (admin function).
        
        Args:
            username: Username
            new_password: New password
            
        Raises:
            HTTPException: If user not found or password invalid
        """
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate and hash new password
        try:
            new_hash = hash_password(new_password, validate_policy=True)
        except PasswordValidationError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc)
            )
        
        user.password_hash = new_hash
        user.password_changed_at = datetime.now(timezone.utc)
        user.failed_login_attempts = 0
        user.account_locked_until = None
        self.db.commit()
        
        logger.info(f"Password reset for user: {username}")
    
    # -------------------------
    # Account Management
    # -------------------------
    
    def unlock_account(self, username: str) -> None:
        """
        Unlock a user account.
        
        Args:
            username: Username to unlock
            
        Raises:
            HTTPException: If user not found
        """
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.failed_login_attempts = 0
        user.account_locked_until = None
        self.db.commit()
        
        logger.info(f"Account unlocked: {username}")
    
    def activate_account(self, username: str) -> None:
        """
        Activate a user account.
        
        Args:
            username: Username to activate
            
        Raises:
            HTTPException: If user not found
        """
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.status = "active"
        user.failed_login_attempts = 0
        user.account_locked_until = None
        self.db.commit()
        
        logger.info(f"Account activated: {username}")
    
    def deactivate_account(self, username: str) -> None:
        """
        Deactivate a user account.
        
        Args:
            username: Username to deactivate
            
        Raises:
            HTTPException: If user not found
        """
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.status = "inactive"
        self.db.commit()
        
        logger.info(f"Account deactivated: {username}")
    
    # -------------------------
    # Private Helper Methods
    # -------------------------
    
    def _check_account_lock(self, user: User) -> None:
        """
        Check if account is locked and raise exception if it is.
        
        Args:
            user: User object to check
            
        Raises:
            HTTPException: If account is locked
        """
        if user.account_locked_until:
            now = datetime.now(timezone.utc)
            locked_until = user.account_locked_until
            
            # Handle timezone-naive datetime
            if locked_until.tzinfo is None:
                locked_until = locked_until.replace(tzinfo=timezone.utc)
            
            if now < locked_until:
                remaining = (locked_until - now).seconds // 60
                logger.warning(f"Login attempt for locked account: {user.username}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Account locked. Try again in {remaining} minutes.",
                )
    
    def _handle_failed_login(self, user: User) -> None:
        """
        Handle failed login attempt by incrementing counter and locking if needed.
        
        Args:
            user: User object
        """
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        
        if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
            user.account_locked_until = datetime.now(timezone.utc) + timedelta(
                minutes=ACCOUNT_LOCKOUT_MINUTES
            )
            self.db.commit()
            logger.warning(f"Account locked due to failed attempts: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account locked due to too many failed attempts. "
                       f"Try again in {ACCOUNT_LOCKOUT_MINUTES} minutes.",
            )
        
        self.db.commit()
        logger.warning(
            f"Failed login attempt for user: {user.username} "
            f"(Attempt {user.failed_login_attempts})"
        )
    
    def _handle_successful_login(self, user: User, password: str) -> None:
        """
        Handle successful login by resetting counters and updating last login.
        
        Args:
            user: User object
            password: Plain password (for hash upgrade check)
        """
        user.failed_login_attempts = 0
        user.account_locked_until = None
        user.last_login = datetime.now(timezone.utc)
        
        # Check if password hash needs upgrade
        if needs_rehash(user.password_hash):
            logger.info(f"Upgrading password hash for user: {user.username}")
            user.password_hash = hash_password(password, validate_policy=False)
        
        self.db.commit()
    
    def _generate_tokens(self, user: User) -> Dict[str, str]:
        """
        Generate access and refresh tokens for user.
        
        Args:
            user: User object
            
        Returns:
            Dict with access_token, refresh_token, and token_type
        """
        token_data = {
            "sub": user.username,
            "role": user.role,
            "user_id": user.id,
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }


# -------------------------
# Convenience Functions
# -------------------------

def get_auth_service(db: Session = None) -> AuthService:
    """
    Get an instance of AuthService.
    
    Args:
        db: Optional database session
        
    Returns:
        AuthService: Service instance
    """
    return AuthService(db)