from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from spms_db.backend.dependencies import get_db, get_current_user, require_admin
from spms_db.backend.schemas.projects import ProjectCreate, ProjectOut, ProjectUpdate
from spms_db.backend import models

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), current=Depends(require_admin)):
    proj = models.Project(**payload.dict())
    db.add(proj); db.commit(); db.refresh(proj)
    return proj

@router.get("", response_model=list[ProjectOut])
def list_projects(response: Response, skip: int = 0, limit: int = 25, db: Session = Depends(get_db), current=Depends(get_current_user)):
    q = db.query(models.Project)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    response.headers["X-Total-Count"] = str(total)
    return items

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    proj = db.get(models.Project, project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db), current=Depends(require_admin)):
    proj = db.get(models.Project, project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(proj, k, v)
    db.add(proj); db.commit(); db.refresh(proj)
    return proj
