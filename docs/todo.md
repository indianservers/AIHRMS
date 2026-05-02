# AI HRMS Fresh TODO Backlog

Date: 2026-05-02
Last updated: 2026-05-02

This is the current backlog after re-checking `docs/competitor_gap_analysis.md` and the implemented backend/frontend modules. Completed historical work is summarized only where it affects the next priorities.

## Current Completed Foundation

- Core HR: companies, branches, departments, designations, employees, lifecycle events, documents, certificates, import/export, sensitive masking.
- Roles: admin/HR/manager/employee permission foundation and admin-only user/role creation.
- Leave: types, balances, ledger, requests, overlap/balance checks, HR/manager approval, leave calendar.
- Attendance: shifts, weekly offs, rosters, holidays, check-in/out, raw punches, regularization, monthly locks, summaries, logging.
- Documents: generated documents, policies, policy versions, employee certificate upload/verify/import/export.
- Payroll foundation: pay groups, legal entities, statutory profiles, periods, components, categories, structures, salary templates, employee salary assignment, salary overrides, salary revisions, payroll runs, payslips, reimbursements, loans, F&F, audit, exports.
- Payroll tax: tax regimes, slabs, sections, limits, regime elections, previous employment tax, tax worksheets, declarations, proofs, Form 16 and 24Q tracking.
- Payroll statutory: PF/ESI/PT/LWF/gratuity rules, employee statutory profile, contribution lines, challans, return-file validation, statutory compliance calendar, EPFO/ESIC submission tracking.
- Payroll calculation depth: salary formula dependency ordering, circular dependency detection, formula trace, tax regime comparison, rebate/surcharge/cess-aware tax projection.
- Workflow/notifications: workflow inbox, workflow engine foundation, notification inbox and delivery logs.
- Helpdesk: tickets, replies, SLA dates, escalation rules, knowledge base.
- Recruitment/onboarding: requisitions, jobs, candidates, interviews, feedback, offers, candidate conversion, onboarding templates/tasks.
- LMS/engagement: course catalog, assignments, certifications, announcements, surveys, recognitions.
- Benefits/BGV/WhatsApp ESS: backend foundations exist; WhatsApp templates, opt-in/out, outbound queue, and delivery callbacks exist.
- Attendance devices/mobile: biometric devices/import batches, punch dedupe, geo/selfie/QR proof and geofence exception foundation exist.
- Platform configurability: custom field definitions/values and report builder definitions/runs exist.
- Deployment: split frontend/backend routing and DigitalOcean MySQL configuration.
- Verification: backend full suite passed at 66 tests before the latest next-10 patch; latest targeted next-10 suite passed at 2 tests. Frontend production build should be rerun after service bindings.

## Highest Gaps Now

1. Payroll is broad but still not fully production-grade: final statutory portal conformance, real Form 16 rendering/DSC, statutory e-filing connector, and payroll setup UX polish remain.
2. Payroll setup UI is behind backend depth: legal entity, pay group, salary template, tax setup, statutory setup, employee statutory profile, formula graph, and worksheet screens need stronger UX.
3. India statutory output still needs real format validation: PF ECR, ESIC, PT/LWF, TDS 24Q/26Q, Form 16 Part A/B, challans, XLSX/portal-ready templates.
4. WhatsApp ESS now has connector metadata and outbound/callback foundations; real Meta Cloud API dispatch, cryptographic signature verification against stored secrets, and CTA approval templates remain.
5. Biometric/geo attendance now has import and proof foundations; vendor SDK sync, mobile camera capture, QR rotation, and manager exception UI remain.
6. Enterprise platform gaps remain: webhooks, MFA/session management, SSO/SAML, DPDP/privacy workflows, and frontend renderers for custom reports/forms.
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

### P1 Connectors And Daily-Use Differentiators

- [x] WhatsApp Business production connector.
  - Signature verification, outbound send API, templates, opt-in/out, delivery callbacks.
- [x] WhatsApp ESS workflows.
  - Apply leave, approve/reject leave, fetch payslip, attendance command, policy QA.
- [x] Biometric attendance import.
  - ZKTeco/eSSL flat file import, device sync table, punch dedupe, error rows.
- [x] Geo/selfie/QR attendance.
  - Mobile punch proof, geofence validation, exception approval.
- [ ] Background verification production connector.
  - Consent capture, AuthBridge/IDfy/HireRight connector, webhook sync, report parsing.

### P1 HRMS Product Depth

- [x] Custom fields and forms.
  - Field definitions, module sections, validation, permissions, frontend renderer.
- [ ] Workflow designer depth.
  - Conditions, reminders, escalations, delegation, field updates, visual editor.
- [ ] Webhooks and integrations framework.
  - Subscriptions, event log, retry queue, connector credentials.
- [x] Report builder.
  - Field catalog, saved filters, scheduled exports, XLSX/PDF.
- [ ] Manager dashboard.
  - Team attendance, leave calendar, approvals, birthdays, performance snapshot.
- [ ] Helpdesk CSAT and SLA analytics.
  - Closure feedback, breach dashboard, category-owner routing.

### P1 Talent, Learning, Engagement, Benefits

- [ ] OKR check-ins and review templates.
- [ ] 360 feedback workflow and calibration.
- [ ] Competency framework and role-skill mapping.
- [ ] Skills gap report and upskilling recommendations.
- [ ] Compensation cycles, pay bands, merit planning, pay equity analytics.
- [ ] LMS SCORM/xAPI support and renewal workflows.
- [ ] Engagement eNPS scoring, anonymity controls, recognition points, dashboards.
- [ ] Benefits claims, limits, tax treatment, payroll worksheet integration.
- [ ] ESOP/RSU vesting schedule and benefit cost report.

### P2 Enterprise, Privacy, And Industry Packs

- [ ] MFA, trusted devices, sessions, password policy, lockout.
- [ ] SSO/SAML/OIDC enterprise login.
- [ ] DPDP consent, privacy requests, data retention, legal hold.
- [ ] Payroll/employee field audit viewer for salary, bank, PAN, Aadhaar, manager, designation.
- [ ] Aadhaar e-KYC and DigiLocker connector.
- [ ] DE&I analytics, pay equity, span-of-control, manager effectiveness.
- [ ] Manufacturing pack: contract labor, safety incidents, PPE, medical fitness, advanced shifts.
- [ ] BFSI pack: certification tracking, policy attestations, evidence retention, maker-checker depth.
- [ ] Retail/field pack: store hierarchy, staffing plan, field visits, offline tasks.
- [ ] Healthcare/education packs: credentials, license expiry, on-call roster, vaccination, faculty workload.

## Recommended Next 10

1. Background verification production connector
2. Workflow designer conditions/reminders/escalations UI
3. Report builder frontend screen with saved reports and exports
4. Custom field renderer inside employee/profile/payroll forms
5. Mobile ESS offline drafts for leave, attendance, documents
6. Benefits claims, limits, tax treatment, payroll worksheet integration
7. Skills/competency framework and role-skill mapping
8. Manager dashboard with team attendance/leave/approvals
9. MFA, trusted devices, active sessions, lockout policy
10. SSO/SAML/OIDC enterprise login
