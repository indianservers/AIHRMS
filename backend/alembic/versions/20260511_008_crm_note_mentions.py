"""Add CRM note mentions

Revision ID: 20260511_008_crm_note_mentions
Revises: 20260511_007_crm_quotation_pdf_metadata
Create Date: 2026-05-11 08:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_008_crm_note_mentions"
down_revision = "20260511_007_crm_quotation_pdf_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crm_note_mentions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("note_id", sa.Integer(), nullable=True),
        sa.Column("activity_id", sa.Integer(), nullable=True),
        sa.Column("mentioned_user_id", sa.Integer(), nullable=False),
        sa.Column("mentioned_by", sa.Integer(), nullable=True),
        sa.Column("entity_type", sa.String(length=40), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["activity_id"], ["crm_activities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mentioned_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["mentioned_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["note_id"], ["crm_notes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_crm_note_mentions_id"), "crm_note_mentions", ["id"], unique=False)
    op.create_index(op.f("ix_crm_note_mentions_organization_id"), "crm_note_mentions", ["organization_id"], unique=False)
    op.create_index(op.f("ix_crm_note_mentions_note_id"), "crm_note_mentions", ["note_id"], unique=False)
    op.create_index(op.f("ix_crm_note_mentions_activity_id"), "crm_note_mentions", ["activity_id"], unique=False)
    op.create_index(op.f("ix_crm_note_mentions_mentioned_user_id"), "crm_note_mentions", ["mentioned_user_id"], unique=False)
    op.create_index(op.f("ix_crm_note_mentions_mentioned_by"), "crm_note_mentions", ["mentioned_by"], unique=False)
    op.create_index(op.f("ix_crm_note_mentions_entity_type"), "crm_note_mentions", ["entity_type"], unique=False)
    op.create_index(op.f("ix_crm_note_mentions_entity_id"), "crm_note_mentions", ["entity_id"], unique=False)
    op.create_index(op.f("ix_crm_note_mentions_created_at"), "crm_note_mentions", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("crm_note_mentions")
