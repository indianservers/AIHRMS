import type React from "react";
import { FormEvent, useEffect, useState } from "react";
import { Activity, AlertTriangle, BarChart3, CheckCircle2, Flame, Gauge, Play, RotateCcw, TrendingUp } from "lucide-react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { formatDate, statusColor } from "@/lib/utils";
import { projectsAPI, reportsAPI, sprintsAPI } from "../services/api";
import type { PMSProject, PMSSprint, ProjectVelocity, SprintBurndown, WorkloadResponse } from "../types";

export default function SprintsPage() {
  const [projects, setProjects] = useState<PMSProject[]>([]);
  const [projectId, setProjectId] = useState("");
  const [sprints, setSprints] = useState<PMSSprint[]>([]);
  const [name, setName] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [goal, setGoal] = useState("Planned delivery increment");
  const [capacityHours, setCapacityHours] = useState("40");
  const [burndown, setBurndown] = useState<SprintBurndown | null>(null);
  const [velocity, setVelocity] = useState<ProjectVelocity | null>(null);
  const [workload, setWorkload] = useState<WorkloadResponse | null>(null);

  useEffect(() => {
    projectsAPI.list().then((items) => {
      setProjects(items);
      const firstId = String(items[0]?.id || "");
      setProjectId(firstId);
      if (firstId) loadProject(Number(firstId));
    });
  }, []);

  const loadProject = async (id: number) => {
    const [sprintItems, velocityData, workloadData] = await Promise.all([
      sprintsAPI.list(id),
      sprintsAPI.velocity(id).catch(() => null),
      reportsAPI.workload(id, { group_by: "sprint" }).catch(() => null),
    ]);
    setSprints(sprintItems);
    setVelocity(velocityData);
    setWorkload(workloadData);
    if (sprintItems[0]) {
      sprintsAPI.burndown(sprintItems[0].id).then(setBurndown).catch(() => setBurndown(null));
    } else {
      setBurndown(null);
    }
  };

  const switchProject = (value: string) => {
    setProjectId(value);
    if (value) loadProject(Number(value));
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!projectId || !name || !startDate || !endDate) return;
    const sprint = await sprintsAPI.create(Number(projectId), {
      name,
      goal,
      status: "Planned",
      start_date: startDate,
      end_date: endDate,
      capacity_hours: Number(capacityHours || 0),
    } as any);
    setSprints((items) => [sprint, ...items]);
    setName("");
  };

  const refreshSprint = (updated: PMSSprint) => {
    setSprints((items) => items.map((item) => item.id === updated.id ? updated : item));
    sprintsAPI.burndown(updated.id).then(setBurndown).catch(() => setBurndown(null));
    if (projectId) sprintsAPI.velocity(Number(projectId)).then(setVelocity).catch(() => null);
  };

  const startSprint = async (sprint: PMSSprint) => {
    refreshSprint(await sprintsAPI.start(sprint.id));
  };

  const completeSprint = async (sprint: PMSSprint) => {
    const carryForward = sprints.find((item) => item.id !== sprint.id && item.status === "Planned")?.id;
    refreshSprint(await sprintsAPI.complete(sprint.id, carryForward));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Sprints</h1>
        <p className="page-description">Plan agile delivery windows, commitment snapshots, carry-forward scope, capacity, burndown, and velocity.</p>
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <Metric icon={Activity} label="Sprints" value={sprints.length} />
        <Metric icon={Play} label="Active" value={sprints.filter((sprint) => sprint.status === "Active").length} />
        <Metric icon={TrendingUp} label="Avg velocity" value={`${Math.round(velocity?.average_velocity_points || 0)} pts`} />
        <Metric icon={AlertTriangle} label="Over capacity" value={workload?.items.filter((item) => (item.load_percent || 0) > 100).length || 0} tone="text-red-600" />
      </div>
      <Card>
        <CardHeader><CardTitle>Create sprint</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={submit} className="grid gap-4 md:grid-cols-[1fr_1fr_1fr_8rem_11rem_11rem_auto] md:items-end">
            <Field label="Project"><select value={projectId} onChange={(event) => switchProject(event.target.value)} className="h-10 w-full rounded-md border bg-background px-3 text-sm">{projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}</select></Field>
            <Field label="Sprint name"><Input value={name} onChange={(event) => setName(event.target.value)} /></Field>
            <Field label="Goal"><Input value={goal} onChange={(event) => setGoal(event.target.value)} /></Field>
            <Field label="Capacity"><Input type="number" value={capacityHours} onChange={(event) => setCapacityHours(event.target.value)} /></Field>
            <Field label="Start"><Input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} /></Field>
            <Field label="End"><Input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} /></Field>
            <Button type="submit">Create</Button>
          </form>
        </CardContent>
      </Card>
      <div className="grid gap-4 xl:grid-cols-[1.4fr_0.8fr]">
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><BarChart3 className="h-5 w-5" />Burndown</CardTitle></CardHeader>
          <CardContent className="h-72">
            {burndown?.points.length ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={burndown.points}>
                  <XAxis dataKey="date" tickLine={false} axisLine={false} />
                  <YAxis allowDecimals={false} tickLine={false} axisLine={false} />
                  <Tooltip />
                  <Line type="monotone" dataKey="ideal_remaining_points" stroke="#64748b" strokeDasharray="4 4" dot={false} />
                  <Line type="monotone" dataKey="actual_remaining_points" stroke="hsl(var(--primary))" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            ) : <EmptyState text="Start a sprint to capture burndown." />}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle className="flex items-center gap-2"><Gauge className="h-5 w-5" />Capacity</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {(workload?.items || []).slice(0, 5).map((item) => (
              <div key={`${item.sprint_id || "none"}`} className="rounded-md border p-3">
                <div className="flex items-center justify-between gap-3 text-sm">
                  <span className="font-medium">Sprint {item.sprint_id || "Unassigned"}</span>
                  <Badge variant={(item.load_percent || 0) > 100 ? "destructive" : "outline"}>{Math.round(item.load_percent || 0)}%</Badge>
                </div>
                <div className="mt-2 h-2 rounded-full bg-muted"><div className="h-2 rounded-full bg-primary" style={{ width: `${Math.min(item.load_percent || 0, 100)}%` }} /></div>
                <p className="mt-2 text-xs text-muted-foreground">{item.task_count} tasks / {item.story_points} pts / {item.estimated_hours}h</p>
              </div>
            ))}
            {!workload?.items.length ? <EmptyState text="No open sprint workload yet." /> : null}
          </CardContent>
        </Card>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {sprints.map((sprint) => (
          <Card key={sprint.id}>
            <CardContent className="p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3"><div className="rounded-lg bg-primary/10 p-2 text-primary"><Activity className="h-5 w-5" /></div><div><h2 className="font-semibold">{sprint.name}</h2><p className="text-sm text-muted-foreground">{formatDate(sprint.start_date)} - {formatDate(sprint.end_date)}</p></div></div>
                <Badge className={statusColor(sprint.status)}>{sprint.status}</Badge>
              </div>
              <p className="mt-4 text-sm text-muted-foreground">{sprint.goal || "No sprint goal defined."}</p>
              <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                <Fact icon={Flame} label="Committed" value={`${sprint.committed_story_points || 0} pts`} />
                <Fact icon={CheckCircle2} label="Completed" value={`${sprint.completed_story_points || 0} pts`} />
                <Fact icon={RotateCcw} label="Carry-over" value={sprint.carry_forward_task_count || 0} />
                <Fact icon={AlertTriangle} label="Scope changes" value={sprint.scope_change_count || 0} />
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                <Button size="sm" onClick={() => startSprint(sprint)} disabled={sprint.status === "Active" || sprint.status === "Completed"}><Play className="h-4 w-4" />Start</Button>
                <Button size="sm" variant="outline" onClick={() => completeSprint(sprint)} disabled={sprint.status === "Completed"}><CheckCircle2 className="h-4 w-4" />Complete</Button>
                <Button size="sm" variant="ghost" onClick={() => sprintsAPI.burndown(sprint.id).then(setBurndown)}><BarChart3 className="h-4 w-4" />Burndown</Button>
              </div>
            </CardContent>
          </Card>
        ))}
        {!sprints.length ? <div className="rounded-lg border border-dashed p-6 text-sm text-muted-foreground">Create your first sprint to unlock lifecycle controls.</div> : null}
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="space-y-2"><Label>{label}</Label>{children}</div>;
}

function Metric({ icon: Icon, label, value, tone }: { icon: typeof Activity; label: string; value: string | number; tone?: string }) {
  return <Card><CardContent className="flex items-center gap-3 p-4"><div className="rounded-lg bg-primary/10 p-2 text-primary"><Icon className="h-5 w-5" /></div><div><p className="text-sm text-muted-foreground">{label}</p><p className={`text-xl font-semibold ${tone || ""}`}>{value}</p></div></CardContent></Card>;
}

function Fact({ icon: Icon, label, value }: { icon: typeof Activity; label: string; value: string | number }) {
  return <div className="rounded-md bg-muted/50 p-2"><div className="flex items-center gap-1 text-xs text-muted-foreground"><Icon className="h-3.5 w-3.5" />{label}</div><p className="mt-1 font-semibold">{value}</p></div>;
}

function EmptyState({ text }: { text: string }) {
  return <div className="flex h-full min-h-32 items-center justify-center rounded-lg border border-dashed text-sm text-muted-foreground">{text}</div>;
}

