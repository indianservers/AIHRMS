"""Add CRM lead scoring

Revision ID: 20260511_006_crm_lead_scoring
Revises: 20260511_005_crm_approval_workflows
Create Date: 2026-05-11 06:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_006_crm_lead_scoring"
down_revision = "20260511_005_crm_approval_workflows"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("crm_leads", sa.Column("lead_score", sa.Integer(), nullable=True))
    op.add_column("crm_leads", sa.Column("lead_score_label", sa.String(length=20), nullable=True))
    op.add_column("crm_leads", sa.Column("lead_score_mode", sa.String(length=20), nullable=True))
    op.add_column("crm_leads", sa.Column("last_score_calculated_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f("ix_crm_leads_lead_score"), "crm_leads", ["lead_score"], unique=False)
    op.create_index(op.f("ix_crm_leads_lead_score_label"), "crm_leads", ["lead_score_label"], unique=False)
    op.create_index(op.f("ix_crm_leads_lead_score_mode"), "crm_leads", ["lead_score_mode"], unique=False)
    op.execute("UPDATE crm_leads SET lead_score = COALESCE(lead_score, 0)")
    op.execute("UPDATE crm_leads SET lead_score_label = COALESCE(lead_score_label, rating, 'Cold')")
    op.execute("UPDATE crm_leads SET lead_score_mode = COALESCE(lead_score_mode, 'automatic')")

    op.create_table(
        "crm_lead_scoring_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("field", sa.String(length=100), nullable=False),
        sa.Column("operator", sa.String(length=40), nullable=False),
        sa.Column("value", sa.String(length=240), nullable=True),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "name", name="uq_crm_lead_scoring_rule_org_name"),
    )
    op.create_index(op.f("ix_crm_lead_scoring_rules_id"), "crm_lead_scoring_rules", ["id"], unique=False)
    op.create_index(op.f("ix_crm_lead_scoring_rules_organization_id"), "crm_lead_scoring_rules", ["organization_id"], unique=False)
    op.create_index(op.f("ix_crm_lead_scoring_rules_name"), "crm_lead_scoring_rules", ["name"], unique=False)
    op.create_index(op.f("ix_crm_lead_scoring_rules_field"), "crm_lead_scoring_rules", ["field"], unique=False)
    op.create_index(op.f("ix_crm_lead_scoring_rules_operator"), "crm_lead_scoring_rules", ["operator"], unique=False)
    op.create_index(op.f("ix_crm_lead_scoring_rules_is_active"), "crm_lead_scoring_rules", ["is_active"], unique=False)


def downgrade() -> None:
    op.drop_table("crm_lead_scoring_rules")
    op.drop_index(op.f("ix_crm_leads_lead_score_mode"), table_name="crm_leads")
    op.drop_index(op.f("ix_crm_leads_lead_score_label"), table_name="crm_leads")
    op.drop_index(op.f("ix_crm_leads_lead_score"), table_name="crm_leads")
    op.drop_column("crm_leads", "last_score_calculated_at")
    op.drop_column("crm_leads", "lead_score_mode")
    op.drop_column("crm_leads", "lead_score_label")
    op.drop_column("crm_leads", "lead_score")
