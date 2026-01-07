# spms_db/backend/models.py
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Enum,
    ForeignKey,
    TIMESTAMP,
    Date,
    Boolean,
    DECIMAL,
    func,
    UniqueConstraint,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property
from backend.database import Base


# -------------------------
# USERS
# -------------------------
class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    email = Column(String(120), unique=True, index=True)
    phone = Column(String(20))
    role = Column(
        Enum("admin", "staff", "participant", name="user_roles"),
        default="staff",
        nullable=False,
        index=True
    )
    status = Column(
        Enum("active", "inactive", "suspended", name="user_status"),
        default="active",
        nullable=False,
        index=True
    )
    last_login = Column(TIMESTAMP, nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    account_locked_until = Column(TIMESTAMP, nullable=True)
    password_changed_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    created_surveys = relationship("Survey", foreign_keys="Survey.created_by", back_populates="creator")
    generated_reports = relationship("Report", foreign_keys="Report.generated_by", back_populates="generator")
    case_notes = relationship("CaseNote", foreign_keys="CaseNote.created_by", back_populates="creator")
    
    __table_args__ = (
        CheckConstraint('failed_login_attempts >= 0', name='check_failed_attempts_positive'),
        Index('idx_user_role_status', 'role', 'status'),
    )
    
    @hybrid_property
    def is_active(self) -> bool:
        """Check if user account is active"""
        return self.status == "active"
    
    @hybrid_property
    def is_locked(self) -> bool:
        """Check if account is currently locked"""
        if self.account_locked_until:
            return datetime.utcnow() < self.account_locked_until
        return False
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


# -------------------------
# PROGRAMMES
# -------------------------
class Programme(Base):
    """Programme model - top level organizational unit"""
    __tablename__ = "programmes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True, index=True)
    description = Column(Text)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    budget = Column(DECIMAL(15, 2), nullable=True)
    status = Column(
        Enum("planning", "active", "completed", "suspended", name="programme_status"),
        default="planning",
        nullable=False,
        index=True
    )
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    projects = relationship("Project", back_populates="programme", cascade="all, delete-orphan", lazy="dynamic")
    
    __table_args__ = (
        CheckConstraint('end_date IS NULL OR start_date IS NULL OR end_date >= start_date', 
                       name='check_programme_dates'),
        CheckConstraint('budget IS NULL OR budget >= 0', name='check_programme_budget_positive'),
    )
    
    @hybrid_property
    def is_active(self) -> bool:
        """Check if programme is currently active"""
        return self.status == "active"
    
    def __repr__(self) -> str:
        return f"<Programme(id={self.id}, name='{self.name}', status='{self.status}')>"


# -------------------------
# PROJECTS
# -------------------------
class Project(Base):
    """Project model - belongs to a programme"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    programme_id = Column(Integer, ForeignKey("programmes.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=True, index=True)
    description = Column(Text)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    budget = Column(DECIMAL(15, 2), nullable=True)
    status = Column(
        Enum("planning", "active", "completed", "suspended", name="project_status"),
        default="planning",
        nullable=False,
        index=True
    )
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    programme = relationship("Programme", back_populates="projects")
    activities = relationship("Activity", back_populates="project", cascade="all, delete-orphan", lazy="dynamic")
    surveys = relationship("Survey", back_populates="project", cascade="all, delete-orphan")
    me_indicators = relationship("MEIndicator", back_populates="project", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="project")
    
    __table_args__ = (
        CheckConstraint('end_date IS NULL OR start_date IS NULL OR end_date >= start_date',
                       name='check_project_dates'),
        CheckConstraint('budget IS NULL OR budget >= 0', name='check_project_budget_positive'),
        Index('idx_project_programme_status', 'programme_id', 'status'),
    )
    
    @hybrid_property
    def is_active(self) -> bool:
        """Check if project is currently active"""
        return self.status == "active"
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', code='{self.code}')>"


# -------------------------
# ACTIVITIES
# -------------------------
class Activity(Base):
    """Activity model - belongs to a project"""
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    location = Column(String(200), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    capacity = Column(Integer, nullable=True)
    status = Column(
        Enum("scheduled", "ongoing", "completed", "cancelled", name="activity_status"),
        default="scheduled",
        nullable=False,
        index=True
    )
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="activities")
    attendance_records = relationship("Attendance", back_populates="activity", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint('project_id', 'name', name='uq_project_activity_name'),
        CheckConstraint('end_date IS NULL OR start_date IS NULL OR end_date >= start_date',
                       name='check_activity_dates'),
        CheckConstraint('capacity IS NULL OR capacity > 0', name='check_activity_capacity_positive'),
        Index('idx_activity_project_status', 'project_id', 'status'),
        Index('idx_activity_dates', 'start_date', 'end_date'),
    )
    
    @hybrid_property
    def is_ongoing(self) -> bool:
        """Check if activity is currently ongoing"""
        return self.status == "ongoing"
    
    def __repr__(self) -> str:
        return f"<Activity(id={self.id}, name='{self.name}', project_id={self.project_id})>"


# -------------------------
# HOUSEHOLDS
# -------------------------
class Household(Base):
    """Household model - represents a family unit"""
    __tablename__ = "households"
    
    id = Column(Integer, primary_key=True, index=True)
    household_number = Column(String(50), unique=True, nullable=True, index=True)
    cluster_name = Column(String(200), nullable=False, index=True)
    community = Column(String(200), nullable=False, index=True)
    village = Column(String(200), nullable=False, index=True)
    consent_given = Column(Boolean, default=False, nullable=False)
    consent_date = Column(Date, nullable=True)
    notes = Column(Text)
    
    # Geographic data
    gps_lat = Column(DECIMAL(10, 7))
    gps_lon = Column(DECIMAL(10, 7))
    
    # Origin information
    origin_country = Column(String(100))
    origin_address = Column(Text)
    
    # Vulnerability flags
    special_judicial_needs = Column(Boolean, default=False, nullable=False)
    economically_depressed = Column(Boolean, default=False, nullable=False)
    food_insecure = Column(Boolean, default=False, nullable=False)
    shelter_insecure = Column(Boolean, default=False, nullable=False)
    war_persecution_affected = Column(Boolean, default=False, nullable=False)
    disaster_affected = Column(Boolean, default=False, nullable=False)
    highly_vulnerable = Column(Boolean, default=False, nullable=False)
    
    # Status
    status = Column(
        Enum("active", "inactive", "relocated", name="household_status"),
        default="active",
        nullable=False,
        index=True
    )
    
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    members = relationship("HouseholdMember", back_populates="household", cascade="all, delete-orphan", lazy="dynamic")
    
    __table_args__ = (
        CheckConstraint('gps_lat IS NULL OR (gps_lat >= -90 AND gps_lat <= 90)',
                       name='check_valid_latitude'),
        CheckConstraint('gps_lon IS NULL OR (gps_lon >= -180 AND gps_lon <= 180)',
                       name='check_valid_longitude'),
        Index('idx_household_location', 'cluster_name', 'community', 'village'),
        Index('idx_household_vulnerability', 'highly_vulnerable', 'food_insecure'),
    )
    
    @hybrid_property
    def is_active(self) -> bool:
        """Check if household is active"""
        return self.status == "active"
    
    @hybrid_property
    def vulnerability_score(self) -> int:
        """Calculate vulnerability score based on flags"""
        score = 0
        if self.special_judicial_needs: score += 1
        if self.economically_depressed: score += 1
        if self.food_insecure: score += 2
        if self.shelter_insecure: score += 2
        if self.war_persecution_affected: score += 2
        if self.disaster_affected: score += 1
        if self.highly_vulnerable: score += 3
        return score
    
    def __repr__(self) -> str:
        return f"<Household(id={self.id}, cluster='{self.cluster_name}', members={self.members.count()})>"


# -------------------------
# HOUSEHOLD MEMBERS
# -------------------------
class HouseholdMember(Base):
    """Household member model - individual participant"""
    __tablename__ = "household_members"
    
    id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey("households.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Profile
    name = Column(String(200), nullable=False, index=True)
    photo_url = Column(String(255))
    age = Column(Integer)
    dob = Column(Date)
    sex = Column(Enum("M", "F", "Other", name="sex_enum"), nullable=False)
    
    relationship_type = Column(
        "relationship",
        Enum(
            "Head", "Aunt", "Child", "Common-law partner", "Cousin", "Grandchild", "Grandparent",
            "Nephew", "Niece", "Other", "Parent", "Sibling", "Spouse", "Uncle",
            name="relationship_types"
        ),
        nullable=False,
        index=True
    )
    
    marital_status = Column(
        Enum("Divorced", "Living common-law", "Married", "Separated", "Single", "Widowed",
             name="marital_statuses"),
        nullable=False
    )
    
    status = Column(
        Enum("active", "inactive", "deceased", "relocated", name="member_status"),
        default="active",
        nullable=False,
        index=True
    )
    reg_date = Column(Date, index=True)
    notes = Column(Text)
    
    # Identification
    assigned_id = Column(String(18), unique=True, index=True)
    gov_id_type = Column(
        Enum("National ID", "Driving License", "ID Card", "NIF", "NRC", "Passport",
             name="gov_id_types"),
        nullable=True
    )
    gov_id_number = Column(String(32), index=True)
    
    # Mobile Phone
    phone_carrier = Column(Enum("Airtel", "MTN", "Other", name="phone_carriers"), nullable=True)
    phone_number = Column(String(20))
    
    # Payment Account
    payment_agency = Column(
        Enum("Airtel Money", "MTN Mobile Money", "Bank", "None", name="payment_agencies"),
        default="None"
    )
    payment_agency_type = Column(
        Enum("Mobile Money", "Bank", "None", name="payment_agency_types"),
        default="None"
    )
    account_number = Column(String(50))
    client_number = Column(String(50))
    
    # Displacement Status
    is_idp = Column(Boolean, default=False, nullable=False)
    is_migrant = Column(Boolean, default=False, nullable=False)
    is_refugee = Column(Boolean, default=False, nullable=False)
    is_refugee_claimant = Column(Boolean, default=False, nullable=False)
    is_returnee = Column(Boolean, default=False, nullable=False)
    
    # Health/Medical
    malnourished = Column(Boolean, default=False, nullable=False)
    pregnant = Column(Boolean, default=False, nullable=False)
    lactating = Column(Boolean, default=False, nullable=False)
    hiv_aids = Column(Boolean, default=False, nullable=False)
    tb = Column(Boolean, default=False, nullable=False)
    other_chronic_illness = Column(Boolean, default=False, nullable=False)
    needs_medical_attention = Column(Boolean, default=False, nullable=False)
    needs_psychological_counselling = Column(Boolean, default=False, nullable=False)
    permanent_physical_disability = Column(Boolean, default=False, nullable=False)
    mental_disability = Column(Boolean, default=False, nullable=False)
    temporarily_incapacitated = Column(Boolean, default=False, nullable=False)
    limited_strength_mobility = Column(Boolean, default=False, nullable=False)
    
    # Protection Needs
    orphan = Column(Boolean, default=False, nullable=False)
    minor_worst_forms_child_labour = Column(Boolean, default=False, nullable=False)
    minor_not_attending_school = Column(Boolean, default=False, nullable=False)
    unaccompanied_by_adult = Column(Boolean, default=False, nullable=False)
    needs_protection = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    household = relationship("Household", back_populates="members")
    attendance_records = relationship("Attendance", back_populates="member", cascade="all, delete-orphan")
    survey_responses = relationship("SurveyResponse", back_populates="member", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="member")
    
    __table_args__ = (
        CheckConstraint('age IS NULL OR age >= 0', name='check_age_positive'),
        CheckConstraint('age IS NULL OR age <= 150', name='check_age_reasonable'),
        Index('idx_member_household_status', 'household_id', 'status'),
        Index('idx_member_name_search', 'name'),
        Index('idx_member_vulnerable', 'needs_protection', 'orphan'),
    )
    
    @hybrid_property
    def is_active(self) -> bool:
        """Check if member is active"""
        return self.status == "active"
    
    @hybrid_property
    def is_minor(self) -> bool:
        """Check if member is under 18"""
        return self.age is not None and self.age < 18
    
    @hybrid_property
    def is_head_of_household(self) -> bool:
        """Check if member is head of household"""
        return self.relationship_type == "Head"
    
    @hybrid_property
    def has_displacement_status(self) -> bool:
        """Check if member has any displacement status"""
        return any([self.is_idp, self.is_migrant, self.is_refugee, 
                   self.is_refugee_claimant, self.is_returnee])
    
    @hybrid_property
    def health_vulnerability_score(self) -> int:
        """Calculate health vulnerability score"""
        score = 0
        health_flags = [
            self.malnourished, self.pregnant, self.lactating, self.hiv_aids,
            self.tb, self.other_chronic_illness, self.needs_medical_attention,
            self.needs_psychological_counselling, self.permanent_physical_disability,
            self.mental_disability, self.temporarily_incapacitated,
            self.limited_strength_mobility
        ]
        return sum(1 for flag in health_flags if flag)
    
    def __repr__(self) -> str:
        return f"<HouseholdMember(id={self.id}, name='{self.name}', household_id={self.household_id})>"


# -------------------------
# ATTENDANCE
# -------------------------
class Attendance(Base):
    """Attendance tracking for activities"""
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("household_members.id", ondelete="CASCADE"), 
                      nullable=False, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), 
                        nullable=False, index=True)
    status = Column(Enum("IN", "OUT", "ABSENT", "LATE", name="attendance_status"), nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)
    notes = Column(Text)
    
    # Relationships
    member = relationship("HouseholdMember", back_populates="attendance_records")
    activity = relationship("Activity", back_populates="attendance_records")
    
    __table_args__ = (
        Index('idx_attendance_member_activity', 'member_id', 'activity_id'),
        Index('idx_attendance_activity_date', 'activity_id', 'timestamp'),
    )
    
    def __repr__(self) -> str:
        return f"<Attendance(id={self.id}, member_id={self.member_id}, activity_id={self.activity_id}, status='{self.status}')>"


# -------------------------
# SURVEYS
# -------------------------
class Survey(Base):
    """Survey model for data collection"""
    __tablename__ = "surveys"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(
        Enum("draft", "active", "closed", name="survey_status"),
        default="draft",
        nullable=False,
        index=True
    )
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="surveys")
    creator = relationship("User", back_populates="created_surveys", foreign_keys=[created_by])
    responses = relationship("SurveyResponse", back_populates="survey", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Survey(id={self.id}, title='{self.title}', status='{self.status}')>"


class SurveyResponse(Base):
    """Survey response from household members"""
    __tablename__ = "survey_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False, index=True)
    member_id = Column(Integer, ForeignKey("household_members.id", ondelete="CASCADE"), 
                      nullable=False, index=True)
    response = Column(Text)
    submitted_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    survey = relationship("Survey", back_populates="responses")
    member = relationship("HouseholdMember", back_populates="survey_responses")
    
    __table_args__ = (
        UniqueConstraint('survey_id', 'member_id', name='uq_survey_member_response'),
        Index('idx_response_survey_date', 'survey_id', 'submitted_at'),
    )
    
    def __repr__(self) -> str:
        return f"<SurveyResponse(id={self.id}, survey_id={self.survey_id}, member_id={self.member_id})>"


# -------------------------
# M&E INDICATORS
# -------------------------
class MEIndicator(Base):
    """Monitoring & Evaluation indicators"""
    __tablename__ = "me_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    indicator_type = Column(
        Enum("output", "outcome", "impact", name="indicator_types"),
        default="output",
        nullable=False
    )
    target_value = Column(DECIMAL(10, 2))
    current_value = Column(DECIMAL(10, 2), default=0)
    unit = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="me_indicators")
    
    __table_args__ = (
        CheckConstraint('target_value IS NULL OR target_value >= 0',
                       name='check_target_positive'),
        CheckConstraint('current_value IS NULL OR current_value >= 0',
                       name='check_current_positive'),
    )
    
    @hybrid_property
    def achievement_percentage(self) -> Optional[float]:
        """Calculate achievement percentage"""
        if self.target_value and self.target_value > 0:
            return (float(self.current_value or 0) / float(self.target_value)) * 100
        return None
    
    def __repr__(self) -> str:
        return f"<MEIndicator(id={self.id}, name='{self.name}', type='{self.indicator_type}')>"


# -------------------------
# REPORTS
# -------------------------
class Report(Base):
    """Report generation and storage"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    generated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    related_module = Column(
        Enum("attendance", "survey", "me", "casemanagement", "project", 
             "programme", "activity", "registration", name="report_modules"),
        index=True
    )
    report_period_start = Column(Date, nullable=True)
    report_period_end = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    generator = relationship("User", back_populates="generated_reports", foreign_keys=[generated_by])
    
    __table_args__ = (
        CheckConstraint(
            'report_period_end IS NULL OR report_period_start IS NULL OR report_period_end >= report_period_start',
            name='check_report_period'
        ),
        Index('idx_report_module_date', 'related_module', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Report(id={self.id}, title='{self.title}', module='{self.related_module}')>"


# -------------------------
# CASES
# -------------------------
class Case(Base):
    """Case management for member issues"""
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(50), unique=True, nullable=False, index=True)
    member_id = Column(Integer, ForeignKey("household_members.id", ondelete="CASCADE"), 
                      nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), index=True)
    status = Column(
        Enum("open", "in_progress", "resolved", "closed", name="case_status"),
        default="open",
        nullable=False,
        index=True
    )
    priority = Column(
        Enum("low", "medium", "high", "critical", name="case_priority"),
        default="medium",
        nullable=False,
        index=True
    )
    category = Column(
        Enum("protection", "health", "legal", "financial", "other", name="case_category"),
        nullable=True,
        index=True
    )
    description = Column(Text)
    resolution = Column(Text)
    opened_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    closed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    member = relationship("HouseholdMember", back_populates="cases")
    project = relationship("Project", back_populates="cases")
    notes = relationship("CaseNote", back_populates="case", cascade="all, delete-orphan", order_by="CaseNote.created_at")
    
    __table_args__ = (
        CheckConstraint('closed_at IS NULL OR opened_at IS NULL OR closed_at >= opened_at',
                       name='check_case_dates'),
        Index('idx_case_status_priority', 'status', 'priority'),
        Index('idx_case_member_status', 'member_id', 'status'),
    )
    
    @hybrid_property
    def is_open(self) -> bool:
        """Check if case is open"""
        return self.status in ("open", "in_progress")
    
    def __repr__(self) -> str:
        return f"<Case(id={self.id}, case_number='{self.case_number}', status='{self.status}')>"


class CaseNote(Base):
    """Notes attached to cases"""
    __tablename__ = "case_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    note = Column(Text, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    case = relationship("Case", back_populates="notes")
    creator = relationship("User", back_populates="case_notes", foreign_keys=[created_by])
    
    def __repr__(self) -> str:
        return f"<CaseNote(id={self.id}, case_id={self.case_id})>"