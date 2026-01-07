# spms_db/backend/households/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Household, HouseholdMember
from auth.routes import get_current_user

router = APIRouter()

@router.post("/")
def create_household(
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Create a new household"""
    # Validate required fields
    if not payload.get("cluster_name"):
        raise HTTPException(status_code=400, detail="Cluster name is required")
    if not payload.get("community"):
        raise HTTPException(status_code=400, detail="Community is required")
    if not payload.get("village"):
        raise HTTPException(status_code=400, detail="Village is required")
    
    household = Household(**payload)
    db.add(household)
    db.commit()
    db.refresh(household)
    return household

@router.get("/")
def list_households(
    cluster_name: Optional[str] = None,
    community: Optional[str] = None,
    village: Optional[str] = None,
    highly_vulnerable: Optional[bool] = None,
    food_insecure: Optional[bool] = None,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all households with optional filters"""
    query = db.query(Household)
    
    if cluster_name:
        query = query.filter(Household.cluster_name.ilike(f"%{cluster_name}%"))
    if community:
        query = query.filter(Household.community.ilike(f"%{community}%"))
    if village:
        query = query.filter(Household.village.ilike(f"%{village}%"))
    if highly_vulnerable is not None:
        query = query.filter(Household.highly_vulnerable == highly_vulnerable)
    if food_insecure is not None:
        query = query.filter(Household.food_insecure == food_insecure)
    
    return query.all()

@router.get("/{household_id}")
def get_household(
    household_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get a specific household by ID"""
    household = db.query(Household).filter(Household.id == household_id).first()
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    return household

@router.get("/{household_id}/members")
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

@router.get("/{household_id}/summary")
def get_household_summary(
    household_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get household summary with member count and statistics"""
    household = db.query(Household).filter(Household.id == household_id).first()
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    
    members = db.query(HouseholdMember).filter(HouseholdMember.household_id == household_id).all()
    
    # Count members by gender
    male_count = sum(1 for m in members if m.sex == "M")
    female_count = sum(1 for m in members if m.sex == "F")
    
    # Count children (age < 18)
    children_count = sum(1 for m in members if m.age and m.age < 18)
    
    # Find head of household
    head = next((m for m in members if m.relationship_type == "Head"), None)
    
    return {
        "household": household,
        "total_members": len(members),
        "male_count": male_count,
        "female_count": female_count,
        "children_count": children_count,
        "head_of_household": head.name if head else None
    }

@router.get("/vulnerable")
def get_vulnerable_households(
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Get all vulnerable households"""
    households = db.query(Household).filter(
        (Household.highly_vulnerable == True) |
        (Household.food_insecure == True) |
        (Household.shelter_insecure == True)
    ).all()
    return households

@router.put("/{household_id}")
def update_household(
    household_id: int,
    payload: dict,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Update a household"""
    household = db.query(Household).filter(Household.id == household_id).first()
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    
    # Update fields
    for key, value in payload.items():
        if hasattr(household, key):
            setattr(household, key, value)
    
    db.commit()
    db.refresh(household)
    return household

@router.delete("/{household_id}")
def delete_household(
    household_id: int,
    db: Session = Depends(get_db), 
    current = Depends(get_current_user)
):
    """Delete a household"""
    if current.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    household = db.query(Household).filter(Household.id == household_id).first()
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    
    # Check if household has members
    member_count = db.query(HouseholdMember).filter(HouseholdMember.household_id == household_id).count()
    if member_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete household with {member_count} members. Delete members first."
        )
    
    db.delete(household)
    db.commit()
    return {"detail": "Household deleted successfully"}