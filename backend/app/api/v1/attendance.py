from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, RequirePermission
from app.crud.crud_attendance import crud_attendance, crud_holiday
from app.models.user import User
from app.models.attendance import Shift, ShiftRosterAssignment, ShiftWeeklyOff, AttendanceRegularization, Holiday, OvertimeRequest
from app.schemas.attendance import (
    ShiftCreate, ShiftSchema,
    ShiftRosterAssignmentCreate, ShiftRosterAssignmentSchema,
    ShiftWeeklyOffCreate, ShiftWeeklyOffSchema,
    HolidayCreate, HolidaySchema,
    CheckInRequest, CheckOutRequest,
    AttendanceSchema, RegularizationRequest,
    RegularizationApproval, RegularizationSchema,
)
from app.schemas.attendance import ShiftCreate as ShiftUpdate
from app.schemas.attendance import HolidayCreate as HolidayUpdate

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# ── Shifts ───────────────────────────────────────────────────────────────────

@router.get("/shifts", response_model=List[ShiftSchema])
def list_shifts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Shift).filter(Shift.is_active == True).all()


@router.post("/shifts", response_model=ShiftSchema, status_code=201)
def create_shift(
    data: ShiftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("attendance_manage")),
):
    shift = Shift(**data.model_dump())
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


@router.put("/shifts/{shift_id}", response_model=ShiftSchema)
def update_shift(
    shift_id: int,
    data: ShiftUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("attendance_manage")),
):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(shift, k, v)
    db.commit()
    db.refresh(shift)
    return shift


@router.delete("/shifts/{shift_id}")
def delete_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("attendance_manage")),
):
    shift = db.query(Shift).filter(Shift.id == shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    shift.is_active = False
    db.commit()
    return {"message": "Shift deactivated"}


@router.get("/weekly-offs", response_model=List[ShiftWeeklyOffSchema])
def list_weekly_offs(
    shift_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("attendance_manage")),
):
    query = db.query(ShiftWeeklyOff).filter(ShiftWeeklyOff.is_active == True)
    if shift_id:
        query = query.filter(ShiftWeeklyOff.shift_id == shift_id)
    return query.order_by(ShiftWeeklyOff.shift_id, ShiftWeeklyOff.weekday).all()


@router.post("/weekly-offs", response_model=ShiftWeeklyOffSchema, status_code=201)
def create_weekly_off(
    data: ShiftWeeklyOffCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("attendance_manage")),
):
    shift = db.query(Shift).filter(Shift.id == data.shift_id, Shift.is_active == True).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    weekly_off = ShiftWeeklyOff(**data.model_dump())
    db.add(weekly_off)
    db.commit()
    db.refresh(weekly_off)
    return weekly_off


@router.post("/roster", response_model=ShiftRosterAssignmentSchema, status_code=201)
def assign_roster(
    data: ShiftRosterAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("attendance_manage")),
):
    shift = db.query(Shift).filter(Shift.id == data.shift_id, Shift.is_active == True).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    existing = db.query(ShiftRosterAssignment).filter(
        ShiftRosterAssignment.employee_id == data.employee_id,
        ShiftRosterAssignment.work_date == data.work_date,
    ).first()
    if existing:
        existing.shift_id = data.shift_id
        existing.status = data.status
        db.commit()
        db.refresh(existing)
        return existing
    assignment = ShiftRosterAssignment(**data.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


# ── Holidays ─────────────────────────────────────────────────────────────────

@router.get("/holidays", response_model=List[HolidaySchema])
def list_holidays(
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Holiday).filter(Holiday.is_active == True)
    if year:
        from sqlalchemy import extract
        q = q.filter(extract("year", Holiday.holiday_date) == year)
    return q.order_by(Holiday.holiday_date).all()


@router.post("/holidays", response_model=HolidaySchema, status_code=201)
def create_holiday(
    data: HolidayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("attendance_manage")),
):
    holiday = Holiday(**data.model_dump())
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    return holiday


