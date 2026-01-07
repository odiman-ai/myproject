# spms_db/backend/projects/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Project, Programme, Activity
from auth.routes import get_current_user

router = APIRouter()

@router.post("/")
def create_project(
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Create a new project"""
    # Validate required fields
    if not payload.get("name"):
        raise HTTPException(status_code=400, detail="Project name is required")
    
    # Verify programme if provided
    if payload.get("programme_id"):
        programme = db.query(Programme).filter(Programme.id == payload["programme_id"]).first()
        if not programme:
            raise HTTPException(status_code=404, detail="Programme not found")
    
    project = Project(**payload)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("/")
def list_projects(
    name: Optional[str] = None,
    programme_id: Optional[int] = None,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all projects with optional filters"""
    query = db.query(Project)
    
    if name:
        query = query.filter(Project.name.ilike(f"%{name}%"))
    if programme_id:
        query = query.filter(Project.programme_id == programme_id)
    
    return query.all()

@router.get("/{project_id}")
def get_project(
    project_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get a specific project by ID"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/{project_id}/activities")
def get_project_activities(
    project_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all activities under a specific project"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    activities = db.query(Activity).filter(Activity.project_id == project_id).all()
    return activities

@router.get("/{project_id}/summary")
def get_project_summary(
    project_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get project summary with activity count and programme info"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    activities = db.query(Activity).filter(Activity.project_id == project_id).all()
    programme = None
    
    if project.programme_id:
        programme = db.query(Programme).filter(Programme.id == project.programme_id).first()
    
    return {
        "project": project,
        "programme": {
            "id": programme.id,
            "name": programme.name
        } if programme else None,
        "total_activities": len(activities),
        "activities": [
            {
                "id": act.id,
                "name": act.name,
                "start_date": act.start_date,
                "end_date": act.end_date
            }
            for act in activities
        ]
    }

@router.put("/{project_id}")
def update_project(
    project_id: int,
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Update a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify programme if being changed
    if payload.get("programme_id"):
        programme = db.query(Programme).filter(Programme.id == payload["programme_id"]).first()
        if not programme:
            raise HTTPException(status_code=404, detail="Programme not found")
    
    # Update fields
    for key, value in payload.items():
        if hasattr(project, key):
            setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Delete a project"""
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if project has activities
    activity_count = db.query(Activity).filter(Activity.project_id == project_id).count()
    if activity_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete project with {activity_count} activities. Delete activities first."
        )
    
    db.delete(project)
    db.commit()
    return {"detail": "Project deleted successfully"}