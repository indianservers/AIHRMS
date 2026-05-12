# AI Agents Frontend Testing

## Preconditions

1. Backend is running with AI Agent migrations applied.
2. Initial AI agents are seeded.
3. User is authenticated through the existing login flow.
4. `OPENAI_API_KEY` is configured only on the backend if testing real chat responses.

## Dashboard

Route: `/ai-agents`

Test cases:

- Agents load from `GET /api/v1/ai-agents`.
- Summary cards show total agents, active agents, pending approvals, AI actions today, and conversations today.
- Module filters work for All, CRM, PMS, HRMS, and Cross-module.
- Chat button opens `/ai-agents/chat/:agentId`.
- Configure button opens `/ai-agents/config`.
- Enable/disable calls `PATCH /api/v1/ai-agents/:id/status`.

## Chat

Route: `/ai-agents/chat/:agentId`

Test cases:

- Agent details load.
- Conversation sidebar lists existing conversations for the selected agent.
- Query params are honored:
  - `module`
  - `related_entity_type`
  - `related_entity_id`
  - `prompt`
- Prompt query param fills the input but does not auto-send.
- Sending a message calls `POST /api/v1/ai-agents/:agentId/chat`.
- Conversation ID is stored in the URL after the first response.
- Saved messages reload from `GET /api/v1/ai-agents/conversations/:id/messages`.
- Tool call previews are collapsed by default.
- Approval cards render when the backend returns approvals.
- Errors show a user-friendly message.

## Approvals

Route: `/ai-agents/approvals`

Test cases:

- Pending approvals load from `GET /api/v1/ai-agents/approvals/pending`.
- Module filter reloads approvals by module.
- Approve calls `POST /api/v1/ai-agents/approvals/:id/approve`.
- Reject requires a reason and calls `POST /api/v1/ai-agents/approvals/:id/reject`.
- Card status updates after approve/reject.
- No action is approved automatically.

## Logs

Route: `/ai-agents/logs`

Test cases:

- Logs load from `GET /api/v1/ai-agents/logs`.
- Module filter reloads logs.
- Status filter works client-side.
- Details expand to show input/output summaries.
- Hidden prompts and API keys are not displayed.

## Configuration

Route: `/ai-agents/config`

Test cases:

- Configuration loads from `GET /api/v1/ai-agents/config`.
- Enable/disable, auto action, approval required, and data access scope can be edited.
- Save calls `PUT /api/v1/ai-agents/config/:agentId`.
- Unauthorized users should be blocked by existing route/API authorization.

## Ask AI Buttons

Existing page placements:

- CRM record detail:
  - Lead opens `crm_lead_qualification`
  - Deal opens `crm_deal_analyzer`
  - Contact/account opens `crm_customer_summary`
  - Quotation opens a CRM analysis prompt
- PMS project detail opens `pms_project_status`.
- PMS task detail opens `pms_deadline_risk`.
- HRMS employee detail opens `hrms_letter_drafting`.
- HRMS leave page opens `hrms_leave_assistant`.
- HRMS attendance page opens `hrms_attendance_anomaly`.
- HRMS recruitment page opens `hrms_recruitment_screening`.

Expected behavior:

- Button fetches active agents from backend.
- Button navigates to `/ai-agents/chat/:agentId`.
- URL includes module and related record context when available.
- Chat page displays the context panel.
- Agent fetches actual record data only through backend tools.

## Security

Verify no frontend key exposure:

```powershell
rg -n "OPENAI_API_KEY|api\.openai\.com|openai" frontend\src frontend\public frontend\index.html
```

Expected: no matches.

Verify frontend build:

```powershell
cd frontend
npm run build
```

Expected: TypeScript and Vite build succeed.

## Known Limitations

- Chat uses non-streaming backend responses.
- Tool result JSON is available only in an explicitly expanded technical preview.
- The first version uses full chat-page navigation for Ask AI instead of an in-place drawer.
- Approval execution after approval remains a backend follow-up; this UI currently marks approval records approved/rejected through existing AI approval APIs.
