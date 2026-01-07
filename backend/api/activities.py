from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from spms_db.backend.dependencies import get_db, get_current_user, require_admin
from spms_db.backend.schemas.activities import ActivityCreate, ActivityOut, ActivityUpdate
from spms_db.backend import models

router = APIRouter(prefix="/api/activities", tags=["activities"])

@router.post("", response_model=ActivityOut, status_code=201)
def create_activity(payload: ActivityCreate, db: Session = Depends(get_db), current=Depends(require_admin)):
    a = models.Activity(**payload.dict())
    db.add(a); db.commit(); db.refresh(a)
    return a

@router.get("", response_model=list[ActivityOut])
def list_activities(response: Response, skip: int = 0, limit: int = 25, db: Session = Depends(get_db), current=Depends(get_current_user)):
    q = db.query(models.Activity)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    response.headers["X-Total-Count"] = str(total)
    return items

@router.get("/{activity_id}", response_model=ActivityOut)
def get_activity(activity_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    a = db.get(models.Activity, activity_id)
    if not a:
        raise HTTPException(status_code=404, detail="Activity not found")
    return a

@router.put("/{activity_id}", response_model=ActivityOut)
def update_activity(activity_id: int, payload: ActivityUpdate, db: Session = Depends(get_db), current=Depends(require_admin)):
    a = db.get(models.Activity, activity_id)
    if not a:
        raise HTTPException(status_code=404, detail="Activity not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(a, k, v)
    db.add(a); db.commit(); db.refresh(a)
    return a
