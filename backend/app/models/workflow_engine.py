from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base


class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False)
    module = Column(String(80), nullable=False, index=True)
    trigger_event = Column(String(120), nullable=False, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WorkflowStepDefinition(Base):
    __tablename__ = "workflow_step_definitions"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflow_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    step_order = Column(Integer, nullable=False)
    step_type = Column(String(40), default="Approval")
    approver_type = Column(String(40), default="Role")  # User, Role, Manager, HR
    approver_value = Column(String(120))
    condition_expression = Column(Text)
    timeout_hours = Column(Integer)
    escalation_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_required = Column(Boolean, default=True)


class WorkflowInstance(Base):
    __tablename__ = "workflow_instances"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflow_definitions.id", ondelete="SET NULL"), nullable=True, index=True)
    module = Column(String(80), nullable=False, index=True)
    entity_type = Column(String(80), nullable=False)
    entity_id = Column(Integer, nullable=False, index=True)
    requester_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    context_json = Column(JSON)
    status = Column(String(30), default="Pending", index=True)
    current_step_order = Column(Integer, default=1)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class WorkflowTask(Base):
    __tablename__ = "workflow_tasks"

    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(Integer, ForeignKey("workflow_instances.id", ondelete="CASCADE"), nullable=False, index=True)
    step_definition_id = Column(Integer, ForeignKey("workflow_step_definitions.id", ondelete="SET NULL"), nullable=True)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_role = Column(String(120), index=True)
    status = Column(String(30), default="Pending", index=True)
    due_at = Column(DateTime(timezone=True))
    reminder_sent_at = Column(DateTime(timezone=True))
    escalated_at = Column(DateTime(timezone=True))
    escalated_to_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    decision = Column(String(30))
    decision_reason = Column(Text)
    decided_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    decided_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
