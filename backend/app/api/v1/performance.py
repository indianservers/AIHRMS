from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user, RequirePermission
from app.models.user import User
from app.models.employee import Employee
from app.models.performance import (
    AppraisalCycle, CompensationCycle, Competency, EmployeeCompetencyAssessment,
    Feedback360Request, GoalCheckIn, MeritRecommendation, PayBand, PerformanceGoal,
    PerformanceReview, ReviewTemplate, ReviewTemplateQuestion, RoleSkillRequirement,
)
from app.schemas.performance import (
    AppraisalCycleCreate, AppraisalCycleSchema,
    CompensationCycleCreate, CompensationCycleSchema, CompetencyCreate, CompetencySchema,
    EmployeeCompetencyAssessmentCreate, EmployeeCompetencyAssessmentSchema,
    Feedback360RequestCreate, Feedback360RequestSchema, Feedback360Submit,
    GoalCheckInCreate, GoalCheckInSchema, MeritRecommendationCreate,
    MeritRecommendationReview, MeritRecommendationSchema, PayBandCreate, PayBandSchema,
    PerformanceGoalCreate, PerformanceGoalUpdate, PerformanceGoalSchema,
    PerformanceReviewCreate, PerformanceReviewSchema, ReviewTemplateCreate,
    ReviewTemplateSchema, RoleSkillRequirementCreate, RoleSkillRequirementSchema,
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


@router.post("/goals/check-ins", response_model=GoalCheckInSchema, status_code=201)
def create_goal_check_in(
    data: GoalCheckInCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.employee:
        raise HTTPException(status_code=400, detail="No employee profile")
    goal = db.query(PerformanceGoal).filter(PerformanceGoal.id == data.goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if goal.employee_id != current_user.employee.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Cannot check in for another employee goal")
    item = GoalCheckIn(employee_id=goal.employee_id, **data.model_dump())
    goal.status = "At Risk" if data.confidence == "At Risk" else goal.status
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/goals/{goal_id}/check-ins", response_model=List[GoalCheckInSchema])
def list_goal_check_ins(goal_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(GoalCheckIn).filter(GoalCheckIn.goal_id == goal_id).order_by(GoalCheckIn.checked_in_at.desc()).all()


@router.post("/review-templates", response_model=ReviewTemplateSchema, status_code=201)
def create_review_template(data: ReviewTemplateCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("performance_manage"))):
    payload = data.model_dump(exclude={"questions"})
    template = ReviewTemplate(**payload)
    db.add(template)
    db.flush()
    for question in data.questions:
        db.add(ReviewTemplateQuestion(template_id=template.id, **question.model_dump()))
    db.commit()
    db.refresh(template)
    return template


@router.get("/review-templates", response_model=List[ReviewTemplateSchema])
def list_review_templates(template_type: Optional[str] = Query(None), db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("performance_view"))):
    query = db.query(ReviewTemplate).filter(ReviewTemplate.is_active == True)
    if template_type:
        query = query.filter(ReviewTemplate.template_type == template_type)
    return query.order_by(ReviewTemplate.name).all()


@router.post("/360/requests", response_model=Feedback360RequestSchema, status_code=201)
@router.post("/360-feedback-requests", response_model=Feedback360RequestSchema, status_code=201)
def create_360_request(data: Feedback360RequestCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("performance_manage"))):
    item = Feedback360Request(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/360/requests/{request_id}/submit", response_model=Feedback360RequestSchema)
@router.put("/360-feedback-requests/{request_id}/submit", response_model=Feedback360RequestSchema)
def submit_360_feedback(request_id: int, data: Feedback360Submit, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(Feedback360Request).filter(Feedback360Request.id == request_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="360 feedback request not found")
    if current_user.employee and item.reviewer_id != current_user.employee.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only assigned reviewer can submit this feedback")
    item.responses_json = data.responses_json
    item.overall_rating = data.overall_rating
    item.comments = data.comments
    item.status = "Submitted"
    item.submitted_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item


@router.get("/360/requests", response_model=List[Feedback360RequestSchema])
@router.get("/360-feedback-requests", response_model=List[Feedback360RequestSchema])
def list_360_requests(employee_id: Optional[int] = Query(None), db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("performance_view"))):
    query = db.query(Feedback360Request)
    if employee_id:
        query = query.filter(Feedback360Request.employee_id == employee_id)
    return query.order_by(Feedback360Request.id.desc()).limit(300).all()


@router.post("/competencies", response_model=CompetencySchema, status_code=201)
def create_competency(data: CompetencyCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("performance_manage"))):
    if db.query(Competency).filter(Competency.code == data.code).first():
        raise HTTPException(status_code=400, detail="Competency code already exists")
    item = Competency(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/competencies", response_model=List[CompetencySchema])
def list_competencies(category: Optional[str] = Query(None), db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("performance_view"))):
    query = db.query(Competency).filter(Competency.is_active == True)
    if category:
        query = query.filter(Competency.category == category)
    return query.order_by(Competency.category, Competency.name).all()


@router.post("/role-skill-requirements", response_model=RoleSkillRequirementSchema, status_code=201)
def create_role_skill_requirement(data: RoleSkillRequirementCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("performance_manage"))):
    if not data.designation_id and not data.job_profile_id:
        raise HTTPException(status_code=400, detail="Either designation_id or job_profile_id is required")
    item = RoleSkillRequirement(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/competency-assessments", response_model=EmployeeCompetencyAssessmentSchema, status_code=201)
def create_competency_assessment(data: EmployeeCompetencyAssessmentCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("performance_manage"))):
    item = EmployeeCompetencyAssessment(**data.model_dump(), assessed_by=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/employees/{employee_id}/skill-gap")
def employee_skill_gap(employee_id: int, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("performance_view"))):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    requirements = db.query(RoleSkillRequirement).filter(
        RoleSkillRequirement.is_active == True,
        (RoleSkillRequirement.designation_id == employee.designation_id) | (RoleSkillRequirement.job_profile_id == None),
    ).all()
    assessments = {
        row.competency_id: row
        for row in db.query(EmployeeCompetencyAssessment).filter(EmployeeCompetencyAssessment.employee_id == employee_id).all()
    }
    gaps = []
    for requirement in requirements:
        assessment = assessments.get(requirement.competency_id)
        current_level = assessment.assessed_level if assessment else 0
        if current_level < requirement.required_level:
            gaps.append({
                "competency_id": requirement.competency_id,
                "competency_code": requirement.competency.code if requirement.competency else None,
                "competency_name": requirement.competency.name if requirement.competency else None,
                "required_level": requirement.required_level,
                "current_level": current_level,
                "gap": requirement.required_level - current_level,
                "importance": requirement.importance,
                "recommendation": "Assign learning path or mentor review",
            })
    return {"employee_id": employee_id, "gap_count": len(gaps), "gaps": gaps}


