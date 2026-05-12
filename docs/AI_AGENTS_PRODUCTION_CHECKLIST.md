# AI Agents Production Checklist

## Environment

- `OPENAI_API_KEY` configured in backend environment only.
- `OPENAI_MODEL` configured.
- `AI_AGENT_DEFAULT_TEMPERATURE` configured.
- `AI_AGENT_MAX_TOOL_CALLS` configured.
- `AI_AGENT_ENABLE_STREAMING=false` unless streaming is intentionally implemented.
- `AI_AGENT_AUDIT_LOGGING=true`.

## Database

- `alembic upgrade head` applied.
- AI seed agents and tools verified.
- `ai_action_approvals.executed_at` and `execution_result_json` columns exist.

## Security

- Frontend bundle contains no OpenAI API key.
- Browser makes no direct OpenAI API calls.
- RBAC permissions mapped to production role names.
- AI permission matrix configured for production roles/users.
- Emergency global and module kill switches tested.
- Tenant/company scoping verified.
- Sensitive HR data masking verified.
- Export redaction verified.
- Prompt injection tests completed.
- Response safety filter tested.
- Unsupported critical actions remain blocked.

## Rate Limiting

- In-memory limiter enabled for AI chat and tool-test endpoints.
- Database usage limits configured for company/user/agent/module needs.
- Distributed rate limiter configured for multi-instance production deployment, or deployment is confirmed single-instance.
- Tool test endpoint restricted to admin/developer users.

## Performance

- Conversation history limited.
- Tool calls capped by `AI_AGENT_MAX_TOOL_CALLS`.
- Large comments/records truncated before model context.
- OpenAI timeout and error handling verified.

## Operations

- Admin can disable an AI agent.
- Admin can disable all AI or module-specific AI.
- Admin can review pending approvals.
- Admin can view audit logs.
- Admin can review security events, feedback, usage, cost, and handoff notes.
- Failed approval executions are traceable.
- Approval replay protection tested by approving the same request twice.
- Error monitoring/log shipping captures backend AI failures.

## Compliance

- HR data minimized before model calls.
- Customer data minimized before model calls.
- Audit logs do not contain API keys.
- Approval execution logs include enough detail for traceability without storing unnecessary sensitive data.

## Release Gate

Before production enablement:

1. Run `docs/AI_AGENTS_FINAL_QA.md`.
2. Verify production RBAC names match `approval_executor.py` mappings.
3. Verify a real OpenAI key is configured only in backend secrets.
4. Verify AI Agents menu visibility follows production permissions.
5. Confirm business owners accept first-release supported/unsupported action list.
