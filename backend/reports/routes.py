# spms_db/backend/reports/routes.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import csv
import io
from database import get_db
from models import Report, Household, HouseholdMember, Activity, Attendance, Project
from auth.routes import get_current_user

router = APIRouter()

@router.post("/")
def create_report(
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Create a new report"""
    # Add current user as generator
    payload["generated_by"] = current.id
    
    report = Report(**payload)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.get("/")
def list_reports(
    related_module: Optional[str] = None,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all reports with optional module filter"""
    query = db.query(Report)
    
    if related_module:
        query = query.filter(Report.related_module == related_module)
    
    return query.all()

@router.get("/{report_id}")
def get_report(
    report_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get a specific report by ID"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.get("/generate/households")
def generate_households_report(
    format: str = "json",
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Generate households report"""
    households = db.query(Household).all()
    
    data = []
    for hh in households:
        member_count = db.query(HouseholdMember).filter(HouseholdMember.household_id == hh.id).count()
        data.append({
            "id": hh.id,
            "cluster_name": hh.cluster_name,
            "community": hh.community,
            "village": hh.village,
            "member_count": member_count,
            "highly_vulnerable": hh.highly_vulnerable,
            "food_insecure": hh.food_insecure,
            "shelter_insecure": hh.shelter_insecure
        })
    
    if format.lower() == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=data[0].keys() if data else [])
        writer.writeheader()
        writer.writerows(data)
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=households_report_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    
    return {"report_type": "households", "total_count": len(households), "data": data}

@router.get("/generate/members")
def generate_members_report(
    format: str = "json",
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Generate members report"""
    members = db.query(HouseholdMember).all()
    
    data = []
    for member in members:
        data.append({
            "id": member.id,
            "name": member.name,
            "age": member.age,
            "sex": member.sex,
            "household_id": member.household_id,
            "relationship_type": member.relationship_type,
            "status": member.status,
            "is_refugee": member.is_refugee,
            "needs_protection": member.needs_protection
        })
    
    if format.lower() == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=data[0].keys() if data else [])
        writer.writeheader()
        writer.writerows(data)
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=members_report_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    
    return {"report_type": "members", "total_count": len(members), "data": data}

@router.get("/generate/attendance")
def generate_attendance_report(
    activity_id: Optional[int] = None,
    format: str = "json",
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Generate attendance report"""
    query = db.query(Attendance)
    
    if activity_id:
        query = query.filter(Attendance.activity_id == activity_id)
    
    records = query.all()
    
    data = []
    for record in records:
        member = db.query(HouseholdMember).filter(HouseholdMember.id == record.member_id).first()
        activity = db.query(Activity).filter(Activity.id == record.activity_id).first()
        
        data.append({
            "id": record.id,
            "member_name": member.name if member else "Unknown",
            "activity_name": activity.name if activity else "Unknown",
            "status": record.status,
            "timestamp": record.timestamp.isoformat() if record.timestamp else None
        })
    
    if format.lower() == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=data[0].keys() if data else [])
        writer.writeheader()
        writer.writerows(data)
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=attendance_report_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    
    return {"report_type": "attendance", "total_count": len(records), "data": data}

@router.get("/generate/vulnerable")
def generate_vulnerable_report(
    format: str = "json",
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Generate vulnerable populations report"""
    vulnerable_households = db.query(Household).filter(
        (Household.highly_vulnerable == True) |
        (Household.food_insecure == True) |
        (Household.shelter_insecure == True)
    ).all()
    
    vulnerable_members = db.query(HouseholdMember).filter(
        (HouseholdMember.needs_protection == True) |
        (HouseholdMember.orphan == True) |
        (HouseholdMember.needs_medical_attention == True)
    ).all()
    
    data = {
        "vulnerable_households": len(vulnerable_households),
        "vulnerable_members": len(vulnerable_members),
        "households": [
            {
                "id": hh.id,
                "cluster_name": hh.cluster_name,
                "village": hh.village,
                "highly_vulnerable": hh.highly_vulnerable,
                "food_insecure": hh.food_insecure,
                "shelter_insecure": hh.shelter_insecure
            }
            for hh in vulnerable_households
        ],
        "members": [
            {
                "id": m.id,
                "name": m.name,
                "needs_protection": m.needs_protection,
                "orphan": m.orphan,
                "needs_medical_attention": m.needs_medical_attention
            }
            for m in vulnerable_members
        ]
    }
    
    return data

@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Delete a report"""
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db.delete(report)
    db.commit()
    return {"detail": "Report deleted successfully"}