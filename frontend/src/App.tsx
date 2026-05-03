import React, { Suspense } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Toaster } from "@/components/ui/toaster";
import { useAuthStore } from "@/store/authStore";
import AppLayout from "@/components/layout/AppLayout";
import { canAccessRoute } from "@/lib/roles";

const LoginPage = React.lazy(() => import("@/pages/auth/LoginPage"));
const DashboardPage = React.lazy(() => import("@/pages/dashboard/DashboardPage"));
const ManagerDashboardPage = React.lazy(() => import("@/pages/dashboard/ManagerDashboardPage"));
const EmployeesPage = React.lazy(() => import("@/pages/employees/EmployeesPage"));
const EmployeeDirectoryPage = React.lazy(() => import("@/pages/employees/EmployeeDirectoryPage"));
const EmployeeDetailPage = React.lazy(() => import("@/pages/employees/EmployeeDetailPage"));
const AddEmployeePage = React.lazy(() => import("@/pages/employees/AddEmployeePage"));
const AttendancePage = React.lazy(() => import("@/pages/attendance/AttendancePage"));
const TimesheetsPage = React.lazy(() => import("@/pages/timesheets/TimesheetsPage"));
const WorkflowInboxPage = React.lazy(() => import("@/pages/workflow/WorkflowInboxPage"));
const WorkflowDesignerPage = React.lazy(() => import("@/pages/workflow/WorkflowDesignerPage"));
const NotificationsPage = React.lazy(() => import("@/pages/notifications/NotificationsPage"));
const LeavePage = React.lazy(() => import("@/pages/leave/LeavePage"));
const PayrollPage = React.lazy(() => import("@/pages/payroll/PayrollPage"));
const RecruitmentPage = React.lazy(() => import("@/pages/recruitment/RecruitmentPage"));
const PerformancePage = React.lazy(() => import("@/pages/performance/PerformancePage"));
const HelpdeskPage = React.lazy(() => import("@/pages/helpdesk/HelpdeskPage"));
const ReportsPage = React.lazy(() => import("@/pages/reports/ReportsPage"));
const AdminLogsPage = React.lazy(() => import("@/pages/logs/AdminLogsPage"));
const CompanyPage = React.lazy(() => import("@/pages/company/CompanyPage"));
const OrgChartPage = React.lazy(() => import("@/pages/company/OrgChartPage"));
const AIAssistantPage = React.lazy(() => import("@/pages/ai/AIAssistantPage"));
const ProfilePage = React.lazy(() => import("@/pages/profile/ProfilePage"));
const ESSPortalPage = React.lazy(() => import("@/pages/profile/ESSPortalPage"));
const AssetsPage = React.lazy(() => import("@/pages/assets/AssetsPage"));
const OnboardingPage = React.lazy(() => import("@/pages/onboarding/OnboardingPage"));
const DocumentsPage = React.lazy(() => import("@/pages/documents/DocumentsPage"));
const ExitPage = React.lazy(() => import("@/pages/exit/ExitPage"));
const SettingsPage = React.lazy(() => import("@/pages/settings/SettingsPage"));
const EngagementPage = React.lazy(() => import("@/pages/engagement/EngagementPage"));
const BenefitsPage = React.lazy(() => import("@/pages/benefits/BenefitsPage"));
const LMSPage = React.lazy(() => import("@/pages/lms/LMSPage"));
const StatutoryCompliancePage = React.lazy(() => import("@/pages/compliance/StatutoryCompliancePage"));
const BackgroundVerificationPage = React.lazy(() => import("@/pages/compliance/BackgroundVerificationPage"));
const WhatsAppESSPage = React.lazy(() => import("@/pages/platform/WhatsAppESSPage"));
const CustomFieldsPage = React.lazy(() => import("@/pages/platform/CustomFieldsPage"));
const EnterprisePage = React.lazy(() => import("@/pages/platform/EnterprisePage"));

function LoadingFallback() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
    </div>
  );
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const { isAuthenticated, isHydrated, user } = useAuthStore();
  if (!isHydrated) return <LoadingFallback />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (!canAccessRoute(location.pathname, user?.role, user?.is_superuser)) {
    return <Navigate to="/dashboard" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <>
      <Suspense fallback={<LoadingFallback />}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="manager-dashboard" element={<ManagerDashboardPage />} />
            <Route path="ess" element={<ESSPortalPage />} />
            <Route path="employee-directory" element={<EmployeeDirectoryPage />} />
            <Route path="employees" element={<EmployeesPage />} />
            <Route path="employees/new" element={<AddEmployeePage />} />
            <Route path="employees/:id" element={<EmployeeDetailPage />} />
            <Route path="attendance" element={<AttendancePage />} />
            <Route path="timesheets" element={<TimesheetsPage />} />
            <Route path="workflow" element={<WorkflowInboxPage />} />
            <Route path="workflow-designer" element={<WorkflowDesignerPage />} />
            <Route path="notifications" element={<NotificationsPage />} />
            <Route path="leave" element={<LeavePage />} />
            <Route path="payroll" element={<PayrollPage />} />
            <Route path="recruitment" element={<RecruitmentPage />} />
            <Route path="performance" element={<PerformancePage />} />
            <Route path="benefits" element={<BenefitsPage />} />
            <Route path="lms" element={<LMSPage />} />
            <Route path="statutory-compliance" element={<StatutoryCompliancePage />} />
            <Route path="background-verification" element={<BackgroundVerificationPage />} />
            <Route path="whatsapp-ess" element={<WhatsAppESSPage />} />
            <Route path="custom-fields" element={<CustomFieldsPage />} />
            <Route path="enterprise" element={<EnterprisePage />} />
            <Route path="engagement" element={<EngagementPage />} />
            <Route path="helpdesk" element={<HelpdeskPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="logs" element={<AdminLogsPage />} />
            <Route path="company" element={<CompanyPage />} />
            <Route path="org-chart" element={<OrgChartPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="assets" element={<AssetsPage />} />
            <Route path="onboarding" element={<OnboardingPage />} />
            <Route path="documents" element={<DocumentsPage />} />
            <Route path="exit" element={<ExitPage />} />
            <Route path="ai-assistant" element={<AIAssistantPage />} />
            <Route path="profile" element={<ProfilePage />} />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Suspense>
      <Toaster />
    </>
  );
}
