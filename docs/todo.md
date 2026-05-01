# AI HRMS TODO Backlog

Date: 2026-05-01

This is the realistic execution backlog derived from `docs/competitor_gap_analysis.md`. Each target is intentionally sliced small enough to build, test, and ship without destabilizing the whole ERP.

## Now

- [x] Create competitor gap analysis.
- [x] Target 1: Employee lifecycle history.
  - [x] Add lifecycle event data model and migration.
  - [x] Add APIs to create/list lifecycle events per employee.
  - [x] Capture current and previous values for auditable job/status/manager changes.
  - [x] Add focused API tests.
- [x] Target 2: Leave correctness foundation.
  - [x] Add leave balance ledger.
  - [x] Block overlapping pending/approved leave.
  - [x] Enforce available balance at application time.
  - [x] Add focused leave tests.
- [x] Target 3: Attendance computation foundation.
  - [x] Add weekly-off/roster model.
  - [x] Add late/early/short-hours fields.
  - [x] Add daily computation service.
  - [x] Add focused attendance tests.
- [x] Target 4: Payroll trust foundation.
  - [x] Enforce payroll lock across run, salary, component, structure, and reimbursement mutation APIs.
  - [x] Restrict employee payslip access to own records unless payroll-view permission is present.
  - [x] Add payroll variance summary before approval.
  - [x] Add statutory report export stubs for PF/ESI/PT/TDS, bank advice, and pay register.
  - [x] Add payroll run audit/export batch records.
  - [x] Add focused payroll tests.

## Next

- [x] Target 5: Payroll component lines and payslip detail.
  - [x] Persist earnings, deductions, employer contributions, and reimbursement component lines during payroll run.
  - [x] Return rich payslip payload with component groups.
  - [x] Add YTD gross, deduction, reimbursement, employer contribution, and net totals.
  - [x] Restrict attendance counting to the payroll month.
  - [x] Add focused payroll component tests.
- [x] Target 6: Scoped RBAC and sensitive data masking.
  - [x] Add sensitive employee field permission.
  - [x] Mask employee email, phone, address, personal, bank, and statutory identifiers for roles without sensitive access.
  - [x] Keep HR/admin access unmasked.
  - [x] Add focused RBAC masking tests.
- [x] Deployment routing foundation.
  - [x] Add DigitalOcean-ready MySQL configuration.
  - [x] Add runtime frontend API configuration.
  - [x] Remove hardcoded dev proxy backend target.
  - [x] Document split frontend/backend deployment.
- [ ] Target 7: Shared workflow/task inbox for approvals.
- [ ] Target 8: Notification inbox and email/SMS integration hooks.
- [ ] Target 9: Employee bulk import/export with row-level errors.
- [ ] Target 10: Leave calendar and team view.
- [ ] Target 11: Tax declarations and proof workflow.
- [ ] Target 12: Document expiry, verification, and policy versioning.
- [ ] Target 13: Helpdesk SLA, escalation, and knowledge base.

## Payroll Module Tasks

- [ ] Payroll setup.
  - [ ] Pay groups and payroll calendar.
  - [ ] State compliance rules for PT/LWF.
  - [ ] Bank advice format setup.
- [ ] Salary components and structures.
  - [ ] Component formula rules.
  - [ ] Payslip display grouping and sequence.
  - [ ] Structure versioning and monthly/annual CTC preview.
- [ ] Employee salary.
  - [ ] Salary revision requests.
  - [ ] Maker-checker salary approval.
  - [ ] Sensitive salary audit and masking.
- [ ] Payroll run.
  - [ ] Pre-run checks.
  - [x] Component-level payroll lines.
  - [x] Attendance/leave/LOP monthly attendance integration.
  - [ ] Bonus, arrears, incentives, and manual inputs.
  - [x] Variance and anomaly review.
  - [x] Approval and lock guardrails.
  - [ ] Unlock with reason.
- [ ] Payslip.
  - [x] Employee-scoped payslip.
  - [ ] PDF generation.
  - [x] YTD summary.
  - [ ] Bulk publish and email dispatch hook.
- [ ] Statutory and finance exports.
  - [x] PF ECR stub.
  - [x] ESI contribution stub.
  - [x] PT state report stub.
  - [x] TDS Form 24Q/Form 16 stubs.
  - [x] Bank advice stub.
  - [x] Pay register stub.
  - [ ] Accounting journal export.
- [ ] Tax declarations.
  - [ ] Declaration cycle.
  - [ ] Proof upload and verification.
  - [ ] TDS projection.
- [ ] Reimbursements.
  - [ ] Claim approval.
  - [ ] Payroll inclusion.
  - [ ] Reimbursement ledger.
- [ ] Loans and advances.
  - [ ] Loan master.
  - [ ] EMI schedule and payroll deduction.
  - [ ] Loan ledger.
- [ ] Full and final settlement.
  - [ ] Exit-linked settlement.
  - [ ] Leave encashment, notice recovery, gratuity, loan recovery.
  - [ ] Settlement letter.

## Industry Implementation Tracks

- [ ] Technology & Services.
  - [x] Project master and client/project allocation.
  - [x] Employee timesheets with billable/non-billable hours.
  - [x] Manager approval for submitted timesheets.
  - [ ] Project utilization and export reports.
- [ ] Pharma & Manufacturing.
  - [ ] Advanced shift roster and overtime classes.
  - [ ] Contract labor attendance and compliance document tracking.
  - [ ] Safety incident, PPE, and medical fitness records.
- [ ] Banks & Financial Services.
  - [ ] Regulatory certification tracking.
  - [ ] Maker-checker for sensitive master-data changes.
  - [ ] Policy attestations and evidence retention.
- [ ] Retail & Field Workforce.
  - [ ] Store hierarchy and staffing plan.
  - [ ] Geo-attendance and field visit logs.
  - [ ] Offline/mobile task capture.
- [ ] Healthcare Workforce.
  - [ ] Clinical credentials and license expiry alerts.
  - [ ] On-call roster and vaccination records.
- [ ] Education Workforce.
  - [ ] Faculty workload, course allocation, publications, and grants.

## Later

- [ ] Target 14: Mobile-first ESS/PWA polish.
- [ ] Target 15: Recruitment requisitions and candidate-to-employee conversion.
- [ ] Target 16: OKR check-ins, review templates, and 360 feedback.
- [ ] Target 17: LMS courses, assignments, and certifications.
- [ ] Target 18: Compensation cycles, pay bands, and merit planning.
- [ ] Target 19: Custom fields, forms, and workflow designer.
- [ ] Target 20: Webhooks and integration framework.
- [ ] Target 21: Report builder, scheduled exports, and governed metrics.
- [ ] Target 22: Engagement surveys, eNPS, recognition, and announcements.
- [ ] Target 23: Enterprise security: MFA, sessions, field audit, retention, privacy requests.

## Build Rule

Only one target moves through implementation at a time. A target is complete when it has database changes, API behavior, frontend where needed, permission checks, tests, and documentation status updates.
