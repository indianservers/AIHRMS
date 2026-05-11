import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Download, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { projectsAPI, reportsAPI, sprintsAPI } from "../services/api";
import type {
  PMSCumulativeFlowReport,
  PMSCycleTimeReport,
  PMSProject,
  PMSProjectHealthReport,
  PMSSprint,
  PMSTaskDistributionReport,
  PMSTeamPerformanceReport,
  PMSTimeInStatusReport,
  ProjectVelocity,
  SprintBurndown,
} from "../types";

const colors = ["#2563eb", "#f59e0b", "#7c3aed", "#16a34a", "#dc2626", "#0891b2", "#64748b"];
const tabs = ["Distribution", "Burndown", "Velocity", "Flow", "Cycle Time", "Time in Status", "Health", "Team"] as const;
type Tab = typeof tabs[number];

export default function ReportsPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [projects, setProjects] = useState<PMSProject[]>([]);
  const [sprints, setSprints] = useState<PMSSprint[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState(projectId || "");
  const [selectedSprintId, setSelectedSprintId] = useState("");
  const [assigneeId, setAssigneeId] = useState("");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [activeTab, setActiveTab] = useState<Tab>("Distribution");
  const [distribution, setDistribution] = useState<PMSTaskDistributionReport | null>(null);
  const [burndown, setBurndown] = useState<SprintBurndown | null>(null);
  const [velocity, setVelocity] = useState<ProjectVelocity | null>(null);
  const [flow, setFlow] = useState<PMSCumulativeFlowReport | null>(null);
  const [cycle, setCycle] = useState<PMSCycleTimeReport | null>(null);
  const [timeInStatus, setTimeInStatus] = useState<PMSTimeInStatusReport | null>(null);
  const [health, setHealth] = useState<PMSProjectHealthReport | null>(null);
  const [team, setTeam] = useState<PMSTeamPerformanceReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const filters = useMemo(() => ({
    projectId: selectedProjectId,
    sprintId: selectedSprintId,
    assigneeId,
    from,
    to,
  }), [assigneeId, from, selectedProjectId, selectedSprintId, to]);

  useEffect(() => {
    projectsAPI.list().then((items) => {
      setProjects(items);
      if (!selectedProjectId) setSelectedProjectId(String(items[0]?.id || ""));
    }).catch(() => setProjects([]));
  }, []);

  useEffect(() => {
    if (projectId) setSelectedProjectId(projectId);
  }, [projectId]);

  useEffect(() => {
    if (!selectedProjectId) {
      setSprints([]);
      return;
    }
    sprintsAPI.list(Number(selectedProjectId)).then((items) => {
      setSprints(items);
      const activeOrLatest = items.find((item) => item.status === "Active") || items[0];
      setSelectedSprintId(String(activeOrLatest?.id || ""));
    }).catch(() => setSprints([]));
  }, [selectedProjectId]);

  const loadReports = () => {
    setLoading(true);
    setError(null);
    Promise.all([
      reportsAPI.taskDistribution(filters),
      selectedSprintId ? reportsAPI.burndown(Number(selectedSprintId)).catch(() => null) : Promise.resolve(null),
      selectedProjectId ? reportsAPI.velocity(Number(selectedProjectId)).catch(() => null) : Promise.resolve(null),
      reportsAPI.cumulativeFlow(filters),
      reportsAPI.cycleTime(filters),
      reportsAPI.timeInStatus(filters),
      reportsAPI.projectHealth(filters),
      reportsAPI.teamPerformance(filters),
    ])
      .then(([distributionData, burndownData, velocityData, flowData, cycleData, timeData, healthData, teamData]) => {
        setDistribution(distributionData);
        setBurndown(burndownData);
        setVelocity(velocityData);
        setFlow(flowData);
        setCycle(cycleData);
        setTimeInStatus(timeData);
        setHealth(healthData);
        setTeam(teamData);
      })
      .catch((err) => setError(err?.response?.data?.detail || "Unable to load reports."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadReports();
  }, [filters]);

  const exportReport = async (format: "csv" | "pdf" | "xlsx") => {
    const report = activeTab.toLowerCase().replace(/\s+/g, "-");
    const blob = await reportsAPI.export({ ...filters, report: report === "distribution" ? "task-distribution" : report, format });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `pms-${report}.${format}`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const completedTasks = distribution?.by_status.find((item) => item.name === "Done")?.tasks || 0;
  const totalTasks = distribution?.total_tasks || 0;
  const avgVelocity = Math.round(velocity?.average_velocity_points || 0);
  const avgCycleDays = cycle ? Math.round((cycle.average_cycle_time_hours / 24) * 10) / 10 : 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <h1 className="page-title">PMS reports</h1>
          <p className="page-description">Real task, sprint, status-history, flow, cycle-time, health, and team analytics.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={loadReports} disabled={loading}><RefreshCw className="h-4 w-4" />Refresh</Button>
          <Button variant="outline" onClick={() => exportReport("csv")}><Download className="h-4 w-4" />CSV</Button>
          <Button variant="outline" onClick={() => exportReport("xlsx")}><Download className="h-4 w-4" />Excel</Button>
          <Button variant="outline" onClick={() => exportReport("pdf")}><Download className="h-4 w-4" />PDF</Button>
        </div>
      </div>

      <Card>
        <CardContent className="grid gap-3 p-4 md:grid-cols-2 xl:grid-cols-5">
          <Select label="Project" value={selectedProjectId} onChange={setSelectedProjectId}>
            <option value="">All accessible projects</option>
            {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
          </Select>
          <Select label="Sprint" value={selectedSprintId} onChange={setSelectedSprintId}>
            <option value="">Any sprint</option>
            {sprints.map((sprint) => <option key={sprint.id} value={sprint.id}>{sprint.name}</option>)}
          </Select>
          <Select label="Assignee" value={assigneeId} onChange={setAssigneeId}>
            <option value="">All assignees</option>
            {distribution?.by_assignee.filter((item) => item.assignee_id).map((item) => <option key={item.assignee_id} value={item.assignee_id}>{item.name}</option>)}
          </Select>
          <DateInput label="From" value={from} onChange={setFrom} />
          <DateInput label="To" value={to} onChange={setTo} />
        </CardContent>
      </Card>

      {error ? <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div> : null}

      <div className="grid gap-4 md:grid-cols-4">
        <ReportMetric label="Tasks" value={totalTasks} />
        <ReportMetric label="Done" value={completedTasks} />
        <ReportMetric label="Avg velocity" value={avgVelocity} suffix="pts" />
        <ReportMetric label="Avg cycle" value={avgCycleDays} suffix="days" />
      </div>

      <div className="flex gap-2 overflow-x-auto">
        {tabs.map((tab) => (
          <Button key={tab} variant={activeTab === tab ? "default" : "outline"} size="sm" onClick={() => setActiveTab(tab)}>
            {tab}
          </Button>
        ))}
      </div>

      {loading ? <div className="skeleton h-96 rounded-lg" /> : null}
      {!loading && activeTab === "Distribution" ? <DistributionCharts data={distribution} /> : null}
      {!loading && activeTab === "Burndown" ? <BurndownChart data={burndown} /> : null}
      {!loading && activeTab === "Velocity" ? <VelocityChart data={velocity} /> : null}
      {!loading && activeTab === "Flow" ? <FlowChart data={flow} /> : null}
      {!loading && activeTab === "Cycle Time" ? <CycleChart data={cycle} /> : null}
      {!loading && activeTab === "Time in Status" ? <TimeInStatusChart data={timeInStatus} /> : null}
      {!loading && activeTab === "Health" ? <HealthChart data={health} /> : null}
      {!loading && activeTab === "Team" ? <TeamPerformance data={team} /> : null}
    </div>
  );
}

function DistributionCharts({ data }: { data: PMSTaskDistributionReport | null }) {
  if (!data) return <Empty text="No task distribution data found." />;
  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <ChartCard title="Tasks by status">
        <BarChart data={data.by_status}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="tasks" fill="#2563eb" /><Bar dataKey="story_points" fill="#16a34a" /></BarChart>
      </ChartCard>
      <ChartCard title="Priority distribution">
        <PieChart><Pie data={data.by_priority} dataKey="tasks" nameKey="name" innerRadius={70} outerRadius={110}>{data.by_priority.map((_, index) => <Cell key={index} fill={colors[index % colors.length]} />)}</Pie><Tooltip /></PieChart>
      </ChartCard>
    </div>
  );
}

function BurndownChart({ data }: { data: SprintBurndown | null }) {
  if (!data?.points.length) return <Empty text="Start a sprint to capture burndown." />;
  return <ChartCard title="Sprint burndown"><LineChart data={data.points}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" /><YAxis allowDecimals={false} /><Tooltip /><Legend /><Line type="monotone" dataKey="ideal_remaining_points" stroke="#94a3b8" name="Ideal remaining" /><Line type="monotone" dataKey="actual_remaining_points" stroke="#2563eb" name="Actual remaining" /><Line type="monotone" dataKey="completed_points" stroke="#16a34a" name="Completed" /></LineChart></ChartCard>;
}

function VelocityChart({ data }: { data: ProjectVelocity | null }) {
  if (!data?.sprints.length) return <Empty text="Complete sprints to build velocity history." />;
  return <ChartCard title="Velocity tracking"><BarChart data={data.sprints}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="velocity_points" fill="#16a34a" /></BarChart></ChartCard>;
}

function FlowChart({ data }: { data: PMSCumulativeFlowReport | null }) {
  if (!data?.points.length) return <Empty text="No cumulative flow data for this range." />;
  return <ChartCard title="Cumulative flow diagram"><LineChart data={data.points}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" /><YAxis allowDecimals={false} /><Tooltip /><Legend />{data.statuses.map((status, index) => <Line key={status} type="monotone" dataKey={status} stroke={colors[index % colors.length]} dot={false} />)}</LineChart></ChartCard>;
}

function CycleChart({ data }: { data: PMSCycleTimeReport | null }) {
  if (!data?.items.length) return <Empty text="No completed tasks found for cycle-time analysis." />;
  return <ChartCard title="Cycle time / lead time"><BarChart data={data.items.slice(0, 25)}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="task_key" /><YAxis /><Tooltip /><Legend /><Bar dataKey="lead_time_hours" fill="#7c3aed" name="Lead hours" /><Bar dataKey="cycle_time_hours" fill="#2563eb" name="Cycle hours" /></BarChart></ChartCard>;
}

function TimeInStatusChart({ data }: { data: PMSTimeInStatusReport | null }) {
  if (!data?.statuses.length) return <Empty text="No status history found for this range." />;
  return <ChartCard title="Time in status"><BarChart data={data.statuses}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="status" /><YAxis /><Tooltip /><Bar dataKey="days" fill="#f59e0b" /></BarChart></ChartCard>;
}

function HealthChart({ data }: { data: PMSProjectHealthReport | null }) {
  if (!data?.points.length) return <Empty text="No project health data found." />;
  return <ChartCard title="Project health over time"><LineChart data={data.points}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" /><YAxis allowDecimals={false} /><Tooltip /><Legend />{["Good", "At Risk", "Blocked", "Completed"].map((status, index) => <Line key={status} type="monotone" dataKey={status} stroke={colors[index % colors.length]} />)}</LineChart></ChartCard>;
}

function TeamPerformance({ data }: { data: PMSTeamPerformanceReport | null }) {
  if (!data?.items.length) return <Empty text="No team performance data found." />;
  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_26rem]">
      <ChartCard title="Individual velocity"><BarChart data={data.items}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis allowDecimals={false} /><Tooltip /><Legend /><Bar dataKey="completed_points" fill="#16a34a" /><Bar dataKey="assigned_points" fill="#94a3b8" /></BarChart></ChartCard>
      <Card><CardHeader><CardTitle>Team table</CardTitle></CardHeader><CardContent className="space-y-3">{data.items.map((item) => <div key={item.name} className="rounded-md border p-3 text-sm"><div className="flex justify-between font-medium"><span>{item.name}</span><span>{item.completion_rate}%</span></div><p className="text-muted-foreground">{item.completed_tasks}/{item.assigned_tasks} tasks, {item.completed_points}/{item.assigned_points} pts</p></div>)}</CardContent></Card>
    </div>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactElement }) {
  return <Card><CardHeader><CardTitle>{title}</CardTitle></CardHeader><CardContent className="h-96"><ResponsiveContainer width="100%" height="100%">{children}</ResponsiveContainer></CardContent></Card>;
}

function ReportMetric({ label, value, suffix }: { label: string; value: number; suffix?: string }) {
  return <Card><CardContent className="p-5"><p className="text-sm text-muted-foreground">{label}</p><p className="mt-2 text-3xl font-semibold">{value}{suffix ? ` ${suffix}` : ""}</p></CardContent></Card>;
}

function Select({ label, value, onChange, children }: { label: string; value: string; onChange: (value: string) => void; children: React.ReactNode }) {
  return <label className="space-y-1 text-sm"><span className="font-medium text-muted-foreground">{label}</span><select value={value} onChange={(event) => onChange(event.target.value)} className="h-10 w-full rounded-md border bg-background px-3 text-sm">{children}</select></label>;
}

function DateInput({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return <label className="space-y-1 text-sm"><span className="font-medium text-muted-foreground">{label}</span><input type="date" value={value} onChange={(event) => onChange(event.target.value)} className="h-10 w-full rounded-md border bg-background px-3 text-sm" /></label>;
}

function Empty({ text }: { text: string }) {
  return <div className="rounded-lg border border-dashed p-10 text-center text-sm text-muted-foreground">{text}</div>;
}
