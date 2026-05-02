from datetime import date, datetime, timedelta, timezone
from io import StringIO
from typing import List, Optional
import csv
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, RequirePermission
from app.core.masking import mask_employee_detail, mask_employee_list_item
from app.crud.crud_employee import crud_employee
from app.models.user import User
from app.models.employee import Employee, EmployeeDocument, EmployeeChangeRequest
from app.api.v1.notifications import create_notification
from app.schemas.notification import NotificationCreate
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeSchema, EmployeeListSchema,
    EmployeeEducationCreate, EmployeeEducationSchema,
    EmployeeExperienceCreate, EmployeeExperienceSchema,
    EmployeeSkillCreate, EmployeeSkillSchema,
    EmployeeDocumentCreate, EmployeeDocumentSchema, EmployeeDocumentVerificationUpdate,
    EmployeeLifecycleEventCreate, EmployeeLifecycleEventSchema,
    EmployeeChangeRequestCreate, EmployeeChangeRequestReview, EmployeeChangeRequestSchema,
)
from app.schemas.common import PaginatedResponse
import os, shutil
from app.core.config import settings

router = APIRouter(prefix="/employees", tags=["Employees"])


def _parse_date(value: Optional[str], row_number: int, field_name: str):
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"{field_name} must be YYYY-MM-DD on row {row_number}")


@router.get("/", response_model=PaginatedResponse[EmployeeListSchema])
def list_employees(
    search: Optional[str] = Query(None),
    department_id: Optional[int] = Query(None),
    branch_id: Optional[int] = Query(None),
    designation_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    employment_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_view")),
):
    skip = (page - 1) * per_page
    items, total = crud_employee.search(
        db,
        search=search,
        department_id=department_id,
        branch_id=branch_id,
        designation_id=designation_id,
        status=status,
        employment_type=employment_type,
        skip=skip,
        limit=per_page,
    )
    import math
    return PaginatedResponse(
        items=[mask_employee_list_item(item, current_user) for item in items],
        total=total,
        page=page,
        per_page=per_page,
        pages=math.ceil(total / per_page) if total else 0,
    )


@router.post("/", response_model=EmployeeSchema, status_code=status.HTTP_201_CREATED)
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_create")),
):
    if data.employee_id and crud_employee.get_by_employee_id(db, data.employee_id):
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    if data.create_user_account and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admin can create login users")
    return crud_employee.create_with_user(db, obj_in=data)


@router.get("/stats")
def employee_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_view")),
):
    return crud_employee.get_headcount_stats(db)


@router.get("/count")
def employee_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_view")),
):
    total = db.query(func.count(Employee.id)).filter(Employee.deleted_at.is_(None)).scalar() or 0
    active = db.query(func.count(Employee.id)).filter(
        Employee.deleted_at.is_(None),
        Employee.status.in_(["Active", "Probation"]),
    ).scalar() or 0
    return {"total": total, "active": active}


@router.get("/documents/expiring", response_model=List[EmployeeDocumentSchema])
def list_expiring_employee_documents(
    days: int = Query(60, ge=0, le=365),
    department_id: Optional[int] = Query(None),
    document_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_view")),
):
    today = date.today()
    query = db.query(EmployeeDocument).join(Employee).filter(
        Employee.deleted_at.is_(None),
        EmployeeDocument.expiry_date.isnot(None),
        EmployeeDocument.expiry_date <= today + timedelta(days=days),
    )
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if document_type:
        query = query.filter(EmployeeDocument.document_type == document_type)
    return query.order_by(EmployeeDocument.expiry_date.asc()).limit(500).all()


@router.get("/export")
def export_employees(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_export")),
):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "employee_id", "first_name", "last_name", "personal_email", "phone_number",
        "date_of_joining", "employment_type", "status", "work_location",
        "branch_id", "department_id", "designation_id", "reporting_manager_id",
    ])

    query = db.query(Employee).filter(Employee.deleted_at.is_(None))
    if status_filter:
        query = query.filter(Employee.status == status_filter)
    for emp in query.order_by(Employee.employee_id).all():
        writer.writerow([
            emp.employee_id,
            emp.first_name,
            emp.last_name,
            emp.personal_email or "",
            emp.phone_number or "",
            emp.date_of_joining.isoformat() if emp.date_of_joining else "",
            emp.employment_type,
            emp.status,
            emp.work_location,
            emp.branch_id or "",
            emp.department_id or "",
            emp.designation_id or "",
            emp.reporting_manager_id or "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees_export.csv"},
    )


