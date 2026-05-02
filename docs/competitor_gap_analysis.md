# HRMS Competitor Gap Analysis

Date: 2026-05-01
Last updated: 2026-05-02

This compares the current AI HRMS implementation with the top 10 HRMS/HCM products globally and in India, identifies what is lacking, and prescribes the modifications required.

## Reference Products (Top 10)

### Global Enterprise
- **Workday HCM**: Skills Cloud, Journeys (guided employee experience), workforce planning and headcount modeling, Peakon continuous listening, extended-enterprise learning, contingent workforce, global payroll orchestration, Workday Extend (custom apps), ESG workforce reporting, predictive analytics.
- **SAP SuccessFactors**: Talent Intelligence Hub (skills-based org), Employee Central (global), multi-country payroll connectivity, career site builder, succession/development, continuous performance management, Business AI, benefits administration, global compliance (100+ countries).
- **ADP Workforce Now**: Payroll-first confidence, multi-state/country tax filing, workers' comp integration, benefits administration, ADP marketplace (300+ connectors), DataCloud benchmarking, predictive compliance alerts, new-hire state reporting.
- **UKG (Ultimate Kronos Group)**: Workforce Intelligence AI scheduling, predictive scheduling, shift trading marketplace, labor analytics and compliance, geo-fencing, multi-location workforce management, manager on-the-go mobile.
- **BambooHR**: Benchmark SMB UX, employee wellbeing surveys, built-in e-sign, automated onboarding reminders, compensation management, candidate tracking, time-off simplicity, eNPS, DE&I reporting.

### Modern Platforms
- **HiBob / Lattice**: People analytics with real-time dashboards, employee lifecycle insights, DE&I metrics, compensation benchmarking, manager effectiveness scores, continuous feedback loops, OKR alignment.

### India-Focused
- **Keka HR**: HR, payroll, performance, hiring/onboarding, time and attendance, PSA/timesheets, LMS, marketplace, industry-specific packs, tax/expense, recognition, single-window approvals, shift marketplace.
- **Zoho People**: Recruitment, onboarding, employee management, attendance, shift management, leave, timesheets, helpdesk with SLA/knowledge base, document management with e-sign integrations, offboarding, performance, compensation, LMS, payroll/expense integrations, engagement, communication, analytics, workflow automation, mobile apps.
- **greytHR**: India-focused HR and payroll, leave, attendance, performance, ESS, engagement, recruitment, expense management, compliance resources, marketplace, EPFO/ESIC portal uploads, Form 16, statutory calendar.
- **factoHR / HRMantra / Qandle / sumHR**: WhatsApp ESS (leave, payslip, attendance over WhatsApp), Aadhaar-based e-KYC, DigiLocker integration, biometric device SDKs (ZKTeco/eSSL/Mantra), statutory compliance calendar with auto-reminders, UPI salary disbursement, vernacular payslip, multi-entity payroll groups, EPFO ECR direct upload, ESIC portal integration, background verification (AuthBridge/IDfy).

Sources checked:
- Keka HR Cloud: https://www.keka.com/us/hr-cloud
- Zoho People features: https://www.zoho.com/people/features.html
- greytHR products: https://www.greythr.com/products
- Darwinbox HRMS feature overview: https://blog.darwinbox.com/advanced-hrms-features
- Workday HCM: https://www.workday.com/en-us/products/human-capital-management/overview.html
- SAP SuccessFactors: https://www.sap.com/india/products/hcm/hxm-suite.html
- ADP Workforce Now: https://www.adp.com/what-we-offer/products/adp-workforce-now.aspx
- UKG: https://www.ukg.com/solutions/hcm-software
- BambooHR: https://www.bamboohr.com/hr-software
- factoHR: https://factohr.com/features

---

## Current Product Position

The ERP has moved beyond a broad HRMS MVP skeleton into a database-backed HRMS foundation. It now contains backend models, APIs, tests, and selected frontend routes/service bindings for:

- Auth, roles, permissions
- Company, branch, department, designation
- Employee master with profile, job, statutory, bank, education, experience, skills, documents, document verification, document expiry, and lifecycle history
- Leave types, balances, ledger, requests, overlap/balance checks, approval/cancel, and calendar/team view
- Attendance shifts, weekly-off/roster foundation, holidays, punch in/out, regularization, late/early/short-hours computation, monthly summary
- Payroll setup, legal entities, statutory profiles, pay groups, generated payroll periods, salary components/categories/formula rules, structures, structure versioning, salary templates, employee template assignments, component overrides, salary revisions, maker-checker approval, payroll run, pre-run checks, manual inputs, lock/unlock workflow, variance/anomaly review, payslip payload, publish hook, reimbursements, reimbursement ledger, loans/EMI ledger, tax regimes/slabs/sections/elections/worksheets, previous employment tax, tax declarations/proofs, and full-final settlement
- Recruitment jobs, candidates, interviews, feedback, offers, AI resume parsing
- Onboarding templates/tasks, policy acknowledgement
- Documents, policies, policy versioning, generated documents, employee certificates, import/export logs
- Performance cycles, goals, reviews
- Helpdesk categories, tickets, replies, SLA due dates, escalation rules, knowledge base, AI suggested reply
- Reports dashboard and standard module reports
- Assets, exit, target catalog, AI assistant
- Deployment routing for split frontend/backend hosting and DigitalOcean MySQL configuration

---

## Implementation Status Summary

