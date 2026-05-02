# AI HRMS Fresh TODO Backlog

Date: 2026-05-02
Last updated: 2026-05-02

This is the current backlog after re-checking `docs/competitor_gap_analysis.md` and the implemented backend/frontend modules. Completed historical work is summarized only where it affects the next priorities.

## Current Completed Foundation

- Core HR: companies, branches, departments, designations, business units, cost centers, work locations, grade bands, job families/profiles, positions, headcount plans, org chart/hierarchy validation, employees, lifecycle events, change requests, documents, certificates, import/export, sensitive masking.
- Roles: admin/HR/manager/employee permission foundation and admin-only user/role creation.
- Leave: types, balances, ledger, requests, overlap/balance checks, HR/manager approval, leave calendar.
- Attendance: shifts, weekly offs, rosters, holidays, check-in/out, raw punches, regularization, monthly locks, summaries, logging.
- Documents: generated documents, policies, policy versions, employee certificate upload/verify/import/export.
- Payroll foundation: pay groups, legal entities, statutory profiles, periods, components, categories, structures, salary templates, employee salary assignment, salary overrides, salary revisions, payroll runs, payslips, reimbursements, loans, F&F, audit, exports.
- Payroll tax: tax regimes, slabs, sections, limits, regime elections, previous employment tax, tax worksheets, declarations, proofs, Form 16 and 24Q tracking.
- Payroll statutory: PF/ESI/PT/LWF/gratuity rules, employee statutory profile, contribution lines, challans, return-file validation, statutory compliance calendar, EPFO/ESIC submission tracking.
- Payroll calculation depth: salary formula dependency ordering, circular dependency detection, formula trace, tax regime comparison, rebate/surcharge/cess-aware tax projection.
- Database scale controls: high-frequency attendance/leave/payroll/notification/audit indexes, employee/leave/payroll soft-delete fields, salary effective-date proration foundation, employee salary currency, salary-component currency flag, and proxy-aware audit IP/user-agent capture exist.
- Workflow/notifications: workflow inbox, workflow engine foundation, notification inbox and delivery logs.
- Helpdesk: tickets, replies, SLA dates, escalation rules, knowledge base.
- Recruitment/onboarding: requisitions, jobs, candidates, interviews, feedback, offers, candidate conversion, onboarding templates/tasks.
- LMS/engagement: course catalog, assignments, certifications, announcements, surveys, recognitions.
- Benefits/BGV/WhatsApp ESS: backend foundations exist; WhatsApp templates, opt-in/out, outbound queue, and delivery callbacks exist.
- Attendance devices/mobile: biometric devices/import batches, punch dedupe, geo/selfie/QR proof and geofence exception foundation exist.
- Platform configurability: custom field definitions/values, dynamic custom forms/submissions/reviews, and report builder definitions/runs exist.
- Enterprise platform: session/device records, MFA method records, password policy records, login attempt logs, integration credentials, webhooks, integration events, consent records, privacy requests, retention policies, legal holds, and governed metric definitions exist.
- Talent and benefits next-10 foundation: OKR check-ins, review templates, 360 feedback requests/submissions, competency library, role-skill requirements, employee competency assessments, skill gap report, compensation cycles, pay bands, merit recommendations, benefits claims, and ESOP vesting schedules now exist.
- Frontend shell/product polish: manager dashboard route, ESS portal route, org chart route, Cmd/Ctrl+K global search, breadcrumbs, keyboard shortcut help, back-to-top, session timeout countdown, profile completeness/change-request UI, employee/company logo/photo upload UX, print-friendly payslip styling, and confirmation guards for destructive frontend actions exist.
- Daily experience UI depth: real-time org chart with filters/zoom/export/vacancy markers, manager dashboard with team attendance/pending approvals/calendar/moments, ESS portal with payslips/documents/goals/assets, and engagement UI for announcements/polls/recognitions exists.
- Deployment: split frontend/backend routing and DigitalOcean MySQL configuration.
- Verification: backend full suite passed at 66 tests before the latest next-10 patch; targeted core-concepts suite passed at 1 test after the latest org/security/privacy/integration patch. Frontend production build should be rerun after service bindings.

## Highest Gaps Now

