"""add pms sprint lifecycle filters and activity

Revision ID: 20260507_003
Revises: 20260507_002
Create Date: 2026-05-07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260507_003"
down_revision = "20260507_002"
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
    if _has_table(conn, "pms_sprints"):
        for column in [
            sa.Column("committed_task_count", sa.Integer(), server_default="0"),
            sa.Column("committed_story_points", sa.Integer(), server_default="0"),
            sa.Column("completed_story_points", sa.Integer(), server_default="0"),
            sa.Column("scope_change_count", sa.Integer(), server_default="0"),
            sa.Column("carry_forward_task_count", sa.Integer(), server_default="0"),
            sa.Column("started_at", sa.DateTime(timezone=True)),
            sa.Column("completed_at", sa.DateTime(timezone=True)),
            sa.Column("commitment_snapshot", sa.Text()),
            sa.Column("completion_summary", sa.Text()),
        ]:
            _add_column_if_missing(conn, "pms_sprints", column)

    if not _has_table(conn, "pms_saved_filters"):
        op.create_table(
            "pms_saved_filters",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), sa.ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE")),
            sa.Column("name", sa.String(length=140), nullable=False),
            sa.Column("view_type", sa.String(length=40), server_default="board"),
            sa.Column("query", sa.Text(), nullable=False),
            sa.Column("is_shared", sa.Boolean(), server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True)),
            sa.UniqueConstraint("project_id", "user_id", "name", name="uq_pms_saved_filter_owner_name"),
        )
    if not _has_table(conn, "pms_activities"):
        op.create_table(
            "pms_activities",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), sa.ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False),
            sa.Column("task_id", sa.Integer(), sa.ForeignKey("pms_tasks.id", ondelete="CASCADE")),
            sa.Column("sprint_id", sa.Integer(), sa.ForeignKey("pms_sprints.id", ondelete="SET NULL")),
            sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
            sa.Column("action", sa.String(length=80), nullable=False),
            sa.Column("entity_type", sa.String(length=40), nullable=False),
            sa.Column("entity_id", sa.Integer()),
            sa.Column("summary", sa.String(length=300), nullable=False),
            sa.Column("metadata_json", sa.Text()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    for table, indexes in {
        "pms_saved_filters": [
            ("ix_pms_saved_filters_project_id", ["project_id"]),
            ("ix_pms_saved_filters_user_id", ["user_id"]),
            ("ix_pms_saved_filters_view_type", ["view_type"]),
            ("ix_pms_saved_filters_is_shared", ["is_shared"]),
        ],
        "pms_activities": [
            ("ix_pms_activities_project_id", ["project_id"]),
            ("ix_pms_activities_task_id", ["task_id"]),
            ("ix_pms_activities_sprint_id", ["sprint_id"]),
            ("ix_pms_activities_actor_user_id", ["actor_user_id"]),
            ("ix_pms_activities_action", ["action"]),
            ("ix_pms_activities_entity_type", ["entity_type"]),
            ("ix_pms_activities_entity_id", ["entity_id"]),
            ("ix_pms_activities_created_at", ["created_at"]),
        ],
    }.items():
        if _has_table(conn, table):
            for index_name, column_names in indexes:
                if not _has_index(conn, table, index_name):
                    op.create_index(index_name, table, column_names)


def downgrade() -> None:
    conn = op.get_bind()
    for table in ["pms_activities", "pms_saved_filters"]:
        if _has_table(conn, table):
            op.drop_table(table)
    if _has_table(conn, "pms_sprints"):
        for column_name in [
            "completion_summary",
            "commitment_snapshot",
            "completed_at",
            "started_at",
            "carry_forward_task_count",
            "scope_change_count",
            "completed_story_points",
            "committed_story_points",
            "committed_task_count",
        ]:
            if _has_column(conn, "pms_sprints", column_name):
                op.drop_column("pms_sprints", column_name)
