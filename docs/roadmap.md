# AI HRMS Step-by-Step Roadmap

Industry reference: Workday · SAP SuccessFactors · Keka · Darwinbox · GreytHR · BambooHR · Zoho People · SmartRecruiters · ServiceNow HR.

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ DONE | Fully implemented and tested |
| 🔄 IN PROGRESS | Partially implemented, active sprint |
| ⬜ PENDING | Not yet started |

---

## Current Baseline

All major backend models, schemas, APIs, and frontend pages exist for:
Auth · Roles · Permissions · Company Setup · Employees · Leave · Attendance · Payroll · Recruitment · Onboarding · Documents · Performance · Helpdesk · Reports · Assets · Exit · AI assistant · Target domain catalog.

The near-term job is not to create more modules. It is to make each module production-usable end to end.

## Build Rules

- Complete one workflow at a time: database → API → frontend → validation → permissions → tests.
- Keep MVP tables stable until the workflow is proven in the UI.
- Prefer practical India-focused HRMS defaults first.
- Add enterprise abstractions only when they unblock a real workflow.
- Every step should finish with build/test verification and a short demo path.

---

## Phase 1: Foundation MVP

### Step 1: Organization Setup ✅ DONE

**Goal:** Make company hierarchy usable by admins.

**Industry reference:** Keka, Darwinbox, GreytHR — multi-level legal entity → branch → department → designation tree with active/inactive lifecycle.

**What was built:**
- Company legal profile with CIN, PAN, TAN, GSTIN, registered address
- Branches with location and contact info
- Departments under branches
- Designations under departments
- Active/inactive management with parent-active guard
- Duplicate name checks at each level
- Frontend create / edit / deactivate flows for all four entities
- Required-field, empty-state, loading, and error-state handling
- Backend tests: static route resolution, duplicate prevention, parent validation

**Acceptance verified:**
- ✅ Admin can create company, branch, department, designation
- ✅ Duplicate names are rejected
- ✅ Child cannot be activated under an inactive parent
- ✅ Employees can reference this hierarchy

---

### Step 2: Employee Master ⬜ PENDING

**Goal:** Make employee records complete enough for end-to-end HR operations.

**Industry reference:** Workday Worker, Darwinbox Employee 360, BambooHR Employee Record, GreytHR Employee Module.

#### 2A — Core Profile
- [ ] Employee ID sequencing: configurable prefix + auto-increment (e.g. IS-2024-0001)
- [ ] Personal info: name (legal/preferred/alias), DOB, gender, marital status, blood group, nationality
- [ ] Emergency contact: name, relationship, phone, address
- [ ] Dependent details: spouse, children (for insurance/gratuity)
- [ ] Nominee details: PF nominee, gratuity nominee
- [ ] Photo upload with size/format validation
- [ ] Aadhaar (masked display, encrypted store), PAN, UAN, ESIC number, PF member ID
- [ ] Address: permanent and current (with PIN lookup)

#### 2B — Job Information
- [ ] Employment types: Permanent, Contract, Probation, Intern, Consultant, Part-Time, Retainer
- [ ] Join date, probation end date, confirmation date
- [ ] Branch / Department / Designation assignment (referencing Step 1 hierarchy)
- [ ] Reporting manager (with org tree traversal, prevent circular reporting)
- [ ] Work location (remote / on-site / hybrid)
- [ ] Employment status lifecycle: Active → Probation → Confirmed → Notice → Resigned → Terminated → Absconded → Retired

#### 2C — Bank and Payroll Fields
- [ ] Primary bank account: account number (encrypted), IFSC, bank name, branch name, account type
- [ ] Secondary account support for salary split
- [ ] IFSC validation against RBI bank master (or offline lookup)
- [ ] Salary structure assignment reference (links to Payroll Step 7)

#### 2D — Statutory Identifiers
- [ ] PF applicable flag + PF account number
- [ ] ESI applicable flag + ESI number
- [ ] Professional Tax state + PT slab auto-assignment
- [ ] Gratuity eligibility date (5-year threshold tracking)
- [ ] LWF (Labour Welfare Fund) applicability by state

#### 2E — History and Lifecycle Events
- [ ] Transfer history: date, from branch/dept/designation, to branch/dept/designation, reason, approved by
- [ ] Promotion/demotion history with salary change reference
- [ ] Manager change history with effective date
- [ ] Employment status change log (all transitions timestamped)
- [ ] Salary revision history (effective date, old CTC, new CTC, revision %)

#### 2F — Employee Directory
- [ ] Searchable employee list: name, ID, department, designation, manager, status
- [ ] Filter by branch, department, employment type, status, join date range
- [ ] Export to Excel/CSV
- [ ] Org chart visualization (SVG/D3 tree from manager chain)
- [ ] Employee 360 view: profile + job + payroll summary + leave summary + attendance summary + documents

#### 2G — Bulk Operations
- [ ] Bulk import via Excel template (with header mapping and row-level error report)
- [ ] Import validation: required fields, duplicate ID/email/PAN, reference integrity (branch/dept/designation must exist)
- [ ] Bulk status update (e.g. confirm all probationers past confirmation date)
- [ ] Bulk transfer (move a batch to another department)

#### 2H — Self-Service Edit Requests
- [ ] Employee can submit a change request for personal/bank details
- [ ] HR reviews and approves/rejects with comment
- [ ] Change log retains original and updated values

**Acceptance:**
- HR can onboard a complete employee record without touching the database
- All statutory fields are captured and validated
- Employee 360 view shows profile, job, payroll, leave, attendance, documents
- Bulk import processes 500 rows with row-level error reporting
- Org tree renders correctly for 3+ reporting levels

---

### Step 3: Authentication, Roles, and Permissions ⬜ PENDING

**Goal:** Make access control predictable and auditable before sensitive workflows expand.

**Industry reference:** Workday Security Groups, SAP SuccessFactors Role-Based Permissions, Darwinbox RBAC, BambooHR Access Levels.

#### 3A — Permission Catalog
- [ ] Module-level permission matrix: Leave · Attendance · Payroll · Recruitment · Performance · Documents · Reports · Admin
- [ ] Action-level granularity: View · Create · Edit · Delete · Approve · Export · Import
- [ ] Data-scope dimension: Own · Team (direct reports) · Department · Branch · Company · All
- [ ] Permission catalog stored in DB — addable without code changes
- [ ] Sensitive-field permissions: mask Aadhaar / PAN / bank account for non-privileged roles

#### 3B — Role Templates
- [ ] Super Admin: full access to all modules and settings
- [ ] HR Admin: full employee and module management, no system config
- [ ] HR Executive: limited to own-region employees
- [ ] Finance: payroll read + approve + export; no employee profile edit
- [ ] Recruiter: recruitment module full; employee read-only
- [ ] Manager: own-team read; leave/attendance approve; performance manage for direct reports
- [ ] Employee: self-service only (own profile, leave, attendance, payslip, documents)
- [ ] Auditor: read-only access to audit logs and reports; no write permissions

#### 3C — Page and Route Guards
- [ ] Every frontend route must check user permission before rendering
- [ ] API routes must enforce permission at controller level (not just middleware)
- [ ] 403 response must return structured error (module, action, reason)
- [ ] UI hides action buttons (Edit, Delete, Approve) when user lacks permission
- [ ] Navigation sidebar items hidden for inaccessible modules

