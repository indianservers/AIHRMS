# AI Agents OpenAI Setup

The AI Agents chat engine uses the official OpenAI Python SDK from the backend only. The frontend never receives `OPENAI_API_KEY`.

## Required Environment Variables

Add these to `backend/.env`:

```env
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4.1-mini
AI_AGENT_DEFAULT_TEMPERATURE=0.2
AI_AGENT_MAX_TOOL_CALLS=8
AI_AGENT_ENABLE_STREAMING=false
AI_AGENT_AUDIT_LOGGING=true
```

`OPENAI_API_KEY` must not be added to frontend `.env` files.

## Install Dependency

The dependency is already declared in `backend/requirements.txt`:

```text
openai==1.35.10
```

Install backend dependencies if needed:

```powershell
cd backend
python -m pip install -r requirements.txt
```

## Start Backend

```powershell
cd backend
alembic upgrade head
python main.py
```

Startup seeds the AI agents and registered tools.

## Chat Endpoint

Effective path:

```text
POST /api/v1/ai-agents/{agentId}/chat
```

PowerShell setup:

```powershell
$token = "<ACCESS_TOKEN>"
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }
```

## Example 1: CRM Lead Qualification

```powershell
$body = @{
  message = "Analyze this lead and suggest next action."
  module = "CRM"
  related_entity_type = "lead"
  related_entity_id = "1"
} | ConvertTo-Json

Invoke-RestMethod -Method POST `
  -Uri "http://localhost:8000/api/v1/ai-agents/1/chat" `
  -Headers $headers `
  -Body $body
```

## Example 2: PMS Project Status

```powershell
$body = @{
  message = "Give me project status with blockers and risks."
  module = "PMS"
  related_entity_type = "project"
  related_entity_id = "1"
} | ConvertTo-Json

Invoke-RestMethod -Method POST `
  -Uri "http://localhost:8000/api/v1/ai-agents/5/chat" `
  -Headers $headers `
  -Body $body
```

## Example 3: HRMS Policy Assistant

```powershell
$body = @{
  message = "What is the leave policy for casual leave?"
  module = "HRMS"
} | ConvertTo-Json

Invoke-RestMethod -Method POST `
  -Uri "http://localhost:8000/api/v1/ai-agents/9/chat" `
  -Headers $headers `
  -Body $body
```

## Example 4: Business Summary

```powershell
$body = @{
  message = "Give me today's business summary across CRM, PMS, and HRMS."
  module = "CROSS"
} | ConvertTo-Json

Invoke-RestMethod -Method POST `
  -Uri "http://localhost:8000/api/v1/ai-agents/14/chat" `
  -Headers $headers `
  -Body $body
```

Agent IDs can vary by database. Use `GET /api/v1/ai-agents` and select by `code`.

## Expected Success Response

```json
{
  "success": true,
  "conversation_id": 12,
  "agent_id": 1,
  "message": "Here is the lead analysis...",
  "tool_calls": [
    {
      "tool_name": "crm_get_lead",
      "success": true,
      "requires_approval": false,
      "approval_id": null
    }
  ],
  "approvals": [],
  "suggested_actions": []
}
```

## Expected Approval Response

```json
{
  "success": true,
  "conversation_id": 13,
  "agent_id": 2,
  "message": "I prepared the proposed action. Please review and approve it before execution.",
  "approvals": [
    {
      "approval_id": 7,
      "action_type": "crm_create_followup_task_draft",
      "module": "CRM",
      "proposed_action": {}
    }
  ]
}
```

Approval records do not execute final CRM, HRMS, or PMS actions in this step.

## Common Errors

### Missing API Key

```json
{
  "success": false,
  "error_code": "OPENAI_API_KEY_MISSING",
  "message": "The AI service is not configured. Please add OPENAI_API_KEY on the backend."
}
```

Fix: set `OPENAI_API_KEY` in `backend/.env` and restart the backend.

### SDK Missing

```json
{
  "success": false,
  "error_code": "OPENAI_SDK_MISSING",
  "message": "The OpenAI SDK is not installed in the backend environment."
}
```

Fix:

```powershell
cd backend
python -m pip install -r requirements.txt
```

### Tool Permission Denied

The selected user or agent is not allowed to use the requested tool. Confirm the user role permissions and the tool's `allowed_agent_codes`.

### Service Method Missing

Some cross-module functionality, such as aggregated alerts, requires mapping to an existing service before use.
