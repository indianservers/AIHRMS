# AI Agents Current Status

Date: 2026-05-12

## Scope Confirmed

This status now covers the backend foundation, Part 3 AI adapters/safe tool registry, and Part 4 OpenAI-backed AI Agent orchestration. It does not add frontend screens and does not execute final risky CRM/HRMS/PMS actions.

## Files Created In This Step

- `backend/app/ai_agents/api.py`
- `backend/app/ai_agents/adapters/base.py`
- `backend/app/ai_agents/adapters/crm_ai_adapter.py`
- `backend/app/ai_agents/adapters/hrms_ai_adapter.py`
- `backend/app/ai_agents/adapters/pms_ai_adapter.py`
- `backend/app/ai_agents/adapters/cross_module_ai_adapter.py`
- `backend/app/ai_agents/models.py`
- `backend/app/ai_agents/prompts.py`
- `backend/app/ai_agents/schemas.py`
- `backend/app/ai_agents/services/approvals.py`
- `backend/app/ai_agents/services/audit.py`
- `backend/app/ai_agents/services/conversations.py`
- `backend/app/ai_agents/services/openai_service.py`
- `backend/app/ai_agents/services/orchestrator.py`
- `backend/app/ai_agents/services/system_prompt_builder.py`
- `backend/app/ai_agents/services/registry.py`
- `backend/app/ai_agents/services/settings.py`
- `backend/app/ai_agents/tools/ai_tool_definition_builder.py`
- `backend/app/ai_agents/tools/tool_schemas.py`
- `backend/app/ai_agents/tools/definitions.py`
- `backend/app/ai_agents/tools/ai_tool_registry_service.py`
- `backend/app/ai_agents/tools/ai_tool_execution_service.py`
- `backend/alembic/versions/20260512_031_ai_agents.py`
- `docs/ai-agents/README.md`
- `docs/AI_AGENTS_API_TESTING.md`
- `docs/AI_AGENTS_TOOL_TESTING.md`
- `docs/AI_AGENTS_OPENAI_SETUP.md`

## Files Modified In This Step

- `backend/app/main.py`
  - Seeds AI agent configuration records during application startup.
- `backend/app/module_registry.py`
  - Registers the AI Agents router and models with the existing module registry.
- `backend/app/core/config.py`
  - Adds AI Agent OpenAI/runtime settings.
- `backend/.env.example`
  - Documents AI Agent OpenAI/runtime variables.
- `docs/AI_AGENTS_CURRENT_STATUS.md`
  - Updated to reflect OpenAI orchestration status.

## Files Removed Or Corrected

Removed earlier out-of-scope AI files:

- `backend/app/ai_agents/adapters/`
- `backend/app/ai_agents/services/openai_service.py`
- `backend/app/ai_agents/services/orchestrator.py`
- `backend/app/ai_agents/services/tools.py`
- `backend/app/apps/crm/services.py`
- `backend/app/apps/project_management/services.py`
- `backend/app/services/hrms_ai_service.py`
- `frontend/src/apps/ai-agents/`

Part 4 reintroduced scoped backend-only `openai_service.py` and `orchestrator.py` implementations that use the safe tool registry and do not bypass adapters.

Corrected earlier frontend/config changes:

- Removed AI Agents route injection from `frontend/src/App.tsx`.
- Removed floating AI button from `frontend/src/components/layout/AppLayout.tsx`.
- Removed AI Agents navigation and route access edits from `frontend/src/lib/roles.ts`.
- Removed frontend `aiAgentsApi` client from `frontend/src/services/api.ts`.
- Earlier out-of-scope frontend changes remain removed.

## Existing CRM/HRMS/PMS Files Found And Reused

Existing modules remain untouched:

- CRM: `backend/app/apps/crm/`
- PMS: `backend/app/apps/project_management/`
- HRMS APIs/models/services under `backend/app/api/v1/`, `backend/app/models/`, `backend/app/crud/`, and `backend/app/services/`

No duplicate CRM, HRMS, or PMS services/controllers/entities are present from the AI Agents work.

Adapter integration approach:

- CRM adapter uses existing CRM SQLAlchemy models from `backend/app/apps/crm/models.py` with organization/deleted-record scoping. The CRM module currently has router/model-heavy logic and no general CRM service class for the required read tools.
- PMS adapter uses existing PMS models and permission helpers from `backend/app/apps/project_management/access.py`.
- HRMS adapter uses existing employee, leave, and attendance CRUD helpers where available:
  - `crud_employee`
  - `crud_leave`
  - `crud_attendance`
