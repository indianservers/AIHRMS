"""normalize payroll run statuses

Revision ID: 20260502_004
Revises: 20260502_003
Create Date: 2026-05-02
"""

from alembic import op


revision = "20260502_004"
down_revision = "20260502_003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE payroll_runs
        SET status = CASE LOWER(status)
            WHEN 'draft' THEN 'draft'
            WHEN 'processing' THEN 'inputs_pending'
            WHEN 'inputs pending' THEN 'inputs_pending'
            WHEN 'inputs_pending' THEN 'inputs_pending'
            WHEN 'completed' THEN 'calculated'
            WHEN 'calculated' THEN 'calculated'
            WHEN 'approved' THEN 'approved'
            WHEN 'locked' THEN 'locked'
            WHEN 'paid' THEN 'paid'
            ELSE status
        END
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE payroll_runs
        SET status = CASE status
            WHEN 'draft' THEN 'Draft'
            WHEN 'inputs_pending' THEN 'Processing'
            WHEN 'calculated' THEN 'Completed'
            WHEN 'approved' THEN 'Approved'
            WHEN 'locked' THEN 'Locked'
            WHEN 'paid' THEN 'Paid'
            ELSE status
        END
        """
    )
