from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("idx_notifications_user_unread", "user_id", "is_read", "created_at"),
        Index("idx_notifications_company_user_unread", "company_id", "user_id", "is_read", "created_at"),
        Index("idx_notifications_company_module", "company_id", "module", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    module = Column(String(50), nullable=True, index=True)
    event_type = Column(String(80), nullable=True, index=True)
    related_entity_type = Column(String(80), nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    action_url = Column(String(500), nullable=True)
    priority = Column(String(20), default="normal")
    channels = Column(JSON, default=lambda: ["in_app"])
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="notifications")
    delivery_logs = relationship("NotificationDeliveryLog", back_populates="notification", cascade="all, delete-orphan")


class NotificationDeliveryLog(Base):
    __tablename__ = "notification_delivery_logs"
    __table_args__ = (
        Index("idx_notification_delivery_channel_status", "channel", "status", "attempted_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(String(20), nullable=False)  # in_app, email, whatsapp, push, sms
    recipient = Column(String(200), nullable=True)
    status = Column(String(30), default="queued")
    provider_message_id = Column(String(200), nullable=True)
    error_message = Column(Text, nullable=True)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True), nullable=True)

    notification = relationship("Notification", back_populates="delivery_logs")
