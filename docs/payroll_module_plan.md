# Payroll Module Plan

Date: 2026-05-01

Goal: Build a realistic India-ready payroll module comparable to Keka, greytHR, Zoho Payroll, Darwinbox, and enterprise HRMS suites, while keeping each implementation slice small enough to ship safely.

## Current Coverage

- Salary component master exists.
- Salary structure master exists.
- Employee salary assignment exists.
- Payroll run generation exists.
- Payroll records and payslip retrieval exist.
- Basic PF, ESI, PT, LOP, gross/net calculation exists.
- Payroll approval and lock status fields exist.
- Reimbursement capture exists.
- AI anomaly service stub exists.

## Critical Gaps

- Payroll lock is not enforced across all mutation APIs.
- Payslip access is not strictly scoped when `employee_id` is passed.
- Salary revisions do not have approval or audit history.
- Payroll run does not run pre-checks for missing salary, attendance lock, pending reimbursements, or declaration readiness.
- Statutory calculations are simplified and not policy/table driven.
- Payroll variance is not exposed before approval.
- No payroll component line items are persisted for payslip detail.
- No statutory export, bank advice, or pay register export.
- No tax declaration/proof workflow.
- No loans, salary advances, arrears, bonuses, incentives, or F&F settlement.
- No payroll unlock workflow with reason and audit.

## Feature Scope

### 1. Payroll Setup

- Pay groups: monthly, weekly, contractor, consultant.
- Payroll calendar: cutoff dates, run date, payout date, attendance freeze date.
- Legal entity and branch mapping.
- State compliance mapping for PT, LWF, and local rules.
- Bank master for salary advice format.
- Payroll roles: payroll viewer, payroll processor, payroll approver, finance approver, auditor.

### 2. Salary Component Master

- Component types: earning, deduction, employee statutory deduction, employer statutory contribution, reimbursement, memo component.
- Standard earnings: Basic, HRA, DA, Conveyance, Medical Allowance, Special Allowance, LTA, Bonus, Variable Pay, Incentive, Arrear, Leave Encashment.
- Standard deductions: PF Employee, ESI Employee, PT, TDS, LOP Deduction, Loan EMI, Advance Recovery, Notice Pay Recovery.
- Employer contributions: PF Employer, EPS, EDLI, ESI Employer, Gratuity Provision, Bonus Provision, LWF Employer.
- Calculation modes: fixed, percentage of component, percentage of CTC, slab, formula.
- Tax flags: taxable, non-taxable, exemption eligible, proof required.
- Payslip flags: show/hide, display group, sort order, YTD visibility.
- Rounding rule per component.
- GL code/cost center mapping.

### 3. Salary Structures

- Grade/band-specific salary structures.
- CTC-to-monthly breakup template.
- Annual and monthly view.
- Formula validation before activation.
- Structure effective date and versioning.
- Structure clone/revise workflow.
- Employee preview: gross, deductions, employer cost, net salary.

### 4. Employee Salary Assignment

- Assign structure, CTC, effective date, pay group, and payout bank.
- Salary revision with old/new CTC, increment percentage, reason, effective date.
- Backdated revision support with arrear calculation.
- Maker-checker approval for salary assignment/revision.
- Salary history and audit trail.
- Sensitive salary data permission and masking.
- Increment letter generation hook.

### 5. Attendance And Leave Inputs

- Attendance lock/freeze before payroll run.
- Paid days, unpaid days, LOP, weekly off, holiday, half day, WFH, OD, and comp-off handling.
- Leave encashment input from leave balances.
- Overtime input from attendance/roster.
- Late/early penalty input when policy enables it.
- Manual payroll input adjustment with reason and audit.

### 6. Tax Declarations And Proofs

- IT declaration window configuration.
- Employee declaration categories: 80C, 80D, HRA, home loan, NPS, donations, other exemptions.
- Proposed declaration and actual proof phase.
- Document upload per declaration line.
- HR/Finance verification with notes.
- TDS projection based on verified amounts.
- Monthly TDS spread across remaining months.
- Form 16 annual summary stub.

