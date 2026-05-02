"""tenant first high frequency indexes

Revision ID: 20260502_003
Revises: 20260502_002
Create Date: 2026-05-02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260502_003"
down_revision = "20260502_002"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _has_index(table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if not _has_column(table_name, column.name):
        op.add_column(table_name, column)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    if not _has_index(table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    _add_column_if_missing("leave_requests", sa.Column("company_id", sa.Integer(), nullable=True))
    _add_column_if_missing("notifications", sa.Column("company_id", sa.Integer(), nullable=True))

    op.execute(
        """
        UPDATE leave_requests
        SET company_id = (
            SELECT branches.company_id
            FROM employees
            JOIN branches ON branches.id = employees.branch_id
            WHERE employees.id = leave_requests.employee_id
        )
        WHERE company_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE notifications
        SET company_id = (
            SELECT branches.company_id
            FROM users
            JOIN employees ON employees.user_id = users.id
            JOIN branches ON branches.id = employees.branch_id
            WHERE users.id = notifications.user_id
        )
        WHERE company_id IS NULL
        """
    )

    _create_index_if_missing("idx_leave_request_company_status", "leave_requests", ["company_id", "status", "employee_id"])
    _create_index_if_missing("idx_leave_request_company_active_status", "leave_requests", ["company_id", "deleted_at", "status", "employee_id"])
    _create_index_if_missing("idx_payroll_run_company_active_month", "payroll_runs", ["company_id", "deleted_at", "year", "month"])
    _create_index_if_missing("idx_payroll_run_company_status_month", "payroll_runs", ["company_id", "status", "year", "month"])
    _create_index_if_missing("idx_notifications_company_user_unread", "notifications", ["company_id", "user_id", "is_read", "created_at"])
    _create_index_if_missing("idx_notifications_company_module", "notifications", ["company_id", "module", "created_at"])


def downgrade() -> None:
    for index_name, table_name in [
        ("idx_notifications_company_module", "notifications"),
        ("idx_notifications_company_user_unread", "notifications"),
        ("idx_payroll_run_company_status_month", "payroll_runs"),
        ("idx_payroll_run_company_active_month", "payroll_runs"),
        ("idx_leave_request_company_active_status", "leave_requests"),
        ("idx_leave_request_company_status", "leave_requests"),
    ]:
        if _has_index(table_name, index_name):
            op.drop_index(index_name, table_name=table_name)

    for table_name, column_name in [
        ("notifications", "company_id"),
        ("leave_requests", "company_id"),
    ]:
        if _has_column(table_name, column_name):
            op.drop_column(table_name, column_name)
