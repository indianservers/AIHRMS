"""leave balance ledger

Revision ID: 20260501_002
Revises: 20260501_001
Create Date: 2026-05-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260501_002"
down_revision = "20260501_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leave_balance_ledger",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("leave_type_id", sa.Integer(), nullable=False),
        sa.Column("leave_balance_id", sa.Integer(), nullable=True),
        sa.Column("leave_request_id", sa.Integer(), nullable=True),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("transaction_type", sa.String(length=40), nullable=False),
        sa.Column("amount", sa.Numeric(precision=5, scale=1), nullable=False),
        sa.Column("balance_after", sa.Numeric(precision=5, scale=1), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["leave_balance_id"], ["leave_balances.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["leave_request_id"], ["leave_requests.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["leave_type_id"], ["leave_types.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_leave_balance_ledger_employee_id"), "leave_balance_ledger", ["employee_id"], unique=False)
    op.create_index(op.f("ix_leave_balance_ledger_id"), "leave_balance_ledger", ["id"], unique=False)
    op.create_index(op.f("ix_leave_balance_ledger_leave_type_id"), "leave_balance_ledger", ["leave_type_id"], unique=False)
    op.create_index(op.f("ix_leave_balance_ledger_year"), "leave_balance_ledger", ["year"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_leave_balance_ledger_year"), table_name="leave_balance_ledger")
    op.drop_index(op.f("ix_leave_balance_ledger_leave_type_id"), table_name="leave_balance_ledger")
    op.drop_index(op.f("ix_leave_balance_ledger_id"), table_name="leave_balance_ledger")
    op.drop_index(op.f("ix_leave_balance_ledger_employee_id"), table_name="leave_balance_ledger")
    op.drop_table("leave_balance_ledger")
