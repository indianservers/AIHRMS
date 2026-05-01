from datetime import date, datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, RequirePermission
from app.crud import crud_payroll
from app.models.user import User
from app.models.payroll import (
    SalaryComponent, SalaryStructure, PayrollRun, PayrollRecord, Reimbursement,
    PayrollExportBatch, PayrollRunAuditLog
)
from app.schemas.payroll import (
    SalaryComponentCreate, SalaryComponentSchema,
    SalaryStructureCreate, SalaryStructureSchema,
    EmployeeSalaryCreate, EmployeeSalarySchema,
    PayrollRunCreate, PayrollRunApproval, PayrollRunSchema,
    PayrollRecordSchema, ReimbursementCreate, ReimbursementSchema,
    PayrollVarianceItemSchema, PayrollExportBatchSchema, PayrollRunAuditLogSchema,
)
from app.schemas.payroll import SalaryComponentCreate as SalaryComponentUpdate

router = APIRouter(prefix="/payroll", tags=["Payroll"])

EXPORT_TYPES = {"pf_ecr", "esi", "pt", "tds_24q", "form_16", "bank_advice", "pay_register"}


def _has_permission(user: User, permission: str) -> bool:
    if user.is_superuser:
        return True
    return permission in {p.name for p in (user.role.permissions if user.role else [])}


def _can_view_other_payslips(user: User) -> bool:
    role_name = user.role.name if user.role else None
    return user.is_superuser or (role_name != "employee" and _has_permission(user, "payroll_view"))


def _locked_period(db: Session, month: int, year: int) -> Optional[PayrollRun]:
    return db.query(PayrollRun).filter(
        PayrollRun.month == month,
        PayrollRun.year == year,
        PayrollRun.status == "Locked",
    ).first()


def _ensure_not_locked_period(db: Session, month: int, year: int, action: str) -> None:
    if _locked_period(db, month, year):
        raise HTTPException(status_code=400, detail=f"Payroll is locked for this period; cannot {action}")


def _ensure_not_locked_for_date(db: Session, value: Optional[date], action: str) -> None:
    if not value:
        value = date.today()
    _ensure_not_locked_period(db, value.month, value.year, action)


def _ensure_no_locked_payroll_exists(db: Session, action: str) -> None:
    if db.query(PayrollRun).filter(PayrollRun.status == "Locked").first():
        raise HTTPException(
            status_code=400,
            detail=f"A payroll period is locked; clone/version setup before you {action}",
        )


def _audit(db: Session, run_id: Optional[int], action: str, user_id: Optional[int], details: Optional[str] = None) -> None:
    db.add(PayrollRunAuditLog(
        payroll_run_id=run_id,
        action=action,
        actor_user_id=user_id,
        details=details,
    ))


# ── Salary Components ─────────────────────────────────────────────────────────

