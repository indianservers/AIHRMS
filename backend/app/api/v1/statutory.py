import csv
import os
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from io import StringIO
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from app.core.config import settings
from app.core.deps import RequirePermission, get_db
from app.models.payroll import (
    PayrollRecord,
    PayrollRun,
    PayrollStatutoryContributionLine,
    StatutoryComplianceCalendar,
    StatutoryFilingSubmission,
)
from app.models.user import User
from app.services.statutory_generators import (
    generate_esi_return,
    generate_pf_ecr,
    generate_pt_challan,
    generate_tds_24q,
)


router = APIRouter(prefix="/statutory", tags=["Statutory"])


class MarkFiledRequest(BaseModel):
    review_remarks: Optional[str] = None


class MarkSubmittedRequest(BaseModel):
    portal_reference: str


def _submission_dir() -> str:
    path = os.path.join(settings.UPLOAD_DIR, "exports", "statutory")
    os.makedirs(path, exist_ok=True)
    return path


def _safe_type(value: str) -> str:
    return value.lower().replace("/", "_").replace(" ", "_")


def _row_count(csv_content: str) -> int:
    return max(len(list(csv.reader(StringIO(csv_content)))) - 1, 0)


def _total_amount(db: Session, payroll_run_id: int, statutory_type: str) -> Decimal:
    kind = statutory_type.upper()
    if kind == "PF_ECR":
        kind = "PF"
    if kind == "ESI":
        return Decimal(
            db.query(func.coalesce(func.sum(PayrollStatutoryContributionLine.employee_amount + PayrollStatutoryContributionLine.employer_amount), 0))
            .join(PayrollRecord, PayrollRecord.id == PayrollStatutoryContributionLine.payroll_record_id)
            .filter(PayrollRecord.payroll_run_id == payroll_run_id, PayrollStatutoryContributionLine.component == "ESI")
            .scalar()
            or 0
        )
    if kind == "PF":
        return Decimal(
            db.query(func.coalesce(func.sum(PayrollStatutoryContributionLine.employee_amount + PayrollStatutoryContributionLine.employer_amount), 0))
            .join(PayrollRecord, PayrollRecord.id == PayrollStatutoryContributionLine.payroll_record_id)
            .filter(PayrollRecord.payroll_run_id == payroll_run_id, PayrollStatutoryContributionLine.component == "PF")
            .scalar()
            or 0
        )
    if kind == "PT":
        return Decimal(db.query(func.coalesce(func.sum(PayrollRecord.professional_tax), 0)).filter(PayrollRecord.payroll_run_id == payroll_run_id).scalar() or 0)
    if kind == "TDS_24Q":
        return Decimal(db.query(func.coalesce(func.sum(PayrollRecord.tds), 0)).filter(PayrollRecord.payroll_run_id == payroll_run_id).scalar() or 0)
    return Decimal("0")


