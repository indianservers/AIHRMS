from app.db.base_class import Base  # noqa: F401

# Import all models so Alembic can detect them
from app.models.user import User, Role, Permission  # noqa: F401
from app.models.company import Company, Branch, Department, Designation  # noqa: F401
from app.models.employee import Employee, EmployeeEducation, EmployeeExperience, EmployeeSkill, EmployeeDocument  # noqa: F401
from app.models.attendance import Shift, Holiday, Attendance, AttendanceRegularization, OvertimeRequest  # noqa: F401
from app.models.leave import LeaveType, LeaveBalance, LeaveRequest  # noqa: F401
from app.models.payroll import (  # noqa: F401
    SalaryComponent, SalaryStructure, SalaryStructureComponent,
    EmployeeSalary, PayrollRun, PayrollRecord, PayrollComponent, Reimbursement
)
from app.models.recruitment import Job, Candidate, Interview, InterviewFeedback, OfferLetter  # noqa: F401
from app.models.onboarding import (  # noqa: F401
    OnboardingTemplate, OnboardingTask, EmployeeOnboarding, OnboardingTaskCompletion, PolicyAcknowledgement
)
from app.models.performance import AppraisalCycle, PerformanceGoal, PerformanceReview  # noqa: F401
from app.models.helpdesk import HelpdeskCategory, HelpdeskTicket, HelpdeskReply  # noqa: F401
from app.models.document import DocumentTemplate, GeneratedDocument, CompanyPolicy  # noqa: F401
from app.models.asset import AssetCategory, Asset, AssetAssignment  # noqa: F401
from app.models.exit import ExitRecord, ExitChecklistItem, ExitInterview  # noqa: F401
from app.models.target import FeatureCatalog, FeaturePlan, IndustryTarget  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
