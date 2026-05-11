# AI Agents Backend

The AI Agents module is a backend AI assistant layer across CRM, HRMS, and PMS.

It stores agent configuration, conversations, messages, approvals, audit logs, company-level settings, uses safe adapters/tools for product data, and calls OpenAI from the backend only.

## Backend Structure

- `app.ai_agents.api` exposes `/api/v1/ai-agents/*`.
- `AiAgentRegistryService` seeds and lists the initial 16 AI agent configuration records.
- `AiConversationService` provides basic conversation/message persistence helpers.
- `AiApprovalService` stores and updates AI approval records. Approving currently marks a proposal as approved only.
- `AiAuditService` records AI foundation actions.
- `AiAgentSettingsService` stores company-scoped agent settings.
- `CrmAiAdapter`, `HrmsAiAdapter`, `PmsAiAdapter`, and `CrossModuleAiAdapter` read from existing product modules without creating duplicate product APIs.
- `AiToolRegistryService` registers safe tool metadata.
- `AiToolExecutionService` validates tool calls, checks agent/tool permissions, routes to adapters, and creates AI approvals for risky tools.
- `OpenAiService` wraps the official OpenAI SDK and normalizes responses/tool calls.
- `AiAgentOrchestratorService` runs the chat loop, saves messages, calls OpenAI, executes safe tools, records approvals, and saves final assistant responses.

## Database Tables

- `ai_agents`
- `ai_agent_tools`
- `ai_conversations`
- `ai_messages`
- `ai_action_approvals`
- `ai_audit_logs`
- `ai_agent_settings`

The `ai_agent_tools` table stores active tool availability per agent. Tool metadata is seeded from the safe registry.

## Seeding

The backend seeds the 16 initial agent configuration records on application startup through `AiAgentRegistryService.ensure_seed_data()`.

These records are AI configuration only. They are not CRM, HRMS, or PMS sample data.

## Security Notes

- All endpoints use the existing authentication dependency.
- No OpenAI API key is exposed to the frontend.
- No frontend AI Agents code is included in this foundation step.
- Conversations are scoped to the creating user.
- Pending approvals are scoped to the current user unless the user is a superuser.
- Company settings use the current user's organization/company context when available.
- The temporary AI access check should be mapped to the full RBAC permission system in a later step.

## Future Steps

1. Map `cross_get_alerts` to an existing alert aggregation service when one is available.
2. Add frontend pages and Ask AI buttons after the backend integration is stable.
3. Add streaming after non-streaming chat is verified in production-like environments.
