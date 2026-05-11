"""crm calendar integrations

Revision ID: 20260511_013_crm_calendar_integrations
Revises: 20260511_012_crm_whatsapp_sms_messages
Create Date: 2026-05-11 00:13:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_013_crm_calendar_integrations"
down_revision = "20260511_012_crm_whatsapp_sms_messages"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "calendar_integrations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("access_token_encrypted", sa.Text(), nullable=True),
        sa.Column("refresh_token_encrypted", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_calendar_integrations_id", "calendar_integrations", ["id"])
    op.create_index("ix_calendar_integrations_organization_id", "calendar_integrations", ["organization_id"])
    op.create_index("ix_calendar_integrations_user_id", "calendar_integrations", ["user_id"])
    op.create_index("ix_calendar_integrations_provider", "calendar_integrations", ["provider"])
    op.create_index("ix_calendar_integrations_is_active", "calendar_integrations", ["is_active"])
    op.create_index("ix_calendar_integrations_created_at", "calendar_integrations", ["created_at"])

    op.add_column("crm_meetings", sa.Column("external_provider", sa.String(length=40), nullable=True))
    op.add_column("crm_meetings", sa.Column("external_event_id", sa.String(length=180), nullable=True))
    op.add_column("crm_meetings", sa.Column("sync_status", sa.String(length=30), nullable=True))
    op.add_column("crm_meetings", sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_crm_meetings_external_provider", "crm_meetings", ["external_provider"])
    op.create_index("ix_crm_meetings_external_event_id", "crm_meetings", ["external_event_id"])
    op.create_index("ix_crm_meetings_sync_status", "crm_meetings", ["sync_status"])
    op.execute("UPDATE crm_meetings SET sync_status = COALESCE(sync_status, 'not_synced')")


def downgrade() -> None:
    op.drop_index("ix_crm_meetings_sync_status", table_name="crm_meetings")
    op.drop_index("ix_crm_meetings_external_event_id", table_name="crm_meetings")
    op.drop_index("ix_crm_meetings_external_provider", table_name="crm_meetings")
    op.drop_column("crm_meetings", "last_synced_at")
    op.drop_column("crm_meetings", "sync_status")
    op.drop_column("crm_meetings", "external_event_id")
    op.drop_column("crm_meetings", "external_provider")
    op.drop_table("calendar_integrations")