| Area | Status | Notes |
| --- | --- | --- |
| Core HR foundation | Mostly complete | Employee master, lifecycle events, documents, certificates, import/export, masking, and role-aware access exist. Remaining: business units, cost centers, grades, positions, org chart, custom fields. |
| Leave | Strong foundation | Ledger, overlap checks, balance checks, approvals, holidays/calendar/team view exist. Remaining: accrual jobs, carry-forward processor, comp-off, delegation/escalation. |
| Attendance | Foundation complete | Shifts, weekly off/roster, daily computation fields, regularization, summaries exist. Remaining: raw punch audit, biometric import, geo/selfie/QR, attendance lock, OD/field visit. |
| Payroll | Strong DB/API foundation | Legal entity, statutory profile, pay groups, periods, component categories, safe formula rules, salary templates, tax regimes/slabs/elections/worksheets, statutory rules/contribution lines/challans/return validation, payroll attendance inputs, salary revisions, run controls, manual inputs, reimbursement, loans, F&F, audit, lock/unlock, PDF payslip, and CSV exports exist. Remaining: payroll worksheet processing, LOP/OT reconciliation, bank payment status, GL accounting, setup UI depth, final statutory formats. |
| Documents/policies | Foundation complete | Policy versioning, document expiry, verification, certificates, import/export logs exist. Remaining: template PDF rendering, e-sign integration. |
| Workflow/notifications | Foundation complete | Shared workflow inbox and notification inbox exist. Remaining: fully configurable workflow designer, delegation, condition branches, reminder scheduler. |
| Helpdesk | Foundation complete | SLA dates, escalation rules, knowledge base, ticket escalation, replies exist. Remaining: CSAT, AI source-cited suggestions, SLA analytics UI. |
| Recruitment/onboarding | MVP | Jobs/candidates/interviews/offers/onboarding exist. Remaining: requisition approvals, candidate-to-employee conversion, career site, e-sign offer flow. |
| Performance | MVP | Cycles, goals, reviews exist. Remaining: OKR check-ins, review templates, 360 feedback, calibration. |
| LMS/learning | Foundation complete | Course catalog, assignments, completions, certifications, verification, and expiry tracking exist. Remaining: SCORM/xAPI, renewals, skill-linked learning, dashboards. |
| Engagement | Foundation complete | Announcements, surveys/responses, and recognition feed exist. Remaining: eNPS scoring, anonymity controls, points, social wall, dashboards. |
| Benefits | Foundation complete | Benefit plans, enrollments, flexi policies/allocations, and payroll deduction lines exist. Remaining: claims, limits, tax treatment, and payroll worksheet integration. |
| WhatsApp ESS | Foundation complete | Provider config, sessions, inbound messages, and basic leave/payslip/attendance intents exist. Remaining: production WhatsApp Business connector, outbound templates, manager CTA approvals, delivery callbacks. |
| Statutory compliance | Strong foundation | Legal entities, Form 16/24Q tracking, EPFO/ESIC portal submission tracking, compliance calendar, PF/ESI/PT/LWF/gratuity rules, challans, and return-file validation exist. Remaining: auto-reminders, final portal file conformance, DSC/signature hooks. |
| Skills-based org | Missing | Employee skills field exists; no skills gap mapping, upskilling paths, competency framework. |
| Employee wellbeing | Missing | No burnout tracking, mental health resources, work-life balance metrics. |
| Reports/analytics | Basic | Standard reports exist. Remaining: custom report builder, scheduled exports, governed metrics, PDF/XLSX outputs, DE&I analytics. |
| Mobile ESS/PWA | Pending | Frontend is web-first. Competitors lead with mobile attendance, leave, payslip, approvals, documents, notifications. |
| Enterprise security | Partial | JWT, RBAC, masking, audit foundations exist. Remaining: MFA, sessions/devices, field audit viewer, retention/privacy/legal hold. |

---

## Completed Gap Closure

These competitor gaps have already been addressed in the current implementation cycle:

- Employee lifecycle history and auditable employee events.
- Leave balance ledger, overlap prevention, balance enforcement, and leave calendar.
- Attendance weekly-off/roster foundation and late/early/short-hours computation.
- Payroll lock guardrails, payroll audit logs, variance/anomaly review, and export batch tracking.
- Payroll component lines, rich payslip payload, and YTD summary.
- Scoped RBAC baseline and sensitive employee masking.
- Split frontend/backend deployment routing and DigitalOcean MySQL configuration.
- Shared workflow/task inbox.
- Notification inbox and email/SMS delivery-log hooks.
- Employee bulk import/export with row-level errors.
- Tax declaration cycle, proof workflow, verification, and TDS projection.
- Employee document expiry and verification.
- Policy versioning.
- Helpdesk SLA dates, escalation rules, and knowledge base.
- Salary revision request and maker-checker approval.
- Sensitive salary audit log.
- Payroll pre-run checks, manual payroll inputs, and unlock request with reason.
- Payslip bulk publish/email dispatch hook.
- Reimbursement approval and ledger.
- Loans/advances with EMI schedule and loan ledger.
- Full and final settlement with exit link, recoveries, payables, and settlement letter URL.
- Payslip PDF generation, storage URL, and employee/admin download endpoint.
- Payroll CSV file exports for PF ECR, ESI, PT, TDS 24Q, Form 16, bank advice, pay register, and accounting journal.
- Payroll component formula preview with a controlled Decimal evaluator.
- Attendance raw punch audit and monthly lock/unlock API.
- Configurable workflow engine foundation with definitions, ordered steps, instances, task inbox, and decisions.
- Project utilization report with CSV export.
- Recruitment requisition approval and candidate-to-employee conversion.
- PWA foundation with manifest, app icon, service worker, and production registration.
- LMS course catalog, assignments, completions, certifications, verification, and expiry tracking.
- Engagement foundation with announcements, surveys/responses, and recognition feed.
- WhatsApp ESS foundation with provider configuration, inbound message sessions, intent handling, and leave/payslip/attendance response hooks.
- Form 16 document lifecycle and 24Q TDS filing tracking.
- EPFO/ESIC portal submission tracking with files, acknowledgements, payment references, and statuses.
- Benefits administration foundation for group health/NPS/flexi-benefit style plans, enrollments, allocations, and payroll deduction lines.
- Statutory compliance calendar for PF/ESI/PT/TDS due dates and completion tracking.
- Background verification foundation with vendors, employee/candidate requests, checks, and result tracking.
- Admin request/error logging with log list, error list, analysis API, and frontend `/logs` page.
- Attendance check-in hardening for older partial attendance rows.
- Payroll-real next-20 foundation: statutory profiles, expanded pay groups, generated periods, period lock/unlock, component categories, salary templates, employee salary assignments/overrides, restricted AST salary formulas, tax regimes/slabs/sections, employee tax regime elections, previous employment tax details, and persisted monthly TDS worksheets.
- Payroll statutory engine foundation: PF, ESI, PT, LWF, and gratuity rule tables; employee statutory profiles; contribution lines; challans; return-file validation; and payroll attendance input table.
- Payroll formula dependency graph: salary structure previews now order component formulas by dependency, detect circular references, expose formula trace metadata, and apply component caps/floors where available.
- Payroll tax depth: old/new regime comparison, rebate, surcharge, cess, standard deduction, previous employment income/TDS, and monthly TDS projection foundations exist.
- WhatsApp ESS production foundation: connector secret references, outbound template messages, employee opt-in/out, queued outbound messages, and delivery callbacks exist.
- Biometric and mobile attendance foundation: biometric devices, import batches, punch dedupe, import error reports, geo/selfie/QR punch proof, and geofence exception status exist.
- Configurability foundation: custom field definitions/values and report builder field catalog, saved definitions, and run history exist.

