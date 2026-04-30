from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, RequirePermission
from app.models.onboarding import EmployeeOnboarding, OnboardingTemplate, PolicyAcknowledgement
from app.models.user import User
from app.schemas.onboarding import (
    EmployeeOnboardingCreate,
    EmployeeOnboardingSchema,
    OnboardingTemplateCreate,
    OnboardingTemplateSchema,
    PolicyAcknowledgementCreate,
    PolicyAcknowledgementSchema,
)

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.get("/templates", response_model=list[OnboardingTemplateSchema])
def list_templates(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("employee_view"))):
    return db.query(OnboardingTemplate).order_by(OnboardingTemplate.created_at.desc()).all()


@router.post("/templates", response_model=OnboardingTemplateSchema, status_code=status.HTTP_201_CREATED)
def create_template(data: OnboardingTemplateCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("employee_update"))):
    template = OnboardingTemplate(**data.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.get("/employees", response_model=list[EmployeeOnboardingSchema])
def list_employee_onboarding(db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("employee_view"))):
    return db.query(EmployeeOnboarding).order_by(EmployeeOnboarding.created_at.desc()).limit(200).all()


@router.post("/employees", response_model=EmployeeOnboardingSchema, status_code=status.HTTP_201_CREATED)
def start_employee_onboarding(data: EmployeeOnboardingCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("employee_update"))):
    onboarding = EmployeeOnboarding(**data.model_dump(), status="In Progress")
    db.add(onboarding)
    db.commit()
    db.refresh(onboarding)
    return onboarding


@router.put("/employees/{onboarding_id}/complete", response_model=EmployeeOnboardingSchema)
def complete_onboarding(onboarding_id: int, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("employee_update"))):
    onboarding = db.get(EmployeeOnboarding, onboarding_id)
    if not onboarding:
        raise HTTPException(status_code=404, detail="Onboarding record not found")
    onboarding.status = "Completed"
    onboarding.completed_date = datetime.now(timezone.utc).date()
    db.commit()
    db.refresh(onboarding)
    return onboarding


@router.post("/policy-acknowledgements", response_model=PolicyAcknowledgementSchema, status_code=status.HTTP_201_CREATED)
def acknowledge_policy(data: PolicyAcknowledgementCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("ai_assistant"))):
    acknowledgement = PolicyAcknowledgement(**data.model_dump(), acknowledged_at=datetime.now(timezone.utc))
    db.add(acknowledgement)
    db.commit()
    db.refresh(acknowledgement)
    return acknowledgement
