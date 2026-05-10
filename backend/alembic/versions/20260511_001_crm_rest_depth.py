"""Add CRM REST API audit and admin models

Revision ID: 20260511_001_crm_rest_depth
Revises: 20260507_003
Create Date: 2026-05-11 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_001_crm_rest_depth"
down_revision = "20260507_003"
branch_labels = None
depends_on = None


CRM_TABLES = [
    "crm_companies",
    "crm_contacts",
    "crm_leads",
    "crm_pipelines",
    "crm_pipeline_stages",
    "crm_deals",
    "crm_products",
    "crm_quotations",
    "crm_activities",
    "crm_tasks",
    "crm_notes",
    "crm_email_logs",
    "crm_call_logs",
    "crm_meetings",
    "crm_tickets",
    "crm_campaigns",
    "crm_file_assets",
]

SOFT_DELETE_UPDATES = [
    "crm_pipelines",
    "crm_pipeline_stages",
    "crm_quotations",
    "crm_activities",
    "crm_email_logs",
    "crm_call_logs",
    "crm_meetings",
]


def _add_audit_columns(table_name: str) -> None:
    op.add_column(table_name, sa.Column("created_by_user_id", sa.Integer(), nullable=True))
    op.add_column(table_name, sa.Column("updated_by_user_id", sa.Integer(), nullable=True))


def upgrade() -> None:
    for table_name in CRM_TABLES:
        _add_audit_columns(table_name)
        if table_name != "crm_pipeline_stages":
            op.execute(f"UPDATE {table_name} SET organization_id = 1 WHERE organization_id IS NULL")

    op.add_column("crm_pipeline_stages", sa.Column("organization_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_crm_pipeline_stages_organization_id"), "crm_pipeline_stages", ["organization_id"], unique=False)
    op.execute("UPDATE crm_pipeline_stages SET organization_id = 1 WHERE organization_id IS NULL")
    for table_name in SOFT_DELETE_UPDATES:
        op.add_column(table_name, sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("crm_email_logs", sa.Column("owner_user_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_crm_email_logs_owner_user_id"), "crm_email_logs", ["owner_user_id"], unique=False)
    op.add_column("crm_call_logs", sa.Column("owner_user_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_crm_call_logs_owner_user_id"), "crm_call_logs", ["owner_user_id"], unique=False)
    op.add_column("crm_meetings", sa.Column("owner_user_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_crm_meetings_owner_user_id"), "crm_meetings", ["owner_user_id"], unique=False)

    op.create_table(
        "crm_territories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "name", name="uq_crm_territory_org_name"),
    )
    op.create_index(op.f("ix_crm_territories_id"), "crm_territories", ["id"], unique=False)
    op.create_index(op.f("ix_crm_territories_name"), "crm_territories", ["name"], unique=False)
    op.create_index(op.f("ix_crm_territories_organization_id"), "crm_territories", ["organization_id"], unique=False)
    op.create_index(op.f("ix_crm_territories_owner_user_id"), "crm_territories", ["owner_user_id"], unique=False)
    op.create_index(op.f("ix_crm_territories_status"), "crm_territories", ["status"], unique=False)

    op.create_table(
        "crm_teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("team_type", sa.String(length=60), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "name", name="uq_crm_team_org_name"),
    )
    op.create_index(op.f("ix_crm_teams_id"), "crm_teams", ["id"], unique=False)
    op.create_index(op.f("ix_crm_teams_name"), "crm_teams", ["name"], unique=False)
    op.create_index(op.f("ix_crm_teams_organization_id"), "crm_teams", ["organization_id"], unique=False)
    op.create_index(op.f("ix_crm_teams_owner_user_id"), "crm_teams", ["owner_user_id"], unique=False)
    op.create_index(op.f("ix_crm_teams_status"), "crm_teams", ["status"], unique=False)
    op.create_index(op.f("ix_crm_teams_team_type"), "crm_teams", ["team_type"], unique=False)

    op.create_table(
        "crm_owners",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("territory_id", sa.Integer(), nullable=True),
        sa.Column("full_name", sa.String(length=180), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("role", sa.String(length=80), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["team_id"], ["crm_teams.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["territory_id"], ["crm_territories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "email", name="uq_crm_owner_org_email"),
    )
    op.create_index(op.f("ix_crm_owners_email"), "crm_owners", ["email"], unique=False)
    op.create_index(op.f("ix_crm_owners_full_name"), "crm_owners", ["full_name"], unique=False)
    op.create_index(op.f("ix_crm_owners_id"), "crm_owners", ["id"], unique=False)
    op.create_index(op.f("ix_crm_owners_organization_id"), "crm_owners", ["organization_id"], unique=False)
    op.create_index(op.f("ix_crm_owners_role"), "crm_owners", ["role"], unique=False)
    op.create_index(op.f("ix_crm_owners_status"), "crm_owners", ["status"], unique=False)

    op.create_table(
        "crm_custom_fields",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("entity", sa.String(length=80), nullable=False),
        sa.Column("field_key", sa.String(length=100), nullable=False),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("field_type", sa.String(length=40), nullable=True),
        sa.Column("options_json", sa.JSON(), nullable=True),
        sa.Column("is_required", sa.Boolean(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "entity", "field_key", name="uq_crm_custom_field_org_entity_key"),
    )
    op.create_index(op.f("ix_crm_custom_fields_entity"), "crm_custom_fields", ["entity"], unique=False)
    op.create_index(op.f("ix_crm_custom_fields_field_key"), "crm_custom_fields", ["field_key"], unique=False)
    op.create_index(op.f("ix_crm_custom_fields_field_type"), "crm_custom_fields", ["field_type"], unique=False)
    op.create_index(op.f("ix_crm_custom_fields_id"), "crm_custom_fields", ["id"], unique=False)
    op.create_index(op.f("ix_crm_custom_fields_is_active"), "crm_custom_fields", ["is_active"], unique=False)
    op.create_index(op.f("ix_crm_custom_fields_organization_id"), "crm_custom_fields", ["organization_id"], unique=False)

    op.create_table(
        "crm_custom_field_values",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("custom_field_id", sa.Integer(), nullable=False),
        sa.Column("entity", sa.String(length=80), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column("value_number", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("value_date", sa.Date(), nullable=True),
        sa.Column("value_datetime", sa.DateTime(timezone=True), nullable=True),
        sa.Column("value_boolean", sa.Boolean(), nullable=True),
        sa.Column("value_json", sa.JSON(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["custom_field_id"], ["crm_custom_fields.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "custom_field_id", "entity", "record_id", name="uq_crm_custom_field_value_record"),
    )
    op.create_index(op.f("ix_crm_custom_field_values_custom_field_id"), "crm_custom_field_values", ["custom_field_id"], unique=False)
    op.create_index(op.f("ix_crm_custom_field_values_entity"), "crm_custom_field_values", ["entity"], unique=False)
    op.create_index(op.f("ix_crm_custom_field_values_id"), "crm_custom_field_values", ["id"], unique=False)
    op.create_index(op.f("ix_crm_custom_field_values_organization_id"), "crm_custom_field_values", ["organization_id"], unique=False)
    op.create_index(op.f("ix_crm_custom_field_values_record_id"), "crm_custom_field_values", ["record_id"], unique=False)


def downgrade() -> None:
    op.drop_table("crm_custom_field_values")
    op.drop_table("crm_custom_fields")
    op.drop_table("crm_owners")
    op.drop_table("crm_teams")
    op.drop_table("crm_territories")
    op.drop_index(op.f("ix_crm_pipeline_stages_organization_id"), table_name="crm_pipeline_stages")
    op.drop_index(op.f("ix_crm_meetings_owner_user_id"), table_name="crm_meetings")
    op.drop_column("crm_meetings", "owner_user_id")
    op.drop_index(op.f("ix_crm_call_logs_owner_user_id"), table_name="crm_call_logs")
    op.drop_column("crm_call_logs", "owner_user_id")
    op.drop_index(op.f("ix_crm_email_logs_owner_user_id"), table_name="crm_email_logs")
    op.drop_column("crm_email_logs", "owner_user_id")
    for table_name in reversed(SOFT_DELETE_UPDATES):
        op.drop_column(table_name, "deleted_at")
    op.drop_column("crm_pipeline_stages", "organization_id")
    for table_name in reversed(CRM_TABLES):
        op.drop_column(table_name, "updated_by_user_id")
        op.drop_column(table_name, "created_by_user_id")
