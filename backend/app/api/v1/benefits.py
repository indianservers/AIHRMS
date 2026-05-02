from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import RequirePermission, get_db
from app.models.benefits import (
    BenefitPayrollDeduction,
    BenefitPlan,
    EmployeeBenefitEnrollment,
    EmployeeFlexiBenefitAllocation,
    FlexiBenefitPolicy,
)
from app.models.user import User
from app.schemas.benefits import (
    BenefitPayrollDeductionCreate,
    BenefitPayrollDeductionSchema,
    BenefitPlanCreate,
    BenefitPlanSchema,
    EmployeeBenefitEnrollmentCreate,
    EmployeeBenefitEnrollmentSchema,
    EmployeeFlexiBenefitAllocationCreate,
    EmployeeFlexiBenefitAllocationSchema,
    FlexiBenefitPolicyCreate,
    FlexiBenefitPolicySchema,
)

router = APIRouter(prefix="/benefits", tags=["Benefits Administration"])


@router.post("/plans", response_model=BenefitPlanSchema, status_code=201)
def create_plan(data: BenefitPlanCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_run"))):
    plan = BenefitPlan(**data.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/plans", response_model=List[BenefitPlanSchema])
def list_plans(plan_type: Optional[str] = Query(None), db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_view"))):
    query = db.query(BenefitPlan).filter(BenefitPlan.is_active == True)
    if plan_type:
        query = query.filter(BenefitPlan.plan_type == plan_type)
    return query.order_by(BenefitPlan.name).all()


@router.post("/enrollments", response_model=EmployeeBenefitEnrollmentSchema, status_code=201)
def create_enrollment(data: EmployeeBenefitEnrollmentCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_run"))):
    plan = db.query(BenefitPlan).filter(BenefitPlan.id == data.benefit_plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Benefit plan not found")
    enrollment = EmployeeBenefitEnrollment(
        **data.model_dump(),
        status="Active",
        approved_by=current_user.id,
        approved_at=datetime.now(timezone.utc),
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("/enrollments", response_model=List[EmployeeBenefitEnrollmentSchema])
def list_enrollments(employee_id: Optional[int] = Query(None), db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_view"))):
    query = db.query(EmployeeBenefitEnrollment)
    if employee_id:
        query = query.filter(EmployeeBenefitEnrollment.employee_id == employee_id)
    return query.order_by(EmployeeBenefitEnrollment.id.desc()).all()


@router.post("/flexi-policies", response_model=FlexiBenefitPolicySchema, status_code=201)
def create_flexi_policy(data: FlexiBenefitPolicyCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_run"))):
    policy = FlexiBenefitPolicy(**data.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.get("/flexi-policies", response_model=List[FlexiBenefitPolicySchema])
def list_flexi_policies(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_view"))):
    return db.query(FlexiBenefitPolicy).filter(FlexiBenefitPolicy.is_active == True).order_by(FlexiBenefitPolicy.name).all()


@router.post("/flexi-allocations", response_model=EmployeeFlexiBenefitAllocationSchema, status_code=201)
def create_flexi_allocation(data: EmployeeFlexiBenefitAllocationCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_run"))):
    policy = db.query(FlexiBenefitPolicy).filter(FlexiBenefitPolicy.id == data.policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Flexi benefit policy not found")
    taxable_fallback = max(data.allocated_amount - data.claimed_amount, 0) if policy.taxable_if_unclaimed else 0
    allocation = EmployeeFlexiBenefitAllocation(**data.model_dump(), taxable_fallback_amount=taxable_fallback)
    db.add(allocation)
    db.commit()
    db.refresh(allocation)
    return allocation


@router.post("/payroll-deductions", response_model=BenefitPayrollDeductionSchema, status_code=201)
def create_payroll_deduction(data: BenefitPayrollDeductionCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_run"))):
    enrollment = db.query(EmployeeBenefitEnrollment).filter(EmployeeBenefitEnrollment.id == data.enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Benefit enrollment not found")
    deduction = BenefitPayrollDeduction(
        enrollment_id=enrollment.id,
        employee_id=enrollment.employee_id,
        payroll_record_id=data.payroll_record_id,
        month=data.month,
        year=data.year,
        employee_amount=enrollment.employee_contribution,
        employer_amount=enrollment.employer_contribution,
        status="Ready",
    )
    db.add(deduction)
    db.commit()
    db.refresh(deduction)
    return deduction
