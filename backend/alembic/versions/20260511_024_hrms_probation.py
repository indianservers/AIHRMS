"""Add HRMS probation workflow."""

from alembic import op
import sqlalchemy as sa


revision = "20260511_024"
down_revision = "20260511_023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("employees", sa.Column("probation_start_date", sa.Date(), nullable=True))
    op.add_column("employees", sa.Column("probation_end_date", sa.Date(), nullable=True))
    op.add_column("employees", sa.Column("probation_status", sa.String(length=30), nullable=True, server_default="on_probation"))
    op.create_index("ix_employees_probation_status", "employees", ["probation_status"])

    op.create_table(
        "probation_reviews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("manager_id", sa.Integer(), nullable=True),
        sa.Column("review_date", sa.Date(), nullable=False),
        sa.Column("performance_rating", sa.Integer(), nullable=True),
        sa.Column("conduct_rating", sa.Integer(), nullable=True),
        sa.Column("attendance_rating", sa.Integer(), nullable=True),
        sa.Column("recommendation", sa.String(length=30), nullable=False),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["manager_id"], ["employees.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_probation_reviews_id", "probation_reviews", ["id"])
    op.create_index("ix_probation_reviews_employee_id", "probation_reviews", ["employee_id"])
    op.create_index("ix_probation_reviews_manager_id", "probation_reviews", ["manager_id"])
    op.create_index("ix_probation_reviews_organization_id", "probation_reviews", ["organization_id"])
    op.create_index("ix_probation_reviews_status", "probation_reviews", ["status"])

    op.create_table(
        "probation_actions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("action_type", sa.String(length=30), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("extended_until", sa.Date(), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("letter_generated", sa.Boolean(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_probation_actions_id", "probation_actions", ["id"])
    op.create_index("ix_probation_actions_employee_id", "probation_actions", ["employee_id"])
    op.create_index("ix_probation_actions_organization_id", "probation_actions", ["organization_id"])
    op.create_index("ix_probation_actions_action_type", "probation_actions", ["action_type"])


def downgrade() -> None:
    op.drop_index("ix_probation_actions_action_type", table_name="probation_actions")
    op.drop_index("ix_probation_actions_organization_id", table_name="probation_actions")
    op.drop_index("ix_probation_actions_employee_id", table_name="probation_actions")
    op.drop_index("ix_probation_actions_id", table_name="probation_actions")
    op.drop_table("probation_actions")
    op.drop_index("ix_probation_reviews_status", table_name="probation_reviews")
    op.drop_index("ix_probation_reviews_organization_id", table_name="probation_reviews")
    op.drop_index("ix_probation_reviews_manager_id", table_name="probation_reviews")
    op.drop_index("ix_probation_reviews_employee_id", table_name="probation_reviews")
    op.drop_index("ix_probation_reviews_id", table_name="probation_reviews")
    op.drop_table("probation_reviews")
    op.drop_index("ix_employees_probation_status", table_name="employees")
    op.drop_column("employees", "probation_status")
    op.drop_column("employees", "probation_end_date")
    op.drop_column("employees", "probation_start_date")
