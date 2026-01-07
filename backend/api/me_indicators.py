from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from spms_db.backend.dependencies import get_db, get_current_user, require_admin
from spms_db.backend.schemas.me_indicators import MEIndicatorCreate, MEIndicatorOut, MEIndicatorUpdate
from spms_db.backend import models

router = APIRouter(prefix="/api/me/indicators", tags=["m&e"])

@router.post("", response_model=MEIndicatorOut, status_code=201)
def create_indicator(payload: MEIndicatorCreate, db: Session = Depends(get_db), current=Depends(require_admin)):
    ind = models.MEIndicator(**payload.dict())
    db.add(ind); db.commit(); db.refresh(ind)
    return ind

@router.get("", response_model=list[MEIndicatorOut])
def list_indicators(response: Response, skip: int = 0, limit: int = 25, project_id: int | None = None, db: Session = Depends(get_db), current=Depends(get_current_user)):
    q = db.query(models.MEIndicator)
    if project_id:
        q = q.filter(models.MEIndicator.project_id == project_id)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    response.headers["X-Total-Count"] = str(total)
    return items

@router.put("/{indicator_id}", response_model=MEIndicatorOut)
def update_indicator(indicator_id: int, payload: MEIndicatorUpdate, db: Session = Depends(get_db), current=Depends(require_admin)):
    ind = db.get(models.MEIndicator, indicator_id)
    if not ind:
        raise HTTPException(status_code=404, detail="Indicator not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(ind, k, v)
    db.add(ind); db.commit(); db.refresh(ind)
    return ind
