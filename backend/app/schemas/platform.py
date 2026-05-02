from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel


class CustomFieldDefinitionCreate(BaseModel):
    module: str
    section: str = "General"
    field_key: str
    label: str
    field_type: str = "Text"
    options_json: Optional[Any] = None
    validation_json: Optional[Any] = None
    is_required: bool = False
    is_sensitive: bool = False
    visible_to_roles: Optional[str] = None
    editable_by_roles: Optional[str] = None
    display_order: int = 100
    is_active: bool = True


class CustomFieldDefinitionSchema(CustomFieldDefinitionCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CustomFieldValueUpsert(BaseModel):
    definition_id: int
    entity_type: str
    entity_id: int
    value_text: Optional[str] = None
    value_json: Optional[Any] = None


class CustomFieldValueSchema(CustomFieldValueUpsert):
    id: int
    updated_by: Optional[int] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomFormFieldCreate(BaseModel):
    field_definition_id: int
    section: str = "General"
    display_order: int = 100
    is_required_override: Optional[bool] = None
    help_text: Optional[str] = None
    visibility_condition_json: Optional[Any] = None


class CustomFormDefinitionCreate(BaseModel):
    name: str
    code: str
    module: str
    entity_type: str
    description: Optional[str] = None
    trigger_event: Optional[str] = None
    visible_to_roles: Optional[str] = None
    editable_by_roles: Optional[str] = None
    allow_multiple_submissions: bool = False
    workflow_required: bool = False
    is_active: bool = True
    fields: list[CustomFormFieldCreate] = []


class CustomFormFieldSchema(CustomFormFieldCreate):
    id: int
    form_id: int

    class Config:
        from_attributes = True


class CustomFormDefinitionSchema(BaseModel):
    id: int
    name: str
    code: str
    module: str
    entity_type: str
    description: Optional[str] = None
    trigger_event: Optional[str] = None
    visible_to_roles: Optional[str] = None
    editable_by_roles: Optional[str] = None
    allow_multiple_submissions: bool
    workflow_required: bool
    is_active: bool
    created_by: Optional[int] = None
    created_at: datetime
    fields: list[CustomFormFieldSchema] = []

    class Config:
        from_attributes = True


class CustomFormSubmissionCreate(BaseModel):
    form_id: int
    entity_type: str
    entity_id: int
    values_json: dict[str, Any]


class CustomFormSubmissionReview(BaseModel):
    status: str
    review_remarks: Optional[str] = None


class CustomFormSubmissionSchema(CustomFormSubmissionCreate):
    id: int
    status: str
    submitted_by: Optional[int] = None
    submitted_at: datetime
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_remarks: Optional[str] = None

    class Config:
        from_attributes = True


class ReportDefinitionCreate(BaseModel):
    name: str
    code: str
    module: str
    field_catalog_json: Optional[Any] = None
    selected_fields_json: Optional[Any] = None
    filters_json: Optional[Any] = None
    schedule_cron: Optional[str] = None
    export_format: str = "csv"
    visible_to_roles: Optional[str] = None
    is_active: bool = True


class ReportDefinitionSchema(ReportDefinitionCreate):
    id: int
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReportRunSchema(BaseModel):
    id: int
    report_definition_id: int
    status: str
    row_count: int
    file_url: Optional[str] = None
    error_message: Optional[str] = None
    requested_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class IntegrationCredentialCreate(BaseModel):
    provider: str
    credential_name: str
    auth_type: str = "API Key"
    secret_ref: str
    scopes: Optional[str] = None
    status: str = "Active"


class IntegrationCredentialSchema(IntegrationCredentialCreate):
    id: int
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookSubscriptionCreate(BaseModel):
    name: str
    event_type: str
    target_url: str
    secret_ref: Optional[str] = None
    retry_policy_json: Optional[Any] = None
    is_active: bool = True


class WebhookSubscriptionSchema(WebhookSubscriptionCreate):
    id: int
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class IntegrationEventCreate(BaseModel):
    subscription_id: Optional[int] = None
    event_type: str
    payload_json: Optional[Any] = None
    status: str = "Queued"


class IntegrationEventSchema(IntegrationEventCreate):
    id: int
    attempts: int
    last_error: Optional[str] = None
    next_retry_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConsentRecordCreate(BaseModel):
    employee_id: int
    consent_type: str
    status: str = "Granted"
    purpose: Optional[str] = None
    channel: str = "Web"
    evidence_url: Optional[str] = None


class ConsentRecordSchema(ConsentRecordCreate):
    id: int
    captured_by: Optional[int] = None
    captured_at: datetime
    revoked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DataPrivacyRequestCreate(BaseModel):
    employee_id: Optional[int] = None
    request_type: str
    requested_by_email: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None


class DataPrivacyRequestReview(BaseModel):
    status: str
    resolution_notes: Optional[str] = None


class DataPrivacyRequestSchema(DataPrivacyRequestCreate):
    id: int
    status: str
    resolution_notes: Optional[str] = None
    created_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DataRetentionPolicyCreate(BaseModel):
    module: str
    record_type: str
    retention_days: int
    action: str = "Archive"
    legal_basis: Optional[str] = None
    is_active: bool = True


class DataRetentionPolicySchema(DataRetentionPolicyCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LegalHoldCreate(BaseModel):
    name: str
    module: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    reason: Optional[str] = None
    status: str = "Active"


class LegalHoldSchema(LegalHoldCreate):
    id: int
    placed_by: Optional[int] = None
    placed_at: datetime
    released_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MetricDefinitionCreate(BaseModel):
    name: str
    code: str
    module: str
    formula_json: Optional[Any] = None
    owner_role: Optional[str] = None
    refresh_frequency: str = "Daily"
    is_active: bool = True


class MetricDefinitionSchema(MetricDefinitionCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
