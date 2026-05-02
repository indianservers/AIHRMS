"""add leave type accrual frequency

Revision ID: 20260502_007
Revises: 20260502_006
Create Date: 2026-05-02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260502_007"
down_revision = "20260502_006"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    if not _has_column("leave_types", "accrual_frequency"):
        op.add_column(
            "leave_types",
            sa.Column("accrual_frequency", sa.String(length=20), nullable=False, server_default="annual"),
        )
    op.execute(
        """
        UPDATE leave_types
        SET accrual_frequency = CASE
            WHEN code IN ('CL', 'SL', 'EL') THEN 'monthly'
            ELSE 'annual'
        END
        WHERE accrual_frequency IS NULL OR accrual_frequency = 'annual'
        """
    )


def downgrade() -> None:
    if _has_column("leave_types", "accrual_frequency"):
        op.drop_column("leave_types", "accrual_frequency")
