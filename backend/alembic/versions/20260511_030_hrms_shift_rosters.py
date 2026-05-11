"""Add HRMS shift rosters

Revision ID: 20260511_030
Revises: 20260511_029
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_030"
down_revision = "20260511_029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shift_rosters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("shift_id", sa.Integer(), nullable=False),
        sa.Column("roster_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("assigned_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["assigned_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["companies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["shift_id"], ["shifts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_shift_rosters_id"), "shift_rosters", ["id"], unique=False)
    op.create_index(op.f("ix_shift_rosters_organization_id"), "shift_rosters", ["organization_id"], unique=False)
    op.create_index(op.f("ix_shift_rosters_employee_id"), "shift_rosters", ["employee_id"], unique=False)
    op.create_index(op.f("ix_shift_rosters_shift_id"), "shift_rosters", ["shift_id"], unique=False)
    op.create_index(op.f("ix_shift_rosters_roster_date"), "shift_rosters", ["roster_date"], unique=False)
    op.create_index(op.f("ix_shift_rosters_status"), "shift_rosters", ["status"], unique=False)
    op.create_index("idx_shift_roster_org_date", "shift_rosters", ["organization_id", "roster_date"], unique=False)
    op.create_index("idx_shift_roster_employee_date", "shift_rosters", ["employee_id", "roster_date"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_shift_roster_employee_date", table_name="shift_rosters")
    op.drop_index("idx_shift_roster_org_date", table_name="shift_rosters")
    op.drop_index(op.f("ix_shift_rosters_status"), table_name="shift_rosters")
    op.drop_index(op.f("ix_shift_rosters_roster_date"), table_name="shift_rosters")
    op.drop_index(op.f("ix_shift_rosters_shift_id"), table_name="shift_rosters")
    op.drop_index(op.f("ix_shift_rosters_employee_id"), table_name="shift_rosters")
    op.drop_index(op.f("ix_shift_rosters_organization_id"), table_name="shift_rosters")
    op.drop_index(op.f("ix_shift_rosters_id"), table_name="shift_rosters")
    op.drop_table("shift_rosters")
