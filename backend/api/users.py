from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from spms_db.backend.dependencies import get_db, get_current_user, require_admin
from spms_db.backend.schemas.users import UserCreate, UserOut, UserUpdate
from spms_db.backend.auth_utils import hash_password
from spms_db.backend import models

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current=Depends(require_admin)):
    user = models.User(
        username=payload.username,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        role=payload.role,
        status=payload.status,
        password_hash=hash_password(payload.password),
    )
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.get("", response_model=list[UserOut])
def list_users(response: Response, skip: int = 0, limit: int = 25, db: Session = Depends(get_db), current=Depends(get_current_user)):
    q = db.query(models.User)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    response.headers["X-Total-Count"] = str(total)
    return items

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), current=Depends(require_admin)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(user, k, v)
    db.add(user); db.commit(); db.refresh(user)
    return user
