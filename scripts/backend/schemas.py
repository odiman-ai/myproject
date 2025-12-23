from pydantic import BaseModel
from datetime import date
from typing import Optional

# Beneficiary
class BeneficiaryBase(BaseModel):
    name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    location: Optional[str] = None

class BeneficiaryCreate(BeneficiaryBase):
    pass

class Beneficiary(BeneficiaryBase):
    id: int
    class Config:
        orm_mode = True


# Attendance
class AttendanceBase(BaseModel):
    beneficiary_id: int
    date: date
    status: str

class AttendanceCreate(AttendanceBase):
    pass

class Attendance(AttendanceBase):
    id: int
    class Config:
        orm_mode = True


# Survey
class SurveyBase(BaseModel):
    beneficiary_id: int
    survey_date: date
    responses: Optional[str] = None

class SurveyCreate(SurveyBase):
    pass

class Survey(SurveyBase):
    id: int
    class Config:
        orm_mode = True