- Cross-module adapter uses existing AI approvals plus safe scoped reads from CRM/PMS/HRMS models.

## Dummy Files Detected

No dummy CRM/HRMS/PMS files, fake lead/project/employee data, or standalone demo modules are present in the AI Agents foundation.

## AI Tables And Models Created

AI-only SQLAlchemy models:

- `AiAgent`
- `AiAgentTool`
- `AiConversation`
- `AiMessage`
- `AiActionApproval`
- `AiAuditLog`
- `AiAgentSetting`

AI-only migration tables:

- `ai_agents`
- `ai_agent_tools`
- `ai_conversations`
- `ai_messages`
- `ai_action_approvals`
- `ai_audit_logs`
- `ai_agent_settings`

No CRM, HRMS, or PMS tables are created or modified by the AI Agents migration.

## APIs Implemented

Registered under the existing API prefix, so the effective paths are `/api/v1/...`:

- `GET /api/v1/ai-agents`
- `GET /api/v1/ai-agents/:id`
- `PATCH /api/v1/ai-agents/:id/status`
- `GET /api/v1/ai-agents/config`
- `PUT /api/v1/ai-agents/config/:agentId`
- `POST /api/v1/ai-agents/conversations`
- `GET /api/v1/ai-agents/conversations`
- `GET /api/v1/ai-agents/conversations/:id`
- `GET /api/v1/ai-agents/conversations/:id/messages`
- `POST /api/v1/ai-agents/conversations/:id/messages`
- `GET /api/v1/ai-agents/approvals/pending`
- `POST /api/v1/ai-agents/approvals/:id/approve`
- `POST /api/v1/ai-agents/approvals/:id/reject`
- `GET /api/v1/ai-agents/logs`
- `POST /api/v1/ai-agents/tools/test`
- `POST /api/v1/ai-agents/:agentId/chat`

The conversation message endpoint still saves a message only. The AI chat endpoint is now:

`POST /api/v1/ai-agents/:agentId/chat`

It saves the user message, sends recent conversation history plus allowed tools to OpenAI, executes requested tools through `AiToolExecutionService`, saves tool calls/results, saves the final assistant response, and returns approvals if generated.

## OpenAI Integration

Created:

- `OpenAiService`
- `AiAgentOrchestratorService`
- `AiSystemPromptBuilder`
- `AiToolDefinitionBuilder`

The implementation uses the official OpenAI Python SDK from the backend only. Tool calls use OpenAI Chat Completions function/tool calling and are normalized before the orchestrator handles them.

Environment variables:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `AI_AGENT_DEFAULT_TEMPERATURE`
- `AI_AGENT_MAX_TOOL_CALLS`
- `AI_AGENT_ENABLE_STREAMING`
- `AI_AGENT_AUDIT_LOGGING`

Streaming remains disabled in this step.

## Seed Agents Created

Initial AI configuration records are seeded by `AiAgentRegistryService` using stable `code` values:

- `crm_lead_qualification`
- `crm_followup`
- `crm_deal_analyzer`
- `crm_customer_summary`
- `pms_project_status`
- `pms_task_planning`
- `pms_deadline_risk`
- `pms_meeting_notes`
- `hrms_policy_assistant`
- `hrms_leave_assistant`
- `hrms_recruitment_screening`
- `hrms_attendance_anomaly`
- `hrms_letter_drafting`
- `business_summary`
- `smart_search`
- `smart_notification`

These are AI agent configuration records only. No CRM/HRMS/PMS data is seeded.

## Tools Registered

The safe tool registry now contains 44 tools:

CRM:

- `crm_get_lead`
- `crm_search_duplicate_leads`
- `crm_get_lead_activities`
- `crm_get_overdue_followups`
- `crm_get_deal`
- `crm_get_deal_notes`
- `crm_get_deal_activities`
- `crm_get_customer`
- `crm_get_customer_deals`
- `crm_get_customer_activities`
- `crm_create_followup_task_draft`
- `crm_propose_lead_update`
- `crm_draft_message`

PMS:

