from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class WorkflowStepDefinitionCreate(BaseModel):
    step_order: int
    step_type: str = "Approval"
    approver_type: str = "Role"
    approver_value: Optional[str] = None
    condition_expression: Optional[str] = None
    timeout_hours: Optional[int] = None
    escalation_user_id: Optional[int] = None
    is_required: bool = True


class WorkflowDefinitionCreate(BaseModel):
    name: str
    module: str
    trigger_event: str
    description: Optional[str] = None
    steps: list[WorkflowStepDefinitionCreate] = []


class WorkflowDefinitionSchema(BaseModel):
    id: int
    name: str
    module: str
    trigger_event: str
    description: Optional[str] = None
    is_active: bool
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class WorkflowInstanceCreate(BaseModel):
    workflow_id: Optional[int] = None
    module: str
    entity_type: str
    entity_id: int
    context_json: Optional[dict[str, Any]] = None


class WorkflowTaskDecision(BaseModel):
    decision: str
    reason: Optional[str] = None


class WorkflowTaskSchema(BaseModel):
    id: int
    instance_id: int
    assigned_to_user_id: Optional[int] = None
    assigned_role: Optional[str] = None
    status: str
    due_at: Optional[datetime] = None
    reminder_sent_at: Optional[datetime] = None
    escalated_at: Optional[datetime] = None
    escalated_to_user_id: Optional[int] = None
    decision: Optional[str] = None
    decision_reason: Optional[str] = None
    decided_by: Optional[int] = None
    decided_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class WorkflowInstanceSchema(BaseModel):
    id: int
    workflow_id: Optional[int] = None
    module: str
    entity_type: str
    entity_id: int
    requester_user_id: Optional[int] = None
    context_json: Optional[dict[str, Any]] = None
    status: str
    current_step_order: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
