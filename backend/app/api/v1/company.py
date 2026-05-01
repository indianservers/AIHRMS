from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.deps import get_db, RequirePermission
from app.models.company import Company, Branch, Department, Designation
from app.models.user import User
from app.schemas.company import (
    CompanyCreate, CompanyUpdate, CompanySchema,
    BranchCreate, BranchUpdate, BranchSchema,
    DepartmentCreate, DepartmentUpdate, DepartmentSchema,
    DesignationCreate, DesignationUpdate, DesignationSchema,
)

router = APIRouter(prefix="/company", tags=["Company Setup"])


def _clean(value: Optional[str]) -> Optional[str]:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _active_company(db: Session, company_id: int) -> Company:
    company = db.query(Company).filter(Company.id == company_id, Company.is_active == True).first()
    if not company:
        raise HTTPException(status_code=404, detail="Active company not found")
    return company


def _active_branch(db: Session, branch_id: int) -> Branch:
    branch = db.query(Branch).filter(Branch.id == branch_id, Branch.is_active == True).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Active branch not found")
    return branch


def _active_department(db: Session, department_id: int) -> Department:
    department = db.query(Department).filter(Department.id == department_id, Department.is_active == True).first()
    if not department:
        raise HTTPException(status_code=404, detail="Active department not found")
    return department


def _ensure_company_unique(db: Session, data: CompanyCreate | CompanyUpdate, exclude_id: Optional[int] = None) -> None:
    checks = {
        "name": _clean(data.name),
        "registration_number": _clean(data.registration_number),
        "pan_number": _clean(data.pan_number),
        "tan_number": _clean(data.tan_number),
        "gstin": _clean(data.gstin),
    }
    for field, value in checks.items():
        if not value:
            continue
        query = db.query(Company).filter(Company.is_active == True, func.lower(getattr(Company, field)) == value.lower())
        if exclude_id:
            query = query.filter(Company.id != exclude_id)
        if query.first():
            raise HTTPException(status_code=409, detail=f"Company {field.replace('_', ' ')} already exists")


def _ensure_branch_unique(db: Session, data: BranchCreate | BranchUpdate, company_id: int, exclude_id: Optional[int] = None) -> None:
    for field in ("name", "code"):
        value = _clean(getattr(data, field))
        if not value:
            continue
        query = db.query(Branch).filter(
            Branch.is_active == True,
            Branch.company_id == company_id,
            func.lower(getattr(Branch, field)) == value.lower(),
        )
        if exclude_id:
            query = query.filter(Branch.id != exclude_id)
        if query.first():
            raise HTTPException(status_code=409, detail=f"Branch {field} already exists for this company")


def _ensure_department_unique(db: Session, data: DepartmentCreate | DepartmentUpdate, branch_id: int, exclude_id: Optional[int] = None) -> None:
    for field in ("name", "code"):
        value = _clean(getattr(data, field))
        if not value:
            continue
        query = db.query(Department).filter(
            Department.is_active == True,
            Department.branch_id == branch_id,
            func.lower(getattr(Department, field)) == value.lower(),
        )
        if exclude_id:
            query = query.filter(Department.id != exclude_id)
        if query.first():
            raise HTTPException(status_code=409, detail=f"Department {field} already exists for this branch")


def _ensure_designation_unique(db: Session, data: DesignationCreate | DesignationUpdate, department_id: int, exclude_id: Optional[int] = None) -> None:
    for field in ("name", "code"):
        value = _clean(getattr(data, field))
        if not value:
            continue
        query = db.query(Designation).filter(
            Designation.is_active == True,
            Designation.department_id == department_id,
            func.lower(getattr(Designation, field)) == value.lower(),
        )
        if exclude_id:
            query = query.filter(Designation.id != exclude_id)
        if query.first():
            raise HTTPException(status_code=409, detail=f"Designation {field} already exists for this department")


# ── Company ──────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[CompanySchema])
def list_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_view")),
):
    return db.query(Company).filter(Company.is_active == True).all()