@router.get("/calendar")
def list_calendar(
    statutory_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    query = db.query(StatutoryComplianceCalendar)
    if statutory_type:
        query = query.filter(StatutoryComplianceCalendar.statutory_type == statutory_type)
    if status:
        query = query.filter(StatutoryComplianceCalendar.status == status)
    if year:
        query = query.filter(func.extract("year", StatutoryComplianceCalendar.due_date) == year)
    return query.order_by(StatutoryComplianceCalendar.due_date.asc()).all()


@router.put("/calendar/{calendar_id}/mark-filed")
def mark_calendar_filed(
    calendar_id: int,
    data: MarkFiledRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_approve")),
):
    item = db.query(StatutoryComplianceCalendar).filter(StatutoryComplianceCalendar.id == calendar_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Calendar item not found")
    item.status = "Filed"
    item.filed_at = datetime.now(timezone.utc)
    item.filed_by = current_user.id
    item.remarks = data.review_remarks
    db.commit()
    db.refresh(item)
    return item


@router.post("/generate/{payroll_run_id}/{statutory_type}")
def generate_statutory_file(
    payroll_run_id: int,
    statutory_type: str,
    state: str = Query("Maharashtra"),
    quarter: int = Query(1, ge=1, le=4),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_run")),
):
    run = db.query(PayrollRun).filter(PayrollRun.id == payroll_run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    normalized = statutory_type.lower()
    if normalized == "pf_ecr":
        csv_content, errors = generate_pf_ecr(db, payroll_run_id)
    elif normalized == "esi":
        csv_content, errors = generate_esi_return(db, payroll_run_id)
    elif normalized == "pt":
        csv_content, errors = generate_pt_challan(db, payroll_run_id, state)
    elif normalized == "tds_24q":
        csv_content, errors = generate_tds_24q(db, payroll_run_id, quarter, year or run.year)
    else:
        raise HTTPException(status_code=422, detail="Unsupported statutory type")

    file_name = f"{_safe_type(statutory_type)}_{run.year}_{run.month}_{payroll_run_id}.csv"
    file_path = os.path.join(_submission_dir(), file_name)
    with open(file_path, "w", encoding="utf-8", newline="") as handle:
        handle.write(csv_content)

    submission = StatutoryFilingSubmission(
        statutory_type=statutory_type.upper(),
        payroll_run_id=payroll_run_id,
        file_type="CSV",
        generated_file_path=file_path,
        validation_status="invalid" if errors else "valid",
        validation_errors_json=errors,
        row_count=_row_count(csv_content),
        total_amount=_total_amount(db, payroll_run_id, statutory_type),
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return {
        "submission_id": submission.id,
        "validation_status": submission.validation_status,
        "row_count": submission.row_count,
        "total_amount": float(submission.total_amount or 0),
        "errors": errors,
        "download_url": f"/api/v1/statutory/submissions/{submission.id}/download",
    }


@router.get("/submissions")
def list_submissions(
    payroll_run_id: Optional[int] = Query(None),
    statutory_type: Optional[str] = Query(None),
    validation_status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    query = db.query(StatutoryFilingSubmission).options(joinedload(StatutoryFilingSubmission.payroll_run))
    if payroll_run_id:
        query = query.filter(StatutoryFilingSubmission.payroll_run_id == payroll_run_id)
    if statutory_type:
        query = query.filter(StatutoryFilingSubmission.statutory_type == statutory_type)
    if validation_status:
        query = query.filter(StatutoryFilingSubmission.validation_status == validation_status)
    rows = query.order_by(StatutoryFilingSubmission.created_at.desc()).all()
    return [
        {
            "id": row.id,
            "statutory_type": row.statutory_type,
            "payroll_run_id": row.payroll_run_id,
            "payroll_period": f"{row.payroll_run.month}/{row.payroll_run.year}" if row.payroll_run else "",
            "validation_status": row.validation_status,
            "validation_errors_json": row.validation_errors_json or [],
            "row_count": row.row_count,
            "total_amount": float(row.total_amount or 0),
            "submitted_at": row.submitted_at,
            "portal_reference": row.portal_reference,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/submissions/{submission_id}/download")
def download_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    submission = db.query(StatutoryFilingSubmission).filter(StatutoryFilingSubmission.id == submission_id).first()
    if not submission or not submission.generated_file_path or not os.path.exists(submission.generated_file_path):
        raise HTTPException(status_code=404, detail="Generated file not found")
    file_name = os.path.basename(submission.generated_file_path)
    return FileResponse(submission.generated_file_path, media_type="text/csv", filename=file_name)


@router.put("/submissions/{submission_id}/mark-submitted")
def mark_submission_submitted(
    submission_id: int,
    data: MarkSubmittedRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_approve")),
):
    submission = db.query(StatutoryFilingSubmission).filter(StatutoryFilingSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    submission.validation_status = "submitted"
    submission.submitted_at = datetime.now(timezone.utc)
    submission.submitted_by = current_user.id
    submission.portal_reference = data.portal_reference
    db.commit()
    db.refresh(submission)
    return submission


@router.get("/compliance-summary")
def compliance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("payroll_view")),
):
    today = date.today()
    upcoming_cutoff = today + timedelta(days=30)
    rows = db.query(StatutoryComplianceCalendar).all()
    by_status = {"Pending": 0, "Filed": 0, "Overdue": 0}
    by_type: dict[str, dict[str, int]] = {}
    upcoming = []
    for row in rows:
        effective_status = "Overdue" if row.status != "Filed" and row.due_date and row.due_date < today else row.status
        by_status[effective_status] = by_status.get(effective_status, 0) + 1
        by_type.setdefault(row.statutory_type or "Other", {"Pending": 0, "Filed": 0, "Overdue": 0})
        by_type[row.statutory_type or "Other"][effective_status] = by_type[row.statutory_type or "Other"].get(effective_status, 0) + 1
        if row.status != "Filed" and row.due_date and today <= row.due_date <= upcoming_cutoff:
            upcoming.append(row)
    return {
        "counts": by_status,
        "by_type": by_type,
        "upcoming_count": len(upcoming),
        "upcoming": upcoming,
    }
