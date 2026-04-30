from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, RequirePermission
from app.crud import crud_payroll
from app.models.user import User
from app.models.payroll import SalaryComponent, SalaryStructure, PayrollRun, PayrollRecord, Reimbursement
from app.schemas.payroll import (
    SalaryComponentCreate, SalaryComponentSchema,
    SalaryStructureCreate, SalaryStructureSchema,
    EmployeeSalaryCreate, EmployeeSalarySchema,
    PayrollRunCreate, PayrollRunApproval, PayrollRunSchema,
    PayrollRecordSchema, ReimbursementCreate, ReimbursementSchema,
)
from app.schemas.payroll import SalaryComponentCreate as SalaryComponentUpdate

router = APIRouter(prefix="/payroll", tags=["Payroll"])


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
    comp = SalaryComponent(**data.model_dump())
    db.add(comp)
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
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(comp, k, v)
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
    comp.is_active = False
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
    from datetime import date

    # Deactivate existing salary
    existing = crud_payroll.get_active_salary(db, data.employee_id)
    if existing:
        existing.is_active = False
        existing.effective_to = data.effective_from

    salary = EmployeeSalary(**data.model_dump())
    db.add(salary)
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
    from datetime import datetime, timezone
    run = db.query(PayrollRun).filter(PayrollRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")

    if data.action == "approve":
        run.status = "Approved"
        run.approved_by = current_user.id
        run.approved_at = datetime.now(timezone.utc)
    elif data.action == "lock":
        if run.status != "Approved":
            raise HTTPException(status_code=400, detail="Payroll must be approved before locking")
        run.status = "Locked"
        run.locked_by = current_user.id
        run.locked_at = datetime.now(timezone.utc)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    run.remarks = data.remarks
    db.commit()
    return {"message": f"Payroll {data.action}d successfully"}


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

    record = crud_payroll.get_payslip(db, emp_id, month, year)
    if not record:
        raise HTTPException(status_code=404, detail="Payslip not found for this period")
    return record


# ── Reimbursements ────────────────────────────────────────────────────────────

@router.post("/reimbursements", response_model=ReimbursementSchema, status_code=201)
def create_reimbursement(
    data: ReimbursementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile")
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
