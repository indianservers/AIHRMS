import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { BarChart3, Briefcase, CalendarDays, Download, RefreshCw, TrendingDown, Users } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { reportsApi } from "@/services/api";
import { formatCurrency } from "@/lib/utils";

const COLORS = ["#2563eb", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#0891b2"];
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export default function ReportsPage() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const fromDate = `${year}-01-01`;
  const toDate = `${year}-12-31`;

  const dashboard = useQuery({ queryKey: ["reports-dashboard"], queryFn: () => reportsApi.dashboard().then((r) => r.data) });
  const headcount = useQuery({ queryKey: ["headcount-by-dept"], queryFn: () => reportsApi.headcountByDept().then((r) => r.data) });
  const payroll = useQuery({ queryKey: ["payroll-summary", year], queryFn: () => reportsApi.payrollSummary(year).then((r) => r.data) });
  const leave = useQuery({ queryKey: ["leave-trend", year], queryFn: () => reportsApi.leaveTrend(year).then((r) => r.data) });
  const attendance = useQuery({ queryKey: ["attendance-trend", month, year], queryFn: () => reportsApi.attendanceTrend(month, year).then((r) => r.data) });
  const turnover = useQuery({ queryKey: ["turnover", year], queryFn: () => reportsApi.turnover(fromDate, toDate).then((r) => r.data) });
  const funnel = useQuery({ queryKey: ["recruitment-funnel"], queryFn: () => reportsApi.recruitmentFunnel().then((r) => r.data) });

  const leaveByMonth = useMemo(() => {
    const rows = Array.from({ length: 12 }, (_, i) => ({ month: MONTHS[i], Approved: 0, Pending: 0, Rejected: 0 }));
    (leave.data || []).forEach((item: any) => {
      const row = rows[(Number(item.month) || 1) - 1];
      row[item.status as "Approved"] = (row[item.status as "Approved"] || 0) + Number(item.count || 0);
    });
    return rows;
  }, [leave.data]);

  const attendanceByDate = useMemo(() => {
    const grouped: Record<string, any> = {};
    (attendance.data || []).forEach((item: any) => {
      grouped[item.date] = grouped[item.date] || { date: item.date.slice(5) };
      grouped[item.date][item.status] = Number(item.count || 0);
    });
    return Object.values(grouped);
  }, [attendance.data]);

  const isLoading = dashboard.isLoading || headcount.isLoading;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h1 className="page-title">Reports & Analytics</h1>
          <p className="page-description">Live HR insights for headcount, attendance, leave, payroll, recruitment, and turnover.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <select value={month} onChange={(e) => setMonth(Number(e.target.value))} className="h-9 rounded-md border bg-background px-3 text-sm">
            {MONTHS.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
          </select>
          <input type="number" value={year} onChange={(e) => setYear(Number(e.target.value))} className="h-9 w-24 rounded-md border bg-background px-3 text-sm" />
          <Button variant="outline" size="sm" onClick={() => { dashboard.refetch(); headcount.refetch(); payroll.refetch(); leave.refetch(); attendance.refetch(); turnover.refetch(); funnel.refetch(); }}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Metric title="Active Employees" value={dashboard.data?.headcount?.active || 0} hint={`${dashboard.data?.headcount?.total || 0} total`} icon={Users} />
        <Metric title="Present Today" value={dashboard.data?.attendance?.present_today || 0} hint={`${dashboard.data?.attendance?.absent_today || 0} absent`} icon={BarChart3} />
        <Metric title="Pending Leaves" value={dashboard.data?.leaves?.pending_approvals || 0} hint="Awaiting approval" icon={CalendarDays} />
        <Metric title="Turnover Rate" value={`${turnover.data?.turnover_rate || 0}%`} hint={`${turnover.data?.resigned || 0} exits in ${year}`} icon={TrendingDown} />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <ChartCard title="Headcount by Department" description="Distribution of employees across departments">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={headcount.data || []}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="department" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title={`Payroll Summary ${year}`} description="Monthly gross, deductions, and net payroll">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={payroll.data || []}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="month" tickFormatter={(m) => MONTHS[Number(m) - 1]} tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={(v) => `₹${Math.round(Number(v) / 1000)}k`} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v: number) => formatCurrency(v)} />
              <Bar dataKey="gross" fill="#2563eb" radius={[4, 4, 0, 0]} />
              <Bar dataKey="net" fill="#16a34a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title={`Attendance Trend ${MONTHS[month - 1]} ${year}`} description="Daily attendance statuses by date">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={attendanceByDate}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="Present" stroke="#16a34a" strokeWidth={2} />
              <Line type="monotone" dataKey="Absent" stroke="#dc2626" strokeWidth={2} />
              <Line type="monotone" dataKey="Half-day" stroke="#f59e0b" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title={`Leave Trend ${year}`} description="Monthly leave requests by status">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={leaveByMonth}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="Approved" fill="#16a34a" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Pending" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Rejected" fill="#dc2626" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <ChartCard title="Recruitment Funnel" description="Candidate status split across all jobs">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={funnel.data || []} dataKey="count" nameKey="status" outerRadius={95} label>
                {(funnel.data || []).map((_: any, index: number) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Executive Snapshot</CardTitle>
            <CardDescription>Key ratios for the selected year</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-2">
            <Snapshot label="Joined" value={turnover.data?.joined || 0} />
            <Snapshot label="Exited" value={turnover.data?.resigned || 0} />
            <Snapshot label="Open Positions" value={dashboard.data?.recruitment?.open_positions || 0} />
            <Snapshot label="Candidates" value={dashboard.data?.recruitment?.total_candidates || 0} />
          </CardContent>
        </Card>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading live reports...</p>}
    </div>
  );
}

function Metric({ title, value, hint, icon: Icon }: { title: string; value: string | number; hint: string; icon: any }) {
  return (
    <Card>
      <CardContent className="flex items-start justify-between p-5">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="mt-2 text-2xl font-semibold">{value}</p>
          <p className="mt-1 text-xs text-muted-foreground">{hint}</p>
        </div>
        <div className="rounded-md bg-primary/10 p-2 text-primary">
          <Icon className="h-5 w-5" />
        </div>
      </CardContent>
    </Card>
  );
}

function ChartCard({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

function Snapshot({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-2 text-xl font-semibold">{value}</p>
    </div>
  );
}
