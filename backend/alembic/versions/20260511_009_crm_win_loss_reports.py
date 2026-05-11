"""Add CRM win/loss reporting deal fields

Revision ID: 20260511_009_crm_win_loss_reports
Revises: 20260511_008_crm_note_mentions, 20260511_008_crm_custom_fields_config
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_009_crm_win_loss_reports"
down_revision = ("20260511_008_crm_note_mentions", "20260511_008_crm_custom_fields_config")
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
    _add_column_if_missing("crm_deals", sa.Column("lost_reason", sa.Text(), nullable=True))
    _add_column_if_missing("crm_deals", sa.Column("source", sa.String(length=80), nullable=True))
    _add_column_if_missing("crm_deals", sa.Column("won_at", sa.DateTime(timezone=True), nullable=True))
    _add_column_if_missing("crm_deals", sa.Column("lost_at", sa.DateTime(timezone=True), nullable=True))
    _add_column_if_missing("crm_deals", sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE crm_deals SET lost_reason = COALESCE(lost_reason, loss_reason)")
    op.execute("UPDATE crm_deals SET source = COALESCE(source, lead_source)")
    op.create_index(op.f("ix_crm_deals_source"), "crm_deals", ["source"], unique=False)
    op.create_index(op.f("ix_crm_deals_won_at"), "crm_deals", ["won_at"], unique=False)
    op.create_index(op.f("ix_crm_deals_lost_at"), "crm_deals", ["lost_at"], unique=False)
    op.create_index(op.f("ix_crm_deals_closed_at"), "crm_deals", ["closed_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_crm_deals_closed_at"), table_name="crm_deals")
    op.drop_index(op.f("ix_crm_deals_lost_at"), table_name="crm_deals")
    op.drop_index(op.f("ix_crm_deals_won_at"), table_name="crm_deals")
    op.drop_index(op.f("ix_crm_deals_source"), table_name="crm_deals")
    _drop_column_if_present("crm_deals", "closed_at")
    _drop_column_if_present("crm_deals", "lost_at")
    _drop_column_if_present("crm_deals", "won_at")
    _drop_column_if_present("crm_deals", "source")
    _drop_column_if_present("crm_deals", "lost_reason")
