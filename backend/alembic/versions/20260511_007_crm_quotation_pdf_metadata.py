"""Add CRM quotation PDF metadata

Revision ID: 20260511_007_crm_quotation_pdf_metadata
Revises: 20260511_006_crm_lead_scoring
Create Date: 2026-05-11 07:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_007_crm_quotation_pdf_metadata"
down_revision = "20260511_006_crm_lead_scoring"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("crm_quotations", sa.Column("pdf_url", sa.String(length=500), nullable=True))
    op.add_column("crm_quotations", sa.Column("pdf_file_name", sa.String(length=180), nullable=True))
    op.add_column("crm_quotations", sa.Column("pdf_status", sa.String(length=30), nullable=True))
    op.add_column("crm_quotations", sa.Column("pdf_generated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("crm_quotations", sa.Column("pdf_generated_by_user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_crm_quotations_pdf_generated_by_user_id_users",
        "crm_quotations",
        "users",
        ["pdf_generated_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_crm_quotations_pdf_status"), "crm_quotations", ["pdf_status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_crm_quotations_pdf_status"), table_name="crm_quotations")
    op.drop_constraint("fk_crm_quotations_pdf_generated_by_user_id_users", "crm_quotations", type_="foreignkey")
    op.drop_column("crm_quotations", "pdf_generated_by_user_id")
    op.drop_column("crm_quotations", "pdf_generated_at")
    op.drop_column("crm_quotations", "pdf_status")
    op.drop_column("crm_quotations", "pdf_file_name")
    op.drop_column("crm_quotations", "pdf_url")
