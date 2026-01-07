from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from spms_db.backend.dependencies import get_db, get_current_user
from spms_db.backend.schemas.households import HouseholdCreate, HouseholdOut, HouseholdUpdate
from spms_db.backend import models

router = APIRouter(prefix="/api/households", tags=["households"])

@router.post("", response_model=HouseholdOut, status_code=201)
def create_household(payload: HouseholdCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    h = models.Household(**payload.dict())
    db.add(h); db.commit(); db.refresh(h)
    return h

@router.get("", response_model=list[HouseholdOut])
def list_households(response: Response, skip: int = 0, limit: int = 25, db: Session = Depends(get_db), current=Depends(get_current_user)):
    q = db.query(models.Household)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    response.headers["X-Total-Count"] = str(total)
    return items

@router.get("/{household_id}", response_model=HouseholdOut)
def get_household(household_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    h = db.get(models.Household, household_id)
    if not h:
        raise HTTPException(status_code=404, detail="Household not found")
    return h

@router.put("/{household_id}", response_model=HouseholdOut)
def update_household(household_id: int, payload: HouseholdUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    h = db.get(models.Household, household_id)
    if not h:
        raise HTTPException(status_code=404, detail="Household not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(h, k, v)
    db.add(h); db.commit(); db.refresh(h)
    return h