@router.put("/holidays/{holiday_id}", response_model=HolidaySchema)
def update_holiday(
    holiday_id: int,
    data: HolidayUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("attendance_manage")),
):
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(holiday, k, v)
    db.commit()
    db.refresh(holiday)
    return holiday


@router.delete("/holidays/{holiday_id}")
def delete_holiday(
    holiday_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("attendance_manage")),
):
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    holiday.is_active = False
    db.commit()
    return {"message": "Holiday deleted"}


# ── Check-in / Check-out ──────────────────────────────────────────────────────

@router.post("/check-in", response_model=AttendanceSchema)
def check_in(
    data: CheckInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile linked to this user")
    return crud_attendance.check_in(
        db,
        current_user.employee.id,
        location=data.check_in_location,
        ip=data.check_in_ip,
        source=data.source,
    )


@router.post("/check-out", response_model=AttendanceSchema)
def check_out(
    data: CheckOutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile linked to this user")
    record = crud_attendance.check_out(
        db,
        current_user.employee.id,
        location=data.check_out_location,
        ip=data.check_out_ip,
    )
    if not record:
        raise HTTPException(status_code=400, detail="No check-in found for today")
    return record


@router.get("/today")
def get_today_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile")
    record = crud_attendance.get_today(db, current_user.employee.id)
    return record


# ── Employee Attendance History ───────────────────────────────────────────────

@router.get("/my", response_model=List[AttendanceSchema])
def my_attendance(
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile")
    return crud_attendance.get_employee_attendance(db, current_user.employee.id, from_date, to_date)


@router.get("/employee/{employee_id}", response_model=List[AttendanceSchema])
def employee_attendance(
    employee_id: int,
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("attendance_view")),
):
    return crud_attendance.get_employee_attendance(db, employee_id, from_date, to_date)


@router.get("/summary/monthly")
def monthly_summary(
    employee_id: Optional[int] = Query(None),
    month: int = Query(...),
    year: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emp_id = employee_id
    if not emp_id:
        if not current_user.employee:
            raise HTTPException(status_code=400, detail="No employee profile")
        emp_id = current_user.employee.id
    return crud_attendance.get_monthly_summary(db, emp_id, month, year)


@router.post("/compute/{employee_id}/{work_date}", response_model=AttendanceSchema)
def compute_attendance_day(
    employee_id: int,
    work_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("attendance_manage")),
):
    return crud_attendance.compute_day(db, employee_id, work_date)


# ── Regularization ───────────────────────────────────────────────────────────

@router.post("/regularize", response_model=RegularizationSchema, status_code=201)
def request_regularization(
    data: RegularizationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile")
    reg = AttendanceRegularization(
        attendance_id=data.attendance_id,
        employee_id=current_user.employee.id,
        requested_check_in=data.requested_check_in,
        requested_check_out=data.requested_check_out,
        reason=data.reason,
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


@router.get("/regularize/pending", response_model=List[RegularizationSchema])
def pending_regularizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("attendance_manage")),
):
    return db.query(AttendanceRegularization).filter(
        AttendanceRegularization.status == "Pending"
    ).all()


@router.put("/regularize/{reg_id}/approve")
def approve_regularization(
    reg_id: int,
    data: RegularizationApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("attendance_manage")),
):
    from datetime import datetime, timezone
    reg = db.query(AttendanceRegularization).filter(AttendanceRegularization.id == reg_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Regularization not found")

    reg.status = data.status
    reg.reviewed_by = current_user.id
    reg.reviewed_at = datetime.now(timezone.utc)
    reg.review_remarks = data.review_remarks

    if data.status == "Approved":
        attendance = crud_attendance.get(db, reg.attendance_id)
        if attendance:
            if reg.requested_check_in:
                attendance.check_in = reg.requested_check_in
            if reg.requested_check_out:
                attendance.check_out = reg.requested_check_out
            attendance.is_regularized = True

    db.commit()
    return {"message": f"Regularization {data.status}"}
