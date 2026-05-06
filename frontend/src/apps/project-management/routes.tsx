import React from "react";
import type { FrontendRoute } from "@/appRegistry";

// Lazy load components
const ProjectManagementHomePage = React.lazy(() => import("./ProjectManagementHomePage"));
const ProjectDashboard = React.lazy(() => import("./pages/ProjectDashboard"));
const KanbanBoard = React.lazy(() => import("./pages/KanbanBoard"));
const ProjectsList = React.lazy(() => import("./pages/ProjectsList"));
const CreateProjectPage = React.lazy(() => import("./pages/CreateProjectPage"));
const TaskDetail = React.lazy(() => import("./pages/TaskDetail"));
const MilestonesPage = React.lazy(() => import("./pages/MilestonesPage"));
const TimeTrackingPage = React.lazy(() => import("./pages/TimeTrackingPage"));
const ReportsPage = React.lazy(() => import("./pages/ReportsPage"));
const CalendarPage = React.lazy(() => import("./pages/CalendarPage"));
const GanttPage = React.lazy(() => import("./pages/GanttPage"));
const SprintsPage = React.lazy(() => import("./pages/SprintsPage"));
const FilesPage = React.lazy(() => import("./pages/FilesPage"));
const ClientPortalPage = React.lazy(() => import("./pages/ClientPortalPage"));
const AdminPage = React.lazy(() => import("./pages/AdminPage"));
const SettingsPage = React.lazy(() => import("./pages/SettingsPage"));
const SoftwarePlanningPage = React.lazy(() => import("./pages/SoftwarePlanningPage"));
const LiveWorkManagementPage = React.lazy(() => import("./pages/LiveWorkManagementPage"));
const ImpactWorkHubPage = React.lazy(() => import("./pages/ImpactWorkHubPage"));
const TimelineDependenciesPage = React.lazy(() => import("./pages/TimelineDependenciesPage"));
const AutomationAIPage = React.lazy(() => import("./pages/AutomationAIPage"));
const CommandCenterPage = React.lazy(() => import("./pages/CommandCenterPage"));
const EnterpriseEnginePage = React.lazy(() => import("./pages/EnterpriseEnginePage"));
const ProductLaunchPage = React.lazy(() => import("./pages/ProductLaunchPage"));

/**
 * KaryaFlow Routes
 * Complete routing for Project Management module
 */
export const projectManagementRoutes: FrontendRoute[] = [
  // Home / Dashboard
  { path: "project-management", element: <ProjectManagementHomePage /> },
  { path: "project-management/command-center", element: <CommandCenterPage /> },
  { path: "project-management/enterprise-engine", element: <EnterpriseEnginePage /> },
  { path: "project-management/product-launch", element: <ProductLaunchPage /> },
  
  // Projects
  { path: "project-management/projects", element: <ProjectsList /> },
  { path: "project-management/projects/new", element: <CreateProjectPage /> },
  
  // Project Dashboard & Views
  { path: "project-management/projects/:projectId", element: <ProjectDashboard /> },
  { path: "project-management/projects/:projectId/board", element: <KanbanBoard /> },
  { path: "project-management/projects/:projectId/timeline", element: <GanttPage /> },
  { path: "project-management/projects/:projectId/gantt", element: <GanttPage /> },
  { path: "project-management/projects/:projectId/milestones", element: <MilestonesPage /> },
  { path: "project-management/projects/:projectId/files", element: <FilesPage /> },
  { path: "project-management/projects/:projectId/reports", element: <ReportsPage /> },
  
  // Tasks
  { path: "project-management/projects/:projectId/tasks/:taskId", element: <TaskDetail /> },

  // KaryaFlow software delivery workspaces
  { path: "project-management/work-hub", element: <ImpactWorkHubPage /> },
  { path: "project-management/impact", element: <ImpactWorkHubPage /> },
  { path: "project-management/ai-planner", element: <ImpactWorkHubPage /> },
  { path: "project-management/timeline-plus", element: <TimelineDependenciesPage /> },
  { path: "project-management/dependency-timeline", element: <TimelineDependenciesPage /> },
  { path: "project-management/automation-ai", element: <AutomationAIPage /> },
  { path: "project-management/software", element: <SoftwarePlanningPage /> },
  { path: "project-management/live", element: <LiveWorkManagementPage /> },
  { path: "project-management/teams-live", element: <LiveWorkManagementPage /> },
  { path: "project-management/backlog", element: <SoftwarePlanningPage /> },
  { path: "project-management/issues", element: <SoftwarePlanningPage /> },
  { path: "project-management/roadmap", element: <SoftwarePlanningPage /> },
  { path: "project-management/releases", element: <SoftwarePlanningPage /> },
  { path: "project-management/automation", element: <AutomationAIPage /> },
  { path: "project-management/goals", element: <CommandCenterPage /> },
  { path: "project-management/forms", element: <CommandCenterPage /> },
  { path: "project-management/templates", element: <CommandCenterPage /> },
  { path: "project-management/components", element: <CommandCenterPage /> },
  { path: "project-management/workflows", element: <CommandCenterPage /> },
  { path: "project-management/security", element: <CommandCenterPage /> },
  { path: "project-management/dependencies", element: <CommandCenterPage /> },
  { path: "project-management/navigator", element: <CommandCenterPage /> },
  { path: "project-management/apps", element: <CommandCenterPage /> },
  { path: "project-management/dashboards", element: <CommandCenterPage /> },
  { path: "project-management/plans", element: <CommandCenterPage /> },
  { path: "project-management/issue-navigator-pro", element: <EnterpriseEnginePage /> },
  { path: "project-management/backlog-grooming", element: <EnterpriseEnginePage /> },
  { path: "project-management/sprint-lifecycle", element: <EnterpriseEnginePage /> },
  { path: "project-management/blueprints", element: <EnterpriseEnginePage /> },
  { path: "project-management/resource-utilization", element: <EnterpriseEnginePage /> },
  
  // Module-level workspaces
  { path: "project-management/calendar", element: <CalendarPage /> },
  { path: "project-management/gantt", element: <GanttPage /> },
  { path: "project-management/sprints", element: <SprintsPage /> },
  { path: "project-management/files", element: <FilesPage /> },
  { path: "project-management/time-tracking", element: <TimeTrackingPage /> },
  { path: "project-management/reports", element: <ReportsPage /> },
  { path: "project-management/client-portal", element: <ClientPortalPage /> },
  { path: "project-management/settings", element: <SettingsPage /> },
  { path: "project-management/admin", element: <AdminPage /> },
];

