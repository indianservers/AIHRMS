from datetime import datetime, timedelta, timezone
import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import RequirePermission, get_current_user, get_db
from app.models.user import User
from app.models.workflow_engine import WorkflowDefinition, WorkflowInstance, WorkflowStepDefinition, WorkflowTask
from app.schemas.workflow_engine import (
    WorkflowDefinitionCreate, WorkflowDefinitionSchema, WorkflowInstanceCreate,
    WorkflowInstanceSchema, WorkflowTaskDecision, WorkflowTaskSchema,
)

router = APIRouter(prefix="/workflow-engine", tags=["Workflow Engine"])


def _condition_matches(expression: str | None, context: dict | None) -> bool:
    if not expression:
        return True
    context = context or {}
    match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_.]*)\s*(==|!=|>=|<=|>|<)\s*(.+?)\s*$", expression)
    if not match:
        return False
    key, operator, expected_raw = match.groups()
    actual = context
    for part in key.split("."):
        actual = actual.get(part) if isinstance(actual, dict) else None
    expected_raw = expected_raw.strip().strip("\"'")
    try:
        actual_value = float(actual)
        expected_value = float(expected_raw)
    except (TypeError, ValueError):
        actual_value = "" if actual is None else str(actual)
        expected_value = expected_raw
    if operator == "==":
        return actual_value == expected_value
    if operator == "!=":
        return actual_value != expected_value
    if operator == ">=":
        return actual_value >= expected_value
    if operator == "<=":
        return actual_value <= expected_value
    if operator == ">":
        return actual_value > expected_value
    if operator == "<":
        return actual_value < expected_value
    return False


def _assign_task_from_step(instance: WorkflowInstance, step: WorkflowStepDefinition) -> WorkflowTask:
    return WorkflowTask(
        instance_id=instance.id,
        step_definition_id=step.id,
        assigned_role=step.approver_value if step.approver_type == "Role" else None,
        assigned_to_user_id=int(step.approver_value) if step.approver_type == "User" and step.approver_value else None,
        due_at=datetime.now(timezone.utc) + timedelta(hours=step.timeout_hours) if step.timeout_hours else None,
    )


def _create_next_pending_task(db: Session, instance: WorkflowInstance, after_step_order: int = 0) -> bool:
    if not instance.workflow_id:
        return False
    steps = db.query(WorkflowStepDefinition).filter(
        WorkflowStepDefinition.workflow_id == instance.workflow_id,
        WorkflowStepDefinition.step_order > after_step_order,
    ).order_by(WorkflowStepDefinition.step_order).all()
    for step in steps:
        if not _condition_matches(step.condition_expression, instance.context_json):
            continue
        db.add(_assign_task_from_step(instance, step))
        instance.current_step_order = step.step_order
        instance.status = "Pending"
        return True
    return False


@router.post("/definitions", response_model=WorkflowDefinitionSchema, status_code=201)
def create_definition(data: WorkflowDefinitionCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("company_manage"))):
    definition = WorkflowDefinition(**data.model_dump(exclude={"steps"}), created_by=current_user.id)
    db.add(definition)
    db.flush()
    for step in data.steps:
        db.add(WorkflowStepDefinition(workflow_id=definition.id, **step.model_dump()))
    db.commit()
    db.refresh(definition)
    return definition


@router.get("/definitions", response_model=list[WorkflowDefinitionSchema])
def list_definitions(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("company_manage"))):
    return db.query(WorkflowDefinition).filter(WorkflowDefinition.is_active == True).order_by(WorkflowDefinition.module, WorkflowDefinition.name).all()


@router.post("/instances", response_model=WorkflowInstanceSchema, status_code=201)
def start_instance(data: WorkflowInstanceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    definition = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == data.workflow_id).first() if data.workflow_id else None
    instance = WorkflowInstance(**data.model_dump(), requester_user_id=current_user.id)
    db.add(instance)
    db.flush()
    if definition and not _create_next_pending_task(db, instance):
        instance.status = "Approved"
        instance.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(instance)
    return instance


@router.get("/tasks", response_model=list[WorkflowTaskSchema])
def my_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(WorkflowTask).filter(WorkflowTask.status == "Pending")
    role_name = current_user.role.name if current_user.role else None
    return query.filter((WorkflowTask.assigned_to_user_id == current_user.id) | (WorkflowTask.assigned_role == role_name)).order_by(WorkflowTask.created_at).limit(200).all()


@router.put("/tasks/{task_id}/decision", response_model=WorkflowTaskSchema)
def decide_task(task_id: int, data: WorkflowTaskDecision, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(WorkflowTask).filter(WorkflowTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Workflow task not found")
    task.status = "Completed"
    task.decision = data.decision
    task.decision_reason = data.reason
    task.decided_by = current_user.id
    task.decided_at = datetime.now(timezone.utc)
    instance = db.query(WorkflowInstance).filter(WorkflowInstance.id == task.instance_id).first()
    if instance:
        if data.decision.lower() == "approve":
            step = db.query(WorkflowStepDefinition).filter(WorkflowStepDefinition.id == task.step_definition_id).first()
            step_order = step.step_order if step else instance.current_step_order
            if not _create_next_pending_task(db, instance, after_step_order=step_order):
                instance.status = "Approved"
                instance.completed_at = datetime.now(timezone.utc)
        else:
            instance.status = "Rejected"
            instance.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return task


@router.post("/tasks/process-escalations", response_model=list[WorkflowTaskSchema])
def process_escalations(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("company_manage"))):
    now = datetime.now(timezone.utc)
    tasks = db.query(WorkflowTask).join(
        WorkflowStepDefinition,
        WorkflowTask.step_definition_id == WorkflowStepDefinition.id,
    ).filter(
        WorkflowTask.status == "Pending",
        WorkflowTask.due_at.isnot(None),
        WorkflowTask.due_at <= now,
        WorkflowTask.escalated_at.is_(None),
        WorkflowStepDefinition.escalation_user_id.isnot(None),
    ).all()
    for task in tasks:
        step = db.query(WorkflowStepDefinition).filter(WorkflowStepDefinition.id == task.step_definition_id).first()
        task.escalated_at = now
        task.escalated_to_user_id = step.escalation_user_id
        task.assigned_to_user_id = step.escalation_user_id
        task.assigned_role = None
    db.commit()
    return tasks


@router.post("/tasks/send-reminders", response_model=list[WorkflowTaskSchema])
def mark_due_reminders(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("company_manage"))):
    now = datetime.now(timezone.utc)
    tasks = db.query(WorkflowTask).filter(
        WorkflowTask.status == "Pending",
        WorkflowTask.due_at.isnot(None),
        WorkflowTask.due_at <= now,
        WorkflowTask.reminder_sent_at.is_(None),
    ).all()
    for task in tasks:
        task.reminder_sent_at = now
    db.commit()
    return tasks