---

## Pending Gap List

### P0 — Showstopper (Must-Have for Production Viability)

| Priority | Pending gap | Competitor benchmark | Recommended build |
| --- | --- | --- | --- |
| P0 | Final statutory/finance exports | PF ECR, ESI challan, PT challan, TDS 24Q/26Q, bank advice, pay register, accounting journal must produce usable files | Completed foundation: CSV writers, export history, file URLs, and download endpoint. Next: statutory-format validation/XLSX templates |
| P0 | Form 16 / Form 16A generation | greytHR, Keka, factoHR generate Form 16 from TDS data with employer DSC | Foundation complete: Form 16 document records, generated/published status, file URLs. Next: statutory template rendering, Part A/B data binding, DSC hook |
| P0 | Payroll formula execution depth | Component formulas must calculate safely from dependencies and effective structure versions | Completed foundation: controlled formula evaluator, dependency graph ordering, circular dependency detection, caps/floors, and formula trace. Next: expose graph visually in setup UI |
| P0 | Payroll attendance/LOP/OT reconciliation | Keka/greytHR payroll needs paid leave, unpaid leave, LOP, OT, regularization, weekly off and holiday reconciliation before approval | Attendance input table exists. Next: LOP adjustments, OT policies, encashment, reconciliation API, approval blocker, input UI |
| P0 | Payroll worksheet processing | Mature payroll suites show per-employee worksheet, calculation trace, hold/skip, deterministic recalculation, and lock snapshots | Add run employee table, calculation snapshots, expanded payroll component trace, staged processor, worksheet UI |
| P0 | Payments and GL accounting | Payroll buyers expect bank advice, UTR import, failed payment correction, and accounting journal posting | Add payment batches/lines, status import, GL ledgers/mappings/journals, balanced journal tests |
| P0 | Configurable workflow engine | Darwinbox/Zoho-style workflow automation across modules | Completed foundation: workflow definitions, ordered steps, approver resolution, instances, task inbox, and decisions. Next: conditions/reminders |
| P0 | EPFO/ESIC portal integration | greytHR, factoHR submit ECR/ESIC challan directly to government portals | Foundation complete: EPFO/ESIC submission tracking, files, acknowledgements, payment references. Next: mandated file validation and real portal connector |

### P1 — High Impact (Differentiators and Buyer Requirements)

| Priority | Pending gap | Competitor benchmark | Recommended build |
| --- | --- | --- | --- |
| P1 | WhatsApp ESS | sumHR, Qandle, factoHR, HRMantra offer leave apply/approve, payslip fetch, attendance punch via WhatsApp | Foundation complete: provider config, sessions, inbound messages, templates, opt-in/out, outbound queue, and delivery callbacks. Next: real Meta Cloud API dispatch and manager CTA templates |
| P1 | Mobile ESS/PWA | All top 10 competitors offer mobile leave, attendance, payslips, documents, approvals, notifications | Completed foundation: installable PWA manifest, icon, service worker, and production registration. Next: mobile ESS flows/offline drafts |
| P1 | Benefits administration | ADP, SuccessFactors, BambooHR, Keka cover group health, flexi-benefits, NPS, ESOP | Foundation complete: benefit plans, enrollments, flexi policies/allocations, payroll deduction lines. Next: policy limits, employee claims, tax treatment, payroll worksheet integration |
| P1 | Statutory compliance calendar | greytHR, factoHR, HRMantra surface PF/ESI/PT/TDS due dates with alerts | Foundation complete: compliance event table/API with due dates, owners, statuses, completion tracking. Next: auto-population, dashboard widget, email/SMS reminders |
| P1 | Recruitment requisition to employee conversion | All top 10 connect workforce plan → hiring approval → offer → onboarding → employee creation | Completed foundation: requisition model/API, approval creates job, candidate conversion creates employee. Next: offer/onboarding linkage |
| P1 | LMS and certifications | Zoho/Keka/Darwinbox/Workday/SuccessFactors include learning/courses/certifications | Completed foundation: course catalog, assignments, completions, certificate expiry, verifier fields. Next: skill-linked completions |
| P1 | Engagement: eNPS, announcements, recognition | BambooHR (eNPS), Keka (recognition), Zoho (surveys), Darwinbox (culture) — all table-stakes | Completed foundation: announcements, surveys/responses, recognition feed. Next: eNPS scoring and points |
| P1 | Skills-based organization | Workday Skills Cloud, SuccessFactors Talent Intelligence Hub map skills to roles | Add competency framework, role-skill mapping, skills gap report, upskilling path recommendations |
| P1 | Custom fields/forms | Zoho and Darwinbox sell configurable services and forms | Foundation complete: custom field definitions, values, module sections, validation metadata, and permissions. Next: frontend renderer in module forms |
| P1 | Webhooks/integrations | All buyers expect accounting, biometric, e-sign, calendar/email, Slack/Teams, APIs | Add webhook subscriptions, event log, retry queue, connector credentials |
| P1 | Report builder | Enterprise HR expects saved filters, scheduled exports, governed metrics | Foundation complete: report field catalog, saved definitions, run history, and service bindings. Next: frontend builder, scheduler worker, XLSX/PDF output |
| P1 | Background verification integration | Keka, Darwinbox, Zoho integrate AuthBridge, HireRight, IDfy for BGV | Foundation complete: vendors, employee/candidate requests, checks, status/result tracking. Next: vendor API connector, consent, webhook sync |
| P1 | Biometric device integration | greytHR, factoHR, HRMantra support ZKTeco, eSSL, Mantra MFSL, Realtime biometric devices | Foundation complete: biometric devices, import batches, punch deduplication, and row-level import errors. Next: vendor SDK sync |
| P1 | Manager dashboard | BambooHR, Keka, Workday provide manager-specific views: team attendance, leave, performance, approvals | Add manager home with team widgets: attendance heat map, leave calendar, pending approvals, performance snapshot |

