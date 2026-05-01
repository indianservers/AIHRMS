# Target Gap Analysis

This compares `docs/targets.md` and `docs/mega_hrms_schema.md` against the current repo implementation.

## Summary

The application has a strong MVP skeleton: most major modules have models, APIs, and pages. The main missing work is depth: validations, workflow states, approval consistency, richer organization data, enterprise security, analytics, and domain-specific packs.

## Essential Automation

| Target area | Current coverage | Missing / partial |
| --- | --- | --- |
| Company/legal entity setup | Company, branch, department, designation models/APIs/UI exist. Active duplicate checks, parent validation, and focused tests exist. | Cost centers, business units, grades/bands, positions, job profiles, import/export, org chart. |
| Employee master | Employee profile, job info, statutory IDs, bank info, education, experience, skills, documents exist. | Dynamic profiles/custom fields, employee ID sequence config UI, lifecycle event history, transfer history, position history, bulk import, directory/org chart polish. |
| RBAC | Users, roles, permissions exist. | Scoped roles, permission templates, page-level guard audit, session/device tracking, privilege review. |
| Audit baseline | AuditLog model and middleware exist. | Field-level audit, sensitive data masking, object diff completeness, audit viewer UI. |
| Leave | Leave types, balances, requests, approval/cancel APIs exist. | Accrual automation, carry-forward processing, overlap/balance hardening, leave calendar, multi-level approvals, team view. |
| Attendance | Shifts, holidays, check-in/out, monthly summary, regularization exist. | Roster model, weekly offs, late/early computed fields, biometric import, geo/selfie attendance, team attendance view. |
| Payroll | Components, structures, salary assignment, payroll runs, records, approval, payslip, reimbursement exist. | Payroll lock enforcement, tax declarations/proofs, loans/advances, accounting export, formula engine, statutory reports, F&F automation. |
| Recruitment | Jobs, candidates, interviews, feedback, offers, resume upload/AI parser exist. | Requisition approval, hiring plans, scorecards, candidate applications table, career site, offer approval workflow. |
| Onboarding | Templates, tasks, employee onboarding, task completion, policy acknowledgement exist. | Candidate-to-employee conversion flow, document collection workflow, welcome checklist automation, assigned task inbox. |
| Documents | Templates, generated documents, policies, employee documents exist. | Policy acknowledgement linked directly to policy ID, version history, expiry dashboard, verification workflow UI, e-sign support. |
| Performance | Cycles, goals, reviews exist. | Goal check-ins, reviewer assignment workflow, review templates/questions, 360/peer orchestration, calibration, promotion/PIP. |
| Employee self-service | Profile, leave, attendance, payslip/document pages partially exist. | Notification inbox, strict self-service scoping, profile change requests, mobile-first flows. |
| Helpdesk | Categories, tickets, assignment, replies, internal notes, AI suggested reply exist. | SLA breach tracking, knowledge base, escalation rules, satisfaction workflow, category owner rules. |
| Reports | Dashboard, headcount, attendance, leave, payroll, turnover, recruitment funnel APIs exist. | Filterable report builder, exports, scheduled reports, metric definitions, reconciliation with module pages. |

## Strength Package

| Target area | Current coverage | Missing / partial |
| --- | --- | --- |
| Advanced Core HR | Basic company and employee hierarchy exists. | Multi-tenant/company hosting, legal entities separate from companies, business units, grades, bands, positions, job families, delegation, maker-checker. |
| Workforce management | Basic shifts, attendance, overtime model exist. | Rosters, rotations, split shifts, weekly offs, shift swaps, comp-off, continuous location punching, timesheets. |
| Payroll/compliance | Payroll model includes PF/ESI/PT/TDS fields and anomaly flags. | Variance checks UI, country/state compliance config, gratuity, benefits, perks, incentives, tax declaration cycle, payroll lock guard. |
| Recruitment maturity | Basic ATS exists. | Hiring plans, job approvals, panel management, structured scorecards, source analytics, offer approvals. |
| Learning | Employee skills exist. | Course catalog, training calendar, assignments, certifications, skill gaps. |
| Service delivery | Helpdesk exists. | Knowledge base, escalations, SLA timers, owner rules, case categories by policy. |
| Assets/travel | Asset inventory and assignment exist. | Travel requests, travel expenses, depreciation rules, asset repair lifecycle. |
| Employee experience | Not materially implemented. | Announcements, polls, surveys, praise, recognition, social wall, company values. |
| Security | Password auth and RBAC exist. | SSO, OTP/MFA, IP restrictions, session management UI, sensitive masking. |
| Analytics | Basic reports and AI risk endpoints exist. | Manager dashboards, absence analytics, compliance analytics, scheduled reports, people analytics drilldowns. |

