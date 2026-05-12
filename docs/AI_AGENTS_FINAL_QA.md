# AI Agents Final QA

## Backend Smoke Tests

```powershell
cd backend
alembic upgrade head
python -m py_compile app/ai_agents/models.py app/ai_agents/schemas.py app/ai_agents/api.py app/ai_agents/services/approval_executor.py app/ai_agents/services/rate_limit.py app/ai_agents/services/system_prompt_builder.py app/ai_agents/services/orchestrator.py app/ai_agents/adapters/crm_ai_adapter.py app/ai_agents/adapters/pms_ai_adapter.py app/ai_agents/adapters/hrms_ai_adapter.py
python -c "from app.main import app; print('routes', len(app.routes))"
```

## Frontend Smoke Tests

```powershell
cd frontend
npm run build
rg -n "OPENAI_API_KEY|api\.openai\.com|openai" src public index.html
```

The scan should return no matches.

## CRM Tests

1. Open a lead detail page and click Ask AI.
2. Use Lead Qualification Agent.
3. Confirm the agent can call `crm_get_lead`.
4. Ask it to check duplicates and confirm `crm_search_duplicate_leads` is used when needed.
5. Ask it to suggest lead score/status.
6. Confirm an approval card appears.
7. Approve the action.
8. Confirm lead score/status updates only after approval.
9. Confirm an AI audit log is written.

Deal analyzer:

1. Open a deal page.
2. Ask for deal health/risk.
3. Confirm no direct deal closure action is available.

## PMS Tests

1. Open a project page and click Ask AI.
2. Use Project Status Agent.
3. Confirm delayed tasks and milestones are read via PMS tools.
4. Use Task Planning Agent to propose a task.
5. Confirm approval card appears.
6. Approve the task.
7. Confirm PMS task is created and activity is recorded.
8. Confirm unsupported deadline-change requests are blocked.

## HRMS Tests

Policy:

1. Ask HR Policy Assistant a policy question.
2. Confirm it answers only from policy data.
3. If unavailable, it should say HR confirmation is required.

Leave:

1. Use Leave Assistant to check leave balance.
2. Ask it to draft a leave request.
3. Confirm approval appears.
4. Approve and confirm leave request is created through existing leave CRUD.

Attendance:

1. Use Attendance Anomaly Agent.
2. Confirm it can create an attendance alert/helpdesk ticket after approval.
3. Confirm it does not modify attendance directly.

Letters:

1. Use HR Letter Drafting Agent.
2. Approve a draft letter.
3. Confirm only a draft generated document is created, not an issued/final letter.

## Cross-Module Tests

1. Business Summary Agent summarizes CRM/PMS/HRMS only through safe tools.
2. Smart Search returns permitted results only.
3. Smart Notification proposes notifications but does not send externally.

## Security Tests

1. User cannot access another user's conversation.
2. User cannot approve another user's pending approval unless superuser.
3. User without PMS permission cannot create PMS task via AI approval.
4. User without CRM permission cannot fetch or update leads.
5. User without salary/payroll permission does not see salary/bank fields.
6. AI cannot use tools not allowed for the selected agent.
7. AI cannot run SQL.
8. AI cannot reveal the system prompt or API key.
9. Prompt injection inside CRM note/project comment/resume is ignored.
10. Unsupported critical action returns `ACTION_NOT_SUPPORTED_IN_FIRST_RELEASE`.

## Current Verification Results

- Backend Python compile passed.
- FastAPI app import and route registration passed.
- Frontend production build passed.
- Frontend OpenAI/API-key scan returned no matches.
