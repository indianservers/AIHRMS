# AI Agents Integration Plan

## Scope

AI Agents are implemented as a separate feature layer over the existing CRM, HRMS, and PMS modules. The integration does not create replacement CRM/HRMS/PMS services or dummy business data.

## Architecture

1. Backend AI module exposes `/api/v1/ai-agents`.
2. OpenAI is called only from backend service code.
3. Agent orchestration loads agent config, builds a guarded prompt, exposes allowed tools, and saves conversation history.
4. Tool calls go through the safe tool registry and execution service.
5. CRM, HRMS, PMS, and cross-module adapters call existing models/services/access helpers.
6. Risky actions create approval records.
7. Approval execution revalidates permissions and executes only supported first-release actions.
8. Frontend calls backend AI APIs only and adds Ask AI entry points to existing pages.

## Implemented Phases

- Foundation tables, models, APIs, seeds, conversations, approvals, logs.
- Safe adapters and tool registry.
- OpenAI service and tool-calling orchestrator.
- Frontend dashboard, chat, approvals, logs, config, and Ask AI buttons.
- Approval execution, rate limiting, prompt-injection hardening, masking, QA docs.

## Production Gate

Before enabling broadly:

1. Apply Alembic migrations.
2. Verify AI seed agents/tools are present.
3. Configure `OPENAI_API_KEY` only in backend secrets.
4. Run `docs/AI_AGENTS_FINAL_QA.md`.
5. Review `docs/AI_AGENTS_PRODUCTION_CHECKLIST.md`.