### P2 — Strategic Depth (Enterprise and Expansion)

| Priority | Pending gap | Competitor benchmark | Recommended build |
| --- | --- | --- | --- |
| P2 | Employee wellbeing module | BambooHR wellbeing surveys, Workday Peakon listening, UKG burnout analytics | Add wellbeing pulse surveys, mood check-in, burnout risk flag linked to attendance/overtime patterns |
| P2 | Aadhaar e-KYC / DigiLocker | factoHR, HRMantra, sumHR use Aadhaar OTP KYC and DigiLocker for document verification | Add Aadhaar e-KYC API hook and DigiLocker document pull for employee onboarding |
| P2 | Shift marketplace / shift swap | UKG, Keka, Deputy allow employees to pick up open shifts or swap with peers | Add shift open-board, employee shift pickup, peer swap request with manager approval |
| P2 | Contractor/gig worker management | ADP, Workday, Darwinbox manage contingent workforce separately | Add contract worker profiles, separate payroll run type, compliance for contract labor |
| P2 | DE&I analytics | Workday, BambooHR, HiBob offer gender diversity, pay equity, representation metrics | Add diversity dimension to employee master, DE&I dashboard: gender/age/dept breakdown, pay equity flags |
| P2 | Employee referral program | Keka, Zoho, Darwinbox track referral bonuses and gamification | Add referral tracking: referrer, bonus type, payout status linked to successful hire |
| P2 | Interview scheduling with calendar sync | Zoho Recruit, Keka, Darwinbox sync interview slots with Google/Outlook calendar | Add calendar OAuth, slot availability, auto-invite send, reschedule flow |
| P2 | Compensation planning | Workday, SuccessFactors, Lattice: merit cycles, pay bands, pay equity, budget simulation | Add compensation cycle model, merit recommendation engine, manager compensation planning UI |
| P2 | Industry packs | Keka (Tech, Manufacturing), Darwinbox (BFSI, Retail, Healthcare) sell domain-fit workflows | Build Technology pack, then Manufacturing, BFSI, Retail, Healthcare, Education |
| P2 | Enterprise security | MFA, sessions, lockout, IP restrictions, privacy and retention | Add session table, MFA policy, field audit viewer, retention/privacy request flows |
| P2 | UPI payroll disbursement | factoHR, sumHR support UPI bulk pay and NEFT bulk upload with bank confirmation | Add salary disbursement via NEFT bulk file + UPI bulk API, payment status webhook |
| P2 | Project utilization reports | Keka PSA-style billable utilization and client/project profitability | Completed foundation: utilization report API and CSV export. Next: profitability and XLSX/scheduled exports |

---

## Highest Impact Gaps (Updated)

| Priority | Gap | Why it matters | Current state |
| --- | --- | --- | --- |
| P0 | Payslip PDF and statutory output generation | Payroll buyers need downloadable, audit-ready files. Form 16 is legally mandated. | Foundation complete: payslip PDFs are generated/stored/downloadable; PF/ESI/PT/TDS/Form 16/bank advice/pay register/accounting journal CSV files are generated with export history. Government-ready statutory file conformance remains pending |
| P0 | EPFO/ESIC portal integration | greytHR and factoHR win SMB payroll business by eliminating manual portal uploads | ECR/ESIC challan file format exists as stubs; actual portal submission pipeline is missing |
| P0 | Configurable workflow engine | Competitors route leave, payroll, onboarding, helpdesk, documents through configurable workflows | Foundation complete: workflow definitions, ordered approver steps, instances, task inbox, and decisions. Conditions, reminders, escalation, and visual designer remain pending |
| P0 | Payroll compliance depth | Keka/greytHR win heavily on India payroll statutory confidence | Foundation strengthened: formula preview, payslip PDF, CSV exports, lock guardrails, audit/export batches, loans, reimbursements, tax declarations, and full-final settlement exist. Final statutory file conformance remains pending |
| P1 | WhatsApp ESS | India SMB market expects WhatsApp-first HR. sumHR and factoHR win on this specifically | Foundation complete: provider config, sessions, inbound message capture, and basic leave/payslip/attendance intent handling exist. Production connector, outbound templates, manager CTA approvals, delivery callbacks, and policy QA remain pending |
| P1 | Mobile/ESS experience | All 10 competitors emphasize mobile leave, attendance, payslips, documents, approvals | PWA foundation is complete with manifest, icon, service worker, and production registration. Mobile UX polish and offline-safe forms remain pending |
| P1 | Benefits administration | ADP, SuccessFactors, BambooHR make benefits a major module. India buyers need group health + NPS + flexi-benefits | Foundation complete for plans, enrollments, flexi allocations, and deduction lines. Policy claims, tax handling, and payroll worksheet integration remain |
| P1 | Statutory compliance calendar | Compliance deadline tracking is a daily-use feature in greytHR and factoHR because it reduces accountant anxiety | Foundation complete: compliance event table/API with PF/ESI/PT/TDS due dates, owners, statuses, and completion tracking exists. Auto-population, reminders, dashboard widget, and escalation remain pending |
| P1 | Skills-based organization | Workday and SuccessFactors are selling skills intelligence as next-generation HCM differentiation | Employee skills field exists; no competency framework, role-skill mapping, or upskilling paths |
| P1 | Engagement/culture | Recognition, pulse surveys, eNPS, social wall are visible differentiators in all top 10 | Foundation complete: announcements, surveys/responses, and recognition feed APIs exist. eNPS analytics and richer social UX remain pending |
| P1 | Learning and skill development | Keka, Zoho, Darwinbox, Workday, SuccessFactors all include LMS/talent development | Foundation complete: courses, assignments, completion/progress, and certifications with expiry/verifier fields exist. Skill gaps and competency framework remain pending |
| P1 | Integrations/marketplace | All 10 buyers expect biometric, accounting, e-sign, calendar/email, Slack/Teams, APIs/webhooks | API exists, but connector framework/webhooks/import-export jobs are missing |

---

## Module-by-Module Gap

