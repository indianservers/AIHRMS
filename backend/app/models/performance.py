from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class AppraisalCycle(Base):
    __tablename__ = "appraisal_cycles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    cycle_type = Column(String(20))  # Annual, Semi-Annual, Quarterly
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    self_review_deadline = Column(Date)
    manager_review_deadline = Column(Date)
    status = Column(String(20), default="Upcoming")  # Upcoming, Self Review, Manager Review, Calibration, Completed
    description = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    goals = relationship("PerformanceGoal", back_populates="cycle")
    reviews = relationship("PerformanceReview", back_populates="cycle")


class PerformanceGoal(Base):
    __tablename__ = "performance_goals"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    cycle_id = Column(Integer, ForeignKey("appraisal_cycles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    goal_type = Column(String(20), default="KRA")  # KRA, KPI, Objective
    weightage = Column(Numeric(5, 2), default=100)
    target = Column(String(500))
    target_date = Column(Date)
    achievement = Column(Text)
    self_rating = Column(Numeric(3, 1))
    manager_rating = Column(Numeric(3, 1))
    status = Column(String(20), default="Active")  # Active, Completed, Cancelled

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    employee = relationship("Employee", back_populates="goals")
    cycle = relationship("AppraisalCycle", back_populates="goals")


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    cycle_id = Column(Integer, ForeignKey("appraisal_cycles.id", ondelete="CASCADE"), nullable=False)
    review_type = Column(String(20))  # Self, Manager, Peer, 360
    overall_rating = Column(Numeric(3, 1))
    strengths = Column(Text)
    improvements = Column(Text)
    comments = Column(Text)
    status = Column(String(20), default="Pending")  # Pending, Submitted, Acknowledged
    submitted_at = Column(DateTime(timezone=True))
    acknowledged_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    cycle = relationship("AppraisalCycle", back_populates="reviews")
