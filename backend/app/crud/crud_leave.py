from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.leave import LeaveType, LeaveBalance, LeaveRequest


def get_leave_type(db: Session, leave_type_id: int) -> Optional[LeaveType]:
    return db.query(LeaveType).filter(LeaveType.id == leave_type_id).first()


def get_all_leave_types(db: Session) -> List[LeaveType]:
    return db.query(LeaveType).filter(LeaveType.is_active == True).all()


def get_leave_balance(db: Session, employee_id: int, leave_type_id: int, year: int) -> Optional[LeaveBalance]:
    return db.query(LeaveBalance).filter(
        and_(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.leave_type_id == leave_type_id,
            LeaveBalance.year == year,
        )
    ).first()


def get_employee_leave_balances(db: Session, employee_id: int, year: int) -> List[LeaveBalance]:
    return db.query(LeaveBalance).filter(
        and_(LeaveBalance.employee_id == employee_id, LeaveBalance.year == year)
    ).all()


def allocate_leave_balance(
    db: Session, employee_id: int, leave_type_id: int, year: int, days: Decimal
) -> LeaveBalance:
    balance = get_leave_balance(db, employee_id, leave_type_id, year)
    if balance:
        balance.allocated = days
    else:
        balance = LeaveBalance(
            employee_id=employee_id,
            leave_type_id=leave_type_id,
            year=year,
            allocated=days,
        )
        db.add(balance)
    db.commit()
    db.refresh(balance)
    return balance


def calculate_leave_days(from_date: date, to_date: date, is_half_day: bool) -> Decimal:
    if is_half_day:
        return Decimal("0.5")
    delta = (to_date - from_date).days + 1
    return Decimal(str(delta))


def create_leave_request(db: Session, employee_id: int, data: dict) -> LeaveRequest:
    from_date = data["from_date"]
    to_date = data["to_date"]
    days = calculate_leave_days(from_date, to_date, data.get("is_half_day", False))

    # Check balance
    year = from_date.year
    balance = get_leave_balance(db, employee_id, data["leave_type_id"], year)
    if balance:
        available = balance.allocated + balance.carried_forward - balance.used - balance.pending
        if available < days:
            raise ValueError(f"Insufficient leave balance. Available: {available}, Requested: {days}")

    request = LeaveRequest(
        employee_id=employee_id,
        days_count=days,
        **{k: v for k, v in data.items() if k != "days_count"},
    )
    db.add(request)

    # Update pending balance
    if balance:
        balance.pending = balance.pending + days

    db.commit()
    db.refresh(request)
    return request


def approve_leave_request(
    db: Session, request_id: int, status: str, reviewer_id: int, remarks: str = None
) -> Optional[LeaveRequest]:
    from datetime import datetime, timezone
    request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
    if not request or request.status != "Pending":
        return None

    old_status = request.status
    request.status = status
    request.reviewed_by = reviewer_id
    request.reviewed_at = datetime.now(timezone.utc)
    request.review_remarks = remarks

    # Update balance
    year = request.from_date.year
    balance = get_leave_balance(db, request.employee_id, request.leave_type_id, year)
    if balance:
        balance.pending = max(Decimal("0"), balance.pending - request.days_count)
        if status == "Approved":
            balance.used = balance.used + request.days_count

    db.commit()
    db.refresh(request)
    return request


def get_leave_requests(
    db: Session,
    employee_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[LeaveRequest], int]:
    query = db.query(LeaveRequest)
    if employee_id:
        query = query.filter(LeaveRequest.employee_id == employee_id)
    if status:
        query = query.filter(LeaveRequest.status == status)
    total = query.count()
    items = query.order_by(LeaveRequest.applied_at.desc()).offset(skip).limit(limit).all()
    return items, total