### 1. Core HR and Organization

Already present:
- Company, branch, department, designation
- Employee master with personal/job/bank/statutory/profile fields
- Reporting manager field
- Employee education, experience, skills, documents
- Employee lifecycle event history
- Employee document verification and expiry tracking
- Employee certificates with import/export logs
- Employee CSV import/export with row-level validation

Missing versus top 10:
- Multi-tenant architecture (Workday, SAP, Darwinbox)
- Legal entities separate from companies (SuccessFactors Employee Central, Darwinbox)
- Business units, cost centers, locations, grades/bands, job families, job profiles (all enterprise)
- Position management and vacancy/headcount slots (Workday, SuccessFactors, Darwinbox)
- Manager hierarchy validation and org chart (all top 10)
- Dynamic custom fields and custom forms (Zoho, Darwinbox, BambooHR)
- Employee profile change requests with approval (Zoho, Darwinbox)
- DE&I demographic fields and analytics (Workday, BambooHR, HiBob)
- Aadhaar e-KYC and DigiLocker integration (factoHR, HRMantra)
- Contractor/gig worker profile type (ADP, Workday)

Recommended build:
1. Add business unit, cost center, grade/band, position.
2. Add org chart and manager hierarchy validation.
3. Add profile change request workflow.
4. Add DE&I fields (gender identity, disability, veteran status optional).
5. Add Aadhaar e-KYC hook for onboarding.
6. Add custom fields after core org depth is stable.

### 2. Leave Management

Already present:
- Leave types, balances, apply, list, approve, cancel
- Basic gender/applicability, carry-forward, encashable flags
- Balance ledger, overlap prevention, balance enforcement
- Leave calendar, holiday-aware calendar payload

Missing versus top 10 (Keka, Zoho, greytHR, BambooHR, UKG):
- Accrual schedules and monthly/year-end jobs
- Holiday/weekend-aware effective working-day calculation
- Comp-off claims and expiry
- Multi-level approvals, delegation, escalation
- Attachments and document-required rules
- Leave encashment linked to payroll
- Paternity, bereavement, sabbatical leave type rules
- Manager on-the-go leave approval (mobile/WhatsApp)

Recommended build:
1. Add accrual/carry-forward processor.
2. Add effective working-day calculation with holidays/weekends.
3. Add comp-off claims and expiry.
4. Move leave approvals to configurable workflow engine.
5. Add WhatsApp approval notification hook.

### 3. Attendance and Workforce Management

Already present:
- Shifts, holidays, web punch in/out
- Attendance records with IP/location fields
- Regularization request/approval, monthly summary
- Overtime request model
- Weekly-off and roster assignment foundation
- Late, early, short-hours computed fields, daily attendance computation service

Missing versus competitors (UKG, Keka, greytHR, factoHR):
- Advanced rotations, split/night-shift edge cases
- Alternate Saturdays and branch-level weekly-off overrides
- Multiple punch events per day with raw audit trail
- Geo-fence, selfie, QR, biometric device import (ZKTeco, eSSL, Mantra MFSL, Realtime)
- Attendance lock by month
- On-duty/field visit workflow
- Payroll LOP and OT integration
- Mobile/offline attendance for field/retail
- Shift marketplace: open shifts, employee pickup, peer swap with approval (UKG, Keka, Deputy)
- Canteen/cafeteria integration (Manufacturing HRMS)

Recommended build:
1. Split raw punch events from computed daily attendance.
2. Add attendance month lock/unlock.
3. Add biometric import connector (ZKTeco SDK / flat-file import).
4. Add geo-fence punch with selfie proof.
5. Add OT payout mapping to payroll components.
6. Add shift open-board and swap request.

### 4. Payroll, Expense, and Compliance

Already present:
- Salary components, structures, versioning, CTC preview
- Salary revision and maker-checker approval
- Payroll run, approval/lock/unlock, pre-run checks, manual inputs, audit logs
- Payslip endpoint with components and YTD totals, bulk publish hook
- Reimbursements, approval, ledger
- Tax declarations, proofs, verification, TDS projection
- Loans/advances, EMI schedules, loan ledger
- Full and final settlement
- AI anomaly flag fields

Missing versus Keka/greytHR/ADP/SuccessFactors:
- Frontend payroll setup flows for legal entity, employer statutory profile, pay groups, periods, salary templates, tax setup, and employee tax worksheets.
- Robust formula dependency graph and circular dependency handling.
- Income tax proof approval impact, old/new regime comparison, rebate/surcharge depth, HRA/LTA calculations, and employee/HR tax worksheet UI.
- Statutory rule engine UI/API depth beyond foundation: advanced EPS splits, state-specific edge cases, challan exports, portal file conformance, and due-date automation.
- Employee statutory profile bulk setup and validation: UAN/PF/ESI/PT/LWF fields exist; pending work is import, validation, and HR-friendly profile editor.
- Real PDF payslip generation with company logo, employer statutory IDs, tax summary, YTD, and configurable display.
- Form 16 / Form 16A generation from TDS data with employer details and digital-signature hook.
- Final statutory reports: PF ECR, ESI challan, PT challan, TDS 24Q/26Q, LWF, gratuity.
- Real bank advice/NEFT bulk upload file, payment status import, UTR tracking, and failed payment correction.
- Real accounting/GL export by legal entity, branch, department, cost center, and project (Tally, SAP, Zoho Books).
- EPFO portal and ESIC portal direct integration
- Statutory compliance calendar with PF/ESI/PT/TDS due dates and alerts
- Payroll worksheet: collect inputs, calculate gross, calculate statutory, calculate tax, apply loans/reimbursements, net pay, variance, approval, lock.
- Leave/attendance payroll input reconciliation: paid leave, unpaid leave, LOP, weekly offs, holidays, regularizations, overtime, arrears/reversals.
- Payroll variance review UI polish and per-employee recalculation.
- Arrear/revision processing for backdated salary changes, joining/exits, missed payouts, LOP reversals.
- Off-cycle payroll for bonus, correction, FnF, reimbursement-only, contractor payouts.
- Benefits deduction to payroll: group health premium, NPS, VPF, insurance, ESOP.
- Flexi-benefit tax optimization: HRA, LTA, fuel/driver, meal card, children education, internet/telephone.
- Payroll import/migration wizards: salary, bank, LOP, tax declarations, previous employment, reimbursements with dry-run and row-level errors.
- Payroll field audit: salary, bank, tax, statutory, payment, and run changes with masked before/after values.
- Multi-entity / multi-company payroll groups

