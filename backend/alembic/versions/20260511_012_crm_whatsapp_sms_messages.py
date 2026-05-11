"""crm whatsapp sms messages

Revision ID: 20260511_012_crm_whatsapp_sms_messages
Revises: 20260511_011_crm_contact_enrichment
Create Date: 2026-05-11 00:12:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_012_crm_whatsapp_sms_messages"
down_revision = "20260511_011_crm_contact_enrichment"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crm_message_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.String(length=40), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "name", "channel", name="uq_crm_message_template_org_name_channel"),
    )
    op.create_index("ix_crm_message_templates_id", "crm_message_templates", ["id"])
    op.create_index("ix_crm_message_templates_organization_id", "crm_message_templates", ["organization_id"])
    op.create_index("ix_crm_message_templates_channel", "crm_message_templates", ["channel"])
    op.create_index("ix_crm_message_templates_entity_type", "crm_message_templates", ["entity_type"])
    op.create_index("ix_crm_message_templates_is_active", "crm_message_templates", ["is_active"])

    op.create_table(
        "crm_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("to", sa.String(length=40), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("provider_message_id", sa.String(length=160), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("template_id", sa.Integer(), nullable=True),
        sa.Column("sent_by_user_id", sa.Integer(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sent_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["template_id"], ["crm_message_templates.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_crm_messages_id", "crm_messages", ["id"])
    op.create_index("ix_crm_messages_organization_id", "crm_messages", ["organization_id"])
    op.create_index("ix_crm_messages_entity_type", "crm_messages", ["entity_type"])
    op.create_index("ix_crm_messages_entity_id", "crm_messages", ["entity_id"])
    op.create_index("ix_crm_messages_channel", "crm_messages", ["channel"])
    op.create_index("ix_crm_messages_to", "crm_messages", ["to"])
    op.create_index("ix_crm_messages_status", "crm_messages", ["status"])
    op.create_index("ix_crm_messages_provider", "crm_messages", ["provider"])
    op.create_index("ix_crm_messages_template_id", "crm_messages", ["template_id"])
    op.create_index("ix_crm_messages_sent_at", "crm_messages", ["sent_at"])
    op.create_index("ix_crm_messages_created_at", "crm_messages", ["created_at"])


def downgrade() -> None:
    op.drop_table("crm_messages")
    op.drop_table("crm_message_templates")
