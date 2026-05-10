"""Project Management (KaryaFlow) API routes."""
import json
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.apps.project_management.models import (
    PMSClient, PMSProject, PMSProjectMember, PMSTask, PMSBoard, PMSBoardColumn,
    PMSMilestone, PMSSprint, PMSComment, PMSTimeLog, PMSFileAsset, PMSTaskDependency,
    PMSChecklistItem, PMSTag, PMSTaskTag, PMSClientApproval, PMSEpic, PMSComponent, PMSRelease,
    PMSSavedFilter, PMSActivity
)
from app.apps.project_management.access import (
    accessible_project_query,
    can_access_project,
    get_project_for_action,
    get_task_project_for_action,
    has_any_permission,
    organization_id_for,
    PMS_GLOBAL_MANAGE_PROJECTS,
)
from app.apps.project_management.schemas import (
    PMSProjectCreate, PMSProjectUpdate, PMSProjectResponse,
    PMSTaskCreate, PMSTaskUpdate, PMSTaskResponse,
    PMSClientCreate, PMSClientUpdate, PMSClientResponse,
    PMSMilestoneCreate, PMSMilestoneUpdate, PMSMilestoneResponse,
    PMSBoardCreate, PMSBoardResponse,
    PMSProjectMemberCreate, PMSProjectMemberUpdate, PMSProjectMemberResponse,
    PMSEpicCreate, PMSEpicUpdate, PMSEpicResponse,
    PMSComponentCreate, PMSComponentUpdate, PMSComponentResponse,
    PMSReleaseCreate, PMSReleaseUpdate, PMSReleaseResponse,
    PMSCommentCreate, PMSCommentUpdate, PMSCommentResponse,
    PMSTimeLogCreate, PMSTimeLogUpdate, PMSTimeLogResponse,
    PMSSprintCreate, PMSSprintUpdate, PMSSprintResponse,
    SprintCompleteRequest, SprintBurndownResponse, ProjectVelocityResponse,
    PMSFileAssetCreate, PMSFileAssetUpdate, PMSFileAssetResponse,
    PMSClientApprovalCreate, PMSClientApprovalUpdate, PMSClientApprovalResponse,
    PMSTaskDependencyCreate, PMSTaskDependencyResponse, PMSTaskDependencyDetail,
    TaskBulkUpdateRequest, TaskBulkUpdateResponse,
    PMSSavedFilterCreate, PMSSavedFilterUpdate, PMSSavedFilterResponse,
    PMSActivityResponse, ReleaseReadinessResponse, WorkloadResponse,
    KanbanBoard, TaskReorderRequest, ProjectMetrics, DashboardResponse,
)

router = APIRouter(prefix="/project-management", tags=["Project Management"])


DONE_STATUSES = {"Done", "Completed", "Closed", "Resolved"}


def _task_points(task: PMSTask) -> int:
    return int(task.story_points or 0)


def _record_activity(
    db: Session,
    project_id: int,
    current_user: User,
    action: str,
    entity_type: str,
    entity_id: int | None,
    summary: str,
    task_id: int | None = None,
    sprint_id: int | None = None,
    metadata: dict | None = None,
) -> None:
    db.add(PMSActivity(
        project_id=project_id,
        task_id=task_id,
        sprint_id=sprint_id,
        actor_user_id=getattr(current_user, "id", None),
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        summary=summary,
        metadata_json=json.dumps(metadata or {}, default=str),
    ))


def _sync_sprint_rollups(db: Session, sprint: PMSSprint) -> None:
    tasks = db.query(PMSTask).filter(
        PMSTask.sprint_id == sprint.id,
        PMSTask.deleted_at == None,
    ).all()
    sprint.committed_task_count = sprint.committed_task_count or len(tasks)
    if sprint.status == "Completed":
        sprint.completed_story_points = sum(_task_points(task) for task in tasks if task.status in DONE_STATUSES)
        sprint.velocity_points = sprint.completed_story_points


def _sync_task_planning_links(db: Session, project_id: int, task_data: dict) -> None:
    """Validate normalized planning links and mirror labels for existing UI fields."""
    if task_data.get("epic_id"):
        epic = db.query(PMSEpic).filter(
            PMSEpic.id == task_data["epic_id"],
            PMSEpic.project_id == project_id,
            PMSEpic.deleted_at == None,
        ).first()
        if not epic:
            raise HTTPException(status_code=400, detail="Epic does not belong to selected project")
        task_data["epic_key"] = epic.epic_key
        task_data["initiative"] = epic.name
    if task_data.get("component_id"):
        component = db.query(PMSComponent).filter(
            PMSComponent.id == task_data["component_id"],
            PMSComponent.project_id == project_id,
        ).first()
        if not component:
            raise HTTPException(status_code=400, detail="Component does not belong to selected project")
        task_data["component"] = component.name
    if task_data.get("release_id"):
        release = db.query(PMSRelease).filter(
            PMSRelease.id == task_data["release_id"],
            PMSRelease.project_id == project_id,
            PMSRelease.deleted_at == None,
        ).first()
        if not release:
            raise HTTPException(status_code=400, detail="Release does not belong to selected project")
        task_data["release_name"] = release.name
        task_data["fix_version"] = release.name


@router.get("/module-info")
def module_info():
    return {
        "key": "project_management",
        "name": "KaryaFlow",
        "status": "installed",
        "description": "Complete project management with Kanban, Gantt, milestones, and collaboration",
        "modules": [
            "clients",
            "projects",
            "project-members",
            "epics",
            "components",
            "releases",
            "boards",
            "board-columns",
            "tasks",
            "dependencies",
            "bulk-updates",
            "saved-filters",
            "activity-feed",
            "release-readiness",
            "workload-capacity",
            "velocity-burndown",
            "checklists",
            "milestones",
            "sprints",
            "files",
            "comments",
            "time-logs",
            "client-approvals",
        ],
    }


