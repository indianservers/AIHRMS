import React from "react";
import type { FrontendRoute } from "@/appRegistry";

const CRMWorkspacePage = React.lazy(() => import("./CRMWorkspacePage"));

export const crmRoutes: FrontendRoute[] = [
  { path: "crm", element: <CRMWorkspacePage kind="dashboard" /> },
  { path: "crm/leads", element: <CRMWorkspacePage kind="leads" /> },
  { path: "crm/contacts", element: <CRMWorkspacePage kind="contacts" /> },
  { path: "crm/companies", element: <CRMWorkspacePage kind="companies" /> },
  { path: "crm/deals", element: <CRMWorkspacePage kind="deals" /> },
  { path: "crm/pipeline", element: <CRMWorkspacePage kind="pipeline" /> },
  { path: "crm/activities", element: <CRMWorkspacePage kind="activities" /> },
  { path: "crm/tasks", element: <CRMWorkspacePage kind="tasks" /> },
  { path: "crm/calendar", element: <CRMWorkspacePage kind="calendar" /> },
  { path: "crm/campaigns", element: <CRMWorkspacePage kind="campaigns" /> },
  { path: "crm/products", element: <CRMWorkspacePage kind="products" /> },
  { path: "crm/quotations", element: <CRMWorkspacePage kind="quotations" /> },
  { path: "crm/tickets", element: <CRMWorkspacePage kind="tickets" /> },
  { path: "crm/files", element: <CRMWorkspacePage kind="files" /> },
  { path: "crm/reports", element: <CRMWorkspacePage kind="reports" /> },
  { path: "crm/automation", element: <CRMWorkspacePage kind="automation" /> },
  { path: "crm/settings", element: <CRMWorkspacePage kind="settings" /> },
  { path: "crm/admin", element: <CRMWorkspacePage kind="admin" /> },
];
