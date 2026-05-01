"""employee lifecycle events

Revision ID: 20260501_001
Revises: 20260430_003
Create Date: 2026-05-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260501_001"
down_revision = "20260430_003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employee_lifecycle_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=True),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("from_status", sa.String(length=30), nullable=True),
        sa.Column("to_status", sa.String(length=30), nullable=True),
        sa.Column("from_branch_id", sa.Integer(), nullable=True),
        sa.Column("to_branch_id", sa.Integer(), nullable=True),
        sa.Column("from_department_id", sa.Integer(), nullable=True),
        sa.Column("to_department_id", sa.Integer(), nullable=True),
        sa.Column("from_designation_id", sa.Integer(), nullable=True),
        sa.Column("to_designation_id", sa.Integer(), nullable=True),
        sa.Column("from_manager_id", sa.Integer(), nullable=True),
        sa.Column("to_manager_id", sa.Integer(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["from_branch_id"], ["branches.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["from_department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["from_designation_id"], ["designations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["from_manager_id"], ["employees.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["to_branch_id"], ["branches.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["to_department_id"], ["departments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["to_designation_id"], ["designations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["to_manager_id"], ["employees.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_employee_lifecycle_events_employee_id"), "employee_lifecycle_events", ["employee_id"], unique=False)
    op.create_index(op.f("ix_employee_lifecycle_events_event_type"), "employee_lifecycle_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_employee_lifecycle_events_id"), "employee_lifecycle_events", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_employee_lifecycle_events_id"), table_name="employee_lifecycle_events")
    op.drop_index(op.f("ix_employee_lifecycle_events_event_type"), table_name="employee_lifecycle_events")
    op.drop_index(op.f("ix_employee_lifecycle_events_employee_id"), table_name="employee_lifecycle_events")
    op.drop_table("employee_lifecycle_events")
