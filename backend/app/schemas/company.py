from typing import List, Optional
from pydantic import BaseModel, EmailStr


class CompanyBase(BaseModel):
    name: str
    legal_name: Optional[str] = None
    registration_number: Optional[str] = None
    pan_number: Optional[str] = None
    tan_number: Optional[str] = None
    gstin: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    pincode: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    name: Optional[str] = None


class CompanySchema(CompanyBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class BranchBase(BaseModel):
    name: str
    code: Optional[str] = None
    company_id: int
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BranchBase):
    name: Optional[str] = None
    company_id: Optional[int] = None


class BranchSchema(BranchBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class DepartmentBase(BaseModel):
    name: str
    code: Optional[str] = None
    branch_id: int
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentBase):
    name: Optional[str] = None
    branch_id: Optional[int] = None


class DepartmentSchema(DepartmentBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class DesignationBase(BaseModel):
    name: str
    code: Optional[str] = None
    department_id: int
    grade: Optional[str] = None
    level: int = 1
    description: Optional[str] = None


class DesignationCreate(DesignationBase):
    pass


class DesignationUpdate(DesignationBase):
    name: Optional[str] = None
    department_id: Optional[int] = None


class DesignationSchema(DesignationBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
