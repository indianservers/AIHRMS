from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class SalaryComponent(Base):
    __tablename__ = "salary_components"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(30), unique=True, nullable=False)
    component_type = Column(String(20), nullable=False)  # Earning, Deduction, Statutory
    calculation_type = Column(String(20), default="Fixed")  # Fixed, Percentage, Formula
    amount = Column(Numeric(12, 2), default=0)
    percentage_of = Column(String(50))  # basic, gross, ctc
    is_taxable = Column(Boolean, default=True)
    is_pf_applicable = Column(Boolean, default=False)
    is_esi_applicable = Column(Boolean, default=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SalaryStructure(Base):
    __tablename__ = "salary_structures"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    effective_from = Column(Date)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    components = relationship("SalaryStructureComponent", back_populates="structure", cascade="all, delete-orphan")
    employee_salaries = relationship("EmployeeSalary", back_populates="structure")


class SalaryStructureComponent(Base):
    __tablename__ = "salary_structure_components"

    id = Column(Integer, primary_key=True, index=True)
    structure_id = Column(Integer, ForeignKey("salary_structures.id", ondelete="CASCADE"), nullable=False)
    component_id = Column(Integer, ForeignKey("salary_components.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(12, 2), default=0)
    percentage = Column(Numeric(5, 2))
    order_sequence = Column(Integer, default=1)

    structure = relationship("SalaryStructure", back_populates="components")
    component = relationship("SalaryComponent")


class EmployeeSalary(Base):
    __tablename__ = "employee_salaries"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    structure_id = Column(Integer, ForeignKey("salary_structures.id", ondelete="SET NULL"), nullable=True)
    ctc = Column(Numeric(14, 2), nullable=False)
    basic = Column(Numeric(12, 2))
    hra = Column(Numeric(12, 2))
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    structure = relationship("SalaryStructure", back_populates="employee_salaries")


class PayrollRun(Base):
    __tablename__ = "payroll_runs"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    run_date = Column(Date)
    status = Column(String(20), default="Draft")  # Draft, Processing, Completed, Approved, Locked
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True))
    locked_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    locked_at = Column(DateTime(timezone=True))
    total_gross = Column(Numeric(16, 2), default=0)
    total_deductions = Column(Numeric(16, 2), default=0)
    total_net = Column(Numeric(16, 2), default=0)
    remarks = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    records = relationship("PayrollRecord", back_populates="payroll_run", cascade="all, delete-orphan")


class PayrollRecord(Base):
    __tablename__ = "payroll_records"

    id = Column(Integer, primary_key=True, index=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    working_days = Column(Integer)
    present_days = Column(Numeric(5, 1))
    lop_days = Column(Numeric(5, 1), default=0)
    paid_days = Column(Numeric(5, 1))
    basic = Column(Numeric(12, 2), default=0)
    hra = Column(Numeric(12, 2), default=0)
    da = Column(Numeric(12, 2), default=0)
    ta = Column(Numeric(12, 2), default=0)
    other_allowances = Column(Numeric(12, 2), default=0)
    gross_salary = Column(Numeric(12, 2), default=0)
    pf_employee = Column(Numeric(10, 2), default=0)
    pf_employer = Column(Numeric(10, 2), default=0)
    esi_employee = Column(Numeric(10, 2), default=0)
    esi_employer = Column(Numeric(10, 2), default=0)
    professional_tax = Column(Numeric(10, 2), default=0)
    tds = Column(Numeric(10, 2), default=0)
    other_deductions = Column(Numeric(10, 2), default=0)
    total_deductions = Column(Numeric(12, 2), default=0)
    reimbursements = Column(Numeric(10, 2), default=0)
    bonus = Column(Numeric(10, 2), default=0)
    net_salary = Column(Numeric(12, 2), default=0)
    is_anomaly = Column(Boolean, default=False)
    anomaly_reason = Column(Text)
    status = Column(String(20), default="Draft")  # Draft, Approved, Paid

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    payroll_run = relationship("PayrollRun", back_populates="records")
    employee = relationship("Employee", back_populates="payrolls")
    components = relationship("PayrollComponent", back_populates="record", cascade="all, delete-orphan")


class PayrollComponent(Base):
    __tablename__ = "payroll_components"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("payroll_records.id", ondelete="CASCADE"), nullable=False)
    component_id = Column(Integer, ForeignKey("salary_components.id", ondelete="SET NULL"), nullable=True)
    component_name = Column(String(100))
    component_type = Column(String(20))
    amount = Column(Numeric(12, 2), default=0)

    record = relationship("PayrollRecord", back_populates="components")


class Reimbursement(Base):
    __tablename__ = "reimbursements"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100))  # Travel, Medical, Food, etc.
    amount = Column(Numeric(12, 2), nullable=False)
    date = Column(Date)
    description = Column(Text)
    receipt_url = Column(String(500))
    status = Column(String(20), default="Pending")  # Pending, Approved, Rejected, Paid
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    payroll_record_id = Column(Integer, ForeignKey("payroll_records.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