@router.post("/import", status_code=201)
async def import_employees(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_import")),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV import is supported")

    raw = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(StringIO(raw))
    required = {"first_name", "last_name", "date_of_joining"}
    headers = set(reader.fieldnames or [])
    missing = sorted(required - headers)
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing)}")

    created = 0
    errors = []
    seen_employee_ids = set()
    for row_number, row in enumerate(reader, start=2):
        row_errors = []
        first_name = (row.get("first_name") or "").strip()
        last_name = (row.get("last_name") or "").strip()
        employee_id = (row.get("employee_id") or "").strip() or f"EMPIMP{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}{row_number:04d}"
        if not first_name:
            row_errors.append("first_name is required")
        if not last_name:
            row_errors.append("last_name is required")
        if crud_employee.get_by_employee_id(db, employee_id):
            row_errors.append(f"employee_id {employee_id} already exists")
        if employee_id in seen_employee_ids:
            row_errors.append(f"employee_id {employee_id} is duplicated in this import")

        try:
            joining_date = _parse_date(row.get("date_of_joining"), row_number, "date_of_joining")
            confirmation_date = _parse_date(row.get("date_of_confirmation"), row_number, "date_of_confirmation")
        except ValueError as exc:
            row_errors.append(str(exc))
            joining_date = None
            confirmation_date = None

        if not joining_date:
            row_errors.append("date_of_joining is required")

        def optional_int(field: str):
            value = (row.get(field) or "").strip()
            if not value:
                return None
            try:
                return int(value)
            except ValueError:
                row_errors.append(f"{field} must be a number")
                return None

        branch_id = optional_int("branch_id")
        department_id = optional_int("department_id")
        designation_id = optional_int("designation_id")
        reporting_manager_id = optional_int("reporting_manager_id")

        if row_errors:
            errors.append({"row": row_number, "employee_id": employee_id, "errors": row_errors})
            seen_employee_ids.add(employee_id)
            continue

        employee = Employee(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            personal_email=(row.get("personal_email") or "").strip() or None,
            phone_number=(row.get("phone_number") or "").strip() or None,
            date_of_joining=joining_date,
            date_of_confirmation=confirmation_date,
            employment_type=(row.get("employment_type") or "Full-time").strip() or "Full-time",
            status=(row.get("status") or "Active").strip() or "Active",
            work_location=(row.get("work_location") or "Office").strip() or "Office",
            branch_id=branch_id,
            department_id=department_id,
            designation_id=designation_id,
            reporting_manager_id=reporting_manager_id,
        )
        db.add(employee)
        seen_employee_ids.add(employee_id)
        created += 1

    db.commit()
    create_notification(
        db,
        NotificationCreate(
            user_id=current_user.id,
            title="Employee import completed",
            message=f"{created} employees imported. {len(errors)} rows need correction.",
            module="employee",
            event_type="employee_import_completed",
            action_url="/employees",
            priority="high" if errors else "normal",
            channels=["in_app", "email"],
        ),
    )
    return {"created": created, "failed": len(errors), "errors": errors}


