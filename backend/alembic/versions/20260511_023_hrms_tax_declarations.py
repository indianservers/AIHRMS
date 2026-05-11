"""Add HRMS investment declarations and tax proofs."""

from alembic import op
import sqlalchemy as sa


revision = "20260511_023"
down_revision = "20260511_022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tax_declaration_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("financial_year", sa.String(length=20), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("section", sa.String(length=80), nullable=False),
        sa.Column("max_limit", sa.Numeric(14, 2), nullable=True),
        sa.Column("requires_proof", sa.Boolean(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tax_declaration_categories_id", "tax_declaration_categories", ["id"])
    op.create_index("ix_tax_declaration_categories_organization_id", "tax_declaration_categories", ["organization_id"])
    op.create_index("idx_tax_declaration_category_fy_code", "tax_declaration_categories", ["organization_id", "financial_year", "code"])

    op.create_table(
        "employee_tax_declarations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("financial_year", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_employee_tax_declarations_id", "employee_tax_declarations", ["id"])
    op.create_index("ix_employee_tax_declarations_employee_id", "employee_tax_declarations", ["employee_id"])
    op.create_index("ix_employee_tax_declarations_organization_id", "employee_tax_declarations", ["organization_id"])
    op.create_index("idx_employee_tax_declaration_employee_fy", "employee_tax_declarations", ["employee_id", "financial_year"])

    op.create_table(
        "employee_tax_declaration_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("declaration_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("declared_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("approved_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["tax_declaration_categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["declaration_id"], ["employee_tax_declarations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_employee_tax_declaration_items_id", "employee_tax_declaration_items", ["id"])
    op.create_index("ix_employee_tax_declaration_items_category_id", "employee_tax_declaration_items", ["category_id"])
    op.create_index("ix_employee_tax_declaration_items_declaration_id", "employee_tax_declaration_items", ["declaration_id"])

    op.create_table(
        "employee_tax_proofs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("declaration_item_id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_type", sa.String(length=120), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["declaration_item_id"], ["employee_tax_declaration_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_employee_tax_proofs_id", "employee_tax_proofs", ["id"])
    op.create_index("ix_employee_tax_proofs_declaration_item_id", "employee_tax_proofs", ["declaration_item_id"])


def downgrade() -> None:
    op.drop_index("ix_employee_tax_proofs_declaration_item_id", table_name="employee_tax_proofs")
    op.drop_index("ix_employee_tax_proofs_id", table_name="employee_tax_proofs")
    op.drop_table("employee_tax_proofs")
    op.drop_index("ix_employee_tax_declaration_items_declaration_id", table_name="employee_tax_declaration_items")
    op.drop_index("ix_employee_tax_declaration_items_category_id", table_name="employee_tax_declaration_items")
    op.drop_index("ix_employee_tax_declaration_items_id", table_name="employee_tax_declaration_items")
    op.drop_table("employee_tax_declaration_items")
    op.drop_index("idx_employee_tax_declaration_employee_fy", table_name="employee_tax_declarations")
    op.drop_index("ix_employee_tax_declarations_organization_id", table_name="employee_tax_declarations")
    op.drop_index("ix_employee_tax_declarations_employee_id", table_name="employee_tax_declarations")
    op.drop_index("ix_employee_tax_declarations_id", table_name="employee_tax_declarations")
    op.drop_table("employee_tax_declarations")
    op.drop_index("idx_tax_declaration_category_fy_code", table_name="tax_declaration_categories")
    op.drop_index("ix_tax_declaration_categories_organization_id", table_name="tax_declaration_categories")
    op.drop_index("ix_tax_declaration_categories_id", table_name="tax_declaration_categories")
    op.drop_table("tax_declaration_categories")
