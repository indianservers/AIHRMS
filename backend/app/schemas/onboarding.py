from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class OnboardingTaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    assigned_to_role: Optional[str] = None
    due_days: int = 1
    is_mandatory: bool = True
    order_sequence: int = 1


class OnboardingTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    applicable_designation_ids: Optional[str] = None
    is_active: bool = True


class OnboardingTemplateSchema(OnboardingTemplateCreate):
    id: int
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class EmployeeOnboardingCreate(BaseModel):
    employee_id: int
    template_id: Optional[int] = None
    start_date: Optional[date] = None
    expected_completion_date: Optional[date] = None


class EmployeeOnboardingSchema(EmployeeOnboardingCreate):
    id: int
    completed_date: Optional[date] = None
    status: str = "In Progress"
    welcome_email_sent: bool = False
    welcome_email_sent_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class PolicyAcknowledgementCreate(BaseModel):
    employee_id: int
    policy_name: str
    policy_document_url: Optional[str] = None
    ip_address: Optional[str] = None


class PolicyAcknowledgementSchema(PolicyAcknowledgementCreate):
    id: int
    acknowledged_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
