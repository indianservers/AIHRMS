from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session, joinedload

from app.ai_agents.models import AiActionApproval, AiAgent, AiAuditLog, AiConversation, AiMessage
from app.ai_agents.schemas import (
    AiAgentRead,
    AiAgentStatusUpdate,
    AiApprovalRead,
    AiApprovalReject,
    AiChatRequest,
    AiChatResponse,
    AiConfigUpdate,
    AiConversationCreate,
    AiConversationDetail,
    AiConversationRead,
    AiMessageCreate,
    AiMessageRead,
    AiMessageSaveResponse,
    AiToolExecutionResponse,
    AiToolTestRequest,
)
from app.ai_agents.services.approvals import AiApprovalService
from app.ai_agents.services.audit import AiAuditService
from app.ai_agents.services.orchestrator import AiAgentOrchestratorService
from app.ai_agents.services.registry import AiAgentRegistryService
from app.ai_agents.services.settings import AiAgentSettingsService
from app.ai_agents.tools.ai_tool_execution_service import AiToolExecutionService
from app.core.deps import get_current_user, get_db
from app.models.user import User

router = APIRouter(prefix="/ai-agents", tags=["AI Agents"])

AI_ENGINE_PLACEHOLDER = "AI engine is not connected yet. Message saved successfully."


def _request_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _company_id(user: User) -> int | None:
    employee = getattr(user, "employee", None)
    return getattr(employee, "organization_id", None) or getattr(user, "company_id", None)


def _can_access_ai_agents(user: User) -> bool:
    # Temporary foundation-level gate. Future work should map this to full RBAC permissions.
    return bool(user and getattr(user, "is_active", True))


def _require_ai_access(user: User) -> None:
    if not _can_access_ai_agents(user):
        raise HTTPException(status_code=403, detail="You do not have permission to access AI Agents")


def _is_ai_tool_tester(user: User) -> bool:
    if user.is_superuser:
        return True
    role_name = (user.role.name if user.role else "").lower().replace(" ", "_")
    if role_name in {"admin", "super_admin", "developer"}:
        return True
    permissions = {permission.name for permission in (user.role.permissions if user.role else [])}
    return bool(permissions.intersection({"settings_view", "settings_manage"}))


def _audit(
    db: Session,
    request: Request,
    user: User,
    *,
    action: str,
    module: str = "CROSS",
    agent_id: int | None = None,
    input_json: dict | None = None,
    output_json: dict | None = None,
    status: str = "success",
    related_entity_type: str | None = None,
    related_entity_id: str | None = None,
) -> None:
    AiAuditService(db).log(
        user=user,
        agent_id=agent_id,
        module=module,
        action=action,
        input_json=input_json,
        output_json=output_json,
        status=status,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        ip_address=_request_ip(request),
        user_agent=request.headers.get("user-agent"),
    )


