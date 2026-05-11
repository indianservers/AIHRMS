"""Add metadata to employee profile change requests."""

from alembic import op
import sqlalchemy as sa


revision = "20260511_026"
down_revision = "20260511_025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("employee_change_requests", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.add_column("employee_change_requests", sa.Column("field_name", sa.String(length=120), nullable=True))
    op.add_column("employee_change_requests", sa.Column("old_value_json", sa.JSON(), nullable=True))
    op.add_column("employee_change_requests", sa.Column("new_value_json", sa.JSON(), nullable=True))
    op.add_column("employee_change_requests", sa.Column("document_path", sa.String(length=500), nullable=True))
    op.create_index("ix_employee_change_requests_organization_id", "employee_change_requests", ["organization_id"])
    op.create_index("ix_employee_change_requests_field_name", "employee_change_requests", ["field_name"])


def downgrade() -> None:
    op.drop_index("ix_employee_change_requests_field_name", table_name="employee_change_requests")
    op.drop_index("ix_employee_change_requests_organization_id", table_name="employee_change_requests")
    op.drop_column("employee_change_requests", "document_path")
    op.drop_column("employee_change_requests", "new_value_json")
    op.drop_column("employee_change_requests", "old_value_json")
    op.drop_column("employee_change_requests", "field_name")
    op.drop_column("employee_change_requests", "organization_id")