#### 3D — Delegation of Authority
- [ ] Approver can delegate approval rights to another user for a date range (e.g. during leave)
- [ ] Delegation is time-boxed and auto-expires
- [ ] Delegation audit trail (who delegated, to whom, period, actions taken)

#### 3E — Session and Device Security
- [ ] Active session list visible to user (device, IP, last active, location)
- [ ] Force logout of specific session
- [ ] Session timeout config per role (e.g. Finance: 15 min idle, Employee: 4 hours)
- [ ] Concurrent session limit config
- [ ] Login attempt lockout after N failures with unlock via email/admin

#### 3F — Two-Factor Authentication
- [ ] OTP via email on login (configurable per role)
- [ ] OTP via SMS stub (integration hook for SMS gateway)
- [ ] Remember-device for N days option
- [ ] Admin can enforce MFA for specific roles (e.g. Payroll, Admin)

#### 3G — Audit and Access Review
- [ ] Login/logout audit log with IP, device, timestamp
- [ ] Failed login attempts log
- [ ] Permission change audit (who changed a role, what was added/removed)
- [ ] Quarterly access review report: role assignments with last login date
- [ ] Privilege review UI: list all users with sensitive permissions

**Acceptance:**
- Super Admin can create and manage all roles
- HR sees only HR-relevant modules; Finance sees only payroll
- Manager sees only own-team data
- Employee sees only self-service
- All routes return 403 with no data when permission is missing

---

### Step 4: Leave Management ⬜ PENDING

**Goal:** Complete the full leave cycle with India-compliant defaults.

**Industry reference:** Keka Leave, Darwinbox Leave, GreytHR Leave, Zoho People Leave.

#### 4A — Leave Type Configuration
- [ ] Standard leave types: Casual Leave (CL), Privilege Leave / Earned Leave (PL/EL), Sick Leave (SL), Maternity Leave (ML), Paternity Leave (PAT), Bereavement Leave, Marriage Leave, Compensatory Off (CO), Leave Without Pay (LWP)
- [ ] Per-type config: paid/unpaid, gender-restricted, documentation required, max days per application, max days per year, min advance notice days
- [ ] Leave type active/inactive toggle
- [ ] Carry-forward rules: max days to carry, expiry date for carried-over balance, auto-lapse config
- [ ] Leave encashment rules: encashable flag, max encashable days, payout linked to payroll run
- [ ] Pro-rata accrual on joining mid-year (based on join date)

#### 4B — Opening Balances and Accruals
- [ ] Opening balance import per employee per leave type
- [ ] Accrual schedule: monthly / quarterly / annual / on-joining
- [ ] Monthly accrual job (cron): credit N days per month, round to 0.5 days
- [ ] Year-end carry-forward processing job: carry eligible balance, lapse excess, log each action
- [ ] Balance ledger: every credit, debit, adjustment with timestamp and reason

#### 4C — Leave Application
- [ ] Apply for leave: type, from date, to date, half-day option, reason, attachment
- [ ] Date range picker with weekend/holiday awareness (show effective working days)
- [ ] Overlap check against existing approved/pending leave (block duplicate dates)
- [ ] Balance check (block if requested days > available balance for paid leave)
- [ ] Blackout date restriction (e.g. financial year close, product launch — configurable by HR)
- [ ] Minimum notice enforcement (cannot apply retroactive CL if min notice = 2 days)
- [ ] Maximum consecutive days enforcement per leave type

#### 4D — Approval Workflow
- [ ] Multi-level approval: up to 3 levels (L1 = manager, L2 = HR, L3 = skip-level if configured)
- [ ] Auto-approve option for leave types with zero required approvers
- [ ] Approver can approve, reject (with mandatory reason), or request more info
- [ ] Auto-escalation: if L1 does not act within N hours, escalate to L2
- [ ] Delegation: if approver is on leave, delegate routes to their delegated approver
- [ ] Notification at each step: in-app + email to employee, approver, CC-list

#### 4E — Cancellation and Revocation
- [ ] Employee can cancel pending leave (immediate)
- [ ] Employee can request cancellation of approved leave (requires approver action)
- [ ] HR can cancel any leave with mandatory reason
- [ ] Balance is restored on cancellation of approved leave
- [ ] Cancellation logged in leave ledger

#### 4F — Leave Calendar
- [ ] Team leave calendar view: who is absent on which day
- [ ] Company holiday calendar integrated (show holidays in a different colour)
- [ ] Filter by department / branch / team
- [ ] iCal export for approved leaves

#### 4G — Compensatory Off
- [ ] Employee claims CO for working on holiday/weekend (with date and reason)
- [ ] Manager approves CO claim
- [ ] CO balance credited on approval
- [ ] CO balance has expiry date (e.g. must be used within 30 days of accrual)
- [ ] CO application same as regular leave application with CO type pre-selected

#### 4H — Reports
- [ ] Leave balance report by employee, type, department
- [ ] Leave utilization report (% taken vs entitled)
- [ ] Absenteeism trend (month-on-month)
- [ ] Pending approval aging report
- [ ] Carry-forward and lapse summary (year-end)

**Acceptance:**
- Employee can apply, manager can approve/reject, balance updates correctly
- Overlap check blocks duplicate date applications
- Year-end carry-forward runs and logs every balance change
- Leave calendar shows team view across all leave types

---

### Step 5: Attendance Core ⬜ PENDING

**Goal:** Make daily attendance operational with India workforce defaults.

**Industry reference:** Keka Attendance, Darwinbox Attendance, GreytHR Attendance, BambooHR Time Tracking.

#### 5A — Shift Configuration
- [ ] Fixed shift: start time, end time, grace period (in), grace period (out), minimum hours for full day
- [ ] Flexible shift: core hours band, total hours required per day
- [ ] Half-day threshold (hours below which day is marked half-day)
- [ ] Night shift: cross-midnight support, overtime calculation from shift end
- [ ] Shift effective date (shift can change over time for an employee)

#### 5B — Shift Roster Assignment
- [ ] Assign shift to employee (permanent assignment)
- [ ] Week-level roster: assign specific shifts to each day for each employee
- [ ] Rotational shift groups (e.g. A/B/C shift cycling weekly)
- [ ] Roster copy: copy previous week's roster to next week
- [ ] Bulk shift assignment by department/branch

#### 5C — Weekly Off Configuration
- [ ] Configure weekly off days per shift (e.g. Sat + Sun, or only Sun)
- [ ] Alternate Saturday off rule (1st and 3rd Sat off)
- [ ] Branch-level weekly off override (e.g. retail stores work all Saturdays)

#### 5D — Holiday Calendar
- [ ] National holidays (hardcoded India defaults + HR editable)
- [ ] Optional/restricted holidays: employee can choose N from a list per year
- [ ] Branch-level holiday calendars (Mumbai vs Chennai have different holidays)
- [ ] Holiday on weekly off: treated as holiday for OT calculation

#### 5E — Check-in / Check-out
- [ ] Manual punch via web (with IP/location capture for audit)
- [ ] Mobile geo-punch: GPS coordinates logged, geofence radius configurable per location
- [ ] Selfie attendance: photo captured on punch, AI liveness check hook
- [ ] QR code punch: location-specific QR, scanned via mobile
- [ ] Biometric integration: import from biometric device (flat-file import: device ID, employee ID, timestamp, punch type)
- [ ] Multiple punches per day: first in = check-in, last out = check-out, middle punches saved for audit
- [ ] Auto check-out: if employee forgets to punch out, auto-checkout at shift-end + grace