@router.post("/compensation/cycles", response_model=CompensationCycleSchema, status_code=201)
def create_compensation_cycle(data: CompensationCycleCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_run"))):
    item = CompensationCycle(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/compensation/pay-bands", response_model=PayBandSchema, status_code=201)
def create_pay_band(data: PayBandCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_run"))):
    if data.max_ctc and data.min_ctc and data.max_ctc < data.min_ctc:
        raise HTTPException(status_code=400, detail="max_ctc cannot be below min_ctc")
    item = PayBand(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/compensation/merit-recommendations", response_model=MeritRecommendationSchema, status_code=201)
def create_merit_recommendation(data: MeritRecommendationCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_run"))):
    increase_percent = Decimal("0")
    if data.current_ctc and data.current_ctc > 0:
        increase_percent = ((data.recommended_ctc - data.current_ctc) / data.current_ctc * Decimal("100")).quantize(Decimal("0.01"))
    item = MeritRecommendation(**data.model_dump(), increase_percent=increase_percent)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/compensation/merit-recommendations/{recommendation_id}", response_model=MeritRecommendationSchema)
def review_merit_recommendation(recommendation_id: int, data: MeritRecommendationReview, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("payroll_approve"))):
    item = db.query(MeritRecommendation).filter(MeritRecommendation.id == recommendation_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Merit recommendation not found")
    item.status = data.status
    item.manager_remarks = data.manager_remarks or item.manager_remarks
    if data.status in {"Approved", "Rejected"}:
        item.approved_by = current_user.id
        item.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item
