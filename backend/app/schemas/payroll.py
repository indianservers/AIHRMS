from datetime import date as date_type, datetime
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
    effective_from: Optional[date_type] = None
    components: List[SalaryStructureComponentInput] = []


class SalaryStructureSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    effective_from: Optional[date_type] = None
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
    effective_from: date_type


class EmployeeSalarySchema(BaseModel):
    id: int
    employee_id: int
    structure_id: Optional[int] = None
    ctc: Decimal
    basic: Optional[Decimal] = None
    hra: Optional[Decimal] = None
    effective_from: date_type
    effective_to: Optional[date_type] = None
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
    run_date: Optional[date_type] = None
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


class PayrollVarianceItemSchema(BaseModel):
    id: int
    payroll_run_id: int
    employee_id: int
    previous_payroll_record_id: Optional[int] = None
    current_gross: Decimal
    previous_gross: Decimal
    gross_delta: Decimal
    gross_delta_percent: Decimal
    current_net: Decimal
    previous_net: Decimal
    net_delta: Decimal
    net_delta_percent: Decimal
    severity: str
    reason: Optional[str] = None

    class Config:
        from_attributes = True


class PayrollExportBatchSchema(BaseModel):
    id: int
    payroll_run_id: int
    export_type: str
    status: str
    output_file_url: Optional[str] = None
    total_records: int
    generated_by: Optional[int] = None
    generated_at: Optional[datetime] = None
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class PayrollRunAuditLogSchema(BaseModel):
    id: int
    payroll_run_id: Optional[int] = None
    action: str
    actor_user_id: Optional[int] = None
    details: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReimbursementCreate(BaseModel):
    category: Optional[str] = None
    amount: Decimal
    date: Optional[date_type] = None
    description: Optional[str] = None
    receipt_url: Optional[str] = None


class ReimbursementSchema(BaseModel):
    id: int
    employee_id: int
    category: Optional[str] = None
    amount: Decimal
    date: Optional[date_type] = None
    description: Optional[str] = None
    receipt_url: Optional[str] = None
    status: str

    class Config:
        from_attributes = True
