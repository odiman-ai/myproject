# spms_db/backend/schemas/schemas.py
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List, Any
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import re


# -----------------------------
# ENUMS
# -----------------------------
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    USER = "user"
    VIEWER = "viewer"
    PARTICIPANT = "participant"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    LOCKED = "locked"


class ProgrammeStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    SUSPENDED = "suspended"


class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    SUSPENDED = "suspended"


class ActivityStatus(str, Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SexEnum(str, Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "Other"


class MemberStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECEASED = "deceased"
    RELOCATED = "relocated"


class AttendanceStatus(str, Enum):
    IN = "IN"
    OUT = "OUT"
    ABSENT = "ABSENT"
    LATE = "LATE"


class SurveyStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CLOSED = "closed"


class CaseStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class CasePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# -----------------------------
# BASE CLASSES
# -----------------------------
class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# -----------------------------
# AUTHENTICATION SCHEMAS
# -----------------------------
class LoginRequest(BaseSchema):
    """Schema for login request"""
    username: str = Field(..., min_length=3, max_length=50, description="Username or email")
    password: str = Field(..., min_length=6, description="User password")


class MessageResponse(BaseSchema):
    """Generic message response"""
    message: str
    detail: Optional[str] = None


class TokenResponse(BaseSchema):
    """Schema for token response - matches OAuth2 standard"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: Optional[int] = Field(None, description="Token expiration time in seconds")


class RefreshTokenRequest(BaseSchema):
    """Schema for refresh token request"""
    refresh_token: str = Field(..., description="Refresh token to exchange for new access token")


class PasswordChangeRequest(BaseSchema):
    """Schema for password change request"""
    current_password: str = Field(..., min_length=6, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 chars)")
    confirm_password: Optional[str] = Field(None, description="Confirm new password")

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure passwords match if provided"""
        if v is not None and 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v


class RegisterRequest(BaseSchema):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    role: Optional[str] = Field(default="staff", description="User role")

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate username format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v.lower()


class PasswordResetRequest(BaseSchema):
    """Schema for password reset request"""
    email: EmailStr = Field(..., description="User's email address")


class PasswordResetConfirm(BaseSchema):
    """Schema for password reset confirmation"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Ensure passwords match"""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v


# -----------------------------
# USER SCHEMAS
# -----------------------------
class UserBase(BaseSchema):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    full_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description="User email address")
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole = Field(default=UserRole.USER)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    
    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v.lower()


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    confirm_password: str = Field(..., description="Confirm password")

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Ensure passwords match"""
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v


class UserUpdate(BaseSchema):
    """Schema for updating a user"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None


class UserResponse(UserBase, TimestampMixin):
    """Schema for user response - NO Request/Response objects"""
    id: int
    is_locked: bool = False
    failed_login_attempts: int = 0
    last_login: Optional[datetime] = None
    last_login_ip: Optional[str] = None


class UserListResponse(BaseSchema):
    """Schema for paginated user list response"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# -----------------------------
# SESSION SCHEMAS
# -----------------------------
class SessionResponse(BaseSchema):
    """Schema for session response"""
    id: int
    user_id: int
    token: str
    expires_at: datetime
    created_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class SessionListResponse(BaseSchema):
    """Schema for user's active sessions"""
    sessions: List[SessionResponse]
    total: int


# -----------------------------
# PROGRAMMES
# -----------------------------
class ProgrammeBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    status: ProgrammeStatus = Field(default=ProgrammeStatus.PLANNING)
    
    @field_validator('end_date')
    @classmethod
    def end_after_start(cls, v: Optional[date], info) -> Optional[date]:
        if v and 'start_date' in info.data and info.data['start_date']:
            if v < info.data['start_date']:
                raise ValueError('end_date must be after start_date')
        return v


class ProgrammeCreate(ProgrammeBase):
    pass


class ProgrammeUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = Field(None, ge=0)
    status: Optional[ProgrammeStatus] = None


class ProgrammeResponse(ProgrammeBase, TimestampMixin):
    id: int
    project_count: Optional[int] = 0


# -----------------------------
# PROJECTS
# -----------------------------
class ProjectBase(BaseSchema):
    programme_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    status: ProjectStatus = Field(default=ProjectStatus.PLANNING)
    
    @field_validator('end_date')
    @classmethod
    def end_after_start(cls, v: Optional[date], info) -> Optional[date]:
        if v and 'start_date' in info.data and info.data['start_date']:
            if v < info.data['start_date']:
                raise ValueError('end_date must be after start_date')
        return v


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseSchema):
    programme_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = Field(None, ge=0)
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase, TimestampMixin):
    id: int
    activity_count: Optional[int] = 0


