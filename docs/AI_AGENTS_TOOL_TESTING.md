# AI Agents Tool Testing

All examples use the backend test endpoint:

```text
POST /api/v1/ai-agents/tools/test
```

PowerShell setup:

```powershell
$token = "<ACCESS_TOKEN>"
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }
```

The endpoint is admin/developer-only and returns the standard tool execution response.

## CRM Tools

### crm_get_lead

```powershell
$body = @{
  agent_code = "crm_lead_qualification"
  tool_name = "crm_get_lead"
  input = @{ lead_id = 1 }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

### crm_search_duplicate_leads

```powershell
$body = @{
  agent_code = "crm_lead_qualification"
  tool_name = "crm_search_duplicate_leads"
  input = @{ email = "customer@example.com"; mobile = "9999999999" }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

### crm_get_deal

```powershell
$body = @{
  agent_code = "crm_deal_analyzer"
  tool_name = "crm_get_deal"
  input = @{ deal_id = 1 }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

### crm_create_followup_task_draft

```powershell
$body = @{
  agent_code = "crm_followup"
  tool_name = "crm_create_followup_task_draft"
  input = @{
    related_entity_type = "lead"
    related_entity_id = 1
    title = "Follow up on product demo"
    description = "Call and confirm demo availability."
    due_date = "2026-05-15"
    priority = "high"
  }
  related_entity_type = "lead"
  related_entity_id = "1"
} | ConvertTo-Json -Depth 6

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

Expected behavior: creates an `ai_action_approvals` pending record and does not create a CRM task.

## PMS Tools

### pms_get_project

```powershell
$body = @{
  agent_code = "pms_project_status"
  tool_name = "pms_get_project"
  input = @{ project_id = 1 }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

### pms_get_project_tasks

```powershell
$body = @{
  agent_code = "pms_project_status"
  tool_name = "pms_get_project_tasks"
  input = @{ project_id = 1; status = "In Progress" }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

### pms_get_delayed_tasks

```powershell
$body = @{
  agent_code = "pms_deadline_risk"
  tool_name = "pms_get_delayed_tasks"
  input = @{ project_id = 1 }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

### pms_create_task_draft

```powershell
$body = @{
  agent_code = "pms_task_planning"
  tool_name = "pms_create_task_draft"
  input = @{
    project_id = 1
    title = "Prepare launch checklist"
    description = "Draft and review launch checklist."
    assignee_id = 2
    due_date = "2026-05-20"
    priority = "high"
  }
  related_entity_type = "project"
  related_entity_id = "1"
} | ConvertTo-Json -Depth 6

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

Expected behavior: creates an approval record and does not create a PMS task.

## HRMS Tools

### hrms_get_employee

```powershell
$body = @{
  agent_code = "hrms_leave_assistant"
  tool_name = "hrms_get_employee"
  input = @{ employee_id = 1 }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

### hrms_get_leave_balance

```powershell
$body = @{
  agent_code = "hrms_leave_assistant"
  tool_name = "hrms_get_leave_balance"
  input = @{ employee_id = 1 }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

### hrms_search_policy

```powershell
$body = @{
  agent_code = "hrms_policy_assistant"
  tool_name = "hrms_search_policy"
  input = @{ query = "leave policy" }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

### hrms_generate_letter_draft

```powershell
$body = @{
  agent_code = "hrms_letter_drafting"
  tool_name = "hrms_generate_letter_draft"
  input = @{
    employee_id = 1
    letter_type = "experience"
    extra_details = @{ purpose = "Employee request" }
  }
  related_entity_type = "employee"
  related_entity_id = "1"
} | ConvertTo-Json -Depth 6

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

Expected behavior: creates an approval record and does not issue a letter.

## Cross-Module Tools

### cross_get_business_summary

```powershell
$body = @{
  agent_code = "business_summary"
  tool_name = "cross_get_business_summary"
  input = @{ from_date = "2026-05-01"; to_date = "2026-05-31" }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

### cross_safe_search_crm

```powershell
$body = @{
  agent_code = "smart_search"
  tool_name = "cross_safe_search_crm"
  input = @{ query = "Acme"; limit = 10 }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

### cross_get_alerts

```powershell
$body = @{
  agent_code = "smart_notification"
  tool_name = "cross_get_alerts"
  input = @{ module = "CRM"; severity = "high" }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method POST -Uri "http://localhost:8000/api/v1/ai-agents/tools/test" -Headers $headers -Body $body
```

Expected behavior until an existing alert aggregation service is mapped:

```json
{
  "success": false,
  "error_code": "SERVICE_METHOD_MISSING",
  "message": "Required existing module service method is not available yet.",
  "missing_method": "existing_alert_aggregation_service"
}
```
