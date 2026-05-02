from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import RequirePermission, get_db
from app.models.background_verification import (
    BackgroundVerificationCheck,
    BackgroundVerificationConnectorEvent,
    BackgroundVerificationRequest,
    BackgroundVerificationVendor,
)
from app.models.user import User
from app.schemas.background_verification import (
    BackgroundVerificationCheckUpdate,
    BackgroundVerificationConnectorEventSchema,
    BackgroundVerificationConsentUpdate,
    BackgroundVerificationRequestCreate,
    BackgroundVerificationRequestSchema,
    BackgroundVerificationRequestUpdate,
    BackgroundVerificationSubmitResponse,
    BackgroundVerificationVendorCreate,
    BackgroundVerificationVendorSchema,
    BackgroundVerificationWebhookPayload,
)

router = APIRouter(prefix="/background-verification", tags=["Background Verification"])


@router.post("/vendors", response_model=BackgroundVerificationVendorSchema, status_code=201)
def create_vendor(data: BackgroundVerificationVendorCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("recruitment_manage"))):
    vendor = BackgroundVerificationVendor(**data.model_dump())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.get("/vendors", response_model=List[BackgroundVerificationVendorSchema])
def list_vendors(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("recruitment_view"))):
    return db.query(BackgroundVerificationVendor).order_by(BackgroundVerificationVendor.name).all()


@router.post("/requests", response_model=BackgroundVerificationRequestSchema, status_code=201)
def create_request(data: BackgroundVerificationRequestCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("recruitment_manage"))):
    if data.vendor_id and not db.query(BackgroundVerificationVendor).filter(BackgroundVerificationVendor.id == data.vendor_id).first():
        raise HTTPException(status_code=404, detail="Background verification vendor not found")
    payload = data.model_dump(exclude={"checks"})
    request = BackgroundVerificationRequest(**payload, initiated_by=current_user.id)
    db.add(request)
    db.flush()
    for check in data.checks:
        db.add(BackgroundVerificationCheck(request_id=request.id, **check.model_dump()))
    db.commit()
    db.refresh(request)
    return request


@router.put("/requests/{request_id}/consent", response_model=BackgroundVerificationRequestSchema)
def capture_consent(request_id: int, data: BackgroundVerificationConsentUpdate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("recruitment_manage"))):
    request = db.query(BackgroundVerificationRequest).filter(BackgroundVerificationRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Background verification request not found")
    if data.consent_status not in {"Pending", "Captured", "Rejected"}:
        raise HTTPException(status_code=400, detail="consent_status must be Pending, Captured, or Rejected")
    request.consent_status = data.consent_status
    request.consent_url = data.consent_url or request.consent_url
    if data.consent_status == "Captured":
        request.consent_captured_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(request)
    return request


@router.post("/requests/{request_id}/submit", response_model=BackgroundVerificationSubmitResponse)
def submit_to_vendor(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("recruitment_manage"))):
    request = db.query(BackgroundVerificationRequest).filter(BackgroundVerificationRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Background verification request not found")
    if not request.vendor_id:
        raise HTTPException(status_code=400, detail="Vendor is required before submission")
    if request.consent_status != "Captured":
        raise HTTPException(status_code=400, detail="Candidate/employee consent must be captured before submission")
    if not request.checks:
        raise HTTPException(status_code=400, detail="At least one verification check is required")
    now = datetime.now(timezone.utc)
    if not request.vendor_reference:
        provider = (request.vendor.provider_code if request.vendor else None) or "BGV"
        request.vendor_reference = f"{provider}-{request.id:06d}"
    request.status = "Submitted"
    request.vendor_status = "Submitted"
    request.submitted_at = now
    request.last_synced_at = now
    db.add(BackgroundVerificationConnectorEvent(
        request_id=request.id,
        vendor_id=request.vendor_id,
        event_type="verification.submitted",
        vendor_reference=request.vendor_reference,
        payload_json={
            "package_name": request.package_name,
            "checks": [check.check_type for check in request.checks],
            "submitted_by": current_user.id,
        },
    ))
    db.commit()
    db.refresh(request)
    return request


@router.get("/requests", response_model=List[BackgroundVerificationRequestSchema])
def list_requests(
    status: Optional[str] = Query(None),
    candidate_id: Optional[int] = Query(None),
    employee_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("recruitment_view")),
):
    query = db.query(BackgroundVerificationRequest)
    if status:
        query = query.filter(BackgroundVerificationRequest.status == status)
    if candidate_id:
        query = query.filter(BackgroundVerificationRequest.candidate_id == candidate_id)
    if employee_id:
        query = query.filter(BackgroundVerificationRequest.employee_id == employee_id)
    return query.order_by(BackgroundVerificationRequest.id.desc()).all()


