"""Add generic CRM activity timeline fields

Revision ID: 20260511_002_crm_activity_timeline
Revises: 20260511_001_crm_rest_depth
Create Date: 2026-05-11 01:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_002_crm_activity_timeline"
down_revision = "20260511_001_crm_rest_depth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("crm_activities", sa.Column("entity_type", sa.String(length=40), nullable=True))
    op.add_column("crm_activities", sa.Column("entity_id", sa.Integer(), nullable=True))
    op.add_column("crm_activities", sa.Column("title", sa.String(length=220), nullable=True))
    op.add_column("crm_activities", sa.Column("body", sa.Text(), nullable=True))
    op.add_column("crm_activities", sa.Column("metadata_json", sa.JSON(), nullable=True))
    op.add_column("crm_activities", sa.Column("activity_date", sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f("ix_crm_activities_entity_type"), "crm_activities", ["entity_type"], unique=False)
    op.create_index(op.f("ix_crm_activities_entity_id"), "crm_activities", ["entity_id"], unique=False)
    op.create_index(op.f("ix_crm_activities_activity_date"), "crm_activities", ["activity_date"], unique=False)

    op.execute("UPDATE crm_activities SET title = subject WHERE title IS NULL AND subject IS NOT NULL")
    op.execute("UPDATE crm_activities SET body = description WHERE body IS NULL AND description IS NOT NULL")
    op.execute("UPDATE crm_activities SET activity_date = COALESCE(due_date, completed_at, created_at) WHERE activity_date IS NULL")
    op.execute("UPDATE crm_activities SET entity_type = 'lead', entity_id = lead_id WHERE entity_type IS NULL AND lead_id IS NOT NULL")
    op.execute("UPDATE crm_activities SET entity_type = 'contact', entity_id = contact_id WHERE entity_type IS NULL AND contact_id IS NOT NULL")
    op.execute("UPDATE crm_activities SET entity_type = 'account', entity_id = company_id WHERE entity_type IS NULL AND company_id IS NOT NULL")
    op.execute("UPDATE crm_activities SET entity_type = 'deal', entity_id = deal_id WHERE entity_type IS NULL AND deal_id IS NOT NULL")


def downgrade() -> None:
    op.drop_index(op.f("ix_crm_activities_activity_date"), table_name="crm_activities")
    op.drop_index(op.f("ix_crm_activities_entity_id"), table_name="crm_activities")
    op.drop_index(op.f("ix_crm_activities_entity_type"), table_name="crm_activities")
    op.drop_column("crm_activities", "activity_date")
    op.drop_column("crm_activities", "metadata_json")
    op.drop_column("crm_activities", "body")
    op.drop_column("crm_activities", "title")
    op.drop_column("crm_activities", "entity_id")
    op.drop_column("crm_activities", "entity_type")
