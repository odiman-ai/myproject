# spms_db/backend/programmes/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Programme, Project
from auth.routes import get_current_user

router = APIRouter()

@router.post("/")
def create_programme(
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Create a new programme"""
    # Validate required fields
    if not payload.get("name"):
        raise HTTPException(status_code=400, detail="Programme name is required")
    
    # Check if name already exists
    existing = db.query(Programme).filter(Programme.name == payload["name"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Programme name already exists")
    
    programme = Programme(**payload)
    db.add(programme)
    db.commit()
    db.refresh(programme)
    return programme

@router.get("/")
def list_programmes(
    name: Optional[str] = None,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all programmes with optional name filter"""
    query = db.query(Programme)
    
    if name:
        query = query.filter(Programme.name.ilike(f"%{name}%"))
    
    return query.all()

@router.get("/{programme_id}")
def get_programme(
    programme_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get a specific programme by ID"""
    programme = db.query(Programme).filter(Programme.id == programme_id).first()
    if not programme:
        raise HTTPException(status_code=404, detail="Programme not found")
    return programme

@router.get("/{programme_id}/projects")
def get_programme_projects(
    programme_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all projects under a specific programme"""
    # Verify programme exists
    programme = db.query(Programme).filter(Programme.id == programme_id).first()
    if not programme:
        raise HTTPException(status_code=404, detail="Programme not found")
    
    projects = db.query(Project).filter(Project.programme_id == programme_id).all()
    return projects

@router.get("/{programme_id}/summary")
def get_programme_summary(
    programme_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get programme summary with project count and details"""
    programme = db.query(Programme).filter(Programme.id == programme_id).first()
    if not programme:
        raise HTTPException(status_code=404, detail="Programme not found")
    
    projects = db.query(Project).filter(Project.programme_id == programme_id).all()
    
    return {
        "programme": programme,
        "total_projects": len(projects),
        "projects": [
            {
                "id": proj.id,
                "name": proj.name,
                "start_date": proj.start_date,
                "end_date": proj.end_date
            }
            for proj in projects
        ]
    }

@router.put("/{programme_id}")
def update_programme(
    programme_id: int,
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Update a programme"""
    programme = db.query(Programme).filter(Programme.id == programme_id).first()
    if not programme:
        raise HTTPException(status_code=404, detail="Programme not found")
    
    # Check if name is being changed and already exists
    if payload.get("name") and payload["name"] != programme.name:
        existing = db.query(Programme).filter(Programme.name == payload["name"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Programme name already exists")
    
    # Update fields
    for key, value in payload.items():
        if hasattr(programme, key):
            setattr(programme, key, value)
    
    db.commit()
    db.refresh(programme)
    return programme

@router.delete("/{programme_id}")
def delete_programme(
    programme_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Delete a programme"""
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    programme = db.query(Programme).filter(Programme.id == programme_id).first()
    if not programme:
        raise HTTPException(status_code=404, detail="Programme not found")
    
    # Check if programme has projects
    project_count = db.query(Project).filter(Project.programme_id == programme_id).count()
    if project_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete programme with {project_count} projects. Delete projects first."
        )
    
    db.delete(programme)
    db.commit()
    return {"detail": "Programme deleted successfully"}