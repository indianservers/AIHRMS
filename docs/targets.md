# AI HRMS Target Domains and Feature Catalog

This target catalog is based on feature patterns visible across leading HRMS/HCM suites: Workday, SAP SuccessFactors, Oracle Fusion Cloud HCM, ADP Workforce Now, UKG Pro, Rippling, BambooHR, Zoho People, Darwinbox, Keka, and HiBob.

## Benchmark Notes

| Product | Feature direction to learn from |
| --- | --- |
| Workday HCM | Global core HCM, skills cloud, workforce agility, scalable talent data, analytics. |
| SAP SuccessFactors | Global core HR, AI-assisted skills and people insights, talent development, compliance. |
| Oracle Fusion Cloud HCM | Unified HCM suite, AI-driven employee success, payroll, benefits, talent, workforce management. |
| ADP Workforce Now | HR, payroll, time, benefits, compliance, AI payroll anomaly detection. |
| UKG Pro | HR, payroll, workforce management, frontline hiring, employee experience. |
| Rippling | Unified HR, IT, finance, payroll, benefits, ATS, performance, surveys, automation. |
| BambooHR | Employee records, onboarding, documents, time off, performance, payroll and benefits add-ons. |
| Zoho People | Mobile HRMS, leave, attendance, timesheets, performance, analytics, integrations, field tracking. |
| Darwinbox | Enterprise HCM, talent acquisition, payroll and expenses, engagement, feedback, analytics. |
| Keka | India-focused HR, payroll, leave, attendance, workflows, compliance, performance. |
| HiBob | People analytics, hiring, learning, payroll, compensation, workforce planning, culture. |

## Target Domains

| Domain | Positioning | Product emphasis |
| --- | --- | --- |
| Technology and Services | HCM for white-collar, project-based, and hybrid teams. | Skills, goals, performance, helpdesk, payroll, analytics, project-friendly profiles, AI assistant. |
| Pharma and Manufacturing | HR and payroll for blue-collar and white-collar workforces. | Shift roster, overtime, biometric attendance, statutory compliance, safety, health, training compliance. |
| BFSI | HCM and payroll for audit-heavy organizations. | RBAC, maker-checker approvals, audit logs, policy attestations, payroll lock, document control, certification tracking. |
| Retail and Field Teams | Central HR platform for stores, field staff, and distributed teams. | Mobile self-service, geo attendance, store staffing, transfers, field routes, helpdesk, announcements. |
| Healthcare | Workforce platform for clinical and non-clinical staff. | Duty roster, on-call schedules, license expiry, vaccination, occupational health, credentials. |
| Education | HRMS for faculty, staff, researchers, and administrators. | Faculty workload, course allocation, research profile, publications, grants, academic calendars. |
| Public Sector and NGOs | Policy-heavy HR with grants, field staff, and regional offices. | Compliance documents, donor/project allocation, field attendance, policy acknowledgement, audit-ready records. |

## Feature Packages

### Essential Automation

This is the minimum production-grade HRMS base:

- Core HR: company/legal entity setup, branch/location/department/cost center/designation hierarchy, employee master, dynamic profiles, lifecycle status, probation, reporting manager, org chart, directory, custom fields, bulk import, employee ID sequencing, RBAC, permission templates, audit baseline.
- Time and Attendance: leave policy, accruals, applications, approval workflow, holiday calendar, check-in/out, register, shifts, grace minutes, monthly summary, regularization, team view, late and early flags.
- Payroll and Expense: salary components, salary structures, employee salary assignment, monthly payroll, approval, payslip, deductions, statutory identifiers, reimbursement capture, payroll reports.
- Recruitment: requisitions, openings, candidate database, candidate stages, resume upload, interview scheduling, interview feedback, offer creation.
- Onboarding: templates, joining tasks, policy acknowledgement, document collection, welcome checklist.
- Documents: templates, employee repository, generated letters, policy library, expiry tracking, verification status.
- Performance: cycles, individual goals, goal progress, reviews, reviewer assignment, ratings.
- Employee Self Service: email login, profile self-service, leave, attendance, payslip, documents, notification inbox.
- Helpdesk: categories, tickets, assignment, statuses, replies, AI suggested replies.
- Reports and Analytics: headcount, department, attendance, leave, payroll, recruitment funnel.

### Strength

This package adds mature operations:

