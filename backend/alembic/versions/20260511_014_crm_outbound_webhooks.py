"""crm outbound webhooks

Revision ID: 20260511_014_crm_outbound_webhooks
Revises: 20260511_013_crm_calendar_integrations
Create Date: 2026-05-11 00:14:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_014_crm_outbound_webhooks"
down_revision = "20260511_013_crm_calendar_integrations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crm_webhooks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("secret", sa.String(length=160), nullable=False),
        sa.Column("events", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_crm_webhooks_id", "crm_webhooks", ["id"])
    op.create_index("ix_crm_webhooks_organization_id", "crm_webhooks", ["organization_id"])
    op.create_index("ix_crm_webhooks_name", "crm_webhooks", ["name"])
    op.create_index("ix_crm_webhooks_is_active", "crm_webhooks", ["is_active"])
    op.create_index("ix_crm_webhooks_created_at", "crm_webhooks", ["created_at"])

    op.create_table(
        "crm_webhook_deliveries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("webhook_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("response_code", sa.Integer(), nullable=True),
        sa.Column("response_body", sa.Text(), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=True),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["webhook_id"], ["crm_webhooks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_crm_webhook_deliveries_id", "crm_webhook_deliveries", ["id"])
    op.create_index("ix_crm_webhook_deliveries_organization_id", "crm_webhook_deliveries", ["organization_id"])
    op.create_index("ix_crm_webhook_deliveries_webhook_id", "crm_webhook_deliveries", ["webhook_id"])
    op.create_index("ix_crm_webhook_deliveries_event_type", "crm_webhook_deliveries", ["event_type"])
    op.create_index("ix_crm_webhook_deliveries_status", "crm_webhook_deliveries", ["status"])
    op.create_index("ix_crm_webhook_deliveries_next_retry_at", "crm_webhook_deliveries", ["next_retry_at"])
    op.create_index("ix_crm_webhook_deliveries_created_at", "crm_webhook_deliveries", ["created_at"])


def downgrade() -> None:
    op.drop_table("crm_webhook_deliveries")
    op.drop_table("crm_webhooks")