## Growth Package

| Target area | Current coverage | Missing / partial |
| --- | --- | --- |
| Workflow automation | Hardcoded approvals exist in modules. | Generic workflow definitions, conditional/parallel approvals, form builder, custom objects. |
| Workforce planning | Not implemented. | Headcount plans, position budgets, scenarios, role forecasts, succession bench. |
| Business performance / OKRs | Performance goals exist. | Company/department OKR alignment map, check-ins, KPI ownership, insights. |
| Advanced performance | Basic review records exist. | Continuous feedback, one-on-ones, 360 orchestration, nine-box, succession, career paths. |
| Skills/learning intelligence | Employee skills exist. | Skills library, competency framework, role requirements, endorsements, recommendations. |
| Compensation | Payroll salary assignment exists. | Compensation cycles, merit planning, bonus planning, bands, pay equity, manager worksheets. |
| Engagement/culture | Not implemented. | Engagement surveys, anonymous feedback, eNPS, sentiment trends, awards. |
| AI/copilot | Assistant, policy Q&A, resume parser, attrition, payroll anomaly, helpdesk reply endpoints exist. | AI run audit, prompt management, summaries, goal/review assistants, human approval UX. |
| Integrations | API exists as backend. | Webhooks, accounting sync, email/calendar integrations, biometric connector, e-sign, import/export jobs. |

## Global Enterprise / Domain Packs

| Target area | Current coverage | Missing / partial |
| --- | --- | --- |
| Global core HR | Employee table supports basic worker data. | Tenants, persons/workers/employments split, worker types, localization, visas, global mobility. |
| Benefits/wellbeing | Not implemented. | Benefit plans, eligibility, enrollment, dependents, wellness, health checks. |
| Manufacturing | Basic attendance and overtime only. | Safety incidents, PPE, medical fitness, production shift handovers, contract labor. |
| Retail/field | Branches and work location exist. | Store staffing, field routes, geo attendance, offline sync, mobile tasks, transfers. |
| BFSI | Audit and RBAC basics exist. | Segregation of duties, regulatory certifications, attestations, evidence retention, maker-checker. |
| Healthcare | Not implemented. | Credentials, license expiry, vaccination, on-call rosters, department privileges. |
| Education | Employee profile has research fields only. | Faculty workload, course allocation, publications, grants, academic calendars. |
| Governance | Target catalog exists. | Feature flags, tenant config, data residency, consent, privacy requests, legal hold. |
| Analytics platform | Reports exist. | Metric definitions, dashboard builder, report definitions, data exports, prediction score persistence. |

## Highest-Priority Missing Items

1. Employee master completion: lifecycle events, manager hierarchy, bulk import, profile/document polish.
2. RBAC hardening: scoped access, page guards, role templates, permission verification tests.
3. Leave and attendance correctness: overlap validation, accrual/carry-forward, late/early flags, rosters.
4. Payroll reliability: lock enforcement, formulas, payroll variance checks, statutory/tax workflows.
5. Workflow/notification foundation: shared approval and task inbox model.
6. Audit/compliance depth: field audit, masking, audit viewer, sensitive change history.
7. Report/export layer: filters, exports, scheduled reports, metric definitions.
8. Learning and certifications: courses, assignments, certification expiry.
9. Domain packs: manufacturing, retail/field, BFSI, healthcare, education tables and workflows.

## Recommended Next Build Order

1. Complete Employee Master and hierarchy integration.
2. Stabilize RBAC and audit.
3. Finish Leave correctness.
4. Finish Attendance correctness.
5. Finish Payroll MVP.
6. Add shared workflow and notifications.
7. Add reporting/export maturity.
8. Add learning/certification module.
9. Add first domain pack based on target customer.
