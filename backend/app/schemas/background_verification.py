from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional
from pydantic import BaseModel, model_validator


class BackgroundVerificationVendorCreate(BaseModel):
    name: str
    contact_email: Optional[str] = None
    provider_code: Optional[str] = None
    api_base_url: Optional[str] = None
    api_key_ref: Optional[str] = None
    webhook_secret_ref: Optional[str] = None
    supports_api_submission: str = "No"
    status: str = "Active"


class BackgroundVerificationVendorSchema(BackgroundVerificationVendorCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BackgroundVerificationCheckCreate(BaseModel):
    check_type: str
    document_url: Optional[str] = None
    remarks: Optional[str] = None


class BackgroundVerificationRequestCreate(BaseModel):
    vendor_id: Optional[int] = None
    candidate_id: Optional[int] = None
    employee_id: Optional[int] = None
    package_name: str
    expected_completion_date: Optional[date] = None
    vendor_reference: Optional[str] = None
    consent_url: Optional[str] = None
    remarks: Optional[str] = None
    checks: List[BackgroundVerificationCheckCreate] = []

    @model_validator(mode="after")
    def require_candidate_or_employee(self):
        if not self.candidate_id and not self.employee_id:
            raise ValueError("candidate_id or employee_id is required")
        return self


class BackgroundVerificationCheckUpdate(BaseModel):
    status: str
    result: Optional[str] = None
    score: Optional[Decimal] = None
    document_url: Optional[str] = None
    verified_by: Optional[str] = None
    remarks: Optional[str] = None


class BackgroundVerificationRequestUpdate(BaseModel):
    status: str
    vendor_status: Optional[str] = None
    overall_result: Optional[str] = None
    report_url: Optional[str] = None
    remarks: Optional[str] = None


class BackgroundVerificationConsentUpdate(BaseModel):
    consent_url: Optional[str] = None
    consent_status: str = "Captured"


class BackgroundVerificationSubmitResponse(BaseModel):
    id: int
    status: str
    vendor_reference: str
    submitted_at: datetime

    class Config:
        from_attributes = True


class BackgroundVerificationWebhookCheck(BackgroundVerificationCheckUpdate):
    check_type: str


class BackgroundVerificationWebhookPayload(BaseModel):
    vendor_reference: str
    event_type: str = "verification.updated"
    status: Optional[str] = None
    vendor_status: Optional[str] = None
    overall_result: Optional[str] = None
    report_url: Optional[str] = None
    remarks: Optional[str] = None
    checks: List[BackgroundVerificationWebhookCheck] = []
    raw_payload: Optional[dict[str, Any]] = None


class BackgroundVerificationConnectorEventSchema(BaseModel):
    id: int
    request_id: int
    vendor_id: Optional[int] = None
    event_type: str
    vendor_reference: Optional[str] = None
    payload_json: Any
    processing_status: str
    error_message: Optional[str] = None
    received_at: datetime

    class Config:
        from_attributes = True


class BackgroundVerificationCheckSchema(BaseModel):
    id: int
    request_id: int
    check_type: str
    status: str
    result: Optional[str] = None
    score: Optional[Decimal] = None
    document_url: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    remarks: Optional[str] = None

    class Config:
        from_attributes = True


class BackgroundVerificationRequestSchema(BaseModel):
    id: int
    vendor_id: Optional[int] = None
    candidate_id: Optional[int] = None
    employee_id: Optional[int] = None
    package_name: str
    status: str
    vendor_status: Optional[str] = None
    initiated_by: Optional[int] = None
    initiated_at: datetime
    consent_status: str
    consent_captured_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    last_synced_at: Optional[datetime] = None
    expected_completion_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    overall_result: Optional[str] = None
    vendor_reference: Optional[str] = None
    report_url: Optional[str] = None
    consent_url: Optional[str] = None
    remarks: Optional[str] = None
    checks: List[BackgroundVerificationCheckSchema] = []

    class Config:
        from_attributes = True
