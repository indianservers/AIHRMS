"""database scale controls

Revision ID: 20260502_001
Revises: 20260501_006
Create Date: 2026-05-02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260502_001"
down_revision = "20260501_006"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _has_index(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if not _has_column(table_name, column.name):
        op.add_column(table_name, column)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    if not _has_index(table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    _add_column_if_missing("employees", sa.Column("salary_currency", sa.String(length=3), nullable=True, server_default="INR"))
    _add_column_if_missing("employees", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    _add_column_if_missing("employees", sa.Column("deleted_by", sa.Integer(), nullable=True))

    _add_column_if_missing("leave_requests", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    _add_column_if_missing("leave_requests", sa.Column("deleted_by", sa.Integer(), nullable=True))

    _add_column_if_missing("payroll_runs", sa.Column("company_id", sa.Integer(), nullable=True))
    _add_column_if_missing("payroll_runs", sa.Column("pay_period_start", sa.Date(), nullable=True))
    _add_column_if_missing("payroll_runs", sa.Column("pay_period_end", sa.Date(), nullable=True))
    _add_column_if_missing("payroll_runs", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    _add_column_if_missing("payroll_runs", sa.Column("deleted_by", sa.Integer(), nullable=True))

    _add_column_if_missing("employee_salaries", sa.Column("effective_date", sa.Date(), nullable=True))
    _add_column_if_missing("salary_components", sa.Column("is_currency_fixed", sa.Boolean(), nullable=True, server_default=sa.true()))

    _create_index_if_missing("idx_attendance_employee_date", "attendances", ["employee_id", "attendance_date"])
    _create_index_if_missing("idx_leave_request_status", "leave_requests", ["status", "employee_id"])
    _create_index_if_missing("idx_leave_request_active_status", "leave_requests", ["deleted_at", "status", "employee_id"])
    _create_index_if_missing("idx_payroll_run_period", "payroll_runs", ["pay_period_start", "pay_period_end", "company_id"])
    _create_index_if_missing("idx_payroll_run_active_month", "payroll_runs", ["deleted_at", "year", "month"])
    _create_index_if_missing("idx_notifications_user_unread", "notifications", ["user_id", "is_read", "created_at"])
    _create_index_if_missing("idx_audit_log_entity", "audit_logs", ["entity_type", "entity_id", "created_at"])
    _create_index_if_missing("idx_employee_salary_effective", "employee_salaries", ["employee_id", "effective_from", "effective_to"])
    _create_index_if_missing("idx_employees_active_status", "employees", ["deleted_at", "status"])


def downgrade() -> None:
    for index_name, table_name in [
        ("idx_employees_active_status", "employees"),
        ("idx_employee_salary_effective", "employee_salaries"),
        ("idx_audit_log_entity", "audit_logs"),
        ("idx_notifications_user_unread", "notifications"),
        ("idx_payroll_run_active_month", "payroll_runs"),
        ("idx_payroll_run_period", "payroll_runs"),
        ("idx_leave_request_active_status", "leave_requests"),
        ("idx_leave_request_status", "leave_requests"),
        ("idx_attendance_employee_date", "attendances"),
    ]:
        if _has_index(table_name, index_name):
            op.drop_index(index_name, table_name=table_name)

    for table_name, column_name in [
        ("salary_components", "is_currency_fixed"),
        ("employee_salaries", "effective_date"),
        ("payroll_runs", "deleted_by"),
        ("payroll_runs", "deleted_at"),
        ("payroll_runs", "pay_period_end"),
        ("payroll_runs", "pay_period_start"),
        ("payroll_runs", "company_id"),
        ("leave_requests", "deleted_by"),
        ("leave_requests", "deleted_at"),
        ("employees", "deleted_by"),
        ("employees", "deleted_at"),
        ("employees", "salary_currency"),
    ]:
        if _has_column(table_name, column_name):
            op.drop_column(table_name, column_name)
