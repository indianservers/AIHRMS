from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, RequirePermission
from app.crud import crud_leave
from app.models.user import User
from app.schemas.leave import (
    LeaveTypeCreate, LeaveTypeUpdate, LeaveTypeSchema,
    LeaveBalanceSchema, LeaveRequestCreate, LeaveApprovalRequest, LeaveRequestSchema,
)

router = APIRouter(prefix="/leave", tags=["Leave Management"])


# ── Leave Types ───────────────────────────────────────────────────────────────

@router.get("/types", response_model=List[LeaveTypeSchema])
def list_leave_types(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud_leave.get_all_leave_types(db)


@router.post("/types", response_model=LeaveTypeSchema, status_code=201)
def create_leave_type(
    data: LeaveTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("leave_manage")),
):
    from app.models.leave import LeaveType
    lt = LeaveType(**data.model_dump())
    db.add(lt)
    db.commit()
    db.refresh(lt)
    return lt


@router.put("/types/{type_id}", response_model=LeaveTypeSchema)
def update_leave_type(
    type_id: int,
    data: LeaveTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("leave_manage")),
):
    from app.models.leave import LeaveType
    lt = db.query(LeaveType).filter(LeaveType.id == type_id).first()
    if not lt:
        raise HTTPException(status_code=404, detail="Leave type not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(lt, k, v)
    db.commit()
    db.refresh(lt)
    return lt


@router.delete("/types/{type_id}")
def delete_leave_type(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("leave_manage")),
):
    from app.models.leave import LeaveType
    lt = db.query(LeaveType).filter(LeaveType.id == type_id).first()
    if not lt:
        raise HTTPException(status_code=404, detail="Leave type not found")
    lt.is_active = False
    db.commit()
    return {"message": "Leave type deactivated"}


# ── Leave Balance ─────────────────────────────────────────────────────────────

@router.get("/balance", response_model=List[LeaveBalanceSchema])
def my_leave_balance(
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile")
    import datetime
    yr = year or datetime.date.today().year
    balances = crud_leave.get_employee_leave_balances(db, current_user.employee.id, yr)
    result = []
    for b in balances:
        from decimal import Decimal
        available = b.allocated + b.carried_forward - b.used - b.pending
        result.append({
            "id": b.id,
            "employee_id": b.employee_id,
            "leave_type_id": b.leave_type_id,
            "leave_type": b.leave_type,
            "year": b.year,
            "allocated": b.allocated,
            "used": b.used,
            "pending": b.pending,
            "carried_forward": b.carried_forward,
            "available": available,
        })
    return result


@router.get("/balance/{employee_id}", response_model=List[LeaveBalanceSchema])
def employee_leave_balance(
    employee_id: int,
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("leave_manage")),
):
    import datetime
    yr = year or datetime.date.today().year
    return crud_leave.get_employee_leave_balances(db, employee_id, yr)


@router.post("/balance/allocate")
def allocate_leave(
    employee_id: int,
    leave_type_id: int,
    year: int,
    days: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("leave_manage")),
):
    from decimal import Decimal
    balance = crud_leave.allocate_leave_balance(db, employee_id, leave_type_id, year, Decimal(str(days)))
    return balance


# ── Leave Requests ────────────────────────────────────────────────────────────

@router.post("/apply", response_model=LeaveRequestSchema, status_code=201)
def apply_leave(
    data: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile")
    try:
        return crud_leave.create_leave_request(db, current_user.employee.id, data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my-requests", response_model=List[LeaveRequestSchema])
def my_leave_requests(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile")
    items, _ = crud_leave.get_leave_requests(
        db, employee_id=current_user.employee.id, status=status,
        skip=(page-1)*per_page, limit=per_page
    )
    return items


@router.get("/requests", response_model=List[LeaveRequestSchema])
def all_leave_requests(
    employee_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("leave_approve")),
):
    items, _ = crud_leave.get_leave_requests(
        db, employee_id=employee_id, status=status,
        skip=(page-1)*per_page, limit=per_page
    )
    return items


@router.put("/requests/{request_id}/approve")
def approve_leave(
    request_id: int,
    data: LeaveApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("leave_approve")),
):
    result = crud_leave.approve_leave_request(
        db, request_id, data.status, current_user.id, data.review_remarks
    )
    if not result:
        raise HTTPException(status_code=404, detail="Leave request not found or already processed")
    return {"message": f"Leave request {data.status}"}


@router.put("/requests/{request_id}/cancel")
def cancel_leave(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.leave import LeaveRequest
    req = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if current_user.employee and req.employee_id != current_user.employee.id:
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Not authorized")
    if req.status not in ["Pending"]:
        raise HTTPException(status_code=400, detail="Can only cancel pending requests")
    req.status = "Cancelled"
    db.commit()
    return {"message": "Leave request cancelled"}
