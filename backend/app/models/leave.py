from sqlalchemy import CheckConstraint, Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Numeric, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class LeaveType(Base):
    __tablename__ = "leave_types"
    __table_args__ = (
        CheckConstraint(
            "accrual_frequency IN ('daily','weekly','monthly','quarterly','annual')",
            name="ck_leave_type_accrual_frequency",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    days_allowed = Column(Numeric(5, 1), nullable=False)
    accrual_frequency = Column(String(20), default="annual", nullable=False)  # daily, weekly, monthly, quarterly, annual
    carry_forward = Column(Boolean, default=False)
    carry_forward_limit = Column(Numeric(5, 1), default=0)
    encashable = Column(Boolean, default=False)
    applicable_gender = Column(String(20), default="All")  # All, Male, Female
    applicable_from_months = Column(Integer, default=0)  # Months after joining
    half_day_allowed = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    color = Column(String(20), default="#3B82F6")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    leave_balances = relationship("LeaveBalance", back_populates="leave_type")
    leave_requests = relationship("LeaveRequest", back_populates="leave_type")


class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id", ondelete="CASCADE"), nullable=False)
    year = Column(Integer, nullable=False)
    allocated = Column(Numeric(5, 1), default=0)
    used = Column(Numeric(5, 1), default=0)
    pending = Column(Numeric(5, 1), default=0)
    carried_forward = Column(Numeric(5, 1), default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    leave_type = relationship("LeaveType", back_populates="leave_balances")
    ledger_entries = relationship("LeaveBalanceLedger", back_populates="balance", cascade="all, delete-orphan")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    __table_args__ = (
        Index("idx_leave_request_status", "status", "employee_id"),
        Index("idx_leave_request_active_status", "deleted_at", "status", "employee_id"),
        Index("idx_leave_request_company_status", "company_id", "status", "employee_id"),
        Index("idx_leave_request_company_active_status", "company_id", "deleted_at", "status", "employee_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id", ondelete="CASCADE"), nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    days_count = Column(Numeric(5, 1), nullable=False)
    is_half_day = Column(Boolean, default=False)
    half_day_period = Column(String(20))  # First Half, Second Half
    reason = Column(Text)
    status = Column(String(20), default="Pending")  # Pending, Approved, Rejected, Cancelled
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True))
    review_remarks = Column(Text)
    contact_during_leave = Column(String(20))
    handover_employee_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))
    deleted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    employee = relationship("Employee", back_populates="leaves", foreign_keys=[employee_id])
    leave_type = relationship("LeaveType", back_populates="leave_requests")
    ledger_entries = relationship("LeaveBalanceLedger", back_populates="leave_request")


class LeaveBalanceLedger(Base):
    __tablename__ = "leave_balance_ledger"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id", ondelete="CASCADE"), nullable=False, index=True)
    leave_balance_id = Column(Integer, ForeignKey("leave_balances.id", ondelete="CASCADE"), nullable=True)
    leave_request_id = Column(Integer, ForeignKey("leave_requests.id", ondelete="SET NULL"), nullable=True)
    year = Column(Integer, nullable=False, index=True)
    transaction_type = Column(String(40), nullable=False)
    amount = Column(Numeric(5, 1), nullable=False)
    balance_after = Column(Numeric(5, 1), nullable=False)
    reason = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    balance = relationship("LeaveBalance", back_populates="ledger_entries")
    leave_request = relationship("LeaveRequest", back_populates="ledger_entries")
