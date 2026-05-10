"""add pms epics components releases

Revision ID: 20260507_002
Revises: 20260507_001
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260507_002"
down_revision = "20260507_001"
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

    if not _has_table(conn, "pms_epics"):
        op.create_table(
            "pms_epics",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), sa.ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False),
            sa.Column("epic_key", sa.String(length=60), nullable=False),
            sa.Column("name", sa.String(length=180), nullable=False),
            sa.Column("description", sa.Text()),
            sa.Column("status", sa.String(length=40), server_default="Planned"),
            sa.Column("owner_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
            sa.Column("color", sa.String(length=30)),
            sa.Column("start_date", sa.Date()),
            sa.Column("target_date", sa.Date()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True)),
            sa.Column("deleted_at", sa.DateTime(timezone=True)),
            sa.UniqueConstraint("project_id", "epic_key", name="uq_pms_epic_project_key"),
        )
    if not _has_table(conn, "pms_components"):
        op.create_table(
            "pms_components",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), sa.ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("description", sa.Text()),
            sa.Column("lead_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
            sa.Column("default_assignee_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
            sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True)),
            sa.UniqueConstraint("project_id", "name", name="uq_pms_component_project_name"),
        )
    if not _has_table(conn, "pms_releases"):
        op.create_table(
            "pms_releases",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), sa.ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("description", sa.Text()),
            sa.Column("status", sa.String(length=40), server_default="Planning"),
            sa.Column("release_date", sa.Date()),
            sa.Column("owner_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
            sa.Column("readiness_percent", sa.Integer(), server_default="0"),
            sa.Column("launch_notes", sa.Text()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True)),
            sa.Column("deleted_at", sa.DateTime(timezone=True)),
            sa.UniqueConstraint("project_id", "name", name="uq_pms_release_project_name"),
        )

    for table, indexes in {
        "pms_epics": [
            ("ix_pms_epics_project_id", ["project_id"]),
            ("ix_pms_epics_epic_key", ["epic_key"]),
            ("ix_pms_epics_status", ["status"]),
            ("ix_pms_epics_owner_user_id", ["owner_user_id"]),
            ("ix_pms_epics_target_date", ["target_date"]),
        ],
        "pms_components": [
            ("ix_pms_components_project_id", ["project_id"]),
            ("ix_pms_components_name", ["name"]),
            ("ix_pms_components_lead_user_id", ["lead_user_id"]),
            ("ix_pms_components_default_assignee_user_id", ["default_assignee_user_id"]),
            ("ix_pms_components_is_active", ["is_active"]),
        ],
        "pms_releases": [
            ("ix_pms_releases_project_id", ["project_id"]),
            ("ix_pms_releases_name", ["name"]),
            ("ix_pms_releases_status", ["status"]),
            ("ix_pms_releases_release_date", ["release_date"]),
            ("ix_pms_releases_owner_user_id", ["owner_user_id"]),
        ],
    }.items():
        for index_name, column_names in indexes:
            if _has_table(conn, table) and not _has_index(conn, table, index_name):
                op.create_index(index_name, table, column_names)

    if _has_table(conn, "pms_tasks"):
        for column in [
            sa.Column("epic_id", sa.Integer(), sa.ForeignKey("pms_epics.id", ondelete="SET NULL")),
            sa.Column("component_id", sa.Integer(), sa.ForeignKey("pms_components.id", ondelete="SET NULL")),
            sa.Column("release_id", sa.Integer(), sa.ForeignKey("pms_releases.id", ondelete="SET NULL")),
        ]:
            _add_column_if_missing(conn, "pms_tasks", column)
        for index_name, column_names in [
            ("ix_pms_tasks_epic_id", ["epic_id"]),
            ("ix_pms_tasks_component_id", ["component_id"]),
            ("ix_pms_tasks_release_id", ["release_id"]),
        ]:
            if not _has_index(conn, "pms_tasks", index_name):
                op.create_index(index_name, "pms_tasks", column_names)


def downgrade() -> None:
    conn = op.get_bind()
    if _has_table(conn, "pms_tasks"):
        for index_name in ["ix_pms_tasks_release_id", "ix_pms_tasks_component_id", "ix_pms_tasks_epic_id"]:
            if _has_index(conn, "pms_tasks", index_name):
                op.drop_index(index_name, table_name="pms_tasks")
        for column_name in ["release_id", "component_id", "epic_id"]:
            if _has_column(conn, "pms_tasks", column_name):
                op.drop_column("pms_tasks", column_name)

    for table in ["pms_releases", "pms_components", "pms_epics"]:
        if _has_table(conn, table):
            op.drop_table(table)

