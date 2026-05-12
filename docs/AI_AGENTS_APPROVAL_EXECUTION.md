# AI Agents Approval Execution

## How It Works

AI tools create `ai_action_approvals` for risky proposed actions. When a user approves an action, the backend now:

1. Loads the pending approval.
2. Confirms the current user can approve it.
3. Resolves the action type to a supported first-release action.
4. Revalidates the proposed action JSON.
5. Rechecks the required permission.
6. Executes only through AI adapters backed by existing CRM, PMS, and HRMS models/services.
7. Marks the approval as `approved` only after execution succeeds.
8. Stores `executed_at` and `execution_result_json`.
9. Writes audit logs for success, failure, and permission denial.

If execution fails, the approval is marked `failed` with an execution result. Permission denial keeps the approval pending and returns HTTP 403.

## Supported Action Types

- `CREATE_CRM_FOLLOWUP_TASK`
- `UPDATE_CRM_LEAD_SCORE_STATUS`
- `CREATE_CRM_DRAFT_MESSAGE`
- `CREATE_PMS_TASK`
- `CREATE_PMS_SUBTASK`
- `CREATE_PMS_RISK_LOG`
- `CREATE_HRMS_LEAVE_REQUEST`
- `CREATE_HRMS_ATTENDANCE_ALERT`
- `CREATE_HRMS_LETTER_DRAFT`
- `SAVE_CANDIDATE_SCREENING_SUMMARY`

Legacy tool action aliases such as `pms.create_task` and `hrms.create_leave_request` are mapped to these first-release action types.

## Unsupported Actions

These remain blocked in the first release:

- Delete CRM/HRMS/PMS records
- Send external emails, WhatsApp, or SMS
- Final approve/reject leave
- Change salary
- Modify attendance directly
- Terminate employee
- Issue final warning letters
- Close deals
- Change project deadlines
- Reassign critical project owners
- Change invoices, payments, or accounting records

Unsupported actions return `ACTION_NOT_SUPPORTED_IN_FIRST_RELEASE`.

## Permission Checks

The executor uses the existing user/role permissions available on the authenticated user. Current mappings:

- CRM follow-up/update/draft: `crm_manage`
- PMS task/subtask/risk: `pms_manage_tasks`
- HRMS leave request: `leave_apply`
- HRMS attendance alert: `attendance_view`
- HRMS letter draft: `employee_documents_manage`
- Candidate screening summary: `recruitment_manage`

These mappings should be aligned with the final RBAC naming if the production roles use different permission labels.

## Adding A New Approved Action Safely

1. Add the action to `ACTION_DEFINITIONS` in `backend/app/ai_agents/services/approval_executor.py`.
2. Map it to an adapter execution method.
3. Add required fields and permission.
4. Validate target record access inside the adapter.
5. Execute through existing module service/model logic only.
6. Never send external messages or mutate critical records without a separate explicit flow.
7. Add QA cases and update this document.