@router.get("/components", response_model=List[SalaryComponentSchema])
def list_components(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    return db.query(SalaryComponent).filter(SalaryComponent.is_active == True).all()


@router.post("/components", response_model=SalaryComponentSchema, status_code=201)
def create_component(
    data: SalaryComponentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_run")),
):
    _ensure_no_locked_payroll_exists(db, "change payroll component masters")
    comp = SalaryComponent(**data.model_dump())
    db.add(comp)
    _audit(db, None, "component_created", current_user.id, data.code)
    db.commit()
    db.refresh(comp)
    return comp


@router.put("/components/{component_id}", response_model=SalaryComponentSchema)
def update_component(
    component_id: int,
    data: SalaryComponentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_run")),
):
    comp = db.query(SalaryComponent).filter(SalaryComponent.id == component_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Salary component not found")
    _ensure_no_locked_payroll_exists(db, "change payroll component masters")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(comp, k, v)
    _audit(db, None, "component_updated", current_user.id, comp.code)
    db.commit()
    db.refresh(comp)
    return comp


@router.delete("/components/{component_id}")
def delete_component(
    component_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_run")),
):
    comp = db.query(SalaryComponent).filter(SalaryComponent.id == component_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Salary component not found")
    _ensure_no_locked_payroll_exists(db, "deactivate payroll component masters")
    comp.is_active = False
    _audit(db, None, "component_deactivated", current_user.id, comp.code)
    db.commit()
    return {"message": "Salary component deactivated"}


# ── Salary Structures ─────────────────────────────────────────────────────────

@router.get("/structures", response_model=List[SalaryStructureSchema])
def list_structures(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    return db.query(SalaryStructure).filter(SalaryStructure.is_active == True).all()


@router.post("/structures", response_model=SalaryStructureSchema, status_code=201)
def create_structure(
    data: SalaryStructureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_run")),
):
    from app.models.payroll import SalaryStructureComponent
    _ensure_no_locked_payroll_exists(db, "change salary structures")
    structure = SalaryStructure(name=data.name, description=data.description, effective_from=data.effective_from)
    db.add(structure)
    db.flush()

    for comp_data in data.components:
        sc = SalaryStructureComponent(
            structure_id=structure.id,
            component_id=comp_data.component_id,
            amount=comp_data.amount,
            percentage=comp_data.percentage,
            order_sequence=comp_data.order_sequence,
        )
        db.add(sc)

    db.commit()
    db.refresh(structure)
    return structure


# ── Employee Salary ───────────────────────────────────────────────────────────

@router.post("/salary", response_model=EmployeeSalarySchema, status_code=201)
def set_employee_salary(
    data: EmployeeSalaryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_run")),
):
    from app.models.payroll import EmployeeSalary
    _ensure_not_locked_for_date(db, data.effective_from, "change salary assignment")

    # Deactivate existing salary
    existing = crud_payroll.get_active_salary(db, data.employee_id)
    if existing:
        existing.is_active = False
        existing.effective_to = data.effective_from

    salary = EmployeeSalary(**data.model_dump())
    db.add(salary)
    _audit(db, None, "salary_assigned", current_user.id, f"employee_id={data.employee_id}")
    db.commit()
    db.refresh(salary)
    return salary


@router.get("/salary/{employee_id}", response_model=List[EmployeeSalarySchema])
def get_employee_salary_history(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    from app.models.payroll import EmployeeSalary
    return db.query(EmployeeSalary).filter(
        EmployeeSalary.employee_id == employee_id
    ).order_by(EmployeeSalary.effective_from.desc()).all()


# ── Payroll Run ───────────────────────────────────────────────────────────────

@router.get("/runs", response_model=List[PayrollRunSchema])
def list_payroll_runs(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    return db.query(PayrollRun).order_by(PayrollRun.year.desc(), PayrollRun.month.desc()).all()


@router.post("/run", response_model=PayrollRunSchema, status_code=201)
def run_payroll(
    data: PayrollRunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_run")),
):
    _ensure_not_locked_period(db, data.month, data.year, "rerun payroll")
    try:
        return crud_payroll.run_payroll(db, data.month, data.year, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/runs/{run_id}", response_model=PayrollRunSchema)
def get_payroll_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    run = db.query(PayrollRun).filter(PayrollRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    return run


@router.put("/runs/{run_id}/approve")
def approve_payroll(
    run_id: int,
    data: PayrollRunApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_approve")),
):
    run = db.query(PayrollRun).filter(PayrollRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    if run.status == "Locked":
        raise HTTPException(status_code=400, detail="Payroll run is already locked")

    if data.action == "approve":
        run.status = "Approved"
        run.approved_by = current_user.id
        run.approved_at = datetime.now(timezone.utc)
        _audit(db, run.id, "approved", current_user.id, data.remarks)
    elif data.action == "lock":
        if run.status != "Approved":
            raise HTTPException(status_code=400, detail="Payroll must be approved before locking")
        run.status = "Locked"
        run.locked_by = current_user.id
        run.locked_at = datetime.now(timezone.utc)
        _audit(db, run.id, "locked", current_user.id, data.remarks)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    run.remarks = data.remarks
    db.commit()
    return {"message": f"Payroll {data.action}d successfully"}


@router.get("/runs/{run_id}/variance", response_model=List[PayrollVarianceItemSchema])
def get_payroll_variance(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    try:
        return crud_payroll.calculate_payroll_variance(db, run_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/runs/{run_id}/exports/{export_type}", response_model=PayrollExportBatchSchema, status_code=201)
def create_payroll_export(
    run_id: int,
    export_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    if export_type not in EXPORT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported payroll export type")
    run = db.query(PayrollRun).filter(PayrollRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    total_records = db.query(PayrollRecord).filter(PayrollRecord.payroll_run_id == run_id).count()
    batch = PayrollExportBatch(
        payroll_run_id=run_id,
        export_type=export_type,
        status="Generated",
        output_file_url=f"/exports/payroll/{run_id}/{export_type}.csv",
        total_records=total_records,
        generated_by=current_user.id,
        remarks="Export stub generated; file writer integration pending.",
    )
    db.add(batch)
    _audit(db, run_id, "export_generated", current_user.id, export_type)
    db.commit()
    db.refresh(batch)
    return batch


@router.get("/runs/{run_id}/audit", response_model=List[PayrollRunAuditLogSchema])
def get_payroll_audit(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    return db.query(PayrollRunAuditLog).filter(
        PayrollRunAuditLog.payroll_run_id == run_id
    ).order_by(PayrollRunAuditLog.id.desc()).all()


@router.get("/runs/{run_id}/records", response_model=List[PayrollRecordSchema])
def get_payroll_records(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    return db.query(PayrollRecord).filter(PayrollRecord.payroll_run_id == run_id).all()


@router.get("/payslip")
def get_payslip(
    month: int = Query(...),
    year: int = Query(...),
    employee_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    emp_id = employee_id
    if not emp_id:
        if not current_user.employee:
            raise HTTPException(status_code=400, detail="No employee profile")
        emp_id = current_user.employee.id
    elif not _can_view_other_payslips(current_user):
        if not current_user.employee or current_user.employee.id != emp_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this payslip")

    record = crud_payroll.get_payslip(db, emp_id, month, year)
    if not record:
        raise HTTPException(status_code=404, detail="Payslip not found for this period")
    return crud_payroll.build_payslip_payload(db, record)


# ── Reimbursements ────────────────────────────────────────────────────────────

@router.post("/reimbursements", response_model=ReimbursementSchema, status_code=201)
def create_reimbursement(
    data: ReimbursementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile")
    _ensure_not_locked_for_date(db, data.date, "create reimbursement")
    reimb = Reimbursement(employee_id=current_user.employee.id, **data.model_dump())
    db.add(reimb)
    db.commit()
    db.refresh(reimb)
    return reimb


@router.get("/reimbursements", response_model=List[ReimbursementSchema])
def list_reimbursements(
    employee_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import and_
    q = db.query(Reimbursement)
    emp_id = employee_id or (current_user.employee.id if current_user.employee else None)
    if emp_id and not current_user.is_superuser:
        q = q.filter(Reimbursement.employee_id == emp_id)
    if status:
        q = q.filter(Reimbursement.status == status)
    return q.order_by(Reimbursement.id.desc()).all()
