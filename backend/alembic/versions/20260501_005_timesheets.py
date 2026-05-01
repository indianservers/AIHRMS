"""technology services timesheets

Revision ID: 20260501_005
Revises: 20260501_004
Create Date: 2026-05-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260501_005"
down_revision = "20260501_004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("client_name", sa.String(length=200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("is_billable", sa.Boolean(), nullable=True),
        sa.Column("owner_employee_id", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_employee_id"], ["employees.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_code"), "projects", ["code"], unique=True)
    op.create_index(op.f("ix_projects_id"), "projects", ["id"], unique=False)
    op.create_index(op.f("ix_projects_name"), "projects", ["name"], unique=False)
    op.create_index(op.f("ix_projects_status"), "projects", ["status"], unique=False)

    op.create_table(
        "timesheets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("total_hours", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("billable_hours", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("non_billable_hours", sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_remarks", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_timesheets_employee_id"), "timesheets", ["employee_id"], unique=False)
    op.create_index(op.f("ix_timesheets_id"), "timesheets", ["id"], unique=False)
    op.create_index(op.f("ix_timesheets_period_start"), "timesheets", ["period_start"], unique=False)
    op.create_index(op.f("ix_timesheets_project_id"), "timesheets", ["project_id"], unique=False)
    op.create_index(op.f("ix_timesheets_status"), "timesheets", ["status"], unique=False)
    op.create_unique_constraint(
        "uq_timesheets_employee_project_period",
        "timesheets",
        ["employee_id", "project_id", "period_start", "period_end"],
    )

    op.create_table(
        "timesheet_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timesheet_id", sa.Integer(), nullable=False),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column("hours", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.Column("is_billable", sa.Boolean(), nullable=True),
        sa.Column("task_name", sa.String(length=200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["timesheet_id"], ["timesheets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_timesheet_entries_id"), "timesheet_entries", ["id"], unique=False)
    op.create_index(op.f("ix_timesheet_entries_timesheet_id"), "timesheet_entries", ["timesheet_id"], unique=False)
    op.create_index(op.f("ix_timesheet_entries_work_date"), "timesheet_entries", ["work_date"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_timesheet_entries_work_date"), table_name="timesheet_entries")
    op.drop_index(op.f("ix_timesheet_entries_timesheet_id"), table_name="timesheet_entries")
    op.drop_index(op.f("ix_timesheet_entries_id"), table_name="timesheet_entries")
    op.drop_table("timesheet_entries")
    op.drop_constraint("uq_timesheets_employee_project_period", "timesheets", type_="unique")
    op.drop_index(op.f("ix_timesheets_status"), table_name="timesheets")
    op.drop_index(op.f("ix_timesheets_project_id"), table_name="timesheets")
    op.drop_index(op.f("ix_timesheets_period_start"), table_name="timesheets")
    op.drop_index(op.f("ix_timesheets_id"), table_name="timesheets")
    op.drop_index(op.f("ix_timesheets_employee_id"), table_name="timesheets")
    op.drop_table("timesheets")
    op.drop_index(op.f("ix_projects_status"), table_name="projects")
    op.drop_index(op.f("ix_projects_name"), table_name="projects")
    op.drop_index(op.f("ix_projects_id"), table_name="projects")
    op.drop_index(op.f("ix_projects_code"), table_name="projects")
    op.drop_table("projects")
