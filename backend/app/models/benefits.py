from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class BenefitPlan(Base):
    __tablename__ = "benefit_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    plan_type = Column(String(50), nullable=False, index=True)  # Group Health, NPS, Flexi Benefit, Insurance, ESOP
    provider_name = Column(String(150))
    policy_number = Column(String(100))
    description = Column(Text)
    employer_contribution = Column(Numeric(12, 2), default=0)
    employee_contribution = Column(Numeric(12, 2), default=0)
    taxable = Column(Boolean, default=False)
    payroll_component_code = Column(String(50))
    effective_from = Column(Date)
    effective_to = Column(Date)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EmployeeBenefitEnrollment(Base):
    __tablename__ = "employee_benefit_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    benefit_plan_id = Column(Integer, ForeignKey("benefit_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    coverage_level = Column(String(80), default="Self")
    enrolled_amount = Column(Numeric(12, 2), default=0)
    employee_contribution = Column(Numeric(12, 2), default=0)
    employer_contribution = Column(Numeric(12, 2), default=0)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    status = Column(String(30), default="Active", index=True)
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True))
    remarks = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee")
    plan = relationship("BenefitPlan")


class FlexiBenefitPolicy(Base):
    __tablename__ = "flexi_benefit_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    component_code = Column(String(50), nullable=False, index=True)
    monthly_limit = Column(Numeric(12, 2), default=0)
    annual_limit = Column(Numeric(12, 2), default=0)
    proof_required = Column(Boolean, default=True)
    taxable_if_unclaimed = Column(Boolean, default=True)
    carry_forward_allowed = Column(Boolean, default=False)
    effective_from = Column(Date)
    effective_to = Column(Date)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EmployeeFlexiBenefitAllocation(Base):
    __tablename__ = "employee_flexi_benefit_allocations"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_id = Column(Integer, ForeignKey("flexi_benefit_policies.id", ondelete="CASCADE"), nullable=False, index=True)
    financial_year = Column(String(20), nullable=False, index=True)
    allocated_amount = Column(Numeric(12, 2), nullable=False)
    claimed_amount = Column(Numeric(12, 2), default=0)
    taxable_fallback_amount = Column(Numeric(12, 2), default=0)
    status = Column(String(30), default="Active", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee")
    policy = relationship("FlexiBenefitPolicy")


class BenefitPayrollDeduction(Base):
    __tablename__ = "benefit_payroll_deductions"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("employee_benefit_enrollments.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    payroll_record_id = Column(Integer, ForeignKey("payroll_records.id", ondelete="SET NULL"), nullable=True, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    employee_amount = Column(Numeric(12, 2), default=0)
    employer_amount = Column(Numeric(12, 2), default=0)
    status = Column(String(30), default="Pending", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    enrollment = relationship("EmployeeBenefitEnrollment")
    employee = relationship("Employee")
