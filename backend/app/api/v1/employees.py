from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, RequirePermission
from app.crud.crud_employee import crud_employee
from app.models.user import User
from app.models.employee import EmployeeDocument
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeSchema, EmployeeListSchema,
    EmployeeEducationCreate, EmployeeEducationSchema,
    EmployeeExperienceCreate, EmployeeExperienceSchema,
    EmployeeSkillCreate, EmployeeSkillSchema,
    EmployeeDocumentCreate, EmployeeDocumentSchema,
)
from app.schemas.common import PaginatedResponse
import os, shutil
from app.core.config import settings

router = APIRouter(prefix="/employees", tags=["Employees"])


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
        items=items,
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
    return crud_employee.create_with_user(db, obj_in=data)


@router.get("/stats")
def employee_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_view")),
):
    return crud_employee.get_headcount_stats(db)


@router.get("/{employee_id}", response_model=EmployeeSchema)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_view")),
):
    emp = crud_employee.get_with_details(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.put("/{employee_id}", response_model=EmployeeSchema)
def update_employee(
    employee_id: int,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_update")),
):
    emp = crud_employee.get(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return crud_employee.update(db, db_obj=emp, obj_in=data)


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_delete")),
):
    emp = crud_employee.get(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    emp.status = "Terminated"
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
    document_type: str,
    document_name: Optional[str] = None,
    document_number: Optional[str] = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_update")),
):
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
    return crud_employee.add_document(db, employee_id, {
        "document_type": document_type,
        "document_name": document_name or file.filename,
        "document_number": document_number,
        "file_url": file_url,
    })


@router.post("/{employee_id}/photo")
async def upload_photo(
    employee_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("employee_update")),
):
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
