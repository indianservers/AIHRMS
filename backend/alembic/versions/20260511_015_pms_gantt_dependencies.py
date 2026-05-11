"""pms gantt dependencies

Revision ID: 20260511_015_pms_gantt_dependencies
Revises: 20260511_014_crm_outbound_webhooks
Create Date: 2026-05-11 00:15:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_015_pms_gantt_dependencies"
down_revision = "20260511_014_crm_outbound_webhooks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("pms_task_dependencies", sa.Column("lag_days", sa.Integer(), nullable=True, server_default="0"))


def downgrade() -> None:
    op.drop_column("pms_task_dependencies", "lag_days")