### 7. Payroll Run

- Run by month/year/pay group/legal entity/branch.
- Pre-run checks:
  - Active employees have salary assignment.
  - Attendance is locked or explicitly waived.
  - Exit/F&F employees are identified.
  - Approved reimbursements are included.
  - Pending salary revisions are blocked.
  - Tax declarations are processed or marked skipped.
- Payroll calculation:
  - Proration for joiners/exits.
  - LOP deduction.
  - Fixed earnings.
  - Formula earnings.
  - Bonus/incentive/arrear.
  - Reimbursements.
  - PF/ESI/PT/TDS/LWF/gratuity.
  - Loans and advances.
- Persist component-level payroll lines.
- Re-run allowed only before approval/lock.
- Run totals: gross, deductions, employer contribution, reimbursements, net, employee count.

### 8. Payroll Review, Approval, And Lock

- Pre-payroll summary dashboard.
- Variance report versus previous month:
  - Gross variance threshold.
  - Net variance threshold.
  - Deduction variance threshold.
  - Missing salary or zero net flags.
  - Negative salary hard block.
- AI anomaly detection results linked to run.
- Approver comments.
- Approval action by finance/payroll approver.
- Lock after approval.
- Unlock requires reason, privileged permission, and audit entry.
- No salary/reimbursement/run mutation after lock unless unlocked.

### 9. Payslip

- Employee self-service payslip with own-record scoping.
- HR/Finance payslip view by employee.
- Earnings, deductions, reimbursements, employer contribution, YTD summary.
- PDF generation with company branding.
- Password-protected PDF option.
- Bulk publish payslips.
- Email dispatch queue hook.
- Download audit.

### 10. Reimbursements

- Employee reimbursement claim.
- Receipt upload.
- Category policy limits.
- Approval workflow.
- Payroll inclusion month.
- Taxable/non-taxable flag.
- Paid status linked to payroll record.
- Reimbursement ledger.

### 11. Loans And Advances

- Employee loan master.
- Loan approval.
- EMI schedule.
- Auto-deduction during payroll.
- Foreclosure and waiver.
- Advance salary request and recovery.
- Loan ledger and outstanding balance.

### 12. Statutory Reports And Exports

- PF ECR export stub.
- ESI contribution export stub.
- PT state-wise report.
- TDS Form 24Q data stub.
- Form 16 annual certificate stub.
- LWF report.
- Gratuity provision report.
- Pay register.
- Bank advice file.
- Accounting journal export.
- Component-wise payroll cost report.

### 13. Full And Final Settlement

- Trigger from exit module.
- Last working day proration.
- Notice period recovery/payout.
- Leave encashment.
- Gratuity eligibility calculation.
- Bonus/incentive proration.
- Asset/reimbursement/loan recovery inputs.
- Settlement approval.
- F&F payslip and settlement letter.

### 14. Security And Audit

- Payroll data masking by role.
- Field audit for salary, bank, PAN, Aadhaar, tax, and payroll changes.
- Privileged re-authentication for approval, lock, unlock, salary revision, bank change.
- Segregation of duties: maker cannot approve own salary revision or payroll run.
- Export audit logs.
- Payroll period close logs.

## Database Additions

- `pay_groups`
- `payroll_calendars`
- `payroll_state_rules`
- `salary_component_rules`
- `salary_revision_requests`
- `payroll_inputs`
- `payroll_run_checks`
- `payroll_variance_items`
- `payroll_run_audit_logs`
- `payroll_unlock_requests`
- `payroll_payslips`
- `payroll_export_batches`
- `tax_declaration_cycles`
- `tax_declaration_items`
- `tax_proof_documents`
- `employee_loans`
- `employee_loan_schedule`
- `employee_loan_ledger`
- `full_and_final_settlements`

## API Plan

