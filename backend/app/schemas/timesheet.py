from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    code: str
    name: str
    client_name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "Active"
    is_billable: bool = True
    owner_employee_id: Optional[int] = None


class ProjectSchema(ProjectCreate):
    id: int
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class TimesheetEntryCreate(BaseModel):
    work_date: date
    hours: Decimal
    is_billable: bool = True
    task_name: Optional[str] = None
    description: Optional[str] = None


class TimesheetEntrySchema(TimesheetEntryCreate):
    id: int
    timesheet_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class TimesheetCreate(BaseModel):
    project_id: int
    period_start: date
    period_end: date


class TimesheetSchema(BaseModel):
    id: int
    employee_id: int
    project_id: int
    period_start: date
    period_end: date
    status: str
    total_hours: Decimal
    billable_hours: Decimal
    non_billable_hours: Decimal
    submitted_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_remarks: Optional[str] = None
    entries: list[TimesheetEntrySchema] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class TimesheetReview(BaseModel):
    status: str
    review_remarks: Optional[str] = None