@router.post("/", response_model=CompanySchema, status_code=status.HTTP_201_CREATED)
def create_company(
    data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_manage")),
):
    _ensure_company_unique(db, data)
    company = Company(**data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


# ── Branch ───────────────────────────────────────────────────────────────────

@router.get("/branches/", response_model=List[BranchSchema])
def list_branches(
    company_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_view")),
):
    q = db.query(Branch).filter(Branch.is_active == True)
    if company_id:
        q = q.filter(Branch.company_id == company_id)
    return q.all()


@router.post("/branches/", response_model=BranchSchema, status_code=201)
def create_branch(
    data: BranchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_manage")),
):
    _active_company(db, data.company_id)
    _ensure_branch_unique(db, data, data.company_id)
    branch = Branch(**data.model_dump())
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


@router.put("/branches/{branch_id}", response_model=BranchSchema)
def update_branch(
    branch_id: int,
    data: BranchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_manage")),
):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    target_company_id = data.company_id if data.company_id is not None else branch.company_id
    _active_company(db, target_company_id)
    _ensure_branch_unique(db, data, target_company_id, exclude_id=branch_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(branch, k, v)
    db.commit()
    db.refresh(branch)
    return branch


@router.delete("/branches/{branch_id}")
def delete_branch(
    branch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_manage")),
):
    branch = db.query(Branch).filter(Branch.id == branch_id).first()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    branch.is_active = False
    db.commit()
    return {"message": "Branch deactivated"}


# ── Department ───────────────────────────────────────────────────────────────

@router.get("/departments/", response_model=List[DepartmentSchema])
def list_departments(
    branch_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_view")),
):
    q = db.query(Department).filter(Department.is_active == True)
    if branch_id:
        q = q.filter(Department.branch_id == branch_id)
    return q.all()


@router.post("/departments/", response_model=DepartmentSchema, status_code=201)
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_manage")),
):
    _active_branch(db, data.branch_id)
    _ensure_department_unique(db, data, data.branch_id)
    dept = Department(**data.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.put("/departments/{dept_id}", response_model=DepartmentSchema)
def update_department(
    dept_id: int,
    data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_manage")),
):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    target_branch_id = data.branch_id if data.branch_id is not None else dept.branch_id
    _active_branch(db, target_branch_id)
    _ensure_department_unique(db, data, target_branch_id, exclude_id=dept_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(dept, k, v)
    db.commit()
    db.refresh(dept)
    return dept


@router.delete("/departments/{dept_id}")
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_manage")),
):
    dept = db.query(Department).filter(Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    dept.is_active = False
    db.commit()
    return {"message": "Department deactivated"}


# ── Designation ──────────────────────────────────────────────────────────────

@router.get("/designations/", response_model=List[DesignationSchema])
def list_designations(
    department_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_view")),
):
    q = db.query(Designation).filter(Designation.is_active == True)
    if department_id:
        q = q.filter(Designation.department_id == department_id)
    return q.all()


@router.post("/designations/", response_model=DesignationSchema, status_code=201)
def create_designation(
    data: DesignationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_manage")),
):
    _active_department(db, data.department_id)
    _ensure_designation_unique(db, data, data.department_id)
    desig = Designation(**data.model_dump())
    db.add(desig)
    db.commit()
    db.refresh(desig)
    return desig


@router.put("/designations/{desig_id}", response_model=DesignationSchema)
def update_designation(
    desig_id: int,
    data: DesignationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_manage")),
):
    desig = db.query(Designation).filter(Designation.id == desig_id).first()
    if not desig:
        raise HTTPException(status_code=404, detail="Designation not found")
    target_department_id = data.department_id if data.department_id is not None else desig.department_id
    _active_department(db, target_department_id)
    _ensure_designation_unique(db, data, target_department_id, exclude_id=desig_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(desig, k, v)
    db.commit()
    db.refresh(desig)
    return desig


@router.delete("/designations/{desig_id}")
def delete_designation(
    desig_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_manage")),
):
    desig = db.query(Designation).filter(Designation.id == desig_id).first()
    if not desig:
        raise HTTPException(status_code=404, detail="Designation not found")
    desig.is_active = False
    db.commit()
    return {"message": "Designation deactivated"}


# Dynamic company routes must stay after the static organization routes above.
@router.get("/{company_id}", response_model=CompanySchema)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_view")),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/{company_id}", response_model=CompanySchema)
def update_company(
    company_id: int,
    data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_manage")),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    _ensure_company_unique(db, data, exclude_id=company_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(company, k, v)
    db.commit()
    db.refresh(company)
    return company


@router.delete("/{company_id}")
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("company_manage")),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    company.is_active = False
    db.commit()
    return {"message": "Company deactivated"}
