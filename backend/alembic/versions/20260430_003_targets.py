"""target market and feature catalog tables

Revision ID: 20260430_003
Revises: 20260430_002
Create Date: 2026-04-30
"""

from alembic import op
import sqlalchemy as sa


revision = "20260430_003"
down_revision = "20260430_002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "industry_targets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("headline", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(length=80), nullable=True),
        sa.Column("color", sa.String(length=40), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_industry_targets_id"), "industry_targets", ["id"], unique=False)
    op.create_index(op.f("ix_industry_targets_name"), "industry_targets", ["name"], unique=False)
    op.create_index(op.f("ix_industry_targets_slug"), "industry_targets", ["slug"], unique=False)

    op.create_table(
        "feature_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("tagline", sa.String(length=255), nullable=True),
        sa.Column("strength", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_feature_plans_code"), "feature_plans", ["code"], unique=False)
    op.create_index(op.f("ix_feature_plans_id"), "feature_plans", ["id"], unique=False)

    op.create_table(
        "feature_catalog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=True),
        sa.Column("module", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_highlight", sa.Boolean(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["plan_id"], ["feature_plans.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feature_catalog_id"), "feature_catalog", ["id"], unique=False)
    op.create_index(op.f("ix_feature_catalog_module"), "feature_catalog", ["module"], unique=False)
    op.create_index(op.f("ix_feature_catalog_name"), "feature_catalog", ["name"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_feature_catalog_name"), table_name="feature_catalog")
    op.drop_index(op.f("ix_feature_catalog_module"), table_name="feature_catalog")
    op.drop_index(op.f("ix_feature_catalog_id"), table_name="feature_catalog")
    op.drop_table("feature_catalog")
    op.drop_index(op.f("ix_feature_plans_id"), table_name="feature_plans")
    op.drop_index(op.f("ix_feature_plans_code"), table_name="feature_plans")
    op.drop_table("feature_plans")
    op.drop_index(op.f("ix_industry_targets_slug"), table_name="industry_targets")
    op.drop_index(op.f("ix_industry_targets_name"), table_name="industry_targets")
    op.drop_index(op.f("ix_industry_targets_id"), table_name="industry_targets")
    op.drop_table("industry_targets")