Recommended build:
1. Complete payroll setup UI for employer/legal entity, statutory profile, pay group, and payroll period setup.
2. Finish formula dependency graph, circular dependency detection, caps/floors, residual components, and pro-rata calculations.
3. Deepen income tax engine: proof impact, regime comparison, HRA/LTA calculations, rebate/surcharge rules, and employee worksheet view.
4. Build statutory engine: PF/ESI/PT/LWF/gratuity rule tables, employee statutory profiles, contribution lines, challans, return files.
5. Build leave/attendance payroll input reconciliation: paid leave, unpaid leave, LOP, OT, regularization, month lock.
6. Build payroll worksheet and run lifecycle: collect inputs, calculate, validate, variance, approve, lock, publish.
7. Build arrears, off-cycle payroll, hold/skip employee, and retroactive correction support.
8. Build benefits/FBP/reimbursement/loan integration with taxable and non-taxable splits.
9. Build bank payment batches, UTR status import, and accounting/GL journal export.
10. Build payslip/Form 16 templates, compliance calendar, field audit, and import/migration wizards.

### 5. Recruitment and Onboarding

Already present:
- Jobs, candidates, resume upload/parser
- Interviews, feedback, offers
- Onboarding templates, tasks, employee onboarding

Missing versus Keka/Zoho/Darwinbox/Workday/SuccessFactors:
- Hiring requisition approval and workforce plan linkage
- Candidate applications per job (many-to-many)
- Career site/job publishing (public)
- Source analytics and funnel conversion
- Structured scorecards/interview kits
- Offer approval workflow and e-sign
- Candidate-to-employee conversion
- New-hire portal and document collection
- Onboarding task inbox and auto-assignment
- Background verification integration (AuthBridge, HireRight, IDfy)
- Interview scheduling with Google/Outlook calendar sync
- Employee referral tracking (referrer, bonus, payout)

Recommended build:
1. Add requisitions and candidate applications.
2. Add candidate-to-employee conversion.
3. Add onboarding document collection.
4. Add BGV connector (AuthBridge/IDfy API).
5. Add Google Calendar OAuth for interview slot sync.
6. Add employee referral model and tracking.
7. Add career site publishing later.

### 6. Documents, Policies, and Offboarding

Already present:
- Document templates, generated documents, company policies
- Company policy version history
- Employee documents, expiry, and verification workflow
- Employee certificates and verification
- Exit records and checklist items, F&F settlement foundation

Missing versus Zoho/Keka/BambooHR:
- Rich template editor and PDF rendering
- Template version history
- Built-in e-sign or DocuSign/AadharSign/eMudhra integration
- Exit interview forms and F&F linkage
- Access revocation checklist and clearance ownership
- Experience letter and NOC auto-generation on exit approval
- DigiLocker push for issued certificates

Recommended build:
1. Add template versioning and PDF rendering.
2. Add document expiry dashboard and reminders.
3. Add e-sign integration hook (AadharSign for India compliance, DocuSign/HelloSign fallback).
4. Connect exit to assets/access revocation checklist UI.
5. Add DigiLocker push hook for certificates.

### 7. Performance, OKRs, Learning, and Compensation

Already present:
- Appraisal cycles, goals, reviews, employee skills

Missing versus Workday/SuccessFactors/Keka/Zoho/Darwinbox/Lattice:
- Goal check-ins and OKR alignment tree
- 360-degree reviews and peer feedback orchestration
- Review templates/questions and calibration
- Continuous feedback, praise, one-on-ones
- Nine-box, succession, career paths
- LMS course catalog, assignments, certifications with expiry
- SCORM player and xAPI support
- Skills-based organization: competency framework, role-skill mapping, skills gap report, upskilling paths
- Compensation cycles, merit planning, pay bands, pay equity analytics
- Manager effectiveness scores (Lattice, HiBob)

Recommended build:
1. Add goal check-ins and review templates.
2. Add 360 feedback orchestration.
3. Add LMS/certification module with SCORM support.
4. Add competency framework and skills gap report.
5. Add compensation planning after payroll stabilizes.

### 8. Helpdesk, Engagement, and Employee Experience

Already present:
- Categories, tickets, replies, internal notes
- SLA due dates, escalation rules, knowledge base
- Basic AI reply suggestion

Missing versus Zoho/Keka/Darwinbox/BambooHR/Workday Peakon:
- Category owner routing
- SLA analytics and breach dashboard UI
- CSAT/feedback after closure
- Employee announcements and notice board
- Pulse/eNPS surveys with trend analysis
- Rewards and recognition with points/badges
- Collaboration/social wall (work anniversaries, birthdays, shout-outs)
- Employee wellbeing module: burnout risk, mood check-in, mental health resources
- Manager effectiveness surveys (360 on manager)

Recommended build:
1. Add SLA/category ownership UI and breach dashboard.
2. Add AI source-grounded suggestions using knowledge articles.
3. Add CSAT.
4. Add announcements, social wall, recognition feed.
5. Add engagement surveys (eNPS) with trend analysis.
6. Add wellbeing pulse survey linked to overtime/attendance signals.

### 9. WhatsApp ESS and Conversational HR

*Foundation exists; production-grade WhatsApp Business flows remain a high-value India differentiator.*

Missing versus factoHR / sumHR / HRMantra / Qandle:
- Production WhatsApp Business API connector with template registration and webhook verification
- Outbound leave approval notifications and manager approve/reject CTA buttons
- Robust command parser for leave, payslip, attendance, holiday, balance, and policy queries
- Attendance punch via WhatsApp with GPS and shift validation
- Delivery/read callback tracking and retry handling
- HR policy QA through the WhatsApp channel
- Onboarding document submission via WhatsApp

Recommended build:
1. Integrate WhatsApp Business API (Meta Cloud API or Twilio).
2. Build NLP intent router: leave-apply, leave-balance, payslip, attendance, holiday-list, policy-qa.
3. Add WhatsApp session handler with employee phone number → user mapping.
4. Surface manager approval CTAs as WhatsApp interactive buttons.
5. Expose AI policy QA through WhatsApp channel.

