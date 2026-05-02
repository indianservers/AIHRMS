import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Toaster } from "@/components/ui/toaster";
import { useAuthStore } from "@/store/authStore";
import AppLayout from "@/components/layout/AppLayout";
import LoginPage from "@/pages/auth/LoginPage";
import DashboardPage from "@/pages/dashboard/DashboardPage";
import EmployeesPage from "@/pages/employees/EmployeesPage";
import EmployeeDetailPage from "@/pages/employees/EmployeeDetailPage";
import AddEmployeePage from "@/pages/employees/AddEmployeePage";
import AttendancePage from "@/pages/attendance/AttendancePage";
import TimesheetsPage from "@/pages/timesheets/TimesheetsPage";
import WorkflowInboxPage from "@/pages/workflow/WorkflowInboxPage";
import NotificationsPage from "@/pages/notifications/NotificationsPage";
import LeavePage from "@/pages/leave/LeavePage";
import PayrollPage from "@/pages/payroll/PayrollPage";
import RecruitmentPage from "@/pages/recruitment/RecruitmentPage";
import PerformancePage from "@/pages/performance/PerformancePage";
import HelpdeskPage from "@/pages/helpdesk/HelpdeskPage";
import ReportsPage from "@/pages/reports/ReportsPage";
import AdminLogsPage from "@/pages/logs/AdminLogsPage";
import CompanyPage from "@/pages/company/CompanyPage";
import AIAssistantPage from "@/pages/ai/AIAssistantPage";
import ProfilePage from "@/pages/profile/ProfilePage";
import AssetsPage from "@/pages/assets/AssetsPage";
import OnboardingPage from "@/pages/onboarding/OnboardingPage";
import DocumentsPage from "@/pages/documents/DocumentsPage";
import ExitPage from "@/pages/exit/ExitPage";
import SettingsPage from "@/pages/settings/SettingsPage";
import { canAccessRoute } from "@/lib/roles";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const { isAuthenticated, user } = useAuthStore();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (!canAccessRoute(location.pathname, user?.role, user?.is_superuser)) {
    return <Navigate to="/dashboard" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <>
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
          <Route path="employees" element={<EmployeesPage />} />
          <Route path="employees/new" element={<AddEmployeePage />} />
          <Route path="employees/:id" element={<EmployeeDetailPage />} />
          <Route path="attendance" element={<AttendancePage />} />
          <Route path="timesheets" element={<TimesheetsPage />} />
          <Route path="workflow" element={<WorkflowInboxPage />} />
          <Route path="notifications" element={<NotificationsPage />} />
          <Route path="leave" element={<LeavePage />} />
          <Route path="payroll" element={<PayrollPage />} />
          <Route path="recruitment" element={<RecruitmentPage />} />
          <Route path="performance" element={<PerformancePage />} />
          <Route path="helpdesk" element={<HelpdeskPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="logs" element={<AdminLogsPage />} />
          <Route path="company" element={<CompanyPage />} />
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
      <Toaster />
    </>
  );
}
