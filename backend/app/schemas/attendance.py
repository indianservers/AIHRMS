from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class ShiftBase(BaseModel):
    name: str
    code: Optional[str] = None
    start_time: time
    end_time: time
    grace_minutes: int = 10
    working_hours: Decimal = Decimal("8.0")
    is_night_shift: bool = False


class ShiftCreate(ShiftBase):
    pass


class ShiftSchema(ShiftBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class ShiftWeeklyOffCreate(BaseModel):
    shift_id: int
    weekday: int
    week_pattern: str = "all"


class ShiftWeeklyOffSchema(ShiftWeeklyOffCreate):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class ShiftRosterAssignmentCreate(BaseModel):
    employee_id: int
    shift_id: int
    work_date: date
    status: str = "Published"


class ShiftRosterAssignmentSchema(ShiftRosterAssignmentCreate):
    id: int

    class Config:
        from_attributes = True


class HolidayBase(BaseModel):
    name: str
    holiday_date: date
    holiday_type: str = "National"
    description: Optional[str] = None
    applicable_branches: Optional[str] = None


class HolidayCreate(HolidayBase):
    pass


class HolidaySchema(HolidayBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class CheckInRequest(BaseModel):
    check_in_location: Optional[str] = None
    check_in_ip: Optional[str] = None
    source: str = "Web"


class CheckOutRequest(BaseModel):
    check_out_location: Optional[str] = None
    check_out_ip: Optional[str] = None


class AttendanceSchema(BaseModel):
    id: int
    employee_id: int
    attendance_date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    shift_id: Optional[int] = None
    total_hours: Optional[Decimal] = None
    overtime_hours: Decimal = Decimal("0")
    late_minutes: int = 0
    early_exit_minutes: int = 0
    short_minutes: int = 0
    is_late: bool = False
    is_early_exit: bool = False
    is_short_hours: bool = False
    status: str
    source: str
    is_regularized: bool
    computed_at: Optional[datetime] = None
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class RegularizationRequest(BaseModel):
    attendance_id: int
    requested_check_in: Optional[datetime] = None
    requested_check_out: Optional[datetime] = None
    reason: str


class RegularizationApproval(BaseModel):
    status: str  # Approved, Rejected
    review_remarks: Optional[str] = None


class RegularizationSchema(BaseModel):
    id: int
    attendance_id: int
    employee_id: int
    requested_check_in: Optional[datetime] = None
    requested_check_out: Optional[datetime] = None
    reason: str
    status: str
    reviewed_at: Optional[datetime] = None
    review_remarks: Optional[str] = None

    class Config:
        from_attributes = True


class AttendanceSummary(BaseModel):
    employee_id: int
    month: int
    year: int
    total_working_days: int
    present_days: int
    absent_days: int
    half_days: int
    leave_days: int
    holiday_days: int
    late_count: int
    overtime_hours: Decimal
