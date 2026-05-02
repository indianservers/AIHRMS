from datetime import date, datetime
from decimal import Decimal
from typing import List, Literal, Optional
from pydantic import BaseModel, field_validator
from app.schemas.employee import EmployeeListSchema


class LeaveTypeBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    days_allowed: Decimal
    accrual_frequency: Literal["daily", "weekly", "monthly", "quarterly", "annual"] = "annual"
    carry_forward: bool = False
    carry_forward_limit: Decimal = Decimal("0")
    encashable: bool = False
    applicable_gender: str = "All"
    applicable_from_months: int = 0
    half_day_allowed: bool = True
    color: str = "#3B82F6"

    @field_validator("accrual_frequency")
    @classmethod
    def validate_accrual_frequency(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"daily", "weekly", "monthly", "quarterly", "annual"}:
            raise ValueError("accrual_frequency must be daily, weekly, monthly, quarterly, or annual")
        return normalized


class LeaveTypeCreate(LeaveTypeBase):
    pass


class LeaveTypeUpdate(LeaveTypeBase):
    name: Optional[str] = None
    code: Optional[str] = None
    days_allowed: Optional[Decimal] = None


class LeaveTypeSchema(LeaveTypeBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class LeaveBalanceSchema(BaseModel):
    id: int
    employee_id: int
    leave_type_id: int
    leave_type: Optional[LeaveTypeSchema] = None
    year: int
    allocated: Decimal
    used: Decimal
    pending: Decimal
    carried_forward: Decimal
    available: Decimal = Decimal("0")

    class Config:
        from_attributes = True

    def model_post_init(self, __context):
        object.__setattr__(self, 'available', self.allocated + self.carried_forward - self.used - self.pending)


class LeaveBalanceLedgerSchema(BaseModel):
    id: int
    employee_id: int
    leave_type_id: int
    leave_balance_id: Optional[int] = None
    leave_request_id: Optional[int] = None
    year: int
    transaction_type: str
    amount: Decimal
    balance_after: Decimal
    reason: Optional[str] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


class LeaveRequestCreate(BaseModel):
    leave_type_id: int
    from_date: date
    to_date: date
    is_half_day: bool = False
    half_day_period: Optional[str] = None
    reason: Optional[str] = None
    contact_during_leave: Optional[str] = None
    handover_employee_id: Optional[int] = None


class LeaveApprovalRequest(BaseModel):
    status: str  # Approved, Rejected
    review_remarks: Optional[str] = None


class LeaveRequestSchema(BaseModel):
    id: int
    company_id: Optional[int] = None
    employee_id: int
    employee: Optional[EmployeeListSchema] = None
    leave_type_id: int
    leave_type: Optional[LeaveTypeSchema] = None
    from_date: date
    to_date: date
    days_count: Decimal
    is_half_day: bool
    half_day_period: Optional[str] = None
    reason: Optional[str] = None
    status: str
    applied_at: datetime
    reviewed_at: Optional[datetime] = None
    review_remarks: Optional[str] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    class Config:
        from_attributes = True


class LeaveCalendarEmployee(BaseModel):
    id: int
    employee_id: str
    first_name: str
    last_name: str
    department_id: Optional[int] = None

    class Config:
        from_attributes = True


class LeaveCalendarItem(BaseModel):
    id: int
    employee_id: int
    employee: Optional[LeaveCalendarEmployee] = None
    leave_type: Optional[LeaveTypeSchema] = None
    from_date: date
    to_date: date
    status: str
    days_count: Decimal
    reason: Optional[str] = None

    class Config:
        from_attributes = True


class LeaveCalendarHoliday(BaseModel):
    id: int
    name: str
    holiday_date: date
    holiday_type: str

    class Config:
        from_attributes = True


class LeaveCalendarDay(BaseModel):
    date: date
    leave_count: int
    pending_count: int
    approved_count: int
    employees_on_leave: List[LeaveCalendarItem] = []
    holidays: List[LeaveCalendarHoliday] = []


class LeaveCalendarResponse(BaseModel):
    from_date: date
    to_date: date
    scope: str
    total_leave_days: int
    days: List[LeaveCalendarDay]
