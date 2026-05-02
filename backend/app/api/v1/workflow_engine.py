from datetime import datetime, timedelta, timezone
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
    steps = db.query(WorkflowStepDefinition).filter(WorkflowStepDefinition.workflow_id == data.workflow_id).order_by(WorkflowStepDefinition.step_order).all() if definition else []
    first = steps[0] if steps else None
    if first:
        db.add(WorkflowTask(
            instance_id=instance.id,
            step_definition_id=first.id,
            assigned_role=first.approver_value if first.approver_type == "Role" else None,
            assigned_to_user_id=int(first.approver_value) if first.approver_type == "User" and first.approver_value else None,
            due_at=datetime.now(timezone.utc) + timedelta(hours=first.timeout_hours) if first.timeout_hours else None,
        ))
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
        instance.status = "Approved" if data.decision.lower() == "approve" else "Rejected"
        instance.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)
    return task