### 10. Benefits Administration

*Foundation exists; claims, taxation, and payroll worksheet integration remain versus ADP/SuccessFactors/BambooHR/Keka.*

Missing versus all top 10:
- Benefit claim submission, approval, limits, and employer cost reporting
- Detailed tax treatment for flexi-benefits, NPS, reimbursements, and exemptions
- Payroll worksheet integration for premium deductions and employer contributions
- ESOP/RSU plan and vesting schedule tracking
- Term life and accident insurance policy tracking depth
- Employee-facing benefit elections and life-event change requests

Recommended build:
1. Add benefit plan types (health, life, NPS, flexi, ESOP).
2. Add employee enrollment and premium amounts.
3. Link premium deduction to payroll component.
4. Add ESOP/RSU vesting schedule model.
5. Add benefit claim and cost report.

### 11. Reports, Analytics, and AI

Already present:
- Dashboard stats; headcount, attendance, leave, payroll, turnover, recruitment funnel reports
- AI assistant, policy QA, resume parsing, attrition risk, payroll anomaly, helpdesk reply

Missing versus top 10 (Workday, SuccessFactors, HiBob, ADP DataCloud):
- Custom report builder with saved filters and scheduled exports
- Excel/PDF exports across all modules
- Governed metric definitions
- Drill-down people analytics with cohort filters
- DE&I analytics: gender pay gap, representation by level/dept
- Span of control and management effectiveness metrics
- Audit-ready reports (SOC2, DPDP)
- AI usage audit, prompt versions, confidence/source citations, human-review controls
- Persisted prediction scores and model governance
- Compensation benchmarking against external salary data (ADP DataCloud equivalent)

Recommended build:
1. Add export layer to current reports (XLSX/PDF).
2. Add saved report definitions and scheduler.
3. Add governed metric definitions.
4. Add DE&I and span-of-control analytics.
5. Add AI audit logs and source-cited policy QA.

### 12. Platform, Security, and Enterprise Readiness

Already present:
- JWT auth, roles, permissions
- Audit middleware/model
- Some route-level `RequirePermission` usage

Missing versus enterprise products (Workday, SAP, Darwinbox, ADP):
- Scoped RBAC: own/team/department/branch/company/all
- Sensitive-field masking and view audit
- MFA/OTP, session/device management
- Password policy, lockout, IP restrictions
- Field-level audit for salary, bank, PAN, Aadhaar, manager, designation
- Maker-checker for payroll, bank, salary, role changes
- Data retention, consent, privacy requests, legal hold
- DPDP (India Digital Personal Data Protection Act) posture artifacts
- SOC2 readiness artifacts
- Admin audit viewer
- SSO (SAML/OIDC) for enterprise login (Workday, Darwinbox)

Recommended build:
1. Add scoped permissions and sensitive masking.
2. Add field-level audit.
3. Add session/MFA controls.
4. Add privacy/retention workflows and DPDP consent model.
5. Add SSO (SAML) for enterprise customers.

---

## Competitive Scorecard (Top 10)

| Area | Current ERP | Workday | SAP SF | ADP | UKG | BambooHR | Keka | Zoho | greytHR | Darwinbox | Gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Core HR | Strong foundation | Enterprise | Enterprise | Strong | Strong | Strong | Strong | Strong | Strong | Enterprise | Low/medium |
| Organization depth | Basic | Enterprise | Enterprise | Medium | Medium | Medium | Medium | Medium | Medium | Enterprise | High |
| Leave | Strong foundation | Strong | Strong | Strong | Strong | Strong | Strong | Strong | Strong | Strong | Medium |
| Attendance | Foundation | Strong | Medium | Medium | Enterprise | Medium | Strong | Strong | Strong | Strong | Medium/high |
| Payroll India | Strong foundation | Via partner | Via partner | Via partner | Via partner | — | Strong | Via Zoho Payroll | Strong | Strong | Medium/high |
| Form 16 / statutory | Foundation | N/A | N/A | N/A | N/A | - | Present | Present | Present | Present | P0 |
| EPFO/ESIC portal | Tracking foundation | N/A | N/A | N/A | N/A | - | Present | Present | Present | Present | P0 |
| Recruitment | MVP | Strong | Strong | Strong | Medium | Medium | Strong | Strong | Present | Strong | Medium/high |
| Onboarding | MVP | Strong | Strong | Strong | Medium | Strong | Strong | Strong | Medium | Strong | Medium/high |
| Documents/e-sign | Foundation | Strong | Strong | Medium | Medium | Strong | Medium | Strong | Medium | Strong | Medium/high |
| Performance/OKR | MVP | Enterprise | Enterprise | Medium | Medium | Medium | Strong | Strong | Medium | Strong | High |
| LMS | Foundation | Present | Enterprise | Medium | - | - | Present | Present | Limited | Present | High |
| Benefits | Foundation | Enterprise | Enterprise | Enterprise | Strong | Strong | Medium | Medium | - | Medium | Very high |
| Engagement | Foundation | Enterprise | Enterprise | Medium | Medium | Strong | Strong | Strong | Present | Strong | Very high |
| WhatsApp ESS | Foundation | - | - | - | - | - | - | - | Present | - | Critical (India) |
| Biometric integration | Missing | — | — | — | Enterprise | — | Present | Present | Present | Present | High |
| Skills-based org | Missing | Enterprise | Enterprise | — | — | Medium | Medium | Medium | — | Medium | High |
| Wellbeing | Missing | Enterprise | — | — | Strong | Strong | — | — | — | Medium | High |
| Helpdesk | Foundation | — | — | — | — | — | Present | Strong | Limited | Strong | Medium |
| Analytics | Basic | Enterprise | Enterprise | Strong | Strong | Strong | Strong | Strong | Medium | Strong | High |
| DE&I analytics | Missing | Enterprise | Enterprise | Strong | — | Strong | — | — | — | Medium | High |
| Workflow automation | Inbox only | Enterprise | Enterprise | Strong | Strong | Medium | Strong | Strong | Medium | Enterprise | High |
| Mobile ESS | Web-first | Strong | Strong | Strong | Enterprise | Strong | Strong | Strong | Strong | Strong | Very high |
| Integrations | Basic API | Enterprise | Enterprise | Marketplace | Enterprise | Medium | Marketplace | Zoho ecosystem | Marketplace | Enterprise | High |
| Security/compliance | Partial | Enterprise | Enterprise | Strong | Strong | Medium | Strong | Strong | Strong | Enterprise | Medium/high |
| DPDP/India privacy | Missing | — | — | — | — | — | — | — | — | — | High |
| SSO / SAML | Missing | Present | Present | Present | Present | Present | Present | Present | — | Present | Medium |

