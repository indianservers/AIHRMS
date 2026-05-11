from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


AiModule = Literal["CRM", "HRMS", "PMS", "CROSS"]
AiMessageRole = Literal["user", "assistant", "system", "tool"]
AiConversationStatus = Literal["active", "archived", "closed"]
AiDataAccessScope = Literal["own_records", "team", "company"]


class AiAgentRead(BaseModel):
    id: int
    name: str
    code: str
    module: str
    description: str | None = None
    model: str | None = None
    temperature: float | None = None
    is_active: bool
    requires_approval: bool

    model_config = {"from_attributes": True}


class AiAgentStatusUpdate(BaseModel):
    is_active: bool


class AiConversationCreate(BaseModel):
    agent_id: int
    module: AiModule
    title: str | None = Field(default=None, max_length=220)
    related_entity_type: str | None = Field(default=None, max_length=80)
    related_entity_id: str | None = Field(default=None, max_length=80)


class AiConversationRead(BaseModel):
    id: int
    user_id: int
    agent_id: int | None
    module: str
    title: str
    related_entity_type: str | None
    related_entity_id: str | None
    status: str
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class AiMessageRead(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str | None
    tool_call_json: dict[str, Any] | None
    tool_result_json: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AiConversationDetail(AiConversationRead):
    messages: list[AiMessageRead] = []


class AiMessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class AiChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str = Field(..., min_length=1)
    module: AiModule | None = None
    related_entity_type: str | None = Field(default=None, max_length=80)
    related_entity_id: str | None = Field(default=None, max_length=80)


class AiChatResponse(BaseModel):
    success: bool
    conversation_id: int | None = None
    agent_id: int | None = None
    message: str
    tool_calls: list[dict[str, Any]] = []
    approvals: list[dict[str, Any]] = []
    suggested_actions: list[dict[str, Any]] = []
    error_code: str | None = None


class AiMessageSaveResponse(BaseModel):
    conversation_id: int
    message_id: int
    response: str


class AiApprovalRead(BaseModel):
    id: int
    conversation_id: int | None
    agent_id: int | None
    user_id: int | None
    module: str
    action_type: str
    related_entity_type: str | None
    related_entity_id: str | None
    proposed_action_json: dict[str, Any]
    status: str
    approved_by: int | None
    approved_at: datetime | None
    rejected_reason: str | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}


class AiApprovalReject(BaseModel):
    rejected_reason: str = Field(..., min_length=1)


class AiConfigUpdate(BaseModel):
    is_enabled: bool | None = None
    auto_action_enabled: bool | None = None
    approval_required: bool | None = None
    data_access_scope: AiDataAccessScope | None = None


class AiToolTestRequest(BaseModel):
    agent_code: str = Field(..., min_length=1, max_length=120)
    tool_name: str = Field(..., min_length=1, max_length=120)
    input: dict[str, Any] = Field(default_factory=dict)
    conversation_id: int | None = None
    related_entity_type: str | None = Field(default=None, max_length=80)
    related_entity_id: str | None = Field(default=None, max_length=80)


class AiToolExecutionResponse(BaseModel):
    success: bool
    tool_name: str
    module: str | None = None
    requires_approval: bool = False
    approval_id: int | None = None
    data: dict[str, Any] | list[Any] | None = None
    message: str
    error_code: str | None = None
    missing_method: str | None = None
    details: list[Any] | None = None
