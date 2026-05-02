from app.db.base_class import Base  # noqa: F401

# Import all models so Alembic can detect them
from app.models.user import User, Role, Permission  # noqa: F401
from app.models.company import Company, Branch, Department, Designation  # noqa: F401
from app.models.employee import Employee, EmployeeEducation, EmployeeExperience, EmployeeSkill, EmployeeDocument, EmployeeLifecycleEvent  # noqa: F401
from app.models.attendance import Shift, ShiftWeeklyOff, ShiftRosterAssignment, Holiday, Attendance, AttendancePunch, BiometricDevice, BiometricImportBatch, GeoAttendancePolicy, AttendancePunchProof, AttendanceMonthLock, AttendanceRegularization, OvertimeRequest  # noqa: F401
from app.models.leave import LeaveType, LeaveBalance, LeaveRequest, LeaveBalanceLedger  # noqa: F401
from app.models.payroll import (  # noqa: F401
    SalaryComponent, SalaryComponentCategory, SalaryComponentFormulaRule,
    SalaryStructure, SalaryStructureComponent,
    EmployeeSalary, PayrollRun, PayrollRecord, PayrollComponent, Reimbursement,
    PayrollVarianceItem, PayrollExportBatch, PayrollRunAuditLog,
    PayrollPayGroup, PayrollCalendar, PayrollStatutoryProfile, PayrollPeriod,
    PayrollComplianceRule, BankAdviceFormat,
    SalaryTemplate, SalaryTemplateComponent, EmployeeSalaryTemplateAssignment,
    EmployeeSalaryComponentOverride,
    SalaryRevisionRequest, SensitiveSalaryAuditLog,
    PayrollPreRunCheck, PayrollManualInput, PayrollUnlockRequest, PayslipPublishBatch,
    ReimbursementLedger, EmployeeLoan, EmployeeLoanInstallment, EmployeeLoanLedger,
    FullFinalSettlement, FullFinalSettlementLine,
    TaxRegime, TaxSlab, TaxSection, TaxSectionLimit, EmployeeTaxRegimeElection,
    EmployeeTaxWorksheet, EmployeeTaxWorksheetLine, PreviousEmploymentTaxDetail,
    PFRule, ESIRule, ProfessionalTaxSlab, LWFSlab, GratuityRule,
    EmployeeStatutoryProfile, PayrollStatutoryContributionLine,
    PayrollAttendanceInput, LOPAdjustment, OvertimePolicy, OvertimePayLine,
    LeaveEncashmentPolicy, LeaveEncashmentLine,
    PayrollRunEmployee, PayrollCalculationSnapshot,
    PayrollArrearRun, PayrollArrearLine, OffCyclePayrollRun,
    PayrollPaymentBatch, PayrollPaymentLine,
    AccountingLedger, PayrollGLMapping, PayrollJournalEntry, PayrollJournalLine,
    StatutoryFileValidation, StatutoryTemplateFile,
    StatutoryChallan, StatutoryReturnFile,
    TaxDeclarationCycle, TaxDeclaration, TaxDeclarationProof
)
from app.models.timesheet import Project, Timesheet, TimesheetEntry  # noqa: F401
from app.models.recruitment import Job, RecruitmentRequisition, Candidate, Interview, InterviewFeedback, OfferLetter  # noqa: F401
from app.models.onboarding import (  # noqa: F401
    OnboardingTemplate, OnboardingTask, EmployeeOnboarding, OnboardingTaskCompletion, PolicyAcknowledgement
)
from app.models.performance import AppraisalCycle, PerformanceGoal, PerformanceReview  # noqa: F401
from app.models.helpdesk import HelpdeskCategory, HelpdeskTicket, HelpdeskReply, HelpdeskKnowledgeArticle, HelpdeskEscalationRule  # noqa: F401
from app.models.document import DocumentTemplate, GeneratedDocument, CompanyPolicy, CompanyPolicyVersion, EmployeeCertificate, CertificateImportExportBatch  # noqa: F401
from app.models.asset import AssetCategory, Asset, AssetAssignment  # noqa: F401
from app.models.exit import ExitRecord, ExitChecklistItem, ExitInterview  # noqa: F401
from app.models.target import FeatureCatalog, FeaturePlan, IndustryTarget  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
from app.models.notification import Notification, NotificationDeliveryLog  # noqa: F401
from app.models.workflow_engine import WorkflowDefinition, WorkflowStepDefinition, WorkflowInstance, WorkflowTask  # noqa: F401
from app.models.lms import LearningCourse, LearningAssignment, LearningCertification  # noqa: F401
from app.models.engagement import Announcement, EngagementSurvey, EngagementSurveyResponse, Recognition  # noqa: F401
from app.models.whatsapp_ess import WhatsAppESSConfig, WhatsAppESSSession, WhatsAppESSMessage, WhatsAppESSTemplate, WhatsAppESSOptIn, WhatsAppESSDeliveryEvent  # noqa: F401
from app.models.statutory_compliance import PayrollLegalEntity, Form16Document, TDSReturnFiling, StatutoryPortalSubmission, StatutoryComplianceEvent  # noqa: F401
from app.models.benefits import BenefitPlan, EmployeeBenefitEnrollment, FlexiBenefitPolicy, EmployeeFlexiBenefitAllocation, BenefitPayrollDeduction  # noqa: F401
from app.models.background_verification import BackgroundVerificationVendor, BackgroundVerificationRequest, BackgroundVerificationCheck  # noqa: F401
from app.models.platform import CustomFieldDefinition, CustomFieldValue, ReportDefinition, ReportRun  # noqa: F401
