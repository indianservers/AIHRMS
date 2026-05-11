"""Add admin CRM custom field configuration flags.

Revision ID: 20260511_008_crm_custom_fields_config
Revises: 20260511_007_crm_quotation_pdf_metadata
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_008_crm_custom_fields_config"
down_revision = "20260511_007_crm_quotation_pdf_metadata"
branch_labels = None
depends_on = None


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {item["name"] for item in inspector.get_columns(table_name)}
    if column.name not in columns:
        op.add_column(table_name, column)


def _drop_column_if_present(table_name: str, column_name: str) -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {item["name"] for item in inspector.get_columns(table_name)}
    if column_name in columns:
        op.drop_column(table_name, column_name)


def upgrade() -> None:
    _add_column_if_missing("crm_custom_fields", sa.Column("field_name", sa.String(length=160), nullable=True))
    _add_column_if_missing("crm_custom_fields", sa.Column("is_unique", sa.Boolean(), nullable=True))
    _add_column_if_missing("crm_custom_fields", sa.Column("is_visible", sa.Boolean(), nullable=True))
    _add_column_if_missing("crm_custom_fields", sa.Column("is_filterable", sa.Boolean(), nullable=True))
    op.execute("UPDATE crm_custom_fields SET field_name = COALESCE(field_name, label)")
    op.execute("UPDATE crm_custom_fields SET is_unique = COALESCE(is_unique, 0)")
    op.execute("UPDATE crm_custom_fields SET is_visible = COALESCE(is_visible, 1)")
    op.execute("UPDATE crm_custom_fields SET is_filterable = COALESCE(is_filterable, 0)")
    op.create_index(op.f("ix_crm_custom_fields_is_unique"), "crm_custom_fields", ["is_unique"], unique=False)
    op.create_index(op.f("ix_crm_custom_fields_is_visible"), "crm_custom_fields", ["is_visible"], unique=False)
    op.create_index(op.f("ix_crm_custom_fields_is_filterable"), "crm_custom_fields", ["is_filterable"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_crm_custom_fields_is_filterable"), table_name="crm_custom_fields")
    op.drop_index(op.f("ix_crm_custom_fields_is_visible"), table_name="crm_custom_fields")
    op.drop_index(op.f("ix_crm_custom_fields_is_unique"), table_name="crm_custom_fields")
    _drop_column_if_present("crm_custom_fields", "is_filterable")
    _drop_column_if_present("crm_custom_fields", "is_visible")
    _drop_column_if_present("crm_custom_fields", "is_unique")
    _drop_column_if_present("crm_custom_fields", "field_name")
