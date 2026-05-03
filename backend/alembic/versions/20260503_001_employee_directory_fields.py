"""add employee directory fields

Revision ID: 20260503_001
Revises: 20260502_007
Create Date: 2026-05-03
"""

from alembic import op
import sqlalchemy as sa


revision = "20260503_001"
down_revision = "20260502_007"
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
        op.create_index(index_name, table_name, columns)


def upgrade() -> None:
    _add_column_if_missing("employees", sa.Column("work_email", sa.String(length=150), nullable=True))
    _add_column_if_missing("employees", sa.Column("office_extension", sa.String(length=20), nullable=True))
    _add_column_if_missing("employees", sa.Column("desk_code", sa.String(length=50), nullable=True))
    _add_column_if_missing("employees", sa.Column("timezone", sa.String(length=80), nullable=True, server_default="Asia/Kolkata"))
    _add_column_if_missing("employees", sa.Column("manager_chain_path", sa.String(length=500), nullable=True))
    _add_column_if_missing("employees", sa.Column("preferred_display_name", sa.String(length=150), nullable=True))
    _add_column_if_missing("employees", sa.Column("directory_visibility", sa.String(length=20), nullable=True, server_default="public"))
    _add_column_if_missing("employees", sa.Column("skills_tags", sa.Text(), nullable=True))
    _add_column_if_missing("employees", sa.Column("profile_completeness", sa.Integer(), nullable=True, server_default="0"))

    op.execute("UPDATE employees SET directory_visibility = 'public' WHERE directory_visibility IS NULL")
    op.execute("UPDATE employees SET timezone = 'Asia/Kolkata' WHERE timezone IS NULL")
    op.execute("UPDATE employees SET profile_completeness = 0 WHERE profile_completeness IS NULL")

    _create_index_if_missing("ix_employees_work_email", "employees", ["work_email"])
    _create_index_if_missing("ix_employees_directory_visibility", "employees", ["directory_visibility"])
    _create_index_if_missing("idx_employees_name", "employees", ["first_name", "last_name"])
    _create_index_if_missing("idx_employees_directory_email", "employees", ["work_email", "personal_email"])
    _create_index_if_missing("idx_employees_department_status", "employees", ["department_id", "status", "deleted_at"])
    _create_index_if_missing("idx_employees_manager_status", "employees", ["reporting_manager_id", "status", "deleted_at"])


def downgrade() -> None:
    for index_name in [
        "idx_employees_manager_status",
        "idx_employees_department_status",
        "idx_employees_directory_email",
        "idx_employees_name",
        "ix_employees_directory_visibility",
        "ix_employees_work_email",
    ]:
        if _has_index("employees", index_name):
            op.drop_index(index_name, table_name="employees")

    for column_name in [
        "profile_completeness",
        "skills_tags",
        "directory_visibility",
        "preferred_display_name",
        "manager_chain_path",
        "timezone",
        "desk_code",
        "office_extension",
        "work_email",
    ]:
        if _has_column("employees", column_name):
            op.drop_column("employees", column_name)
