import pytest
from fastapi import HTTPException

from app.apps.project_management.access import can_access_project, get_project_for_action
from app.apps.project_management.api.router import (
    add_project_member,
    create_component,
    create_epic,
    create_project,
    create_release,
    create_sprint,
    create_saved_filter,
    start_sprint,
    complete_sprint,
    create_task,
    get_project_velocity,
    get_project_workload,
    get_release_readiness,
    add_task_dependency,
    bulk_update_tasks,
    list_project_activity,
    list_tasks,
)
from app.apps.project_management.models import PMSProjectMember  # noqa: F401 - ensure PMS tables are registered
from app.apps.project_management.schemas import (
    PMSComponentCreate,
    PMSEpicCreate,
    PMSProjectCreate,
    PMSProjectMemberCreate,
    PMSReleaseCreate,
    PMSSavedFilterCreate,
    PMSSprintCreate,
    PMSTaskDependencyCreate,
    SprintCompleteRequest,
    TaskBulkUpdateRequest,
    PMSTaskCreate,
)
from app.models.user import Permission, Role, User


def _user(db, email: str, permission_names: list[str] | None = None) -> User:
    role = Role(name=f"role_{email}", description="PMS test role")
    db.add(role)
    db.flush()
    permissions = []
    for name in permission_names or []:
        permission = db.query(Permission).filter(Permission.name == name).first()
        if not permission:
            permission = Permission(name=name, description=name, module="project_management")
            db.add(permission)
            db.flush()
        permissions.append(permission)
    role.permissions = permissions
    user = User(email=email, hashed_password="not-used", is_active=True, role_id=role.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_project_creator_becomes_manager_and_can_add_member(db):
    manager = _user(db, "pms-manager@example.com", ["pms_manage_projects"])
    viewer = _user(db, "pms-viewer@example.com")

    project = create_project(
        PMSProjectCreate(name="Client Launch", project_key="CL"),
        db=db,
        current_user=manager,
    )

    assert can_access_project(db, project, manager, "manage_members")

    member = add_project_member(
        project.id,
        PMSProjectMemberCreate(user_id=viewer.id, role="Viewer"),
        db=db,
        current_user=manager,
    )

    assert member.role == "Viewer"
    assert can_access_project(db, project, viewer, "browse")
    assert not can_access_project(db, project, viewer, "manage_tasks")


def test_non_member_cannot_view_or_create_project_tasks(db):
    manager = _user(db, "pms-task-manager@example.com", ["pms_manage_projects"])
    outsider = _user(db, "pms-outsider@example.com")

    project = create_project(
        PMSProjectCreate(name="Private Build", project_key="PB"),
        db=db,
        current_user=manager,
    )

    with pytest.raises(HTTPException) as denied:
        get_project_for_action(db, project.id, outsider, "browse")
    assert denied.value.status_code == 403

    with pytest.raises(HTTPException) as task_denied:
        create_task(
            project.id,
            PMSTaskCreate(title="Hidden task", task_key="PB-1"),
            db=db,
            current_user=outsider,
        )
    assert task_denied.value.status_code == 403


def test_advanced_issue_fields_persist_and_filter(db):
    manager = _user(db, "pms-issue-manager@example.com", ["pms_manage_projects"])
    project = create_project(
        PMSProjectCreate(name="Software Delivery", project_key="SD"),
        db=db,
        current_user=manager,
    )

    task = create_task(
        project.id,
        PMSTaskCreate(
            title="Fix calendar regression",
            task_key="SD-1",
            work_type="Bug",
            epic_key="EPIC-PLANNING",
            component="Calendar",
            severity="S1",
            environment="Production",
            affected_version="v2.2.1",
            fix_version="v2.3",
            release_name="May Stabilization",
            original_estimate_hours=12,
            remaining_estimate_hours=5,
            story_points=3,
            security_level="Internal",
            development_branch="fix/sd-1-calendar-regression",
            development_commits=2,
            development_prs=1,
            development_build="Failing",
        ),
        db=db,
        current_user=manager,
    )

    assert task.work_type == "Bug"
    assert task.component == "Calendar"
    assert task.fix_version == "v2.3"
    assert task.rank == 1

    filtered = list_tasks(
        project.id,
        skip=0,
        limit=100,
        status=None,
        assignee_id=None,
        sprint_id=None,
        epic_id=None,
        component_id=None,
        release_id=None,
        work_type="Bug",
        epic_key=None,
        component="Calendar",
        severity="S1",
        fix_version="v2.3",
        release_name="May Stabilization",
        security_level=None,
        db=db,
        current_user=manager,
    )

    assert [item.task_key for item in filtered] == ["SD-1"]


def test_normalized_planning_objects_link_to_tasks(db):
    manager = _user(db, "pms-planning-manager@example.com", ["pms_manage_projects"])
    project = create_project(
        PMSProjectCreate(name="Roadmap Build", project_key="RB"),
        db=db,
        current_user=manager,
    )
    epic = create_epic(
        project.id,
        PMSEpicCreate(epic_key="RB-EPIC-1", name="Planning Intelligence", status="Active"),
        db=db,
        current_user=manager,
    )
    component = create_component(
        project.id,
        PMSComponentCreate(name="Timeline", lead_user_id=manager.id),
        db=db,
        current_user=manager,
    )
    release = create_release(
        project.id,
        PMSReleaseCreate(name="v2.4", status="Planning", readiness_percent=35),
        db=db,
        current_user=manager,
    )

    task = create_task(
        project.id,
        PMSTaskCreate(
            title="Build critical path rollup",
            task_key="RB-1",
            epic_id=epic.id,
            component_id=component.id,
            release_id=release.id,
            work_type="Story",
        ),
        db=db,
        current_user=manager,
    )

    assert task.epic_id == epic.id
    assert task.component_id == component.id
    assert task.release_id == release.id
    assert task.epic_key == "RB-EPIC-1"
    assert task.initiative == "Planning Intelligence"
    assert task.component == "Timeline"
    assert task.release_name == "v2.4"
    assert task.fix_version == "v2.4"

    filtered = list_tasks(
        project.id,
        skip=0,
        limit=100,
        status=None,
        assignee_id=None,
        sprint_id=None,
        epic_id=epic.id,
        component_id=component.id,
        release_id=release.id,
        work_type=None,
        epic_key=None,
        component=None,
        severity=None,
        fix_version=None,
        release_name=None,
        security_level=None,
        db=db,
        current_user=manager,
    )
    assert [item.task_key for item in filtered] == ["RB-1"]


def test_market_gap_api_additions_for_sprints_dependencies_filters_and_reports(db):
    manager = _user(db, "pms-gap-manager@example.com", ["pms_manage_projects"])
    project = create_project(
        PMSProjectCreate(name="Market Gap APIs", project_key="MG"),
        db=db,
        current_user=manager,
    )
    release = create_release(
        project.id,
        PMSReleaseCreate(name="v3.0", status="Planning", readiness_percent=40),
        db=db,
        current_user=manager,
    )
    sprint = create_sprint(
        project.id,
        PMSSprintCreate(name="Sprint Gap", start_date="2026-05-07", end_date="2026-05-21", capacity_hours=40),
        db=db,
        current_user=manager,
    )
    blocker = create_task(
        project.id,
        PMSTaskCreate(title="Critical blocker", task_key="MG-1", work_type="Bug", severity="S1", story_points=5, release_id=release.id),
        db=db,
        current_user=manager,
    )
    dependent = create_task(
        project.id,
        PMSTaskCreate(title="Dependent story", task_key="MG-2", work_type="Story", story_points=8),
        db=db,
        current_user=manager,
    )

    dependency = add_task_dependency(
        dependent.id,
        PMSTaskDependencyCreate(depends_on_task_id=blocker.id),
        db=db,
        current_user=manager,
    )
    assert dependency.depends_on_task_id == blocker.id

    bulk = bulk_update_tasks(
        TaskBulkUpdateRequest(task_ids=[blocker.id, dependent.id], sprint_id=sprint.id, release_id=release.id),
        db=db,
        current_user=manager,
    )
    assert bulk["updated_count"] == 2

    started = start_sprint(sprint.id, db=db, current_user=manager)
    assert started.status == "Active"
    assert started.committed_story_points == 13

    blocker.status = "Done"
    db.add(blocker)
    db.commit()
    completed = complete_sprint(
        sprint.id,
        SprintCompleteRequest(),
        db=db,
        current_user=manager,
    )
    assert completed.status == "Completed"
    assert completed.velocity_points == 5

    velocity = get_project_velocity(project.id, db=db, current_user=manager)
    assert velocity["average_velocity_points"] == 5

    saved = create_saved_filter(
        project.id,
        PMSSavedFilterCreate(name="Critical release bugs", view_type="backlog", query="severity = S1 AND release = v3.0"),
        db=db,
        current_user=manager,
    )
    assert saved.name == "Critical release bugs"

    readiness = get_release_readiness(release.id, db=db, current_user=manager)
    assert readiness["total_tasks"] == 2
    assert readiness["severity_counts"]["S1"] == 1

    workload = get_project_workload(project.id, group_by="sprint", sprint_id=None, db=db, current_user=manager)
    assert workload["group_by"] == "sprint"

    activity = list_project_activity(project.id, task_id=None, limit=20, db=db, current_user=manager)
    assert any(item.action == "dependency_added" for item in activity)
