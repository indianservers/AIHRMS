from app.db.init_db import init_db
from app.models.user import User


def _login(client, email="admin@aihrms.com", password="Admin@123456"):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_workflow_conditions_escalations_and_reminders(client, db):
    init_db(db)
    admin_headers = _login(client)
    hr_user = db.query(User).filter(User.email == "hr@aihrms.com").first()

    definition = client.post(
        "/api/v1/workflow-engine/definitions",
        json={
            "name": "High Value Payroll Approval",
            "module": "payroll",
            "trigger_event": "submitted",
            "steps": [
                {
                    "step_order": 1,
                    "approver_type": "Role",
                    "approver_value": "super_admin",
                    "condition_expression": "amount >= 100000",
                    "timeout_hours": -1,
                    "escalation_user_id": hr_user.id,
                },
                {
                    "step_order": 2,
                    "approver_type": "Role",
                    "approver_value": "hr_manager",
                    "condition_expression": "requires_hr == true",
                },
            ],
        },
        headers=admin_headers,
    )
    assert definition.status_code == 201

    skipped = client.post(
        "/api/v1/workflow-engine/instances",
        json={
            "workflow_id": definition.json()["id"],
            "module": "payroll",
            "entity_type": "payroll_run",
            "entity_id": 1,
            "context_json": {"amount": 50000, "requires_hr": "false"},
        },
        headers=admin_headers,
    )
    assert skipped.status_code == 201
    assert skipped.json()["status"] == "Approved"

    instance = client.post(
        "/api/v1/workflow-engine/instances",
        json={
            "workflow_id": definition.json()["id"],
            "module": "payroll",
            "entity_type": "payroll_run",
            "entity_id": 2,
            "context_json": {"amount": 150000, "requires_hr": "true"},
        },
        headers=admin_headers,
    )
    assert instance.status_code == 201
    assert instance.json()["status"] == "Pending"

    reminders = client.post("/api/v1/workflow-engine/tasks/send-reminders", headers=admin_headers)
    assert reminders.status_code == 200
    assert reminders.json()[0]["reminder_sent_at"] is not None

    escalated = client.post("/api/v1/workflow-engine/tasks/process-escalations", headers=admin_headers)
    assert escalated.status_code == 200
    assert escalated.json()[0]["escalated_to_user_id"] == hr_user.id

    hr_headers = _login(client, "hr@aihrms.com", "HR@123456")
    first_tasks = client.get("/api/v1/workflow-engine/tasks", headers=hr_headers)
    assert first_tasks.status_code == 200
    assert any(item["instance_id"] == instance.json()["id"] for item in first_tasks.json())

    first_task_id = next(item["id"] for item in first_tasks.json() if item["instance_id"] == instance.json()["id"])
    decided = client.put(
        f"/api/v1/workflow-engine/tasks/{first_task_id}/decision",
        json={"decision": "approve", "reason": "Amount verified"},
        headers=hr_headers,
    )
    assert decided.status_code == 200

    second_tasks = client.get("/api/v1/workflow-engine/tasks", headers=hr_headers)
    assert second_tasks.status_code == 200
    assert any(item["instance_id"] == instance.json()["id"] for item in second_tasks.json())
