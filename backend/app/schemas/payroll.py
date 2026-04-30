from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel


class SalaryComponentBase(BaseModel):
    name: str
    code: str
    component_type: str
    calculation_type: str = "Fixed"
    amount: Decimal = Decimal("0")
    percentage_of: Optional[str] = None
    is_taxable: bool = True
    is_pf_applicable: bool = False
    is_esi_applicable: bool = False
    description: Optional[str] = None


class SalaryComponentCreate(SalaryComponentBase):
    pass


class SalaryComponentSchema(SalaryComponentBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class SalaryStructureComponentInput(BaseModel):
    component_id: int
    amount: Optional[Decimal] = None
    percentage: Optional[Decimal] = None
    order_sequence: int = 1


class SalaryStructureCreate(BaseModel):
    name: str
    description: Optional[str] = None
    effective_from: Optional[date] = None
    components: List[SalaryStructureComponentInput] = []


class SalaryStructureSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    effective_from: Optional[date] = None
    is_active: bool
    components: List[dict] = []

    class Config:
        from_attributes = True


class EmployeeSalaryCreate(BaseModel):
    employee_id: int
    structure_id: Optional[int] = None
    ctc: Decimal
    basic: Optional[Decimal] = None
    hra: Optional[Decimal] = None
    effective_from: date


class EmployeeSalarySchema(BaseModel):
    id: int
    employee_id: int
    structure_id: Optional[int] = None
    ctc: Decimal
    basic: Optional[Decimal] = None
    hra: Optional[Decimal] = None
    effective_from: date
    effective_to: Optional[date] = None
    is_active: bool

    class Config:
        from_attributes = True


class PayrollRunCreate(BaseModel):
    month: int
    year: int


class PayrollRunApproval(BaseModel):
    action: str  # approve, lock
    remarks: Optional[str] = None


class PayrollRunSchema(BaseModel):
    id: int
    month: int
    year: int
    run_date: Optional[date] = None
    status: str
    total_gross: Decimal
    total_deductions: Decimal
    total_net: Decimal
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class PayrollRecordSchema(BaseModel):
    id: int
    payroll_run_id: int
    employee_id: int
    working_days: Optional[int] = None
    present_days: Optional[Decimal] = None
    lop_days: Decimal = Decimal("0")
    paid_days: Optional[Decimal] = None
    basic: Decimal
    hra: Decimal
    gross_salary: Decimal
    total_deductions: Decimal
    net_salary: Decimal
    is_anomaly: bool
    anomaly_reason: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class ReimbursementCreate(BaseModel):
    category: Optional[str] = None
    amount: Decimal
    date: Optional[date] = None
    description: Optional[str] = None
    receipt_url: Optional[str] = None


class ReimbursementSchema(BaseModel):
    id: int
    employee_id: int
    category: Optional[str] = None
    amount: Decimal
    date: Optional[date] = None
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    status: str

    class Config:
        from_attributes = True