- Advanced Core HR: multi-company, business units, grades, bands, positions, job profiles, delegation, maker-checker, approval chains, advanced audit, data retention.
- Workforce Management: advanced rosters, rotations, split shifts, weekly offs, swaps, overtime, comp-off, selfie attendance, geo fence, continuous location punching, biometric integration, timesheets.
- Payroll and Compliance: payroll lock, variance checks, anomaly detection, loans, advances, perks, benefits, gratuity, incentives, F&F, accounting integration, country/state compliance, tax declarations.
- Recruitment and TA: hiring plans, job approvals, career site readiness, sources, resume parsing, panel management, scorecards, offer approvals.
- Learning: course catalog, training calendar, assignments, certifications, skill gaps.
- Service Delivery: HR case management, SLA, knowledge base, queries, escalation, internal comments.
- Assets and Travel: inventory, assignment, return, condition tracking, travel requests and expenses.
- Employee Experience: announcements, polls, pulse surveys, praise, recognition badges, social wall, company values.
- Security: SSO, OTP, MFA readiness, IP restrictions, sessions, privilege review, sensitive masking.
- Analytics: people analytics, attrition risk, absence, payroll variance, compliance, manager dashboards, scheduled reports.

### Growth

This package targets business and talent advantage:

- Workflow Automation: no-code workflow builder, triggers, conditional/parallel approvals, escalation, form builder, custom objects, report builder.
- Workforce Planning: headcount plan, position budget, scenarios, role forecast, attrition impact, mobility, succession bench.
- Business Performance: company OKRs, department goals, individual goals, alignment map, check-ins, insights, KPI ownership.
- Employee Performance: continuous feedback, one-on-one, 360 feedback, self/manager/peer reviews, promotion recommendations, PIP, nine-box, succession, career pathing.
- Skills and Learning Intelligence: skills library, competency framework, role requirements, skill matrix, endorsements, history, analytics, recommendations, opportunity marketplace.
- Compensation: bands, salary review cycles, merit planning, bonus planning, equity tracking, budgets, pay equity, manager worksheets.
- Engagement and Culture: engagement surveys, anonymous feedback, eNPS, sentiment trends, recognition programs, awards, culture analytics.
- AI and Copilot: assistant, policy Q&A, resume parser, attrition predictor, payroll anomaly detector, helpdesk reply generator, summaries, goal and review assistants.
- Integrations: API, webhooks, accounting, email, calendar, ATS, LMS, biometric, e-sign, import/export jobs.

### Global Enterprise

This package makes the product domain-neutral:

- Global Core HR: multi-country worker records, worker types, contingent workforce, localization, global mobility, visa and immigration.
- Benefits and Wellbeing: plans, eligibility, enrollment, insurance dependents, wellness, health checks, EAP, wellbeing analytics.
- Industrial Workforce: factory staffing, production shift handover, safety incidents, PPE, medical fitness, training compliance, contract labor.
- Retail and Field Workforce: store staffing, area hierarchy, field routes, beat plans, geo attendance, offline capture, mobile tasks, store transfer.
- BFSI and Regulated Workforce: maker-checker, SoD, fit and proper checks, regulatory certifications, attestations, locks, evidence retention.
- Healthcare Workforce: credentials, license expiry, duty roster, on-call scheduling, department privileges, vaccination, occupational health.
- Education Workforce: academic departments, faculty workload, course allocation, research profile, publications, grants, academic calendar.
- Governance: tenant config, feature flags, domain packs, data residency, consent, privacy requests, legal hold, field audit, data quality, master data.
- Analytics: workforce data lake, metric definitions, dashboard builder, predictive models, cost, productivity, diversity, compliance analytics.

## Implementation in This Repo

The `/api/v1/targets/*` endpoints expose:

| Table | Purpose |
| --- | --- |
| `industry_targets` | Stores target domain cards and positioning. |
| `feature_plans` | Stores package tiers such as Essential, Strength, Growth, and Global Enterprise. |
| `feature_catalog` | Stores module-level capabilities linked to feature plans. |

The seed data in `backend/app/db/init_db.py` now loads the full roadmap into `feature_catalog`. Existing databases can be re-seeded by running the app database initialization; new features are additive because the seed checks `plan_id`, `module`, and `name` before inserting.

## Source Pointers

- Workday HCM: https://www.workday.com/en-us/products/human-capital-management/overview.html
- SAP SuccessFactors Employee Central: https://www.sap.com/products/hcm/employee-central-hris/features.html
- Oracle Cloud HCM: https://www.oracle.com/human-capital-management/cloud-expansion/
- ADP Workforce Now: https://www.adp.com/what-we-offer/products/adp-workforce-now.aspx
- UKG Pro: https://www.ukg.com/products/ukg-pro
- Rippling HRIS: https://www.rippling.com/products/global/global-hris
- BambooHR: https://www.bamboohr.com/
- Zoho People: https://www.zoho.com/people/features.html
- Darwinbox: https://explore.darwinbox.com/lp/hcm-software
- Keka: https://www.keka.com/hr-software
- HiBob HRMS: https://www.hibob.com/hrms-software/