#### 5F — Daily Attendance Computation
- [ ] Status flags: Present (P), Absent (A), Half Day (H), On Leave (L), Holiday (HO), Weekly Off (WO), On Duty (OD)
- [ ] Late entry flag: check-in after shift start + grace period
- [ ] Early exit flag: check-out before shift end - grace period
- [ ] Overtime hours: hours worked beyond shift end + threshold
- [ ] Short hours flag: worked hours < minimum for full day but > half-day threshold
- [ ] Daily computation job (runs at midnight or on-demand)

#### 5G — Regularization
- [ ] Employee submits regularization: date, reason, claimed in-time, claimed out-time, supporting note
- [ ] Manager reviews and approves/rejects
- [ ] On approval, attendance record is updated and recomputed
- [ ] Regularization allowed within N days of the attendance date (configurable)
- [ ] Regularization history visible to HR and employee

#### 5H — On-Duty / Field Visit
- [ ] On-duty request: employee marks a day as OD (client visit, travel)
- [ ] Manager approves OD
- [ ] OD days count as Present for payroll purposes
- [ ] OD linked to travel request if Travel module is enabled

#### 5I — Monthly Attendance Report
- [ ] Attendance muster: employee × day grid showing status for the month
- [ ] Summary columns: working days, present, absent, leaves, holidays, OT hours, late entries
- [ ] Filter by branch, department, month
- [ ] Export to Excel (for payroll input)
- [ ] Lock attendance for a month (HR locks; no further changes without unlock)

#### 5J — Payroll Integration
- [ ] Monthly attendance summary feeds payroll LOP (Loss of Pay) calculation
- [ ] Late/early deduction rules configurable per policy
- [ ] OT payout rate linkable to salary component

**Acceptance:**
- Employee can punch in/out
- Late/early flags compute correctly against shift
- Regularization can be submitted and approved
- Monthly muster exports with correct counts
- Attendance data feeds payroll LOP input

---

### Step 6: Documents and Policies ⬜ PENDING

**Goal:** Centralize employee and HR documents with lifecycle tracking.

**Industry reference:** Darwinbox Documents, BambooHR Documents, Keka Documents, SpringRecruit Offer Engine.

#### 6A — Document Templates
- [ ] Template engine with merge fields: {{employee.name}}, {{company.name}}, {{join_date}}, {{designation}}, {{salary}} etc.
- [ ] Template categories: Offer Letter, Appointment Letter, Confirmation Letter, Increment Letter, Experience Letter, Relieving Letter, Warning Letter, Termination Letter, Probation Extension
- [ ] Rich-text editor for template body (preserve formatting on generation)
- [ ] Version history for templates (date, changed by, change summary)
- [ ] Preview mode: render template with sample data before publishing

#### 6B — Document Generation
- [ ] Generate document for an employee: select template → auto-fill merge fields → preview → finalize
- [ ] PDF generation with company letterhead (logo, address, signature block)
- [ ] Batch generation: generate letters for a filtered employee list
- [ ] Generated document stored in employee document repository with date and generated-by log

#### 6C — Employee Document Repository
- [ ] Upload documents against an employee: category, name, file (PDF/image), issue date, expiry date
- [ ] Document categories: ID Proof, Address Proof, Educational Certificates, Experience Certificates, Statutory (PAN card, Aadhaar, UAN card), Offer/Appointment Letter, Bank Proof, Medical, Other
- [ ] Expiry tracking: documents with expiry date show alerts 30/60/90 days before expiry
- [ ] Expiry dashboard: list all expiring/expired documents across employees with filter
- [ ] Access control: employee sees own documents; HR sees all; manager sees team documents

#### 6D — Policy Library
- [ ] Policy record: title, category, version number, effective date, content (rich text), attachment (PDF)
- [ ] Policy categories: HR Policy, Leave Policy, Code of Conduct, IT Policy, Travel Policy, Anti-Harassment, Grievance
- [ ] Policy version history: superseded versions archived, current version flagged
- [ ] Policy search by keyword and category

#### 6E — Policy Acknowledgement
- [ ] HR publishes a policy and assigns it to employees (by department / designation / all)
- [ ] Employee receives notification to acknowledge
- [ ] Employee reads policy inline and clicks Acknowledge (with timestamp)
- [ ] Digital acknowledgement record: employee ID, policy ID, version, timestamp, IP
- [ ] HR tracks pending acknowledgements with reminder trigger
- [ ] Acknowledgement report: % completion by department, list of non-acknowledgers

#### 6F — E-sign Integration Stub
- [ ] Document can be flagged as "requires e-sign"
- [ ] Integration hook interface for DigiSign/DocuSign/Aadhaar eSign
- [ ] Signed document stored with signature audit trail placeholder
- [ ] Manual workaround: upload signed scanned copy if e-sign provider not configured

**Acceptance:**
- HR can generate any standard letter for any employee
- Employee can view own documents in repository
- Expiry dashboard shows all documents expiring in next 90 days
- Policy acknowledgement tracks completion rate by department

---

## Phase 2: Payroll and Operational Depth

### Step 7: Payroll MVP ⬜ PENDING

**Goal:** Run a complete, statutory-compliant monthly payroll for Indian workforce.

**Industry reference:** GreytHR Payroll, Keka Payroll, Darwinbox Payroll, Spine Payroll, SAP Payroll India.

#### 7A — Salary Component Master
- [ ] Component types: Earning, Deduction, Statutory Contribution (employer), Statutory Deduction (employee)
- [ ] Standard earnings: Basic, HRA, Conveyance Allowance, Medical Allowance, Special Allowance, LTA, Bonus, Variable Pay, Flexi Benefit
- [ ] Standard deductions: PF Employee, ESI Employee, PT, TDS, Loan EMI, Advance Recovery, LWP Deduction
- [ ] Standard employer contributions: PF Employer, ESI Employer, Gratuity Provision, Bonus Provision
- [ ] Calculation type: fixed amount, % of Basic, % of CTC, formula-based
- [ ] Formula engine: define salary component as formula referencing other components (e.g. HRA = Basic × 0.4)
- [ ] Taxable / non-taxable flag per component (for TDS computation)
- [ ] Show-on-payslip flag; sequence / sort order on payslip

#### 7B — Salary Structures
- [ ] Structure template: group of components with their calculation rules
- [ ] Multiple structures for different grades/bands (e.g. Junior Band, Senior Band, Management Band)
- [ ] CTC-to-gross-to-net explainer view (how total CTC splits into take-home)
- [ ] Annual and monthly CTC breakdown

#### 7C — Employee Salary Assignment
- [ ] Assign structure + component amounts to employee with effective date
- [ ] Salary revision: new row with new effective date (old row retained for history)
- [ ] Increment letter auto-generated on revision (links to Step 6)
- [ ] Salary assignment approval: Finance head approves new/revised salary

#### 7D — Investment Declarations (IT Declaration)
- [ ] Declaration window open/close dates configurable by HR
- [ ] Employee submits investments: 80C (PPF, LIC, ELSS, tuition fee), 80D (health insurance), HRA exemption, home loan interest, NPS (80CCD)
- [ ] Proposed investment → actual proof submission window (Jan-Mar)
- [ ] Proof submission: upload documents against each declaration item
- [ ] HR/Finance verifies proof, marks verified/rejected with comment
- [ ] TDS computation uses verified amounts; unverified defaults to zero

