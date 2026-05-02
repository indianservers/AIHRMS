from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
import csv
import io
from app.core.deps import get_db, RequirePermission
from app.models.user import User
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.leave import LeaveRequest
from app.models.payroll import PayrollRecord, PayrollRun
from app.models.recruitment import Candidate, Job
from app.models.timesheet import Project, Timesheet
from app.models.platform import ReportDefinition, ReportRun
from app.schemas.platform import ReportDefinitionCreate, ReportDefinitionSchema, ReportRunSchema

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])


REPORT_FIELD_CATALOG = {
    "employees": ["id", "employee_code", "first_name", "last_name", "department_id", "designation_id", "status", "date_of_joining"],
    "attendance": ["employee_id", "attendance_date", "status", "total_hours", "late_minutes", "overtime_hours", "source"],
    "payroll": ["employee_id", "payroll_run_id", "gross_salary", "total_deductions", "net_salary"],
    "recruitment": ["id", "job_id", "first_name", "last_name", "email", "status", "source"],
}


@router.get("/field-catalog")
def report_field_catalog(
    module: Optional[str] = Query(None),
    current_user: User = Depends(RequirePermission("reports_view")),
):
    if module:
        return {"module": module, "fields": REPORT_FIELD_CATALOG.get(module, [])}
    return REPORT_FIELD_CATALOG


@router.post("/definitions", response_model=ReportDefinitionSchema, status_code=201)
def create_report_definition(
    data: ReportDefinitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("reports_manage")),
):
    if data.module not in REPORT_FIELD_CATALOG:
        return_fields = ", ".join(sorted(REPORT_FIELD_CATALOG))
        raise HTTPException(status_code=400, detail=f"Unsupported report module. Choose one of: {return_fields}")
    report = ReportDefinition(**data.model_dump(), created_by=current_user.id)
    if not report.field_catalog_json:
        report.field_catalog_json = REPORT_FIELD_CATALOG[data.module]
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/definitions", response_model=List[ReportDefinitionSchema])
def list_report_definitions(
    module: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("reports_view")),
):
    query = db.query(ReportDefinition).filter(ReportDefinition.is_active == True)
    if module:
        query = query.filter(ReportDefinition.module == module)
    return query.order_by(ReportDefinition.name).all()


@router.post("/definitions/{definition_id}/run", response_model=ReportRunSchema, status_code=201)
def run_report_definition(
    definition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("reports_view")),
):
    definition = db.query(ReportDefinition).filter(ReportDefinition.id == definition_id, ReportDefinition.is_active == True).first()
    if not definition:
        raise HTTPException(status_code=404, detail="Report definition not found")
    row_count = 0
    if definition.module == "employees":
        row_count = db.query(func.count(Employee.id)).scalar() or 0
    elif definition.module == "attendance":
        row_count = db.query(func.count(Attendance.id)).scalar() or 0
    elif definition.module == "payroll":
        row_count = db.query(func.count(PayrollRecord.id)).scalar() or 0
    elif definition.module == "recruitment":
        row_count = db.query(func.count(Candidate.id)).scalar() or 0
    run = ReportRun(
        report_definition_id=definition.id,
        status="Completed",
        row_count=row_count,
        file_url=f"/uploads/reports/{definition.code}.{definition.export_format}",
        requested_by=current_user.id,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


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


@router.get("/project-utilization")
def project_utilization_report(
    from_date: date = Query(...),
    to_date: date = Query(...),
    project_id: Optional[int] = Query(None),
    export: Optional[str] = Query(None, pattern="^(csv)?$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("reports_view")),
):
    query = (
        db.query(
            Project.id,
            Project.code,
            Project.name,
            Project.client_name,
            func.coalesce(func.sum(Timesheet.total_hours), 0).label("total_hours"),
            func.coalesce(func.sum(Timesheet.billable_hours), 0).label("billable_hours"),
            func.coalesce(func.sum(Timesheet.non_billable_hours), 0).label("non_billable_hours"),
        )
        .outerjoin(Timesheet, Timesheet.project_id == Project.id)
        .filter((Timesheet.id.is_(None)) | ((Timesheet.period_start <= to_date) & (Timesheet.period_end >= from_date)))
        .group_by(Project.id, Project.code, Project.name, Project.client_name)
    )
    if project_id:
        query = query.filter(Project.id == project_id)
    rows = query.order_by(Project.name).all()
    result = []
    for row in rows:
        total = float(row.total_hours or 0)
        billable = float(row.billable_hours or 0)
        result.append({
            "project_id": row.id,
            "project_code": row.code,
            "project_name": row.name,
            "client_name": row.client_name,
            "total_hours": total,
            "billable_hours": billable,
            "non_billable_hours": float(row.non_billable_hours or 0),
            "billable_utilization_percent": round((billable / total * 100) if total else 0, 2),
        })
    if export == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(
            buffer,
            fieldnames=[
                "project_id",
                "project_code",
                "project_name",
                "client_name",
                "total_hours",
                "billable_hours",
                "non_billable_hours",
                "billable_utilization_percent",
            ],
        )
        writer.writeheader()
        writer.writerows(result)
        return Response(
            content=buffer.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=project_utilization.csv"},
        )
    return result
