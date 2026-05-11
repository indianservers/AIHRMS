"""Add payroll bank export history

Revision ID: 20260511_027
Revises: 20260511_026
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_027"
down_revision = "20260511_026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payroll_bank_exports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("payroll_run_id", sa.Integer(), nullable=False),
        sa.Column("export_type", sa.String(length=20), nullable=False),
        sa.Column("bank_name", sa.String(length=120), nullable=True),
        sa.Column("total_employees", sa.Integer(), nullable=True),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("generated_by", sa.Integer(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("downloaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("download_count", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["generated_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["companies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["payroll_run_id"], ["payroll_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payroll_bank_exports_id"), "payroll_bank_exports", ["id"], unique=False)
    op.create_index(op.f("ix_payroll_bank_exports_organization_id"), "payroll_bank_exports", ["organization_id"], unique=False)
    op.create_index(op.f("ix_payroll_bank_exports_payroll_run_id"), "payroll_bank_exports", ["payroll_run_id"], unique=False)
    op.create_index(op.f("ix_payroll_bank_exports_export_type"), "payroll_bank_exports", ["export_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_payroll_bank_exports_export_type"), table_name="payroll_bank_exports")
    op.drop_index(op.f("ix_payroll_bank_exports_payroll_run_id"), table_name="payroll_bank_exports")
    op.drop_index(op.f("ix_payroll_bank_exports_organization_id"), table_name="payroll_bank_exports")
    op.drop_index(op.f("ix_payroll_bank_exports_id"), table_name="payroll_bank_exports")
    op.drop_table("payroll_bank_exports")
