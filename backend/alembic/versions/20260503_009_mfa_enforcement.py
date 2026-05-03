"""add mfa enforcement fields

Revision ID: 20260503_009
Revises: 20260503_008
Create Date: 2026-05-03
"""

from alembic import op
import sqlalchemy as sa


revision = "20260503_009"
down_revision = "20260503_008"
branch_labels = None
depends_on = None


def _has_column(conn, table, col):
    insp = sa.inspect(conn)
    return col in [c["name"] for c in insp.get_columns(table)]


def _add(table, column):
    conn = op.get_bind()
    if not _has_column(conn, table, column.name):
        op.add_column(table, column)


def upgrade() -> None:
    _add("users", sa.Column("mfa_enabled", sa.Boolean(), nullable=True, server_default=sa.false()))
    _add("users", sa.Column("mfa_enforced_at", sa.DateTime(timezone=True), nullable=True))
    _add("mfa_methods", sa.Column("secret", sa.String(length=255), nullable=True))
    _add("mfa_methods", sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.true()))
    _add("mfa_methods", sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True))
    _add("mfa_methods", sa.Column("recovery_codes_json", sa.JSON(), nullable=True))
    _add("mfa_methods", sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True))
    _add("mfa_methods", sa.Column("backup_email", sa.String(length=255), nullable=True))
    _add("login_attempts", sa.Column("success", sa.Boolean(), nullable=True))
    _add("login_attempts", sa.Column("mfa_attempted", sa.Boolean(), nullable=True, server_default=sa.false()))
    _add("login_attempts", sa.Column("mfa_success", sa.Boolean(), nullable=True))
    _add("password_policies", sa.Column("require_special", sa.Boolean(), nullable=True, server_default=sa.false()))
    _add("password_policies", sa.Column("max_age_days", sa.Integer(), nullable=True))
    _add("password_policies", sa.Column("lockout_duration_minutes", sa.Integer(), nullable=True))
    _add("password_policies", sa.Column("mfa_required", sa.Boolean(), nullable=True, server_default=sa.false()))
    _add("password_policies", sa.Column("is_default", sa.Boolean(), nullable=True, server_default=sa.false()))


def downgrade() -> None:
    for table, columns in {
        "password_policies": ["is_default", "mfa_required", "lockout_duration_minutes", "max_age_days", "require_special"],
        "login_attempts": ["mfa_success", "mfa_attempted", "success"],
        "mfa_methods": ["backup_email", "verified_at", "recovery_codes_json", "last_used_at", "is_active", "secret"],
        "users": ["mfa_enforced_at", "mfa_enabled"],
    }.items():
        for column in columns:
            if _has_column(op.get_bind(), table, column):
                op.drop_column(table, column)
