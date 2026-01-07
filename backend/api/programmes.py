from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from spms_db.backend.dependencies import get_db, get_current_user, require_admin
from spms_db.backend.schemas.programmes import ProgrammeCreate, ProgrammeOut, ProgrammeUpdate
from spms_db.backend import models

router = APIRouter(prefix="/api/programmes", tags=["programmes"])

@router.post("", response_model=ProgrammeOut, status_code=201)
def create_programme(payload: ProgrammeCreate, db: Session = Depends(get_db), current=Depends(require_admin)):
    p = models.Programme(**payload.dict())
    db.add(p); db.commit(); db.refresh(p)
    return p

@router.get("", response_model=list[ProgrammeOut])
def list_programmes(response: Response, skip: int = 0, limit: int = 25, db: Session = Depends(get_db), current=Depends(get_current_user)):
    q = db.query(models.Programme)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    response.headers["X-Total-Count"] = str(total)
    return items

@router.get("/{programme_id}", response_model=ProgrammeOut)
def get_programme(programme_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    p = db.get(models.Programme, programme_id)
    if not p:
        raise HTTPException(status_code=404, detail="Programme not found")
    return p

@router.put("/{programme_id}", response_model=ProgrammeOut)
def update_programme(programme_id: int, payload: ProgrammeUpdate, db: Session = Depends(get_db), current=Depends(require_admin)):
    p = db.get(models.Programme, programme_id)
    if not p:
        raise HTTPException(status_code=404, detail="Programme not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(p, k, v)
    db.add(p); db.commit(); db.refresh(p)
    return p
