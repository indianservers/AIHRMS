from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class HelpdeskCategory(Base):
    __tablename__ = "helpdesk_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    sla_hours = Column(Integer, default=24)
    assigned_team = Column(String(100))
    is_active = Column(Boolean, default=True)

    tickets = relationship("HelpdeskTicket", back_populates="category")


class HelpdeskTicket(Base):
    __tablename__ = "helpdesk_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(30), unique=True, nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("helpdesk_categories.id", ondelete="SET NULL"), nullable=True)
    subject = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="Medium")  # Low, Medium, High, Critical
    status = Column(String(20), default="Open")  # Open, In Progress, Pending, Resolved, Closed
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))
    satisfaction_rating = Column(Integer)  # 1-5
    attachment_url = Column(String(500))
    ai_suggested_reply = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    employee = relationship("Employee", back_populates="helpdesk_tickets")
    category = relationship("HelpdeskCategory", back_populates="tickets")
    replies = relationship("HelpdeskReply", back_populates="ticket", cascade="all, delete-orphan")


class HelpdeskReply(Base):
    __tablename__ = "helpdesk_replies"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("helpdesk_tickets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)
    attachment_url = Column(String(500))
    is_ai_generated = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ticket = relationship("HelpdeskTicket", back_populates="replies")