#### 7E — Payroll Run
- [ ] HR creates payroll run for a month and company/branch
- [ ] System checks: all employees have salary assigned, attendance locked for month, IT declarations processed
- [ ] Attendance-based LOP calculation: LOP days × (monthly salary / working days in month)
- [ ] Statutory calculations:
  - PF: Employee 12% of Basic (max ₹15,000 basic cap for EPS), Employer 12% (EPS 8.33% + EPF 3.67%), EDLI 0.5%
  - ESI: Employee 0.75% of gross (if gross ≤ ₹21,000/month), Employer 3.25%
  - PT: state-wise slab table (Maharashtra, Karnataka, AP, etc.)
  - TDS: income tax slab computation on projected annual income, monthly TDS = annual TDS / 12
  - Gratuity provision: (Basic/26) × 15 per year of service (monthly accrual for provision)
  - LWF: state-wise flat contribution (employer + employee)
- [ ] Reimbursements processing: pending approved reimbursements included in payroll
- [ ] Arrear calculation: if salary revision was backdated, system computes arrear and adds to current month
- [ ] Pre-payroll variance report: month-on-month comparison (flag employees where gross change > 10%)
- [ ] Payroll review and approval (Finance head)
- [ ] Payroll lock after approval (no changes without explicit unlock with reason)

#### 7F — Payslip
- [ ] Payslip PDF: company letterhead, month, employee details, earnings table, deductions table, employer contribution table, net pay, YTD summary
- [ ] Employee self-service payslip download (own months only)
- [ ] Payslip email dispatch (bulk send to all employees for a payroll run)
- [ ] Password-protected payslip PDF (password = last 4 digits of mobile or DOB)

#### 7G — Statutory Reports and Exports
- [ ] PF: ECR (Electronic Challan cum Return) format export
- [ ] ESI: ESI monthly contribution report
- [ ] PT: Professional Tax workings by state
- [ ] TDS: Form 24Q quarterly return data stub
- [ ] Form 16: annual salary certificate stub (generated after April 1)
- [ ] Pay register: all employees, all components, for a month (HR internal)
- [ ] Bank advice / salary payment file: bank-specific format (NEFT/RTGS batch file)

#### 7H — Loans and Advances
- [ ] Loan master: employee, loan type, amount sanctioned, EMI amount, tenure, start month
- [ ] Advance request and approval workflow
- [ ] EMI auto-deduction in payroll run
- [ ] Loan closure and foreclosure
- [ ] Loan ledger per employee

#### 7I — Full and Final Settlement (F&F)
- [ ] Triggered on employee exit initiation (links to Exit module)
- [ ] F&F components: last month salary (LOP-adjusted), leave encashment (earned leave balance × daily rate), gratuity (if eligible), PF payout reference, notice period adjustment (deduction or payout), bonus pro-rata
- [ ] F&F approval workflow
- [ ] F&F payslip / settlement letter generation

**Acceptance:**
- HR can run payroll for 100 employees with correct PF/ESI/PT/TDS computation
- Variance report flags employees with > 10% change in gross
- Payroll is locked after approval; edit requires unlock with reason
- ECR and bank advice files export correctly

---

### Step 8: Recruitment and Offers ⬜ PENDING

**Goal:** Manage the full hiring pipeline from requisition to offer acceptance.

**Industry reference:** Workday Recruiting, Darwinbox ATS, SmartRecruiters, Keka Recruit, Zoho Recruit.

#### 8A — Manpower Requisition (MRF)
- [ ] MRF form: department, designation, number of positions, type (new / backfill / replacement), location, target join date, JD attachment, justification
- [ ] MRF approval workflow: HOD → HR → Finance (budget check) → MD/CEO for senior roles
- [ ] MRF status: Draft → Submitted → Approved → Active → Filled → Cancelled
- [ ] Hiring plan: link MRF to annual headcount budget
- [ ] MRF dashboard: open positions, in-progress, filled this month

#### 8B — Job Postings
- [ ] Job posting: title, department, location, employment type, experience range, CTC range, JD, skills required, closing date
- [ ] Internal job board: visible to employees for internal mobility
- [ ] External career site page: public-facing listing (static or embedded widget)
- [ ] Job board integration hooks: Naukri, LinkedIn, Indeed (OAuth/API key config per board)
- [ ] Source tracking: tag each candidate with source (portal, employee referral, LinkedIn, direct, agency)
- [ ] Referral portal: employee submits referral with candidate details; tracks referral bonus eligibility

#### 8C — Candidate Management
- [ ] Candidate profile: name, email, phone, current company, current designation, current CTC, expected CTC, notice period, location, experience, resume file
- [ ] Resume parser (AI): extract name, email, phone, skills, experience, education from PDF/DOCX
- [ ] Duplicate candidate check by email/phone
- [ ] Candidate tagging (good fit, hold, blacklisted)
- [ ] Candidate database search: skills, experience range, location, notice period, source

#### 8D — Application Pipeline
- [ ] Pipeline stages: Applied → Screening → L1 Interview → L2 Interview → HR Interview → Offer → Joined / Rejected / Withdrawn
- [ ] Stage-wise kanban board view
- [ ] Move candidate across stages with reason
- [ ] Bulk stage move for multiple candidates
- [ ] Auto-reject: if not moved in N days, flag for review (configurable)

#### 8E — Interview Scheduling
- [ ] Schedule interview: candidate, job, interviewer(s), date-time, mode (in-person / video / phone), meeting link
- [ ] Calendar invite sent to candidate and interviewer(s) (via email)
- [ ] Panel interview: multiple interviewers per round, each submits independent scorecard
- [ ] Interview reminder: 24 hours before and 1 hour before
- [ ] Reschedule / cancel interview with notification

