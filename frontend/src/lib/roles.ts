import {
  BarChart3,
  Bell,
  Briefcase,
  Building2,
  CalendarDays,
  ClipboardCheck,
  Clock,
  Inbox,
  Timer,
  DollarSign,
  FileText,
  GitBranch,
  HelpCircle,
  LayoutDashboard,
  LogOut,
  Megaphone,
  Package,
  ScrollText,
  Settings,
  Sparkles,
  Target,
  UserRound,
  Users,
} from "lucide-react";

export type RoleKey = "admin" | "ceo" | "hr" | "manager" | "employee";

export type RoleNavItem = {
  label: string;
  icon: React.ElementType;
  to: string;
  badge?: string;
};

export function getRoleKey(role?: string | null, isSuperuser = false): RoleKey {
  const value = (role || "").toLowerCase().replace(/\s+/g, "_");
  if (isSuperuser || ["super_admin", "admin"].includes(value)) return "admin";
  if (["hr_manager", "hr_admin", "hr"].includes(value)) return "hr";
  if (["ceo", "founder", "director", "executive"].includes(value)) return "ceo";
  if (["manager", "team_lead", "department_head"].includes(value)) return "manager";
  return "employee";
}

export function getRoleLabel(role?: string | null, isSuperuser = false) {
  const key = getRoleKey(role, isSuperuser);
  const labels: Record<RoleKey, string> = {
    admin: "Admin Console",
    ceo: "CEO Console",
    hr: "HR Admin Console",
    manager: "Manager Workspace",
    employee: "Employee Self Service",
  };
  return labels[key];
}

const hrNav: RoleNavItem[] = [
  { label: "Dashboard", icon: LayoutDashboard, to: "/dashboard" },
  { label: "Employees", icon: Users, to: "/employees" },
  { label: "Inbox", icon: Inbox, to: "/workflow" },
  { label: "Notifications", icon: Bell, to: "/notifications" },
  { label: "Attendance", icon: Clock, to: "/attendance" },
  { label: "Timesheets", icon: Timer, to: "/timesheets" },
  { label: "Leave", icon: CalendarDays, to: "/leave" },
  { label: "Payroll", icon: DollarSign, to: "/payroll" },
  { label: "Recruitment", icon: Briefcase, to: "/recruitment" },
  { label: "Performance", icon: Target, to: "/performance" },
  { label: "Engagement", icon: Megaphone, to: "/engagement" },
  { label: "Helpdesk", icon: HelpCircle, to: "/helpdesk" },
  { label: "Reports", icon: BarChart3, to: "/reports" },
  { label: "Company", icon: Building2, to: "/company" },
  { label: "Org Chart", icon: GitBranch, to: "/org-chart" },
  { label: "Onboarding", icon: ClipboardCheck, to: "/onboarding" },
  { label: "Documents", icon: FileText, to: "/documents" },
  { label: "Assets", icon: Package, to: "/assets" },
  { label: "Exit", icon: LogOut, to: "/exit" },
  { label: "AI Assistant", icon: Sparkles, to: "/ai-assistant", badge: "AI" },
];

const adminNav: RoleNavItem[] = [
  { label: "Dashboard", icon: LayoutDashboard, to: "/dashboard" },
  { label: "Company", icon: Building2, to: "/company" },
  { label: "Org Chart", icon: GitBranch, to: "/org-chart" },
  { label: "Settings", icon: Settings, to: "/settings" },
  { label: "Logs", icon: ScrollText, to: "/logs" },
  { label: "Inbox", icon: Inbox, to: "/workflow" },
  { label: "Notifications", icon: Bell, to: "/notifications" },
  { label: "Employees", icon: Users, to: "/employees" },
  { label: "Attendance", icon: Clock, to: "/attendance" },
  { label: "Timesheets", icon: Timer, to: "/timesheets" },
  { label: "Leave", icon: CalendarDays, to: "/leave" },
  { label: "Payroll", icon: DollarSign, to: "/payroll" },
  { label: "Recruitment", icon: Briefcase, to: "/recruitment" },
  { label: "Performance", icon: Target, to: "/performance" },
  { label: "Engagement", icon: Megaphone, to: "/engagement" },
  { label: "Helpdesk", icon: HelpCircle, to: "/helpdesk" },
  { label: "Reports", icon: BarChart3, to: "/reports" },
  { label: "Onboarding", icon: ClipboardCheck, to: "/onboarding" },
  { label: "Documents", icon: FileText, to: "/documents" },
  { label: "Assets", icon: Package, to: "/assets" },
  { label: "Exit", icon: LogOut, to: "/exit" },
  { label: "AI Assistant", icon: Sparkles, to: "/ai-assistant", badge: "AI" },
];

const ceoNav: RoleNavItem[] = [
  { label: "Executive Dashboard", icon: LayoutDashboard, to: "/dashboard" },
  { label: "Inbox", icon: Inbox, to: "/workflow" },
  { label: "Notifications", icon: Bell, to: "/notifications" },
  { label: "Reports", icon: BarChart3, to: "/reports" },
  { label: "Payroll", icon: DollarSign, to: "/payroll" },
  { label: "Performance", icon: Target, to: "/performance" },
  { label: "Engagement", icon: Megaphone, to: "/engagement" },
  { label: "Employees", icon: Users, to: "/employees" },
  { label: "Company", icon: Building2, to: "/company" },
  { label: "Org Chart", icon: GitBranch, to: "/org-chart" },
  { label: "AI Assistant", icon: Sparkles, to: "/ai-assistant", badge: "AI" },
];

