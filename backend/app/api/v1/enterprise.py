from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import RequirePermission, get_db
from app.models.platform import (
    ConsentRecord, DataPrivacyRequest, DataRetentionPolicy, IntegrationCredential,
    IntegrationEvent, LegalHold, MetricDefinition, WebhookSubscription,
)
from app.models.user import User
from app.schemas.platform import (
    ConsentRecordCreate, ConsentRecordSchema, DataPrivacyRequestCreate,
    DataPrivacyRequestReview, DataPrivacyRequestSchema, DataRetentionPolicyCreate,
    DataRetentionPolicySchema, IntegrationCredentialCreate, IntegrationCredentialSchema,
    IntegrationEventCreate, IntegrationEventSchema, LegalHoldCreate, LegalHoldSchema,
    MetricDefinitionCreate, MetricDefinitionSchema, WebhookSubscriptionCreate,
    WebhookSubscriptionSchema,
)

router = APIRouter(prefix="/enterprise", tags=["Enterprise Platform"])


@router.post("/integration-credentials", response_model=IntegrationCredentialSchema, status_code=201)
def create_integration_credential(data: IntegrationCredentialCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_manage"))):
    item = IntegrationCredential(**data.model_dump(), created_by=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/integration-credentials", response_model=List[IntegrationCredentialSchema])
def list_integration_credentials(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_view"))):
    return db.query(IntegrationCredential).order_by(IntegrationCredential.id.desc()).all()


@router.post("/webhooks", response_model=WebhookSubscriptionSchema, status_code=201)
def create_webhook_subscription(data: WebhookSubscriptionCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_manage"))):
    item = WebhookSubscription(**data.model_dump(), created_by=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/webhooks", response_model=List[WebhookSubscriptionSchema])
def list_webhook_subscriptions(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_view"))):
    return db.query(WebhookSubscription).order_by(WebhookSubscription.id.desc()).all()


@router.post("/integration-events", response_model=IntegrationEventSchema, status_code=201)
def queue_integration_event(data: IntegrationEventCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_manage"))):
    item = IntegrationEvent(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/integration-events", response_model=List[IntegrationEventSchema])
def list_integration_events(
    status: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("settings_view")),
):
    query = db.query(IntegrationEvent)
    if event_type:
        query = query.filter(IntegrationEvent.event_type == event_type)
    if status:
        query = query.filter(IntegrationEvent.status == status)
    return query.order_by(IntegrationEvent.id.desc()).limit(300).all()


@router.post("/consents", response_model=ConsentRecordSchema, status_code=201)
def create_consent(data: ConsentRecordCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_manage"))):
    item = ConsentRecord(**data.model_dump(), captured_by=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/consents/{consent_id}/revoke", response_model=ConsentRecordSchema)
def revoke_consent(consent_id: int, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_manage"))):
    item = db.query(ConsentRecord).filter(ConsentRecord.id == consent_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Consent not found")
    item.status = "Revoked"
    item.revoked_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item


@router.get("/consents", response_model=List[ConsentRecordSchema])
def list_consents(employee_id: Optional[int] = Query(None), db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_view"))):
    query = db.query(ConsentRecord)
    if employee_id:
        query = query.filter(ConsentRecord.employee_id == employee_id)
    return query.order_by(ConsentRecord.id.desc()).limit(300).all()


@router.post("/privacy-requests", response_model=DataPrivacyRequestSchema, status_code=201)
def create_privacy_request(data: DataPrivacyRequestCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_manage"))):
    item = DataPrivacyRequest(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/privacy-requests/{request_id}", response_model=DataPrivacyRequestSchema)
def review_privacy_request(request_id: int, data: DataPrivacyRequestReview, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_manage"))):
    item = db.query(DataPrivacyRequest).filter(DataPrivacyRequest.id == request_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Privacy request not found")
    item.status = data.status
    item.resolution_notes = data.resolution_notes
    if data.status in {"Closed", "Rejected", "Completed"}:
        item.closed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item


@router.get("/privacy-requests", response_model=List[DataPrivacyRequestSchema])
def list_privacy_requests(status: Optional[str] = Query(None), db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_view"))):
    query = db.query(DataPrivacyRequest)
    if status:
        query = query.filter(DataPrivacyRequest.status == status)
    return query.order_by(DataPrivacyRequest.id.desc()).limit(300).all()


@router.post("/retention-policies", response_model=DataRetentionPolicySchema, status_code=201)
def create_retention_policy(data: DataRetentionPolicyCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_manage"))):
    item = DataRetentionPolicy(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/retention-policies", response_model=List[DataRetentionPolicySchema])
def list_retention_policies(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_view"))):
    return db.query(DataRetentionPolicy).order_by(DataRetentionPolicy.module, DataRetentionPolicy.record_type).all()


@router.post("/legal-holds", response_model=LegalHoldSchema, status_code=201)
def create_legal_hold(data: LegalHoldCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_manage"))):
    item = LegalHold(**data.model_dump(), placed_by=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/legal-holds/{hold_id}/release", response_model=LegalHoldSchema)
def release_legal_hold(hold_id: int, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_manage"))):
    item = db.query(LegalHold).filter(LegalHold.id == hold_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Legal hold not found")
    item.status = "Released"
    item.released_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item


@router.get("/legal-holds", response_model=List[LegalHoldSchema])
def list_legal_holds(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("settings_view"))):
    return db.query(LegalHold).order_by(LegalHold.id.desc()).all()


@router.post("/metrics", response_model=MetricDefinitionSchema, status_code=201)
def create_metric_definition(data: MetricDefinitionCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("reports_manage"))):
    item = MetricDefinition(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/metrics", response_model=List[MetricDefinitionSchema])
def list_metric_definitions(module: Optional[str] = Query(None), db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("reports_view"))):
    query = db.query(MetricDefinition).filter(MetricDefinition.is_active == True)
    if module:
        query = query.filter(MetricDefinition.module == module)
    return query.order_by(MetricDefinition.module, MetricDefinition.name).all()
