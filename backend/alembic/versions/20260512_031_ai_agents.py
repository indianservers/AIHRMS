"""Add AI Agents module

Revision ID: 20260512_031
Revises: 20260511_030
Create Date: 2026-05-12
"""

from alembic import op
import sqlalchemy as sa


revision = "20260512_031"
down_revision = "20260511_030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_agents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("module", sa.String(length=40), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("model", sa.String(length=80), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("requires_approval", sa.Boolean(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_agents_id"), "ai_agents", ["id"], unique=False)
    op.create_index(op.f("ix_ai_agents_name"), "ai_agents", ["name"], unique=False)
    op.create_index(op.f("ix_ai_agents_code"), "ai_agents", ["code"], unique=True)
    op.create_index(op.f("ix_ai_agents_module"), "ai_agents", ["module"], unique=False)
    op.create_index(op.f("ix_ai_agents_is_active"), "ai_agents", ["is_active"], unique=False)

    op.create_table(
        "ai_agent_tools",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("tool_name", sa.String(length=120), nullable=False),
        sa.Column("tool_description", sa.Text(), nullable=True),
        sa.Column("input_schema_json", sa.JSON(), nullable=False),
        sa.Column("module", sa.String(length=40), nullable=False),
        sa.Column("permission_required", sa.String(length=120), nullable=True),
        sa.Column("risk_level", sa.String(length=30), nullable=True),
        sa.Column("requires_approval", sa.Boolean(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["ai_agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_agent_tools_id"), "ai_agent_tools", ["id"], unique=False)
    op.create_index(op.f("ix_ai_agent_tools_agent_id"), "ai_agent_tools", ["agent_id"], unique=False)
    op.create_index(op.f("ix_ai_agent_tools_tool_name"), "ai_agent_tools", ["tool_name"], unique=False)
    op.create_index(op.f("ix_ai_agent_tools_module"), "ai_agent_tools", ["module"], unique=False)
    op.create_index(op.f("ix_ai_agent_tools_risk_level"), "ai_agent_tools", ["risk_level"], unique=False)
    op.create_index(op.f("ix_ai_agent_tools_is_active"), "ai_agent_tools", ["is_active"], unique=False)

    op.create_table(
        "ai_conversations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=True),
        sa.Column("module", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("related_entity_type", sa.String(length=80), nullable=True),
        sa.Column("related_entity_id", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["ai_agents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_conversations_id"), "ai_conversations", ["id"], unique=False)
    op.create_index(op.f("ix_ai_conversations_user_id"), "ai_conversations", ["user_id"], unique=False)
    op.create_index(op.f("ix_ai_conversations_agent_id"), "ai_conversations", ["agent_id"], unique=False)
    op.create_index(op.f("ix_ai_conversations_module"), "ai_conversations", ["module"], unique=False)
    op.create_index(op.f("ix_ai_conversations_status"), "ai_conversations", ["status"], unique=False)
    op.create_index(op.f("ix_ai_conversations_related_entity_type"), "ai_conversations", ["related_entity_type"], unique=False)
    op.create_index(op.f("ix_ai_conversations_related_entity_id"), "ai_conversations", ["related_entity_id"], unique=False)

    op.create_table(
        "ai_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=True),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("tool_call_json", sa.JSON(), nullable=True),
        sa.Column("tool_result_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["conversation_id"], ["ai_conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_messages_id"), "ai_messages", ["id"], unique=False)
    op.create_index(op.f("ix_ai_messages_conversation_id"), "ai_messages", ["conversation_id"], unique=False)
    op.create_index(op.f("ix_ai_messages_role"), "ai_messages", ["role"], unique=False)

    op.create_table(
        "ai_action_approvals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("module", sa.String(length=40), nullable=False),
        sa.Column("action_type", sa.String(length=120), nullable=False),
        sa.Column("related_entity_type", sa.String(length=80), nullable=True),
        sa.Column("related_entity_id", sa.String(length=80), nullable=True),
        sa.Column("proposed_action_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["ai_agents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["conversation_id"], ["ai_conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("id", "conversation_id", "agent_id", "user_id", "module", "action_type", "related_entity_type", "related_entity_id", "status"):
        op.create_index(op.f(f"ix_ai_action_approvals_{column}"), "ai_action_approvals", [column], unique=False)

    op.create_table(
        "ai_audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("agent_id", sa.Integer(), nullable=True),
        sa.Column("module", sa.String(length=40), nullable=False),
        sa.Column("action", sa.String(length=140), nullable=False),
        sa.Column("related_entity_type", sa.String(length=80), nullable=True),
        sa.Column("related_entity_id", sa.String(length=80), nullable=True),
        sa.Column("input_json", sa.JSON(), nullable=True),
        sa.Column("output_json", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["ai_agents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("id", "user_id", "agent_id", "module", "action", "related_entity_type", "related_entity_id", "status"):
        op.create_index(op.f(f"ix_ai_audit_logs_{column}"), "ai_audit_logs", [column], unique=False)

    op.create_table(
        "ai_agent_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=True),
        sa.Column("auto_action_enabled", sa.Boolean(), nullable=True),
        sa.Column("approval_required", sa.Boolean(), nullable=True),
        sa.Column("data_access_scope", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["ai_agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_agent_settings_id"), "ai_agent_settings", ["id"], unique=False)
    op.create_index(op.f("ix_ai_agent_settings_company_id"), "ai_agent_settings", ["company_id"], unique=False)
    op.create_index(op.f("ix_ai_agent_settings_agent_id"), "ai_agent_settings", ["agent_id"], unique=False)
    op.create_index(op.f("ix_ai_agent_settings_is_enabled"), "ai_agent_settings", ["is_enabled"], unique=False)


def downgrade() -> None:
    op.drop_table("ai_agent_settings")
    op.drop_table("ai_audit_logs")
    op.drop_table("ai_action_approvals")
    op.drop_table("ai_messages")
    op.drop_table("ai_conversations")
    op.drop_table("ai_agent_tools")
    op.drop_table("ai_agents")
