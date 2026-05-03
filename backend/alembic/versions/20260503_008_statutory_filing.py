"""add statutory filing connector tables

Revision ID: 20260503_008
Revises: 20260503_001
Create Date: 2026-05-03
"""

from alembic import op
import sqlalchemy as sa


revision = "20260503_008"
down_revision = "20260503_001"
branch_labels = None
depends_on = None


def _has_table(conn, name):
    return conn.dialect.has_table(conn, name)


def upgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn, "statutory_compliance_calendar"):
        op.create_table(
            "statutory_compliance_calendar",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("statutory_type", sa.String(length=50), nullable=True),
            sa.Column("due_date", sa.Date(), nullable=False),
            sa.Column("period_start", sa.Date(), nullable=True),
            sa.Column("period_end", sa.Date(), nullable=True),
            sa.Column("description", sa.String(length=500), nullable=True),
            sa.Column("status", sa.String(length=30), nullable=True, server_default="Pending"),
            sa.Column("filed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("filed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("remarks", sa.Text(), nullable=True),
            sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        )
        op.create_index("ix_statutory_calendar_type", "statutory_compliance_calendar", ["statutory_type"])
        op.create_index("ix_statutory_calendar_status", "statutory_compliance_calendar", ["status"])
        op.create_index("ix_statutory_calendar_due_date", "statutory_compliance_calendar", ["due_date"])

    if not _has_table(conn, "statutory_filing_submissions"):
        op.create_table(
            "statutory_filing_submissions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("statutory_type", sa.String(length=50), nullable=True),
            sa.Column("payroll_run_id", sa.Integer(), sa.ForeignKey("payroll_runs.id"), nullable=True),
            sa.Column("file_type", sa.String(length=20), nullable=True),
            sa.Column("generated_file_path", sa.String(length=500), nullable=True),
            sa.Column("validation_status", sa.String(length=30), nullable=True, server_default="pending"),
            sa.Column("validation_errors_json", sa.JSON(), nullable=True),
            sa.Column("row_count", sa.Integer(), nullable=True),
            sa.Column("total_amount", sa.Numeric(18, 2), nullable=True),
            sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("submitted_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("portal_reference", sa.String(length=200), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        )
        op.create_index("ix_statutory_submission_type", "statutory_filing_submissions", ["statutory_type"])
        op.create_index("ix_statutory_submission_run", "statutory_filing_submissions", ["payroll_run_id"])
        op.create_index("ix_statutory_submission_status", "statutory_filing_submissions", ["validation_status"])


def downgrade() -> None:
    conn = op.get_bind()
    if _has_table(conn, "statutory_filing_submissions"):
        op.drop_table("statutory_filing_submissions")
    if _has_table(conn, "statutory_compliance_calendar"):
        op.drop_table("statutory_compliance_calendar")