- `pms_get_project`
- `pms_get_project_tasks`
- `pms_get_delayed_tasks`
- `pms_get_milestones`
- `pms_get_project_comments`
- `pms_get_team_members`
- `pms_get_team_workload`
- `pms_get_task_dependencies`
- `pms_create_task_draft`
- `pms_create_subtask_draft`
- `pms_create_risk_log_proposal`
- `pms_create_project_status_report_draft`

HRMS:

- `hrms_get_employee`
- `hrms_get_leave_balance`
- `hrms_get_team_leave_calendar`
- `hrms_search_policy`
- `hrms_get_policy_document`
- `hrms_get_attendance`
- `hrms_get_shift`
- `hrms_get_job_opening`
- `hrms_get_candidate`
- `hrms_get_candidate_resume_text`
- `hrms_generate_letter_draft`
- `hrms_create_leave_request_proposal`
- `hrms_create_attendance_alert_proposal`

Cross-module:

- `cross_get_business_summary`
- `cross_get_pending_approvals`
- `cross_safe_search_crm`
- `cross_safe_search_pms`
- `cross_safe_search_hrms`
- `cross_get_alerts`

## Approval Tools

These tools create `ai_action_approvals` records and do not execute final product actions:

- `crm_create_followup_task_draft`
- `crm_propose_lead_update`
- `pms_create_task_draft`
- `pms_create_subtask_draft`
- `pms_create_risk_log_proposal`
- `hrms_generate_letter_draft`
- `hrms_create_leave_request_proposal`
- `hrms_create_attendance_alert_proposal`

## Missing Existing Service Methods

- `cross_get_alerts` returns `SERVICE_METHOD_MISSING` because there is no single existing cross-module alert aggregation service mapped yet.
- CRM adapter read methods use existing CRM models directly because the CRM module currently exposes most logic through a router rather than a reusable service layer.
- HRMS letter draft uses existing document template and employee records, but final document generation/issue is intentionally not executed.

## Auth And Permission Approach

- All AI endpoints use the existing `get_current_user` dependency.
- No separate authentication system was added.
- User-owned resources such as conversations are filtered by `current_user.id`.
- Pending approvals are scoped to the current user unless the user is a superuser.
- A temporary internal `canAccessAiAgents` gate checks active authenticated users. This should be mapped to the full RBAC permission system in a later step.
- Company-level settings use the current user's company/organization context when available.

## Audit Logging

Audit logs are written for:

- Agent list viewed
- Agent status changed
- Conversation created
- Message saved
- Approval approved
- Approval rejected
- Agent config updated
- AI tool executed
- AI tool failed
- AI tool approval created
- AI chat started
- AI user message saved
- AI OpenAI request sent
- AI tool call requested
- AI approval requested
- AI assistant response saved
- AI chat failed

Audit records include user, agent, module, action, input/output JSON, status, IP address, user agent, and related entity context where available.

## How To Test

1. Run the migration:

```powershell
cd backend
alembic upgrade head
```

2. Start the backend, which also seeds the 16 AI agents:

```powershell
python main.py
```

3. If a manual seed is needed without starting the server:

```powershell
@'
from app.db.session import SessionLocal
from app.ai_agents.services.registry import AiAgentRegistryService
from app.ai_agents.tools.ai_tool_registry_service import AiToolRegistryService

db = SessionLocal()
try:
    AiAgentRegistryService(db).ensure_seed_data()
    AiToolRegistryService(db).ensure_seed_data()
    db.commit()
finally:
    db.close()
'@ | python -
```

4. Authenticate with the existing login API and call the sample requests in `docs/AI_AGENTS_API_TESTING.md`.

5. Test tools using `docs/AI_AGENTS_TOOL_TESTING.md`.

6. Configure `OPENAI_API_KEY` and test chat using `docs/AI_AGENTS_OPENAI_SETUP.md`.

## Known Limitations

- The active Python environment emitted an OpenAI SDK compatibility warning under Python 3.14 from the SDK's Pydantic v1 compatibility layer. Imports and route registration still pass.
- `cross_get_alerts` is intentionally mapped to `SERVICE_METHOD_MISSING` until an existing alert aggregation service is available.
- Chat uses non-streaming responses only.
- Conversation history is limited to the last 20 user/assistant messages.

## Not Implemented Yet

- Risky action execution after approval
- Frontend AI Agent pages
- Ask AI buttons
- Streaming responses

## Next Recommended Step

Build the frontend AI Agent dashboard/chat UI and add scoped "Ask AI" buttons in CRM, HRMS, and PMS pages.
