from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class AiAgent(Base):
    __tablename__ = "ai_agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(160), nullable=False, index=True)
    code = Column(String(120), nullable=False, unique=True, index=True)
    module = Column(String(40), nullable=False, index=True)
    description = Column(Text)
    system_prompt = Column(Text, nullable=False)
    model = Column(String(80))
    temperature = Column(Float, default=0.2)
    is_active = Column(Boolean, default=True, index=True)
    requires_approval = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tools = relationship("AiAgentTool", back_populates="agent", cascade="all, delete-orphan")


class AiAgentTool(Base):
    __tablename__ = "ai_agent_tools"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("ai_agents.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_name = Column(String(120), nullable=False, index=True)
    tool_description = Column(Text)
    input_schema_json = Column(JSON, nullable=False)
    module = Column(String(40), nullable=False, index=True)
    permission_required = Column(String(120))
    risk_level = Column(String(30), default="low", index=True)
    requires_approval = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    agent = relationship("AiAgent", back_populates="tools")


class AiConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("ai_agents.id", ondelete="SET NULL"), nullable=True, index=True)
    module = Column(String(40), nullable=False, index=True)
    title = Column(String(220), nullable=False)
    related_entity_type = Column(String(80), index=True)
    related_entity_id = Column(String(80), index=True)
    status = Column(String(30), default="active", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    agent = relationship("AiAgent")
    messages = relationship("AiMessage", back_populates="conversation", cascade="all, delete-orphan")


class AiMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=True, index=True)
    role = Column(String(30), nullable=False, index=True)
    content = Column(Text)
    tool_call_json = Column(JSON)
    tool_result_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("AiConversation", back_populates="messages")


class AiActionApproval(Base):
    __tablename__ = "ai_action_approvals"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("ai_agents.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    module = Column(String(40), nullable=False, index=True)
    action_type = Column(String(120), nullable=False, index=True)
    related_entity_type = Column(String(80), index=True)
    related_entity_id = Column(String(80), index=True)
    proposed_action_json = Column(JSON, nullable=False)
    status = Column(String(30), default="pending", index=True)
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True))
    rejected_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    agent = relationship("AiAgent")
    conversation = relationship("AiConversation")


class AiAuditLog(Base):
    __tablename__ = "ai_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    agent_id = Column(Integer, ForeignKey("ai_agents.id", ondelete="SET NULL"), nullable=True, index=True)
    module = Column(String(40), nullable=False, index=True)
    action = Column(String(140), nullable=False, index=True)
    related_entity_type = Column(String(80), index=True)
    related_entity_id = Column(String(80), index=True)
    input_json = Column(JSON)
    output_json = Column(JSON)
    status = Column(String(30), default="success", index=True)
    ip_address = Column(String(64))
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    agent = relationship("AiAgent")


class AiAgentSetting(Base):
    __tablename__ = "ai_agent_settings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=True, index=True)
    agent_id = Column(Integer, ForeignKey("ai_agents.id", ondelete="CASCADE"), nullable=False, index=True)
    is_enabled = Column(Boolean, default=True, index=True)
    auto_action_enabled = Column(Boolean, default=False)
    approval_required = Column(Boolean, default=True)
    data_access_scope = Column(String(80), default="own_records")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    agent = relationship("AiAgent")
