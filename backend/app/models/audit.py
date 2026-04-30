from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    method = Column(String(10), nullable=False)
    endpoint = Column(String(500))
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    status_code = Column(Integer)
    duration_ms = Column(Integer)
    entity_type = Column(String(100))
    entity_id = Column(Integer)
    action = Column(String(50))  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT
    old_values = Column(Text)  # JSON
    new_values = Column(Text)  # JSON
    description = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="audit_logs")
