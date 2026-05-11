"""Add PMS risk register.

Revision ID: 20260511_021
Revises: 20260511_020
Create Date: 2026-05-11
"""
from alembic import op
import sqlalchemy as sa


revision = "20260511_021"
down_revision = "20260511_020"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pms_risks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("linked_task_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=80), nullable=True),
        sa.Column("probability", sa.Integer(), nullable=True),
        sa.Column("impact", sa.Integer(), nullable=True),
        sa.Column("risk_score", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        sa.Column("mitigation_plan", sa.Text(), nullable=True),
        sa.Column("contingency_plan", sa.Text(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["linked_task_id"], ["pms_tasks.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["pms_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pms_risks_id", "pms_risks", ["id"])
    op.create_index("ix_pms_risks_organization_id", "pms_risks", ["organization_id"])
    op.create_index("ix_pms_risks_project_id", "pms_risks", ["project_id"])
    op.create_index("ix_pms_risks_linked_task_id", "pms_risks", ["linked_task_id"])
    op.create_index("ix_pms_risks_category", "pms_risks", ["category"])
    op.create_index("ix_pms_risks_probability", "pms_risks", ["probability"])
    op.create_index("ix_pms_risks_impact", "pms_risks", ["impact"])
    op.create_index("ix_pms_risks_risk_score", "pms_risks", ["risk_score"])
    op.create_index("ix_pms_risks_status", "pms_risks", ["status"])
    op.create_index("ix_pms_risks_owner_user_id", "pms_risks", ["owner_user_id"])
    op.create_index("ix_pms_risks_due_date", "pms_risks", ["due_date"])


def downgrade():
    op.drop_index("ix_pms_risks_due_date", table_name="pms_risks")
    op.drop_index("ix_pms_risks_owner_user_id", table_name="pms_risks")
    op.drop_index("ix_pms_risks_status", table_name="pms_risks")
    op.drop_index("ix_pms_risks_risk_score", table_name="pms_risks")
    op.drop_index("ix_pms_risks_impact", table_name="pms_risks")
    op.drop_index("ix_pms_risks_probability", table_name="pms_risks")
    op.drop_index("ix_pms_risks_category", table_name="pms_risks")
    op.drop_index("ix_pms_risks_linked_task_id", table_name="pms_risks")
    op.drop_index("ix_pms_risks_project_id", table_name="pms_risks")
    op.drop_index("ix_pms_risks_organization_id", table_name="pms_risks")
    op.drop_index("ix_pms_risks_id", table_name="pms_risks")
    op.drop_table("pms_risks")
