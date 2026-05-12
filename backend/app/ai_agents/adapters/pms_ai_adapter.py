from __future__ import annotations

import json
from datetime import date
from typing import Any

from app.ai_agents.adapters.base import AiAdapterBase, model_to_dict
from app.apps.project_management.access import accessible_project_query, get_project_for_action, get_task_project_for_action
from app.apps.project_management.models import PMSActivity, PMSComment, PMSMilestone, PMSProject, PMSProjectMember, PMSRisk, PMSTask, PMSTaskDependency
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
        comments = []
        for row in rows:
            data = model_to_dict(row)
            for field in ("body", "content", "comment"):
                if data.get(field) and len(str(data[field])) > 1200:
                    data[field] = str(data[field])[:1200] + "...[truncated]"
            comments.append(data)
        return {"comments": comments}

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

    def execute_create_task(self, user: User, proposed_action: dict[str, Any]) -> dict[str, Any]:
        input = self._approval_input(proposed_action)
        project = get_project_for_action(self.db, int(input["project_id"]), user, "manage_tasks")
        task = PMSTask(
            project_id=project.id,
            assignee_user_id=int(input["assignee_id"]) if input.get("assignee_id") else None,
            reporter_user_id=user.id,
            title=str(input["title"])[:220],
            description=input.get("description"),
            task_key=self._next_task_key(project),
            work_type="Task",
            status="To Do",
            priority=self._priority(input.get("priority")),
            due_date=self._parse_date(input.get("due_date")),
        )
        self.db.add(task)
        self.db.flush()
        self._record_activity(project.id, task.id, user.id, "task.created", "task", task.id, f"AI-approved task created: {task.title}", {"source": "ai_approval"})
        return {"success": True, "record_type": "pms_task", "record_id": task.id, "task_key": task.task_key, "title": task.title}

    def execute_create_subtask(self, user: User, proposed_action: dict[str, Any]) -> dict[str, Any]:
        input = self._approval_input(proposed_action)
        parent, project = get_task_project_for_action(self.db, int(input["parent_task_id"]), user, "manage_tasks")
        task = PMSTask(
            project_id=project.id,
            parent_task_id=parent.id,
            assignee_user_id=int(input["assignee_id"]) if input.get("assignee_id") else None,
            reporter_user_id=user.id,
            title=str(input["title"])[:220],
            description=input.get("description"),
            task_key=self._next_subtask_key(parent),
            work_type="Sub-task",
            sprint_id=parent.sprint_id,
            epic_id=parent.epic_id,
            status="To Do",
            priority=parent.priority or "Medium",
            due_date=self._parse_date(input.get("due_date")),
        )
        self.db.add(task)
        self.db.flush()
        self._record_activity(project.id, task.id, user.id, "subtask.created", "task", task.id, f"AI-approved sub-task created: {task.title}", {"parent_task_id": parent.id, "source": "ai_approval"})
        return {"success": True, "record_type": "pms_task", "record_id": task.id, "task_key": task.task_key, "parent_task_id": parent.id}

    def execute_create_risk_log(self, user: User, proposed_action: dict[str, Any]) -> dict[str, Any]:
        input = self._approval_input(proposed_action)
        project = get_project_for_action(self.db, int(input["project_id"]), user, "manage_tasks")
        probability, impact = self._severity_scores(input.get("severity"))
        risk = PMSRisk(
            organization_id=project.organization_id,
            project_id=project.id,
            title=str(input["risk_title"])[:220],
            description=input.get("risk_description"),
            category="AI identified",
            probability=probability,
            impact=impact,
            risk_score=probability * impact,
            status="open",
            owner_user_id=user.id,
            mitigation_plan=input.get("mitigation_plan"),
        )
        self.db.add(risk)
        self.db.flush()
        self._record_activity(project.id, None, user.id, "risk.created", "risk", risk.id, f"AI-approved risk logged: {risk.title}", {"source": "ai_approval"})
        return {"success": True, "record_type": "pms_risk", "record_id": risk.id, "risk_score": risk.risk_score}

    def _approval_input(self, proposed_action: dict[str, Any]) -> dict[str, Any]:
        return proposed_action.get("input") if isinstance(proposed_action.get("input"), dict) else proposed_action

    def _next_task_key(self, project: PMSProject) -> str:
        count = self.db.query(PMSTask).filter(PMSTask.project_id == project.id).count()
        prefix = (project.project_key or "TASK").upper()
        while True:
            count += 1
            key = f"{prefix}-{count}"
            exists = self.db.query(PMSTask.id).filter(PMSTask.project_id == project.id, PMSTask.task_key == key).first()
            if not exists:
                return key

    def _next_subtask_key(self, parent: PMSTask) -> str:
        count = self.db.query(PMSTask).filter(PMSTask.parent_task_id == parent.id).count()
        while True:
            count += 1
            key = f"{parent.task_key}-{count}"
            exists = self.db.query(PMSTask.id).filter(PMSTask.project_id == parent.project_id, PMSTask.task_key == key).first()
            if not exists:
                return key

    def _parse_date(self, value: Any) -> date | None:
        if not value:
            return None
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value)[:10])

    def _priority(self, value: Any) -> str:
        mapping = {"low": "Low", "medium": "Medium", "high": "High", "critical": "Critical"}
        return mapping.get(str(value or "medium").lower(), "Medium")

    def _severity_scores(self, value: Any) -> tuple[int, int]:
        return {
            "low": (2, 2),
            "medium": (3, 3),
            "high": (4, 4),
            "critical": (5, 5),
        }.get(str(value or "medium").lower(), (3, 3))

    def _record_activity(self, project_id: int, task_id: int | None, actor_id: int, action: str, entity_type: str, entity_id: int | None, summary: str, metadata: dict[str, Any]) -> None:
        self.db.add(
            PMSActivity(
                project_id=project_id,
                task_id=task_id,
                actor_user_id=actor_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                summary=summary[:300],
                metadata_json=json.dumps(metadata, default=str),
            )
        )