# -----------------------------
# ACTIVITIES
# -----------------------------
class ActivityBase(BaseSchema):
    project_id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=200)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    capacity: Optional[int] = Field(None, gt=0)
    status: ActivityStatus = Field(default=ActivityStatus.SCHEDULED)
    
    @field_validator('end_date')
    @classmethod
    def end_after_start(cls, v: Optional[date], info) -> Optional[date]:
        if v and 'start_date' in info.data and info.data['start_date']:
            if v < info.data['start_date']:
                raise ValueError('end_date must be after start_date')
        return v


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseSchema):
    project_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    capacity: Optional[int] = Field(None, gt=0)
    status: Optional[ActivityStatus] = None


class ActivityResponse(ActivityBase, TimestampMixin):
    id: int
    attendance_count: Optional[int] = 0


# -----------------------------
# HOUSEHOLDS
# -----------------------------
class HouseholdBase(BaseSchema):
    household_number: Optional[str] = Field(None, max_length=50)
    cluster_name: str = Field(..., min_length=1, max_length=200)
    community: str = Field(..., min_length=1, max_length=200)
    village: str = Field(..., min_length=1, max_length=200)
    consent_given: bool = False
    consent_date: Optional[date] = None
    notes: Optional[str] = None
    gps_lat: Optional[Decimal] = Field(None, ge=-90, le=90, decimal_places=7)
    gps_lon: Optional[Decimal] = Field(None, ge=-180, le=180, decimal_places=7)
    origin_country: Optional[str] = Field(None, max_length=100)
    origin_address: Optional[str] = None
    # Vulnerability flags
    special_judicial_needs: bool = False
    economically_depressed: bool = False
    food_insecure: bool = False
    shelter_insecure: bool = False
    war_persecution_affected: bool = False
    disaster_affected: bool = False
    highly_vulnerable: bool = False
    status: str = Field(default="active")


class HouseholdCreate(HouseholdBase):
    pass


class HouseholdUpdate(BaseSchema):
    household_number: Optional[str] = None
    cluster_name: Optional[str] = None
    community: Optional[str] = None
    village: Optional[str] = None
    consent_given: Optional[bool] = None
    consent_date: Optional[date] = None
    notes: Optional[str] = None
    gps_lat: Optional[Decimal] = Field(None, ge=-90, le=90)
    gps_lon: Optional[Decimal] = Field(None, ge=-180, le=180)
    status: Optional[str] = None


class HouseholdResponse(HouseholdBase, TimestampMixin):
    id: int
    member_count: Optional[int] = 0
    vulnerability_score: Optional[int] = 0


# -----------------------------
# HOUSEHOLD MEMBERS
# -----------------------------
class HouseholdMemberBase(BaseSchema):
    household_id: int
    name: str = Field(..., min_length=1, max_length=200)
    photo_url: Optional[str] = Field(None, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=150)
    dob: Optional[date] = None
    sex: SexEnum
    relationship_type: str
    marital_status: str
    status: MemberStatus = Field(default=MemberStatus.ACTIVE)
    reg_date: Optional[date] = None
    notes: Optional[str] = None
    # Identification
    assigned_id: Optional[str] = Field(None, max_length=18)
    gov_id_type: Optional[str] = None
    gov_id_number: Optional[str] = Field(None, max_length=32)
    # Phone
    phone_carrier: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    # Payment
    payment_agency: Optional[str] = "None"
    payment_agency_type: Optional[str] = "None"
    account_number: Optional[str] = Field(None, max_length=50)
    client_number: Optional[str] = Field(None, max_length=50)
    # Displacement
    is_idp: bool = False
    is_migrant: bool = False
    is_refugee: bool = False
    is_refugee_claimant: bool = False
    is_returnee: bool = False
    # Health
    malnourished: bool = False
    pregnant: bool = False
    lactating: bool = False
    hiv_aids: bool = False
    tb: bool = False
    other_chronic_illness: bool = False
    needs_medical_attention: bool = False
    needs_psychological_counselling: bool = False
    permanent_physical_disability: bool = False
    mental_disability: bool = False
    temporarily_incapacitated: bool = False
    limited_strength_mobility: bool = False
    # Protection
    orphan: bool = False
    minor_worst_forms_child_labour: bool = False
    minor_not_attending_school: bool = False
    unaccompanied_by_adult: bool = False
    needs_protection: bool = False
    
    @field_validator('age')
    @classmethod
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        """Validate age is within reasonable range"""
        if v is not None:
            if v < 0 or v > 150:
                raise ValueError('Age must be between 0 and 150')
        return v


class HouseholdMemberCreate(HouseholdMemberBase):
    pass


