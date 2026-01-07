# backend/auth/dependencies.py
"""
Authentication dependencies for FastAPI endpoints.
Provides user authentication, authorization, and role-based access control.
"""
import logging
from typing import Optional, List, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from backend.database import get_db
from backend.models import User
from backend.auth.utils import decode_access_token

# Logging
logger = logging.getLogger("spms_auth_deps")

# OAuth2 scheme - points to the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# -------------------------
# Core Authentication Dependencies
# -------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Decode JWT token and return the corresponding User instance.
    
    **Raises:**
    - 401 if token is invalid or expired
    - 404 if user not found in database
    
    **Usage:**
    ```python
    @router.get("/protected")
    def protected_route(user: User = Depends(get_current_user)):
        return {"user": user.username}
    ```
    
    Args:
        token: JWT access token from Authorization header
        db: Database session
        
    Returns:
        User: Authenticated user object
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token, verify_type=True)
        username: Optional[str] = payload.get("sub")
        
        if username is None:
            logger.warning("Token missing username claim")
            raise credentials_exception
            
    except JWTError as exc:
        logger.warning(f"JWT validation failed: {exc}")
        raise credentials_exception
    
    # Get user from database
    user: Optional[User] = db.query(User).filter(
        User.username == username
    ).first()
    
    if user is None:
        logger.warning(f"User not found in database: {username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Ensure the user account is active and not locked.
    
    **Raises:**
    - 403 if user account is not active or is locked
    
    **Usage:**
    ```python
    @router.get("/protected")
    def protected_route(user: User = Depends(get_current_active_user)):
        return {"user": user.username}
    ```
    
    Args:
        current_user: Authenticated user from get_current_user
        
    Returns:
        User: Active user object
    """
    if current_user.status != "active":
        logger.warning(f"Access denied for {current_user.status} user: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {current_user.status}"
        )
    
    # Check if account is locked
    if hasattr(current_user, 'is_locked') and current_user.is_locked:
        logger.warning(f"Access denied for locked user: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is locked"
        )
    
    return current_user


def optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    Useful for endpoints that work with or without authentication.
    
    **Usage:**
    ```python
    @router.get("/public-or-private")
    def mixed_route(user: Optional[User] = Depends(optional_user)):
        if user:
            return {"message": f"Hello {user.username}"}
        return {"message": "Hello anonymous user"}
    ```
    
    Args:
        token: Optional JWT access token
        db: Database session
        
    Returns:
        Optional[User]: User object if authenticated, None otherwise
    """
    if not token:
        return None
    
    try:
        return get_current_user(token, db)
    except HTTPException:
        return None


# -------------------------
# Role-Based Access Control
# -------------------------

def require_roles(allowed_roles: List[str]) -> Callable:
    """
    Dependency factory to require one of the allowed roles.
    
    **Args:**
    - `allowed_roles`: List of role names that are allowed
    
    **Usage:**
    ```python
    @router.get("/admin-only")
    def admin_route(user: User = Depends(require_roles(["admin"]))):
        return {"message": "Admin access granted"}
    
    @router.get("/admin-or-manager")
    def manager_route(user: User = Depends(require_roles(["admin", "manager"]))):
        return {"message": "Access granted"}
    ```
    
    Args:
        allowed_roles: List of allowed role names
        
    Returns:
        Callable: Dependency function that checks user role
        
    Raises:
        HTTPException: 403 if user doesn't have required role
    """
    def _require_roles(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            logger.warning(
                f"Access denied for user {current_user.username} "
                f"(role: {current_user.role}, required: {allowed_roles})"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient privileges. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return _require_roles


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Shortcut dependency to require admin role.
    
    **Usage:**
    ```python
    @router.delete("/users/{user_id}")
    def delete_user(
        user_id: int,
        admin: User = Depends(require_admin)
    ):
        # Only admins can delete users
        pass
    ```
    
    Args:
        current_user: Authenticated active user
        
    Returns:
        User: Admin user object
        
    Raises:
        HTTPException: 403 if user is not an admin
    """
    if current_user.role != "admin":
        logger.warning(f"Admin access denied for user: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required"
        )
    return current_user


def require_manager(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Shortcut dependency to require manager or admin role.
    
    **Usage:**
    ```python
    @router.post("/projects")
    def create_project(
        project_data: ProjectCreate,
        manager: User = Depends(require_manager)
    ):
        # Only managers and admins can create projects
        pass
    ```
    
    Args:
        current_user: Authenticated active user
        
    Returns:
        User: Manager or admin user object
        
    Raises:
        HTTPException: 403 if user is not a manager or admin
    """
    if current_user.role not in ["admin", "manager"]:
        logger.warning(f"Manager access denied for user: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or administrator privileges required"
        )
    return current_user


def require_staff(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Shortcut dependency to require staff, manager, or admin role.
    
    **Usage:**
    ```python
    @router.get("/reports")
    def get_reports(
        staff: User = Depends(require_staff)
    ):
        # Staff, managers, and admins can view reports
        pass
    ```
    
    Args:
        current_user: Authenticated active user
        
    Returns:
        User: Staff, manager, or admin user object
        
    Raises:
        HTTPException: 403 if user doesn't have staff privileges
    """
    if current_user.role not in ["admin", "manager", "staff"]:
        logger.warning(f"Staff access denied for user: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff privileges required"
        )
    return current_user


# -------------------------
# Permission Checking Utilities
# -------------------------

def can_modify_user(current_user: User, target_user: User) -> bool:
    """
    Check if current user can modify target user.
    
    Rules:
    - Admins can modify anyone
    - Managers can modify staff and users
    - Users can only modify themselves
    
    Args:
        current_user: User attempting the modification
        target_user: User being modified
        
    Returns:
        bool: True if modification is allowed
    """
    # Admins can modify anyone
    if current_user.role == "admin":
        return True
    
    # Managers can modify non-admin users
    if current_user.role == "manager" and target_user.role not in ["admin", "manager"]:
        return True
    
    # Users can only modify themselves
    if current_user.id == target_user.id:
        return True
    
    return False


def can_delete_user(current_user: User, target_user: User) -> bool:
    """
    Check if current user can delete target user.
    
    Rules:
    - Only admins can delete users
    - Cannot delete yourself
    
    Args:
        current_user: User attempting the deletion
        target_user: User being deleted
        
    Returns:
        bool: True if deletion is allowed
    """
    # Only admins can delete
    if current_user.role != "admin":
        return False
    
    # Cannot delete yourself
    if current_user.id == target_user.id:
        return False
    
    return True


def check_resource_access(
    current_user: User,
    resource_owner_id: int,
    require_ownership: bool = False
) -> bool:
    """
    Check if user can access a resource.
    
    Args:
        current_user: User attempting access
        resource_owner_id: ID of the resource owner
        require_ownership: If True, only owner or admin can access
        
    Returns:
        bool: True if access is allowed
    """
    # Admins can access everything
    if current_user.role == "admin":
        return True
    
    # If ownership is required, only owner and admin can access
    if require_ownership:
        return current_user.id == resource_owner_id
    
    # Managers can access most resources
    if current_user.role in ["manager", "staff"]:
        return True
    
    # Regular users can only access their own resources
    return current_user.id == resource_owner_id


# -------------------------
# Example Usage in Routes
# -------------------------

"""
Example usage in your route files:

from backend.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    require_admin,
    require_manager,
    require_staff,
    require_roles,
    optional_user
)

# Basic authentication
@router.get("/profile")
def get_profile(user: User = Depends(get_current_active_user)):
    return {"username": user.username, "role": user.role}

# Admin only
@router.delete("/users/{user_id}")
def delete_user(user_id: int, admin: User = Depends(require_admin)):
    # Delete user logic
    pass

# Manager or Admin
@router.post("/projects")
def create_project(data: dict, user: User = Depends(require_manager)):
    # Create project logic
    pass

# Multiple roles
@router.get("/reports")
def get_reports(user: User = Depends(require_roles(["admin", "manager", "staff"]))):
    # Get reports logic
    pass

# Optional authentication
@router.get("/public-data")
def get_public_data(user: Optional[User] = Depends(optional_user)):
    if user:
        # Return personalized data
        pass
    # Return public data
    pass
"""