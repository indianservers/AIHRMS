# HRMS Competitor Gap Analysis

Date: 2026-05-01

This compares the current AI HRMS implementation with Keka HR, Zoho People, greytHR, Darwinbox, and the broader expectations of top HRMS/HCM suites.

## Reference Products

- Keka: HR, payroll, performance, hiring/onboarding, time and attendance, PSA/timesheets, LMS, marketplace, industry-specific packs, tax/expense, recognition, single-window approvals.
- Zoho People: recruitment, onboarding, employee management, attendance, shift management, leave, timesheets, helpdesk with SLA/knowledge base, document management with e-sign integrations, offboarding, performance, compensation, LMS, payroll/expense integrations, engagement, communication, analytics, workflow automation, mobile apps.
- greytHR: India-focused HR and payroll, leave, attendance, performance, ESS, engagement, recruitment, expense management, compliance resources, marketplace.
- Darwinbox: enterprise-grade mobile-first HRMS, configurable workflows, global workforce/legal entity support, payroll and expenses, talent acquisition, engagement, performance/OKRs/360 feedback, talent development, people analytics, audit-ready reports, enterprise security.

Sources checked: https://www.keka.com/, https://www.zoho.com/people/features.html, https://www.greythr.com/, https://explore.darwinbox.com/lp/hrms-software

## Current Product Position

The ERP has a broad HRMS MVP skeleton. It already contains backend models, APIs, and frontend routes for:

- Auth, roles, permissions
- Company, branch, department, designation
- Employee master with profile, job, statutory, bank, education, experience, skills, documents
- Leave types, balances, requests, approval/cancel
- Attendance shifts, holidays, punch in/out, regularization, monthly summary
- Payroll components, structures, employee salary, payroll run, payslip, reimbursements
- Recruitment jobs, candidates, interviews, feedback, offers, AI resume parsing
- Onboarding templates/tasks, policy acknowledgement
- Documents, policies, generated documents
- Performance cycles, goals, reviews
- Helpdesk categories, tickets, replies, AI suggested reply
- Reports dashboard and standard module reports
- Assets, exit, target catalog, AI assistant

The gap is not "missing modules" as much as "missing production depth". Keka, Zoho, greytHR, and Darwinbox compete by making daily workflows configurable, compliant, mobile-friendly, auditable, and integrated end to end.

## Highest Impact Gaps

| Priority | Gap | Why it matters | Current state |
| --- | --- | --- | --- |
| P0 | Workflow engine and notification inbox | Competitors route leave, payroll, onboarding, helpdesk, documents, and approvals through configurable workflows and single-window approval queues. | Approvals are hardcoded per module. No reusable workflow instance/task model. |
| P0 | Employee lifecycle history | HRMS buyers expect joining, probation, confirmation, transfer, promotion, manager change, salary revision, and exit timelines. | Employee record has current fields but little effective-dated history. |
| P0 | Leave and attendance correctness | This directly affects payroll trust. | Basic leave/attendance exists, but accrual jobs, carry-forward, overlap hardening, roster/weekly off, late/early computation, lock, and payroll integration are incomplete. |
| P0 | Payroll compliance depth | Keka/greytHR win heavily on India payroll and statutory confidence. | Payroll run exists, but formula engine, tax declarations/proofs, PF/ESI/PT reports, loans/advances, F&F, variance review, accounting export, and true post-lock immutability are missing. |
| P0 | RBAC/data scope/security hardening | HR and payroll data need strict own/team/department/branch/company scopes. | Roles/permissions exist, but scoped permissions, route audit, sensitive field masking, MFA/session controls are incomplete. |
| P1 | Mobile/ESS experience | Competitors emphasize mobile leave, attendance, payslips, documents, approvals, and self-service. | Frontend exists, but no native/PWA mobile-first employee workflows, profile change approvals, or notification center. |
| P1 | HR automation/custom fields/forms | Zoho and Darwinbox sell configurable forms, workflow automation, field updates, webhooks, and custom services. | Mostly static schemas and hardcoded module flows. |
| P1 | Engagement/culture | Recognition, pulse surveys, eNPS, announcements, social/collaboration are visible competitor differentiators. | Mostly absent except helpdesk/performance skeletons. |
| P1 | Learning and skill development | Keka, Zoho, Darwinbox include LMS/talent development. | Employee skills exist, but no courses, assignments, certifications, skill gaps, competency framework. |
| P1 | Integrations/marketplace | Buyers expect biometric, accounting, email/calendar, e-sign, payroll banks, Slack/Teams, APIs/webhooks. | API exists, but connector framework/webhooks/import-export jobs are missing. |

## Module-by-Module Gap

### 1. Core HR and Organization

Already present:
- Company, branch, department, designation
- Employee master with personal/job/bank/statutory/profile fields
- Reporting manager field
- Employee education, experience, skills, documents