@router.get("/me", response_model=EmployeeSchema)
def get_my_employee_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=404, detail="Employee profile not linked")
    emp = crud_employee.get_with_details(db, current_user.employee.id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return mask_employee_detail(emp, current_user)


@router.get("/me/completeness")
def my_profile_completeness(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=404, detail="Employee profile not linked")
    employee = db.query(Employee).filter(
        Employee.id == current_user.employee.id,
        Employee.deleted_at.is_(None),
    ).first()
    fields = {
        "personal_email": employee.personal_email,
        "phone_number": employee.phone_number,
        "date_of_birth": employee.date_of_birth,
        "present_address": employee.present_address,
        "permanent_address": employee.permanent_address,
        "emergency_contact_name": employee.emergency_contact_name,
        "emergency_contact_number": employee.emergency_contact_number,
        "bank_name": employee.bank_name,
        "account_number": employee.account_number,
        "ifsc_code": employee.ifsc_code,
        "pan_number": employee.pan_number,
        "profile_photo_url": employee.profile_photo_url,
    }
    completed = [key for key, value in fields.items() if value]
    missing = [key for key, value in fields.items() if not value]
    percent = round((len(completed) / len(fields)) * 100, 2)
    pending_requests = db.query(EmployeeChangeRequest).filter(
        EmployeeChangeRequest.employee_id == employee.id,
        EmployeeChangeRequest.status == "Pending",
    ).count()
    return {
        "employee_id": employee.id,
        "percent": percent,
        "completed": completed,
        "missing": missing,
        "pending_change_requests": pending_requests,
    }


@router.post("/change-requests", response_model=EmployeeChangeRequestSchema, status_code=201)
def create_employee_change_request(
    data: EmployeeChangeRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_superuser and not any(p.name == "employee_update" for p in (current_user.role.permissions if current_user.role else [])):
        if not current_user.employee or current_user.employee.id != data.employee_id:
            raise HTTPException(status_code=403, detail="Not authorized to request changes for this employee")
    if not db.query(Employee).filter(
        Employee.id == data.employee_id,
        Employee.deleted_at.is_(None),
    ).first():
        raise HTTPException(status_code=404, detail="Employee not found")
    item = EmployeeChangeRequest(**data.model_dump(), requested_by=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/change-requests", response_model=List[EmployeeChangeRequestSchema])
def list_employee_change_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    employee_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(EmployeeChangeRequest)
    role_name = (current_user.role.name if current_user.role else "").lower().replace(" ", "_")
    has_employee_view = current_user.is_superuser or any(p.name == "employee_view" for p in (current_user.role.permissions if current_user.role else []))
    has_employee_update = current_user.is_superuser or any(p.name == "employee_update" for p in (current_user.role.permissions if current_user.role else []))
    if not has_employee_view and not current_user.employee:
        raise HTTPException(status_code=403, detail="Not authorized to view change requests")
    if not has_employee_update:
        if role_name in {"manager", "team_lead", "department_head"} and current_user.employee:
            direct_report_ids = [
                row.id for row in db.query(Employee.id).filter(
                    Employee.reporting_manager_id == current_user.employee.id,
                    Employee.deleted_at.is_(None),
                ).all()
            ]
            allowed_employee_ids = set(direct_report_ids + [current_user.employee.id])
            query = query.filter(EmployeeChangeRequest.employee_id.in_(allowed_employee_ids or {0}))
        elif current_user.employee:
            query = query.filter(EmployeeChangeRequest.employee_id == current_user.employee.id)
        else:
            raise HTTPException(status_code=403, detail="Not authorized to view change requests")
    if status_filter:
        query = query.filter(EmployeeChangeRequest.status == status_filter)
    if employee_id:
        if not has_employee_update and current_user.employee and employee_id != current_user.employee.id:
            if role_name not in {"manager", "team_lead", "department_head"}:
                raise HTTPException(status_code=403, detail="Not authorized to view this employee's change requests")
        query = query.filter(EmployeeChangeRequest.employee_id == employee_id)
    items = query.order_by(EmployeeChangeRequest.id.desc()).limit(300).all()
    employees = {
        emp.id: emp
        for emp in db.query(Employee).filter(
            Employee.id.in_([item.employee_id for item in items] or [0]),
            Employee.deleted_at.is_(None),
        ).all()
    }
    payload = []
    for item in items:
        employee = employees.get(item.employee_id)
        changes = item.field_changes_json or {}
        current_values = {
            field: getattr(employee, field, None)
            for field in changes.keys()
            if employee and hasattr(employee, field)
        }
        payload.append({
            "id": item.id,
            "employee_id": item.employee_id,
            "request_type": item.request_type,
            "effective_date": item.effective_date,
            "field_changes_json": changes,
            "reason": item.reason,
            "status": item.status,
            "requested_by": item.requested_by,
            "reviewed_by": item.reviewed_by,
            "reviewed_at": item.reviewed_at,
            "review_remarks": item.review_remarks,
            "created_at": item.created_at,
            "employee_name": f"{employee.first_name} {employee.last_name}" if employee else None,
            "employee_code": employee.employee_id if employee else None,
            "current_values_json": current_values,
        })
    return payload


@router.put("/change-requests/{request_id}/review", response_model=EmployeeChangeRequestSchema)
def review_employee_change_request(
    request_id: int,
    data: EmployeeChangeRequestReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(EmployeeChangeRequest).filter(EmployeeChangeRequest.id == request_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Change request not found")
    employee = db.query(Employee).filter(
        Employee.id == item.employee_id,
        Employee.deleted_at.is_(None),
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    has_employee_update = any(p.name == "employee_update" for p in (current_user.role.permissions if current_user.role else []))
    is_direct_manager = bool(current_user.employee and employee.reporting_manager_id == current_user.employee.id)
    if not (current_user.is_superuser or has_employee_update or is_direct_manager):
        raise HTTPException(status_code=403, detail="Not authorized to review this change request")
    if item.status != "Pending":
        raise HTTPException(status_code=400, detail="Change request already reviewed")
    if data.status not in {"Approved", "Rejected"}:
        raise HTTPException(status_code=400, detail="Status must be Approved or Rejected")
    item.status = data.status
    item.reviewed_by = current_user.id
    item.reviewed_at = datetime.now(timezone.utc)
    item.review_remarks = data.review_remarks
    if data.status == "Approved" and data.apply_changes:
        allowed_fields = {
            "present_address", "permanent_address", "phone_number", "personal_email",
            "bank_name", "bank_branch", "account_number", "ifsc_code", "pan_number",
            "aadhaar_number", "branch_id", "department_id", "designation_id",
            "business_unit_id", "cost_center_id", "location_id", "grade_band_id",
            "position_id", "reporting_manager_id", "status", "worker_type",
        }
        for field, value in (item.field_changes_json or {}).items():
            if field in allowed_fields and hasattr(employee, field):
                setattr(employee, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{employee_id}", response_model=EmployeeSchema)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_view")),
):
    emp = crud_employee.get_with_details(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return mask_employee_detail(emp, current_user)


@router.put("/{employee_id}", response_model=EmployeeSchema)
def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_update")),
):
    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.deleted_at.is_(None)).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return crud_employee.update(db, db_obj=emp, obj_in=data)


@router.get("/{employee_id}/lifecycle", response_model=List[EmployeeLifecycleEventSchema])
def list_lifecycle_events(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_view")),
):
    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.deleted_at.is_(None)).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return crud_employee.list_lifecycle_events(db, employee_id)


@router.post("/{employee_id}/lifecycle", response_model=EmployeeLifecycleEventSchema, status_code=201)
def add_lifecycle_event(
    employee_id: int,
    data: EmployeeLifecycleEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_update")),
):
    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.deleted_at.is_(None)).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return crud_employee.add_lifecycle_event(
        db,
        employee=emp,
        data=data.model_dump(),
        created_by=current_user.id,
    )


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_delete")),
):
    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.deleted_at.is_(None)).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.status = "Terminated"
    emp.deleted_at = datetime.now(timezone.utc)
    emp.deleted_by = current_user.id
    db.commit()
    return {"message": "Employee terminated"}


