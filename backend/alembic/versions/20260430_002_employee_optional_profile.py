"""Employee optional profile fields

Revision ID: 20260430_002
Revises: 20260430_001
Create Date: 2026-04-30
"""

from alembic import op
import sqlalchemy as sa

revision = "20260430_002"
down_revision = "20260430_001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("employees", sa.Column("interests", sa.Text(), nullable=True))
    op.add_column("employees", sa.Column("research_work", sa.Text(), nullable=True))
    op.add_column("employees", sa.Column("family_information", sa.Text(), nullable=True))
    op.add_column("employees", sa.Column("health_information", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("employees", "health_information")
    op.drop_column("employees", "family_information")
    op.drop_column("employees", "research_work")
    op.drop_column("employees", "interests")
