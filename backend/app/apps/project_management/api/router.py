"""Project Management (KaryaFlow) API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.apps.project_management.models import (
    PMSClient, PMSProject, PMSProjectMember, PMSTask, PMSBoard, PMSBoardColumn,
    PMSMilestone, PMSSprint, PMSComment, PMSTimeLog, PMSFileAsset, PMSTaskDependency,
    PMSChecklistItem, PMSTag, PMSTaskTag, PMSClientApproval
)
from app.apps.project_management.schemas import (
    PMSProjectCreate, PMSProjectUpdate, PMSProjectResponse,
    PMSTaskCreate, PMSTaskUpdate, PMSTaskResponse,
    PMSClientCreate, PMSClientUpdate, PMSClientResponse,
    PMSMilestoneCreate, PMSMilestoneUpdate, PMSMilestoneResponse,
    PMSBoardCreate, PMSBoardResponse,
    PMSCommentCreate, PMSCommentUpdate, PMSCommentResponse,
    PMSTimeLogCreate, PMSTimeLogUpdate, PMSTimeLogResponse,
    PMSSprintCreate, PMSSprintUpdate, PMSSprintResponse,
    PMSFileAssetCreate, PMSFileAssetUpdate, PMSFileAssetResponse,
    PMSClientApprovalCreate, PMSClientApprovalUpdate, PMSClientApprovalResponse,
    KanbanBoard, TaskReorderRequest, ProjectMetrics, DashboardResponse,
)

router = APIRouter(prefix="/project-management", tags=["Project Management"])


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
            "boards",
            "board-columns",
            "tasks",
            "dependencies",
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
    db_client = PMSClient(
        organization_id=current_user.organization_id,
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
    clients = db.query(PMSClient).filter(
        PMSClient.organization_id == current_user.organization_id,
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
    client = db.query(PMSClient).filter(
        PMSClient.id == client_id,
        PMSClient.organization_id == current_user.organization_id
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
    client = db.query(PMSClient).filter(
        PMSClient.id == client_id,
        PMSClient.organization_id == current_user.organization_id
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
    client = db.query(PMSClient).filter(
        PMSClient.id == client_id,
        PMSClient.organization_id == current_user.organization_id
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
    # Check unique constraint on project_key
    existing = db.query(PMSProject).filter(
        PMSProject.organization_id == current_user.organization_id,
        PMSProject.project_key == project_in.project_key.upper()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Project key already exists")
    
    db_project = PMSProject(
        organization_id=current_user.organization_id,
        **project_in.dict()
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
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
    query = db.query(PMSProject).filter(
        PMSProject.organization_id == current_user.organization_id,
        PMSProject.deleted_at == None
    )
    
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
    project = db.query(PMSProject).filter(
        PMSProject.id == project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/projects/{project_id}", response_model=PMSProjectResponse)
def update_project(
    project_id: int,
    project_in: PMSProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a project."""
    project = db.query(PMSProject).filter(
        PMSProject.id == project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
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
    project = db.query(PMSProject).filter(
        PMSProject.id == project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    from datetime import datetime
    project.deleted_at = datetime.utcnow()
    db.add(project)
    db.commit()
    return {"message": "Project deleted"}


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
    project = db.query(PMSProject).filter(
        PMSProject.id == project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check unique constraint on task_key
    existing = db.query(PMSTask).filter(
        PMSTask.project_id == project_id,
        PMSTask.task_key == task_in.task_key.upper()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Task key already exists in this project")
    
    task_data = task_in.dict()
    task_data['project_id'] = project_id
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
    db_task = PMSTask(**task_data)
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("/projects/{project_id}/tasks", response_model=list[PMSTaskResponse])
def list_tasks(
    project_id: int,
    skip: int = Query(0),
    limit: int = Query(100),
    status: str = Query(None),
    assignee_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all tasks in a project."""
    # Verify project exists
    project = db.query(PMSProject).filter(
        PMSProject.id == project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    query = db.query(PMSTask).filter(
        PMSTask.project_id == project_id,
        PMSTask.deleted_at == None
    )
    
    if status:
        query = query.filter(PMSTask.status == status)
    if assignee_id:
        query = query.filter(PMSTask.assignee_user_id == assignee_id)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.get("/tasks/{task_id}", response_model=PMSTaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific task."""
    task = db.query(PMSTask).filter(PMSTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify user has access to this project
    project = db.query(PMSProject).filter(
        PMSProject.id == task.project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return task


@router.patch("/tasks/{task_id}", response_model=PMSTaskResponse)
def update_task(
    task_id: int,
    task_in: PMSTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a task."""
    task = db.query(PMSTask).filter(PMSTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify user has access
    project = db.query(PMSProject).filter(
        PMSProject.id == task.project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = task_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
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
    task = db.query(PMSTask).filter(PMSTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project = db.query(PMSProject).filter(
        PMSProject.id == task.project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")
    
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
    project = db.query(PMSProject).filter(
        PMSProject.id == project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
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
    project = db.query(PMSProject).filter(
        PMSProject.id == project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
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
    task = db.query(PMSTask).filter(PMSTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project = db.query(PMSProject).filter(
        PMSProject.id == task.project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")
    
    comment_data = comment_in.dict()
    comment_data['author_user_id'] = current_user.id
    comment_data['task_id'] = task_id
    
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
    task = db.query(PMSTask).filter(PMSTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    project = db.query(PMSProject).filter(
        PMSProject.id == task.project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")
    
    comments = db.query(PMSComment).filter(
        PMSComment.task_id == task_id,
        PMSComment.deleted_at == None
    ).order_by(desc(PMSComment.created_at)).all()
    return comments


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
    project = db.query(PMSProject).filter(
        PMSProject.id == project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
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
    project = db.query(PMSProject).filter(
        PMSProject.id == project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
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
    project = db.query(PMSProject).filter(
        PMSProject.id == milestone.project_id,
        PMSProject.organization_id == current_user.organization_id,
    ).first()
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")

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
    project = db.query(PMSProject).filter(
        PMSProject.id == milestone.project_id,
        PMSProject.organization_id == current_user.organization_id,
    ).first()
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")
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
    project = db.query(PMSProject).filter(
        PMSProject.id == milestone.project_id,
        PMSProject.organization_id == current_user.organization_id,
    ).first()
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")
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
    project = db.query(PMSProject).filter(
        PMSProject.id == project_id,
        PMSProject.organization_id == current_user.organization_id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
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
    project = db.query(PMSProject).filter(
        PMSProject.id == project_id,
        PMSProject.organization_id == current_user.organization_id,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db.query(PMSSprint).filter(PMSSprint.project_id == project_id).offset(skip).limit(limit).all()


# ============= FILES =============
@router.post("/files", response_model=PMSFileAssetResponse)
def create_file_metadata(
    file_in: PMSFileAssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create file metadata. Actual binary upload can be plugged in later."""
    if file_in.project_id:
        project = db.query(PMSProject).filter(
            PMSProject.id == file_in.project_id,
            PMSProject.organization_id == current_user.organization_id,
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="Access denied")
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
    accessible_project_ids = db.query(PMSProject.id).filter(
        PMSProject.organization_id == current_user.organization_id,
        PMSProject.deleted_at == None,
    )
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
    project = db.query(PMSProject).filter(
        PMSProject.id == file_asset.project_id,
        PMSProject.organization_id == current_user.organization_id,
    ).first()
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")
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
    project = db.query(PMSProject).filter(
        PMSProject.id == timelog_in.project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
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
    accessible_project_ids = db.query(PMSProject.id).filter(
        PMSProject.organization_id == current_user.organization_id,
        PMSProject.deleted_at == None,
    )
    query = db.query(PMSTimeLog).filter(PMSTimeLog.project_id.in_(accessible_project_ids))
    
    if project_id:
        # Verify project access
        project = db.query(PMSProject).filter(
            PMSProject.id == project_id,
            PMSProject.organization_id == current_user.organization_id
        ).first()
        if not project:
            raise HTTPException(status_code=403, detail="Access denied")
        query = query.filter(PMSTimeLog.project_id == project_id)
    
    if user_id:
        query = query.filter(PMSTimeLog.user_id == user_id)
    
    timelogs = query.offset(skip).limit(limit).all()
    return timelogs


# ============= DASHBOARD =============
@router.get("/dashboard/{project_id}")
def get_project_dashboard(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get project dashboard metrics."""
    project = db.query(PMSProject).filter(
        PMSProject.id == project_id,
        PMSProject.organization_id == current_user.organization_id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
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