- `GET/POST /payroll/pay-groups`
- `GET/POST /payroll/calendars`
- `GET/POST /payroll/components`
- `GET/POST /payroll/structures`
- `POST /payroll/salary`
- `POST /payroll/salary-revisions`
- `PUT /payroll/salary-revisions/{id}/approve`
- `POST /payroll/run`
- `GET /payroll/runs`
- `GET /payroll/runs/{id}`
- `GET /payroll/runs/{id}/checks`
- `GET /payroll/runs/{id}/variance`
- `PUT /payroll/runs/{id}/approve`
- `PUT /payroll/runs/{id}/lock`
- `POST /payroll/runs/{id}/unlock-request`
- `PUT /payroll/unlock-requests/{id}/approve`
- `GET /payroll/runs/{id}/records`
- `GET /payroll/runs/{id}/exports/{type}`
- `GET /payroll/payslip`
- `GET /payroll/payslip/{record_id}/pdf`
- `POST /payroll/reimbursements`
- `PUT /payroll/reimbursements/{id}/approve`
- `GET/POST /payroll/tax-declarations`
- `PUT /payroll/tax-declarations/{id}/verify`
- `GET/POST /payroll/loans`
- `POST /payroll/fnf`

## Frontend Plan

- Payroll overview: current run, blockers, monthly totals, approval state.
- Setup tab: components, structures, pay groups, calendars, state rules.
- Salary tab: employee salary assignment and revision history.
- Run tab: create run, pre-checks, records, variance, anomalies.
- Payslip tab: employee own payslip and HR employee lookup.
- Reimbursements tab: claims, approvals, payroll inclusion status.
- Tax tab: declarations, proof upload, verification.
- Loans tab: loan schedule, EMI, ledger.
- Exports tab: PF, ESI, PT, TDS, bank advice, pay register.
- F&F tab: exit-linked settlement calculations.
- Audit tab: lock/unlock, exports, sensitive changes.

## Implementation Tasks

### Target 4A: Payroll Trust Foundation

- Enforce payroll lock on run, salary, component, structure, and reimbursement mutation APIs.
- Add strict payslip self-service scoping.
- Add payroll variance endpoint.
- Add export batch model and statutory export stubs.
- Add focused tests for locked mutation, variance, exports, and payslip access.

### Target 4B: Component Lines And Payslip Detail

- Persist payroll component lines during run.
- Add earnings/deductions/employer contribution grouping in payslip response.
- Add YTD summary.
- Update frontend payslip detail.

### Target 4C: Pre-Run Checks

- Add payroll run check table.
- Block approval when critical checks fail.
- Add missing salary, attendance lock, pending revision, and negative salary checks.
- Show checks in frontend.

### Target 4D: Statutory Rule Tables

- Add state PT/LWF rules.
- Add PF/ESI rule configuration.
- Replace hardcoded statutory calculations with rule service.

### Target 4E: Salary Revision Approval

- Add salary revision request table.
- Implement maker-checker approval.
- Apply approved revision to employee salary history.

### Target 4F: Tax Declarations

- Add declaration cycles, items, proof documents, verification.
- Add TDS projection stub.
- Include monthly TDS in payroll run.

### Target 4G: Reimbursements And Payroll Inputs

- Add reimbursement approval.
- Include approved unpaid reimbursements in payroll run.
- Add manual payroll input table for bonus, incentive, recovery, and arrears.

### Target 4H: Loans And Advances

- Add loan master, schedule, ledger.
- Deduct EMI automatically in payroll run.

### Target 4I: Payslip PDF And Publish

- Generate branded PDF payslip.
- Publish payslips after lock.
- Add employee download audit.

### Target 4J: Full And Final Settlement

- Add F&F settlement calculation.
- Pull inputs from exit, leave, payroll, loans, reimbursements, and assets.
- Generate settlement letter.

## Acceptance Criteria

- HR can run payroll for a normal month without manual SQL.
- Payroll cannot be changed after lock except through unlock approval.
- Employees can view only their own payslips.
- Approver sees variance and critical checks before approval.
- Payroll exports are generated as tracked batches.
- Salary changes retain history and maker-checker state.
- Payslip shows component lines and YTD figures.
- Statutory values are rule-driven, not hardcoded.
