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
        "tagline": "Core HRMS automation for growing companies.",
        "strength": "Scaling with advanced automation and employee engagement.",
        "sort_order": 10,
        "features": {
            "Core HR": [
                "Org Structure Management", "Documents & Letters", "Employee Onboarding - Basic",
                "Dynamic Employee Profiles", "Standard Access Roles", "Employee Exit",
                "Notification Engine - Basic", "Reports - Basic",
            ],
            "Time & Attendance": [
                "Leave Management", "Gamified Attendance Tracking", "Overtime Automation", "Shift Management - Basic",
            ],
            "Payroll and Expense": [
                "Payroll Automation", "Statutory Compliance", "Accounting Integration",
                "Loans & Salary Advances", "Perks & Benefits", "Expense Management",
                "Employee Tax Management", "Gratuity Management",
            ],
            "Employee Self Service": ["Signup using Email", "Mobile App", "Inbox (Notification Centre)"],
            "Employee Experience": ["Social Wall", "Polls and Announcements", "Public Praise"],
        },
    },
    {
        "code": "strength",
        "name": "Strength",
        "tagline": "Advanced automation for larger HR operations.",
        "strength": "All Foundation features plus deeper workflow, analytics, and engagement.",
        "sort_order": 20,
        "features": {
            "Core HR": [
                "Employee Onboarding - Advanced", "E-signature", "Travel Desk", "Asset Tracking",
                "People Analytics", "Employee Timeline", "Custom Roles & Privileges",
                "Employee Exit Survey", "Notification Engine - Advanced", "Reports - Advanced",
            ],
            "Time & Attendance": ["Selfie clock-in", "Continuous Location Punching", "Geo Fencing"],
            "Employee Self Service": ["Single Sign-on (SSO)", "Login Using Mobile OTP"],
            "Employee Experience": ["Employee Pulse", "Surveys"],
        },
    },
    {
        "code": "growth",
        "name": "Growth",
        "tagline": "Performance management and business review capabilities.",
        "strength": "All Strength features plus goals, reviews, compensation planning, and skill intelligence.",
        "sort_order": 30,
        "features": {
            "Core HR": ["Workflow Automation", "Custom Reports Builder", "Headcount Planning", "Pre-boarding"],
            "Business Performance": [
                "Company Goals/OKRs", "Department and Individual Goals", "Goals Alignment",
                "Goal Insights", "Core Values",
            ],
            "Employee Performance": [
                "Praise & Recognition", "Continuous Feedback", "One-on-one Meetings",
                "Performance Reviews", "Performance Calibration", "Promotions",
                "Performance Improvement Plan", "Performance Insights", "Basic Compensation Plans",
                "Skills and Competencies", "Skill Analytics",
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
