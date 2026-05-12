# AI Agents Security

## API Key Handling

- `OPENAI_API_KEY` is read by the backend OpenAI service only.
- The frontend calls only `/api/v1/ai-agents/...`.
- No frontend code references `OPENAI_API_KEY` or calls `api.openai.com`.

## Tool Registry Security

- AI cannot access the database directly.
- AI cannot run generated SQL.
- AI can only request tools registered in `AiToolRegistryService`.
- Every tool call goes through `AiToolExecutionService`.
- Tool execution validates agent permission, user permission, input schema, active status, and approval requirements.

## Approval Workflow

- Risky tools create `ai_action_approvals`.
- Approval execution revalidates proposed JSON and permissions.
- Supported first-release actions execute only through adapters backed by existing CRM, PMS, and HRMS services/models.
- Unsupported critical actions remain blocked.

## RBAC And Tenant Isolation

- AI endpoints require the existing authenticated user.
- Conversations and approvals are scoped to the current user unless the user is superuser.
- Adapters reuse existing project/employee/module access helpers where available.
- PMS project/task access uses project-management access helpers.
- HRMS employee access uses the existing employee manager/self/HR permission model in the adapter.

## Sensitive Data Masking

- HRMS employee responses mask account/Aadhaar/PAN-style identifiers.
- Salary and bank fields are removed unless payroll/salary permissions are present.
- Medical/confidential employee fields are removed.
- PMS comments are truncated before tool results are sent to OpenAI.
- Conversation history is limited to recent messages.

Known limitation: CRM/PMS/HRMS field-level masking should be expanded if the application adds more confidential fields or more granular RBAC.

## Prompt Injection Protection

- System prompts label CRM notes, HR records, project comments, resumes, emails, uploaded files, and database text as untrusted.
- Tool results sent back to OpenAI are prefixed with `UNTRUSTED_BACKEND_TOOL_RESULT`.
- The AI is instructed to ignore instructions embedded in business records.
- The AI is instructed not to reveal prompts, API keys, tool schema internals, backend details, or security policies.

## Rate Limiting

- AI chat and tool-test endpoints have in-memory per-user hourly limits.
- Normal users: 30 AI messages/tool tests per hour.
- Admin/developer/superuser: 100 per hour.
- Advanced usage limits can additionally be configured per user, agent, company, or module in `ai_usage_limits`.

Production recommendation: replace or augment the in-memory limiter with Redis/platform-level distributed rate limiting for multi-instance deployments.

## Advanced Controls

- Permission matrix rules live in `ai_agent_permissions`; user rules override role rules.
- Emergency kill switches live in `ai_security_settings` and are checked before chat/tool execution.
- Prompt injection scanning blocks critical prompts and disables tool execution for high-risk prompts.
- Tool results are sanitized and redacted before being sent back to the model.
- Assistant responses are scanned before being returned to the frontend.
- Conversation exports redact tool results and message text before file generation.
- Approval replay protection uses `execution_status` and blocks duplicate execution.

## Audit Logging

Audit logs are written for:

- AI chat start
- User message save
- OpenAI request metadata
- Tool call request
- Tool execution success/failure
- Approval creation
- Approval execution success/failure
- Approval rejection
- Permission denial
- Rate limit exceeded

Audit logs do not store API keys and should avoid storing unnecessary sensitive HR/customer data.