1. Payroll is broad but still not fully production-grade: final statutory portal conformance, real Form 16 rendering/DSC, statutory e-filing connector, and payroll setup UX polish remain.
2. Payroll setup UI is behind backend depth: legal entity, pay group, salary template, tax setup, statutory setup, employee statutory profile, formula graph, and worksheet screens need stronger UX.
3. India statutory output still needs real format validation: PF ECR, ESIC, PT/LWF, TDS 24Q/26Q, Form 16 Part A/B, challans, XLSX/portal-ready templates.
4. WhatsApp ESS now has connector metadata and outbound/callback foundations; real Meta Cloud API dispatch, cryptographic signature verification against stored secrets, and CTA approval templates remain.
5. Biometric/geo attendance now has import and proof foundations; vendor SDK sync, mobile camera capture, QR rotation, and manager exception UI remain.
6. Enterprise platform foundation now exists for webhooks, sessions/MFA records, login attempts, DPDP/privacy requests, retention, legal holds, and governed metrics. Remaining: real SSO/SAML/OIDC, MFA verification flow, lockout/IP policy enforcement, retry workers, and frontend admin screens.
7. Talent suite is shallow: OKR check-ins, 360 reviews, calibration, skill framework, career paths, compensation planning.
8. Analytics is basic: scheduled exports, governed metrics, DE&I, pay equity, span-of-control, manager effectiveness.
9. Benefits needs claims, limits, tax treatment, payroll worksheet integration, ESOP/vesting.
10. Industry packs still need real workflows for manufacturing, BFSI, retail/field, healthcare, and education.

## Next 30 Implementation TODOs

### P0 Payroll Reality

- [x] Add `lop_adjustments`.
  - Fields: period_id, employee_id, adjustment_days, reason, source, status, approved_by, approved_at.
- [x] Add `overtime_policies` and `overtime_pay_lines`.
  - Include multiplier, wage base, holiday/weekend OT, approval source, payroll component mapping.
- [x] Add `leave_encashment_policies` and `leave_encashment_lines`.
  - Include leave_type_id, formula, max_days, tax_treatment, payroll_record_id.
- [x] Build leave/attendance reconciliation API.
  - Reconcile approved leave, unpaid leave, attendance, holidays, weekly offs, regularizations, OT into `payroll_attendance_inputs`.
- [x] Block payroll approval when attendance inputs are missing, unapproved, or unlocked.
- [x] Add Payroll Inputs frontend screen.
  - Attendance summary, LOP adjustments, OT lines, encashment lines, exception approvals.
- [x] Add payroll input tests.
  - Paid leave not LOP, unpaid leave becomes LOP, regularization changes input, OT payout, month lock behavior.
- [x] Add `payroll_run_employees`.
  - Fields: payroll_run_id, employee_id, status, hold_reason, skip_reason, input_status, calculation_status, approval_status.
- [x] Add `payroll_calculation_snapshots`.
  - Snapshot salary template, tax worksheet, attendance input, statutory profile, formula version used.
- [x] Expand `payroll_components`.
  - Add source_type, source_id, taxable_amount, exempt_amount, wage_base_flags, calculation_order, formula_trace_json, is_manual, is_arrear, is_reversal.
- [x] Add staged payroll worksheet processor.
  - Collect inputs, calculate gross, statutory, tax, reimbursements, loans, net pay, variance, approval, lock.
- [x] Add payroll worksheet frontend grid.
  - Per-employee preview, hold/skip, recalculate, variance, approval actions.
- [x] Add deterministic payroll worksheet tests.
  - Recalculation consistency, snapshot immutability after lock, hold/skip employee.
- [x] Add `payroll_arrear_runs` and `payroll_arrear_lines`.
  - Retro salary revisions, backdated joining/exits, missed payout, LOP reversal.
- [x] Add `off_cycle_payroll_runs`.
  - Bonus, correction, FnF, contractor, reimbursement-only runs.

### P0 Payments, Accounting, And Compliance Files

- [x] Add `payroll_payment_batches`.
  - Fields: payroll_run_id, bank_format_id, debit_account, total_amount, status, generated_file_url, approved_by, released_at.
- [x] Add `payroll_payment_lines`.
  - Fields: batch_id, employee_id, net_amount, bank_account, ifsc, payment_status, utr_number, failure_reason.
- [x] Add payment status import API.
  - UTR success/failure, failed payment correction, batch release audit.
