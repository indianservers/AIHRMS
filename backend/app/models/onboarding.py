from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class OnboardingTemplate(Base):
    __tablename__ = "onboarding_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    applicable_designation_ids = Column(Text)  # JSON
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tasks = relationship("OnboardingTask", back_populates="template", cascade="all, delete-orphan")


class OnboardingTask(Base):
    __tablename__ = "onboarding_tasks"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("onboarding_templates.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # Document, IT Setup, Training, Policy, Orientation
    assigned_to_role = Column(String(50))  # HR, IT, Manager, Employee
    due_days = Column(Integer, default=1)  # Days from joining
    is_mandatory = Column(Boolean, default=True)
    order_sequence = Column(Integer, default=1)

    template = relationship("OnboardingTemplate", back_populates="tasks")


class EmployeeOnboarding(Base):
    __tablename__ = "employee_onboardings"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, unique=True)
    template_id = Column(Integer, ForeignKey("onboarding_templates.id", ondelete="SET NULL"), nullable=True)
    start_date = Column(Date)
    expected_completion_date = Column(Date)
    completed_date = Column(Date)
    status = Column(String(30), default="In Progress")  # Not Started, In Progress, Completed
    welcome_email_sent = Column(Boolean, default=False)
    welcome_email_sent_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    task_completions = relationship("OnboardingTaskCompletion", back_populates="onboarding", cascade="all, delete-orphan")


class OnboardingTaskCompletion(Base):
    __tablename__ = "onboarding_task_completions"

    id = Column(Integer, primary_key=True, index=True)
    onboarding_id = Column(Integer, ForeignKey("employee_onboardings.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(Integer, ForeignKey("onboarding_tasks.id", ondelete="CASCADE"), nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    completed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    remarks = Column(Text)
    document_url = Column(String(500))

    onboarding = relationship("EmployeeOnboarding", back_populates="task_completions")
    task = relationship("OnboardingTask")


class PolicyAcknowledgement(Base):
    __tablename__ = "policy_acknowledgements"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    policy_name = Column(String(200), nullable=False)
    policy_document_url = Column(String(500))
    acknowledged_at = Column(DateTime(timezone=True))
    ip_address = Column(String(50))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
