"""Add CRM email compose logging and templates

Revision ID: 20260511_003_crm_email_compose
Revises: 20260511_002_crm_activity_timeline
Create Date: 2026-05-11 02:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_003_crm_email_compose"
down_revision = "20260511_002_crm_activity_timeline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("crm_email_logs", sa.Column("entity_type", sa.String(length=40), nullable=True))
    op.add_column("crm_email_logs", sa.Column("entity_id", sa.Integer(), nullable=True))
    op.add_column("crm_email_logs", sa.Column("bcc", sa.String(length=500), nullable=True))
    op.add_column("crm_email_logs", sa.Column("status", sa.String(length=30), nullable=True))
    op.add_column("crm_email_logs", sa.Column("provider_message_id", sa.String(length=160), nullable=True))
    op.add_column("crm_email_logs", sa.Column("failure_reason", sa.Text(), nullable=True))
    op.add_column("crm_email_logs", sa.Column("sent_by_user_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_crm_email_logs_entity_type"), "crm_email_logs", ["entity_type"], unique=False)
    op.create_index(op.f("ix_crm_email_logs_entity_id"), "crm_email_logs", ["entity_id"], unique=False)
    op.create_index(op.f("ix_crm_email_logs_status"), "crm_email_logs", ["status"], unique=False)
    op.execute("UPDATE crm_email_logs SET status = COALESCE(status, 'sent')")
    op.execute("UPDATE crm_email_logs SET entity_type = 'lead', entity_id = lead_id WHERE entity_type IS NULL AND lead_id IS NOT NULL")
    op.execute("UPDATE crm_email_logs SET entity_type = 'contact', entity_id = contact_id WHERE entity_type IS NULL AND contact_id IS NOT NULL")
    op.execute("UPDATE crm_email_logs SET entity_type = 'account', entity_id = company_id WHERE entity_type IS NULL AND company_id IS NOT NULL")
    op.execute("UPDATE crm_email_logs SET entity_type = 'deal', entity_id = deal_id WHERE entity_type IS NULL AND deal_id IS NOT NULL")

    op.create_table(
        "crm_email_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("subject", sa.String(length=220), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.String(length=40), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "name", name="uq_crm_email_template_org_name"),
    )
    op.create_index(op.f("ix_crm_email_templates_entity_type"), "crm_email_templates", ["entity_type"], unique=False)
    op.create_index(op.f("ix_crm_email_templates_id"), "crm_email_templates", ["id"], unique=False)
    op.create_index(op.f("ix_crm_email_templates_is_active"), "crm_email_templates", ["is_active"], unique=False)
    op.create_index(op.f("ix_crm_email_templates_name"), "crm_email_templates", ["name"], unique=False)
    op.create_index(op.f("ix_crm_email_templates_organization_id"), "crm_email_templates", ["organization_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_crm_email_templates_organization_id"), table_name="crm_email_templates")
    op.drop_index(op.f("ix_crm_email_templates_name"), table_name="crm_email_templates")
    op.drop_index(op.f("ix_crm_email_templates_is_active"), table_name="crm_email_templates")
    op.drop_index(op.f("ix_crm_email_templates_id"), table_name="crm_email_templates")
    op.drop_index(op.f("ix_crm_email_templates_entity_type"), table_name="crm_email_templates")
    op.drop_table("crm_email_templates")
    op.drop_index(op.f("ix_crm_email_logs_status"), table_name="crm_email_logs")
    op.drop_index(op.f("ix_crm_email_logs_entity_id"), table_name="crm_email_logs")
    op.drop_index(op.f("ix_crm_email_logs_entity_type"), table_name="crm_email_logs")
    op.drop_column("crm_email_logs", "sent_by_user_id")
    op.drop_column("crm_email_logs", "failure_reason")
    op.drop_column("crm_email_logs", "provider_message_id")
    op.drop_column("crm_email_logs", "status")
    op.drop_column("crm_email_logs", "bcc")
    op.drop_column("crm_email_logs", "entity_id")
    op.drop_column("crm_email_logs", "entity_type")
