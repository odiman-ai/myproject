import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.database import get_db
from backend.models import User
from backend.schemas.schemas import UserListResponse
from backend.auth.dependencies import require_admin

logger = logging.getLogger("spms_users_routes")

router = APIRouter(prefix="/api/v1/users", tags=["Users"])

@router.get("/", response_model=UserListResponse, summary="List all users (Admin Only)")
def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    search: str = Query("", description="Search by username or email"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    Paginated list of all users, with optional search filter.
    Admin only.
    """
    try:
        query = db.query(User)

        # Apply search filter if provided
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        users = query.offset(skip).limit(limit).all()

        return UserListResponse(
            users=users,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit,
            total_pages=(total + limit - 1) // limit,
        )
    except Exception as exc:
        logger.error(f"Error listing users: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error retrieving users")
