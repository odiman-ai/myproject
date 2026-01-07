# spms_db/backend/core/api_key_routes.py
import logging
from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import APIKey, User
from backend.dependencies import require_admin, get_current_active_user
from backend.auth.service import create_api_key
from backend.schemas.schemas import APIKeyResponse, APIKeyCreateRequest, MessageResponse

# Logger
logger = logging.getLogger("spms_api_key")

# Router
router = APIRouter(prefix="/api/v1/api-keys", tags=["API Keys"])


@router.post("/", response_model=APIKeyResponse, summary="Create API Key (Admin Only)")
def create_key(
    data: APIKeyCreateRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new API key for integrations or services.
    Returns the key once (hashed in DB).
    """
    key_value, key_hash = create_api_key()
    
    api_key = APIKey(
        name=data.name,
        hashed_key=key_hash,
        owner_id=admin.id,
        scopes=",".join(data.scopes),
        created_at=datetime.utcnow(),
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    logger.info(f"API key created by admin {admin.username}: {data.name}")
    
    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        key=key_value,  # Return plain key once
        scopes=data.scopes,
        created_at=api_key.created_at
    )


@router.get("/", response_model=List[APIKeyResponse], summary="List API Keys (Admin Only)")
def list_keys(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all API keys. Only admin can see the keys metadata (not the plain key).
    """
    keys = db.query(APIKey).all()
    
    return [
        APIKeyResponse(
            id=k.id,
            name=k.name,
            key=None,  # Do NOT return plain key
            scopes=k.scopes.split(",") if k.scopes else [],
            created_at=k.created_at
        )
        for k in keys
    ]


@router.delete("/{api_key_id}", response_model=MessageResponse, summary="Revoke API Key (Admin Only)")
def revoke_key(
    api_key_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Revoke/delete an API key by ID.
    """
    key = db.query(APIKey).filter(APIKey.id == api_key_id).first()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    db.delete(key)
    db.commit()
    
    logger.info(f"API key revoked by admin {admin.username}: {key.name}")
    
    return MessageResponse(
        message="API key revoked successfully",
        detail=f"API key '{key.name}' has been deleted."
    )


@router.get("/me", response_model=List[APIKeyResponse], summary="List My API Keys")
def list_my_keys(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List API keys created by the currently authenticated user.
    """
    keys = db.query(APIKey).filter(APIKey.owner_id == current_user.id).all()
    
    return [
        APIKeyResponse(
            id=k.id,
            name=k.name,
            key=None,  # Do not expose plain key
            scopes=k.scopes.split(",") if k.scopes else [],
            created_at=k.created_at
        )
        for k in keys
    ]
