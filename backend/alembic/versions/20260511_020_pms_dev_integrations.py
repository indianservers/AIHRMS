"""Add PMS development integrations.

Revision ID: 20260511_020
Revises: 20260511_019
Create Date: 2026-05-11
"""
from alembic import op
import sqlalchemy as sa


revision = "20260511_020"
down_revision = "20260511_019"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pms_dev_integrations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("repo_owner", sa.String(length=160), nullable=False),
        sa.Column("repo_name", sa.String(length=180), nullable=False),
        sa.Column("access_token_encrypted", sa.Text(), nullable=True),
        sa.Column("webhook_secret_encrypted", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["pms_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "provider", "repo_owner", "repo_name", name="uq_pms_dev_integration_repo"),
    )
    op.create_index("ix_pms_dev_integrations_id", "pms_dev_integrations", ["id"])
    op.create_index("ix_pms_dev_integrations_organization_id", "pms_dev_integrations", ["organization_id"])
    op.create_index("ix_pms_dev_integrations_project_id", "pms_dev_integrations", ["project_id"])
    op.create_index("ix_pms_dev_integrations_provider", "pms_dev_integrations", ["provider"])
    op.create_index("ix_pms_dev_integrations_repo_owner", "pms_dev_integrations", ["repo_owner"])
    op.create_index("ix_pms_dev_integrations_repo_name", "pms_dev_integrations", ["repo_name"])
    op.create_index("ix_pms_dev_integrations_is_active", "pms_dev_integrations", ["is_active"])

    op.create_table(
        "pms_dev_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("link_type", sa.String(length=30), nullable=False),
        sa.Column("external_id", sa.String(length=240), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=True),
        sa.Column("url", sa.String(length=800), nullable=True),
        sa.Column("status", sa.String(length=60), nullable=True),
        sa.Column("author", sa.String(length=160), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["task_id"], ["pms_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_id", "provider", "link_type", "external_id", name="uq_pms_dev_link_external"),
    )
    op.create_index("ix_pms_dev_links_id", "pms_dev_links", ["id"])
    op.create_index("ix_pms_dev_links_organization_id", "pms_dev_links", ["organization_id"])
    op.create_index("ix_pms_dev_links_task_id", "pms_dev_links", ["task_id"])
    op.create_index("ix_pms_dev_links_provider", "pms_dev_links", ["provider"])
    op.create_index("ix_pms_dev_links_link_type", "pms_dev_links", ["link_type"])
    op.create_index("ix_pms_dev_links_external_id", "pms_dev_links", ["external_id"])
    op.create_index("ix_pms_dev_links_status", "pms_dev_links", ["status"])


def downgrade():
    op.drop_index("ix_pms_dev_links_status", table_name="pms_dev_links")
    op.drop_index("ix_pms_dev_links_external_id", table_name="pms_dev_links")
    op.drop_index("ix_pms_dev_links_link_type", table_name="pms_dev_links")
    op.drop_index("ix_pms_dev_links_provider", table_name="pms_dev_links")
    op.drop_index("ix_pms_dev_links_task_id", table_name="pms_dev_links")
    op.drop_index("ix_pms_dev_links_organization_id", table_name="pms_dev_links")
    op.drop_index("ix_pms_dev_links_id", table_name="pms_dev_links")
    op.drop_table("pms_dev_links")

    op.drop_index("ix_pms_dev_integrations_is_active", table_name="pms_dev_integrations")
    op.drop_index("ix_pms_dev_integrations_repo_name", table_name="pms_dev_integrations")
    op.drop_index("ix_pms_dev_integrations_repo_owner", table_name="pms_dev_integrations")
    op.drop_index("ix_pms_dev_integrations_provider", table_name="pms_dev_integrations")
    op.drop_index("ix_pms_dev_integrations_project_id", table_name="pms_dev_integrations")
    op.drop_index("ix_pms_dev_integrations_organization_id", table_name="pms_dev_integrations")
    op.drop_index("ix_pms_dev_integrations_id", table_name="pms_dev_integrations")
    op.drop_table("pms_dev_integrations")