- [x] Add `accounting_ledgers`, `payroll_gl_mappings`, `payroll_journal_entries`, `payroll_journal_lines`.
- [x] Add GL journal generation by legal entity, branch, department, cost center, and project.
- [x] Add payment batch and GL preview frontend screens.
- [x] Add bank/GL tests.
  - Bank file validation, UTR import, balanced journal entries, cost-center split.
- [x] Build statutory file validation engine.
  - PF ECR, ESI, PT, LWF, TDS 24Q/26Q validation rows and error report.
- [x] Add CSV portal-ready statutory templates.
- [x] Add Form 16 template depth.
  - Part A/B data binding, tax worksheet reconciliation, employer statutory details, digital-signature hook placeholder.

### P1 Payroll Setup And Employee Tax UI

- [x] Build Payroll Setup frontend tabs.
  - Legal Entity, Statutory IDs, Pay Groups, Periods.
- [x] Build Salary Template Builder frontend.
  - Component ordering, formula preview, monthly/annual CTC preview, employee assignment.
- [x] Complete formula dependency graph.
  - Dependency ordering, circular dependency detection, caps/floors, residual component.
- [x] Complete tax engine depth.
  - Old/new regime comparison, proof approval impact, 80C/80D caps, HRA/LTA rules, rebate/surcharge rules.
- [x] Build employee tax regime and worksheet frontend.
  - Regime selection, declaration/proof wizard, HR verification, worksheet view.
- [x] Add tax depth tests.
  - Old vs new regime, previous employment, monthly TDS spread, section caps.

### P1 Database Scale And Audit Controls

- [x] Add high-frequency composite indexes.
  - Attendance employee/date, leave status/employee, payroll period/company, notifications user/unread/date, audit entity/date, employee active status, and salary effective history.
- [x] Add soft-delete protection for critical HR/payroll records.
  - Employee, leave request, and payroll run now carry `deleted_at`/`deleted_by`; core employee, leave, and payroll-run queries exclude deleted rows.
- [x] Add salary effective-date support and mid-month proration.
  - Employee salary stores `effective_date`; payroll run traces calendar-day salary proration across revisions.
- [x] Add multi-currency payroll master data.
  - Employee salary currency defaults to INR; salary components now declare whether amounts are fixed in currency.
- [x] Enhance audit context for compliance.
  - Audit log indexes entity lookup and captures user-agent plus proxy-aware client IP.

### P1 Daily Experience Screens

- [x] Upgrade real-time org chart.
  - Interactive SVG chart, zoom controls, employee profile drill-down, department/location/grade-band filters, PDF/PNG/SVG export, and dashed vacant-position boxes.
- [x] Upgrade manager dashboard.
  - Team attendance split, pending leave/regularization/change-request counts, birthdays/anniversaries, direct reports, open tickets, and color-coded team leave/holiday calendar.
- [x] Upgrade ESS portal.
  - Last 12 payslips with PDF links, leave balances, attendance/leave/helpdesk shortcuts, generated documents, goals/appraisal status, and IT asset assignments.
- [x] Add engagement frontend.
  - Published announcement banner, HR announcement form, poll creation/voting/results chart, recognition wall, reactions, and people moments list.

### P1 Connectors And Daily-Use Differentiators

- [x] WhatsApp Business production connector.
  - Signature verification, outbound send API, templates, opt-in/out, delivery callbacks.
- [x] WhatsApp ESS workflows.
  - Apply leave, approve/reject leave, fetch payslip, attendance command, policy QA.
- [x] Biometric attendance import.
  - ZKTeco/eSSL flat file import, device sync table, punch dedupe, error rows.
- [x] Geo/selfie/QR attendance.
  - Mobile punch proof, geofence validation, exception approval.
- [x] Background verification production connector foundation.
  - Consent capture, provider code/API secret refs, vendor submission reference, webhook sync, report URL/result mapping, and connector event audit exist. Remaining: real AuthBridge/IDfy/HireRight SDK calls, webhook signature verification against secret manager, document/report parser.

### P1 HRMS Product Depth

- [x] Custom fields and forms.
  - Field definitions, module sections, validation, permissions, dynamic form definitions, ordered form fields, submissions, review flow, and value persistence exist. Remaining: visual drag/drop renderer inside each module page.