Missing versus top HRMS:
- Multi-tenant architecture
- Legal entities separate from companies
- Business units, cost centers, locations, grades/bands, job families, job profiles
- Position management and vacancy/headcount slots
- Effective-dated assignments and transfer history
- Manager hierarchy validation and org chart
- Bulk import/export with row-level validation
- Dynamic custom fields and custom forms
- Employee profile change requests with approval

Recommended build:
1. Add employee lifecycle/event tables.
2. Add business unit, cost center, grade/band, position.
3. Add org chart and bulk import/export.
4. Add custom fields only after core history is stable.

### 2. Leave Management

Already present:
- Leave types
- Leave balances
- Apply, list, approve, cancel
- Basic gender/applicability, carry-forward, encashable flags

Missing versus Keka/Zoho/greytHR:
- Accrual schedules and monthly/year-end jobs
- Balance ledger for every credit/debit
- Overlap prevention across pending/approved requests
- Holiday/weekend-aware day calculation
- Leave calendar and team view
- Comp-off claims and expiry
- Multi-level approvals, delegation, escalation
- Attachments and document-required rules
- Leave encashment linked to payroll

Recommended build:
1. Add leave ledger and overlap/balance enforcement.
2. Add accrual/carry-forward processor.
3. Add calendar/team views.
4. Move approval to shared workflow engine.

### 3. Attendance and Workforce Management

Already present:
- Shifts and holidays
- Web punch in/out
- Attendance records with IP/location fields
- Regularization request/approval
- Monthly summary
- Overtime request model

Missing versus competitors:
- Shift rosters, rotations, split/night-shift edge cases
- Weekly off rules and alternate Saturdays
- Late/early/short-hours computed flags
- Multiple punch events per day with audit trail
- Geo-fence, selfie, QR, biometric import
- Attendance lock by month
- On-duty/field visit workflow
- Payroll LOP and OT integration
- Mobile/offline attendance for field/retail

Recommended build:
1. Split raw punch events from computed daily attendance.
2. Add roster and weekly-off configuration.
3. Add computation job for status, late, early, OT, LOP.
4. Add biometric import and mobile geo-punch later.

### 4. Payroll, Expense, and Compliance

Already present:
- Salary components and structures
- Employee salary assignment
- Payroll run and records
- Payroll approval/lock fields
- Payslip endpoint
- Reimbursements
- AI anomaly flag fields

Missing versus Keka/greytHR:
- Robust formula engine and component dependency handling
- Payroll lock enforcement across all mutation APIs
- Tax declarations, proof submission, HRA/LTA/80C workflows
- Loans and advances
- Full and final settlement
- Statutory reports: PF, ESI, PT, TDS, LWF, gratuity
- Bank advice/payment export
- Accounting/GL export by cost center
- Payroll variance review UI
- Arrear/revision processing

Recommended build:
1. Enforce payroll lock and add variance review.
2. Add tax declaration/proof workflow.
3. Add statutory report exports.
4. Add F&F and accounting export.

### 5. Recruitment and Onboarding

Already present:
- Jobs, candidates, resume upload/parser
- Interviews, feedback, offers
- Onboarding templates, tasks, employee onboarding

Missing versus Keka/Zoho/Darwinbox:
- Hiring requisition approval and workforce plan linkage
- Candidate applications per job
- Career site/job publishing
- Source analytics and funnel conversion
- Structured scorecards/interview kits
- Offer approval workflow and e-sign
- Candidate-to-employee conversion
- New-hire portal and document collection
- Onboarding task inbox and auto-assignment

Recommended build:
1. Add requisitions and candidate applications.
2. Add candidate-to-employee conversion.
3. Add onboarding document collection.
4. Add career site later.

### 6. Documents, Policies, and Offboarding

Already present:
- Document templates
- Generated documents
- Company policies
- Employee documents
- Exit records and checklist items

Missing versus Zoho/Keka:
- Rich template editor and PDF rendering
- Template version history
- E-sign integration
- Policy versioning and policy-specific acknowledgement
- Document expiry alerts/dashboard
- Verification workflow
- Exit interview forms and F&F linkage
- Access revocation checklist and clearance ownership

Recommended build:
1. Add policy/template versioning.
2. Add document expiry and verification workflow.
3. Add e-sign integration hook.
4. Connect exit to assets, payroll F&F, and access checklist.

### 7. Performance, OKRs, Learning, and Compensation

Already present:
- Appraisal cycles
- Goals
- Reviews
- Employee skills

Missing versus Keka/Zoho/Darwinbox:
- Goal check-ins and OKR alignment
- 360-degree reviews and peer feedback orchestration
- Review templates/questions and calibration
- Continuous feedback, praise, one-on-ones
- Nine-box, succession, career paths
- LMS course catalog, assignments, certifications
- Compensation cycles, merit planning, pay bands, pay equity

Recommended build:
1. Add goal check-ins and review templates.
2. Add 360 feedback orchestration.
3. Add LMS/certification module.
4. Add compensation planning after payroll stabilizes.

### 8. Helpdesk and Employee Experience

Already present:
- Categories, tickets, replies, internal notes
- Basic AI reply suggestion