# ── Education ────────────────────────────────────────────────────────────────

@router.post("/{employee_id}/education", response_model=EmployeeEducationSchema, status_code=201)
def add_education(
    employee_id: int,
    data: EmployeeEducationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_update")),
):
    return crud_employee.add_education(db, employee_id, data.model_dump())


@router.delete("/{employee_id}/education/{edu_id}")
def delete_education(
    employee_id: int,
    edu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_update")),
):
    from app.models.employee import EmployeeEducation
    edu = db.query(EmployeeEducation).filter_by(id=edu_id, employee_id=employee_id).first()
    if not edu:
        raise HTTPException(status_code=404, detail="Education record not found")
    db.delete(edu)
    db.commit()
    return {"message": "Deleted"}


# ── Experience ───────────────────────────────────────────────────────────────

@router.post("/{employee_id}/experience", response_model=EmployeeExperienceSchema, status_code=201)
def add_experience(
    employee_id: int,
    data: EmployeeExperienceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_update")),
):
    return crud_employee.add_experience(db, employee_id, data.model_dump())


# ── Skills ───────────────────────────────────────────────────────────────────

@router.post("/{employee_id}/skills", response_model=EmployeeSkillSchema, status_code=201)
def add_skill(
    employee_id: int,
    data: EmployeeSkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_update")),
):
    return crud_employee.add_skill(db, employee_id, data.model_dump())


