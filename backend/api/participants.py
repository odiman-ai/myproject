from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session
from spms_db.backend.dependencies import get_db, get_current_user
from spms_db.backend.schemas.participants import ParticipantCreate, ParticipantOut, ParticipantUpdate
from spms_db.backend import models

router = APIRouter(prefix="/api/participants", tags=["participants"])

@router.post("", response_model=ParticipantOut, status_code=201)
def create_participant(payload: ParticipantCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    data = payload.dict(by_alias=True)
    p = models.HouseholdMember(**data)
    db.add(p); db.commit(); db.refresh(p)
    return p

@router.get("", response_model=list[ParticipantOut])
def list_participants(response: Response, skip: int = 0, limit: int = 25, q: str | None = Query(None), db: Session = Depends(get_db), current=Depends(get_current_user)):
    query = db.query(models.HouseholdMember)
    if q:
        query = query.filter(models.HouseholdMember.name.ilike(f"%{q}%"))
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    response.headers["X-Total-Count"] = str(total)
    return items

@router.get("/{participant_id}", response_model=ParticipantOut)
def get_participant(participant_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    p = db.get(models.HouseholdMember, participant_id)
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")
    return p

@router.put("/{participant_id}", response_model=ParticipantOut)
def update_participant(participant_id: int, payload: ParticipantUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    p = db.get(models.HouseholdMember, participant_id)
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")
    for k, v in payload.dict(by_alias=True, exclude_unset=True).items():
        setattr(p, k, v)
    db.add(p); db.commit(); db.refresh(p)
    return p
