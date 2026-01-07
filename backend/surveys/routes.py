# spms_db/backend/surveys/routes.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import csv
import io
import json
from database import get_db
from models import Survey, SurveyResponse, Project, HouseholdMember
from auth.routes import get_current_user

router = APIRouter()

# Create survey
@router.post("/")
def create_survey(
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Create a new survey"""
    # Validate required fields
    if not payload.get("title"):
        raise HTTPException(status_code=400, detail="Survey title is required")
    if not payload.get("project_id"):
        raise HTTPException(status_code=400, detail="Project ID is required")
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == payload["project_id"]).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Add creator
    payload["created_by"] = current.id
    
    survey = Survey(**payload)
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return survey

# List surveys
@router.get("/")
def list_surveys(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all surveys with optional project filter"""
    query = db.query(Survey)
    
    if project_id:
        query = query.filter(Survey.project_id == project_id)
    
    return query.all()

# Get survey
@router.get("/{survey_id}")
def get_survey(
    survey_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get a specific survey by ID"""
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return survey

# Update survey
@router.put("/{survey_id}")
def update_survey(
    survey_id: int,
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Update a survey"""
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    # Update fields
    for key, value in payload.items():
        if hasattr(survey, key):
            setattr(survey, key, value)
    
    db.commit()
    db.refresh(survey)
    return survey

# Delete survey
@router.delete("/{survey_id}")
def delete_survey(
    survey_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Delete a survey"""
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    # Check if survey has responses
    response_count = db.query(SurveyResponse).filter(SurveyResponse.survey_id == survey_id).count()
    if response_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete survey with {response_count} responses. Delete responses first."
        )
    
    db.delete(survey)
    db.commit()
    return {"detail": "Survey deleted successfully"}

# Submit a survey response
@router.post("/response")
def submit_response(
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Submit a survey response"""
    # Validate required fields
    if not payload.get("survey_id"):
        raise HTTPException(status_code=400, detail="Survey ID is required")
    if not payload.get("member_id"):
        raise HTTPException(status_code=400, detail="Member ID is required")
    if not payload.get("response"):
        raise HTTPException(status_code=400, detail="Response is required")
    
    # Verify survey exists
    survey = db.query(Survey).filter(Survey.id == payload["survey_id"]).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    # Verify member exists
    member = db.query(HouseholdMember).filter(HouseholdMember.id == payload["member_id"]).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    response = SurveyResponse(**payload)
    db.add(response)
    db.commit()
    db.refresh(response)
    return response

# List responses for a survey
@router.get("/{survey_id}/responses")
def list_survey_responses(
    survey_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all responses for a survey"""
    # Verify survey exists
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    responses = db.query(SurveyResponse).filter(SurveyResponse.survey_id == survey_id).all()
    
    # Enrich with member names
    result = []
    for resp in responses:
        member = db.query(HouseholdMember).filter(HouseholdMember.id == resp.member_id).first()
        result.append({
            "id": resp.id,
            "survey_id": resp.survey_id,
            "member_id": resp.member_id,
            "member_name": member.name if member else "Unknown",
            "response": resp.response,
            "submitted_at": resp.submitted_at
        })
    
    return result

# Get survey summary
@router.get("/{survey_id}/summary")
def get_survey_summary(
    survey_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get survey summary with response count"""
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    response_count = db.query(SurveyResponse).filter(SurveyResponse.survey_id == survey_id).count()
    
    return {
        "survey": survey,
        "response_count": response_count
    }

# Export responses to CSV or JSON
@router.get("/{survey_id}/responses/export")
def export_survey_responses(
    survey_id: int,
    format: str = "csv",
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Export survey responses"""
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")

    responses = db.query(SurveyResponse).filter(SurveyResponse.survey_id == survey_id).all()

    # JSON export
    if format.lower() == "json":
        data = []
        for resp in responses:
            member = db.query(HouseholdMember).filter(HouseholdMember.id == resp.member_id).first()
            data.append({
                "id": resp.id,
                "member_id": resp.member_id,
                "member_name": member.name if member else "Unknown",
                "response": resp.response,
                "submitted_at": resp.submitted_at.isoformat() if resp.submitted_at else None
            })
        return JSONResponse(content={
            "survey": {"id": survey.id, "title": survey.title},
            "response_count": len(responses),
            "responses": data
        })

    # CSV export
    if format.lower() == "csv":
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        
        # Header
        writer.writerow(["response_id", "member_id", "member_name", "response", "submitted_at"])
        
        for resp in responses:
            member = db.query(HouseholdMember).filter(HouseholdMember.id == resp.member_id).first()
            writer.writerow([
                resp.id,
                resp.member_id,
                member.name if member else "Unknown",
                resp.response,
                resp.submitted_at.isoformat() if resp.submitted_at else ""
            ])

        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=survey_{survey_id}_responses.csv"}
        )

    raise HTTPException(status_code=400, detail="Unsupported format. Use csv or json.")