- [x] Workflow designer backend depth.
  - Condition expressions, context-based step skipping, multi-step progression, due reminders, and escalation processing exist. Remaining: delegation, cross-module field updates, visual editor.
- [x] Webhooks and integrations framework.
  - Subscriptions, event log, and connector credentials foundation exist; retry worker and connector SDKs remain.
- [x] Report builder.
  - Field catalog, saved filters, scheduled exports, XLSX/PDF.
- [ ] Manager dashboard.
  - Team attendance, leave calendar, approvals, birthdays, performance snapshot.
- [ ] Helpdesk CSAT and SLA analytics.
  - Closure feedback, breach dashboard, category-owner routing.

### P1 Talent, Learning, Engagement, Benefits

- [ ] OKR check-ins and review templates.
- [x] OKR check-ins and review templates.
  - Goal progress check-ins and configurable review templates/questions are database-backed.
- [x] 360 feedback workflow foundation.
  - Request/submission tracking with relationship type, due date, response JSON, rating, comments, and status exists. Remaining: calibration sessions and UI.
- [x] Competency framework and role-skill mapping.
  - Competency library, role skill requirements, and employee competency assessments exist.
- [x] Skills gap report and upskilling recommendations.
  - Employee skill gap API compares required role levels against assessments and returns recommendations. Remaining: LMS-linked recommendation engine.
- [x] Compensation cycles, pay bands, and merit planning foundation.
  - Compensation cycles, pay bands, and merit recommendations with increase percentage/review status exist. Remaining: manager worksheet UI and controlled pay-equity model.
- [ ] LMS SCORM/xAPI support and renewal workflows.
- [ ] Engagement eNPS scoring, anonymity controls, recognition points, dashboards.
- [x] Benefits claims, limits/tax treatment, payroll worksheet integration foundation.
  - Benefit claims include approval, taxable/exempt split, receipts, and payroll record link; flexi allocation claimed/taxable fallback updates on approval. Remaining: payroll worksheet auto-pull and richer limits by family/dependent.
- [x] ESOP/RSU vesting schedule foundation.
  - ESOP plans, grants, and generated vesting schedules exist. Remaining: exercise workflow, RSU taxation, and cost report.

### P2 Enterprise, Privacy, And Industry Packs

- [x] MFA, trusted devices, sessions, password policy, lockout foundation.
  - Session/device, MFA method, password policy, and login attempt APIs exist. Remaining: real OTP/TOTP verification, lockout enforcement, IP allowlist, recovery codes.
- [ ] SSO/SAML/OIDC enterprise login.
- [x] DPDP consent, privacy requests, data retention, legal hold foundation.
  - Consent capture/revoke, privacy request review, retention policies, and legal hold/release APIs exist. Remaining: retention job, export/delete processor, employee-facing portal.
- [ ] Payroll/employee field audit viewer for salary, bank, PAN, Aadhaar, manager, designation.
- [ ] Aadhaar e-KYC and DigiLocker connector.
- [x] DE&I analytics foundation.
  - Representation by gender identity, legal gender, disability, veteran status, department, grade band, and latest payroll average-gross pay equity view exist. Remaining: pay-equity controls by role/grade/tenure/location, span-of-control, manager effectiveness.
- [ ] Manufacturing pack: contract labor, safety incidents, PPE, medical fitness, advanced shifts.
- [ ] BFSI pack: certification tracking, policy attestations, evidence retention, maker-checker depth.
- [ ] Retail/field pack: store hierarchy, staffing plan, field visits, offline tasks.
- [ ] Healthcare/education packs: credentials, license expiry, on-call roster, vaccination, faculty workload.

## Recommended Next 10

1. Workflow designer visual UI, delegation, and field-update actions
2. Organization admin frontend for business units, positions, and headcount plans
3. Employee profile change request approval inbox integration
4. Report builder frontend screen with saved reports and exports
5. Custom form visual renderer inside employee/profile/payroll forms
6. Mobile ESS offline drafts for leave, attendance, documents
7. LMS SCORM/xAPI support and certification renewal workflows
8. Engagement eNPS scoring, anonymity controls, recognition points, dashboards
9. SSO/SAML/OIDC enterprise login plus real MFA/lockout enforcement
10. BGV real vendor SDK and signed webhook verification
