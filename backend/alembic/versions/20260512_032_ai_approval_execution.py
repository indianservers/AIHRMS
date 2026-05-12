"""Add AI approval execution result fields

Revision ID: 20260512_032
Revises: 20260512_031
Create Date: 2026-05-12
"""

from alembic import op
import sqlalchemy as sa


revision = "20260512_032"
down_revision = "20260512_031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ai_action_approvals", sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("ai_action_approvals", sa.Column("execution_result_json", sa.JSON(), nullable=True))
    with op.batch_alter_table("ai_action_approvals") as batch_op:
        batch_op.alter_column("conversation_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.drop_column("ai_action_approvals", "execution_result_json")
    op.drop_column("ai_action_approvals", "executed_at")
    with op.batch_alter_table("ai_action_approvals") as batch_op:
        batch_op.alter_column("conversation_id", existing_type=sa.Integer(), nullable=False)
