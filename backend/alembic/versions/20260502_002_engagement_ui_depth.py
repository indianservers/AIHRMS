"""engagement ui depth

Revision ID: 20260502_002
Revises: 20260502_001
Create Date: 2026-05-02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260502_002"
down_revision = "20260502_001"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _has_table(table_name: str) -> bool:
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_column("engagement_surveys", "question"):
        op.add_column("engagement_surveys", sa.Column("question", sa.Text(), nullable=True))
    if not _has_column("engagement_surveys", "options_json"):
        op.add_column("engagement_surveys", sa.Column("options_json", sa.JSON(), nullable=True))
    if not _has_table("recognition_reactions"):
        op.create_table(
            "recognition_reactions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("recognition_id", sa.Integer(), nullable=False),
            sa.Column("employee_id", sa.Integer(), nullable=False),
            sa.Column("emoji", sa.String(length=20), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["recognition_id"], ["recognitions.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_recognition_reactions_id"), "recognition_reactions", ["id"], unique=False)
        op.create_index(op.f("ix_recognition_reactions_employee_id"), "recognition_reactions", ["employee_id"], unique=False)
        op.create_index(op.f("ix_recognition_reactions_recognition_id"), "recognition_reactions", ["recognition_id"], unique=False)


def downgrade() -> None:
    if _has_table("recognition_reactions"):
        op.drop_index(op.f("ix_recognition_reactions_recognition_id"), table_name="recognition_reactions")
        op.drop_index(op.f("ix_recognition_reactions_employee_id"), table_name="recognition_reactions")
        op.drop_index(op.f("ix_recognition_reactions_id"), table_name="recognition_reactions")
        op.drop_table("recognition_reactions")
    if _has_column("engagement_surveys", "options_json"):
        op.drop_column("engagement_surveys", "options_json")
    if _has_column("engagement_surveys", "question"):
        op.drop_column("engagement_surveys", "question")
