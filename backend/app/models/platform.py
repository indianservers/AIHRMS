from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base


class CustomFieldDefinition(Base):
    __tablename__ = "custom_field_definitions"

    id = Column(Integer, primary_key=True, index=True)
    module = Column(String(80), nullable=False, index=True)
    section = Column(String(120), default="General")
    field_key = Column(String(120), nullable=False, index=True)
    label = Column(String(150), nullable=False)
    field_type = Column(String(40), default="Text")
    options_json = Column(JSON)
    validation_json = Column(JSON)
    is_required = Column(Boolean, default=False)
    is_sensitive = Column(Boolean, default=False)
    visible_to_roles = Column(String(250))
    editable_by_roles = Column(String(250))
    display_order = Column(Integer, default=100)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CustomFieldValue(Base):
    __tablename__ = "custom_field_values"

    id = Column(Integer, primary_key=True, index=True)
    definition_id = Column(Integer, ForeignKey("custom_field_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(80), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)
    value_text = Column(Text)
    value_json = Column(JSON)
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ReportDefinition(Base):
    __tablename__ = "report_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    code = Column(String(80), nullable=False, unique=True, index=True)
    module = Column(String(80), nullable=False, index=True)
    field_catalog_json = Column(JSON)
    selected_fields_json = Column(JSON)
    filters_json = Column(JSON)
    schedule_cron = Column(String(80))
    export_format = Column(String(20), default="csv")
    visible_to_roles = Column(String(250))
    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ReportRun(Base):
    __tablename__ = "report_runs"

    id = Column(Integer, primary_key=True, index=True)
    report_definition_id = Column(Integer, ForeignKey("report_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(30), default="Queued", index=True)
    row_count = Column(Integer, default=0)
    file_url = Column(String(500))
    error_message = Column(Text)
    requested_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
