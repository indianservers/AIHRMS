"""Add HRMS Form 16 records

Revision ID: 20260511_029
Revises: 20260511_028
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_029"
down_revision = "20260511_028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "form16_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("financial_year", sa.String(length=20), nullable=False),
        sa.Column("part_a_file_path", sa.String(length=500), nullable=True),
        sa.Column("part_b_file_path", sa.String(length=500), nullable=True),
        sa.Column("combined_file_path", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("taxable_income", sa.Numeric(14, 2), nullable=True),
        sa.Column("tax_deducted", sa.Numeric(14, 2), nullable=True),
        sa.Column("generated_by", sa.Integer(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["generated_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["organization_id"], ["companies.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_form16_records_id"), "form16_records", ["id"], unique=False)
    op.create_index(op.f("ix_form16_records_organization_id"), "form16_records", ["organization_id"], unique=False)
    op.create_index(op.f("ix_form16_records_employee_id"), "form16_records", ["employee_id"], unique=False)
    op.create_index(op.f("ix_form16_records_financial_year"), "form16_records", ["financial_year"], unique=False)
    op.create_index(op.f("ix_form16_records_status"), "form16_records", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_form16_records_status"), table_name="form16_records")
    op.drop_index(op.f("ix_form16_records_financial_year"), table_name="form16_records")
    op.drop_index(op.f("ix_form16_records_employee_id"), table_name="form16_records")
    op.drop_index(op.f("ix_form16_records_organization_id"), table_name="form16_records")
    op.drop_index(op.f("ix_form16_records_id"), table_name="form16_records")
    op.drop_table("form16_records")
