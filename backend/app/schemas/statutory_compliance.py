from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class PayrollLegalEntityCreate(BaseModel):
    company_id: Optional[int] = None
    legal_name: str
    registered_address: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    pan: Optional[str] = None
    tan: Optional[str] = None
    cin: Optional[str] = None
    gstin: Optional[str] = None
    pf_establishment_code: Optional[str] = None
    esi_employer_code: Optional[str] = None
    pt_registration_number: Optional[str] = None
    lwf_registration_number: Optional[str] = None
    signatory_name: Optional[str] = None
    signatory_designation: Optional[str] = None
    logo_url: Optional[str] = None
    is_default: bool = False
    is_active: bool = True


class PayrollLegalEntitySchema(PayrollLegalEntityCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Form16DocumentCreate(BaseModel):
    legal_entity_id: int
    employee_id: int
    financial_year: str
    taxable_income: Decimal = Decimal("0")
    tax_deducted: Decimal = Decimal("0")
    remarks: Optional[str] = None


class Form16Publish(BaseModel):
    combined_pdf_url: Optional[str] = None
    part_a_url: Optional[str] = None
    part_b_url: Optional[str] = None
    remarks: Optional[str] = None


class Form16DocumentSchema(BaseModel):
    id: int
    legal_entity_id: int
    employee_id: int
    financial_year: str
    part_a_url: Optional[str] = None
    part_b_url: Optional[str] = None
    combined_pdf_url: Optional[str] = None
    taxable_income: Decimal
    tax_deducted: Decimal
    status: str
    generated_by: Optional[int] = None
    generated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class TDSReturnFilingCreate(BaseModel):
    legal_entity_id: int
    financial_year: str
    quarter: str
    form_type: str = "24Q"
    due_date: Optional[date] = None
    total_tax_deducted: Decimal = Decimal("0")
    remarks: Optional[str] = None


class FilingSubmit(BaseModel):
    return_file_url: Optional[str] = None
    fvu_file_url: Optional[str] = None
    acknowledgement_number: Optional[str] = None
    remarks: Optional[str] = None


class TDSReturnFilingSchema(TDSReturnFilingCreate):
    id: int
    status: str
    return_file_url: Optional[str] = None
    fvu_file_url: Optional[str] = None
    acknowledgement_number: Optional[str] = None
    filed_at: Optional[datetime] = None
    filed_by: Optional[int] = None

    class Config:
        from_attributes = True


class StatutoryPortalSubmissionCreate(BaseModel):
    legal_entity_id: int
    portal_type: str
    period_month: int
    period_year: int
    submission_type: str
    due_date: Optional[date] = None
    upload_file_url: Optional[str] = None
    total_amount: Decimal = Decimal("0")
    remarks: Optional[str] = None


class PortalSubmissionSubmit(BaseModel):
    challan_file_url: Optional[str] = None
    acknowledgement_number: Optional[str] = None
    payment_reference: Optional[str] = None
    remarks: Optional[str] = None


class StatutoryPortalSubmissionSchema(StatutoryPortalSubmissionCreate):
    id: int
    status: str
    challan_file_url: Optional[str] = None
    acknowledgement_number: Optional[str] = None
    payment_reference: Optional[str] = None
    submitted_at: Optional[datetime] = None
    submitted_by: Optional[int] = None

    class Config:
        from_attributes = True


class StatutoryComplianceEventCreate(BaseModel):
    legal_entity_id: int
    compliance_type: str
    due_date: date
    period_month: Optional[int] = None
    period_year: Optional[int] = None
    financial_year: Optional[str] = None
    owner_user_id: Optional[int] = None
    source_entity_type: Optional[str] = None
    source_entity_id: Optional[int] = None
    remarks: Optional[str] = None


class ComplianceEventUpdate(BaseModel):
    status: str
    remarks: Optional[str] = None


class StatutoryComplianceEventSchema(StatutoryComplianceEventCreate):
    id: int
    status: str
    alert_status: str
    reminder_sent_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
