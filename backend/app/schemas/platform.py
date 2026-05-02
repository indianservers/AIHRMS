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
