"""Add leave encashment requests and LWP payroll feed."""

from alembic import op
import sqlalchemy as sa


revision = "20260511_025"
down_revision = "20260511_024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leave_encashment_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("leave_type_id", sa.Integer(), nullable=False),
        sa.Column("days_to_encash", sa.Numeric(6, 2), nullable=False),
        sa.Column("encashment_rate", sa.Numeric(12, 2), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payroll_run_id", sa.Integer(), nullable=True),
        sa.Column("leave_encashment_line_id", sa.Integer(), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["leave_encashment_line_id"], ["leave_encashment_lines.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["leave_type_id"], ["leave_types.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["payroll_run_id"], ["payroll_runs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_leave_encashment_requests_id", "leave_encashment_requests", ["id"])
    op.create_index("ix_leave_encashment_requests_organization_id", "leave_encashment_requests", ["organization_id"])
    op.create_index("ix_leave_encashment_requests_employee_id", "leave_encashment_requests", ["employee_id"])
    op.create_index("ix_leave_encashment_requests_leave_type_id", "leave_encashment_requests", ["leave_type_id"])
    op.create_index("ix_leave_encashment_requests_status", "leave_encashment_requests", ["status"])
    op.create_index("ix_leave_encashment_requests_payroll_run_id", "leave_encashment_requests", ["payroll_run_id"])
    op.create_index("ix_leave_encashment_requests_leave_encashment_line_id", "leave_encashment_requests", ["leave_encashment_line_id"])

    op.create_table(
        "payroll_lwp_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("payroll_month", sa.String(length=7), nullable=False),
        sa.Column("lwp_days", sa.Numeric(6, 2), nullable=True),
        sa.Column("source", sa.String(length=40), nullable=True),
        sa.Column("amount_deducted", sa.Numeric(12, 2), nullable=True),
        sa.Column("payroll_run_id", sa.Integer(), nullable=True),
        sa.Column("payroll_attendance_input_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["payroll_attendance_input_id"], ["payroll_attendance_inputs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["payroll_run_id"], ["payroll_runs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_payroll_lwp_entries_id", "payroll_lwp_entries", ["id"])
    op.create_index("ix_payroll_lwp_entries_organization_id", "payroll_lwp_entries", ["organization_id"])
    op.create_index("ix_payroll_lwp_entries_employee_id", "payroll_lwp_entries", ["employee_id"])
    op.create_index("ix_payroll_lwp_entries_payroll_month", "payroll_lwp_entries", ["payroll_month"])
    op.create_index("ix_payroll_lwp_entries_source", "payroll_lwp_entries", ["source"])
    op.create_index("ix_payroll_lwp_entries_payroll_run_id", "payroll_lwp_entries", ["payroll_run_id"])
    op.create_index("ix_payroll_lwp_entries_payroll_attendance_input_id", "payroll_lwp_entries", ["payroll_attendance_input_id"])


def downgrade() -> None:
    op.drop_index("ix_payroll_lwp_entries_payroll_attendance_input_id", table_name="payroll_lwp_entries")
    op.drop_index("ix_payroll_lwp_entries_payroll_run_id", table_name="payroll_lwp_entries")
    op.drop_index("ix_payroll_lwp_entries_source", table_name="payroll_lwp_entries")
    op.drop_index("ix_payroll_lwp_entries_payroll_month", table_name="payroll_lwp_entries")
    op.drop_index("ix_payroll_lwp_entries_employee_id", table_name="payroll_lwp_entries")
    op.drop_index("ix_payroll_lwp_entries_organization_id", table_name="payroll_lwp_entries")
    op.drop_index("ix_payroll_lwp_entries_id", table_name="payroll_lwp_entries")
    op.drop_table("payroll_lwp_entries")

    op.drop_index("ix_leave_encashment_requests_leave_encashment_line_id", table_name="leave_encashment_requests")
    op.drop_index("ix_leave_encashment_requests_payroll_run_id", table_name="leave_encashment_requests")
    op.drop_index("ix_leave_encashment_requests_status", table_name="leave_encashment_requests")
    op.drop_index("ix_leave_encashment_requests_leave_type_id", table_name="leave_encashment_requests")
    op.drop_index("ix_leave_encashment_requests_employee_id", table_name="leave_encashment_requests")
    op.drop_index("ix_leave_encashment_requests_organization_id", table_name="leave_encashment_requests")
    op.drop_index("ix_leave_encashment_requests_id", table_name="leave_encashment_requests")
    op.drop_table("leave_encashment_requests")
