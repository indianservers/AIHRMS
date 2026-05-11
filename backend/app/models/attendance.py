from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Time, Numeric, Text, Index
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


class ShiftRoster(Base):
    __tablename__ = "shift_rosters"
    __table_args__ = (
        Index("idx_shift_roster_org_date", "organization_id", "roster_date"),
        Index("idx_shift_roster_employee_date", "employee_id", "roster_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id", ondelete="CASCADE"), nullable=False, index=True)
    roster_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), default="draft", index=True)
    assigned_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    shift = relationship("Shift")
    employee = relationship("Employee")


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
    __table_args__ = (
        Index("idx_attendance_employee_date", "employee_id", "attendance_date"),
    )

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


class AttendancePunch(Base):
    __tablename__ = "attendance_punches"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    punch_time = Column(DateTime(timezone=True), nullable=False, index=True)
    punch_type = Column(String(20), nullable=False)  # IN, OUT, BREAK_IN, BREAK_OUT
    source = Column(String(30), default="Web")
    device_id = Column(String(120))
    ip_address = Column(String(50))
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    location_text = Column(String(250))
    raw_payload = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BiometricDevice(Base):
    __tablename__ = "biometric_devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    vendor = Column(String(80), nullable=False)
    device_code = Column(String(80), nullable=False, unique=True, index=True)
    location = Column(String(150))
    sync_mode = Column(String(40), default="File Import")
    last_sync_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BiometricImportBatch(Base):
    __tablename__ = "biometric_import_batches"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("biometric_devices.id", ondelete="SET NULL"), nullable=True, index=True)
    source_filename = Column(String(250))
    imported_rows = Column(Integer, default=0)
    skipped_rows = Column(Integer, default=0)
    error_rows = Column(Integer, default=0)
    status = Column(String(30), default="Imported", index=True)
    error_report_json = Column(Text)
    imported_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    device = relationship("BiometricDevice")


class GeoAttendancePolicy(Base):
    __tablename__ = "geo_attendance_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)
    radius_meters = Column(Integer, default=200)
    require_selfie = Column(Boolean, default=False)
    require_qr = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AttendancePunchProof(Base):
    __tablename__ = "attendance_punch_proofs"

    id = Column(Integer, primary_key=True, index=True)
    punch_id = Column(Integer, ForeignKey("attendance_punches.id", ondelete="CASCADE"), nullable=False, index=True)
    proof_type = Column(String(30), nullable=False)  # Geo, Selfie, QR
    proof_url = Column(String(500))
    latitude = Column(Numeric(10, 7))
    longitude = Column(Numeric(10, 7))
    qr_code = Column(String(120))
    validation_status = Column(String(30), default="Pending", index=True)
    validation_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    punch = relationship("AttendancePunch")


class AttendanceMonthLock(Base):
    __tablename__ = "attendance_month_locks"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    status = Column(String(20), default="Locked", index=True)
    reason = Column(Text)
    locked_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    locked_at = Column(DateTime(timezone=True), server_default=func.now())
    unlocked_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    unlocked_at = Column(DateTime(timezone=True))


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