#### 8F — Feedback and Scorecards
- [ ] Scorecard template per stage: list of evaluation parameters (communication, technical skill, problem-solving, culture fit) with rating scale (1-5) and comments field
- [ ] Interviewer submits scorecard online; remains editable until HR closes the round
- [ ] Aggregate scorecard view for hiring manager (all interviewers' ratings side by side)
- [ ] Overall hiring decision: Recommended / Not Recommended / On Hold
- [ ] Feedback visible to next interviewer or hidden (configurable per org)

#### 8G — Offer Management
- [ ] Offer creation: CTC components, joining date, designation, department, location, offer validity date
- [ ] Offer approval workflow: HR → HOD → Finance for offers above threshold
- [ ] Offer letter auto-generated from template (links to Step 6)
- [ ] Offer sent to candidate via email (secure link to view and e-sign)
- [ ] Candidate can Accept / Reject / Negotiate (with counter-proposal)
- [ ] Offer revoke with reason

#### 8H — Background Verification
- [ ] BGV request: select verification type (address, education, employment, criminal, reference)
- [ ] BGV vendor integration hook (IDfy, AuthBridge, SpringVerify)
- [ ] BGV status tracking: Initiated → In Progress → Completed → Discrepancy Found
- [ ] Conditional joining: employee can join while BGV is in progress; completion required within N days

#### 8I — Candidate to Employee Conversion
- [ ] One-click convert accepted offer to employee record draft (pre-fills profile from candidate data)
- [ ] HR reviews and completes missing fields
- [ ] Onboarding task automatically triggered (links to Step 9)
- [ ] Recruitment cost tracked: agency fee, referral bonus, job board spend vs hires

**Acceptance:**
- Recruiter can create MRF, get approval, post job, source candidates, track through pipeline
- Scorecard aggregated for hiring decision
- Offer generated and sent; acceptance triggers onboarding
- Recruitment funnel report shows conversion at each stage

---

### Step 9: Onboarding ⬜ PENDING

**Goal:** Convert hired candidates into fully operational employees through checklist-driven onboarding.

**Industry reference:** Darwinbox Onboarding, BambooHR Onboarding, Keka Onboarding, WorkBright.

#### 9A — Onboarding Templates
- [ ] Template per role/department/location (e.g. Tech Onboarding, Sales Onboarding)
- [ ] Template tasks: name, owner (HR / IT / Finance / Manager / Employee), due offset (day -3, day 0, day 7, day 30), required/optional flag
- [ ] Document collection tasks linked to document categories
- [ ] Policy acknowledgement tasks linked to specific policies

#### 9B — Pre-boarding (Before Day 1)
- [ ] Welcome email to new hire on offer acceptance: login credentials to self-service portal, company handbook link, first-day instructions
- [ ] Pre-boarding checklist for employee: fill personal details, emergency contact, bank details, upload ID proofs
- [ ] Pre-boarding checklist for HR: send offer kit, arrange workstation, create IT accounts, assign buddy
- [ ] Joining kit dispatch tracking: laptop, ID card, access card, swag

#### 9C — Day-1 Onboarding Tasks
- [ ] Asset assignment: laptop, phone, peripherals, desk number (links to Assets module)
- [ ] IT access provisioning checklist: email account, VPN, HRIS portal, domain access
- [ ] Policy acknowledgement: Code of Conduct, IT Policy, Leave Policy (links to Step 6)
- [ ] Buddy / mentor assignment with introduction meeting scheduled
- [ ] Org chart orientation: show new employee their team structure

#### 9D — Document Collection
- [ ] Required documents list displayed to new employee
- [ ] Employee uploads documents via self-service portal
- [ ] HR verifies each document: Verified / Rejected with comment
- [ ] Completion tracker: % documents collected and verified

#### 9E — Post-Joining Follow-Up
- [ ] Day 30 check-in task: manager submits short survey on new hire settling in
- [ ] Day 60 check-in: HR reviews probation progress
- [ ] Day 90 check-in / probation review linked to Performance module
- [ ] New employee submits onboarding feedback survey (satisfaction, clarity, helpfulness)

#### 9F — Onboarding Dashboard
- [ ] List of employees currently in onboarding with completion %
- [ ] Overdue tasks flagged in red
- [ ] HR can manually mark tasks complete or reassign
- [ ] Onboarding completion report by cohort (month of joining)

**Acceptance:**
- HR starts onboarding; new employee receives welcome email and self-service access
- All tasks track completion; HR dashboard shows overdue items
- New employee record is ready for payroll and leave operations after completion

---

### Step 10: Helpdesk ⬜ PENDING

**Goal:** Enable structured HR service request management with SLA tracking.

**Industry reference:** ServiceNow HR Service Delivery, Freshservice, Zoho Desk adapted for HR.

#### 10A — Category and SLA Setup
- [ ] Category hierarchy: Parent Category (Leave Queries, Payroll Queries, Attendance, IT Access, Policy, Benefits, Other) → Sub-categories
- [ ] SLA per category: first response time, resolution time (in business hours)
- [ ] Category owner assignment: default assignee team/person per category
- [ ] Priority levels: Low, Medium, High, Critical (SLA multiplier per priority)
- [ ] Business hours config for SLA calculation (weekdays 9-6, exclude holidays)

#### 10B — Ticket Management
- [ ] Employee raises ticket: subject, category, description, priority, attachments
- [ ] Auto-assignment to category owner
- [ ] Ticket status: Open → In Progress → Pending Employee Action → Resolved → Closed
- [ ] SLA timer shown on ticket: time remaining to respond / resolve
- [ ] SLA breach alert: notifies agent and supervisor when SLA is at 80% and 100%
- [ ] Ticket ID auto-generated (e.g. HD-2024-0001)

#### 10C — Agent Actions
- [ ] Reply to employee (external comment, visible to employee)
- [ ] Internal note (not visible to employee, for team collaboration)
- [ ] Reassign to another agent or team
- [ ] Merge duplicate tickets
- [ ] Escalate to supervisor with escalation note
- [ ] Bulk close resolved tickets

#### 10D — Escalation Rules
- [ ] Auto-escalation on SLA breach: assign to supervisor, send alert
- [ ] Manual escalation by agent with reason
- [ ] Escalation tier 2: HOD or HR Head if supervisor SLA also breached
- [ ] Escalation history on ticket

#### 10E — Knowledge Base
- [ ] Article categories matching ticket categories
- [ ] Rich-text articles with attachments
- [ ] Article publish / draft / archive lifecycle
- [ ] Auto-suggest articles on ticket creation (keyword match against open ticket subject)
- [ ] Article rating by employees (helpful / not helpful)
- [ ] Search knowledge base from self-service portal

#### 10F — AI-Assisted Reply
- [ ] AI suggests reply based on ticket content and knowledge base articles
- [ ] Agent can use suggestion as-is, edit, or discard
- [ ] AI suggestion logged (used/edited/discarded) for quality tracking

#### 10G — Satisfaction Survey (CSAT)
- [ ] Auto-send survey on ticket close: single rating (1-5 stars) + optional comment
- [ ] Employee can rate within 7 days of closure
- [ ] CSAT report: per agent, per category, per month
- [ ] Low CSAT flag triggers manager review

#### 10H — Reports
- [ ] Ticket volume by category, agent, priority, month
- [ ] SLA compliance rate: % tickets resolved within SLA
- [ ] Average resolution time by category
- [ ] Agent workload: open tickets per agent

**Acceptance:**
- Employee can raise a ticket; it routes to correct agent automatically
- SLA timer is visible and breach triggers notification
- Knowledge base articles are suggested on ticket creation
- CSAT survey dispatches on closure; reports show agent performance

---

## Phase 3: Talent, Analytics, and AI

### Step 11: Performance Management ⬜ PENDING

**Goal:** Support goal setting, progress tracking, and complete review cycles.

**Industry reference:** Workday Performance, SAP SuccessFactors Performance & Goals, Darwinbox Performance, Leapsome.

#### 11A — Review Cycle Configuration
- [ ] Cycle setup: name, type (Annual / Mid-Year / Quarterly / Probation), start date, end date, employee scope (all / department / grade)
- [ ] Cycle phases: Goal Setting → Check-ins → Self Review → Manager Review → Calibration → Results Published
- [ ] Phase open/close dates with auto-lock on close date
- [ ] Reviewer mapping: direct manager, skip-level reviewer, HR business partner

#### 11B — Goal Management
- [ ] Goal setting: title, description, category (Business / Personal Development / OKR), KPIs, target value, measurement unit, due date, weight %
- [ ] SMART goal validation prompts: Specific, Measurable, Achievable, Relevant, Time-bound
- [ ] Goal cascade: company goals → department goals → individual goals (alignment tree)
- [ ] Goal approve/reject by manager before the goal is committed
- [ ] Goal modification: employee can propose change; manager approves
- [ ] Goal carry-forward to next cycle

#### 11C — Check-ins and Progress Updates
- [ ] Employee updates goal progress: current value, % complete, status (On Track / At Risk / Behind / Completed)
- [ ] Check-in comments visible to employee and manager
- [ ] Configurable check-in frequency reminder (weekly/bi-weekly/monthly)
- [ ] Manager can add coaching notes on check-ins
- [ ] One-on-one meeting notes linked to check-in records

#### 11D — Self Review
- [ ] Self review form: per-goal rating + comment, competency ratings, overall self-rating, achievements narrative, development areas, career aspirations
- [ ] Form auto-locks after phase close date
- [ ] Self review visible to manager during manager review phase

#### 11E — Manager Review
- [ ] Manager reviews self-assessment for each direct report
- [ ] Per-goal rating (override or confirm employee's self-rating) with mandatory comment for overrides
- [ ] Competency-based rating (Leadership, Collaboration, Innovation, Execution, Customer Focus)
- [ ] Overall performance rating: Exceptional / Exceeds Expectations / Meets Expectations / Needs Improvement / Unsatisfactory
- [ ] Manager can request additional reviewer input (lateral / skip-level)
- [ ] Manager review visible to employee after results published

#### 11F — 360-Degree Feedback
- [ ] Employee nominates peers and cross-functional colleagues (up to N nominations)
- [ ] HR can add mandatory reviewers (skip-level, HRBP)
- [ ] Feedback form: rating per competency + open-text feedback
- [ ] Anonymous option: reviewer identity hidden from employee (but visible to HR)
- [ ] 360 feedback aggregated separately from manager rating; shown in review summary

#### 11G — Calibration
- [ ] Calibration committee view: all employees in scope on a rating distribution grid
- [ ] Forced distribution bell curve guide (suggested % per rating band)
- [ ] Calibration notes per employee
- [ ] Final calibrated rating can override manager's submitted rating
- [ ] Calibration session locked and audited after HR closes

#### 11H — Nine-Box Grid
- [ ] Plot employees on 3×3 grid: Y-axis = Performance (Exceeds / Meets / Below), X-axis = Potential (High / Medium / Low)
- [ ] HR assigns potential rating separately from performance rating
- [ ] Nine-box export for succession and development planning

#### 11I — Performance Improvement Plan (PIP)
- [ ] PIP triggered from review: employee, start date, duration, specific improvement areas, milestones, manager support plan
- [ ] PIP progress tracked weekly (manager updates milestone status)
- [ ] PIP outcome: Improved → Normal → Extended or Terminated
- [ ] PIP fully audited and linked to employee record

#### 11J — Promotion and Increment Recommendations
- [ ] Manager submits promotion recommendation from review: new designation, new grade, justification
- [ ] HR and Finance approve promotion and linked salary revision
- [ ] Promotion triggers designation change in employee master (effective date)
- [ ] Increment percentage auto-populated in salary revision form after review

**Acceptance:**
- HR creates a review cycle; employees set goals; managers review
- 360 feedback collected; calibration adjusts ratings
- PIP can be created and tracked
- Results published to employees with full narrative

---

### Step 12: Reports and Analytics ⬜ PENDING

**Goal:** Provide decision-ready reporting for leadership, HR, and managers.

**Industry reference:** Workday Prism Analytics, SAP SuccessFactors People Analytics, Keka Analytics, Darwinbox Insights.

#### 12A — Standard Report Library

**People / Headcount**
- [ ] Headcount by department, branch, grade, employment type, gender (current and as of any date)
- [ ] Headcount movement: joiners vs leavers per month (net movement chart)
- [ ] Attrition report: voluntary vs involuntary, department-wise, tenure-band analysis
- [ ] Tenure distribution: < 1 yr, 1-3 yrs, 3-5 yrs, 5-10 yrs, > 10 yrs
- [ ] Diversity report: gender ratio by dept/grade, age distribution

**Attendance**
- [ ] Absenteeism rate: absent days / working days per department per month
- [ ] Late arrival trend: count and % by department
- [ ] Overtime hours by department / employee
- [ ] Shift adherence report

**Leave**
- [ ] Leave utilization: balance vs consumed per employee per type
- [ ] Leave encashment liability (earned leave × daily rate for all eligible employees)
- [ ] Absenteeism calendar heatmap

**Payroll**
- [ ] Payroll cost by department / grade / month
- [ ] CTC vs cost-to-company breakdown (salary + employer PF + ESI + gratuity)
- [ ] LOP (Loss of Pay) summary
- [ ] Statutory liability: monthly PF, ESI, PT, TDS
- [ ] Salary increment analysis: distribution of revision %

**Recruitment**
- [ ] Open positions vs filled
- [ ] Recruitment funnel: applications → screened → interviewed → offered → joined conversion %
- [ ] Time to hire (application date to joining date)
- [ ] Source effectiveness: hires per source channel
- [ ] Cost per hire: agency fees + referral bonus per hire

**Performance**
- [ ] Rating distribution by cycle / department / grade
- [ ] Goal completion rate
- [ ] PIP count and outcome

#### 12B — Custom Report Builder
- [ ] Field selector: user picks fields from a module (Employee, Leave, Attendance, Payroll)
- [ ] Filter builder: conditions with AND/OR logic (department = X, join date > Y)
- [ ] Grouping: group by department / branch / month
- [ ] Aggregations: count, sum, average, min, max
- [ ] Sort and limit
- [ ] Save report definition with name for reuse
- [ ] Schedule saved report: daily / weekly / monthly delivery to email list

#### 12C — Exports and Formats
- [ ] Every report exports to Excel (.xlsx) with formatted headers
- [ ] CSV export for data integration
- [ ] PDF export for management reports (with chart images embedded)
- [ ] Scheduled report email: attach PDF or Excel, send to configurable email list

#### 12D — Executive Dashboard
- [ ] KPI cards: total headcount, open positions, attrition rate (rolling 12m), payroll cost this month, leave utilization, avg rating last cycle
- [ ] Charts: headcount trend, attrition trend, payroll trend, recruitment funnel
- [ ] Department health matrix: headcount, attrition, avg rating, open roles per department
- [ ] Manager self-service: manager sees own-team reports (headcount, leave, attendance, performance)

**Acceptance:**
- All standard reports load from real transactional data
- Custom report builder can combine fields from at least two modules
- Scheduled report delivers on time via email with correct data
- Dashboard KPIs reconcile with module-level detail pages

---

### Step 13: AI Assistant Pack ⬜ PENDING

**Goal:** Add assistive AI features that are helpful but never block core HR workflows.

**Industry reference:** Darwinbox Darwin AI, SAP Joule, Keka AI, Workday AI.

#### 13A — HR Policy Q&A (RAG Chatbot)
- [ ] Policy documents indexed in vector store (update on policy publish/revision)
- [ ] Employee asks question in natural language; answer grounded in policy docs
- [ ] Source citation: show which policy article the answer is drawn from
- [ ] Escalate to helpdesk: if AI cannot answer confidently, offer to raise a ticket
- [ ] Conversation history per user (last 30 days)
- [ ] Admin can exclude specific policies from AI indexing

#### 13B — Resume Parser and Candidate Scoring
- [ ] Extract structured data: name, email, phone, skills, education, work history from PDF/DOCX
- [ ] Skill match score: compare candidate skills vs job requirements (JD keywords)
- [ ] Experience fit: years of experience vs job requirement range
- [ ] Parser failure graceful fallback: manual entry form pre-filled with whatever was extracted
- [ ] Parsing audit: original file retained alongside parsed output

#### 13C — Payroll Anomaly Detector
- [ ] Compare current month vs prior month for each employee
- [ ] Anomaly flags: gross change > 20%, new deduction > ₹5,000, PF mismatch, negative net pay
- [ ] Anomaly report presented to payroll approver before approval
- [ ] False-positive suppression: salary revision in current month suppresses gross-change flag
- [ ] Anomaly history retained per payroll run

#### 13D — Attrition Risk Prediction
- [ ] Feature inputs: tenure, recent rating, salary vs market (if configured), manager change count, leave taken, overtime hours, engagement survey score (if available)
- [ ] Risk score: Low / Medium / High per employee
- [ ] Risk factors explanation: which factors most contributed to risk
- [ ] HR dashboard: list of High-risk employees with recommended action prompts
- [ ] Model retrain stub: monthly batch job with updated data
- [ ] Employee privacy: attrition score visible only to HR, not to employee or manager

#### 13E — Helpdesk Auto-Categorization and Reply Suggestions
- [ ] On ticket creation, AI predicts category and sub-category (HR can override)
- [ ] AI generates a draft reply based on ticket content + knowledge base match
- [ ] Agent accepts / edits / discards AI reply (tracked for model feedback)
- [ ] Escalation suggestion: if ticket sentiment is very negative, AI flags for priority

#### 13F — Goal and Review Assistant
- [ ] When employee drafts a goal, AI suggests SMART improvement (rephrase, add metric, add deadline)
- [ ] When manager writes performance review narrative, AI offers grammar/tone check and expansion
- [ ] AI-generated review summary: pull together goal ratings, 360 comments, check-in notes into a structured paragraph (manager edits before saving)

#### 13G — AI Governance
- [ ] Every AI interaction logged: user, prompt, response, module, timestamp
- [ ] AI output cannot be saved without human review / edit / confirmation (no silent auto-actions)
- [ ] HR admin can view AI usage log and export
- [ ] AI confidence score shown where applicable
- [ ] Fallback: all AI features disable gracefully if AI service is unavailable

**Acceptance:**
- Policy Q&A answers with source citation
- Resume parsed and candidate scored in < 10 seconds
- Payroll anomaly report available before approver sees run
- Attrition risk visible on HR dashboard
- Core HR workflows function identically when AI service is offline

---

## Phase 4: Enterprise Readiness

### Step 14: Workflow Engine and Notifications ⬜ PENDING

**Goal:** Replace hardcoded approvals with a configurable workflow engine shared across modules.

**Industry reference:** Workday Business Process Framework, ServiceNow Flow Designer, Darwinbox Workflow Studio.

#### 14A — Workflow Definitions
- [ ] Workflow entity: name, trigger (module + event), steps
- [ ] Step types: Approval (human), Notification (auto), Condition (if/else branch), System Action (auto-update field)
- [ ] Sequential steps: step N starts only when step N-1 is approved
- [ ] Parallel approval: all approvers in a group must approve (consensus) or any one (consensus OR)
- [ ] Condition branches: if salary > ₹10L then require Finance approval, else skip
- [ ] Timeout handling: if approver does not act in N hours → escalate / auto-approve / auto-reject (configurable per step)

#### 14B — Approver Assignment
- [ ] Static approver: named user
- [ ] Role-based: e.g. any user with role "Finance Head"
- [ ] Dynamic: reporting manager, skip-level manager, HR business partner mapped to employee
- [ ] Delegation: if primary approver is on leave, workflow routes to delegated approver (links to Step 3D)
- [ ] Self-approval prevention: system blocks if employee is their own approver

#### 14C — Workflow Instances
- [ ] Every approval request creates a workflow instance: reference (leave request ID, payroll run ID etc.), current step, history of all steps with decision and timestamp
- [ ] Pending instance visible to approver on their task inbox
- [ ] Requester sees real-time status of their submitted request
- [ ] Audit trail: full decision history for every workflow instance, non-deletable

#### 14D — Notification Engine
- [ ] Notification templates: subject, body with merge fields, channel (in-app / email / SMS / WhatsApp)
- [ ] Trigger events: workflow step assigned, approved, rejected, escalated, completed, reminder
- [ ] Notification preferences per user: opt-out of email if in-app is enough (configurable by module)
- [ ] Bulk notification: HR can send announcement to all or filtered employees
- [ ] Email delivery log: sent / delivered / failed per notification

#### 14E — In-App Notification Inbox
- [ ] Notification list: icon count badge, expandable inbox
- [ ] Mark as read / mark all as read
- [ ] Deep link: notification links directly to the related record (click leave notification → opens leave request)
- [ ] Notification retention: last 90 days shown; older archived

#### 14F — Reminder Cadence
- [ ] Configure reminder intervals per workflow step (e.g. remind approver after 4 hours, again after 8 hours, escalate at 24 hours)
- [ ] Recurring reminders for pending self-review, policy acknowledgement, document expiry

**Acceptance:**
- Leave, payroll, and onboarding share workflow engine (no hardcoded approval logic)
- Users see pending task inbox with correct counts
- Escalation fires at configured timeout
- Notification templates can be edited by HR admin without code change

---

### Step 15: Advanced Organization Model ⬜ PENDING

**Goal:** Support larger and more complex companies with richer org structures.

**Industry reference:** Workday Organization Management, SAP SuccessFactors Employee Central, Darwinbox Org Setup.

#### 15A — Business Units
- [ ] Business unit as separate grouping (e.g. B2B Division, Consumer Division, Platform)
- [ ] Business units independent from department tree
- [ ] Employee can belong to a department and a business unit (cost-sharing possible)

#### 15B — Cost Centers
- [ ] Cost center master: code, name, GL code, parent cost center (hierarchy), owner
- [ ] Employee cost center assignment (primary + secondary split %)
- [ ] Cost center used in payroll reports for salary cost allocation
- [ ] Cost center budget tracking (annual headcount and salary budget vs actual)

#### 15C — Grades, Bands, and Pay Ranges
- [ ] Grade master: code, name, description (e.g. Grade L1, L2, L3 or Band A, B, C)
- [ ] Pay band per grade: min CTC, mid CTC, max CTC
- [ ] Compa-ratio: employee CTC vs midpoint of their grade band
- [ ] Employees outside band flagged for compensation review
- [ ] Grade assigned to designation (designation inherits grade range)

#### 15D — Job Families and Job Profiles
- [ ] Job family: group of related roles (e.g. Engineering, Sales, Operations)
- [ ] Job profile per designation: summary, responsibilities, required competencies, required experience, required education
- [ ] Job profiles used in recruitment (auto-fill JD from profile) and performance (competency ratings from profile)

#### 15E — Position Management
- [ ] Position (slot) concept: a headcount slot independent of who fills it
- [ ] Position attributes: title, department, grade, cost center, headcount budget
- [ ] Position statuses: Filled, Vacant, On Hold, Closed
- [ ] MRF linked to vacant position (recruitment fills position)
- [ ] Org chart shows positions (including vacancies) not just filled employees

#### 15F — Reporting Line Matrix
- [ ] Solid-line manager: primary reporting manager
- [ ] Dotted-line manager: functional or project reporting (non-primary)
- [ ] Matrix org chart showing both relationships
- [ ] Approval workflows can route to either solid-line or dotted-line based on config

#### 15G — Org Chart Visualization
- [ ] Interactive org chart: expand/collapse nodes, zoom, search
- [ ] Node shows: name, designation, department, photo, direct report count
- [ ] Export org chart as PNG or PDF
- [ ] Org chart as of any historical date (point-in-time view)
- [ ] Vacant positions shown as dashed boxes

**Acceptance:**
- Employee assignment references business unit + cost center + grade + position
- Payroll cost report groups by cost center with correct GL codes
- Org chart renders interactively for 500+ employee company
- Vacancy slots visible on org chart for recruitment planning

---

### Step 16: Security, Audit, and Compliance ⬜ PENDING

**Goal:** Make the product safe for sensitive HR and payroll data with full audit coverage.

**Industry reference:** Workday Security, SAP SF Security, GreytHR Compliance, DPDP Act (India), SOC 2 Type II controls.

#### 16A — Field-Level Audit
- [ ] Audit every change to sensitive fields: salary, bank account, PAN, Aadhaar, designation, manager, employment status
- [ ] Audit record captures: entity type, entity ID, field name, old value, new value, changed by, change timestamp, IP address, reason (if required)
- [ ] Field audit visible to HR and Auditor role in employee record timeline
- [ ] Sensitive fields (bank account, Aadhaar): old and new values masked in audit display (show last 4 digits)

#### 16B — PII Masking
- [ ] Aadhaar number: show XXXX-XXXX-1234 format to all users except designated HR
- [ ] PAN number: show ABCXX1234X format for most roles
- [ ] Bank account number: show XXXXXXXX1234
- [ ] Mobile number: show XXXXX67890 for manager role and below
- [ ] Access the unmasked value requires dedicated permission + audit log entry of who viewed it

#### 16C — Data Retention and Privacy (DPDP Act)
- [ ] Data retention policy config: how long to keep ex-employee data (default 7 years for statutory)
- [ ] Right to erasure request: HR can flag ex-employee record for anonymization (replace PII with placeholder, retain aggregated data for statutory reporting)
- [ ] Consent capture: employee consent for data processing logged at onboarding
- [ ] Data export for employee: employee can request download of their own data (HR generates export within 30 days)
- [ ] Legal hold: prevent deletion of records linked to an active legal case

#### 16D — Payroll Lock and Maker-Checker
- [ ] Payroll lock: after approval, payroll run cannot be edited; any edit requires "unlock payroll" action (logged with reason, requires Finance Head approval)
- [ ] Salary revision maker-checker: HR initiates → Finance Head approves before it takes effect
- [ ] Bank account change: requires two-step verification (employee initiates → HR verifies → Finance approves for accounts linked to payroll)
- [ ] Maker-checker log: all maker-checker events with maker, checker, decision, timestamp

#### 16E — Session and Access Controls
- [ ] Password policy: min length, complexity, expiry (90 days), no reuse of last 5 passwords
- [ ] IP whitelist per org: office IPs allowed; login from outside triggers OTP challenge
- [ ] Force logout: admin can terminate any active session
- [ ] Inactive session auto-logout (configurable timeout per role)
- [ ] Privileged action re-authentication: for payroll approval, bank change, role assignment — require password re-entry

#### 16F — Compliance Reports
- [ ] PF register (Form 3A, 6A stubs)
- [ ] ESI register
- [ ] PT register by state
- [ ] Muster roll (Factories Act compliant format)
- [ ] Leave register (Shops and Establishments Act format)
- [ ] Gratuity provision report (5-year service tracker)

**Acceptance:**
- Every salary change shows old/new value in field audit log
- PII fields are masked by default; viewing full value is logged
- Payroll lock prevents any edit post-approval
- Bank account change requires three-party approval chain

---

## Phase 5: Domain Packs

### Step 17: Manufacturing Pack ⬜ PENDING

**Industry reference:** SAP HCM Manufacturing, Ramco HCM, Spine HCM.

- [ ] Advanced shift rosters: 24×7 three-shift coverage matrix
- [ ] Shift handover notes: outgoing shift writes handover log for incoming supervisor
- [ ] Overtime types: OT1 (beyond shift), OT2 (rest day), OT3 (national holiday) — separate pay rates
- [ ] Comp-off for overtime: OT worked → comp-off balance credited
- [ ] Safety incident reporting: near miss, minor injury, LTI (Lost Time Injury) — linked to employee
- [ ] PPE (Personal Protective Equipment) issuance log: item, quantity, issue date, next replacement date
- [ ] Medical fitness certificate tracking: periodic medical exam, result, next exam due date
- [ ] Contract labour management: third-party agency, contract worker headcount, compliance docs
- [ ] Canteen / transport allowance tracking

### Step 18: Retail and Field Pack ⬜ PENDING

**Industry reference:** Reflexis WFM, Darwinbox Retail.

- [ ] Store hierarchy: Region → Zone → Store → Counter
- [ ] Store staffing plan: minimum staff required per shift per store
- [ ] Geo-attendance with configurable geofence per store location
- [ ] Field visit log: salesperson marks client visits with location + notes
- [ ] Offline attendance sync: mobile punch saved locally and syncs when online
- [ ] Inter-store transfer workflow
- [ ] Incentive/commission tracking linked to sales targets

### Step 19: BFSI Pack ⬜ PENDING

**Industry reference:** Workday BFSI, Oracle HCM for Banking.

- [ ] Regulatory certification tracking: AMFI, IRDAI, NISM — license number, issue date, expiry, mandatory renewal alert
- [ ] Policy attestation: employee reads and attests to SEBI/RBI circulars applicable to their role
- [ ] Segregation of duties (SoD) check: flag roles that grant conflicting access (e.g. initiate payment + approve payment)
- [ ] Maker-checker expansion: all master data changes require dual approval
- [ ] Evidence retention: digitally signed attestations stored with tamper-evident audit trail
- [ ] Variable pay / incentive compliance: ensure incentive calculations comply with regulatory caps

### Step 20: Healthcare and Education Packs ⬜ PENDING

**Healthcare — Industry reference:** API Healthcare, Kronos Healthcare WFM.

- [ ] Professional credential tracking: medical council registration, specialization, renewal date
- [ ] License expiry alert: 60/30/7 day notifications + auto-block from scheduling if lapsed
- [ ] Vaccination record: type, date, next due (for staff health policy compliance)
- [ ] On-call roster: doctor / nurse on-call scheduling with overtime rules
- [ ] Department privilege matrix: procedures each clinician is credentialed for

**Education — Industry reference:** PeopleAdmin, Banner HR.**

- [ ] Faculty workload assignment: courses, credits, lab hours, research hours per semester
- [ ] Course allocation and timetable integration hook
- [ ] Publications tracking: journal, conference papers linked to faculty profile
- [ ] Grant management: grant title, funding agency, amount, period, PI/Co-PI assignment
- [ ] Academic calendar: semester-aligned holiday and leave calendar overlay

---

## Immediate Next Sprint

1. Begin Step 2 (Employee Master): implement employee ID sequencing, statutory IDs, bank fields, org tree, and bulk import.
2. Add Step 2 API tests: statutory field validation, org tree traversal, bulk import error reporting.
3. Build Employee 360 detail view in frontend.
4. Write `test_employees.py` coverage for all new endpoints.
5. Move to Step 3 RBAC hardening once Employee Master is stable.

---

## Step Template

Use this checklist for each feature step:

- [ ] Confirm existing models, schemas, APIs, UI, and tests.
- [ ] Define acceptance criteria before editing.
- [ ] Patch backend validation and route behavior.
- [ ] Patch frontend workflow.
- [ ] Add or update tests.
- [ ] Run backend and frontend verification.
- [ ] Update this roadmap status.
