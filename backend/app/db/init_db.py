from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.user import User, Role, Permission
from app.models.target import FeatureCatalog, FeaturePlan, IndustryTarget


SYSTEM_PERMISSIONS = [
    # Company
    ("company_view", "View company settings", "company"),
    ("company_manage", "Manage company settings", "company"),
    # Employees
    ("employee_view", "View employees", "employee"),
    ("employee_create", "Create employees", "employee"),
    ("employee_update", "Update employees", "employee"),
    ("employee_delete", "Delete employees", "employee"),
    # Attendance
    ("attendance_view", "View attendance", "attendance"),
    ("attendance_manage", "Manage attendance", "attendance"),
    # Leave
    ("leave_view", "View leave requests", "leave"),
    ("leave_apply", "Apply for leave", "leave"),
    ("leave_approve", "Approve leave requests", "leave"),
    ("leave_manage", "Manage leave types and balances", "leave"),
    # Payroll
    ("payroll_view", "View payroll", "payroll"),
    ("payroll_run", "Run payroll", "payroll"),
    ("payroll_approve", "Approve payroll", "payroll"),
    # Recruitment
    ("recruitment_view", "View recruitment", "recruitment"),
    ("recruitment_manage", "Manage recruitment", "recruitment"),
    # Performance
    ("performance_view", "View performance reviews", "performance"),
    ("performance_manage", "Manage performance reviews", "performance"),
    # Helpdesk
    ("helpdesk_view", "View helpdesk tickets", "helpdesk"),
    ("helpdesk_manage", "Manage helpdesk tickets", "helpdesk"),
    # Reports
    ("reports_view", "View reports", "reports"),
    # Targets
    ("targets_view", "View target markets and feature plans", "targets"),
    ("targets_manage", "Manage target markets and feature plans", "targets"),
    # Assets
    ("asset_view", "View assets", "asset"),
    ("asset_manage", "Manage assets", "asset"),
    # Exit
    ("exit_view", "View exit records", "exit"),
    ("exit_manage", "Manage exit process", "exit"),
    # AI
    ("ai_assistant", "Use AI assistant", "ai"),
]

SYSTEM_ROLES = [
    {
        "name": "super_admin",
        "description": "Full system access",
        "permissions": [p[0] for p in SYSTEM_PERMISSIONS],
    },
    {
        "name": "hr_manager",
        "description": "HR Manager with full HR access",
        "permissions": [
            "company_view", "employee_view", "employee_create", "employee_update",
            "attendance_view", "attendance_manage", "leave_view", "leave_approve", "leave_manage",
            "payroll_view", "payroll_run", "recruitment_view", "recruitment_manage",
            "performance_view", "performance_manage", "helpdesk_view", "helpdesk_manage",
            "reports_view", "asset_view", "asset_manage", "exit_view", "exit_manage", "ai_assistant",
            "targets_view", "targets_manage",
        ],
    },
    {
        "name": "ceo",
        "description": "Executive leadership dashboard access",
        "permissions": [
            "company_view", "employee_view", "attendance_view", "leave_view",
            "payroll_view", "recruitment_view", "performance_view", "reports_view",
            "targets_view", "ai_assistant",
        ],
    },
    {
        "name": "manager",
        "description": "Department manager",
        "permissions": [
            "employee_view", "attendance_view", "leave_view", "leave_approve",
            "payroll_view", "performance_view", "performance_manage", "helpdesk_view",
            "reports_view", "ai_assistant",
            "targets_view",
        ],
    },
    {
        "name": "employee",
        "description": "Regular employee - self-service only",
        "permissions": [
            "attendance_view", "leave_view", "leave_apply", "payroll_view",
            "performance_view", "helpdesk_view", "ai_assistant",
            "targets_view",
        ],
    },
]


INDUSTRY_TARGETS = [
    {
        "name": "Technology & Services",
        "slug": "technology-services",
        "headline": "Powerful HCM for technology and white collar services companies.",
        "description": "Employee experience, skills, projects, performance, helpdesk, payroll, and analytics built for fast-moving services teams.",
        "icon": "cpu",
        "color": "blue",
        "sort_order": 10,
    },
    {
        "name": "Pharma & Manufacturing",
        "slug": "pharma-manufacturing",
        "headline": "HR and payroll for blue-collar and white-collar workforces.",
        "description": "Shift rosters, overtime, statutory compliance, attendance, safety notes, document control, and approvals for regulated operations.",
        "icon": "factory",
        "color": "green",
        "sort_order": 20,
    },
    {
        "name": "Banks & Financial Services",
        "slug": "banks-financial-services",
        "headline": "Complete HCM and payroll where compliance and audit are mandatory.",
        "description": "RBAC, audit logs, maker-checker approvals, document evidence, payroll locks, and robust reporting for financial institutions.",
        "icon": "landmark",
        "color": "violet",
        "sort_order": 30,
    },
    {
        "name": "Retail & Other Industries",
        "slug": "retail-other-industries",
        "headline": "One HR platform for distributed stores and field teams.",
        "description": "Mobile-first self-service, geo attendance, store staffing, leave, helpdesk, and instant updates from anywhere.",
        "icon": "store",
        "color": "amber",
        "sort_order": 40,
    },
]

