# spms_db/backend/members/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import HouseholdMember, Household
from auth.routes import get_current_user

router = APIRouter()

@router.post("/")
def create_member(
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Create a new household member"""
    # Validate required fields
    if not payload.get("household_id"):
        raise HTTPException(status_code=400, detail="Household ID is required")
    if not payload.get("name"):
        raise HTTPException(status_code=400, detail="Member name is required")
    if not payload.get("sex"):
        raise HTTPException(status_code=400, detail="Sex is required")
    if not payload.get("relationship_type"):
        raise HTTPException(status_code=400, detail="Relationship type is required")
    if not payload.get("marital_status"):
        raise HTTPException(status_code=400, detail="Marital status is required")
    
    # Verify household exists
    household = db.query(Household).filter(Household.id == payload["household_id"]).first()
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    
    member = HouseholdMember(**payload)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

@router.get("/")
def list_members(
    household_id: Optional[int] = None,
    name: Optional[str] = None,
    sex: Optional[str] = None,
    relationship_type: Optional[str] = None,
    status: Optional[str] = None,
    is_refugee: Optional[bool] = None,
    needs_protection: Optional[bool] = None,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all members with optional filters"""
    query = db.query(HouseholdMember)
    
    if household_id:
        query = query.filter(HouseholdMember.household_id == household_id)
    if name:
        query = query.filter(HouseholdMember.name.ilike(f"%{name}%"))
    if sex:
        query = query.filter(HouseholdMember.sex == sex)
    if relationship_type:
        query = query.filter(HouseholdMember.relationship_type == relationship_type)
    if status:
        query = query.filter(HouseholdMember.status == status)
    if is_refugee is not None:
        query = query.filter(HouseholdMember.is_refugee == is_refugee)
    if needs_protection is not None:
        query = query.filter(HouseholdMember.needs_protection == needs_protection)
    
    return query.all()

@router.get("/household/{household_id}")
def get_household_members(
    household_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all members of a specific household"""
    # Verify household exists
    household = db.query(Household).filter(Household.id == household_id).first()
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    
    members = db.query(HouseholdMember).filter(HouseholdMember.household_id == household_id).all()
    return members

@router.get("/{member_id}")
def get_member(
    member_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get a specific member by ID"""
    member = db.query(HouseholdMember).filter(HouseholdMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member

@router.get("/vulnerable")
def get_vulnerable_members(
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all vulnerable members"""
    members = db.query(HouseholdMember).filter(
        (HouseholdMember.needs_protection == True) |
        (HouseholdMember.orphan == True) |
        (HouseholdMember.unaccompanied_by_adult == True) |
        (HouseholdMember.needs_medical_attention == True) |
        (HouseholdMember.malnourished == True)
    ).all()
    return members

@router.get("/children")
def get_children(
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all children (age < 18)"""
    members = db.query(HouseholdMember).filter(HouseholdMember.age < 18).all()
    return members

@router.get("/displacement")
def get_displaced_members(
    displacement_type: Optional[str] = None,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get displaced members (refugees, IDPs, returnees, migrants)"""
    query = db.query(HouseholdMember)
    
    if displacement_type == "refugee":
        query = query.filter(HouseholdMember.is_refugee == True)
    elif displacement_type == "idp":
        query = query.filter(HouseholdMember.is_idp == True)
    elif displacement_type == "returnee":
        query = query.filter(HouseholdMember.is_returnee == True)
    elif displacement_type == "migrant":
        query = query.filter(HouseholdMember.is_migrant == True)
    else:
        # Return all displaced
        query = query.filter(
            (HouseholdMember.is_refugee == True) |
            (HouseholdMember.is_idp == True) |
            (HouseholdMember.is_returnee == True) |
            (HouseholdMember.is_migrant == True)
        )
    
    return query.all()

@router.put("/{member_id}")
def update_member(
    member_id: int,
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Update a member"""
    member = db.query(HouseholdMember).filter(HouseholdMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Update fields
    for key, value in payload.items():
        if hasattr(member, key):
            setattr(member, key, value)
    
    db.commit()
    db.refresh(member)
    return member

@router.put("/{member_id}/status")
def update_member_status(
    member_id: int,
    status: str,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Update member status (active/inactive)"""
    if status not in ["active", "inactive"]:
        raise HTTPException(status_code=400, detail="Status must be 'active' or 'inactive'")
    
    member = db.query(HouseholdMember).filter(HouseholdMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    member.status = status
    db.commit()
    db.refresh(member)
    return member

@router.delete("/{member_id}")
def delete_member(
    member_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Delete a member"""
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    member = db.query(HouseholdMember).filter(HouseholdMember.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    db.delete(member)
    db.commit()
    return {"detail": "Member deleted successfully"}