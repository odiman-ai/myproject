# spms_db/backend/attendance/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Attendance, Activity, HouseholdMember
from auth.routes import get_current_user

router = APIRouter()

@router.post("/checkin")
def check_in(
    member_id: int, 
    activity_id: int, 
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Check in a member to an activity"""
    # Verify member exists
    member = db.query(HouseholdMember).filter(HouseholdMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Verify activity exists
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Create check-in record
    record = Attendance(
        member_id=member_id, 
        activity_id=activity_id, 
        status="IN"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {
        "id": record.id,
        "member_id": member_id,
        "member_name": member.name,
        "activity_id": activity_id,
        "status": "IN",
        "timestamp": record.timestamp
    }

@router.post("/checkout")
def check_out(
    member_id: int, 
    activity_id: int, 
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Check out a member from an activity"""
    # Verify member exists
    member = db.query(HouseholdMember).filter(HouseholdMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Verify activity exists
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Create check-out record
    record = Attendance(
        member_id=member_id, 
        activity_id=activity_id, 
        status="OUT"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {
        "id": record.id,
        "member_id": member_id,
        "member_name": member.name,
        "activity_id": activity_id,
        "status": "OUT",
        "timestamp": record.timestamp
    }

@router.get("/activity/{activity_id}")
def get_activity_attendance(
    activity_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all attendance records for a specific activity"""
    query = db.query(Attendance).filter(Attendance.activity_id == activity_id)
    
    if status:
        query = query.filter(Attendance.status == status)
    
    records = query.all()
    return records

@router.get("/member/{member_id}")
def get_member_attendance(
    member_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all attendance records for a specific member"""
    records = db.query(Attendance).filter(Attendance.member_id == member_id).all()
    return records

@router.get("/")
def list_attendance(
    activity_id: Optional[int] = None,
    member_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all attendance records with optional filters"""
    query = db.query(Attendance)
    
    if activity_id:
        query = query.filter(Attendance.activity_id == activity_id)
    if member_id:
        query = query.filter(Attendance.member_id == member_id)
    if status:
        query = query.filter(Attendance.status == status)
    
    return query.all()

@router.delete("/{attendance_id}")
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Delete an attendance record"""
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    db.delete(record)
    db.commit()
    return {"detail": "Attendance record deleted successfully"}