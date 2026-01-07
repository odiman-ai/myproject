# spms_db/backend/cases/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from database import get_db
from models import Case, CaseNote, HouseholdMember, Project
from auth.routes import get_current_user

router = APIRouter()

@router.post("/")
def create_case(
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Create a new case"""
    # Validate required fields
    if not payload.get("case_number"):
        raise HTTPException(status_code=400, detail="Case number is required")
    if not payload.get("member_id"):
        raise HTTPException(status_code=400, detail="Member ID is required")
    
    # Check if case number already exists
    existing = db.query(Case).filter(Case.case_number == payload["case_number"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Case number already exists")
    
    # Verify member exists
    member = db.query(HouseholdMember).filter(HouseholdMember.id == payload["member_id"]).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Verify project if provided
    if payload.get("project_id"):
        project = db.query(Project).filter(Project.id == payload["project_id"]).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    
    # Create case
    case = Case(**payload)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case

@router.post("/note")
def add_case_note(
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Add a note to a case"""
    if not payload.get("case_id"):
        raise HTTPException(status_code=400, detail="Case ID is required")
    if not payload.get("note"):
        raise HTTPException(status_code=400, detail="Note content is required")
    
    # Verify case exists
    case = db.query(Case).filter(Case.id == payload["case_id"]).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Add created_by from current user
    payload["created_by"] = current.id
    
    note = CaseNote(**payload)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.get("/")
def list_cases(
    status: Optional[str] = None,
    member_id: Optional[int] = None,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all cases with optional filters"""
    query = db.query(Case)
    
    if status:
        query = query.filter(Case.status == status)
    if member_id:
        query = query.filter(Case.member_id == member_id)
    if project_id:
        query = query.filter(Case.project_id == project_id)
    
    return query.all()

@router.get("/{case_id}")
def get_case(
    case_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get a specific case by ID"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.get("/{case_id}/notes")
def get_case_notes(
    case_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all notes for a specific case"""
    # Verify case exists
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    notes = db.query(CaseNote).filter(CaseNote.case_id == case_id).all()
    return notes

@router.get("/member/{member_id}")
def get_member_cases(
    member_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all cases for a specific member"""
    # Verify member exists
    member = db.query(HouseholdMember).filter(HouseholdMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    cases = db.query(Case).filter(Case.member_id == member_id).all()
    return cases

@router.put("/{case_id}")
def update_case(
    case_id: int,
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Update a case"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Update fields
    for key, value in payload.items():
        if hasattr(case, key):
            setattr(case, key, value)
    
    db.commit()
    db.refresh(case)
    return case

@router.put("/{case_id}/close")
def close_case(
    case_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Close a case"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case.status = "closed"
    case.closed_at = datetime.utcnow()
    db.commit()
    db.refresh(case)
    return case

@router.delete("/{case_id}")
def delete_case(
    case_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Delete a case"""
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    db.delete(case)
    db.commit()
    return {"detail": "Case deleted successfully"}