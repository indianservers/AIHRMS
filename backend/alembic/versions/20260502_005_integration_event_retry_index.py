"""add integration event retry index

Revision ID: 20260502_005
Revises: 20260502_004
Create Date: 2026-05-02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260502_005"
down_revision = "20260502_004"
branch_labels = None
depends_on = None


def _has_index(table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _has_index("integration_events", "idx_integration_event_type_status_retry"):
        op.create_index(
            "idx_integration_event_type_status_retry",
            "integration_events",
            ["event_type", "status", "next_retry_at"],
            unique=False,
        )


def downgrade() -> None:
    if _has_index("integration_events", "idx_integration_event_type_status_retry"):
        op.drop_index("idx_integration_event_type_status_retry", table_name="integration_events")