@router.put("/requests/{request_id}", response_model=BackgroundVerificationRequestSchema)
def update_request(request_id: int, data: BackgroundVerificationRequestUpdate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("recruitment_manage"))):
    request = db.query(BackgroundVerificationRequest).filter(BackgroundVerificationRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Background verification request not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(request, field, value)
    if data.status.lower() in {"completed", "clear", "red", "amber"}:
        request.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(request)
    return request


@router.put("/checks/{check_id}", response_model=BackgroundVerificationRequestSchema)
def update_check(check_id: int, data: BackgroundVerificationCheckUpdate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("recruitment_manage"))):
    check = db.query(BackgroundVerificationCheck).filter(BackgroundVerificationCheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="Background verification check not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(check, field, value)
    if data.status.lower() in {"completed", "verified"}:
        check.verified_at = datetime.now(timezone.utc)
    request = check.request
    if all(item.status in {"Completed", "Verified"} for item in request.checks):
        request.status = "Completed"
        request.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(request)
    return request


@router.post("/webhooks/{vendor_id}", response_model=BackgroundVerificationRequestSchema)
def ingest_vendor_webhook(vendor_id: int, data: BackgroundVerificationWebhookPayload, db: Session = Depends(get_db)):
    vendor = db.query(BackgroundVerificationVendor).filter(BackgroundVerificationVendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Background verification vendor not found")
    request = db.query(BackgroundVerificationRequest).filter(
        BackgroundVerificationRequest.vendor_id == vendor_id,
        BackgroundVerificationRequest.vendor_reference == data.vendor_reference,
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Background verification request not found for vendor reference")

    payload = data.model_dump()
    db.add(BackgroundVerificationConnectorEvent(
        request_id=request.id,
        vendor_id=vendor_id,
        event_type=data.event_type,
        vendor_reference=data.vendor_reference,
        payload_json=data.raw_payload or payload,
    ))

    if data.status:
        request.status = data.status
    if data.vendor_status:
        request.vendor_status = data.vendor_status
    if data.overall_result:
        request.overall_result = data.overall_result
    if data.report_url:
        request.report_url = data.report_url
    if data.remarks:
        request.remarks = data.remarks
    request.last_synced_at = datetime.now(timezone.utc)

    checks_by_type = {check.check_type.lower(): check for check in request.checks}
    for incoming in data.checks:
        check = checks_by_type.get(incoming.check_type.lower())
        if not check:
            check = BackgroundVerificationCheck(request_id=request.id, check_type=incoming.check_type)
            db.add(check)
            request.checks.append(check)
        for field, value in incoming.model_dump(exclude_unset=True).items():
            setattr(check, field, value)
        if incoming.status.lower() in {"completed", "verified"}:
            check.verified_at = datetime.now(timezone.utc)

    terminal_statuses = {"Completed", "Clear", "Red", "Amber", "Rejected"}
    if request.status in terminal_statuses or data.overall_result in {"Clear", "Red", "Amber"}:
        request.status = "Completed" if request.status in {"Clear", "Red", "Amber"} else request.status
        request.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(request)
    return request


@router.get("/requests/{request_id}/events", response_model=List[BackgroundVerificationConnectorEventSchema])
def list_connector_events(request_id: int, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("recruitment_view"))):
    if not db.query(BackgroundVerificationRequest).filter(BackgroundVerificationRequest.id == request_id).first():
        raise HTTPException(status_code=404, detail="Background verification request not found")
    return db.query(BackgroundVerificationConnectorEvent).filter(
        BackgroundVerificationConnectorEvent.request_id == request_id
    ).order_by(BackgroundVerificationConnectorEvent.id.desc()).all()
