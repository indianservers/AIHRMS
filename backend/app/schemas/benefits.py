from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class BenefitPlanCreate(BaseModel):
    name: str
    plan_type: str
    provider_name: Optional[str] = None
    policy_number: Optional[str] = None
    description: Optional[str] = None
    employer_contribution: Decimal = Decimal("0")
    employee_contribution: Decimal = Decimal("0")
    taxable: bool = False
    payroll_component_code: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    is_active: bool = True


class BenefitPlanSchema(BenefitPlanCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EmployeeBenefitEnrollmentCreate(BaseModel):
    employee_id: int
    benefit_plan_id: int
    coverage_level: str = "Self"
    enrolled_amount: Decimal = Decimal("0")
    employee_contribution: Decimal = Decimal("0")
    employer_contribution: Decimal = Decimal("0")
    start_date: date
    end_date: Optional[date] = None
    remarks: Optional[str] = None


class EmployeeBenefitEnrollmentSchema(EmployeeBenefitEnrollmentCreate):
    id: int
    status: str
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class FlexiBenefitPolicyCreate(BaseModel):
    name: str
    component_code: str
    monthly_limit: Decimal = Decimal("0")
    annual_limit: Decimal = Decimal("0")
    proof_required: bool = True
    taxable_if_unclaimed: bool = True
    carry_forward_allowed: bool = False
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    is_active: bool = True


class FlexiBenefitPolicySchema(FlexiBenefitPolicyCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class EmployeeFlexiBenefitAllocationCreate(BaseModel):
    employee_id: int
    policy_id: int
    financial_year: str
    allocated_amount: Decimal
    claimed_amount: Decimal = Decimal("0")


class EmployeeFlexiBenefitAllocationSchema(EmployeeFlexiBenefitAllocationCreate):
    id: int
    taxable_fallback_amount: Decimal
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class BenefitPayrollDeductionCreate(BaseModel):
    enrollment_id: int
    month: int
    year: int
    payroll_record_id: Optional[int] = None


class BenefitPayrollDeductionSchema(BaseModel):
    id: int
    enrollment_id: int
    employee_id: int
    payroll_record_id: Optional[int] = None
    month: int
    year: int
    employee_amount: Decimal
    employer_amount: Decimal
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