---

## Updated Roadmap to Catch Up

### Completed: Trust Core
- Employee lifecycle history
- Leave overlap/balance ledger
- Attendance roster/weekly off/computation
- Payroll lock enforcement
- Scoped RBAC baseline and sensitive masking

### Completed: Daily HR Operations
- Workflow/task inbox, notifications
- Bulk employee import/export
- Leave calendar
- Payroll variance review

### Completed: India Payroll Database/API Strength
- Tax declarations and proofs
- Statutory report stubs and export tracking
- Loans/advances, F&F settlement
- Bank/accounting export stubs
- Salary revisions, payroll manual inputs, reimbursements, pre-run checks

---

### Sprint 1: Payroll Output and Statutory Compliance (P0)
- Payslip PDF generation and download
- Real statutory CSV/XLSX exports: PF ECR, ESI challan, PT challan, 24Q TDS, pay register
- Form 16 / Form 16A generation from TDS records
- Bank advice NEFT bulk upload file
- Payroll formula evaluator
- EPFO/ESIC portal submission integration
- Statutory compliance calendar with due-date alerts

### Sprint 2: Employee Experience and ESS (P1)
- Mobile-first ESS/PWA polish
- WhatsApp Business API: leave, payslip, attendance, policy QA conversational flows
- Manager dashboard with team widgets
- Profile change requests
- Helpdesk SLA dashboard and CSAT
- Announcements, social wall, recognition feed
- Pulse/eNPS surveys

### Sprint 3: Talent Suite and Benefits (P1)
- Benefits administration: group health, flexi-benefits, NPS, ESOP
- OKR check-ins and review templates
- 360 feedback orchestration
- LMS/course/certification module with SCORM
- Competency framework and skills gap report
- Compensation cycles and pay bands

### Sprint 4: Integrations and Enterprise Layer (P1/P2)
- Custom fields/forms
- Configurable workflow designer
- Webhooks/integration framework
- Biometric device import (ZKTeco/eSSL flat file)
- Background verification connector (AuthBridge/IDfy)
- Google/Outlook calendar sync for interviews
- Employee referral tracking

### Sprint 5: Analytics, Security, and Compliance (P2)
- Report builder and scheduled exports
- DE&I analytics and span-of-control metrics
- Field-level audit and masking hardening
- MFA/session/device management
- DPDP consent and privacy request workflows
- SSO/SAML for enterprise login
- Aadhaar e-KYC and DigiLocker integration

### Future Sprint: Domain Packs (P2)
- Technology company reports and workflows
- Manufacturing: canteen management, shift marketplace, contract labor
- BFSI: maker-checker depth, regulatory reporting
- Retail: multi-location attendance, flexi scheduling
- Healthcare: credential expiry, shift compliance
- Education: academic calendar integration, faculty load management

---

## What We Are Lacking vs Top 10 — Summary

The following are the most significant remaining gaps when benchmarked across all 10 competitors. Items marked "foundation complete" now have working database/API support, but still need deeper product polish before they match mature HRMS suites:

1. **WhatsApp ESS** — Unique India differentiator. 4/10 India-focused competitors offer this; global ones don't, but India SMB buyers expect it from local HRMS.
2. **Payslip PDF + Form 16** — Payslip PDF foundation is complete; Form 16 still needs final statutory template, employer details, TDS reconciliation, and digital-signature hook.
3. **EPFO/ESIC portal integration** — Core greytHR/factoHR selling point. Manual portal uploads are a daily pain for Indian HR teams.
4. **Benefits administration** — Foundation complete for group health/NPS/flexi-benefit style plans; claims, tax treatment, and payroll worksheet integration remain.
5. **LMS/Learning** — Foundation complete for course catalog, assignments, completions, and certifications; skill gaps, competency mapping, renewals, and dashboards remain.
6. **Employee engagement (eNPS, recognition, announcements)** — Foundation complete for announcements, surveys/responses, and recognition; eNPS scoring, anonymity controls, points, and dashboards remain.
7. **Skills-based organization and competency framework** — 5/10 competitors (weighted heavily by Workday/SuccessFactors) are pushing this as the future of HCM. Early advantage if built now.
8. **Employee wellbeing** — 4/10 competitors include dedicated wellbeing features. Growing buyer expectation.
9. **Mobile-first PWA** — PWA shell is complete; mobile-first page polish, offline-safe ESS forms, and push notifications remain.
10. **DE&I analytics** — 5/10 competitors surface gender/pay-equity dashboards. Missing from our reporting.
11. **Biometric device integration** — 6/10 India competitors support ZKTeco/eSSL. Missing.
12. **Background verification integration** — 5/10 competitors integrate BGV vendors. Missing from recruitment.
13. **Configurable workflow engine** — Engine foundation is complete; visual designer, conditions, SLA reminders, escalations, and cross-module field updates remain.
14. **Custom fields/forms** — 6/10 competitors sell this as a key differentiator. Missing.
15. **SSO/SAML** — 8/10 competitors support enterprise SSO. Missing.

---

## Best Differentiation Opportunity

Do not try to out-feature everyone immediately. The strongest positioning for this ERP is:

> India-first HRMS with payroll-grade correctness, WhatsApp-native ESS, AI-assisted HR operations, and configurable workflows for mid-market companies.

The next product advantage should be:
1. **Statutory accuracy** — Form 16, PF ECR, EPFO portal. Win the CFO/accountant trust.
2. **WhatsApp ESS** — Win the daily-use battle. Every employee already has WhatsApp.
3. **Benefits administration** — No India HRMS does this well. First-mover advantage.
4. **Skills intelligence** — Get ahead of Keka/greytHR by shipping competency framework + skills gap + AI upskilling paths before they do.

That sequence beats a broad-but-shallow engagement or LMS feature push.
