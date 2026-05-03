from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from app.db.base_class import Base


class SSOProvider(Base):
    __tablename__ = "sso_providers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    provider_type = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    button_label = Column(String(100))
    button_icon = Column(String(50))
    domain_hint = Column(String(255))
    client_id = Column(String(500))
    client_secret = Column(String(500))
    authorization_url = Column(String(1000))
    token_url = Column(String(1000))
    userinfo_url = Column(String(1000))
    scope = Column(String(500), default="openid email profile")
    redirect_uri = Column(String(500))
    idp_entity_id = Column(String(500))
    idp_sso_url = Column(String(500))
    idp_slo_url = Column(String(500))
    idp_x509_cert = Column(Text)
    sp_entity_id = Column(String(500))
    sp_private_key = Column(Text)
    sp_certificate = Column(Text)
    attr_email = Column(String(100), default="email")
    attr_first_name = Column(String(100), default="given_name")
    attr_last_name = Column(String(100), default="family_name")
    attr_role = Column(String(100))
    auto_provision = Column(Boolean, default=True)
    default_role_id = Column(Integer, ForeignKey("roles.id"))
    force_mfa = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SSOSession(Base):
    __tablename__ = "sso_sessions"

    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey("sso_providers.id"))
    state = Column(String(100), unique=True)
    nonce = Column(String(100))
    relay_state = Column(String(500))
    code_verifier = Column(String(200))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
