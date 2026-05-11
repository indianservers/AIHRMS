# AI Agents API Testing

All examples assume the backend is running at `http://localhost:8000` and the existing API prefix is `/api/v1`.

Set an access token first:

```powershell
$token = "<ACCESS_TOKEN>"
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }
```

## List Agents

```powershell
Invoke-RestMethod -Method GET `
  -Uri "http://localhost:8000/api/v1/ai-agents" `
  -Headers $headers
```

Sample response:

```json
[
  {
    "id": 1,
    "name": "Lead Qualification Agent",
    "code": "crm_lead_qualification",
    "module": "CRM",
    "description": "Analyzes CRM leads, scores them, classifies them, and suggests next action.",
    "model": null,
    "temperature": 0.2,
    "is_active": true,
    "requires_approval": true
  }
]
```

## Create Conversation

```powershell
$body = @{
  agent_id = 1
  module = "CRM"
  title = "Lead review"
  related_entity_type = "lead"
  related_entity_id = "123"
} | ConvertTo-Json

Invoke-RestMethod -Method POST `
  -Uri "http://localhost:8000/api/v1/ai-agents/conversations" `
  -Headers $headers `
  -Body $body
```

Sample response:

```json
{
  "id": 10,
  "user_id": 5,
  "agent_id": 1,
  "module": "CRM",
  "title": "Lead review",
  "related_entity_type": "lead",
  "related_entity_id": "123",
  "status": "active",
  "created_at": "2026-05-12T10:00:00",
  "updated_at": null
}
```

## Save Message

```powershell
$body = @{ content = "Please summarize this lead when the AI engine is connected." } | ConvertTo-Json

Invoke-RestMethod -Method POST `
  -Uri "http://localhost:8000/api/v1/ai-agents/conversations/10/messages" `
  -Headers $headers `
  -Body $body
```

Sample response:

```json
{
  "conversation_id": 10,
  "message_id": 25,
  "response": "AI engine is not connected yet. Message saved successfully."
}
```

## List Pending Approvals

```powershell
Invoke-RestMethod -Method GET `
  -Uri "http://localhost:8000/api/v1/ai-agents/approvals/pending" `
  -Headers $headers
```

Sample response:

```json
[]
```

## Approve Approval

```powershell
Invoke-RestMethod -Method POST `
  -Uri "http://localhost:8000/api/v1/ai-agents/approvals/1/approve" `
  -Headers $headers
```

Sample response:

```json
{
  "id": 1,
  "status": "approved",
  "approved_by": 5,
  "approved_at": "2026-05-12T10:15:00"
}
```

This only marks the approval as approved. It does not execute CRM, HRMS, or PMS actions yet.

## Reject Approval

```powershell
$body = @{ rejected_reason = "Needs manager review first." } | ConvertTo-Json

Invoke-RestMethod -Method POST `
  -Uri "http://localhost:8000/api/v1/ai-agents/approvals/1/reject" `
  -Headers $headers `
  -Body $body
```

Sample response:

```json
{
  "id": 1,
  "status": "rejected",
  "rejected_reason": "Needs manager review first."
}
```

## View Audit Logs

```powershell
Invoke-RestMethod -Method GET `
  -Uri "http://localhost:8000/api/v1/ai-agents/logs" `
  -Headers $headers
```

Sample response:

```json
[
  {
    "id": 1,
    "user_id": 5,
    "agent_id": null,
    "module": "CROSS",
    "action": "agent.list_viewed",
    "status": "success",
    "related_entity_type": null,
    "related_entity_id": null,
    "input_json": { "module": null },
    "output_json": { "count": 16 },
    "created_at": "2026-05-12T10:05:00"
  }
]
```
