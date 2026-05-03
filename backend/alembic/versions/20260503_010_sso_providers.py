"""add sso providers

Revision ID: 20260503_010
Revises: 20260503_009
Create Date: 2026-05-03
"""

from alembic import op
import sqlalchemy as sa


revision = "20260503_010"
down_revision = "20260503_009"
branch_labels = None
depends_on = None


def _has_table(conn, name):
    return conn.dialect.has_table(conn, name)


def _has_column(conn, table, col):
    insp = sa.inspect(conn)
    return col in [c["name"] for c in insp.get_columns(table)]


def upgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn, "sso_providers"):
        op.create_table(
            "sso_providers",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("provider_type", sa.String(length=20), nullable=False),
            sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
            sa.Column("is_default", sa.Boolean(), server_default=sa.false()),
            sa.Column("button_label", sa.String(length=100)),
            sa.Column("button_icon", sa.String(length=50)),
            sa.Column("domain_hint", sa.String(length=255)),
            sa.Column("client_id", sa.String(length=500)),
            sa.Column("client_secret", sa.String(length=500)),
            sa.Column("authorization_url", sa.String(length=1000)),
            sa.Column("token_url", sa.String(length=1000)),
            sa.Column("userinfo_url", sa.String(length=1000)),
            sa.Column("scope", sa.String(length=500), server_default="openid email profile"),
            sa.Column("redirect_uri", sa.String(length=500)),
            sa.Column("idp_entity_id", sa.String(length=500)),
            sa.Column("idp_sso_url", sa.String(length=500)),
            sa.Column("idp_slo_url", sa.String(length=500)),
            sa.Column("idp_x509_cert", sa.Text()),
            sa.Column("sp_entity_id", sa.String(length=500)),
            sa.Column("sp_private_key", sa.Text()),
            sa.Column("sp_certificate", sa.Text()),
            sa.Column("attr_email", sa.String(length=100), server_default="email"),
            sa.Column("attr_first_name", sa.String(length=100), server_default="given_name"),
            sa.Column("attr_last_name", sa.String(length=100), server_default="family_name"),
            sa.Column("attr_role", sa.String(length=100)),
            sa.Column("auto_provision", sa.Boolean(), server_default=sa.true()),
            sa.Column("default_role_id", sa.Integer(), sa.ForeignKey("roles.id")),
            sa.Column("force_mfa", sa.Boolean(), server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True)),
        )
    if not _has_table(conn, "sso_sessions"):
        op.create_table(
            "sso_sessions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("provider_id", sa.Integer(), sa.ForeignKey("sso_providers.id")),
            sa.Column("state", sa.String(length=100), unique=True),
            sa.Column("nonce", sa.String(length=100)),
            sa.Column("relay_state", sa.String(length=500)),
            sa.Column("code_verifier", sa.String(length=200)),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")),
            sa.Column("completed", sa.Boolean(), server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("expires_at", sa.DateTime(timezone=True)),
        )
    if not _has_column(conn, "users", "sso_provider_id"):
        op.add_column("users", sa.Column("sso_provider_id", sa.Integer(), sa.ForeignKey("sso_providers.id"), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    if _has_column(conn, "users", "sso_provider_id"):
        op.drop_column("users", "sso_provider_id")
    if _has_table(conn, "sso_sessions"):
        op.drop_table("sso_sessions")
    if _has_table(conn, "sso_providers"):
        op.drop_table("sso_providers")
