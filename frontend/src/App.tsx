import React, { Suspense } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Toaster } from "@/components/ui/toaster";
import { useAuthStore } from "@/store/authStore";
import AppLayout from "@/components/layout/AppLayout";
import { canAccessRoute } from "@/lib/roles";
import { getInstalledAppKeys, type FrontendRoute } from "@/appRegistry";
import { hrmsRoutes } from "@/apps/hrms/routes";
import { crmRoutes } from "@/apps/crm/routes";
import { projectManagementRoutes } from "@/apps/project-management/routes";

const LoginPage = React.lazy(() => import("@/pages/auth/LoginPage"));
const SuiteIndexPage = React.lazy(() => import("@/pages/SuiteIndexPage"));

const appRoutes: Record<string, FrontendRoute[]> = {
  hrms: hrmsRoutes,
  crm: crmRoutes,
  project_management: projectManagementRoutes,
};

function getEnabledRoutes() {
  return getInstalledAppKeys().flatMap((key) => appRoutes[key] || []);
}

function getDefaultPath() {
  return "/";
}

function getLoginPath(pathname: string) {
  if (pathname.startsWith("/crm")) return "/crm/login";
  if (pathname.startsWith("/project-management")) return "/project-management/login";
  if (pathname.startsWith("/hrms")) return "/hrms/login";
  return "/login";
}

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
  if (!isAuthenticated) return <Navigate to={getLoginPath(location.pathname)} replace />;
  if (!canAccessRoute(location.pathname, user?.role, user?.is_superuser)) {
    return <Navigate to={getLoginPath(location.pathname)} replace />;
  }
  return <>{children}</>;
}

export default function App() {
  const enabledRoutes = getEnabledRoutes();
  const defaultPath = getDefaultPath();

  return (
    <>
      <Suspense fallback={<LoadingFallback />}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/hrms/login" element={<LoginPage />} />
          <Route path="/crm/login" element={<LoginPage />} />
          <Route path="/project-management/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<SuiteIndexPage />} />
            {enabledRoutes.map((route) => (
              <Route key={route.path} path={route.path} element={route.element} />
            ))}
          </Route>
          <Route path="*" element={<Navigate to={defaultPath} replace />} />
        </Routes>
      </Suspense>
      <Toaster />
    </>
  );
}
