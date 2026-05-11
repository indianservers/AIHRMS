"""Add CRM approval workflows

Revision ID: 20260511_005_crm_approval_workflows
Revises: 20260511_004_crm_multiple_pipelines
Create Date: 2026-05-11 09:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260511_005_crm_approval_workflows"
down_revision = "20260511_004_crm_multiple_pipelines"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crm_approval_workflows",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("trigger_type", sa.String(length=80), nullable=False),
        sa.Column("conditions", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_crm_approval_workflows_id"), "crm_approval_workflows", ["id"], unique=False)
    op.create_index(op.f("ix_crm_approval_workflows_organization_id"), "crm_approval_workflows", ["organization_id"], unique=False)
    op.create_index(op.f("ix_crm_approval_workflows_name"), "crm_approval_workflows", ["name"], unique=False)
    op.create_index(op.f("ix_crm_approval_workflows_entity_type"), "crm_approval_workflows", ["entity_type"], unique=False)
    op.create_index(op.f("ix_crm_approval_workflows_trigger_type"), "crm_approval_workflows", ["trigger_type"], unique=False)
    op.create_index(op.f("ix_crm_approval_workflows_is_active"), "crm_approval_workflows", ["is_active"], unique=False)

    op.create_table(
        "crm_approval_steps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workflow_id", sa.Integer(), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("approver_type", sa.String(length=30), nullable=False),
        sa.Column("approver_id", sa.Integer(), nullable=True),
        sa.Column("action_on_reject", sa.String(length=30), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["workflow_id"], ["crm_approval_workflows.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_crm_approval_steps_id"), "crm_approval_steps", ["id"], unique=False)
    op.create_index(op.f("ix_crm_approval_steps_workflow_id"), "crm_approval_steps", ["workflow_id"], unique=False)
    op.create_index(op.f("ix_crm_approval_steps_step_order"), "crm_approval_steps", ["step_order"], unique=False)
    op.create_index(op.f("ix_crm_approval_steps_approver_type"), "crm_approval_steps", ["approver_type"], unique=False)
    op.create_index(op.f("ix_crm_approval_steps_approver_id"), "crm_approval_steps", ["approver_id"], unique=False)
    op.create_index(op.f("ix_crm_approval_steps_action_on_reject"), "crm_approval_steps", ["action_on_reject"], unique=False)

    op.create_table(
        "crm_approval_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("workflow_id", sa.Integer(), nullable=True),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("submitted_by", sa.Integer(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["submitted_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["workflow_id"], ["crm_approval_workflows.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_crm_approval_requests_id"), "crm_approval_requests", ["id"], unique=False)
    op.create_index(op.f("ix_crm_approval_requests_organization_id"), "crm_approval_requests", ["organization_id"], unique=False)
    op.create_index(op.f("ix_crm_approval_requests_workflow_id"), "crm_approval_requests", ["workflow_id"], unique=False)
    op.create_index(op.f("ix_crm_approval_requests_entity_type"), "crm_approval_requests", ["entity_type"], unique=False)
    op.create_index(op.f("ix_crm_approval_requests_entity_id"), "crm_approval_requests", ["entity_id"], unique=False)
    op.create_index(op.f("ix_crm_approval_requests_status"), "crm_approval_requests", ["status"], unique=False)
    op.create_index(op.f("ix_crm_approval_requests_submitted_by"), "crm_approval_requests", ["submitted_by"], unique=False)
    op.create_index(op.f("ix_crm_approval_requests_submitted_at"), "crm_approval_requests", ["submitted_at"], unique=False)

    op.create_table(
        "crm_approval_request_steps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("step_id", sa.Integer(), nullable=True),
        sa.Column("approver_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("acted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["approver_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["request_id"], ["crm_approval_requests.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["step_id"], ["crm_approval_steps.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_crm_approval_request_steps_id"), "crm_approval_request_steps", ["id"], unique=False)
    op.create_index(op.f("ix_crm_approval_request_steps_request_id"), "crm_approval_request_steps", ["request_id"], unique=False)
    op.create_index(op.f("ix_crm_approval_request_steps_step_id"), "crm_approval_request_steps", ["step_id"], unique=False)
    op.create_index(op.f("ix_crm_approval_request_steps_approver_id"), "crm_approval_request_steps", ["approver_id"], unique=False)
    op.create_index(op.f("ix_crm_approval_request_steps_status"), "crm_approval_request_steps", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_crm_approval_request_steps_status"), table_name="crm_approval_request_steps")
    op.drop_index(op.f("ix_crm_approval_request_steps_approver_id"), table_name="crm_approval_request_steps")
    op.drop_index(op.f("ix_crm_approval_request_steps_step_id"), table_name="crm_approval_request_steps")
    op.drop_index(op.f("ix_crm_approval_request_steps_request_id"), table_name="crm_approval_request_steps")
    op.drop_index(op.f("ix_crm_approval_request_steps_id"), table_name="crm_approval_request_steps")
    op.drop_table("crm_approval_request_steps")
    op.drop_index(op.f("ix_crm_approval_requests_submitted_at"), table_name="crm_approval_requests")
    op.drop_index(op.f("ix_crm_approval_requests_submitted_by"), table_name="crm_approval_requests")
    op.drop_index(op.f("ix_crm_approval_requests_status"), table_name="crm_approval_requests")
    op.drop_index(op.f("ix_crm_approval_requests_entity_id"), table_name="crm_approval_requests")
    op.drop_index(op.f("ix_crm_approval_requests_entity_type"), table_name="crm_approval_requests")
    op.drop_index(op.f("ix_crm_approval_requests_workflow_id"), table_name="crm_approval_requests")
    op.drop_index(op.f("ix_crm_approval_requests_organization_id"), table_name="crm_approval_requests")
    op.drop_index(op.f("ix_crm_approval_requests_id"), table_name="crm_approval_requests")
    op.drop_table("crm_approval_requests")
    op.drop_index(op.f("ix_crm_approval_steps_action_on_reject"), table_name="crm_approval_steps")
    op.drop_index(op.f("ix_crm_approval_steps_approver_id"), table_name="crm_approval_steps")
    op.drop_index(op.f("ix_crm_approval_steps_approver_type"), table_name="crm_approval_steps")
    op.drop_index(op.f("ix_crm_approval_steps_step_order"), table_name="crm_approval_steps")
    op.drop_index(op.f("ix_crm_approval_steps_workflow_id"), table_name="crm_approval_steps")
    op.drop_index(op.f("ix_crm_approval_steps_id"), table_name="crm_approval_steps")
    op.drop_table("crm_approval_steps")
    op.drop_index(op.f("ix_crm_approval_workflows_is_active"), table_name="crm_approval_workflows")
    op.drop_index(op.f("ix_crm_approval_workflows_trigger_type"), table_name="crm_approval_workflows")
    op.drop_index(op.f("ix_crm_approval_workflows_entity_type"), table_name="crm_approval_workflows")
    op.drop_index(op.f("ix_crm_approval_workflows_name"), table_name="crm_approval_workflows")
    op.drop_index(op.f("ix_crm_approval_workflows_organization_id"), table_name="crm_approval_workflows")
    op.drop_index(op.f("ix_crm_approval_workflows_id"), table_name="crm_approval_workflows")
    op.drop_table("crm_approval_workflows")
