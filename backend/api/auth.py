from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from spms_db.backend.dependencies import get_db
from spms_db.backend.schemas.auth import LoginRequest, Token
from spms_db.backend.schemas.users import UserCreate
from spms_db.backend.auth_utils import verify_password, hash_password, create_access_token
from spms_db.backend import models

# Updated: Added /v1 to prefix for API versioning
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=dict, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Endpoint: POST /api/v1/auth/register
    """
    if db.query(models.User).filter(models.User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user = models.User(
        username=payload.username,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        role=payload.role,
        status=payload.status,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"id": user.id, "username": user.username}

@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.
    
    Endpoint: POST /api/v1/auth/login
    """
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    
    token = create_access_token(subject=user.id)
    
    return {"access_token": token, "token_type": "bearer"}