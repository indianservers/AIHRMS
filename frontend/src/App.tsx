import React, { Suspense } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Toaster } from "@/components/ui/toaster";
import { useAuthStore } from "@/store/authStore";
import AppLayout from "@/components/layout/AppLayout";
import { canAccessRoute } from "@/lib/roles";
import { getInstalledAppKeys, type FrontendRoute } from "@/appRegistry";
import { getDefaultPathForUser, getLoginPathForContext } from "@/lib/products";
import { hrmsRoutes } from "@/apps/hrms/routes";
import { crmRoutes } from "@/apps/crm/routes";
import { projectManagementRoutes } from "@/apps/project-management/routes";
import { aiAgentRoutes } from "@/pages/ai-agents/routes";
import PMSRealtimeBridge from "@/apps/project-management/PMSRealtimeBridge";

const LoginPage = React.lazy(() => import("@/pages/auth/LoginPage"));

const appRoutes: Record<string, FrontendRoute[]> = {
  hrms: hrmsRoutes,
  crm: crmRoutes,
  project_management: projectManagementRoutes,
};

function getEnabledRoutes() {
  return getInstalledAppKeys().flatMap((key) => appRoutes[key] || []);
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
  if (!isAuthenticated) return <Navigate to={getLoginPathForContext(location.pathname, user?.role, user?.is_superuser)} replace />;
  if (!canAccessRoute(location.pathname, user?.role, user?.is_superuser)) {
    return <Navigate to={getDefaultPathForUser(user?.role, user?.is_superuser)} replace />;
  }
  return <>{children}</>;
}

function ProductHomeRedirect() {
  const { user } = useAuthStore();
  return <Navigate to={getDefaultPathForUser(user?.role, user?.is_superuser)} replace />;
}

export default function App() {
  const enabledRoutes = getEnabledRoutes();
  const routes = [...enabledRoutes, ...aiAgentRoutes];

  return (
    <>
      <Suspense fallback={<LoadingFallback />}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/hrms/login" element={<LoginPage />} />
          <Route path="/crm/login" element={<LoginPage />} />
          <Route path="/pms/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<ProductHomeRedirect />} />
            {routes.map((route) => (
              <Route key={route.path} path={route.path} element={route.element} />
            ))}
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
      <PMSRealtimeBridge />
      <Toaster />
    </>
  );
}