# ============= CLIENTS =============
@router.post("/clients", response_model=PMSClientResponse)
def create_client(
    client_in: PMSClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new client."""
    if not has_any_permission(current_user, PMS_GLOBAL_MANAGE_PROJECTS):
        raise HTTPException(status_code=403, detail="Project management permission required")
    db_client = PMSClient(
        organization_id=organization_id_for(current_user),
        **client_in.dict()
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.get("/clients", response_model=list[PMSClientResponse])
def list_clients(
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all clients for the organization."""
    if not has_any_permission(current_user, PMS_GLOBAL_MANAGE_PROJECTS):
        raise HTTPException(status_code=403, detail="Project management permission required")
    clients = db.query(PMSClient).filter(
        PMSClient.organization_id == organization_id_for(current_user),
        PMSClient.deleted_at == None
    ).offset(skip).limit(limit).all()
    return clients


@router.get("/clients/{client_id}", response_model=PMSClientResponse)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific client."""
    if not has_any_permission(current_user, PMS_GLOBAL_MANAGE_PROJECTS):
        raise HTTPException(status_code=403, detail="Project management permission required")
    client = db.query(PMSClient).filter(
        PMSClient.id == client_id,
        PMSClient.organization_id == organization_id_for(current_user)
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.patch("/clients/{client_id}", response_model=PMSClientResponse)
def update_client(
    client_id: int,
    client_in: PMSClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a client."""
    if not has_any_permission(current_user, PMS_GLOBAL_MANAGE_PROJECTS):
        raise HTTPException(status_code=403, detail="Project management permission required")
    client = db.query(PMSClient).filter(
        PMSClient.id == client_id,
        PMSClient.organization_id == organization_id_for(current_user)
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    update_data = client_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.delete("/clients/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete a client."""
    if not has_any_permission(current_user, PMS_GLOBAL_MANAGE_PROJECTS):
        raise HTTPException(status_code=403, detail="Project management permission required")
    client = db.query(PMSClient).filter(
        PMSClient.id == client_id,
        PMSClient.organization_id == organization_id_for(current_user)
    ).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    from datetime import datetime
    client.deleted_at = datetime.utcnow()
    db.add(client)
    db.commit()
    return {"message": "Client deleted"}


# ============= PROJECTS =============
@router.post("/projects", response_model=PMSProjectResponse)
def create_project(
    project_in: PMSProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new project."""
    if not has_any_permission(current_user, PMS_GLOBAL_MANAGE_PROJECTS):
        raise HTTPException(status_code=403, detail="Project management permission required")
    # Check unique constraint on project_key
    existing = db.query(PMSProject).filter(
        PMSProject.organization_id == organization_id_for(current_user),
        PMSProject.project_key == project_in.project_key.upper()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project key already exists")
    
    db_project = PMSProject(
        organization_id=organization_id_for(current_user),
        **project_in.dict()
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    if not db.query(PMSProjectMember).filter(
        PMSProjectMember.project_id == db_project.id,
        PMSProjectMember.user_id == current_user.id,
    ).first():
        db.add(PMSProjectMember(project_id=db_project.id, user_id=current_user.id, role="Manager"))
        if db_project.manager_user_id and db_project.manager_user_id != current_user.id:
            db.add(PMSProjectMember(project_id=db_project.id, user_id=db_project.manager_user_id, role="Manager"))
        db.commit()
    return db_project


@router.get("/projects", response_model=list[PMSProjectResponse])
def list_projects(
    skip: int = Query(0),
    limit: int = Query(100),
    status: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all projects for the organization."""
    query = accessible_project_query(db, current_user)
    
    if status:
        query = query.filter(PMSProject.status == status)
    
    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/projects/{project_id}", response_model=PMSProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific project."""
    return get_project_for_action(db, project_id, current_user)


@router.patch("/projects/{project_id}", response_model=PMSProjectResponse)
def update_project(
    project_id: int,
    project_in: PMSProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a project."""
    project = get_project_for_action(db, project_id, current_user, "edit_project")
    
    update_data = project_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete a project."""
    project = get_project_for_action(db, project_id, current_user, "edit_project")
    
    from datetime import datetime
    project.deleted_at = datetime.utcnow()
    db.add(project)
    db.commit()
    return {"message": "Project deleted"}


# ============= PROJECT MEMBERS =============
@router.post("/projects/{project_id}/members", response_model=PMSProjectMemberResponse, status_code=status.HTTP_201_CREATED)
def add_project_member(
    project_id: int,
    member_in: PMSProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a user to a project with a project role."""
    get_project_for_action(db, project_id, current_user, "manage_members")
    existing = db.query(PMSProjectMember).filter(
        PMSProjectMember.project_id == project_id,
        PMSProjectMember.user_id == member_in.user_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project member already exists")
    member = PMSProjectMember(project_id=project_id, **member_in.dict())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get("/projects/{project_id}/members", response_model=list[PMSProjectMemberResponse])
def list_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List project members visible to project users."""
    get_project_for_action(db, project_id, current_user, "browse")
    return db.query(PMSProjectMember).filter(PMSProjectMember.project_id == project_id).all()


@router.patch("/projects/{project_id}/members/{member_id}", response_model=PMSProjectMemberResponse)
def update_project_member(
    project_id: int,
    member_id: int,
    member_in: PMSProjectMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a project member role."""
    get_project_for_action(db, project_id, current_user, "manage_members")
    member = db.query(PMSProjectMember).filter(
        PMSProjectMember.id == member_id,
        PMSProjectMember.project_id == project_id,
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Project member not found")
    for field, value in member_in.dict(exclude_unset=True).items():
        setattr(member, field, value)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/projects/{project_id}/members/{member_id}")
def remove_project_member(
    project_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a user from a project."""
    get_project_for_action(db, project_id, current_user, "manage_members")
    member = db.query(PMSProjectMember).filter(
        PMSProjectMember.id == member_id,
        PMSProjectMember.project_id == project_id,
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Project member not found")
    db.delete(member)
    db.commit()
    return {"message": "Project member removed"}


# ============= EPICS, COMPONENTS, RELEASES =============
@router.post("/projects/{project_id}/epics", response_model=PMSEpicResponse, status_code=status.HTTP_201_CREATED)
def create_epic(
    project_id: int,
    epic_in: PMSEpicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a project epic."""
    get_project_for_action(db, project_id, current_user, "manage_tasks")
    existing = db.query(PMSEpic).filter(
        PMSEpic.project_id == project_id,
        PMSEpic.epic_key == epic_in.epic_key.upper(),
        PMSEpic.deleted_at == None,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Epic key already exists in this project")
    epic = PMSEpic(project_id=project_id, **epic_in.dict())
    db.add(epic)
    db.commit()
    db.refresh(epic)
    return epic


@router.get("/projects/{project_id}/epics", response_model=list[PMSEpicResponse])
def list_epics(
    project_id: int,
    status_filter: str = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List project epics."""
    get_project_for_action(db, project_id, current_user, "browse")
    query = db.query(PMSEpic).filter(PMSEpic.project_id == project_id, PMSEpic.deleted_at == None)
    if status_filter:
        query = query.filter(PMSEpic.status == status_filter)
    return query.order_by(PMSEpic.created_at.desc()).all()


@router.patch("/epics/{epic_id}", response_model=PMSEpicResponse)
def update_epic(
    epic_id: int,
    epic_in: PMSEpicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a project epic."""
    epic = db.query(PMSEpic).filter(PMSEpic.id == epic_id, PMSEpic.deleted_at == None).first()
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")
    get_project_for_action(db, epic.project_id, current_user, "manage_tasks")
    for field, value in epic_in.dict(exclude_unset=True).items():
        setattr(epic, field, value)
    db.add(epic)
    db.commit()
    db.refresh(epic)
    return epic


@router.post("/projects/{project_id}/components", response_model=PMSComponentResponse, status_code=status.HTTP_201_CREATED)
def create_component(
    project_id: int,
    component_in: PMSComponentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a project component."""
    get_project_for_action(db, project_id, current_user, "manage_tasks")
    existing = db.query(PMSComponent).filter(
        PMSComponent.project_id == project_id,
        PMSComponent.name == component_in.name,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Component already exists in this project")
    component = PMSComponent(project_id=project_id, **component_in.dict())
    db.add(component)
    db.commit()
    db.refresh(component)
    return component


@router.get("/projects/{project_id}/components", response_model=list[PMSComponentResponse])
def list_components(
    project_id: int,
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List project components."""
    get_project_for_action(db, project_id, current_user, "browse")
    query = db.query(PMSComponent).filter(PMSComponent.project_id == project_id)
    if active_only:
        query = query.filter(PMSComponent.is_active == True)
    return query.order_by(PMSComponent.name).all()


@router.patch("/components/{component_id}", response_model=PMSComponentResponse)
def update_component(
    component_id: int,
    component_in: PMSComponentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a project component."""
    component = db.query(PMSComponent).filter(PMSComponent.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    get_project_for_action(db, component.project_id, current_user, "manage_tasks")
    for field, value in component_in.dict(exclude_unset=True).items():
        setattr(component, field, value)
    db.add(component)
    db.commit()
    db.refresh(component)
    return component


@router.post("/projects/{project_id}/releases", response_model=PMSReleaseResponse, status_code=status.HTTP_201_CREATED)
def create_release(
    project_id: int,
    release_in: PMSReleaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a project release."""
    get_project_for_action(db, project_id, current_user, "manage_tasks")
    existing = db.query(PMSRelease).filter(
        PMSRelease.project_id == project_id,
        PMSRelease.name == release_in.name,
        PMSRelease.deleted_at == None,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Release already exists in this project")
    release = PMSRelease(project_id=project_id, **release_in.dict())
    db.add(release)
    db.commit()
    db.refresh(release)
    return release


@router.get("/projects/{project_id}/releases", response_model=list[PMSReleaseResponse])
def list_releases(
    project_id: int,
    status_filter: str = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List project releases."""
    get_project_for_action(db, project_id, current_user, "browse")
    query = db.query(PMSRelease).filter(PMSRelease.project_id == project_id, PMSRelease.deleted_at == None)
    if status_filter:
        query = query.filter(PMSRelease.status == status_filter)
    return query.order_by(PMSRelease.release_date.is_(None), PMSRelease.release_date, PMSRelease.id).all()


@router.patch("/releases/{release_id}", response_model=PMSReleaseResponse)
def update_release(
    release_id: int,
    release_in: PMSReleaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a project release."""
    release = db.query(PMSRelease).filter(PMSRelease.id == release_id, PMSRelease.deleted_at == None).first()
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    get_project_for_action(db, release.project_id, current_user, "manage_tasks")
    for field, value in release_in.dict(exclude_unset=True).items():
        setattr(release, field, value)
    db.add(release)
    db.commit()
    db.refresh(release)
    return release


@router.get("/releases/{release_id}/readiness", response_model=ReleaseReadinessResponse)
def get_release_readiness(
    release_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Summarize release readiness, blockers, severity, and overdue risk."""
    release = db.query(PMSRelease).filter(PMSRelease.id == release_id, PMSRelease.deleted_at == None).first()
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    get_project_for_action(db, release.project_id, current_user, "browse")
    tasks = db.query(PMSTask).filter(
        PMSTask.project_id == release.project_id,
        PMSTask.release_id == release_id,
        PMSTask.deleted_at == None,
    ).all()
    total = len(tasks)
    done = len([task for task in tasks if task.status in DONE_STATUSES])
    today = date.today()
    open_blockers = len([task for task in tasks if task.is_blocking and task.status not in DONE_STATUSES])
    overdue = len([task for task in tasks if task.due_date and task.due_date < today and task.status not in DONE_STATUSES])
    severity_counts: dict[str, int] = {}
    for task in tasks:
        if task.severity:
            severity_counts[task.severity] = severity_counts.get(task.severity, 0) + 1
    readiness = release.readiness_percent if release.readiness_percent is not None else int((done / total) * 100) if total else 0
    health = "Blocked" if open_blockers else "At Risk" if overdue or severity_counts.get("S1", 0) else "Ready" if readiness >= 90 else "On Track"
    return {
        "release_id": release.id,
        "release_name": release.name,
        "readiness_percent": readiness,
        "health": health,
        "total_tasks": total,
        "done_tasks": done,
        "open_blockers": open_blockers,
        "overdue_tasks": overdue,
        "severity_counts": severity_counts,
    }


# ============= TASKS (KANBAN & CRUD) =============
@router.post("/projects/{project_id}/tasks", response_model=PMSTaskResponse)
def create_task(
    project_id: int,
    task_in: PMSTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task in a project."""
    # Verify project exists
    get_project_for_action(db, project_id, current_user, "manage_tasks")
    
    # Check unique constraint on task_key
    existing = db.query(PMSTask).filter(
        PMSTask.project_id == project_id,
        PMSTask.task_key == task_in.task_key.upper()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Task key already exists in this project")
    
    task_data = task_in.dict()
    task_data['project_id'] = project_id
    _sync_task_planning_links(db, project_id, task_data)
    if not task_data.get("column_id"):
        board = db.query(PMSBoard).filter(PMSBoard.project_id == project_id).first()
        if not board:
            board = PMSBoard(project_id=project_id, name="Default Board", board_type="Kanban")
            db.add(board)
            db.commit()
            db.refresh(board)
        status_to_key = {
            "Backlog": "BACKLOG",
            "To Do": "TODO",
            "In Progress": "IN_PROGRESS",
            "In Review": "IN_REVIEW",
            "Blocked": "IN_PROGRESS",
            "Done": "DONE",
        }
        target_status_key = status_to_key.get(task_data.get("status", "To Do"), "TODO")
        column = db.query(PMSBoardColumn).filter(
            PMSBoardColumn.board_id == board.id,
            PMSBoardColumn.status_key == target_status_key,
        ).first()
        if not column:
            defaults = [
                ("Backlog", "BACKLOG", 0),
                ("To Do", "TODO", 1),
                ("In Progress", "IN_PROGRESS", 2),
                ("In Review", "IN_REVIEW", 3),
                ("Done", "DONE", 4),
            ]
            for name, status_key, position in defaults:
                db.add(PMSBoardColumn(board_id=board.id, name=name, status_key=status_key, position=position))
            db.commit()
            column = db.query(PMSBoardColumn).filter(
                PMSBoardColumn.board_id == board.id,
                PMSBoardColumn.status_key == target_status_key,
            ).first()
        task_data["board_id"] = board.id
        task_data["column_id"] = column.id if column else None
        task_data["position"] = db.query(PMSTask).filter(
            PMSTask.project_id == project_id,
            PMSTask.column_id == task_data["column_id"],
            PMSTask.deleted_at == None,
        ).count()
    if task_data.get("rank") is None:
        task_data["rank"] = db.query(PMSTask).filter(
            PMSTask.project_id == project_id,
            PMSTask.deleted_at == None,
        ).count() + 1
    db_task = PMSTask(**task_data)
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    _record_activity(db, project_id, current_user, "created", "task", db_task.id, f"Created task {db_task.task_key}", task_id=db_task.id)
    db.commit()
    return db_task


@router.get("/projects/{project_id}/tasks", response_model=list[PMSTaskResponse])
def list_tasks(
    project_id: int,
    skip: int = Query(0),
    limit: int = Query(100),
    status: str = Query(None),
    assignee_id: int = Query(None),
    sprint_id: int = Query(None),
    epic_id: int = Query(None),
    component_id: int = Query(None),
    release_id: int = Query(None),
    work_type: str = Query(None),
    epic_key: str = Query(None),
    component: str = Query(None),
    severity: str = Query(None),
    fix_version: str = Query(None),
    release_name: str = Query(None),
    security_level: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all tasks in a project."""
    # Verify project exists
    get_project_for_action(db, project_id, current_user, "browse")
    
    query = db.query(PMSTask).filter(
        PMSTask.project_id == project_id,
        PMSTask.deleted_at == None
    )
    
    if status:
        query = query.filter(PMSTask.status == status)
    if assignee_id:
        query = query.filter(PMSTask.assignee_user_id == assignee_id)
    if sprint_id:
        query = query.filter(PMSTask.sprint_id == sprint_id)
    if epic_id:
        query = query.filter(PMSTask.epic_id == epic_id)
    if component_id:
        query = query.filter(PMSTask.component_id == component_id)
    if release_id:
        query = query.filter(PMSTask.release_id == release_id)
    if work_type:
        query = query.filter(PMSTask.work_type == work_type)
    if epic_key:
        query = query.filter(PMSTask.epic_key == epic_key)
    if component:
        query = query.filter(PMSTask.component == component)
    if severity:
        query = query.filter(PMSTask.severity == severity)
    if fix_version:
        query = query.filter(PMSTask.fix_version == fix_version)
    if release_name:
        query = query.filter(PMSTask.release_name == release_name)
    if security_level:
        query = query.filter(PMSTask.security_level == security_level)
    
    tasks = query.order_by(PMSTask.rank.is_(None), PMSTask.rank, PMSTask.position, PMSTask.id).offset(skip).limit(limit).all()
    return tasks


@router.patch("/tasks/bulk", response_model=TaskBulkUpdateResponse)
def bulk_update_tasks(
    bulk_in: TaskBulkUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk update common planning fields across selected tasks."""
    tasks = db.query(PMSTask).filter(
        PMSTask.id.in_(bulk_in.task_ids),
        PMSTask.deleted_at == None,
    ).all()
    if len(tasks) != len(set(bulk_in.task_ids)):
        raise HTTPException(status_code=404, detail="One or more tasks were not found")

    update_data = bulk_in.dict(exclude={"task_ids"}, exclude_unset=True)
    by_project: dict[int, list[PMSTask]] = {}
    for task in tasks:
        by_project.setdefault(task.project_id, []).append(task)
    for project_id, project_tasks in by_project.items():
        get_project_for_action(db, project_id, current_user, "manage_tasks")
        _sync_task_planning_links(db, project_id, update_data)
        if update_data.get("sprint_id"):
            sprint = db.query(PMSSprint).filter(PMSSprint.id == update_data["sprint_id"], PMSSprint.project_id == project_id).first()
            if not sprint:
                raise HTTPException(status_code=400, detail="Sprint does not belong to selected project")
            if sprint.status == "Active":
                sprint.scope_change_count = (sprint.scope_change_count or 0) + len(project_tasks)
        for task in project_tasks:
            for field, value in update_data.items():
                setattr(task, field, value)
            _record_activity(db, project_id, current_user, "bulk_updated", "task", task.id, f"Bulk updated {task.task_key}", task_id=task.id, metadata=update_data)
            db.add(task)

    db.commit()
    for task in tasks:
        db.refresh(task)
    return {"updated_count": len(tasks), "tasks": tasks}


@router.get("/tasks/{task_id}", response_model=PMSTaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific task."""
    task, _project = get_task_project_for_action(db, task_id, current_user, "browse")
    return task


@router.post("/tasks/{task_id}/dependencies", response_model=PMSTaskDependencyResponse, status_code=status.HTTP_201_CREATED)
def add_task_dependency(
    task_id: int,
    dependency_in: PMSTaskDependencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark another task as a blocker/dependency for this task."""
    task, project = get_task_project_for_action(db, task_id, current_user, "manage_tasks")
    blocker = db.query(PMSTask).filter(
        PMSTask.id == dependency_in.depends_on_task_id,
        PMSTask.project_id == project.id,
        PMSTask.deleted_at == None,
    ).first()
    if not blocker:
        raise HTTPException(status_code=404, detail="Dependency task not found in this project")
    if blocker.id == task.id:
        raise HTTPException(status_code=400, detail="A task cannot depend on itself")
    existing = db.query(PMSTaskDependency).filter(
        PMSTaskDependency.task_id == task.id,
        PMSTaskDependency.depends_on_task_id == blocker.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Dependency already exists")
    dependency = PMSTaskDependency(task_id=task.id, **dependency_in.dict())
    blocker.is_blocking = True
    _record_activity(
        db,
        project.id,
        current_user,
        "dependency_added",
        "task_dependency",
        task.id,
        f"{blocker.task_key} now blocks {task.task_key}",
        task_id=task.id,
        metadata={"depends_on_task_id": blocker.id},
    )
    db.add(blocker)
    db.add(dependency)
    db.commit()
    db.refresh(dependency)
    return dependency


@router.get("/tasks/{task_id}/dependencies", response_model=list[PMSTaskDependencyDetail])
def list_task_dependencies(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List blockers and dependent work for a task."""
    task, _project = get_task_project_for_action(db, task_id, current_user, "browse")
    dependencies = db.query(PMSTaskDependency).filter(
        or_(PMSTaskDependency.task_id == task.id, PMSTaskDependency.depends_on_task_id == task.id)
    ).all()
    task_ids = {dep.task_id for dep in dependencies} | {dep.depends_on_task_id for dep in dependencies}
    related = {item.id: item for item in db.query(PMSTask).filter(PMSTask.id.in_(task_ids)).all()} if task_ids else {}
    return [
        {
            "id": dep.id,
            "task_id": dep.task_id,
            "depends_on_task_id": dep.depends_on_task_id,
            "dependency_type": dep.dependency_type,
            "created_at": dep.created_at,
            "task_key": related.get(dep.task_id).task_key if related.get(dep.task_id) else None,
            "depends_on_task_key": related.get(dep.depends_on_task_id).task_key if related.get(dep.depends_on_task_id) else None,
            "task_title": related.get(dep.task_id).title if related.get(dep.task_id) else None,
            "depends_on_task_title": related.get(dep.depends_on_task_id).title if related.get(dep.depends_on_task_id) else None,
        }
        for dep in dependencies
    ]


@router.delete("/tasks/{task_id}/dependencies/{dependency_id}")
def remove_task_dependency(
    task_id: int,
    dependency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a blocker/dependency link."""
    task, project = get_task_project_for_action(db, task_id, current_user, "manage_tasks")
    dependency = db.query(PMSTaskDependency).filter(
        PMSTaskDependency.id == dependency_id,
        or_(PMSTaskDependency.task_id == task.id, PMSTaskDependency.depends_on_task_id == task.id),
    ).first()
    if not dependency:
        raise HTTPException(status_code=404, detail="Dependency not found")
    blocker_id = dependency.depends_on_task_id
    db.delete(dependency)
    db.flush()
    still_blocks = db.query(PMSTaskDependency).filter(PMSTaskDependency.depends_on_task_id == blocker_id).count()
    if not still_blocks:
        blocker = db.query(PMSTask).filter(PMSTask.id == blocker_id).first()
        if blocker:
            blocker.is_blocking = False
            db.add(blocker)
    _record_activity(db, project.id, current_user, "dependency_removed", "task_dependency", dependency_id, f"Removed dependency link for {task.task_key}", task_id=task.id)
    db.commit()
    return {"message": "Dependency removed"}


@router.patch("/tasks/{task_id}", response_model=PMSTaskResponse)
def update_task(
    task_id: int,
    task_in: PMSTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a task."""
    task, project = get_task_project_for_action(db, task_id, current_user, "manage_tasks")
    
    update_data = task_in.dict(exclude_unset=True)
    _sync_task_planning_links(db, project.id, update_data)
    if "sprint_id" in update_data and update_data["sprint_id"] != task.sprint_id and update_data["sprint_id"]:
        sprint = db.query(PMSSprint).filter(PMSSprint.id == update_data["sprint_id"], PMSSprint.project_id == project.id).first()
        if not sprint:
            raise HTTPException(status_code=400, detail="Sprint does not belong to selected project")
        if sprint.status == "Active":
            sprint.scope_change_count = (sprint.scope_change_count or 0) + 1
    for field, value in update_data.items():
        setattr(task, field, value)

    if task.sprint_id:
        sprint = db.query(PMSSprint).filter(PMSSprint.id == task.sprint_id).first()
        if sprint:
            _sync_sprint_rollups(db, sprint)
    _record_activity(db, project.id, current_user, "updated", "task", task.id, f"Updated task {task.task_key}", task_id=task.id, metadata=update_data)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete a task."""
    task, _project = get_task_project_for_action(db, task_id, current_user, "manage_tasks")
    
    from datetime import datetime
    task.deleted_at = datetime.utcnow()
    db.add(task)
    db.commit()
    return {"message": "Task deleted"}


# ============= KANBAN BOARD =============
@router.get("/projects/{project_id}/board", response_model=KanbanBoard)
def get_kanban_board(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get Kanban board with columns and tasks."""
    get_project_for_action(db, project_id, current_user, "browse")
    
    # Get or create default board
    board = db.query(PMSBoard).filter(
        PMSBoard.project_id == project_id
    ).first()
    
    if not board:
        # Create default board with standard columns
        board = PMSBoard(
            project_id=project_id,
            name="Default Board",
            board_type="Kanban"
        )
        db.add(board)
        db.commit()
        db.refresh(board)
        
        # Create default columns
        default_columns = [
            ("Backlog", "BACKLOG", 0),
            ("To Do", "TODO", 1),
            ("In Progress", "IN_PROGRESS", 2),
            ("In Review", "IN_REVIEW", 3),
            ("Done", "DONE", 4),
        ]
        
        for name, status_key, position in default_columns:
            col = PMSBoardColumn(
                board_id=board.id,
                name=name,
                status_key=status_key,
                position=position
            )
            db.add(col)
        db.commit()
    
    # Get columns with tasks
    columns = db.query(PMSBoardColumn).filter(
        PMSBoardColumn.board_id == board.id
    ).order_by(PMSBoardColumn.position).all()
    
    columns_data = []
    for col in columns:
        tasks = db.query(PMSTask).filter(
            PMSTask.project_id == project_id,
            PMSTask.column_id == col.id,
            PMSTask.deleted_at == None
        ).order_by(PMSTask.position).all()
        
        columns_data.append({
            "id": col.id,
            "board_id": col.board_id,
            "name": col.name,
            "status_key": col.status_key,
            "position": col.position,
            "wip_limit": col.wip_limit,
            "is_collapsed": col.is_collapsed,
            "color": col.color,
            "tasks": tasks,
            "task_count": len(tasks)
        })
    
    return {
        "id": board.id,
        "project_id": board.project_id,
        "name": board.name,
        "board_type": board.board_type,
        "created_at": board.created_at,
        "columns": columns_data
    }


@router.post("/projects/{project_id}/board/reorder")
def reorder_task(
    project_id: int,
    reorder_req: TaskReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reorder task within or between columns (Drag & Drop)."""
    get_project_for_action(db, project_id, current_user, "manage_tasks")
    
    task = db.query(PMSTask).filter(
        PMSTask.id == reorder_req.task_id,
        PMSTask.project_id == project_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update task's column and position
    task.column_id = reorder_req.column_id
    task.position = reorder_req.position
    column = db.query(PMSBoardColumn).filter(PMSBoardColumn.id == reorder_req.column_id).first()
    if column:
        status_map = {
            "BACKLOG": "Backlog",
            "TODO": "To Do",
            "IN_PROGRESS": "In Progress",
            "IN_REVIEW": "In Review",
            "DONE": "Done",
        }
        task.status = status_map.get(column.status_key, task.status)
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return {"message": "Task reordered", "task": task}


# ============= COMMENTS (COLLABORATION) =============
@router.post("/tasks/{task_id}/comments", response_model=PMSCommentResponse)
def add_comment_to_task(
    task_id: int,
    comment_in: PMSCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a comment to a task (Collaboration)."""
    task, project = get_task_project_for_action(db, task_id, current_user, "comment")
    
    comment_data = comment_in.dict()
    comment_data['author_user_id'] = current_user.id
    comment_data['task_id'] = task_id
    comment_data['project_id'] = project.id
    
    db_comment = PMSComment(**comment_data)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.get("/tasks/{task_id}/comments", response_model=list[PMSCommentResponse])
def list_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all comments on a task."""
    task, project = get_task_project_for_action(db, task_id, current_user, "browse")
    
    query = db.query(PMSComment).filter(
        PMSComment.task_id == task_id,
        PMSComment.deleted_at == None
    )
    if not can_access_project(db, project, current_user, "manage_tasks"):
        query = query.filter(PMSComment.is_internal == False)
    return query.order_by(desc(PMSComment.created_at)).all()


@router.patch("/comments/{comment_id}", response_model=PMSCommentResponse)
def update_comment(
    comment_id: int,
    comment_in: PMSCommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a comment."""
    comment = db.query(PMSComment).filter(PMSComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.author_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only edit your own comments")
    if comment.task_id:
        get_task_project_for_action(db, comment.task_id, current_user, "comment")
    
    update_data = comment_in.dict(exclude_unset=True)
    update_data['is_edited'] = True
    for field, value in update_data.items():
        setattr(comment, field, value)
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a comment."""
    comment = db.query(PMSComment).filter(PMSComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.author_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only delete your own comments")
    if comment.task_id:
        get_task_project_for_action(db, comment.task_id, current_user, "comment")
    
    from datetime import datetime
    comment.deleted_at = datetime.utcnow()
    db.add(comment)
    db.commit()
    return {"message": "Comment deleted"}


# ============= MILESTONES =============
@router.post("/projects/{project_id}/milestones", response_model=PMSMilestoneResponse)
def create_milestone(
    project_id: int,
    milestone_in: PMSMilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a milestone for a project."""
    get_project_for_action(db, project_id, current_user, "manage_tasks")
    
    db_milestone = PMSMilestone(
        project_id=project_id,
        **milestone_in.dict()
    )
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    return db_milestone


@router.get("/projects/{project_id}/milestones", response_model=list[PMSMilestoneResponse])
def list_milestones(
    project_id: int,
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all milestones for a project."""
    get_project_for_action(db, project_id, current_user, "browse")
    
    milestones = db.query(PMSMilestone).filter(
        PMSMilestone.project_id == project_id
    ).offset(skip).limit(limit).all()
    return milestones


@router.post("/milestones/{milestone_id}/submit-approval", response_model=PMSClientApprovalResponse)
def submit_milestone_approval(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a milestone for client approval."""
    milestone = db.query(PMSMilestone).filter(PMSMilestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    project = get_project_for_action(db, milestone.project_id, current_user, "manage_tasks")

    milestone.client_approval_status = "Pending"
    approval = PMSClientApproval(
        project_id=project.id,
        milestone_id=milestone.id,
        requested_by_user_id=current_user.id,
        status="Pending",
    )
    db.add(milestone)
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


@router.post("/milestones/{milestone_id}/approve", response_model=PMSMilestoneResponse)
def approve_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve a milestone from the client portal."""
    from datetime import datetime

    milestone = db.query(PMSMilestone).filter(PMSMilestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    get_project_for_action(db, milestone.project_id, current_user, "approve")
    milestone.client_approval_status = "Approved"
    milestone.client_approved_at = datetime.utcnow()
    db.query(PMSClientApproval).filter(
        PMSClientApproval.milestone_id == milestone_id,
        PMSClientApproval.status == "Pending",
    ).update({"status": "Approved", "decided_at": datetime.utcnow()})
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


@router.post("/milestones/{milestone_id}/reject", response_model=PMSMilestoneResponse)
def reject_milestone(
    milestone_id: int,
    approval_in: PMSClientApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject a milestone with a reason."""
    from datetime import datetime

    milestone = db.query(PMSMilestone).filter(PMSMilestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    get_project_for_action(db, milestone.project_id, current_user, "approve")
    if not approval_in.remarks:
        raise HTTPException(status_code=400, detail="Rejection reason is required")
    milestone.client_approval_status = "Rejected"
    milestone.client_rejected_reason = approval_in.remarks
    db.query(PMSClientApproval).filter(
        PMSClientApproval.milestone_id == milestone_id,
        PMSClientApproval.status == "Pending",
    ).update({"status": "Rejected", "remarks": approval_in.remarks, "decided_at": datetime.utcnow()})
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


# ============= SPRINTS =============
@router.post("/projects/{project_id}/sprints", response_model=PMSSprintResponse)
def create_sprint(
    project_id: int,
    sprint_in: PMSSprintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a sprint for a project."""
    get_project_for_action(db, project_id, current_user, "manage_tasks")
    sprint = PMSSprint(project_id=project_id, **sprint_in.dict())
    db.add(sprint)
    db.commit()
    db.refresh(sprint)
    return sprint


@router.get("/projects/{project_id}/sprints", response_model=list[PMSSprintResponse])
def list_sprints(
    project_id: int,
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List project sprints."""
    get_project_for_action(db, project_id, current_user, "browse")
    return db.query(PMSSprint).filter(PMSSprint.project_id == project_id).offset(skip).limit(limit).all()


@router.post("/sprints/{sprint_id}/start", response_model=PMSSprintResponse)
def start_sprint(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a sprint and capture the committed scope snapshot."""
    sprint = db.query(PMSSprint).filter(PMSSprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    get_project_for_action(db, sprint.project_id, current_user, "manage_tasks")
    if sprint.status == "Completed":
        raise HTTPException(status_code=400, detail="Completed sprints cannot be restarted")
    tasks = db.query(PMSTask).filter(PMSTask.sprint_id == sprint.id, PMSTask.deleted_at == None).all()
    committed_points = sum(_task_points(task) for task in tasks)
    sprint.status = "Active"
    sprint.started_at = datetime.utcnow()
    sprint.committed_task_count = len(tasks)
    sprint.committed_story_points = committed_points
    sprint.completed_story_points = sum(_task_points(task) for task in tasks if task.status in DONE_STATUSES)
    sprint.commitment_snapshot = json.dumps([
        {"id": task.id, "task_key": task.task_key, "title": task.title, "story_points": _task_points(task), "status": task.status}
        for task in tasks
    ], default=str)
    _record_activity(db, sprint.project_id, current_user, "started", "sprint", sprint.id, f"Started sprint {sprint.name}", sprint_id=sprint.id)
    db.add(sprint)
    db.commit()
    db.refresh(sprint)
    return sprint


@router.post("/sprints/{sprint_id}/complete", response_model=PMSSprintResponse)
def complete_sprint(
    sprint_id: int,
    complete_in: SprintCompleteRequest | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete a sprint and optionally carry unfinished work forward."""
    sprint = db.query(PMSSprint).filter(PMSSprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    get_project_for_action(db, sprint.project_id, current_user, "manage_tasks")
    carry_forward_sprint = None
    if complete_in and complete_in.carry_forward_sprint_id:
        carry_forward_sprint = db.query(PMSSprint).filter(
            PMSSprint.id == complete_in.carry_forward_sprint_id,
            PMSSprint.project_id == sprint.project_id,
        ).first()
        if not carry_forward_sprint:
            raise HTTPException(status_code=400, detail="Carry-forward sprint does not belong to this project")
    tasks = db.query(PMSTask).filter(PMSTask.sprint_id == sprint.id, PMSTask.deleted_at == None).all()
    completed = [task for task in tasks if task.status in DONE_STATUSES]
    unfinished = [task for task in tasks if task.status not in DONE_STATUSES]
    if carry_forward_sprint:
        for task in unfinished:
            task.sprint_id = carry_forward_sprint.id
            db.add(task)
        carry_forward_sprint.scope_change_count = (carry_forward_sprint.scope_change_count or 0) + len(unfinished)
        db.add(carry_forward_sprint)
    sprint.status = "Completed"
    sprint.completed_at = datetime.utcnow()
    sprint.completed_story_points = sum(_task_points(task) for task in completed)
    sprint.velocity_points = sprint.completed_story_points
    sprint.carry_forward_task_count = len(unfinished)
    sprint.completion_summary = json.dumps({
        "completed_task_count": len(completed),
        "unfinished_task_count": len(unfinished),
        "carry_forward_sprint_id": carry_forward_sprint.id if carry_forward_sprint else None,
    }, default=str)
    _record_activity(db, sprint.project_id, current_user, "completed", "sprint", sprint.id, f"Completed sprint {sprint.name}", sprint_id=sprint.id)
    db.add(sprint)
    db.commit()
    db.refresh(sprint)
    return sprint


@router.get("/sprints/{sprint_id}/burndown", response_model=SprintBurndownResponse)
def get_sprint_burndown(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a sprint burndown series from commitment and completion dates."""
    sprint = db.query(PMSSprint).filter(PMSSprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    get_project_for_action(db, sprint.project_id, current_user, "browse")
    tasks = db.query(PMSTask).filter(PMSTask.sprint_id == sprint.id, PMSTask.deleted_at == None).all()
    committed = int(sprint.committed_story_points or sum(_task_points(task) for task in tasks))
    completed = sum(_task_points(task) for task in tasks if task.status in DONE_STATUSES)
    start = sprint.start_date
    end = sprint.end_date
    days = max((end - start).days, 1)
    points = []
    for offset in range(days + 1):
        day = start + timedelta(days=offset)
        ideal = max(committed - (committed * offset / days), 0)
        actual_completed = completed if day >= date.today() or sprint.status == "Completed" else 0
        points.append({
            "date": day,
            "ideal_remaining_points": ideal,
            "actual_remaining_points": max(committed - actual_completed, 0),
            "completed_points": actual_completed,
        })
    return {
        "sprint_id": sprint.id,
        "committed_story_points": committed,
        "completed_story_points": completed,
        "remaining_story_points": max(committed - completed, 0),
        "points": points,
    }


@router.get("/projects/{project_id}/velocity", response_model=ProjectVelocityResponse)
def get_project_velocity(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return completed sprint velocity history for a project."""
    get_project_for_action(db, project_id, current_user, "browse")
    sprints = db.query(PMSSprint).filter(
        PMSSprint.project_id == project_id,
        PMSSprint.status == "Completed",
    ).order_by(PMSSprint.end_date).all()
    items = [
        {"id": sprint.id, "name": sprint.name, "end_date": sprint.end_date, "velocity_points": int(sprint.velocity_points or sprint.completed_story_points or 0)}
        for sprint in sprints
    ]
    average = sum(item["velocity_points"] for item in items) / len(items) if items else 0
    return {"project_id": project_id, "average_velocity_points": average, "sprints": items}


# ============= FILES =============
@router.post("/files", response_model=PMSFileAssetResponse)
def create_file_metadata(
    file_in: PMSFileAssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create file metadata. Actual binary upload can be plugged in later."""
    if file_in.project_id:
        get_project_for_action(db, file_in.project_id, current_user, "upload")
    if file_in.task_id:
        task, _project = get_task_project_for_action(db, file_in.task_id, current_user, "upload")
        if file_in.project_id and task.project_id != file_in.project_id:
            raise HTTPException(status_code=400, detail="Task does not belong to selected project")
    file_asset = PMSFileAsset(
        **file_in.dict(exclude={"uploaded_by_user_id"}),
        uploaded_by_user_id=current_user.id,
    )
    db.add(file_asset)
    db.commit()
    db.refresh(file_asset)
    return file_asset


@router.get("/files", response_model=list[PMSFileAssetResponse])
def list_files(
    project_id: int = Query(None),
    task_id: int = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List accessible file metadata."""
    accessible_project_ids = accessible_project_query(db, current_user).with_entities(PMSProject.id)
    query = db.query(PMSFileAsset).filter(
        PMSFileAsset.deleted_at == None,
        PMSFileAsset.project_id.in_(accessible_project_ids),
    )
    if project_id:
        query = query.filter(PMSFileAsset.project_id == project_id)
    if task_id:
        query = query.filter(PMSFileAsset.task_id == task_id)
    return query.order_by(desc(PMSFileAsset.created_at)).offset(skip).limit(limit).all()


@router.patch("/files/{file_id}", response_model=PMSFileAssetResponse)
def update_file_metadata(
    file_id: int,
    file_in: PMSFileAssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update file metadata."""
    file_asset = db.query(PMSFileAsset).filter(PMSFileAsset.id == file_id).first()
    if not file_asset:
        raise HTTPException(status_code=404, detail="File not found")
    if file_asset.project_id:
        get_project_for_action(db, file_asset.project_id, current_user, "upload")
    for field, value in file_in.dict(exclude_unset=True).items():
        setattr(file_asset, field, value)
    db.add(file_asset)
    db.commit()
    db.refresh(file_asset)
    return file_asset


# ============= TIME TRACKING =============
@router.post("/time-logs", response_model=PMSTimeLogResponse)
def create_time_log(
    timelog_in: PMSTimeLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a time log entry."""
    # Verify project exists
    get_project_for_action(db, timelog_in.project_id, current_user, "log_time")
    if timelog_in.task_id:
        task, _project = get_task_project_for_action(db, timelog_in.task_id, current_user, "log_time")
        if task.project_id != timelog_in.project_id:
            raise HTTPException(status_code=400, detail="Task does not belong to selected project")
    
    db_timelog = PMSTimeLog(user_id=current_user.id, **timelog_in.dict())
    db.add(db_timelog)
    db.commit()
    db.refresh(db_timelog)
    return db_timelog


@router.get("/time-logs", response_model=list[PMSTimeLogResponse])
def list_time_logs(
    skip: int = Query(0),
    limit: int = Query(100),
    project_id: int = Query(None),
    user_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List time logs."""
    accessible_project_ids = accessible_project_query(db, current_user).with_entities(PMSProject.id)
    query = db.query(PMSTimeLog).filter(PMSTimeLog.project_id.in_(accessible_project_ids))
    
    if project_id:
        # Verify project access
        get_project_for_action(db, project_id, current_user, "browse")
        query = query.filter(PMSTimeLog.project_id == project_id)
    
    if user_id:
        query = query.filter(PMSTimeLog.user_id == user_id)
    
    timelogs = query.offset(skip).limit(limit).all()
    return timelogs


# ============= SAVED FILTERS, ACTIVITY, REPORTS =============
@router.post("/projects/{project_id}/saved-filters", response_model=PMSSavedFilterResponse, status_code=status.HTTP_201_CREATED)
def create_saved_filter(
    project_id: int,
    filter_in: PMSSavedFilterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a project board/backlog/report filter."""
    get_project_for_action(db, project_id, current_user, "browse")
    saved_filter = PMSSavedFilter(project_id=project_id, user_id=current_user.id, **filter_in.dict())
    db.add(saved_filter)
    _record_activity(db, project_id, current_user, "created", "saved_filter", None, f"Saved filter {filter_in.name}")
    db.commit()
    db.refresh(saved_filter)
    return saved_filter


@router.get("/projects/{project_id}/saved-filters", response_model=list[PMSSavedFilterResponse])
def list_saved_filters(
    project_id: int,
    view_type: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user-owned and shared saved filters for a project."""
    get_project_for_action(db, project_id, current_user, "browse")
    query = db.query(PMSSavedFilter).filter(
        PMSSavedFilter.project_id == project_id,
        or_(PMSSavedFilter.user_id == current_user.id, PMSSavedFilter.is_shared == True),
    )
    if view_type:
        query = query.filter(PMSSavedFilter.view_type == view_type)
    return query.order_by(PMSSavedFilter.is_shared.desc(), PMSSavedFilter.name).all()


@router.patch("/saved-filters/{filter_id}", response_model=PMSSavedFilterResponse)
def update_saved_filter(
    filter_id: int,
    filter_in: PMSSavedFilterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a saved filter."""
    saved_filter = db.query(PMSSavedFilter).filter(PMSSavedFilter.id == filter_id).first()
    if not saved_filter:
        raise HTTPException(status_code=404, detail="Saved filter not found")
    get_project_for_action(db, saved_filter.project_id, current_user, "browse")
    if saved_filter.user_id != current_user.id and not can_access_project(db, get_project_for_action(db, saved_filter.project_id, current_user, "browse"), current_user, "manage_tasks"):
        raise HTTPException(status_code=403, detail="Can only edit your own filters")
    for field, value in filter_in.dict(exclude_unset=True).items():
        setattr(saved_filter, field, value)
    db.add(saved_filter)
    db.commit()
    db.refresh(saved_filter)
    return saved_filter


@router.delete("/saved-filters/{filter_id}")
def delete_saved_filter(
    filter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a saved filter."""
    saved_filter = db.query(PMSSavedFilter).filter(PMSSavedFilter.id == filter_id).first()
    if not saved_filter:
        raise HTTPException(status_code=404, detail="Saved filter not found")
    get_project_for_action(db, saved_filter.project_id, current_user, "browse")
    if saved_filter.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only delete your own filters")
    db.delete(saved_filter)
    db.commit()
    return {"message": "Saved filter deleted"}


@router.get("/projects/{project_id}/activity", response_model=list[PMSActivityResponse])
def list_project_activity(
    project_id: int,
    task_id: int = Query(None),
    limit: int = Query(50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return recent activity for a project or task."""
    get_project_for_action(db, project_id, current_user, "browse")
    query = db.query(PMSActivity).filter(PMSActivity.project_id == project_id)
    if task_id:
        query = query.filter(PMSActivity.task_id == task_id)
    return query.order_by(desc(PMSActivity.created_at)).limit(limit).all()


@router.get("/projects/{project_id}/workload", response_model=WorkloadResponse)
def get_project_workload(
    project_id: int,
    group_by: str = Query("user"),
    sprint_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return capacity/workload grouped by user or sprint."""
    get_project_for_action(db, project_id, current_user, "browse")
    query = db.query(PMSTask).filter(PMSTask.project_id == project_id, PMSTask.deleted_at == None, PMSTask.status.notin_(DONE_STATUSES))
    if sprint_id:
        query = query.filter(PMSTask.sprint_id == sprint_id)
    tasks = query.all()
    today = date.today()
    grouped: dict[int | None, dict] = {}
    key_field = "sprint_id" if group_by == "sprint" else "assignee_user_id"
    for task in tasks:
        key = getattr(task, key_field)
        item = grouped.setdefault(key, {
            "user_id": task.assignee_user_id if group_by != "sprint" else None,
            "sprint_id": task.sprint_id if group_by == "sprint" else None,
            "task_count": 0,
            "story_points": 0,
            "estimated_hours": 0.0,
            "overdue_tasks": 0,
            "capacity_hours": None,
            "load_percent": None,
        })
        item["task_count"] += 1
        item["story_points"] += _task_points(task)
        item["estimated_hours"] += float(task.estimated_hours or task.remaining_estimate_hours or task.original_estimate_hours or 0)
        if task.due_date and task.due_date < today:
            item["overdue_tasks"] += 1
    if group_by == "sprint":
        sprints = {sprint.id: sprint for sprint in db.query(PMSSprint).filter(PMSSprint.project_id == project_id).all()}
        for item in grouped.values():
            sprint = sprints.get(item["sprint_id"])
            if sprint and sprint.capacity_hours:
                item["capacity_hours"] = float(sprint.capacity_hours)
                item["load_percent"] = round((item["estimated_hours"] / item["capacity_hours"]) * 100, 1) if item["capacity_hours"] else None
    return {"project_id": project_id, "group_by": group_by, "items": list(grouped.values())}


# ============= DASHBOARD =============
@router.get("/dashboard/{project_id}")
def get_project_dashboard(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project dashboard metrics."""
    project = get_project_for_action(db, project_id, current_user, "browse")
    
    # Calculate metrics
    total_tasks = db.query(PMSTask).filter(
        PMSTask.project_id == project_id,
        PMSTask.deleted_at == None
    ).count()
    
    completed_tasks = db.query(PMSTask).filter(
        PMSTask.project_id == project_id,
        PMSTask.status == "Done",
        PMSTask.deleted_at == None
    ).count()
    
    overdue_tasks = db.query(PMSTask).filter(
        PMSTask.project_id == project_id,
        PMSTask.status != "Done",
        PMSTask.due_date < __import__('datetime').date.today(),
        PMSTask.deleted_at == None
    ).count()
    
    metrics = {
        "total_projects": 1,
        "active_projects": 1 if project.status == "Active" else 0,
        "completed_projects": 1 if project.status == "Completed" else 0,
        "overdue_projects": 1 if project.due_date and project.due_date < __import__('datetime').date.today() else 0,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "pending_approvals": db.query(PMSClientApproval).filter(
            PMSClientApproval.project_id == project_id,
            PMSClientApproval.status == "Pending"
        ).count(),
        "team_utilization": 0.0,
        "hours_logged_this_week": 0,
        "upcoming_milestones": db.query(PMSMilestone).filter(
            PMSMilestone.project_id == project_id,
            PMSMilestone.status != "Completed"
        ).count(),
        "recent_activities": 0,
    }
    
    return {
        "project": project,
        "metrics": metrics
    }
