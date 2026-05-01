from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Time, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20))
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    grace_minutes = Column(Integer, default=10)
    working_hours = Column(Numeric(4, 2), default=8.0)
    is_night_shift = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    employees = relationship("Employee", back_populates="shift")
    weekly_offs = relationship("ShiftWeeklyOff", back_populates="shift", cascade="all, delete-orphan")
    roster_assignments = relationship("ShiftRosterAssignment", back_populates="shift", cascade="all, delete-orphan")


class ShiftWeeklyOff(Base):
    __tablename__ = "shift_weekly_offs"

    id = Column(Integer, primary_key=True, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False, index=True)
    weekday = Column(Integer, nullable=False)  # Monday=0, Sunday=6
    week_pattern = Column(String(20), default="all")  # all, 1, 2, 3, 4, 5
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    shift = relationship("Shift", back_populates="weekly_offs")


class ShiftRosterAssignment(Base):
    __tablename__ = "shift_roster_assignments"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False, index=True)
    work_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), default="Published")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    shift = relationship("Shift", back_populates="roster_assignments")


class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    holiday_date = Column(Date, nullable=False)
    holiday_type = Column(String(30), default="National")  # National, Regional, Optional
    description = Column(Text)
    applicable_branches = Column(String(500))  # CSV of branch IDs, empty = all
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    attendance_date = Column(Date, nullable=False)
    check_in = Column(DateTime(timezone=True))
    check_out = Column(DateTime(timezone=True))
    check_in_location = Column(String(200))
    check_out_location = Column(String(200))
    check_in_ip = Column(String(50))
    check_out_ip = Column(String(50))
    shift_id = Column(Integer, ForeignKey("shifts.id", ondelete="SET NULL"), nullable=True)
    total_hours = Column(Numeric(5, 2))
    overtime_hours = Column(Numeric(5, 2), default=0)
    late_minutes = Column(Integer, default=0)
    early_exit_minutes = Column(Integer, default=0)
    short_minutes = Column(Integer, default=0)
    is_late = Column(Boolean, default=False)
    is_early_exit = Column(Boolean, default=False)
    is_short_hours = Column(Boolean, default=False)
    status = Column(String(30), default="Present")  # Present, Absent, Half-day, WFH, Holiday, Weekend, On Leave
    source = Column(String(30), default="Web")  # Web, Mobile, Biometric, Manual
    is_regularized = Column(Boolean, default=False)
    computed_at = Column(DateTime(timezone=True))
    remarks = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    employee = relationship("Employee", back_populates="attendances")
    regularization = relationship("AttendanceRegularization", back_populates="attendance", uselist=False)


class AttendanceRegularization(Base):
    __tablename__ = "attendance_regularizations"

    id = Column(Integer, primary_key=True, index=True)
    attendance_id = Column(Integer, ForeignKey("attendances.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    requested_check_in = Column(DateTime(timezone=True))
    requested_check_out = Column(DateTime(timezone=True))
    reason = Column(Text, nullable=False)
    status = Column(String(20), default="Pending")  # Pending, Approved, Rejected
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True))
    review_remarks = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    attendance = relationship("Attendance", back_populates="regularization")


class OvertimeRequest(Base):
    __tablename__ = "overtime_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    hours = Column(Numeric(4, 2), nullable=False)
    reason = Column(Text)
    status = Column(String(20), default="Pending")  # Pending, Approved, Rejected
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
