# AI Agents Advanced Features

## Added Features

- Usage limits per company, user, agent, and module.
- Usage event and token/cost tracking.
- Agent permission matrix with user-specific overrides over role rules.
- Data access scope values: `own_records`, `team_records`, `department_records`, `company_records`, `custom`.
- Prompt injection scanning for user prompts, business context, and tool results.
- Sensitive data redaction before AI context, frontend tool previews, and exports.
- AI response safety filter before returning assistant output.
- Conversation export in JSON, CSV, and PDF.
- Message feedback with thumbs up/down and feedback category.
- Agent analytics and cost dashboards.
- Admin security dashboard with kill switches.
- Human handoff notes.
- Approval replay protection via execution status/idempotency fields.

## Database Tables Added

- `ai_usage_limits`
- `ai_usage_events`
- `ai_agent_permissions`
- `ai_security_settings`
- `ai_cost_logs`
- `ai_message_feedback`
- `ai_handoff_notes`

`ai_action_approvals` was extended with execution replay fields:

- `execution_status`
- `execution_error`
- `idempotency_key`

## APIs Added

- `GET /api/ai-agents/security/summary`
- `GET /api/ai-agents/security/events`
- `GET /api/ai-agents/security/settings`
- `PUT /api/ai-agents/security/settings`
- `GET /api/ai-agents/security/permissions`
- `PUT /api/ai-agents/security/permissions`
- `GET /api/ai-agents/usage/summary`
- `GET /api/ai-agents/usage/limits`
- `PUT /api/ai-agents/usage/limits`
- `GET /api/ai-agents/analytics/summary`
- `GET /api/ai-agents/analytics/by-agent`
- `GET /api/ai-agents/analytics/by-module`
- `GET /api/ai-agents/analytics/by-user`
- `GET /api/ai-agents/analytics/cost`
- `POST /api/ai-agents/messages/:messageId/feedback`
- `GET /api/ai-agents/feedback`
- `GET /api/ai-agents/conversations/:id/export?format=json|csv|pdf`
- `POST /api/ai-agents/handoff-notes`
- `GET /api/ai-agents/handoff-notes`
- `PATCH /api/ai-agents/handoff-notes/:id/status`

## Frontend Pages Added

- `/ai-agents/analytics`
- `/ai-agents/usage`
- `/ai-agents/security`
- `/ai-agents/security/permissions`
- `/ai-agents/feedback`
- `/ai-agents/handoff`

The AI Agents sidebar now includes Analytics, Usage, Security, Permissions, Feedback, and Handoff Notes.

## Security Controls

- The backend checks global/module kill switches before chat/tool execution.
- The backend checks the permission matrix before agent use, approval, logs, and export.
- Prompt injection detection blocks critical prompts and prevents tool execution for high-risk prompts.
- Tool results are labelled as untrusted business data and sanitized/redacted before model reuse.
- Response safety filtering blocks prompt/key disclosure, SQL snippets, and unsafe completion claims.
- Conversation exports redact secrets and sensitive fields.
- Approval execution uses execution status to block double execution.

## Configuration Notes

Usage limits are configured at `/ai-agents/usage`.

Permission rules are configured at `/ai-agents/security/permissions`.

Emergency kill switches are configured at `/ai-agents/security`.

Cost tracking stores model token usage when OpenAI returns usage metadata. Estimated cost is populated for models configured in `AiCostTrackingService.MODEL_PRICING`; otherwise token counts are still stored.

## Known Limitations

- Data access scope is passed through the AI tool layer and enforced through existing adapters and module permissions. More granular field/record scope rules should be mapped as CRM/PMS/HRMS RBAC matures.
- PDF export is intentionally simple and redacted; use the JSON export for complete audit review.
- Usage limits are database-backed for AI usage limits, while the older per-hour endpoint limiter remains in-memory.
