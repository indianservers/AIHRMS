"""Add PMS user capacity.

Revision ID: 20260511_019
Revises: 20260511_018
Create Date: 2026-05-11
"""
from alembic import op
import sqlalchemy as sa


revision = "20260511_019"
down_revision = "20260511_018"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pms_user_capacity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("week_start_date", sa.Date(), nullable=False),
        sa.Column("capacity_hours", sa.Numeric(8, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "user_id", "week_start_date", name="uq_pms_user_capacity_week"),
    )
    op.create_index("ix_pms_user_capacity_id", "pms_user_capacity", ["id"])
    op.create_index("ix_pms_user_capacity_organization_id", "pms_user_capacity", ["organization_id"])
    op.create_index("ix_pms_user_capacity_user_id", "pms_user_capacity", ["user_id"])
    op.create_index("ix_pms_user_capacity_week_start_date", "pms_user_capacity", ["week_start_date"])


def downgrade():
    op.drop_index("ix_pms_user_capacity_week_start_date", table_name="pms_user_capacity")
    op.drop_index("ix_pms_user_capacity_user_id", table_name="pms_user_capacity")
    op.drop_index("ix_pms_user_capacity_organization_id", table_name="pms_user_capacity")
    op.drop_index("ix_pms_user_capacity_id", table_name="pms_user_capacity")
    op.drop_table("pms_user_capacity")
