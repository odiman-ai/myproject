# spms_db/backend/me/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from database import get_db
from models import MEIndicator, Project
from auth.routes import get_current_user

router = APIRouter()

@router.post("/indicator")
def create_indicator(
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Create a new M&E indicator"""
    # Validate required fields
    if not payload.get("name"):
        raise HTTPException(status_code=400, detail="Indicator name is required")
    if not payload.get("project_id"):
        raise HTTPException(status_code=400, detail="Project ID is required")
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == payload["project_id"]).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    indicator = MEIndicator(**payload)
    db.add(indicator)
    db.commit()
    db.refresh(indicator)
    return indicator

@router.get("/indicator")
def list_indicators(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all M&E indicators with optional project filter"""
    query = db.query(MEIndicator)
    
    if project_id:
        query = query.filter(MEIndicator.project_id == project_id)
    
    return query.all()

@router.get("/indicator/{indicator_id}")
def get_indicator(
    indicator_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get a specific indicator by ID"""
    indicator = db.query(MEIndicator).filter(MEIndicator.id == indicator_id).first()
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return indicator

@router.get("/project/{project_id}")
def get_project_indicators(
    project_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all indicators for a specific project"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    indicators = db.query(MEIndicator).filter(MEIndicator.project_id == project_id).all()
    return indicators

@router.get("/project/{project_id}/progress")
def get_project_progress(
    project_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get project progress summary based on indicators"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    indicators = db.query(MEIndicator).filter(MEIndicator.project_id == project_id).all()
    
    if not indicators:
        return {
            "project_id": project_id,
            "project_name": project.name,
            "total_indicators": 0,
            "overall_progress": 0
        }
    
    # Calculate overall progress
    total_progress = 0
    indicators_with_targets = 0
    
    for indicator in indicators:
        if indicator.target_value and indicator.target_value > 0:
            current_val = indicator.current_value or Decimal(0)
            progress = (current_val / indicator.target_value) * 100
            total_progress += float(progress)
            indicators_with_targets += 1
    
    overall_progress = total_progress / indicators_with_targets if indicators_with_targets > 0 else 0
    
    return {
        "project_id": project_id,
        "project_name": project.name,
        "total_indicators": len(indicators),
        "indicators_with_targets": indicators_with_targets,
        "overall_progress": round(overall_progress, 2),
        "indicators": [
            {
                "id": ind.id,
                "name": ind.name,
                "current_value": float(ind.current_value) if ind.current_value else 0,
                "target_value": float(ind.target_value) if ind.target_value else 0,
                "unit": ind.unit,
                "progress": round((float(ind.current_value or 0) / float(ind.target_value) * 100), 2) if ind.target_value and ind.target_value > 0 else 0
            }
            for ind in indicators
        ]
    }

@router.put("/indicator/{indicator_id}")
def update_indicator(
    indicator_id: int,
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Update an indicator"""
    indicator = db.query(MEIndicator).filter(MEIndicator.id == indicator_id).first()
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")
    
    # Update fields
    for key, value in payload.items():
        if hasattr(indicator, key):
            setattr(indicator, key, value)
    
    db.commit()
    db.refresh(indicator)
    return indicator

@router.put("/indicator/{indicator_id}/update-value")
def update_indicator_value(
    indicator_id: int,
    current_value: float,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Quick update of indicator current value"""
    indicator = db.query(MEIndicator).filter(MEIndicator.id == indicator_id).first()
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")
    
    indicator.current_value = Decimal(str(current_value))
    db.commit()
    db.refresh(indicator)
    
    # Calculate progress
    progress = 0
    if indicator.target_value and indicator.target_value > 0:
        progress = (float(indicator.current_value) / float(indicator.target_value)) * 100
    
    return {
        "indicator": indicator,
        "progress_percentage": round(progress, 2)
    }

@router.delete("/indicator/{indicator_id}")
def delete_indicator(
    indicator_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Delete an indicator"""
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    indicator = db.query(MEIndicator).filter(MEIndicator.id == indicator_id).first()
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")
    
    db.delete(indicator)
    db.commit()
    return {"detail": "Indicator deleted successfully"}