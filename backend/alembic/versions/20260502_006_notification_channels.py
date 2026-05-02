"""add notification channel fanout fields

Revision ID: 20260502_006
Revises: 20260502_005
Create Date: 2026-05-02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260502_006"
down_revision = "20260502_005"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _has_index(table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _has_column("notifications", "channels"):
        op.add_column("notifications", sa.Column("channels", sa.JSON(), nullable=True))
    op.execute("UPDATE notifications SET channels = '[\"in_app\"]' WHERE channels IS NULL")
    if not _has_index("notification_delivery_logs", "idx_notification_delivery_channel_status"):
        op.create_index(
            "idx_notification_delivery_channel_status",
            "notification_delivery_logs",
            ["channel", "status", "attempted_at"],
            unique=False,
        )


def downgrade() -> None:
    if _has_index("notification_delivery_logs", "idx_notification_delivery_channel_status"):
        op.drop_index("idx_notification_delivery_channel_status", table_name="notification_delivery_logs")
    if _has_column("notifications", "channels"):
        op.drop_column("notifications", "channels")
