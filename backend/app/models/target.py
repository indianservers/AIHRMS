from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class IndustryTarget(Base):
    __tablename__ = "industry_targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, unique=True, index=True)
    slug = Column(String(120), nullable=False, unique=True, index=True)
    headline = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(80))
    color = Column(String(40), default="blue")
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FeaturePlan(Base):
    __tablename__ = "feature_plans"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(120), nullable=False)
    tagline = Column(String(255))
    strength = Column(Text)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    features = relationship("FeatureCatalog", back_populates="plan", cascade="all, delete-orphan")


class FeatureCatalog(Base):
    __tablename__ = "feature_catalog"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("feature_plans.id", ondelete="CASCADE"), nullable=True)
    module = Column(String(120), nullable=False, index=True)
    name = Column(String(180), nullable=False, index=True)
    description = Column(Text)
    is_highlight = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    plan = relationship("FeaturePlan", back_populates="features")
