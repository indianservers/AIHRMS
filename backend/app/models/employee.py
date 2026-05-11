from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Numeric, Text, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        Index("idx_employees_active_status", "deleted_at", "status"),
        Index("idx_employees_name", "first_name", "last_name"),
        Index("idx_employees_directory_email", "work_email", "personal_email"),
        Index("idx_employees_department_status", "department_id", "status", "deleted_at"),
        Index("idx_employees_manager_status", "reporting_manager_id", "status", "deleted_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True)

    # Personal Info
    first_name = Column(String(80), nullable=False)
    middle_name = Column(String(80))
    last_name = Column(String(80), nullable=False)
    gender = Column(String(20))
    date_of_birth = Column(Date)
    marital_status = Column(String(20))
    blood_group = Column(String(10))
    nationality = Column(String(50), default="Indian")
    religion = Column(String(50))
    category = Column(String(20))  # General/OBC/SC/ST
    gender_identity = Column(String(50))
    disability_status = Column(String(50))
    veteran_status = Column(String(50))

    # Contact
    work_email = Column(String(150), index=True)
    personal_email = Column(String(150))
    phone_number = Column(String(20))
    alternate_phone = Column(String(20))
    office_extension = Column(String(20))
    emergency_contact_name = Column(String(100))
    emergency_contact_number = Column(String(20))
    emergency_contact_relation = Column(String(50))

    # Address
    present_address = Column(Text)
    permanent_address = Column(Text)
    present_city = Column(String(100))
    present_state = Column(String(100))
    present_pincode = Column(String(20))
    permanent_city = Column(String(100))
    permanent_state = Column(String(100))
    permanent_pincode = Column(String(20))

    # Job Info
    date_of_joining = Column(Date, nullable=False)
    date_of_confirmation = Column(Date)
    date_of_exit = Column(Date)
    branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    designation_id = Column(Integer, ForeignKey("designations.id", ondelete="SET NULL"), nullable=True)
    business_unit_id = Column(Integer, ForeignKey("business_units.id", ondelete="SET NULL"), nullable=True)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id", ondelete="SET NULL"), nullable=True)
    location_id = Column(Integer, ForeignKey("work_locations.id", ondelete="SET NULL"), nullable=True)
    grade_band_id = Column(Integer, ForeignKey("grade_bands.id", ondelete="SET NULL"), nullable=True)
    position_id = Column(Integer, ForeignKey("positions.id", ondelete="SET NULL"), nullable=True)
    reporting_manager_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    employment_type = Column(String(50), default="Full-time")  # Full-time, Part-time, Contract, Intern
    worker_type = Column(String(50), default="Employee")  # Employee, Contractor, Consultant, Gig
    status = Column(String(30), default="Active")  # Active, Probation, On Leave, Resigned, Terminated
    work_location = Column(String(50), default="Office")  # Office, Remote, Hybrid
    shift_id = Column(Integer, ForeignKey("shifts.id", ondelete="SET NULL"), nullable=True)
    probation_period_months = Column(Integer, default=6)
    probation_start_date = Column(Date)
    probation_end_date = Column(Date)
    probation_status = Column(String(30), default="on_probation", index=True)
    desk_code = Column(String(50))
    timezone = Column(String(80), default="Asia/Kolkata")
    manager_chain_path = Column(String(500))

    # Bank Details (encrypted in production)
    bank_name = Column(String(100))
    bank_branch = Column(String(100))
    account_number = Column(String(100))
    account_type = Column(String(30), default="Savings")
    ifsc_code = Column(String(20))

    # Tax / Compliance
    pan_number = Column(String(20))
    aadhaar_number = Column(String(20))
    uan_number = Column(String(30))
    pf_number = Column(String(50))
    esic_number = Column(String(50))
    salary_currency = Column(String(3), default="INR")

    # Profile
    profile_photo_url = Column(String(500))
    preferred_display_name = Column(String(150))
    directory_visibility = Column(String(20), default="public", index=True)  # public, team, hidden
    skills_tags = Column(Text)
    profile_completeness = Column(Integer, default=0)
    bio = Column(Text)
    interests = Column(Text)
    research_work = Column(Text)
    family_information = Column(Text)
    health_information = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))
    deleted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="employee", foreign_keys=[user_id])
    branch = relationship("Branch", back_populates="employees")
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    designation = relationship("Designation", back_populates="employees")
    reporting_manager = relationship("Employee", remote_side=[id], foreign_keys=[reporting_manager_id])
    shift = relationship("Shift", back_populates="employees")
    business_unit = relationship("BusinessUnit", foreign_keys=[business_unit_id])
    cost_center = relationship("CostCenter", foreign_keys=[cost_center_id])
    location = relationship("WorkLocation", foreign_keys=[location_id])
    grade_band = relationship("GradeBand", foreign_keys=[grade_band_id])
    position = relationship("Position", foreign_keys=[position_id])

    educations = relationship("EmployeeEducation", back_populates="employee", cascade="all, delete-orphan")
    experiences = relationship("EmployeeExperience", back_populates="employee", cascade="all, delete-orphan")
    skills = relationship("EmployeeSkill", back_populates="employee", cascade="all, delete-orphan")
    documents = relationship("EmployeeDocument", back_populates="employee", cascade="all, delete-orphan")
    lifecycle_events = relationship(
        "EmployeeLifecycleEvent",
        foreign_keys="EmployeeLifecycleEvent.employee_id",
        back_populates="employee",
        cascade="all, delete-orphan",
        order_by="EmployeeLifecycleEvent.event_date.desc()",
    )

    attendances = relationship("Attendance", back_populates="employee")
    leaves = relationship("LeaveRequest", back_populates="employee", foreign_keys="LeaveRequest.employee_id")
    payrolls = relationship("PayrollRecord", back_populates="employee")
    assets = relationship("AssetAssignment", back_populates="employee")
    goals = relationship("PerformanceGoal", back_populates="employee")
    helpdesk_tickets = relationship("HelpdeskTicket", back_populates="employee")
    exit_record = relationship("ExitRecord", back_populates="employee", uselist=False)


