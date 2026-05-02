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
  GraduationCap,
  HelpCircle,
  HeartPulse,
  Landmark,
  LayoutDashboard,
  LogOut,
  Megaphone,
  MessageCircle,
  Network,
  Package,
  ScrollText,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
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
  group?: string;
  exact?: boolean;
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
  { label: "Dashboard", icon: LayoutDashboard, to: "/dashboard", group: "Core HR", exact: true },
  { label: "Employees", icon: Users, to: "/employees", group: "Core HR" },
  { label: "Inbox", icon: Inbox, to: "/workflow", group: "Core HR" },
  { label: "Workflow Designer", icon: GitBranch, to: "/workflow-designer", group: "Core HR" },
  { label: "Notifications", icon: Bell, to: "/notifications", group: "Core HR" },
  { label: "Attendance", icon: Clock, to: "/attendance", group: "Core HR" },
  { label: "Timesheets", icon: Timer, to: "/timesheets", group: "Core HR" },
  { label: "Leave", icon: CalendarDays, to: "/leave", group: "Core HR" },
  { label: "Payroll", icon: DollarSign, to: "/payroll", group: "Payroll & Finance" },
  { label: "Benefits", icon: HeartPulse, to: "/benefits", group: "Payroll & Finance" },
  { label: "Recruitment", icon: Briefcase, to: "/recruitment", group: "Talent" },
  { label: "Performance", icon: Target, to: "/performance", group: "Talent" },
  { label: "LMS", icon: GraduationCap, to: "/lms", group: "Talent" },
  { label: "Engagement", icon: Megaphone, to: "/engagement", group: "Talent" },
  { label: "Statutory Compliance", icon: Landmark, to: "/statutory-compliance", group: "Compliance" },
  { label: "BGV", icon: ShieldCheck, to: "/background-verification", group: "Compliance" },
  { label: "Helpdesk", icon: HelpCircle, to: "/helpdesk", group: "Compliance" },
  { label: "Reports", icon: BarChart3, to: "/reports", group: "Platform" },
  { label: "Company", icon: Building2, to: "/company", group: "Platform" },
  { label: "Org Chart", icon: GitBranch, to: "/org-chart", group: "Platform" },
  { label: "Onboarding", icon: ClipboardCheck, to: "/onboarding", group: "Platform" },
  { label: "Documents", icon: FileText, to: "/documents", group: "Platform" },
  { label: "Assets", icon: Package, to: "/assets", group: "Platform" },
  { label: "Exit", icon: LogOut, to: "/exit", group: "Platform" },
  { label: "WhatsApp ESS", icon: MessageCircle, to: "/whatsapp-ess", group: "Platform" },
  { label: "Custom Fields", icon: SlidersHorizontal, to: "/custom-fields", group: "Platform" },
  { label: "AI Assistant", icon: Sparkles, to: "/ai-assistant", badge: "AI", group: "Platform" },
];

const adminNav: RoleNavItem[] = [
  { label: "Dashboard", icon: LayoutDashboard, to: "/dashboard", group: "Core HR", exact: true },
  { label: "Inbox", icon: Inbox, to: "/workflow", group: "Core HR" },
  { label: "Workflow Designer", icon: GitBranch, to: "/workflow-designer", group: "Core HR" },
  { label: "Notifications", icon: Bell, to: "/notifications", group: "Core HR" },
  { label: "Employees", icon: Users, to: "/employees", group: "Core HR" },
  { label: "Attendance", icon: Clock, to: "/attendance", group: "Core HR" },
  { label: "Timesheets", icon: Timer, to: "/timesheets", group: "Core HR" },
  { label: "Leave", icon: CalendarDays, to: "/leave", group: "Core HR" },
  { label: "Payroll", icon: DollarSign, to: "/payroll", group: "Payroll & Finance" },
  { label: "Benefits", icon: HeartPulse, to: "/benefits", group: "Payroll & Finance" },
  { label: "Recruitment", icon: Briefcase, to: "/recruitment", group: "Talent" },
  { label: "Performance", icon: Target, to: "/performance", group: "Talent" },
  { label: "LMS", icon: GraduationCap, to: "/lms", group: "Talent" },
  { label: "Engagement", icon: Megaphone, to: "/engagement", group: "Talent" },
  { label: "Statutory Compliance", icon: Landmark, to: "/statutory-compliance", group: "Compliance" },
  { label: "BGV", icon: ShieldCheck, to: "/background-verification", group: "Compliance" },
  { label: "Helpdesk", icon: HelpCircle, to: "/helpdesk", group: "Compliance" },
  { label: "Company", icon: Building2, to: "/company", group: "Platform" },
  { label: "Org Chart", icon: GitBranch, to: "/org-chart", group: "Platform" },
  { label: "Settings", icon: Settings, to: "/settings", group: "Platform" },
  { label: "Logs", icon: ScrollText, to: "/logs", group: "Platform" },
  { label: "WhatsApp ESS", icon: MessageCircle, to: "/whatsapp-ess", group: "Platform" },
  { label: "Custom Fields", icon: SlidersHorizontal, to: "/custom-fields", group: "Platform" },
  { label: "Enterprise", icon: Network, to: "/enterprise", group: "Platform" },
  { label: "Reports", icon: BarChart3, to: "/reports", group: "Platform" },
  { label: "Onboarding", icon: ClipboardCheck, to: "/onboarding", group: "Platform" },
  { label: "Documents", icon: FileText, to: "/documents", group: "Platform" },
  { label: "Assets", icon: Package, to: "/assets", group: "Platform" },
  { label: "Exit", icon: LogOut, to: "/exit", group: "Platform" },
  { label: "AI Assistant", icon: Sparkles, to: "/ai-assistant", badge: "AI", group: "Platform" },
];

