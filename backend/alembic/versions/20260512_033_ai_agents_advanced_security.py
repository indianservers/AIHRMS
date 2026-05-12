"""Add advanced AI Agent security and usage tables

Revision ID: 20260512_033
Revises: 20260512_032
Create Date: 2026-05-12
"""

from alembic import op
import sqlalchemy as sa


revision = "20260512_033"
down_revision = "20260512_032"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ai_action_approvals", sa.Column("execution_status", sa.String(length=30), nullable=True, server_default="pending"))
    op.add_column("ai_action_approvals", sa.Column("execution_error", sa.Text(), nullable=True))
    op.add_column("ai_action_approvals", sa.Column("idempotency_key", sa.String(length=160), nullable=True))
    op.create_index(op.f("ix_ai_action_approvals_execution_status"), "ai_action_approvals", ["execution_status"], unique=False)
    op.create_index(op.f("ix_ai_action_approvals_idempotency_key"), "ai_action_approvals", ["idempotency_key"], unique=False)

    op.create_table(
        "ai_usage_limits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("agent_id", sa.Integer(), nullable=True),
        sa.Column("module", sa.String(length=40), nullable=True),
        sa.Column("limit_type", sa.String(length=40), nullable=False),
        sa.Column("max_requests", sa.Integer(), nullable=False),
        sa.Column("period", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["ai_agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("id", "company_id", "user_id", "agent_id", "module", "limit_type", "period", "is_active"):
        op.create_index(op.f(f"ix_ai_usage_limits_{column}"), "ai_usage_limits", [column], unique=False)

    op.create_table(
        "ai_usage_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("agent_id", sa.Integer(), nullable=True),
        sa.Column("module", sa.String(length=40), nullable=True),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("token_input", sa.Integer(), nullable=True),
        sa.Column("token_output", sa.Integer(), nullable=True),
        sa.Column("estimated_cost", sa.Numeric(12, 6), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["ai_agents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("id", "company_id", "user_id", "agent_id", "module", "event_type", "created_at"):
        op.create_index(op.f(f"ix_ai_usage_events_{column}"), "ai_usage_events", [column], unique=False)

    op.create_table(
        "ai_agent_permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("can_use", sa.Boolean(), nullable=True),
        sa.Column("can_configure", sa.Boolean(), nullable=True),
        sa.Column("can_approve_actions", sa.Boolean(), nullable=True),
        sa.Column("can_view_logs", sa.Boolean(), nullable=True),
        sa.Column("can_export_conversations", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["ai_agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("id", "company_id", "agent_id", "role_id", "user_id"):
        op.create_index(op.f(f"ix_ai_agent_permissions_{column}"), "ai_agent_permissions", [column], unique=False)

    op.create_table(
        "ai_security_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("ai_enabled", sa.Boolean(), nullable=True),
        sa.Column("crm_ai_enabled", sa.Boolean(), nullable=True),
        sa.Column("pms_ai_enabled", sa.Boolean(), nullable=True),
        sa.Column("hrms_ai_enabled", sa.Boolean(), nullable=True),
        sa.Column("cross_ai_enabled", sa.Boolean(), nullable=True),
        sa.Column("emergency_message", sa.Text(), nullable=True),
        sa.Column("updated_by", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_security_settings_id"), "ai_security_settings", ["id"], unique=False)
    op.create_index(op.f("ix_ai_security_settings_company_id"), "ai_security_settings", ["company_id"], unique=True)

    op.create_table(
        "ai_cost_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("agent_id", sa.Integer(), nullable=True),
        sa.Column("conversation_id", sa.Integer(), nullable=True),
        sa.Column("model", sa.String(length=80), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("estimated_cost", sa.Numeric(12, 6), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["ai_agents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["conversation_id"], ["ai_conversations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("id", "company_id", "user_id", "agent_id", "conversation_id", "model", "created_at"):
        op.create_index(op.f(f"ix_ai_cost_logs_{column}"), "ai_cost_logs", [column], unique=False)

    op.create_table(
        "ai_message_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("agent_id", sa.Integer(), nullable=True),
        sa.Column("rating", sa.String(length=20), nullable=False),
        sa.Column("feedback_text", sa.Text(), nullable=True),
        sa.Column("feedback_type", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["ai_agents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["conversation_id"], ["ai_conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["message_id"], ["ai_messages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("id", "message_id", "conversation_id", "user_id", "agent_id", "rating", "feedback_type", "created_at"):
        op.create_index(op.f(f"ix_ai_message_feedback_{column}"), "ai_message_feedback", [column], unique=False)

    op.create_table(
        "ai_handoff_notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=True),
        sa.Column("agent_id", sa.Integer(), nullable=True),
        sa.Column("module", sa.String(length=40), nullable=False),
        sa.Column("related_entity_type", sa.String(length=80), nullable=True),
        sa.Column("related_entity_id", sa.String(length=80), nullable=True),
        sa.Column("assigned_to", sa.Integer(), nullable=True),
        sa.Column("priority", sa.String(length=20), nullable=True),
        sa.Column("summary", sa.String(length=300), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("recommended_action", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["ai_agents.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["conversation_id"], ["ai_conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("id", "conversation_id", "agent_id", "module", "related_entity_type", "related_entity_id", "assigned_to", "priority", "status", "created_by", "created_at"):
        op.create_index(op.f(f"ix_ai_handoff_notes_{column}"), "ai_handoff_notes", [column], unique=False)


def downgrade() -> None:
    op.drop_table("ai_handoff_notes")
    op.drop_table("ai_message_feedback")
    op.drop_table("ai_cost_logs")
    op.drop_table("ai_security_settings")
    op.drop_table("ai_agent_permissions")
    op.drop_table("ai_usage_events")
    op.drop_table("ai_usage_limits")
    op.drop_index(op.f("ix_ai_action_approvals_idempotency_key"), table_name="ai_action_approvals")
    op.drop_index(op.f("ix_ai_action_approvals_execution_status"), table_name="ai_action_approvals")
    op.drop_column("ai_action_approvals", "idempotency_key")
    op.drop_column("ai_action_approvals", "execution_error")
    op.drop_column("ai_action_approvals", "execution_status")