Missing versus Zoho/Keka/Darwinbox:
- SLA timers and breach tracking
- Category owner routing
- Escalation rules
- Knowledge base
- CSAT/feedback after closure
- Employee announcements
- Pulse/eNPS surveys
- Rewards and recognition
- Collaboration/social wall

Recommended build:
1. Add SLA/category ownership.
2. Add knowledge base and AI source-grounded suggestions.
3. Add CSAT.
4. Add engagement surveys and recognition.

### 9. Reports, Analytics, and AI

Already present:
- Dashboard stats
- Headcount, attendance, leave, payroll, turnover, recruitment funnel
- AI assistant, policy QA, resume parsing, attrition risk, payroll anomaly, helpdesk reply

Missing versus top HRMS:
- Custom report builder
- Saved filters and scheduled reports
- Excel/PDF exports across all modules
- Governed metric definitions
- Drill-down people analytics
- Audit-ready reports
- AI usage audit, prompt versions, confidence/source citations, human-review controls
- Persisted prediction scores and model governance

Recommended build:
1. Add export layer to current reports.
2. Add saved report definitions and scheduler.
3. Add metric definitions.
4. Add AI audit logs and source-cited policy QA.

### 10. Platform, Security, and Enterprise Readiness

Already present:
- JWT auth
- Roles and permissions
- Audit middleware/model
- Some route-level `RequirePermission` usage

Missing versus enterprise products:
- Scoped RBAC: own/team/department/branch/company/all
- Sensitive-field masking and view audit
- MFA/OTP, session/device management
- Password policy, lockout, IP restrictions
- Field-level audit for salary, bank, PAN, Aadhaar, manager, designation
- Maker-checker for payroll, bank, salary, role changes
- Data retention, consent, privacy requests, legal hold
- SOC2/GDPR/DPDP posture artifacts
- Admin audit viewer

Recommended build:
1. Add scoped permissions and sensitive masking.
2. Add field-level audit.
3. Add session/MFA controls.
4. Add privacy/retention workflows.

## Competitive Scorecard

| Area | Current ERP | Keka | Zoho People | greytHR | Darwinbox | Gap level |
| --- | --- | --- | --- | --- | --- | --- |
| Core HR | MVP | Strong | Strong | Strong | Enterprise | Medium |
| Organization depth | Basic | Medium/Strong | Medium | Medium | Enterprise | High |
| Leave | MVP | Strong | Strong | Strong | Strong | High |
| Attendance | MVP | Strong | Strong | Strong | Strong | High |
| Payroll India | MVP | Strong | Via Zoho Payroll/integration | Strong | Strong | Very high |
| Recruitment | MVP | Strong | Strong via Zoho Recruit | Present | Strong | Medium/high |
| Onboarding | MVP | Strong | Strong | Medium | Strong | Medium/high |
| Documents/e-sign | MVP | Medium/Strong | Strong | Medium | Strong | High |
| Performance/OKR | MVP | Strong | Strong | Medium | Strong | High |
| LMS | Missing | Present | Present | Limited/market | Present | High |
| Engagement | Missing | Strong | Strong | Present | Strong | Very high |
| Helpdesk | MVP | Present | Strong | Limited/present | Strong | Medium/high |
| Analytics | Basic | Strong | Strong | Medium | Strong | High |
| Workflow automation | Hardcoded | Strong | Strong | Medium | Enterprise | Very high |
| Mobile ESS | Web-first | Strong | Strong | Strong | Strong | Very high |
| Integrations | Basic API | Marketplace | Zoho + third-party | Marketplace | Enterprise | High |
| Security/compliance | Basic | Strong | Strong | Strong | Enterprise | High |

## Suggested Roadmap to Catch Up

### Sprint 1: Trust Core
- Employee lifecycle history
- Leave overlap/balance ledger
- Attendance roster/weekly off/computation
- Payroll lock enforcement
- Scoped RBAC baseline

### Sprint 2: Daily HR Operations
- Workflow/task inbox
- Notifications
- Bulk employee import/export
- Leave calendar
- Payroll variance review

### Sprint 3: India Payroll Strength
- Tax declarations and proofs
- Statutory reports
- Loans/advances
- F&F settlement
- Bank/accounting export

### Sprint 4: Employee Experience
- Mobile-first ESS/PWA polish
- Profile change requests
- Helpdesk SLA and knowledge base
- Announcements
- Pulse/eNPS and recognition

### Sprint 5: Talent Suite
- OKR check-ins
- Review templates and 360 feedback
- LMS/course/certification module
- Compensation cycles and pay bands

### Sprint 6: Enterprise Layer
- Custom fields/forms
- Workflow designer
- Webhooks/integration framework
- Field-level audit and masking
- Report builder and scheduled exports

## Best Differentiation Opportunity

Do not try to out-feature everyone immediately. The strongest positioning for this ERP is:

> India-first HRMS with payroll-grade correctness, AI-assisted HR operations, and configurable workflows for mid-market companies.

That means the next product advantage should be accuracy and automation in leave, attendance, payroll, and approvals before adding broad but shallow engagement or LMS features.
