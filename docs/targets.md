# AI HRMS Target Domains and Feature Packages

## Target Domains

| Domain | Positioning | Product emphasis |
| --- | --- | --- |
| Technology & Services | HCM for technology and white collar services companies where employee experience is essential. | Skills, goals, performance, helpdesk, payroll, analytics, project-friendly profiles. |
| Pharma & Manufacturing | HR and payroll for mixed blue-collar and white-collar workforces. | Shift management, overtime, statutory compliance, attendance regularization, documents, safety and health data. |
| Banks & Financial Services | HCM and payroll for compliance-heavy organizations with audit requirements. | RBAC, audit logs, maker-checker approvals, payroll lock, policy records, controlled document workflows. |
| Retail & Other Industries | Central HR platform for store, field, and distributed teams. | Mobile self-service, geo attendance, store staffing, leave, issue resolution, always-on updates. |

## Employee Experience Targets

| Target | Expected capability |
| --- | --- |
| Simplified leave and attendance | Employees can clock in, regularize attendance, and apply leave remotely, in-office, or on field. |
| Tax and expense in 2 clicks | Employees submit declarations, proofs, expenses, and reimbursements with simple guided flows. |
| Culture of recognition | Employees and managers give public praise, feedback, and recognition badges. |
| Approvals from a single window | Managers approve leave, attendance, payroll, claims, helpdesk, and documents from one queue. |
| Adaptable employee home | Employees can prioritize preferred features on the main screen based on role and domain. |
| Faster issue resolution | HR helpdesk supports ticket categories, SLA tracking, and AI suggested replies. |

## Feature Packages

### Essential Automation

Core HR: org structure, documents and letters, basic onboarding, dynamic employee profiles, standard access roles, employee exit, basic notifications, basic reports.

Time and Attendance: leave management, attendance tracking, overtime automation, basic shift management.

Payroll and Expense: payroll automation, statutory compliance, accounting integration, loans and salary advances, perks and benefits, expense management, employee tax management, gratuity management.

Employee Self Service: email signup, mobile app readiness, notification inbox.

Employee Experience: social wall, polls, announcements, public praise.

### Strength

Adds advanced onboarding, e-signature readiness, travel desk, asset tracking, people analytics, employee timeline, custom roles and privileges, exit surveys, advanced notification engine, advanced reports, selfie clock-in, continuous location punching, geo fencing, SSO, mobile OTP login, employee pulse, and surveys.

### Growth

Adds workflow automation, custom report builder, headcount planning, pre-boarding, company goals and OKRs, department and individual goals, goal alignment, goal insights, core values, praise and recognition, continuous feedback, one-on-one meetings, performance reviews, calibration, promotions, PIP, compensation plans, skills, competencies, and skill analytics.

## Database Tables Added

| Table | Purpose |
| --- | --- |
| `industry_targets` | Stores domain positioning cards and ordering. |
| `feature_plans` | Stores package tiers such as Essential, Strength, and Growth. |
| `feature_catalog` | Stores module-level capabilities linked to feature plans. |

The new `/api/v1/targets/*` APIs expose CRUD operations for industry targets, plans, and features.