FEATURE_PLANS = [
    {
        "code": "essential",
        "name": "Essential Automation",
        "tagline": "Core HRMS automation for every domain.",
        "strength": "A complete hire-to-retire operating base for HR, employees, managers, and finance.",
        "sort_order": 10,
        "features": {
            "Core HR": [
                "Company and legal entity setup", "Branch, location, department, cost center, and designation hierarchy",
                "Employee master record", "Dynamic employee profiles", "Employee lifecycle status tracking",
                "Probation and confirmation tracking", "Reporting manager mapping", "Organization chart",
                "Employee directory", "Custom employee fields", "Bulk employee import", "Employee ID sequencing",
                "Role based access control", "Permission templates", "Employee timeline", "Audit trail baseline",
            ],
            "Time and Attendance": [
                "Leave types and policies", "Leave balance accruals", "Leave application workflow",
                "Leave approval workflow", "Holiday calendar", "Attendance check-in and check-out",
                "Daily attendance register", "Shift setup", "Grace minutes", "Monthly attendance summary",
                "Attendance regularization", "Team attendance view", "Late coming and early leaving flags",
            ],
            "Payroll and Expense": [
                "Salary components", "Salary structures", "Employee salary assignment",
                "Monthly payroll run", "Payroll approval", "Payslip generation", "Basic deductions",
                "Statutory identifiers", "Reimbursement capture", "Payroll reports",
            ],
            "Recruitment": [
                "Job requisitions", "Job openings", "Candidate database", "Candidate stages",
                "Resume upload", "Interview scheduling", "Interview feedback", "Offer creation",
            ],
            "Onboarding": [
                "Onboarding templates", "New hire onboarding tasks", "Policy acknowledgements",
                "Joining document collection", "Welcome checklist",
            ],
            "Documents": [
                "Document templates", "Employee document repository", "Generated letters",
                "Policy library", "Document expiry tracking", "Document verification status",
            ],
            "Performance": [
                "Appraisal cycles", "Individual goals", "Goal progress tracking",
                "Performance reviews", "Reviewer assignment", "Rating capture",
            ],
            "Employee Self Service": [
                "Email login", "Employee profile self-service", "Leave self-service",
                "Attendance self-service", "Payslip self-service", "Document self-service",
                "Notification inbox",
            ],
            "Helpdesk": [
                "Helpdesk categories", "Employee tickets", "Ticket assignment",
                "Ticket status workflow", "Ticket replies", "AI suggested helpdesk reply",
            ],
            "Reports and Analytics": [
                "Headcount dashboard", "Department headcount report", "Attendance trend report",
                "Leave trend report", "Payroll summary report", "Recruitment funnel report",
            ],
        },
    },
    {
        "code": "strength",
        "name": "Strength",
        "tagline": "Advanced automation for distributed and regulated workforces.",
        "strength": "All Essential features plus deeper workforce management, compliance, employee service, and operational analytics.",
        "sort_order": 20,
        "features": {
            "Core HR": [
                "Multi-company tenant model", "Business unit hierarchy", "Grade and band management",
                "Position management", "Job profile library", "Delegation of authority",
                "Maker-checker employee changes", "Configurable approval chains", "Advanced audit logs",
                "Data retention rules", "Employee data completeness score", "HR operations calendar",
            ],
            "Workforce Management": [
                "Advanced shift roster", "Rotational shifts", "Split shifts", "Weekly offs",
                "Shift swaps", "Roster publishing", "Overtime calculation", "Comp-off rules",
                "Selfie attendance", "Geo-fenced attendance", "Continuous field location punching",
                "Biometric device integration", "Timesheets", "Project time capture",
            ],
            "Payroll and Compliance": [
                "Payroll lock and unlock", "Payroll variance checks", "AI payroll anomaly detection",
                "Loans and salary advances", "Perks and benefits", "Gratuity tracking",
                "Bonus and incentives", "Full and final settlement", "Accounting integration",
                "Country and state compliance profiles", "Tax declaration and proof collection",
            ],
            "Recruitment and Talent Acquisition": [
                "Hiring plans", "Job approval workflow", "Career site readiness", "Candidate source tracking",
                "Resume parsing", "Interview panel management", "Evaluation scorecards",
                "Offer approval workflow", "Offer letter templates", "Candidate conversion to employee",
            ],
            "Learning and Development": [
                "Course catalog", "Training calendar", "Learning assignments", "Training attendance",
                "Certification tracking", "Skill gap mapping", "Manager nominated learning",
            ],
            "Employee Service Delivery": [
                "HR case management", "SLA tracking", "Knowledge base", "Employee query management",
                "Internal comments", "Escalation rules", "Canned responses",
            ],
            "Assets and Travel": [
                "Asset categories", "Asset inventory", "Asset assignment", "Asset return workflow",
                "Asset condition tracking", "Travel requests", "Travel approvals", "Travel expense linkage",
            ],
            "Employee Experience": [
                "Announcements", "Polls", "Pulse surveys", "Public praise", "Recognition badges",
                "Employee social wall", "Company values tagging", "Birthday and work anniversary moments",
            ],
            "Security and Identity": [
                "Single sign-on", "Mobile OTP login", "MFA readiness", "IP restrictions",
                "Device/session tracking", "Privilege review", "Sensitive field masking",
            ],
            "Reports and Analytics": [
                "People analytics", "Attrition risk analysis", "Absence analytics",
                "Payroll variance dashboard", "Compliance dashboard", "Manager dashboards",
                "Custom report filters", "Scheduled reports",
            ],
        },
    },
    {
        "code": "growth",
        "name": "Growth",
        "tagline": "Talent, skills, culture, and business performance management.",
        "strength": "All Strength features plus strategic workforce planning, talent development, compensation, and skills intelligence.",
        "sort_order": 30,
        "features": {
            "Workflow Automation": [
                "No-code workflow builder", "Workflow triggers", "Conditional approvals",
                "Parallel approvals", "Escalation matrix", "Task automation", "Notification automation",
                "Form builder", "Custom objects", "Custom report builder",
            ],
            "Workforce Planning": [
                "Headcount planning", "Position budget", "Workforce scenarios", "Open role forecasting",
                "Attrition impact planning", "Internal mobility planning", "Succession bench strength",
            ],
            "Business Performance": [
                "Company goals and OKRs", "Department goals", "Individual goals",
                "Goal alignment map", "Goal check-ins", "Goal insights", "Core values",
                "Business review dashboards", "KPI ownership", "Performance calibration",
            ],
            "Employee Performance": [
                "Continuous feedback", "One-on-one meetings", "360 degree feedback",
                "Self-appraisals", "Manager appraisals", "Peer reviews", "Performance review templates",
                "Promotion recommendations", "Performance improvement plans", "Performance insights",
                "Nine-box talent grid", "Succession planning", "Career pathing",
            ],
            "Skills and Learning Intelligence": [
                "Skills library", "Competency framework", "Role skill requirements",
                "Employee skill matrix", "Skill endorsements", "Skill proficiency history",
                "Skill analytics", "Learning recommendations", "Internal opportunity marketplace",
            ],
            "Compensation Management": [
                "Compensation bands", "Salary review cycles", "Merit increase planning",
                "Bonus planning", "Equity grant tracking", "Compensation budgets",
                "Pay equity analysis", "Manager compensation worksheets",
            ],
            "Engagement and Culture": [
                "Engagement surveys", "Anonymous feedback", "eNPS", "Sentiment trends",
                "Recognition programs", "Awards marketplace", "Culture analytics",
            ],
            "AI and Copilot": [
                "HR assistant", "Policy Q&A", "Resume parser", "Attrition predictor",
                "Payroll anomaly detector", "Helpdesk reply generator", "Employee profile summaries",
                "Goal writing assistant", "Review summary assistant",
            ],
            "Integrations": [
                "Open API", "Webhook events", "Accounting connector", "Email connector",
                "Calendar connector", "ATS connector", "LMS connector", "Biometric connector",
                "Document e-sign connector", "Data import and export jobs",
            ],
        },
    },
    {
        "code": "global-enterprise",
        "name": "Global Enterprise",
        "tagline": "Mega-suite readiness for any industry and country.",
        "strength": "Enterprise governance, localization, domain-specific workforce rules, and platform extensibility.",
        "sort_order": 40,
        "features": {
            "Global Core HR": [
                "Multi-country worker records", "Multiple worker types", "Contingent workforce",
                "Global addresses and identifiers", "Localization packs", "Country-specific documents",
                "Legal entity transfers", "Global mobility", "Visa and immigration tracking",
            ],
            "Benefits and Wellbeing": [
                "Benefits plans", "Benefit eligibility rules", "Benefit enrollment",
                "Insurance dependents", "Wellness programs", "Health checks", "Employee assistance programs",
                "Wellbeing analytics",
            ],
            "Industrial Workforce": [
                "Factory line staffing", "Production shift handover", "Safety incidents",
                "PPE issuance", "Medical fitness", "Training compliance", "Contract labor attendance",
                "Union agreement rules",
            ],
            "Retail and Field Workforce": [
                "Store staffing", "Area manager hierarchy", "Field route plans", "Beat plans",
                "Geo attendance", "Offline attendance capture", "Mobile task lists", "Store transfer workflow",
            ],
            "BFSI and Regulated Workforce": [
                "Maker-checker approvals", "Segregation of duties", "Fit and proper checks",
                "Regulatory certification", "Policy attestations", "Payroll and document lock",
                "Investigation case files", "Evidence retention",
            ],
            "Healthcare Workforce": [
                "Clinical credentialing", "License expiry", "Duty roster", "On-call scheduling",
                "Department privileges", "Vaccination records", "Occupational health tracking",
            ],
            "Education Workforce": [
                "Academic departments", "Faculty workload", "Course allocation", "Research profile",
                "Publication records", "Grant participation", "Academic calendar alignment",
            ],
            "Platform Governance": [
                "Tenant configuration", "Feature flags", "Domain feature packs", "Data residency settings",
                "Consent management", "Privacy requests", "Legal hold", "Field-level audit",
                "Data quality rules", "Master data governance",
            ],
            "Advanced Analytics": [
                "Workforce data lake", "Metric definitions", "Dashboard builder", "Predictive workforce models",
                "Cost analytics", "Productivity analytics", "Diversity analytics", "Compliance analytics",
            ],
        },
    },
]


