from __future__ import annotations

from datetime import date
from typing import Any

from app.ai_agents.adapters.base import AiAdapterBase, model_to_dict
from app.apps.project_management.access import accessible_project_query, get_project_for_action, get_task_project_for_action
from app.apps.project_management.models import PMSComment, PMSMilestone, PMSProjectMember, PMSTask, PMSTaskDependency
from app.models.user import User


class PmsAiAdapter(AiAdapterBase):
    def get_project_by_id(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        project = get_project_for_action(self.db, int(input["project_id"]), user, "browse")
        return {"project": model_to_dict(project)}

    def get_project_tasks(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        project = get_project_for_action(self.db, int(input["project_id"]), user, "browse")
        query = self.db.query(PMSTask).filter(PMSTask.project_id == project.id, PMSTask.deleted_at == None)
        if input.get("status"):
            query = query.filter(PMSTask.status == input["status"])
        rows = query.order_by(PMSTask.rank.asc().nullslast(), PMSTask.created_at.desc()).limit(200).all()
        return {"tasks": [model_to_dict(row) for row in rows], "count": len(rows)}

    def get_delayed_tasks(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        project = get_project_for_action(self.db, int(input["project_id"]), user, "browse")
        rows = (
            self.db.query(PMSTask)
            .filter(PMSTask.project_id == project.id, PMSTask.deleted_at == None, PMSTask.due_date != None, PMSTask.due_date < date.today(), PMSTask.completed_at == None)
            .order_by(PMSTask.due_date.asc())
            .limit(100)
            .all()
        )
        return {"delayed_tasks": [model_to_dict(row) for row in rows], "count": len(rows)}

    def get_milestones(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        project = get_project_for_action(self.db, int(input["project_id"]), user, "browse")
        rows = self.db.query(PMSMilestone).filter(PMSMilestone.project_id == project.id).order_by(PMSMilestone.due_date.asc().nullslast()).limit(100).all()
        return {"milestones": [model_to_dict(row) for row in rows]}

    def get_project_comments(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        project = get_project_for_action(self.db, int(input["project_id"]), user, "browse")
        rows = self.db.query(PMSComment).filter(PMSComment.project_id == project.id, PMSComment.deleted_at == None).order_by(PMSComment.created_at.desc()).limit(100).all()
        return {"comments": [model_to_dict(row) for row in rows]}

    def get_team_members(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        project = get_project_for_action(self.db, int(input["project_id"]), user, "browse")
        rows = self.db.query(PMSProjectMember).filter(PMSProjectMember.project_id == project.id).all()
        return {"members": [model_to_dict(row) for row in rows]}

    def get_team_workload(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        project = get_project_for_action(self.db, int(input["project_id"]), user, "browse")
        rows = (
            self.db.query(PMSTask)
            .filter(PMSTask.project_id == project.id, PMSTask.deleted_at == None, PMSTask.completed_at == None)
            .all()
        )
        workload: dict[str, dict[str, Any]] = {}
        for task in rows:
            key = str(task.assignee_user_id or "unassigned")
            bucket = workload.setdefault(key, {"assignee_user_id": task.assignee_user_id, "task_count": 0, "story_points": 0, "estimated_hours": 0.0})
            bucket["task_count"] += 1
            bucket["story_points"] += int(task.story_points or 0)
            bucket["estimated_hours"] += float(task.estimated_hours or 0)
        return {"workload": list(workload.values())}

    def get_task_dependencies(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        if input.get("task_id"):
            task, _project = get_task_project_for_action(self.db, int(input["task_id"]), user, "browse")
            rows = self.db.query(PMSTaskDependency).filter(PMSTaskDependency.task_id == task.id).all()
        elif input.get("project_id"):
            project = get_project_for_action(self.db, int(input["project_id"]), user, "browse")
            task_ids = self.db.query(PMSTask.id).filter(PMSTask.project_id == project.id, PMSTask.deleted_at == None)
            rows = self.db.query(PMSTaskDependency).filter(PMSTaskDependency.task_id.in_(task_ids)).all()
        else:
            rows = []
        return {"dependencies": [model_to_dict(row) for row in rows]}

    def create_task_draft(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        get_project_for_action(self.db, int(input["project_id"]), user, "manage_tasks")
        return {"draft": {**input, "created_by": user.id, "status": "draft", "note": "Draft only. No PMS task has been created."}}

    def create_subtask_draft(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        task, _project = get_task_project_for_action(self.db, int(input["parent_task_id"]), user, "manage_tasks")
        return {"draft": {**input, "project_id": task.project_id, "created_by": user.id, "status": "draft", "note": "Draft only. No PMS sub-task has been created."}}

    def create_risk_log_proposal(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        get_project_for_action(self.db, int(input["project_id"]), user, "manage_tasks")
        return {"proposed_action": {**input, "created_by": user.id, "note": "Proposal only. No risk record has been created."}}

    def create_project_status_report_draft(self, user: User, input: dict[str, Any]) -> dict[str, Any]:
        project = get_project_for_action(self.db, int(input["project_id"]), user, "browse")
        return {"draft": {**input, "project": model_to_dict(project), "note": "Draft report only. No report file has been generated."}}

    def portfolio_summary(self, user: User) -> dict[str, Any]:
        projects = accessible_project_query(self.db, user).all()
        ids = [project.id for project in projects]
        open_tasks = self.db.query(PMSTask).filter(PMSTask.project_id.in_(ids), PMSTask.deleted_at == None, PMSTask.completed_at == None).count() if ids else 0
        return {"total_projects": len(projects), "active_projects": len([p for p in projects if str(p.status).lower() not in {"completed", "closed"}]), "open_tasks": open_tasks}
