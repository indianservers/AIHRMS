from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.leave import LeaveType, LeaveBalance, LeaveBalanceLedger, LeaveRequest


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


def get_available_balance(balance: LeaveBalance) -> Decimal:
    return balance.allocated + balance.carried_forward - balance.used - balance.pending


def add_ledger_entry(
    db: Session,
    *,
    balance: LeaveBalance,
    transaction_type: str,
    amount: Decimal,
    balance_after: Decimal,
    leave_request_id: int | None = None,
    reason: str | None = None,
    created_by: int | None = None,
) -> LeaveBalanceLedger:
    entry = LeaveBalanceLedger(
        employee_id=balance.employee_id,
        leave_type_id=balance.leave_type_id,
        leave_balance_id=balance.id,
        leave_request_id=leave_request_id,
        year=balance.year,
        transaction_type=transaction_type,
        amount=amount,
        balance_after=balance_after,
        reason=reason,
        created_by=created_by,
    )
    db.add(entry)
    return entry


def allocate_leave_balance(
    db: Session, employee_id: int, leave_type_id: int, year: int, days: Decimal
) -> LeaveBalance:
    balance = get_leave_balance(db, employee_id, leave_type_id, year)
    if balance:
        previous_available = get_available_balance(balance)
        balance.allocated = days
    else:
        previous_available = Decimal("0")
        balance = LeaveBalance(
            employee_id=employee_id,
            leave_type_id=leave_type_id,
            year=year,
            allocated=days,
        )
        db.add(balance)
        db.flush()
    add_ledger_entry(
        db,
        balance=balance,
        transaction_type="allocation_adjustment",
        amount=days - previous_available,
        balance_after=get_available_balance(balance),
        reason="Leave balance allocation",
    )
    db.commit()
    db.refresh(balance)
    return balance


def calculate_leave_days(from_date: date, to_date: date, is_half_day: bool) -> Decimal:
    if to_date < from_date:
        raise ValueError("Leave end date cannot be before start date")
    if is_half_day:
        return Decimal("0.5")
    delta = (to_date - from_date).days + 1
    return Decimal(str(delta))


def has_overlapping_leave(
    db: Session,
    employee_id: int,
    from_date: date,
    to_date: date,
    exclude_request_id: int | None = None,
) -> bool:
    query = db.query(LeaveRequest).filter(
        LeaveRequest.employee_id == employee_id,
        LeaveRequest.deleted_at.is_(None),
        LeaveRequest.status.in_(["Pending", "Approved"]),
        LeaveRequest.from_date <= to_date,
        LeaveRequest.to_date >= from_date,
    )
    if exclude_request_id:
        query = query.filter(LeaveRequest.id != exclude_request_id)
    return db.query(query.exists()).scalar()


def create_leave_request(db: Session, employee_id: int, data: dict) -> LeaveRequest:
    from_date = data["from_date"]
    to_date = data["to_date"]
    days = calculate_leave_days(from_date, to_date, data.get("is_half_day", False))

    if has_overlapping_leave(db, employee_id, from_date, to_date):
        raise ValueError("Leave dates overlap an existing pending or approved request")

    # Check balance
    year = from_date.year
    balance = get_leave_balance(db, employee_id, data["leave_type_id"], year)
    if not balance:
        raise ValueError("No leave balance allocated for this leave type and year")

    available = get_available_balance(balance)
    if available < days:
        raise ValueError(f"Insufficient leave balance. Available: {available}, Requested: {days}")

    request = LeaveRequest(
        employee_id=employee_id,
        days_count=days,
        **{k: v for k, v in data.items() if k != "days_count"},
    )
    db.add(request)

    # Update pending balance
    balance.pending = balance.pending + days
    db.flush()
    add_ledger_entry(
        db,
        balance=balance,
        transaction_type="request_pending",
        amount=-days,
        balance_after=get_available_balance(balance),
        leave_request_id=request.id,
        reason="Leave request submitted",
    )

    db.commit()
    db.refresh(request)
    return request


def approve_leave_request(
    db: Session, request_id: int, status: str, reviewer_id: int, remarks: str = None
) -> Optional[LeaveRequest]:
    from datetime import datetime, timezone
    request = db.query(LeaveRequest).filter(
        LeaveRequest.id == request_id,
        LeaveRequest.deleted_at.is_(None),
    ).first()
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
            transaction_type = "request_approved"
            amount = Decimal("0")
            reason = "Leave request approved"
        else:
            transaction_type = "request_rejected"
            amount = request.days_count
            reason = "Leave request rejected"
        add_ledger_entry(
            db,
            balance=balance,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=get_available_balance(balance),
            leave_request_id=request.id,
            reason=reason,
            created_by=reviewer_id,
        )

    db.commit()
    db.refresh(request)
    return request


def cancel_leave_request(db: Session, request_id: int, actor_id: int | None = None) -> Optional[LeaveRequest]:
    request = db.query(LeaveRequest).filter(
        LeaveRequest.id == request_id,
        LeaveRequest.deleted_at.is_(None),
    ).first()
    if not request or request.status != "Pending":
        return None

    request.status = "Cancelled"
    balance = get_leave_balance(db, request.employee_id, request.leave_type_id, request.from_date.year)
    if balance:
        balance.pending = max(Decimal("0"), balance.pending - request.days_count)
        add_ledger_entry(
            db,
            balance=balance,
            transaction_type="request_cancelled",
            amount=request.days_count,
            balance_after=get_available_balance(balance),
            leave_request_id=request.id,
            reason="Leave request cancelled",
            created_by=actor_id,
        )
    db.commit()
    db.refresh(request)
    return request


def get_leave_ledger(
    db: Session,
    *,
    employee_id: int,
    leave_type_id: Optional[int] = None,
    year: Optional[int] = None,
) -> List[LeaveBalanceLedger]:
    query = db.query(LeaveBalanceLedger).filter(LeaveBalanceLedger.employee_id == employee_id)
    if leave_type_id:
        query = query.filter(LeaveBalanceLedger.leave_type_id == leave_type_id)
    if year:
        query = query.filter(LeaveBalanceLedger.year == year)
    return query.order_by(LeaveBalanceLedger.created_at.desc(), LeaveBalanceLedger.id.desc()).all()


def get_leave_requests(
    db: Session,
    employee_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[LeaveRequest], int]:
    query = db.query(LeaveRequest).filter(LeaveRequest.deleted_at.is_(None))
    if employee_id:
        query = query.filter(LeaveRequest.employee_id == employee_id)
    if status:
        query = query.filter(LeaveRequest.status == status)
    total = query.count()
    items = query.order_by(LeaveRequest.applied_at.desc()).offset(skip).limit(limit).all()
    return items, total