class EmployeeEducation(Base):
    __tablename__ = "employee_educations"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    degree = Column(String(100), nullable=False)
    specialization = Column(String(150))
    institution = Column(String(200))
    board_university = Column(String(200))
    pass_year = Column(Integer)
    percentage_cgpa = Column(Numeric(5, 2))
    document_url = Column(String(500))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    employee = relationship("Employee", back_populates="educations")


class EmployeeExperience(Base):
    __tablename__ = "employee_experiences"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    company_name = Column(String(200), nullable=False)
    designation = Column(String(150))
    from_date = Column(Date)
    to_date = Column(Date)
    is_current = Column(Boolean, default=False)
    responsibilities = Column(Text)
    relieving_letter_url = Column(String(500))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    employee = relationship("Employee", back_populates="experiences")


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    proficiency = Column(String(30))  # Beginner, Intermediate, Advanced, Expert
    years_experience = Column(Numeric(4, 1))

    employee = relationship("Employee", back_populates="skills")


class EmployeeDocument(Base):
    __tablename__ = "employee_documents"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(100), nullable=False)  # ID Proof, Address Proof, etc.
    document_name = Column(String(200))
    document_number = Column(String(100))
    file_url = Column(String(500))
    expiry_date = Column(Date)
    verification_status = Column(String(30), default="Pending", index=True)
    is_verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at = Column(DateTime(timezone=True))
    verifier_name = Column(String(150))
    verifier_company = Column(String(200))
    verification_notes = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    employee = relationship("Employee", back_populates="documents")


class EmployeeLifecycleEvent(Base):
    __tablename__ = "employee_lifecycle_events"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_date = Column(Date, nullable=False)
    effective_from = Column(Date)
    effective_to = Column(Date)
    from_status = Column(String(30))
    to_status = Column(String(30))
    from_branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    to_branch_id = Column(Integer, ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    from_department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    to_department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    from_designation_id = Column(Integer, ForeignKey("designations.id", ondelete="SET NULL"), nullable=True)
    to_designation_id = Column(Integer, ForeignKey("designations.id", ondelete="SET NULL"), nullable=True)
    from_manager_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    to_manager_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    reason = Column(Text)
    remarks = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="lifecycle_events")


class EmployeeChangeRequest(Base):
    __tablename__ = "employee_change_requests"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    request_type = Column(String(60), nullable=False, index=True)
    field_name = Column(String(120), nullable=True, index=True)
    effective_date = Column(Date)
    field_changes_json = Column(JSON, nullable=False)
    old_value_json = Column(JSON)
    new_value_json = Column(JSON)
    document_path = Column(String(500))
    status = Column(String(30), default="Pending", index=True)
    reason = Column(Text)
    requested_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True))
    review_remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee")


class ProbationReview(Base):
    __tablename__ = "probation_reviews"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    manager_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True)
    review_date = Column(Date, nullable=False)
    performance_rating = Column(Integer)
    conduct_rating = Column(Integer)
    attendance_rating = Column(Integer)
    recommendation = Column(String(30), nullable=False)
    comments = Column(Text)
    status = Column(String(30), default="pending", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    employee = relationship("Employee", foreign_keys=[employee_id])
    manager = relationship("Employee", foreign_keys=[manager_id])


class ProbationAction(Base):
    __tablename__ = "probation_actions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    action_type = Column(String(30), nullable=False, index=True)
    effective_date = Column(Date, nullable=False)
    extended_until = Column(Date)
    remarks = Column(Text)
    letter_generated = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee")
