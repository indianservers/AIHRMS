"""employee certificate management

Revision ID: 20260501_004
Revises: 20260501_003
Create Date: 2026-05-01
"""

from alembic import op
import sqlalchemy as sa


revision = "20260501_004"
down_revision = "20260501_003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employee_certificates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("certificate_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("issuing_entity", sa.String(length=250), nullable=True),
        sa.Column("issuing_entity_type", sa.String(length=50), nullable=True),
        sa.Column("class_or_grade", sa.String(length=80), nullable=True),
        sa.Column("course_or_program", sa.String(length=200), nullable=True),
        sa.Column("certificate_number", sa.String(length=120), nullable=True),
        sa.Column("issue_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("file_url", sa.String(length=500), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("content_type", sa.String(length=120), nullable=True),
        sa.Column("file_size_bytes", sa.Integer(), nullable=True),
        sa.Column("verification_status", sa.String(length=30), nullable=True),
        sa.Column("verified_by_user_id", sa.Integer(), nullable=True),
        sa.Column("verifier_name", sa.String(length=150), nullable=True),
        sa.Column("verifier_company", sa.String(length=200), nullable=True),
        sa.Column("verifier_designation", sa.String(length=150), nullable=True),
        sa.Column("verifier_contact", sa.String(length=150), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_notes", sa.Text(), nullable=True),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["verified_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_employee_certificates_category"), "employee_certificates", ["category"], unique=False)
    op.create_index(op.f("ix_employee_certificates_employee_id"), "employee_certificates", ["employee_id"], unique=False)
    op.create_index(op.f("ix_employee_certificates_id"), "employee_certificates", ["id"], unique=False)
    op.create_index(op.f("ix_employee_certificates_verification_status"), "employee_certificates", ["verification_status"], unique=False)

    op.create_table(
        "certificate_import_export_batches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("operation_type", sa.String(length=20), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=True),
        sa.Column("source_file_url", sa.String(length=500), nullable=True),
        sa.Column("output_file_url", sa.String(length=500), nullable=True),
        sa.Column("error_report_url", sa.String(length=500), nullable=True),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=True),
        sa.Column("total_records", sa.Integer(), nullable=True),
        sa.Column("success_count", sa.Integer(), nullable=True),
        sa.Column("failure_count", sa.Integer(), nullable=True),
        sa.Column("requested_by", sa.Integer(), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_certificate_import_export_batches_employee_id"), "certificate_import_export_batches", ["employee_id"], unique=False)
    op.create_index(op.f("ix_certificate_import_export_batches_id"), "certificate_import_export_batches", ["id"], unique=False)
    op.create_index(op.f("ix_certificate_import_export_batches_operation_type"), "certificate_import_export_batches", ["operation_type"], unique=False)
    op.create_index(op.f("ix_certificate_import_export_batches_status"), "certificate_import_export_batches", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_certificate_import_export_batches_status"), table_name="certificate_import_export_batches")
    op.drop_index(op.f("ix_certificate_import_export_batches_operation_type"), table_name="certificate_import_export_batches")
    op.drop_index(op.f("ix_certificate_import_export_batches_id"), table_name="certificate_import_export_batches")
    op.drop_index(op.f("ix_certificate_import_export_batches_employee_id"), table_name="certificate_import_export_batches")
    op.drop_table("certificate_import_export_batches")
    op.drop_index(op.f("ix_employee_certificates_verification_status"), table_name="employee_certificates")
    op.drop_index(op.f("ix_employee_certificates_id"), table_name="employee_certificates")
    op.drop_index(op.f("ix_employee_certificates_employee_id"), table_name="employee_certificates")
    op.drop_index(op.f("ix_employee_certificates_category"), table_name="employee_certificates")
    op.drop_table("employee_certificates")
