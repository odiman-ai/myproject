from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base

# ---------------- Beneficiaries ----------------
class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    gender = Column(String(10), nullable=True)
    age = Column(Integer, nullable=True)
    location = Column(String(255), nullable=True)

    attendance_records = relationship("Attendance", back_populates="beneficiary")
    surveys = relationship("Survey", back_populates="beneficiary")


# ---------------- Attendance ----------------
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)

    beneficiary = relationship("Beneficiary", back_populates="attendance_records")


# ---------------- Surveys ----------------
class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"), nullable=False)
    survey_date = Column(Date, nullable=False)
    responses = Column(Text, nullable=True)

    beneficiary = relationship("Beneficiary", back_populates="surveys")


# ---------------- Users ----------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)


# ---------------- Programs ----------------
class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)


# ---------------- Activities ----------------
class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)


# ---------------- Enrollments ----------------
class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    enrollment_date = Column(Date, nullable=False)


# ---------------- Notifications ----------------
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)


# ---------------- Audit Logs ----------------
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    timestamp = Column(DateTime, nullable=False)


# ---------------- Custom Fields ----------------
class CustomField(Base):
    __tablename__ = "custom_fields"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    field_type = Column(String(50), nullable=False)
    value = Column(Text, nullable=True)


# ---------------- Data Records ----------------
class DataRecord(Base):
    __tablename__ = "data_records"

    id = Column(Integer, primary_key=True, index=True)
    beneficiary_id = Column(Integer, ForeignKey("beneficiaries.id"), nullable=False)
    field_id = Column(Integer, ForeignKey("custom_fields.id"), nullable=False)
    value = Column(Text, nullable=True)


# ---------------- Offline Queue ----------------
class OfflineQueue(Base):
    __tablename__ = "offline_queue"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    processed = Column(Boolean, default=False)


# ---------------- User Sessions ----------------
class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