const managerNav: RoleNavItem[] = [
  { label: "Team Dashboard", icon: LayoutDashboard, to: "/dashboard" },
  { label: "Manager Hub", icon: Users, to: "/manager-dashboard" },
  { label: "Inbox", icon: Inbox, to: "/workflow" },
  { label: "Notifications", icon: Bell, to: "/notifications" },
  { label: "Employees", icon: Users, to: "/employees" },
  { label: "Attendance", icon: Clock, to: "/attendance" },
  { label: "Timesheets", icon: Timer, to: "/timesheets" },
  { label: "Leave Approvals", icon: CalendarDays, to: "/leave" },
  { label: "Performance", icon: Target, to: "/performance" },
  { label: "Engagement", icon: Megaphone, to: "/engagement" },
  { label: "Helpdesk", icon: HelpCircle, to: "/helpdesk" },
  { label: "Reports", icon: BarChart3, to: "/reports" },
  { label: "Org Chart", icon: GitBranch, to: "/org-chart" },
  { label: "AI Assistant", icon: Sparkles, to: "/ai-assistant", badge: "AI" },
];

const employeeNav: RoleNavItem[] = [
  { label: "My Home", icon: LayoutDashboard, to: "/dashboard" },
  { label: "ESS Portal", icon: UserRound, to: "/ess" },
  { label: "My Requests", icon: Inbox, to: "/workflow" },
  { label: "Notifications", icon: Bell, to: "/notifications" },
  { label: "Attendance", icon: Clock, to: "/attendance" },
  { label: "Timesheets", icon: Timer, to: "/timesheets" },
  { label: "Leave", icon: CalendarDays, to: "/leave" },
  { label: "Payslip", icon: DollarSign, to: "/payroll" },
  { label: "Reviews", icon: Target, to: "/performance" },
  { label: "Engagement", icon: Megaphone, to: "/engagement" },
  { label: "Helpdesk", icon: HelpCircle, to: "/helpdesk" },
  { label: "Documents", icon: FileText, to: "/documents" },
  { label: "AI Assistant", icon: Sparkles, to: "/ai-assistant", badge: "AI" },
];

export function getRoleNav(role?: string | null, isSuperuser = false) {
  const key = getRoleKey(role, isSuperuser);
  if (key === "admin") return adminNav;
  if (key === "ceo") return ceoNav;
  if (key === "manager") return managerNav;
  if (key === "employee") return employeeNav;
  return hrNav;
}

const routeAccess: Record<string, RoleKey[]> = {
  "/dashboard": ["admin", "ceo", "hr", "manager", "employee"],
  "/manager-dashboard": ["admin", "hr", "manager"],
  "/ess": ["admin", "ceo", "hr", "manager", "employee"],
  "/profile": ["admin", "ceo", "hr", "manager", "employee"],
  "/workflow": ["admin", "ceo", "hr", "manager", "employee"],
  "/notifications": ["admin", "ceo", "hr", "manager", "employee"],
  "/attendance": ["admin", "hr", "manager", "employee"],
  "/timesheets": ["admin", "ceo", "hr", "manager", "employee"],
  "/leave": ["admin", "hr", "manager", "employee"],
  "/payroll": ["admin", "ceo", "hr", "employee"],
  "/performance": ["admin", "ceo", "hr", "manager", "employee"],
  "/engagement": ["admin", "ceo", "hr", "manager", "employee"],
  "/helpdesk": ["admin", "hr", "manager", "employee"],
  "/documents": ["admin", "hr", "employee"],
  "/employees": ["admin", "ceo", "hr", "manager"],
  "/reports": ["admin", "ceo", "hr", "manager"],
  "/logs": ["admin"],
  "/recruitment": ["admin", "hr"],
  "/company": ["admin", "ceo", "hr"],
  "/org-chart": ["admin", "ceo", "hr", "manager"],
  "/settings": ["admin"],
  "/assets": ["admin", "hr"],
  "/onboarding": ["admin", "hr"],
  "/exit": ["admin", "hr"],
  "/ai-assistant": ["admin", "ceo", "hr", "manager", "employee"],
};

export function canAccessRoute(pathname: string, role?: string | null, isSuperuser = false) {
  const key = getRoleKey(role, isSuperuser);
  const match = Object.keys(routeAccess)
    .sort((a, b) => b.length - a.length)
    .find((path) => pathname === path || pathname.startsWith(`${path}/`));
  if (!match) return true;
  return routeAccess[match].includes(key);
}

export function getSearchPlaceholder(role?: string | null, isSuperuser = false) {
  const key = getRoleKey(role, isSuperuser);
  if (key === "ceo") return "Search KPIs, payroll, reports...";
  if (key === "manager") return "Search team, leave, goals...";
  if (key === "employee") return "Search payslips, policies, tickets...";
  return "Search employees, documents, payroll...";
}
