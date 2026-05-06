"""Pydantic schemas for Project Management (KaryaFlow) module."""
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field, validator


# ============= CLIENT SCHEMAS =============
class PMSClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=180)
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None


class PMSClientCreate(PMSClientBase):
    pass


class PMSClientUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None


class PMSClientResponse(PMSClientBase):
    id: int
    organization_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= PROJECT SCHEMAS =============
class PMSProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=180)
    project_key: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None
    client_id: Optional[int] = None
    manager_user_id: Optional[int] = None
    status: str = "Draft"
    priority: str = "Medium"
    health: str = "Good"
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    budget_amount: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    progress_percent: int = 0
    is_client_visible: bool = False
    is_archived: bool = False

    @validator("project_key")
    def project_key_uppercase(cls, v):
        return v.upper()


class PMSProjectCreate(PMSProjectBase):
    pass


class PMSProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    client_id: Optional[int] = None
    manager_user_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    health: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    budget_amount: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    progress_percent: Optional[int] = None
    is_client_visible: Optional[bool] = None
    is_archived: Optional[bool] = None


class PMSProjectResponse(PMSProjectBase):
    id: int
    organization_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= PROJECT MEMBER SCHEMAS =============
class PMSProjectMemberBase(BaseModel):
    user_id: int
    role: str = "Member"


class PMSProjectMemberCreate(PMSProjectMemberBase):
    pass


class PMSProjectMemberUpdate(BaseModel):
    role: Optional[str] = None


class PMSProjectMemberResponse(PMSProjectMemberBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============= BOARD & COLUMN SCHEMAS =============
class PMSBoardColumnBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    status_key: str = Field(..., min_length=1, max_length=60)
    position: int = 0
    wip_limit: Optional[int] = None
    is_collapsed: bool = False
    color: Optional[str] = None


class PMSBoardColumnCreate(PMSBoardColumnBase):
    pass


class PMSBoardColumnUpdate(BaseModel):
    name: Optional[str] = None
    status_key: Optional[str] = None
    position: Optional[int] = None
    wip_limit: Optional[int] = None
    is_collapsed: Optional[bool] = None
    color: Optional[str] = None


class PMSBoardColumnResponse(PMSBoardColumnBase):
    id: int
    board_id: int

    class Config:
        from_attributes = True


class PMSBoardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=140)
    board_type: str = "Kanban"


class PMSBoardCreate(PMSBoardBase):
    columns: Optional[List[PMSBoardColumnCreate]] = []


class PMSBoardUpdate(BaseModel):
    name: Optional[str] = None
    board_type: Optional[str] = None


class PMSBoardResponse(PMSBoardBase):
    id: int
    project_id: int
    created_at: datetime
    columns: Optional[List[PMSBoardColumnResponse]] = []

    class Config:
        from_attributes = True


# ============= SPRINT SCHEMAS =============
class PMSSprintBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=160)
    goal: Optional[str] = None
    status: str = "Planned"
    start_date: date
    end_date: date
    capacity_hours: Optional[Decimal] = None
    velocity_points: Optional[int] = None


class PMSSprintCreate(PMSSprintBase):
    pass


class PMSSprintUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    capacity_hours: Optional[Decimal] = None
    velocity_points: Optional[int] = None


class PMSSprintResponse(PMSSprintBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= MILESTONE SCHEMAS =============
class PMSMilestoneBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=180)
    description: Optional[str] = None
    status: str = "Not Started"
    owner_user_id: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    progress_percent: int = 0
    client_approval_status: str = "Not Required"


class PMSMilestoneCreate(PMSMilestoneBase):
    pass


class PMSMilestoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    owner_user_id: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    progress_percent: Optional[int] = None
    client_approval_status: Optional[str] = None


class PMSMilestoneResponse(PMSMilestoneBase):
    id: int
    project_id: int
    completed_at: Optional[datetime] = None
    client_approved_at: Optional[datetime] = None
    client_rejected_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= TAG SCHEMAS =============
class PMSTagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = None


class PMSTagCreate(PMSTagBase):
    pass


class PMSTagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class PMSTagResponse(PMSTagBase):
    id: int
    organization_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============= TASK SCHEMAS =============
class PMSChecklistItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=220)
    is_completed: bool = False
    position: int = 0


class PMSChecklistItemCreate(PMSChecklistItemBase):
    pass


class PMSChecklistItemUpdate(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None
    position: Optional[int] = None


class PMSChecklistItemResponse(PMSChecklistItemBase):
    id: int
    task_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PMSTaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=220)
    description: Optional[str] = None
    task_key: str = Field(..., min_length=1, max_length=30)
    status: str = "To Do"
    priority: str = "Medium"
    assignee_user_id: Optional[int] = None
    reporter_user_id: Optional[int] = None
    milestone_id: Optional[int] = None
    sprint_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    story_points: Optional[int] = None
    position: int = 0
    is_client_visible: bool = False
    is_blocking: bool = False


class PMSTaskCreate(PMSTaskBase):
    column_id: Optional[int] = None


class PMSTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_user_id: Optional[int] = None
    reporter_user_id: Optional[int] = None
    column_id: Optional[int] = None
    milestone_id: Optional[int] = None
    sprint_id: Optional[int] = None
    parent_task_id: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    story_points: Optional[int] = None
    position: Optional[int] = None
    is_client_visible: Optional[bool] = None
    is_blocking: Optional[bool] = None


class PMSTaskResponse(PMSTaskBase):
    id: int
    project_id: int
    board_id: Optional[int] = None
    column_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= TASK DEPENDENCY SCHEMAS =============
class PMSTaskDependencyBase(BaseModel):
    depends_on_task_id: int
    dependency_type: str = "Finish To Start"


class PMSTaskDependencyCreate(PMSTaskDependencyBase):
    pass


class PMSTaskDependencyResponse(PMSTaskDependencyBase):
    id: int
    task_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============= FILE ASSET SCHEMAS =============
class PMSFileAssetBase(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=240)
    original_name: str = Field(..., min_length=1, max_length=240)
    mime_type: Optional[str] = None
    size_bytes: int = 0
    storage_path: str = Field(..., min_length=1, max_length=500)
    visibility: str = "Internal"


class PMSFileAssetCreate(PMSFileAssetBase):
    uploaded_by_user_id: Optional[int] = None
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    milestone_id: Optional[int] = None


class PMSFileAssetUpdate(BaseModel):
    visibility: Optional[str] = None
    file_name: Optional[str] = None


class PMSFileAssetResponse(PMSFileAssetBase):
    id: int
    uploaded_by_user_id: Optional[int] = None
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    milestone_id: Optional[int] = None
    version_number: int = 1
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= COMMENT SCHEMAS =============
class PMSCommentBase(BaseModel):
    body: str = Field(..., min_length=1)
    is_internal: bool = True


class PMSCommentCreate(PMSCommentBase):
    author_user_id: Optional[int] = None
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    milestone_id: Optional[int] = None
    parent_comment_id: Optional[int] = None


class PMSCommentUpdate(BaseModel):
    body: Optional[str] = None
    is_internal: Optional[bool] = None


class PMSCommentResponse(PMSCommentBase):
    id: int
    author_user_id: Optional[int] = None
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    milestone_id: Optional[int] = None
    parent_comment_id: Optional[int] = None
    is_edited: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= TIME LOG SCHEMAS =============
class PMSTimeLogBase(BaseModel):
    log_date: date
    duration_minutes: int = Field(..., gt=0)
    description: Optional[str] = None
    is_billable: bool = False
    approval_status: str = "Pending"
    task_id: Optional[int] = None


class PMSTimeLogCreate(PMSTimeLogBase):
    project_id: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class PMSTimeLogUpdate(BaseModel):
    duration_minutes: Optional[int] = None
    description: Optional[str] = None
    is_billable: Optional[bool] = None
    approval_status: Optional[str] = None
    task_id: Optional[int] = None


class PMSTimeLogResponse(PMSTimeLogBase):
    id: int
    user_id: int
    project_id: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    approved_by_user_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= CLIENT APPROVAL SCHEMAS =============
class PMSClientApprovalBase(BaseModel):
    status: str = "Pending"
    remarks: Optional[str] = None


class PMSClientApprovalCreate(BaseModel):
    project_id: int
    milestone_id: Optional[int] = None
    client_user_id: Optional[int] = None
    requested_by_user_id: Optional[int] = None


class PMSClientApprovalUpdate(BaseModel):
    status: Optional[str] = None
    remarks: Optional[str] = None


class PMSClientApprovalResponse(PMSClientApprovalBase):
    id: int
    project_id: int
    milestone_id: Optional[int] = None
    requested_by_user_id: Optional[int] = None
    client_user_id: Optional[int] = None
    decided_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============= KANBAN BOARD SCHEMAS =============
class KanbanTaskCard(PMSTaskResponse):
    """Task card for Kanban board display."""
    assignee_name: Optional[str] = None
    tags: Optional[List[PMSTagResponse]] = []


class KanbanColumn(PMSBoardColumnResponse):
    """Kanban column with tasks."""
    tasks: Optional[List[KanbanTaskCard]] = []
    task_count: int = 0


class KanbanBoard(PMSBoardResponse):
    """Full Kanban board with columns and tasks."""
    columns: Optional[List[KanbanColumn]] = []


class TaskReorderRequest(BaseModel):
    """Request to reorder tasks within or between columns."""
    task_id: int
    column_id: int
    position: int


# ============= DASHBOARD SCHEMAS =============
class ProjectMetrics(BaseModel):
    """Project overview metrics."""
    total_projects: int = 0
    active_projects: int = 0
    completed_projects: int = 0
    overdue_projects: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    overdue_tasks: int = 0
    pending_approvals: int = 0
    team_utilization: float = 0.0
    hours_logged_this_week: Decimal = Decimal(0)
    upcoming_milestones: int = 0
    recent_activities: int = 0


class DashboardResponse(BaseModel):
    """Dashboard data response."""
    metrics: ProjectMetrics
    recent_projects: Optional[List[PMSProjectResponse]] = []
    recent_tasks: Optional[List[PMSTaskResponse]] = []
    recent_comments: Optional[List[PMSCommentResponse]] = []
