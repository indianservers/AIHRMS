"""payroll trust foundation

Revision ID: 20260501_006
Revises: 20260501_005
Create Date: 2026-05-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260501_006"
down_revision = "20260501_005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payroll_variance_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payroll_run_id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("previous_payroll_record_id", sa.Integer(), nullable=True),
        sa.Column("current_gross", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("previous_gross", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("gross_delta", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("gross_delta_percent", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("current_net", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("previous_net", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("net_delta", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("net_delta_percent", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["payroll_run_id"], ["payroll_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["previous_payroll_record_id"], ["payroll_records.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payroll_variance_items_employee_id"), "payroll_variance_items", ["employee_id"], unique=False)
    op.create_index(op.f("ix_payroll_variance_items_id"), "payroll_variance_items", ["id"], unique=False)
    op.create_index(op.f("ix_payroll_variance_items_payroll_run_id"), "payroll_variance_items", ["payroll_run_id"], unique=False)

    op.create_table(
        "payroll_export_batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payroll_run_id", sa.Integer(), nullable=False),
        sa.Column("export_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("output_file_url", sa.String(length=500), nullable=True),
        sa.Column("total_records", sa.Integer(), nullable=True),
        sa.Column("generated_by", sa.Integer(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["generated_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["payroll_run_id"], ["payroll_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payroll_export_batches_export_type"), "payroll_export_batches", ["export_type"], unique=False)
    op.create_index(op.f("ix_payroll_export_batches_id"), "payroll_export_batches", ["id"], unique=False)
    op.create_index(op.f("ix_payroll_export_batches_payroll_run_id"), "payroll_export_batches", ["payroll_run_id"], unique=False)
    op.create_index(op.f("ix_payroll_export_batches_status"), "payroll_export_batches", ["status"], unique=False)

    op.create_table(
        "payroll_run_audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payroll_run_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["payroll_run_id"], ["payroll_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payroll_run_audit_logs_action"), "payroll_run_audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_payroll_run_audit_logs_id"), "payroll_run_audit_logs", ["id"], unique=False)
    op.create_index(op.f("ix_payroll_run_audit_logs_payroll_run_id"), "payroll_run_audit_logs", ["payroll_run_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_payroll_run_audit_logs_payroll_run_id"), table_name="payroll_run_audit_logs")
    op.drop_index(op.f("ix_payroll_run_audit_logs_id"), table_name="payroll_run_audit_logs")
    op.drop_index(op.f("ix_payroll_run_audit_logs_action"), table_name="payroll_run_audit_logs")
    op.drop_table("payroll_run_audit_logs")
    op.drop_index(op.f("ix_payroll_export_batches_status"), table_name="payroll_export_batches")
    op.drop_index(op.f("ix_payroll_export_batches_payroll_run_id"), table_name="payroll_export_batches")
    op.drop_index(op.f("ix_payroll_export_batches_id"), table_name="payroll_export_batches")
    op.drop_index(op.f("ix_payroll_export_batches_export_type"), table_name="payroll_export_batches")
    op.drop_table("payroll_export_batches")
    op.drop_index(op.f("ix_payroll_variance_items_payroll_run_id"), table_name="payroll_variance_items")
    op.drop_index(op.f("ix_payroll_variance_items_id"), table_name="payroll_variance_items")
    op.drop_index(op.f("ix_payroll_variance_items_employee_id"), table_name="payroll_variance_items")
    op.drop_table("payroll_variance_items")
