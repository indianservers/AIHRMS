"""pms mentions markdown comments

Revision ID: 20260511_016_pms_mentions_markdown_comments
Revises: 20260511_015_pms_gantt_dependencies
Create Date: 2026-05-11 00:16:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_016_pms_mentions_markdown_comments"
down_revision = "20260511_015_pms_gantt_dependencies"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pms_comments", sa.Column("body_format", sa.String(length=20), nullable=True, server_default="markdown"))
    op.create_index("ix_pms_comments_body_format", "pms_comments", ["body_format"])

    op.create_table(
        "pms_mentions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("comment_id", sa.Integer(), nullable=True),
        sa.Column("mentioned_user_id", sa.Integer(), nullable=False),
        sa.Column("mentioned_by_user_id", sa.Integer(), nullable=True),
        sa.Column("notification_id", sa.Integer(), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["comment_id"], ["pms_comments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mentioned_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["mentioned_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["notification_id"], ["notifications.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["pms_projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["pms_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pms_mentions_id", "pms_mentions", ["id"])
    op.create_index("ix_pms_mentions_project_id", "pms_mentions", ["project_id"])
    op.create_index("ix_pms_mentions_task_id", "pms_mentions", ["task_id"])
    op.create_index("ix_pms_mentions_comment_id", "pms_mentions", ["comment_id"])
    op.create_index("ix_pms_mentions_mentioned_user_id", "pms_mentions", ["mentioned_user_id"])
    op.create_index("ix_pms_mentions_mentioned_by_user_id", "pms_mentions", ["mentioned_by_user_id"])
    op.create_index("ix_pms_mentions_notification_id", "pms_mentions", ["notification_id"])
    op.create_index("ix_pms_mentions_created_at", "pms_mentions", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_pms_mentions_created_at", table_name="pms_mentions")
    op.drop_index("ix_pms_mentions_notification_id", table_name="pms_mentions")
    op.drop_index("ix_pms_mentions_mentioned_by_user_id", table_name="pms_mentions")
    op.drop_index("ix_pms_mentions_mentioned_user_id", table_name="pms_mentions")
    op.drop_index("ix_pms_mentions_comment_id", table_name="pms_mentions")
    op.drop_index("ix_pms_mentions_task_id", table_name="pms_mentions")
    op.drop_index("ix_pms_mentions_project_id", table_name="pms_mentions")
    op.drop_index("ix_pms_mentions_id", table_name="pms_mentions")
    op.drop_table("pms_mentions")
    op.drop_index("ix_pms_comments_body_format", table_name="pms_comments")
    op.drop_column("pms_comments", "body_format")