const ceoNav: RoleNavItem[] = [
  { label: "Executive Dashboard", icon: LayoutDashboard, to: "/dashboard", exact: true },
  { label: "Inbox", icon: Inbox, to: "/workflow" },
  { label: "Notifications", icon: Bell, to: "/notifications" },
  { label: "Reports", icon: BarChart3, to: "/reports" },
  { label: "Payroll", icon: DollarSign, to: "/payroll" },
  { label: "Benefits", icon: HeartPulse, to: "/benefits" },
  { label: "Performance", icon: Target, to: "/performance" },
  { label: "Engagement", icon: Megaphone, to: "/engagement" },
  { label: "Employees", icon: Users, to: "/employees" },
  { label: "Company", icon: Building2, to: "/company" },
  { label: "Org Chart", icon: GitBranch, to: "/org-chart" },
  { label: "AI Assistant", icon: Sparkles, to: "/ai-assistant", badge: "AI" },
];

const managerNav: RoleNavItem[] = [
  { label: "Team Dashboard", icon: LayoutDashboard, to: "/dashboard", exact: true },
  { label: "Manager Hub", icon: Users, to: "/manager-dashboard", exact: true },
  { label: "Inbox", icon: Inbox, to: "/workflow" },
  { label: "Notifications", icon: Bell, to: "/notifications" },
  { label: "Employees", icon: Users, to: "/employees" },
  { label: "Attendance", icon: Clock, to: "/attendance" },
  { label: "Timesheets", icon: Timer, to: "/timesheets" },
  { label: "Leave Approvals", icon: CalendarDays, to: "/leave" },
  { label: "Recruitment", icon: Briefcase, to: "/recruitment" },
  { label: "Assets", icon: Package, to: "/assets" },
  { label: "Performance", icon: Target, to: "/performance" },
  { label: "LMS", icon: GraduationCap, to: "/lms" },
  { label: "Engagement", icon: Megaphone, to: "/engagement" },
  { label: "Helpdesk", icon: HelpCircle, to: "/helpdesk" },
  { label: "Reports", icon: BarChart3, to: "/reports" },
  { label: "Org Chart", icon: GitBranch, to: "/org-chart" },
  { label: "AI Assistant", icon: Sparkles, to: "/ai-assistant", badge: "AI" },
];

const employeeNav: RoleNavItem[] = [
  { label: "My Home", icon: LayoutDashboard, to: "/dashboard", exact: true },
  { label: "ESS Portal", icon: UserRound, to: "/ess", exact: true },
  { label: "My Requests", icon: Inbox, to: "/workflow" },
  { label: "Notifications", icon: Bell, to: "/notifications" },
  { label: "Attendance", icon: Clock, to: "/attendance" },
  { label: "Timesheets", icon: Timer, to: "/timesheets" },
  { label: "Leave", icon: CalendarDays, to: "/leave" },
  { label: "Payslip", icon: DollarSign, to: "/payroll" },
  { label: "Benefits", icon: HeartPulse, to: "/benefits" },
  { label: "My Assets", icon: Package, to: "/assets" },
  { label: "Reviews", icon: Target, to: "/performance" },
  { label: "Learning", icon: GraduationCap, to: "/lms" },
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
  "/workflow-designer": ["admin", "hr"],
  "/notifications": ["admin", "ceo", "hr", "manager", "employee"],
  "/attendance": ["admin", "hr", "manager", "employee"],
  "/timesheets": ["admin", "ceo", "hr", "manager", "employee"],
  "/leave": ["admin", "hr", "manager", "employee"],
  "/payroll": ["admin", "ceo", "hr", "employee"],
  "/benefits": ["admin", "ceo", "hr", "employee"],
  "/performance": ["admin", "ceo", "hr", "manager", "employee"],
  "/lms": ["admin", "ceo", "hr", "manager", "employee"],
  "/statutory-compliance": ["admin", "ceo", "hr"],
  "/background-verification": ["admin", "hr"],
  "/whatsapp-ess": ["admin", "hr"],
  "/custom-fields": ["admin", "hr"],
  "/enterprise": ["admin"],
  "/engagement": ["admin", "ceo", "hr", "manager", "employee"],
  "/helpdesk": ["admin", "hr", "manager", "employee"],
  "/documents": ["admin", "hr", "employee"],
  "/employees": ["admin", "ceo", "hr", "manager"],
  "/reports": ["admin", "ceo", "hr", "manager"],
  "/logs": ["admin"],
  "/recruitment": ["admin", "hr", "manager"],
  "/company": ["admin", "ceo", "hr"],
  "/org-chart": ["admin", "ceo", "hr", "manager"],
  "/settings": ["admin"],
  "/assets": ["admin", "hr", "manager", "employee"],
  "/onboarding": ["admin", "hr"],
  "/exit": ["admin", "hr"],
  "/ai-assistant": ["admin", "ceo", "hr", "manager", "employee"],
};

export function canAccessRoute(pathname: string, role?: string | null, isSuperuser = false) {
  const key = getRoleKey(role, isSuperuser);
  const match = Object.keys(routeAccess)
    .sort((a, b) => b.length - a.length)
    .find((path) => pathname === path || pathname.startsWith(`${path}/`));
  if (!match) return key === "admin" || isSuperuser;
  return routeAccess[match].includes(key);
}

export function getSearchPlaceholder(role?: string | null, isSuperuser = false) {
  const key = getRoleKey(role, isSuperuser);
  if (key === "ceo") return "Search KPIs, payroll, reports...";
  if (key === "manager") return "Search team, leave, goals...";
  if (key === "employee") return "Search payslips, policies, tickets...";
  return "Search employees, documents, payroll...";
}
