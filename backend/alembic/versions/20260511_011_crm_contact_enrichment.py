"""Add CRM contact enrichment logs

Revision ID: 20260511_011_crm_contact_enrichment
Revises: 20260511_010_crm_territory_management
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_011_crm_contact_enrichment"
down_revision = "20260511_010_crm_territory_management"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crm_enrichment_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=True),
        sa.Column("old_values_json", sa.JSON(), nullable=True),
        sa.Column("new_values_json", sa.JSON(), nullable=True),
        sa.Column("applied_fields_json", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_crm_enrichment_logs_id"), "crm_enrichment_logs", ["id"], unique=False)
    op.create_index(op.f("ix_crm_enrichment_logs_organization_id"), "crm_enrichment_logs", ["organization_id"], unique=False)
    op.create_index(op.f("ix_crm_enrichment_logs_entity_type"), "crm_enrichment_logs", ["entity_type"], unique=False)
    op.create_index(op.f("ix_crm_enrichment_logs_entity_id"), "crm_enrichment_logs", ["entity_id"], unique=False)
    op.create_index(op.f("ix_crm_enrichment_logs_provider"), "crm_enrichment_logs", ["provider"], unique=False)
    op.create_index(op.f("ix_crm_enrichment_logs_status"), "crm_enrichment_logs", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_crm_enrichment_logs_status"), table_name="crm_enrichment_logs")
    op.drop_index(op.f("ix_crm_enrichment_logs_provider"), table_name="crm_enrichment_logs")
    op.drop_index(op.f("ix_crm_enrichment_logs_entity_id"), table_name="crm_enrichment_logs")
    op.drop_index(op.f("ix_crm_enrichment_logs_entity_type"), table_name="crm_enrichment_logs")
    op.drop_index(op.f("ix_crm_enrichment_logs_organization_id"), table_name="crm_enrichment_logs")
    op.drop_index(op.f("ix_crm_enrichment_logs_id"), table_name="crm_enrichment_logs")
    op.drop_table("crm_enrichment_logs")
