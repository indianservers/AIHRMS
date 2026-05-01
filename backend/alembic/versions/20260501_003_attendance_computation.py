"""attendance computation foundation

Revision ID: 20260501_003
Revises: 20260501_002
Create Date: 2026-05-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260501_003"
down_revision = "20260501_002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shift_weekly_offs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("shift_id", sa.Integer(), nullable=False),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("week_pattern", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["shift_id"], ["shifts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_shift_weekly_offs_id"), "shift_weekly_offs", ["id"], unique=False)
    op.create_index(op.f("ix_shift_weekly_offs_shift_id"), "shift_weekly_offs", ["shift_id"], unique=False)

    op.create_table(
        "shift_roster_assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("shift_id", sa.Integer(), nullable=False),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["shift_id"], ["shifts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_shift_roster_assignments_employee_id"), "shift_roster_assignments", ["employee_id"], unique=False)
    op.create_index(op.f("ix_shift_roster_assignments_id"), "shift_roster_assignments", ["id"], unique=False)
    op.create_index(op.f("ix_shift_roster_assignments_shift_id"), "shift_roster_assignments", ["shift_id"], unique=False)
    op.create_index(op.f("ix_shift_roster_assignments_work_date"), "shift_roster_assignments", ["work_date"], unique=False)

    op.add_column("attendances", sa.Column("shift_id", sa.Integer(), nullable=True))
    op.add_column("attendances", sa.Column("late_minutes", sa.Integer(), nullable=True))
    op.add_column("attendances", sa.Column("early_exit_minutes", sa.Integer(), nullable=True))
    op.add_column("attendances", sa.Column("short_minutes", sa.Integer(), nullable=True))
    op.add_column("attendances", sa.Column("is_late", sa.Boolean(), nullable=True))
    op.add_column("attendances", sa.Column("is_early_exit", sa.Boolean(), nullable=True))
    op.add_column("attendances", sa.Column("is_short_hours", sa.Boolean(), nullable=True))
    op.add_column("attendances", sa.Column("computed_at", sa.DateTime(timezone=True), nullable=True))
    op.create_foreign_key("fk_attendances_shift_id_shifts", "attendances", "shifts", ["shift_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    op.drop_constraint("fk_attendances_shift_id_shifts", "attendances", type_="foreignkey")
    op.drop_column("attendances", "computed_at")
    op.drop_column("attendances", "is_short_hours")
    op.drop_column("attendances", "is_early_exit")
    op.drop_column("attendances", "is_late")
    op.drop_column("attendances", "short_minutes")
    op.drop_column("attendances", "early_exit_minutes")
    op.drop_column("attendances", "late_minutes")
    op.drop_column("attendances", "shift_id")
    op.drop_index(op.f("ix_shift_roster_assignments_work_date"), table_name="shift_roster_assignments")
    op.drop_index(op.f("ix_shift_roster_assignments_shift_id"), table_name="shift_roster_assignments")
    op.drop_index(op.f("ix_shift_roster_assignments_id"), table_name="shift_roster_assignments")
    op.drop_index(op.f("ix_shift_roster_assignments_employee_id"), table_name="shift_roster_assignments")
    op.drop_table("shift_roster_assignments")
    op.drop_index(op.f("ix_shift_weekly_offs_shift_id"), table_name="shift_weekly_offs")
    op.drop_index(op.f("ix_shift_weekly_offs_id"), table_name="shift_weekly_offs")
    op.drop_table("shift_weekly_offs")
