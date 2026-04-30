import {
  BarChart3,
  Briefcase,
  Building2,
  CalendarDays,
  ClipboardCheck,
  Clock,
  DollarSign,
  FileText,
  HelpCircle,
  LayoutDashboard,
  LogOut,
  Package,
  Settings,
  Sparkles,
  Target,
  Users,
} from "lucide-react";

export type RoleKey = "ceo" | "hr" | "manager" | "employee";

export type RoleNavItem = {
  label: string;
  icon: React.ElementType;
  to: string;
  badge?: string;
};

export function getRoleKey(role?: string | null, isSuperuser = false): RoleKey {
  const value = (role || "").toLowerCase().replace(/\s+/g, "_");
  if (isSuperuser || ["super_admin", "admin", "hr_manager", "hr_admin", "hr"].includes(value)) return "hr";
  if (["ceo", "founder", "director", "executive"].includes(value)) return "ceo";
  if (["manager", "team_lead", "department_head"].includes(value)) return "manager";
  return "employee";
}

export function getRoleLabel(role?: string | null, isSuperuser = false) {
  const key = getRoleKey(role, isSuperuser);
  const labels: Record<RoleKey, string> = {
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
  { label: "Attendance", icon: Clock, to: "/attendance" },
  { label: "Leave", icon: CalendarDays, to: "/leave" },
  { label: "Payroll", icon: DollarSign, to: "/payroll" },
  { label: "Recruitment", icon: Briefcase, to: "/recruitment" },
  { label: "Performance", icon: Target, to: "/performance" },
  { label: "Helpdesk", icon: HelpCircle, to: "/helpdesk" },
  { label: "Reports", icon: BarChart3, to: "/reports" },
  { label: "Targets", icon: Target, to: "/targets" },
  { label: "Company", icon: Building2, to: "/company" },
  { label: "Settings", icon: Settings, to: "/settings" },
  { label: "Onboarding", icon: ClipboardCheck, to: "/onboarding" },
  { label: "Documents", icon: FileText, to: "/documents" },
  { label: "Assets", icon: Package, to: "/assets" },
  { label: "Exit", icon: LogOut, to: "/exit" },
  { label: "AI Assistant", icon: Sparkles, to: "/ai-assistant", badge: "AI" },
];

const ceoNav: RoleNavItem[] = [
  { label: "Executive Dashboard", icon: LayoutDashboard, to: "/dashboard" },
  { label: "Reports", icon: BarChart3, to: "/reports" },
  { label: "Payroll", icon: DollarSign, to: "/payroll" },
  { label: "Performance", icon: Target, to: "/performance" },
  { label: "Employees", icon: Users, to: "/employees" },
  { label: "Targets", icon: Target, to: "/targets" },
  { label: "Company", icon: Building2, to: "/company" },
  { label: "AI Assistant", icon: Sparkles, to: "/ai-assistant", badge: "AI" },
];

const managerNav: RoleNavItem[] = [
  { label: "Team Dashboard", icon: LayoutDashboard, to: "/dashboard" },
  { label: "Employees", icon: Users, to: "/employees" },
  { label: "Attendance", icon: Clock, to: "/attendance" },
  { label: "Leave Approvals", icon: CalendarDays, to: "/leave" },
  { label: "Performance", icon: Target, to: "/performance" },
  { label: "Helpdesk", icon: HelpCircle, to: "/helpdesk" },
  { label: "Reports", icon: BarChart3, to: "/reports" },
  { label: "AI Assistant", icon: Sparkles, to: "/ai-assistant", badge: "AI" },
];

const employeeNav: RoleNavItem[] = [
  { label: "My Home", icon: LayoutDashboard, to: "/dashboard" },
  { label: "Attendance", icon: Clock, to: "/attendance" },
  { label: "Leave", icon: CalendarDays, to: "/leave" },
  { label: "Payslip", icon: DollarSign, to: "/payroll" },
  { label: "Reviews", icon: Target, to: "/performance" },
  { label: "Helpdesk", icon: HelpCircle, to: "/helpdesk" },
  { label: "Documents", icon: FileText, to: "/documents" },
  { label: "AI Assistant", icon: Sparkles, to: "/ai-assistant", badge: "AI" },
];

export function getRoleNav(role?: string | null, isSuperuser = false) {
  const key = getRoleKey(role, isSuperuser);
  if (key === "ceo") return ceoNav;
  if (key === "manager") return managerNav;
  if (key === "employee") return employeeNav;
  return hrNav;
}

export function getSearchPlaceholder(role?: string | null, isSuperuser = false) {
  const key = getRoleKey(role, isSuperuser);
  if (key === "ceo") return "Search KPIs, payroll, reports...";
  if (key === "manager") return "Search team, leave, goals...";
  if (key === "employee") return "Search payslips, policies, tickets...";
  return "Search employees, documents, payroll...";
}
