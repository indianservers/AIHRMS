from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, RequirePermission
from app.models.user import User
from app.models.performance import AppraisalCycle, PerformanceGoal, PerformanceReview
from app.schemas.performance import (
    AppraisalCycleCreate, AppraisalCycleSchema,
    PerformanceGoalCreate, PerformanceGoalUpdate, PerformanceGoalSchema,
    PerformanceReviewCreate, PerformanceReviewSchema,
)

router = APIRouter(prefix="/performance", tags=["Performance Management"])


@router.get("/cycles", response_model=List[AppraisalCycleSchema])
def list_cycles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(AppraisalCycle).order_by(AppraisalCycle.start_date.desc()).all()


@router.post("/cycles", response_model=AppraisalCycleSchema, status_code=201)
def create_cycle(
    data: AppraisalCycleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("performance_manage")),
):
    cycle = AppraisalCycle(**data.model_dump())
    db.add(cycle)
    db.commit()
    db.refresh(cycle)
    return cycle


@router.put("/cycles/{cycle_id}/status")
def update_cycle_status(
    cycle_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("performance_manage")),
):
    cycle = db.query(AppraisalCycle).filter(AppraisalCycle.id == cycle_id).first()
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    cycle.status = status
    db.commit()
    return {"message": f"Cycle status updated to {status}"}


# ── Goals ──────────────────────────────────────────────────────────────────────

@router.get("/goals", response_model=List[PerformanceGoalSchema])
def list_my_goals(
    cycle_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile")
    q = db.query(PerformanceGoal).filter(PerformanceGoal.employee_id == current_user.employee.id)
    if cycle_id:
        q = q.filter(PerformanceGoal.cycle_id == cycle_id)
    return q.all()


@router.post("/goals", response_model=PerformanceGoalSchema, status_code=201)
def create_goal(
    data: PerformanceGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile")
    goal = PerformanceGoal(employee_id=current_user.employee.id, **data.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.put("/goals/{goal_id}", response_model=PerformanceGoalSchema)
def update_goal(
    goal_id: int,
    data: PerformanceGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(PerformanceGoal).filter(PerformanceGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(goal, k, v)
    db.commit()
    db.refresh(goal)
    return goal


# ── Reviews ───────────────────────────────────────────────────────────────────

@router.post("/reviews", response_model=PerformanceReviewSchema, status_code=201)
def submit_review(
    data: PerformanceReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile")
    from datetime import datetime, timezone
    payload = data.model_dump()
    if not payload.get("employee_id"):
        payload["employee_id"] = current_user.employee.id
    if not payload.get("cycle_id"):
        cycle = db.query(AppraisalCycle).order_by(AppraisalCycle.start_date.desc()).first()
        if not cycle:
            raise HTTPException(status_code=400, detail="Create an appraisal cycle before submitting reviews")
        payload["cycle_id"] = cycle.id
    review = PerformanceReview(
        reviewer_id=current_user.employee.id,
        status="Submitted",
        submitted_at=datetime.now(timezone.utc),
        **payload,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/reviews/{employee_id}", response_model=List[PerformanceReviewSchema])
def get_employee_reviews(
    employee_id: int,
    cycle_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RequirePermission("performance_view")),
):
    q = db.query(PerformanceReview).filter(PerformanceReview.employee_id == employee_id)
    if cycle_id:
        q = q.filter(PerformanceReview.cycle_id == cycle_id)
    return q.all()
