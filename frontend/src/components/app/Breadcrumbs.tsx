import { Link, useLocation } from "react-router-dom";
import { ChevronRight } from "lucide-react";

const labels: Record<string, string> = {
  hrms: "HRMS",
  crm: "CRM",
  "project-management": "Project Management",
  dashboard: "Dashboard",
  employees: "Employees",
  attendance: "Attendance",
  timesheets: "Timesheets",
  workflow: "Workflow",
  notifications: "Notifications",
  leave: "Leave",
  payroll: "Payroll",
  recruitment: "Recruitment",
  performance: "Talent",
  helpdesk: "Helpdesk",
  reports: "Reports",
  company: "Company",
  settings: "Settings",
  assets: "Assets",
  onboarding: "Onboarding",
  documents: "Documents",
  exit: "Exit",
  profile: "Profile",
  "ai-assistant": "AI Assistant",
};

export default function Breadcrumbs() {
  const location = useLocation();
  const parts = location.pathname.split("/").filter(Boolean);
  if (!parts.length) return null;
  return (
    <nav className="mb-4 flex items-center gap-1 text-xs text-muted-foreground">
      <Link to="/" className="hover:text-foreground">Apps</Link>
      {parts.map((part, index) => {
        const path = `/${parts.slice(0, index + 1).join("/")}`;
        const active = index === parts.length - 1;
        return (
          <span key={path} className="flex items-center gap-1">
            <ChevronRight className="h-3 w-3" />
            {active ? (
              <span className="font-medium text-foreground">{labels[part] || part}</span>
            ) : (
              <Link to={path} className="hover:text-foreground">{labels[part] || part}</Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
