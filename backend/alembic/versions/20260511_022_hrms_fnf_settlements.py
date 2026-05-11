"""Extend HRMS full and final settlement lifecycle fields."""

from alembic import op
import sqlalchemy as sa


revision = "20260511_022"
down_revision = "20260511_021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("full_final_settlements", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.add_column("full_final_settlements", sa.Column("last_working_date", sa.Date(), nullable=True))
    op.add_column("full_final_settlements", sa.Column("unpaid_salary", sa.Numeric(12, 2), nullable=True, server_default="0"))
    op.add_column("full_final_settlements", sa.Column("reimbursement_payable", sa.Numeric(12, 2), nullable=True, server_default="0"))
    op.add_column("full_final_settlements", sa.Column("bonus_payable", sa.Numeric(12, 2), nullable=True, server_default="0"))
    op.add_column("full_final_settlements", sa.Column("other_earnings", sa.Numeric(12, 2), nullable=True, server_default="0"))
    op.add_column("full_final_settlements", sa.Column("other_deductions", sa.Numeric(12, 2), nullable=True, server_default="0"))
    op.add_column("full_final_settlements", sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("full_final_settlements", sa.Column("rejected_by", sa.Integer(), nullable=True))
    op.add_column("full_final_settlements", sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("full_final_settlements", sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("full_final_settlements", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_full_final_settlements_organization_id", "full_final_settlements", ["organization_id"])
    op.create_foreign_key(
        "fk_full_final_settlements_rejected_by_users",
        "full_final_settlements",
        "users",
        ["rejected_by"],
        ["id"],
        ondelete="SET NULL",
    )
    op.add_column("full_final_settlement_lines", sa.Column("is_manual_adjustment", sa.Boolean(), nullable=True, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("full_final_settlement_lines", "is_manual_adjustment")
    op.drop_constraint("fk_full_final_settlements_rejected_by_users", "full_final_settlements", type_="foreignkey")
    op.drop_index("ix_full_final_settlements_organization_id", table_name="full_final_settlements")
    op.drop_column("full_final_settlements", "updated_at")
    op.drop_column("full_final_settlements", "paid_at")
    op.drop_column("full_final_settlements", "rejected_at")
    op.drop_column("full_final_settlements", "rejected_by")
    op.drop_column("full_final_settlements", "submitted_at")
    op.drop_column("full_final_settlements", "other_deductions")
    op.drop_column("full_final_settlements", "other_earnings")
    op.drop_column("full_final_settlements", "bonus_payable")
    op.drop_column("full_final_settlements", "reimbursement_payable")
    op.drop_column("full_final_settlements", "unpaid_salary")
    op.drop_column("full_final_settlements", "last_working_date")
    op.drop_column("full_final_settlements", "organization_id")
