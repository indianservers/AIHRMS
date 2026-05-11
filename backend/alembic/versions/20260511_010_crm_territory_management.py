"""Add CRM territory management

Revision ID: 20260511_010_crm_territory_management
Revises: 20260511_009_crm_win_loss_reports
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_010_crm_territory_management"
down_revision = "20260511_009_crm_win_loss_reports"
branch_labels = None
depends_on = None


def _columns(table_name: str) -> set[str]:
    return {item["name"] for item in sa.inspect(op.get_bind()).get_columns(table_name)}


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if column.name not in _columns(table_name):
        op.add_column(table_name, column)


def upgrade() -> None:
    _add_column_if_missing("crm_territories", sa.Column("rules_json", sa.JSON(), nullable=True))
    _add_column_if_missing("crm_territories", sa.Column("priority", sa.Integer(), nullable=True))
    _add_column_if_missing("crm_territories", sa.Column("is_active", sa.Boolean(), nullable=True))
    op.execute("UPDATE crm_territories SET priority = COALESCE(priority, 100)")
    op.execute("UPDATE crm_territories SET is_active = COALESCE(is_active, CASE WHEN status = 'Active' THEN 1 ELSE 0 END)")
    for table_name in ("crm_leads", "crm_companies", "crm_deals"):
        _add_column_if_missing(table_name, sa.Column("territory_id", sa.Integer(), nullable=True))
        op.create_index(op.f(f"ix_{table_name}_territory_id"), table_name, ["territory_id"], unique=False)
    op.create_index(op.f("ix_crm_territories_priority"), "crm_territories", ["priority"], unique=False)
    op.create_index(op.f("ix_crm_territories_is_active"), "crm_territories", ["is_active"], unique=False)
    op.create_table(
        "crm_territory_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("territory_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["territory_id"], ["crm_territories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("territory_id", "user_id", name="uq_crm_territory_user"),
    )
    op.create_index(op.f("ix_crm_territory_users_organization_id"), "crm_territory_users", ["organization_id"], unique=False)
    op.create_index(op.f("ix_crm_territory_users_territory_id"), "crm_territory_users", ["territory_id"], unique=False)
    op.create_index(op.f("ix_crm_territory_users_user_id"), "crm_territory_users", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_table("crm_territory_users")
    op.drop_index(op.f("ix_crm_territories_is_active"), table_name="crm_territories")
    op.drop_index(op.f("ix_crm_territories_priority"), table_name="crm_territories")
    for table_name in ("crm_deals", "crm_companies", "crm_leads"):
        op.drop_index(op.f(f"ix_{table_name}_territory_id"), table_name=table_name)
        if "territory_id" in _columns(table_name):
            op.drop_column(table_name, "territory_id")
    for column_name in ("is_active", "priority", "rules_json"):
        if column_name in _columns("crm_territories"):
            op.drop_column("crm_territories", column_name)
