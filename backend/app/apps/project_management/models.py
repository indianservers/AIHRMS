from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.sql import func

from app.db.base_class import Base


class PMSClient(Base):
    __tablename__ = "pms_clients"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    name = Column(String(180), nullable=False, index=True)
    company_name = Column(String(180))
    email = Column(String(150), index=True)
    phone = Column(String(40))
    website = Column(String(200))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class PMSProject(Base):
    __tablename__ = "pms_projects"
    __table_args__ = (UniqueConstraint("organization_id", "project_key", name="uq_pms_project_org_key"),)

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    client_id = Column(Integer, ForeignKey("pms_clients.id", ondelete="SET NULL"), nullable=True, index=True)
    manager_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(180), nullable=False, index=True)
    project_key = Column(String(20), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(40), default="Draft", index=True)
    priority = Column(String(30), default="Medium", index=True)
    health = Column(String(30), default="Good", index=True)
    start_date = Column(Date)
    due_date = Column(Date, index=True)
    completed_at = Column(DateTime(timezone=True))
    budget_amount = Column(Numeric(12, 2))
    actual_cost = Column(Numeric(12, 2))
    progress_percent = Column(Integer, default=0)
    is_client_visible = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class PMSProjectMember(Base):
    __tablename__ = "pms_project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_pms_project_member"),)

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(40), default="Member", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PMSEpic(Base):
    __tablename__ = "pms_epics"
    __table_args__ = (UniqueConstraint("project_id", "epic_key", name="uq_pms_epic_project_key"),)

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    epic_key = Column(String(60), nullable=False, index=True)
    name = Column(String(180), nullable=False)
    description = Column(Text)
    status = Column(String(40), default="Planned", index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    color = Column(String(30))
    start_date = Column(Date)
    target_date = Column(Date, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class PMSComponent(Base):
    __tablename__ = "pms_components"
    __table_args__ = (UniqueConstraint("project_id", "name", name="uq_pms_component_project_name"),)

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False, index=True)
    description = Column(Text)
    lead_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    default_assignee_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PMSRelease(Base):
    __tablename__ = "pms_releases"
    __table_args__ = (UniqueConstraint("project_id", "name", name="uq_pms_release_project_name"),)

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(40), default="Planning", index=True)
    release_date = Column(Date, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    readiness_percent = Column(Integer, default=0)
    launch_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class PMSBoard(Base):
    __tablename__ = "pms_boards"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(140), nullable=False)
    board_type = Column(String(40), default="Kanban", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PMSBoardColumn(Base):
    __tablename__ = "pms_board_columns"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("pms_boards.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    status_key = Column(String(60), nullable=False, index=True)
    position = Column(Integer, default=0)
    wip_limit = Column(Integer)
    is_collapsed = Column(Boolean, default=False)
    color = Column(String(30))


class PMSSprint(Base):
    __tablename__ = "pms_sprints"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(160), nullable=False)
    goal = Column(Text)
    status = Column(String(30), default="Planned", index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    capacity_hours = Column(Numeric(8, 2))
    velocity_points = Column(Integer)
    committed_task_count = Column(Integer, default=0)
    committed_story_points = Column(Integer, default=0)
    completed_story_points = Column(Integer, default=0)
    scope_change_count = Column(Integer, default=0)
    carry_forward_task_count = Column(Integer, default=0)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    commitment_snapshot = Column(Text)
    completion_summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PMSMilestone(Base):
    __tablename__ = "pms_milestones"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(180), nullable=False)
    description = Column(Text)
    status = Column(String(40), default="Not Started", index=True)
    start_date = Column(Date)
    due_date = Column(Date, index=True)
    completed_at = Column(DateTime(timezone=True))
    progress_percent = Column(Integer, default=0)
    client_approval_status = Column(String(40), default="Not Required", index=True)
    client_approved_at = Column(DateTime(timezone=True))
    client_rejected_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PMSTask(Base):
    __tablename__ = "pms_tasks"
    __table_args__ = (UniqueConstraint("project_id", "task_key", name="uq_pms_task_project_key"),)

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    board_id = Column(Integer, ForeignKey("pms_boards.id", ondelete="SET NULL"), nullable=True, index=True)
    column_id = Column(Integer, ForeignKey("pms_board_columns.id", ondelete="SET NULL"), nullable=True, index=True)
    milestone_id = Column(Integer, ForeignKey("pms_milestones.id", ondelete="SET NULL"), nullable=True, index=True)
    sprint_id = Column(Integer, ForeignKey("pms_sprints.id", ondelete="SET NULL"), nullable=True, index=True)
    epic_id = Column(Integer, ForeignKey("pms_epics.id", ondelete="SET NULL"), nullable=True, index=True)
    component_id = Column(Integer, ForeignKey("pms_components.id", ondelete="SET NULL"), nullable=True, index=True)
    release_id = Column(Integer, ForeignKey("pms_releases.id", ondelete="SET NULL"), nullable=True, index=True)
    parent_task_id = Column(Integer, ForeignKey("pms_tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    assignee_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reporter_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(220), nullable=False)
    description = Column(Text)
    task_key = Column(String(30), nullable=False, index=True)
    work_type = Column(String(40), default="Task", index=True)
    epic_key = Column(String(60), index=True)
    initiative = Column(String(160))
    component = Column(String(120), index=True)
    severity = Column(String(20), index=True)
    environment = Column(String(80))
    affected_version = Column(String(80))
    fix_version = Column(String(80), index=True)
    release_name = Column(String(120), index=True)
    status = Column(String(50), default="To Do", index=True)
    priority = Column(String(30), default="Medium", index=True)
    start_date = Column(Date)
    due_date = Column(Date, index=True)
    completed_at = Column(DateTime(timezone=True))
    estimated_hours = Column(Numeric(8, 2))
    actual_hours = Column(Numeric(8, 2))
    original_estimate_hours = Column(Numeric(8, 2))
    remaining_estimate_hours = Column(Numeric(8, 2))
    story_points = Column(Integer)
    rank = Column(Integer, index=True)
    security_level = Column(String(40), default="Internal", index=True)
    development_branch = Column(String(200))
    development_commits = Column(Integer, default=0)
    development_prs = Column(Integer, default=0)
    development_deployments = Column(Integer, default=0)
    development_build = Column(String(30), default="Pending", index=True)
    position = Column(Integer, default=0)
    is_client_visible = Column(Boolean, default=False)
    is_blocking = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class PMSTaskDependency(Base):
    __tablename__ = "pms_task_dependencies"
    __table_args__ = (UniqueConstraint("task_id", "depends_on_task_id", name="uq_pms_task_dependency"),)

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("pms_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    depends_on_task_id = Column(Integer, ForeignKey("pms_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    dependency_type = Column(String(40), default="Finish To Start")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PMSSavedFilter(Base):
    __tablename__ = "pms_saved_filters"
    __table_args__ = (UniqueConstraint("project_id", "user_id", "name", name="uq_pms_saved_filter_owner_name"),)

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(140), nullable=False)
    view_type = Column(String(40), default="board", index=True)
    query = Column(Text, nullable=False)
    is_shared = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PMSActivity(Base):
    __tablename__ = "pms_activities"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("pms_tasks.id", ondelete="CASCADE"), nullable=True, index=True)
    sprint_id = Column(Integer, ForeignKey("pms_sprints.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(80), nullable=False, index=True)
    entity_type = Column(String(40), nullable=False, index=True)
    entity_id = Column(Integer, nullable=True, index=True)
    summary = Column(String(300), nullable=False)
    metadata_json = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class PMSChecklistItem(Base):
    __tablename__ = "pms_checklist_items"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("pms_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(220), nullable=False)
    is_completed = Column(Boolean, default=False)
    position = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PMSTag(Base):
    __tablename__ = "pms_tags"
    __table_args__ = (UniqueConstraint("organization_id", "name", name="uq_pms_tag_org_name"),)

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, nullable=True, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(30))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PMSTaskTag(Base):
    __tablename__ = "pms_task_tags"

    task_id = Column(Integer, ForeignKey("pms_tasks.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("pms_tags.id", ondelete="CASCADE"), primary_key=True)


class PMSFileAsset(Base):
    __tablename__ = "pms_file_assets"

    id = Column(Integer, primary_key=True, index=True)
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    project_id = Column(Integer, ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=True, index=True)
    task_id = Column(Integer, ForeignKey("pms_tasks.id", ondelete="CASCADE"), nullable=True, index=True)
    milestone_id = Column(Integer, ForeignKey("pms_milestones.id", ondelete="CASCADE"), nullable=True, index=True)
    file_name = Column(String(240), nullable=False)
    original_name = Column(String(240), nullable=False)
    mime_type = Column(String(120))
    size_bytes = Column(Integer, default=0)
    storage_path = Column(String(500), nullable=False)
    version_number = Column(Integer, default=1)
    visibility = Column(String(40), default="Internal", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class PMSComment(Base):
    __tablename__ = "pms_comments"

    id = Column(Integer, primary_key=True, index=True)
    author_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    project_id = Column(Integer, ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=True, index=True)
    task_id = Column(Integer, ForeignKey("pms_tasks.id", ondelete="CASCADE"), nullable=True, index=True)
    milestone_id = Column(Integer, ForeignKey("pms_milestones.id", ondelete="CASCADE"), nullable=True, index=True)
    parent_comment_id = Column(Integer, ForeignKey("pms_comments.id", ondelete="CASCADE"), nullable=True, index=True)
    body = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=True, index=True)
    is_edited = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))


class PMSTimeLog(Base):
    __tablename__ = "pms_time_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("pms_tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    log_date = Column(Date, nullable=False, index=True)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer, nullable=False)
    description = Column(Text)
    is_billable = Column(Boolean, default=False, index=True)
    approval_status = Column(String(30), default="Pending", index=True)
    approved_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PMSClientApproval(Base):
    __tablename__ = "pms_client_approvals"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pms_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    milestone_id = Column(Integer, ForeignKey("pms_milestones.id", ondelete="CASCADE"), nullable=True, index=True)
    requested_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    client_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(30), default="Pending", index=True)
    remarks = Column(Text)
    decided_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
