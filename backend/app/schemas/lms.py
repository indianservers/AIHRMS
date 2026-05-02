from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict


class LearningCourseCreate(BaseModel):
    code: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    delivery_mode: str = "Online"
    duration_hours: Decimal = Decimal("0")
    is_mandatory: bool = False


class LearningCourseSchema(LearningCourseCreate):
    id: int
    is_active: bool
    created_by: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class LearningAssignmentCreate(BaseModel):
    course_id: int
    employee_id: int
    due_date: Optional[date] = None


class LearningAssignmentUpdate(BaseModel):
    status: str
    score: Optional[Decimal] = None


class LearningAssignmentSchema(LearningAssignmentCreate):
    id: int
    assigned_by: Optional[int] = None
    status: str
    completed_at: Optional[datetime] = None
    score: Optional[Decimal] = None
    model_config = ConfigDict(from_attributes=True)


class LearningCertificationCreate(BaseModel):
    employee_id: int
    course_id: Optional[int] = None
    title: str
    certificate_url: Optional[str] = None
    issued_on: Optional[date] = None
    expires_on: Optional[date] = None


class LearningCertificationSchema(LearningCertificationCreate):
    id: int
    status: str
    verified_by: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
