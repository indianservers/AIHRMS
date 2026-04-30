from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class AppraisalCycleCreate(BaseModel):
    name: str
    cycle_type: Optional[str] = None
    start_date: date
    end_date: date
    self_review_deadline: Optional[date] = None
    manager_review_deadline: Optional[date] = None
    description: Optional[str] = None


class AppraisalCycleSchema(AppraisalCycleCreate):
    id: int
    status: str

    class Config:
        from_attributes = True


class PerformanceGoalCreate(BaseModel):
    cycle_id: int
    title: str
    description: Optional[str] = None
    goal_type: str = "KRA"
    weightage: Decimal = Decimal("100")
    target: Optional[str] = None
    target_date: Optional[date] = None


class PerformanceGoalUpdate(BaseModel):
    achievement: Optional[str] = None
    self_rating: Optional[Decimal] = None
    status: Optional[str] = None


class PerformanceGoalSchema(PerformanceGoalCreate):
    id: int
    employee_id: int
    achievement: Optional[str] = None
    self_rating: Optional[Decimal] = None
    manager_rating: Optional[Decimal] = None
    status: str

    class Config:
        from_attributes = True


class PerformanceReviewCreate(BaseModel):
    employee_id: Optional[int] = None
    cycle_id: Optional[int] = None
    review_type: str = "Self"
    overall_rating: Optional[Decimal] = None
    strengths: Optional[str] = None
    improvements: Optional[str] = None
    comments: Optional[str] = None


class PerformanceReviewSchema(PerformanceReviewCreate):
    id: int
    reviewer_id: int
    status: str
    submitted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
