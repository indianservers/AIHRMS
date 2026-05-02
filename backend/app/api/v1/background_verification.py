from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import RequirePermission, get_db
from app.models.background_verification import (
    BackgroundVerificationCheck,
    BackgroundVerificationRequest,
    BackgroundVerificationVendor,
)
from app.models.user import User
from app.schemas.background_verification import (
    BackgroundVerificationCheckUpdate,
    BackgroundVerificationRequestCreate,
    BackgroundVerificationRequestSchema,
    BackgroundVerificationRequestUpdate,
    BackgroundVerificationVendorCreate,
    BackgroundVerificationVendorSchema,
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
    payload = data.model_dump(exclude={"checks"})
    request = BackgroundVerificationRequest(**payload, initiated_by=current_user.id)
    db.add(request)
    db.flush()
    for check in data.checks:
        db.add(BackgroundVerificationCheck(request_id=request.id, **check.model_dump()))
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