@router.get("", response_model=list[AiAgentRead])
def list_agents(
    request: Request,
    module: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    agents = AiAgentRegistryService(db).list_agents(module)
    _audit(
        db,
        request,
        current_user,
        action="agent.list_viewed",
        module=module.upper() if module else "CROSS",
        input_json={"module": module},
        output_json={"count": len(agents)},
    )
    db.commit()
    return agents


@router.get("/config")
def ai_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    company_id = _company_id(current_user)
    agents = AiAgentRegistryService(db).list_agents()
    settings_by_agent = {row.agent_id: row for row in AiAgentSettingsService(db).list_for_company(company_id)}
    return [
        {
            "agent": AiAgentRead.model_validate(agent),
            "setting": {
                "is_enabled": settings_by_agent.get(agent.id).is_enabled if settings_by_agent.get(agent.id) else True,
                "auto_action_enabled": settings_by_agent.get(agent.id).auto_action_enabled if settings_by_agent.get(agent.id) else False,
                "approval_required": settings_by_agent.get(agent.id).approval_required if settings_by_agent.get(agent.id) else True,
                "data_access_scope": settings_by_agent.get(agent.id).data_access_scope if settings_by_agent.get(agent.id) else "own_records",
            },
        }
        for agent in agents
    ]


@router.put("/config/{agent_id}")
def update_ai_config(
    agent_id: int,
    payload: AiConfigUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    agent = db.query(AiAgent).filter(AiAgent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    company_id = _company_id(current_user)
    setting = AiAgentSettingsService(db).get_or_create(agent_id=agent_id, company_id=company_id)

    for field in ("is_enabled", "auto_action_enabled", "approval_required", "data_access_scope"):
        value = getattr(payload, field)
        if value is not None:
            setattr(setting, field, value)

    _audit(
        db,
        request,
        current_user,
        agent_id=agent.id,
        module=agent.module,
        action="agent.config_updated",
        input_json=payload.model_dump(exclude_none=True),
        output_json={"status": "updated"},
    )
    db.commit()
    return {"status": "updated"}


@router.post("/conversations", response_model=AiConversationRead)
def create_conversation(
    payload: AiConversationCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    agent = AiAgentRegistryService(db).get_agent(payload.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="AI agent not found")
    if agent.module != payload.module:
        raise HTTPException(status_code=400, detail="Conversation module does not match the selected agent")

    conversation = AiConversation(
        user_id=current_user.id,
        agent_id=agent.id,
        module=payload.module,
        title=payload.title or agent.name,
        related_entity_type=payload.related_entity_type,
        related_entity_id=payload.related_entity_id,
        status="active",
    )
    db.add(conversation)
    db.flush()
    _audit(
        db,
        request,
        current_user,
        agent_id=agent.id,
        module=agent.module,
        action="conversation.created",
        input_json=payload.model_dump(exclude_none=True),
        output_json={"conversation_id": conversation.id},
        related_entity_type=conversation.related_entity_type,
        related_entity_id=conversation.related_entity_id,
    )
    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("/conversations", response_model=list[AiConversationRead])
def list_conversations(
    agent_id: int | None = None,
    module: str | None = None,
    related_entity_type: str | None = None,
    related_entity_id: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    query = db.query(AiConversation).filter(AiConversation.user_id == current_user.id)
    if agent_id:
        query = query.filter(AiConversation.agent_id == agent_id)
    if module:
        query = query.filter(AiConversation.module == module.upper())
    if related_entity_type:
        query = query.filter(AiConversation.related_entity_type == related_entity_type)
    if related_entity_id:
        query = query.filter(AiConversation.related_entity_id == related_entity_id)
    if status:
        query = query.filter(AiConversation.status == status)
    return query.order_by(AiConversation.updated_at.desc().nullslast(), AiConversation.created_at.desc()).limit(100).all()


@router.post("/tools/test", response_model=AiToolExecutionResponse)
def test_ai_tool(
    payload: AiToolTestRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    if not _is_ai_tool_tester(current_user):
        raise HTTPException(status_code=403, detail="Only admin/developer users can test AI tools")
    result = AiToolExecutionService(db).execute_tool(
        user=current_user,
        agent_code=payload.agent_code,
        tool_name=payload.tool_name,
        input=payload.input,
        conversation_id=payload.conversation_id,
        related_entity_type=payload.related_entity_type,
        related_entity_id=payload.related_entity_id,
        ip_address=_request_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    db.commit()
    return result


@router.get("/conversations/{conversation_id}", response_model=AiConversationDetail)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    row = (
        db.query(AiConversation)
        .options(joinedload(AiConversation.messages))
        .filter(AiConversation.id == conversation_id, AiConversation.user_id == current_user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return row


@router.get("/conversations/{conversation_id}/messages", response_model=list[AiMessageRead])
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    conversation = db.query(AiConversation).filter(AiConversation.id == conversation_id, AiConversation.user_id == current_user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return db.query(AiMessage).filter(AiMessage.conversation_id == conversation.id).order_by(AiMessage.created_at.asc(), AiMessage.id.asc()).all()


@router.post("/conversations/{conversation_id}/messages", response_model=AiMessageSaveResponse)
def save_conversation_message(
    conversation_id: int,
    payload: AiMessageCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    conversation = db.query(AiConversation).filter(AiConversation.id == conversation_id, AiConversation.user_id == current_user.id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    message = AiMessage(conversation_id=conversation.id, role="user", content=payload.content)
    db.add(message)
    db.flush()
    _audit(
        db,
        request,
        current_user,
        agent_id=conversation.agent_id,
        module=conversation.module,
        action="message.saved",
        input_json={"content_length": len(payload.content)},
        output_json={"message_id": message.id, "placeholder": True},
        related_entity_type=conversation.related_entity_type,
        related_entity_id=conversation.related_entity_id,
    )
    db.commit()
    db.refresh(message)
    return AiMessageSaveResponse(conversation_id=conversation.id, message_id=message.id, response=AI_ENGINE_PLACEHOLDER)


@router.get("/approvals/pending", response_model=list[AiApprovalRead])
def pending_approvals(
    module: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    query = db.query(AiActionApproval).filter(AiActionApproval.status == "pending")
    if module:
        query = query.filter(AiActionApproval.module == module.upper())
    if not current_user.is_superuser:
        query = query.filter(AiActionApproval.user_id == current_user.id)
    return query.order_by(AiActionApproval.created_at.desc()).limit(100).all()


@router.post("/approvals/{approval_id}/approve", response_model=AiApprovalRead)
def approve_ai_action(
    approval_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    row = AiApprovalService(db).approve(approval_id, current_user)
    _audit(
        db,
        request,
        current_user,
        agent_id=row.agent_id,
        module=row.module,
        action="approval.approved",
        input_json={"approval_id": approval_id},
        output_json={"status": row.status},
        related_entity_type=row.related_entity_type,
        related_entity_id=row.related_entity_id,
    )
    db.commit()
    db.refresh(row)
    return row


@router.post("/approvals/{approval_id}/reject", response_model=AiApprovalRead)
def reject_ai_action(
    approval_id: int,
    payload: AiApprovalReject,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    row = AiApprovalService(db).reject(approval_id, payload.rejected_reason, current_user)
    _audit(
        db,
        request,
        current_user,
        agent_id=row.agent_id,
        module=row.module,
        action="approval.rejected",
        input_json={"approval_id": approval_id, "rejected_reason": payload.rejected_reason},
        output_json={"status": row.status},
        related_entity_type=row.related_entity_type,
        related_entity_id=row.related_entity_id,
    )
    db.commit()
    db.refresh(row)
    return row


@router.get("/logs")
def ai_logs(
    module: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    query = db.query(AiAuditLog)
    if module:
        query = query.filter(AiAuditLog.module == module.upper())
    if not current_user.is_superuser:
        query = query.filter(AiAuditLog.user_id == current_user.id)
    rows = query.order_by(AiAuditLog.created_at.desc()).limit(200).all()
    return [
        {
            "id": row.id,
            "user_id": row.user_id,
            "agent_id": row.agent_id,
            "module": row.module,
            "action": row.action,
            "status": row.status,
            "related_entity_type": row.related_entity_type,
            "related_entity_id": row.related_entity_id,
            "input_json": row.input_json,
            "output_json": row.output_json,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.post("/{agent_id}/chat", response_model=AiChatResponse)
def chat_with_agent(
    agent_id: int,
    payload: AiChatRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    result = AiAgentOrchestratorService(db).send_message(
        user=current_user,
        agent_id=agent_id,
        payload=payload,
        ip_address=_request_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    db.commit()
    return result


@router.get("/{agent_id}", response_model=AiAgentRead)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    agent = AiAgentRegistryService(db).get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="AI agent not found")
    return agent


@router.patch("/{agent_id}/status", response_model=AiAgentRead)
def update_agent_status(
    agent_id: int,
    payload: AiAgentStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_ai_access(current_user)
    agent = AiAgentRegistryService(db).set_status(agent_id, payload.is_active)
    if not agent:
        raise HTTPException(status_code=404, detail="AI agent not found")
    _audit(
        db,
        request,
        current_user,
        agent_id=agent.id,
        module=agent.module,
        action="agent.status_changed",
        input_json=payload.model_dump(),
        output_json={"is_active": agent.is_active},
    )
    db.commit()
    db.refresh(agent)
    return agent
