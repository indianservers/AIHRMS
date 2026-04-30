from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DocumentTemplateCreate(BaseModel):
    name: str
    template_type: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[str] = None
    is_active: bool = True


class DocumentTemplateSchema(DocumentTemplateCreate):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class CompanyPolicyCreate(BaseModel):
    title: str
    category: Optional[str] = None
    content: Optional[str] = None
    document_url: Optional[str] = None
    version: str = "1.0"
    effective_date: Optional[datetime] = None
    is_published: bool = False
    require_acknowledgement: bool = False


class CompanyPolicySchema(CompanyPolicyCreate):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class GeneratedDocumentCreate(BaseModel):
    template_id: Optional[int] = None
    employee_id: int
    document_type: Optional[str] = None
    document_name: str
    file_url: Optional[str] = None


class GeneratedDocumentSchema(GeneratedDocumentCreate):
    id: int
    is_signed: bool = False
    signed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