# ── Documents ────────────────────────────────────────────────────────────────

@router.post("/{employee_id}/documents", response_model=EmployeeDocumentSchema, status_code=201)
async def upload_document(
    employee_id: int,
    document_type: str = Form(...),
    document_name: Optional[str] = Form(None),
    document_number: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    can_update = current_user.is_superuser or any(p.name == "employee_update" for p in (current_user.role.permissions if current_user.role else []))
    is_self = bool(current_user.employee and current_user.employee.id == employee_id)
    if not (can_update or is_self):
        raise HTTPException(status_code=403, detail="Not authorized to upload documents for this employee")
    # Validate file type
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in settings.allowed_extensions_list:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}")

    upload_path = os.path.join(settings.UPLOAD_DIR, "employee_docs", str(employee_id))
    os.makedirs(upload_path, exist_ok=True)

    import uuid
    filename = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(upload_path, filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    file_url = f"/uploads/employee_docs/{employee_id}/{filename}"
    try:
        parsed_expiry_date = _parse_date(expiry_date, 0, "expiry_date") if expiry_date else None
    except ValueError:
        raise HTTPException(status_code=400, detail="expiry_date must be YYYY-MM-DD")

    return crud_employee.add_document(db, employee_id, {
        "document_type": document_type,
        "document_name": document_name or file.filename,
        "document_number": document_number,
        "file_url": file_url,
        "expiry_date": parsed_expiry_date,
    })


@router.put("/{employee_id}/documents/{document_id}/verify", response_model=EmployeeDocumentSchema)
def verify_employee_document(
    employee_id: int,
    document_id: int,
    data: EmployeeDocumentVerificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_update")),
):
    if data.verification_status not in {"Pending", "Verified", "Rejected"}:
        raise HTTPException(status_code=400, detail="verification_status must be Pending, Verified, or Rejected")
    document = db.query(EmployeeDocument).filter_by(id=document_id, employee_id=employee_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    document.verification_status = data.verification_status
    document.is_verified = data.verification_status == "Verified"
    document.verified_by = current_user.id
    document.verified_at = datetime.now(timezone.utc)
    document.verifier_name = data.verifier_name
    document.verifier_company = data.verifier_company
    document.verification_notes = data.verification_notes
    db.commit()
    db.refresh(document)
    return document


@router.post("/{employee_id}/photo")
async def upload_photo(
    employee_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    can_update = current_user.is_superuser or any(p.name == "employee_update" for p in (current_user.role.permissions if current_user.role else []))
    is_self = bool(current_user.employee and current_user.employee.id == employee_id)
    if not (can_update or is_self):
        raise HTTPException(status_code=403, detail="Not authorized to upload photo for this employee")
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ["jpg", "jpeg", "png"]:
        raise HTTPException(status_code=400, detail="Only JPG/PNG allowed for photos")

    upload_path = os.path.join(settings.UPLOAD_DIR, "photos")
    os.makedirs(upload_path, exist_ok=True)

    import uuid
    filename = f"{employee_id}_{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(upload_path, filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    emp = crud_employee.get(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    emp.profile_photo_url = f"/uploads/photos/{filename}"
    db.commit()
    return {"url": emp.profile_photo_url}