class HouseholdMemberUpdate(BaseSchema):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    dob: Optional[date] = None
    status: Optional[MemberStatus] = None
    notes: Optional[str] = None
    phone_number: Optional[str] = None
    # Allow updating any health/protection flags
    malnourished: Optional[bool] = None
    needs_medical_attention: Optional[bool] = None
    needs_protection: Optional[bool] = None


class HouseholdMemberResponse(HouseholdMemberBase, TimestampMixin):
    id: int
    is_minor: Optional[bool] = None
    health_vulnerability_score: Optional[int] = 0


# -----------------------------
# ATTENDANCE
# -----------------------------
class AttendanceBase(BaseSchema):
    member_id: int
    activity_id: int
    status: AttendanceStatus
    notes: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseSchema):
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    id: int
    timestamp: datetime
    member_name: Optional[str] = None
    activity_name: Optional[str] = None


# -----------------------------
# SURVEYS
# -----------------------------
class SurveyBase(BaseSchema):
    project_id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: SurveyStatus = Field(default=SurveyStatus.DRAFT)


class SurveyCreate(SurveyBase):
    pass


class SurveyUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[SurveyStatus] = None


class SurveyResponse(SurveyBase, TimestampMixin):
    id: int
    created_by: Optional[int] = None
    response_count: Optional[int] = 0


class SurveyResponseBase(BaseSchema):
    survey_id: int
    member_id: int
    response: Optional[str] = None


class SurveyResponseCreate(SurveyResponseBase):
    pass


class SurveyResponseOut(SurveyResponseBase):
    id: int
    submitted_at: datetime


# -----------------------------
# M&E INDICATORS
# -----------------------------
class MEIndicatorBase(BaseSchema):
    project_id: int
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    indicator_type: str = Field(default="output")
    target_value: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    current_value: Optional[Decimal] = Field(default=0, ge=0, decimal_places=2)
    unit: Optional[str] = Field(None, max_length=50)


class MEIndicatorCreate(MEIndicatorBase):
    pass


class MEIndicatorUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[Decimal] = Field(None, ge=0)
    current_value: Optional[Decimal] = Field(None, ge=0)
    unit: Optional[str] = None


class MEIndicatorResponse(MEIndicatorBase, TimestampMixin):
    id: int
    achievement_percentage: Optional[float] = None


# -----------------------------
# REPORTS
# -----------------------------
class ReportBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = None
    generated_by: Optional[int] = None
    related_module: Optional[str] = None
    report_period_start: Optional[date] = None
    report_period_end: Optional[date] = None


class ReportCreate(ReportBase):
    pass


class ReportResponse(ReportBase):
    id: int
    created_at: datetime


# -----------------------------
# CASES
# -----------------------------
class CaseBase(BaseSchema):
    case_number: str = Field(..., min_length=1, max_length=50)
    member_id: int
    project_id: Optional[int] = None
    status: CaseStatus = Field(default=CaseStatus.OPEN)
    priority: CasePriority = Field(default=CasePriority.MEDIUM)
    category: Optional[str] = None
    description: Optional[str] = None
    resolution: Optional[str] = None


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseSchema):
    status: Optional[CaseStatus] = None
    priority: Optional[CasePriority] = None
    category: Optional[str] = None
    description: Optional[str] = None
    resolution: Optional[str] = None


class CaseResponse(CaseBase, TimestampMixin):
    id: int
    opened_at: datetime
    closed_at: Optional[datetime] = None
    is_open: Optional[bool] = None
    note_count: Optional[int] = 0


# -----------------------------
# CASE NOTES
# -----------------------------
class CaseNoteBase(BaseSchema):
    case_id: int
    note: str = Field(..., min_length=1)
    created_by: Optional[int] = None


class CaseNoteCreate(CaseNoteBase):
    pass


class CaseNoteResponse(CaseNoteBase):
    id: int
    created_at: datetime
    creator_name: Optional[str] = None


# -----------------------------
# PAGINATION
# -----------------------------
class PaginationParams(BaseSchema):
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum number of records to return")


class PaginatedResponse(BaseSchema):
    total: int = Field(..., description="Total number of records")
    skip: int
    limit: int
    data: List[Any]
    
    @property
    def has_more(self) -> bool:
        """Check if there are more records"""
        return self.skip + self.limit < self.total


# -----------------------------
# GENERIC RESPONSES
# -----------------------------
class ErrorResponse(BaseSchema):
    detail: str
    status_code: Optional[int] = None
    error_code: Optional[str] = None
    path: Optional[str] = None


class SuccessResponse(BaseSchema):
    success: bool = True
    message: str
    data: Optional[dict] = None


class BulkOperationResponse(BaseSchema):
    success_count: int
    failure_count: int
    total: int
    errors: Optional[List[dict]] = None