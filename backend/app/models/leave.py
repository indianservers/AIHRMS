from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class LeaveType(Base):
    __tablename__ = "leave_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    days_allowed = Column(Numeric(5, 1), nullable=False)
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


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
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

    employee = relationship("Employee", back_populates="leaves", foreign_keys=[employee_id])
    leave_type = relationship("LeaveType", back_populates="leave_requests")
