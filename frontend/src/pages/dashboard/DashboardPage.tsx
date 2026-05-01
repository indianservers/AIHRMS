import { useQuery } from "@tanstack/react-query";
import {
  Users, Clock, CalendarDays, Briefcase, TrendingUp, TrendingDown,
  CheckCircle2, AlertCircle, Building2, DollarSign, ShieldCheck, Target,
  FileText, HelpCircle, Award, UserCheck, ArrowRight, BarChart3, Sparkles
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { reportsApi } from "@/services/api";
import { formatCurrency } from "@/lib/utils";
import { useAuthStore } from "@/store/authStore";
import { getRoleKey, getRoleLabel } from "@/lib/roles";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from "recharts";

const COLORS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"];

function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  color = "blue",
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ElementType;
  trend?: { value: number; label: string };
  color?: string;
}) {
  const colorMap: Record<string, string> = {
    blue: "bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
    green: "bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400",
    yellow: "bg-yellow-50 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400",
    red: "bg-red-50 text-red-600 dark:bg-red-900/30 dark:text-red-400",
    purple: "bg-purple-50 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400",
  };

  return (
    <Card className="stat-card">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-3xl font-bold tracking-tight">{value}</p>
            {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
            {trend && (
              <div className="flex items-center gap-1 text-xs">
                {trend.value >= 0 ? (
                  <TrendingUp className="h-3 w-3 text-green-500" />
                ) : (
                  <TrendingDown className="h-3 w-3 text-red-500" />
                )}
                <span className={trend.value >= 0 ? "text-green-600" : "text-red-600"}>
                  {Math.abs(trend.value)}% {trend.label}
                </span>
              </div>
            )}
          </div>
          <div className={`rounded-xl p-3 ${colorMap[color]}`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function SkeletonCard() {
  return (
    <Card className="stat-card">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <div className="h-4 w-24 skeleton rounded" />
            <div className="h-8 w-16 skeleton rounded" />
            <div className="h-3 w-20 skeleton rounded" />
          </div>
          <div className="h-12 w-12 skeleton rounded-xl" />
        </div>
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  const roleKey = getRoleKey(user?.role, user?.is_superuser);
  const roleLabel = getRoleLabel(user?.role, user?.is_superuser);

  const { data: dashboard, isLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => reportsApi.dashboard().then((r) => r.data),
  });

  const { data: deptData } = useQuery({
    queryKey: ["headcount-by-dept"],
    queryFn: () => reportsApi.headcountByDept().then((r) => r.data),
  });

  const currentMonth = new Date().getMonth() + 1;
  const currentYear = new Date().getFullYear();

  const { data: payrollData } = useQuery({
    queryKey: ["payroll-summary", currentYear],
    queryFn: () => reportsApi.payrollSummary(currentYear).then((r) => r.data),
  });

  const employeeActions = [
    { label: "Check Attendance", detail: "Clock in, clock out, regularize", icon: Clock, href: "/attendance" },
    { label: "Apply Leave", detail: "Balances and leave requests", icon: CalendarDays, href: "/leave" },
    { label: "Download Payslip", detail: "Monthly salary slip", icon: DollarSign, href: "/payroll" },
    { label: "Raise Ticket", detail: "HR helpdesk support", icon: HelpCircle, href: "/helpdesk" },
  ];

  const managerActions = [
    { label: "Leave Approvals", detail: `${dashboard?.leaves?.pending_approvals ?? 0} requests pending`, icon: CalendarDays, href: "/leave" },
    { label: "Team Performance", detail: "Goals, reviews, feedback", icon: Target, href: "/performance" },
    { label: "Team Attendance", detail: "Monthly presence trends", icon: Clock, href: "/attendance" },
    { label: "Open Helpdesk", detail: "Resolve employee issues", icon: HelpCircle, href: "/helpdesk" },
  ];

  const ceoMetrics = [
    { label: "Active Workforce", value: dashboard?.headcount?.active ?? 0, icon: Users, tone: "text-blue-600" },
    { label: "Monthly Payroll", value: formatCurrency(payrollData?.reduce?.((sum: number, row: { net?: number }) => sum + Number(row.net || 0), 0) || 0), icon: DollarSign, tone: "text-emerald-600" },
    { label: "Open Roles", value: dashboard?.recruitment?.open_positions ?? 0, icon: Briefcase, tone: "text-violet-600" },
    { label: "Pending Decisions", value: dashboard?.leaves?.pending_approvals ?? 0, icon: ShieldCheck, tone: "text-amber-600" },
  ];

  if (roleKey === "employee") {
    return (
      <div className="space-y-5">
        <div className="rounded-lg border bg-card p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{roleLabel}</p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight">My HR workspace</h1>
          <p className="mt-1 text-sm text-muted-foreground">Attendance, leave, payslips, documents, and support in one place.</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {employeeActions.map((item) => (
            <a key={item.label} href={item.href} className="group rounded-lg border bg-card p-4 shadow-sm transition hover:border-primary/50 hover:shadow-md">
              <div className="flex items-center justify-between">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <item.icon className="h-5 w-5" />
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground transition group-hover:translate-x-1 group-hover:text-primary" />
              </div>
              <p className="mt-4 font-medium">{item.label}</p>
              <p className="mt-1 text-sm text-muted-foreground">{item.detail}</p>
            </a>
          ))}
        </div>

        <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">My Week</CardTitle>
              <CardDescription>Quick personal summary</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3 sm:grid-cols-3">
              {[
                ["Present", dashboard?.attendance?.present_today ?? 0, UserCheck],
                ["Leave Balance", "View", CalendarDays],
                ["Documents", "Ready", FileText],
              ].map(([label, value, Icon]) => (
                <div key={label as string} className="rounded-lg border p-4">
                  <Icon className="mb-3 h-5 w-5 text-primary" />
                  <p className="text-xl font-semibold">{value as string}</p>
                  <p className="text-xs text-muted-foreground">{label as string}</p>
                </div>
              ))}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Recognition</CardTitle>
              <CardDescription>Praise and culture moments</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {["Problem Solver", "Relentless Cogwheel", "Customer First"].map((label, index) => (
                <div key={label} className="flex items-center gap-3 rounded-lg border p-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-amber-100 text-amber-700">
                    <Award className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">{label}</p>
                    <p className="text-xs text-muted-foreground">{index + 1} praise received</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (roleKey === "manager") {
    return (
      <div className="space-y-5">
        <div className="flex flex-col gap-3 rounded-lg border bg-card p-5 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{roleLabel}</p>
            <h1 className="mt-2 text-2xl font-semibold tracking-tight">Team command center</h1>
            <p className="mt-1 text-sm text-muted-foreground">Approvals, team attendance, goals, and employee issues.</p>
          </div>
          <Badge variant="outline">{dashboard?.leaves?.pending_approvals ?? 0} approvals pending</Badge>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {managerActions.map((item) => (
            <a key={item.label} href={item.href} className="rounded-lg border bg-card p-4 shadow-sm transition hover:border-primary/50 hover:shadow-md">
              <item.icon className="mb-4 h-5 w-5 text-primary" />
              <p className="font-medium">{item.label}</p>
              <p className="mt-1 text-sm text-muted-foreground">{item.detail}</p>
            </a>
          ))}
        </div>

        <div className="grid gap-5 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Headcount by Department</CardTitle>
              <CardDescription>Team distribution and capacity</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={deptData || []} margin={{ top: 0, right: 0, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="department" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Manager Inbox</CardTitle>
              <CardDescription>Requests needing action</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {managerActions.map((item) => (
                <a key={item.label} href={item.href} className="flex items-center justify-between rounded-lg border p-3 hover:bg-muted/50">
                  <div className="flex items-center gap-3">
                    <item.icon className="h-4 w-4 text-primary" />
                    <div>
                      <p className="text-sm font-medium">{item.label}</p>
                      <p className="text-xs text-muted-foreground">{item.detail}</p>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </a>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (roleKey === "ceo") {
    return (
      <div className="space-y-5">
        <div className="rounded-lg border bg-card p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{roleLabel}</p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight">Executive people dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">Workforce health, payroll exposure, hiring movement, and operating priorities.</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {ceoMetrics.map((metric) => (
            <Card key={metric.label}>
              <CardContent className="p-5">
                <metric.icon className={`mb-4 h-5 w-5 ${metric.tone}`} />
                <p className="text-2xl font-semibold">{metric.value}</p>
                <p className="text-xs uppercase tracking-wide text-muted-foreground">{metric.label}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid gap-5 lg:grid-cols-[1.3fr_0.7fr]">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Payroll Trend</CardTitle>
              <CardDescription>Gross vs net salary comparison</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={payrollData || []} margin={{ top: 0, right: 0, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="month" tickFormatter={(m) => new Date(currentYear, m - 1).toLocaleString("en", { month: "short" })} tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}K`} />
                  <Tooltip formatter={(v: number) => formatCurrency(v)} />
                  <Legend />
                  <Bar dataKey="gross" name="Gross" fill="#2563eb" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="net" name="Net" fill="#059669" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Board Pack</CardTitle>
              <CardDescription>High-signal HR views</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                ["Reports & Analytics", "/reports", BarChart3],
                ["Company Setup", "/company", Building2],
                ["AI Workforce Notes", "/ai-assistant", Sparkles],
              ].map(([label, href, Icon]) => (
                <a key={label as string} href={href as string} className="flex items-center justify-between rounded-lg border p-3 hover:bg-muted/50">
                  <span className="flex items-center gap-3 text-sm font-medium">
                    <Icon className="h-4 w-4 text-primary" />
                    {label as string}
                  </span>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </a>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="page-title">Dashboard</h1>
        <p className="page-description">
          Welcome back! Here's your HR overview for today.
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : (
          <>
            <StatCard
              title="Total Employees"
              value={dashboard?.headcount?.total ?? 0}
              subtitle={`${dashboard?.headcount?.active ?? 0} active`}
              icon={Users}
              color="blue"
              trend={{ value: 5, label: "this month" }}
            />
            <StatCard
              title="Present Today"
              value={dashboard?.attendance?.present_today ?? 0}
              subtitle={`${dashboard?.attendance?.absent_today ?? 0} absent`}
              icon={Clock}
              color="green"
            />
            <StatCard
              title="Pending Leaves"
              value={dashboard?.leaves?.pending_approvals ?? 0}
              subtitle="Awaiting approval"
              icon={CalendarDays}
              color="yellow"
            />
            <StatCard
              title="Open Positions"
              value={dashboard?.recruitment?.open_positions ?? 0}
              subtitle={`${dashboard?.recruitment?.total_candidates ?? 0} candidates`}
              icon={Briefcase}
              color="purple"
            />
          </>
        )}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Headcount by Department */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Headcount by Department</CardTitle>
            <CardDescription>Employee distribution across departments</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={deptData || []} margin={{ top: 0, right: 0, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis
                  dataKey="department"
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{
                    background: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Payroll trend */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Monthly Payroll ({currentYear})</CardTitle>
            <CardDescription>Gross vs net salary comparison</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart
                data={payrollData || []}
                margin={{ top: 0, right: 0, left: -10, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis
                  dataKey="month"
                  tickFormatter={(m) =>
                    new Date(currentYear, m - 1).toLocaleString("en", { month: "short" })
                  }
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}K`}
                />
                <Tooltip
                  formatter={(v: number) => formatCurrency(v)}
                  contentStyle={{
                    background: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Legend />
                <Bar dataKey="gross" name="Gross" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="net" name="Net" fill="#10B981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Add Employee", icon: Users, href: "/employees/new", color: "bg-blue-600 hover:bg-blue-700" },
          { label: "Run Payroll", icon: DollarSign, href: "/payroll", color: "bg-green-600 hover:bg-green-700" },
          { label: "Leave Approvals", icon: CalendarDays, href: "/leave", color: "bg-yellow-600 hover:bg-yellow-700" },
          { label: "View Reports", icon: TrendingUp, href: "/reports", color: "bg-purple-600 hover:bg-purple-700" },
        ].map((action) => (
          <a
            key={action.label}
            href={action.href}
            className={`flex flex-col items-center gap-2 p-4 rounded-xl text-white text-sm font-medium transition-transform hover:scale-105 ${action.color}`}
          >
            <action.icon className="h-6 w-6" />
            {action.label}
          </a>
        ))}
      </div>
    </div>
  );
}
