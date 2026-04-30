from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, RequirePermission
from app.models.document import CompanyPolicy, DocumentTemplate, GeneratedDocument
from app.models.user import User
from app.schemas.document import (
    CompanyPolicyCreate,
    CompanyPolicySchema,
    DocumentTemplateCreate,
    DocumentTemplateSchema,
    GeneratedDocumentCreate,
    GeneratedDocumentSchema,
)

router = APIRouter(prefix="/documents", tags=["Documents & Policies"])


@router.get("/templates", response_model=list[DocumentTemplateSchema])
def list_templates(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("company_view"))):
    return db.query(DocumentTemplate).order_by(DocumentTemplate.created_at.desc()).all()


@router.post("/templates", response_model=DocumentTemplateSchema, status_code=status.HTTP_201_CREATED)
def create_template(data: DocumentTemplateCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("company_manage"))):
    template = DocumentTemplate(**data.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/policies", response_model=list[CompanyPolicySchema])
def list_policies(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("company_view"))):
    return db.query(CompanyPolicy).order_by(CompanyPolicy.updated_at.desc().nullslast(), CompanyPolicy.created_at.desc()).all()


@router.post("/policies", response_model=CompanyPolicySchema, status_code=status.HTTP_201_CREATED)
def create_policy(data: CompanyPolicyCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("company_manage"))):
    policy = CompanyPolicy(**data.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.get("/generated", response_model=list[GeneratedDocumentSchema])
def list_generated(employee_id: int | None = None, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("employee_view"))):
    query = db.query(GeneratedDocument)
    if employee_id:
        query = query.filter(GeneratedDocument.employee_id == employee_id)
    return query.order_by(GeneratedDocument.created_at.desc()).limit(200).all()


@router.post("/generated", response_model=GeneratedDocumentSchema, status_code=status.HTTP_201_CREATED)
def create_generated(data: GeneratedDocumentCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("employee_update"))):
    document = GeneratedDocument(**data.model_dump(), generated_by=current_user.id)
    db.add(document)
    db.commit()
    db.refresh(document)
    return document
