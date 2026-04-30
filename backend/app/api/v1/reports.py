from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.core.deps import get_db, RequirePermission
from app.models.user import User
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave import LeaveRequest
from app.models.payroll import PayrollRecord, PayrollRun
from app.models.recruitment import Candidate, Job

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])


@router.get("/dashboard")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("reports_view")),
):
    total_employees = db.query(func.count(Employee.id)).scalar()
    active_employees = db.query(func.count(Employee.id)).filter(Employee.status == "Active").scalar()
    today = date.today()

    present_today = db.query(func.count(Attendance.id)).filter(
        Attendance.attendance_date == today,
        Attendance.status == "Present",
    ).scalar()

    pending_leaves = db.query(func.count(LeaveRequest.id)).filter(
        LeaveRequest.status == "Pending"
    ).scalar()

    open_positions = db.query(func.count(Job.id)).filter(Job.status == "Open").scalar()
    total_candidates = db.query(func.count(Candidate.id)).scalar()

    return {
        "headcount": {
            "total": total_employees,
            "active": active_employees,
            "on_leave": total_employees - active_employees,
        },
        "attendance": {
            "present_today": present_today,
            "absent_today": active_employees - present_today,
        },
        "leaves": {
            "pending_approvals": pending_leaves,
        },
        "recruitment": {
            "open_positions": open_positions,
            "total_candidates": total_candidates,
        },
    }


@router.get("/headcount-by-department")
def headcount_by_department(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("reports_view")),
):
    from app.models.company import Department
    result = (
        db.query(Department.name, func.count(Employee.id).label("count"))
        .outerjoin(Employee, Employee.department_id == Department.id)
        .group_by(Department.id, Department.name)
        .all()
    )
    return [{"department": r[0], "count": r[1]} for r in result]


@router.get("/attendance-trend")
def attendance_trend(
    month: int = Query(...),
    year: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("reports_view")),
):
    result = (
        db.query(
            Attendance.attendance_date,
            Attendance.status,
            func.count(Attendance.id).label("count"),
        )
        .filter(
            extract("month", Attendance.attendance_date) == month,
            extract("year", Attendance.attendance_date) == year,
        )
        .group_by(Attendance.attendance_date, Attendance.status)
        .order_by(Attendance.attendance_date)
        .all()
    )
    return [{"date": str(r[0]), "status": r[1], "count": r[2]} for r in result]


@router.get("/leave-trend")
def leave_trend(
    year: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("reports_view")),
):
    result = (
        db.query(
            extract("month", LeaveRequest.from_date).label("month"),
            func.count(LeaveRequest.id).label("count"),
            LeaveRequest.status,
        )
        .filter(extract("year", LeaveRequest.from_date) == year)
        .group_by("month", LeaveRequest.status)
        .order_by("month")
        .all()
    )
    return [{"month": int(r[0]), "count": r[1], "status": r[2]} for r in result]


@router.get("/payroll-summary")
def payroll_summary(
    year: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    result = (
        db.query(
            PayrollRun.month,
            PayrollRun.total_gross,
            PayrollRun.total_deductions,
            PayrollRun.total_net,
            PayrollRun.status,
        )
        .filter(PayrollRun.year == year)
        .order_by(PayrollRun.month)
        .all()
    )
    return [
        {"month": r[0], "gross": float(r[1] or 0), "deductions": float(r[2] or 0),
         "net": float(r[3] or 0), "status": r[4]}
        for r in result
    ]


@router.get("/employee-turnover")
def turnover_report(
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("reports_view")),
):
    resigned = db.query(func.count(Employee.id)).filter(
        Employee.status.in_(["Resigned", "Terminated"]),
        Employee.date_of_exit >= from_date,
        Employee.date_of_exit <= to_date,
    ).scalar()
    joined = db.query(func.count(Employee.id)).filter(
        Employee.date_of_joining >= from_date,
        Employee.date_of_joining <= to_date,
    ).scalar()
    total = db.query(func.count(Employee.id)).filter(Employee.status == "Active").scalar()
    turnover_rate = round((resigned / total * 100) if total > 0 else 0, 2)
    return {
        "period": {"from": str(from_date), "to": str(to_date)},
        "joined": joined,
        "resigned": resigned,
        "turnover_rate": turnover_rate,
        "total_active": total,
    }


@router.get("/recruitment-funnel")
def recruitment_funnel(
    job_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("recruitment_view")),
):
    q = db.query(Candidate.status, func.count(Candidate.id).label("count"))
    if job_id:
        q = q.filter(Candidate.job_id == job_id)
    result = q.group_by(Candidate.status).all()
    return [{"status": r[0], "count": r[1]} for r in result]
