# spms_db/backend/activities/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from database import get_db
from models import Activity, Project
from auth.routes import get_current_user

router = APIRouter()

@router.post("/")
def create_activity(
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Create a new activity"""
    # Validate required fields
    if not payload.get("name"):
        raise HTTPException(status_code=400, detail="Activity name is required")
    if not payload.get("project_id"):
        raise HTTPException(status_code=400, detail="Project ID is required")
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == payload["project_id"]).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create activity
    activity = Activity(**payload)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity

@router.get("/")
def list_activities(
    name: Optional[str] = None,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all activities with optional filters"""
    query = db.query(Activity)
    
    if name:
        query = query.filter(Activity.name.ilike(f"%{name}%"))
    if project_id:
        query = query.filter(Activity.project_id == project_id)
    
    return query.all()

@router.get("/{activity_id}")
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get a specific activity by ID"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

@router.get("/project/{project_id}")
def get_project_activities(
    project_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all activities for a specific project"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    activities = db.query(Activity).filter(Activity.project_id == project_id).all()
    return activities

@router.put("/{activity_id}")
def update_activity(
    activity_id: int,
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Update an activity"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Update fields
    for key, value in payload.items():
        if hasattr(activity, key):
            setattr(activity, key, value)
    
    db.commit()
    db.refresh(activity)
    return activity

@router.delete("/{activity_id}")
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Delete an activity"""
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    db.delete(activity)
    db.commit()
    return {"detail": "Activity deleted successfully"}