from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import RequirePermission, get_current_user, get_db
from app.models.lms import LearningAssignment, LearningCertification, LearningCourse
from app.models.user import User
from app.schemas.lms import (
    LearningAssignmentCreate, LearningAssignmentSchema, LearningAssignmentUpdate,
    LearningCertificationCreate, LearningCertificationSchema,
    LearningCourseCreate, LearningCourseSchema,
)

router = APIRouter(prefix="/lms", tags=["Learning"])


@router.post("/courses", response_model=LearningCourseSchema, status_code=201)
def create_course(data: LearningCourseCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("performance_manage"))):
    course = LearningCourse(**data.model_dump(), created_by=current_user.id)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/courses", response_model=list[LearningCourseSchema])
def list_courses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(LearningCourse).filter(LearningCourse.is_active == True).order_by(LearningCourse.title).all()


@router.post("/assignments", response_model=LearningAssignmentSchema, status_code=201)
def assign_course(data: LearningAssignmentCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("performance_manage"))):
    assignment = LearningAssignment(**data.model_dump(), assigned_by=current_user.id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.put("/assignments/{assignment_id}", response_model=LearningAssignmentSchema)
def update_assignment(assignment_id: int, data: LearningAssignmentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    assignment = db.query(LearningAssignment).filter(LearningAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if not current_user.is_superuser and (not current_user.employee or current_user.employee.id != assignment.employee_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    assignment.status = data.status
    assignment.score = data.score
    if data.status == "Completed":
        assignment.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/assignments", response_model=list[LearningAssignmentSchema])
def list_assignments(employee_id: int | None = Query(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(LearningAssignment)
    if employee_id:
        query = query.filter(LearningAssignment.employee_id == employee_id)
    elif current_user.employee and not current_user.is_superuser:
        query = query.filter(LearningAssignment.employee_id == current_user.employee.id)
    return query.order_by(LearningAssignment.id.desc()).limit(200).all()


@router.post("/certifications", response_model=LearningCertificationSchema, status_code=201)
def create_certification(data: LearningCertificationCreate, db: Session = Depends(get_db), current_user: User = Depends(RequirePermission("performance_manage"))):
    cert = LearningCertification(**data.model_dump(), verified_by=current_user.id)
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


@router.get("/certifications", response_model=list[LearningCertificationSchema])
def list_certifications(employee_id: int | None = Query(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(LearningCertification)
    if employee_id:
        query = query.filter(LearningCertification.employee_id == employee_id)
    elif current_user.employee and not current_user.is_superuser:
        query = query.filter(LearningCertification.employee_id == current_user.employee.id)
    return query.order_by(LearningCertification.expires_on.asc().nullslast()).limit(200).all()
