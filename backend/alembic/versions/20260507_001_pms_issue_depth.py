"""add pms issue planning fields

Revision ID: 20260507_001
Revises: 20260503_010
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260507_001"
down_revision = "20260503_010"
branch_labels = None
depends_on = None


def _has_table(conn, name):
    return conn.dialect.has_table(conn, name)


def _has_column(conn, table, col):
    insp = sa.inspect(conn)
    return col in [c["name"] for c in insp.get_columns(table)]


def _has_index(conn, table, index_name):
    insp = sa.inspect(conn)
    return index_name in {item["name"] for item in insp.get_indexes(table)}


def _add_column_if_missing(conn, table, column):
    if not _has_column(conn, table, column.name):
        op.add_column(table, column)


def upgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn, "pms_tasks"):
        return

    columns = [
        sa.Column("work_type", sa.String(length=40), server_default="Task"),
        sa.Column("epic_key", sa.String(length=60)),
        sa.Column("initiative", sa.String(length=160)),
        sa.Column("component", sa.String(length=120)),
        sa.Column("severity", sa.String(length=20)),
        sa.Column("environment", sa.String(length=80)),
        sa.Column("affected_version", sa.String(length=80)),
        sa.Column("fix_version", sa.String(length=80)),
        sa.Column("release_name", sa.String(length=120)),
        sa.Column("original_estimate_hours", sa.Numeric(8, 2)),
        sa.Column("remaining_estimate_hours", sa.Numeric(8, 2)),
        sa.Column("rank", sa.Integer()),
        sa.Column("security_level", sa.String(length=40), server_default="Internal"),
        sa.Column("development_branch", sa.String(length=200)),
        sa.Column("development_commits", sa.Integer(), server_default="0"),
        sa.Column("development_prs", sa.Integer(), server_default="0"),
        sa.Column("development_deployments", sa.Integer(), server_default="0"),
        sa.Column("development_build", sa.String(length=30), server_default="Pending"),
    ]
    for column in columns:
        _add_column_if_missing(conn, "pms_tasks", column)

    indexes = [
        ("ix_pms_tasks_work_type", ["work_type"]),
        ("ix_pms_tasks_epic_key", ["epic_key"]),
        ("ix_pms_tasks_component", ["component"]),
        ("ix_pms_tasks_severity", ["severity"]),
        ("ix_pms_tasks_fix_version", ["fix_version"]),
        ("ix_pms_tasks_release_name", ["release_name"]),
        ("ix_pms_tasks_rank", ["rank"]),
        ("ix_pms_tasks_security_level", ["security_level"]),
        ("ix_pms_tasks_development_build", ["development_build"]),
    ]
    for index_name, column_names in indexes:
        if not _has_index(conn, "pms_tasks", index_name):
            op.create_index(index_name, "pms_tasks", column_names)


def downgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn, "pms_tasks"):
        return

    for index_name in [
        "ix_pms_tasks_development_build",
        "ix_pms_tasks_security_level",
        "ix_pms_tasks_rank",
        "ix_pms_tasks_release_name",
        "ix_pms_tasks_fix_version",
        "ix_pms_tasks_severity",
        "ix_pms_tasks_component",
        "ix_pms_tasks_epic_key",
        "ix_pms_tasks_work_type",
    ]:
        if _has_index(conn, "pms_tasks", index_name):
            op.drop_index(index_name, table_name="pms_tasks")

    for column_name in [
        "development_build",
        "development_deployments",
        "development_prs",
        "development_commits",
        "development_branch",
        "security_level",
        "rank",
        "remaining_estimate_hours",
        "original_estimate_hours",
        "release_name",
        "fix_version",
        "affected_version",
        "environment",
        "severity",
        "component",
        "initiative",
        "epic_key",
        "work_type",
    ]:
        if _has_column(conn, "pms_tasks", column_name):
            op.drop_column("pms_tasks", column_name)

