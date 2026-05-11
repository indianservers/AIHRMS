"""Add PMS roadmap epic fields.

Revision ID: 20260511_018
Revises: 20260511_017
Create Date: 2026-05-11
"""
from alembic import op
import sqlalchemy as sa


revision = "20260511_018"
down_revision = "20260511_017"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("pms_epics") as batch_op:
        batch_op.add_column(sa.Column("organization_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("end_date", sa.Date(), nullable=True))
    op.create_index("ix_pms_epics_organization_id", "pms_epics", ["organization_id"])
    op.create_index("ix_pms_epics_end_date", "pms_epics", ["end_date"])
    op.execute("UPDATE pms_epics SET end_date = target_date WHERE end_date IS NULL")


def downgrade():
    op.drop_index("ix_pms_epics_end_date", table_name="pms_epics")
    op.drop_index("ix_pms_epics_organization_id", table_name="pms_epics")
    with op.batch_alter_table("pms_epics") as batch_op:
        batch_op.drop_column("end_date")
        batch_op.drop_column("organization_id")
