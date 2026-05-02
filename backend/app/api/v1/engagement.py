from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import RequirePermission, get_current_user, get_db
from app.models.engagement import Announcement, EngagementSurvey, EngagementSurveyResponse, Recognition
from app.models.user import User
from app.schemas.engagement import (
    AnnouncementCreate, AnnouncementSchema, EngagementSurveyCreate, EngagementSurveyResponseCreate,
    EngagementSurveyResponseSchema, EngagementSurveySchema, RecognitionCreate, RecognitionSchema,
)

router = APIRouter(prefix="/engagement", tags=["Engagement"])


@router.post("/announcements", response_model=AnnouncementSchema, status_code=201)
def create_announcement(data: AnnouncementCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("notification_manage"))):
    item = Announcement(**data.model_dump(), created_by=current_user.id)
    if data.is_published:
        item.published_at = datetime.now(timezone.utc)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/announcements", response_model=list[AnnouncementSchema])
def list_announcements(published_only: bool = Query(True), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Announcement)
    if published_only:
        query = query.filter(Announcement.is_published == True)
    return query.order_by(Announcement.created_at.desc()).limit(100).all()


@router.post("/surveys", response_model=EngagementSurveySchema, status_code=201)
def create_survey(data: EngagementSurveyCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("performance_manage"))):
    survey = EngagementSurvey(**data.model_dump(), created_by=current_user.id)
    db.add(survey)
    db.commit()
    db.refresh(survey)
    return survey


@router.post("/survey-responses", response_model=EngagementSurveyResponseSchema, status_code=201)
def submit_survey_response(data: EngagementSurveyResponseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    employee_id = data.employee_id or (current_user.employee.id if current_user.employee else None)
    if not employee_id:
        raise HTTPException(status_code=400, detail="No employee profile")
    response = EngagementSurveyResponse(**data.model_dump(exclude={"employee_id"}), employee_id=employee_id)
    db.add(response)
    db.commit()
    db.refresh(response)
    return response


@router.post("/recognitions", response_model=RecognitionSchema, status_code=201)
def create_recognition(data: RecognitionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from_employee_id = current_user.employee.id if current_user.employee else None
    recognition = Recognition(**data.model_dump(), from_employee_id=from_employee_id)
    db.add(recognition)
    db.commit()
    db.refresh(recognition)
    return recognition


@router.get("/recognitions", response_model=list[RecognitionSchema])
def list_recognitions(employee_id: int | None = Query(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Recognition).filter(Recognition.is_public == True)
    if employee_id:
        query = query.filter(Recognition.to_employee_id == employee_id)
    return query.order_by(Recognition.created_at.desc()).limit(100).all()
