from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.deps import RequirePermission, get_db
from app.models.statutory_compliance import (
    Form16Document,
    PayrollLegalEntity,
    StatutoryComplianceEvent,
    StatutoryPortalSubmission,
    TDSReturnFiling,
)
from app.models.user import User
from app.schemas.statutory_compliance import (
    ComplianceEventUpdate,
    FilingSubmit,
    Form16DocumentCreate,
    Form16DocumentSchema,
    Form16Publish,
    PayrollLegalEntityCreate,
    PayrollLegalEntitySchema,
    PortalSubmissionSubmit,
    StatutoryComplianceEventCreate,
    StatutoryComplianceEventSchema,
    StatutoryPortalSubmissionCreate,
    StatutoryPortalSubmissionSchema,
    TDSReturnFilingCreate,
    TDSReturnFilingSchema,
)

router = APIRouter(prefix="/statutory-compliance", tags=["Statutory Compliance"])


@router.post("/legal-entities", response_model=PayrollLegalEntitySchema, status_code=201)
def create_legal_entity(data: PayrollLegalEntityCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_run"))):
    if data.is_default:
        db.query(PayrollLegalEntity).update({PayrollLegalEntity.is_default: False})
    item = PayrollLegalEntity(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/legal-entities", response_model=List[PayrollLegalEntitySchema])
def list_legal_entities(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_view"))):
    return db.query(PayrollLegalEntity).filter(PayrollLegalEntity.is_active == True).order_by(PayrollLegalEntity.legal_name).all()


@router.post("/form16", response_model=Form16DocumentSchema, status_code=201)
def generate_form16(data: Form16DocumentCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_run"))):
    document = Form16Document(
        **data.model_dump(),
        status="Generated",
        generated_by=current_user.id,
        generated_at=datetime.now(timezone.utc),
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.put("/form16/{document_id}/publish", response_model=Form16DocumentSchema)
def publish_form16(document_id: int, data: Form16Publish, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_approve"))):
    document = db.query(Form16Document).filter(Form16Document.id == document_id).first()
    if not document:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Form 16 document not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(document, field, value)
    document.status = "Published"
    document.published_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(document)
    return document


@router.get("/form16", response_model=List[Form16DocumentSchema])
def list_form16(
    financial_year: Optional[str] = Query(None),
    employee_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    query = db.query(Form16Document)
    if financial_year:
        query = query.filter(Form16Document.financial_year == financial_year)
    if employee_id:
        query = query.filter(Form16Document.employee_id == employee_id)
    return query.order_by(Form16Document.id.desc()).all()


@router.post("/tds-filings", response_model=TDSReturnFilingSchema, status_code=201)
def create_tds_filing(data: TDSReturnFilingCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_run"))):
    filing = TDSReturnFiling(**data.model_dump(), status="Draft")
    db.add(filing)
    db.commit()
    db.refresh(filing)
    return filing


@router.put("/tds-filings/{filing_id}/submit", response_model=TDSReturnFilingSchema)
def submit_tds_filing(filing_id: int, data: FilingSubmit, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_approve"))):
    from fastapi import HTTPException
    filing = db.query(TDSReturnFiling).filter(TDSReturnFiling.id == filing_id).first()
    if not filing:
        raise HTTPException(status_code=404, detail="TDS filing not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(filing, field, value)
    filing.status = "Filed"
    filing.filed_at = datetime.now(timezone.utc)
    filing.filed_by = current_user.id
    db.commit()
    db.refresh(filing)
    return filing


@router.post("/portal-submissions", response_model=StatutoryPortalSubmissionSchema, status_code=201)
def create_portal_submission(data: StatutoryPortalSubmissionCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_run"))):
    submission = StatutoryPortalSubmission(**data.model_dump())
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@router.put("/portal-submissions/{submission_id}/submit", response_model=StatutoryPortalSubmissionSchema)
def submit_portal_submission(submission_id: int, data: PortalSubmissionSubmit, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_approve"))):
    from fastapi import HTTPException
    submission = db.query(StatutoryPortalSubmission).filter(StatutoryPortalSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Portal submission not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(submission, field, value)
    submission.status = "Submitted"
    submission.submitted_at = datetime.now(timezone.utc)
    submission.submitted_by = current_user.id
    db.commit()
    db.refresh(submission)
    return submission


@router.post("/calendar", response_model=StatutoryComplianceEventSchema, status_code=201)
def create_calendar_event(data: StatutoryComplianceEventCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_run"))):
    event = StatutoryComplianceEvent(**data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/calendar", response_model=List[StatutoryComplianceEventSchema])
def list_calendar_events(
    status: Optional[str] = Query(None),
    compliance_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    query = db.query(StatutoryComplianceEvent)
    if status:
        query = query.filter(StatutoryComplianceEvent.status == status)
    if compliance_type:
        query = query.filter(StatutoryComplianceEvent.compliance_type == compliance_type)
    return query.order_by(StatutoryComplianceEvent.due_date).all()


@router.put("/calendar/{event_id}", response_model=StatutoryComplianceEventSchema)
def update_calendar_event(event_id: int, data: ComplianceEventUpdate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_run"))):
    from fastapi import HTTPException
    event = db.query(StatutoryComplianceEvent).filter(StatutoryComplianceEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Compliance event not found")
    event.status = data.status
    event.remarks = data.remarks
    if data.status.lower() in {"completed", "filed", "paid"}:
        event.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(event)
    return event