def init_db(db: Session) -> None:
    # Create permissions
    perm_map = {}
    for name, description, module in SYSTEM_PERMISSIONS:
        perm = db.query(Permission).filter(Permission.name == name).first()
        if not perm:
            perm = Permission(name=name, description=description, module=module)
            db.add(perm)
            db.flush()
        perm_map[name] = perm

    # Create roles
    role_map = {}
    for role_data in SYSTEM_ROLES:
        role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not role:
            role = Role(name=role_data["name"], description=role_data["description"], is_system=True)
            db.add(role)
            db.flush()
        role.permissions = [perm_map[p] for p in role_data["permissions"] if p in perm_map]
        role_map[role_data["name"]] = role

    db.commit()

    # Seed target markets and feature plans
    for item in INDUSTRY_TARGETS:
        target = db.query(IndustryTarget).filter(IndustryTarget.slug == item["slug"]).first()
        if not target:
            db.add(IndustryTarget(**item))

    for plan_data in FEATURE_PLANS:
        features = plan_data.pop("features")
        plan = db.query(FeaturePlan).filter(FeaturePlan.code == plan_data["code"]).first()
        if not plan:
            plan = FeaturePlan(**plan_data)
            db.add(plan)
            db.flush()
        else:
            for key, value in plan_data.items():
                setattr(plan, key, value)
        order = 0
        for module, names in features.items():
            for name in names:
                exists = (
                    db.query(FeatureCatalog)
                    .filter(FeatureCatalog.plan_id == plan.id, FeatureCatalog.module == module, FeatureCatalog.name == name)
                    .first()
                )
                if not exists:
                    db.add(
                        FeatureCatalog(
                            plan_id=plan.id,
                            module=module,
                            name=name,
                            sort_order=order,
                            is_highlight=name in {"Payroll Automation", "People Analytics", "Performance Reviews", "Geo Fencing"},
                        )
                    )
                order += 1
        plan_data["features"] = features

    db.commit()

    # Create superuser
    superuser = db.query(User).filter(User.email == "admin@aihrms.com").first()
    if not superuser:
        superuser = User(
            email="admin@aihrms.com",
            hashed_password=get_password_hash("Admin@123456"),
            is_active=True,
            is_superuser=True,
            role_id=role_map["super_admin"].id,
        )
        db.add(superuser)
        db.commit()
