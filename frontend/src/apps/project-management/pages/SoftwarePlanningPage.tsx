import { useEffect, useMemo, useState } from "react";
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  closestCorners,
  useDroppable,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import { useSortable, SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Activity, Boxes, Bug, CheckCircle2, ClipboardList, Columns3, FileQuestion, Flag, GitBranch, GripVertical, ListChecks, Plus, Rocket, Search, ShieldAlert, Sparkles, Target, Timer, Workflow } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { formatDate, statusColor } from "@/lib/utils";
import {
  workAdvancedPlanning,
  workAutomationRules,
  workComponents,
  workForms,
  workGoals,
  WorkIssues,
  workNavigatorFilters,
  workReleases,
  workReports,
  workSecurityRows,
  workTemplates,
  workWorkflowSchemes,
  type WorkIssue,
} from "../workData";

const lanes = ["Backlog", "Selected", "In Progress", "In Review", "Done"] as const;

export default function SoftwarePlanningPage() {
  const [issues, setIssues] = useState<WorkIssue[]>(() => {
    const stored = localStorage.getItem("karyaflow-software-issues");
    return stored ? JSON.parse(stored) : WorkIssues;
  });
  const [activeId, setActiveId] = useState<number | null>(null);
  const [search, setSearch] = useState("");
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 8 } }));
  const activeIssue = issues.find((issue) => issue.id === activeId);
  const filtered = useMemo(
    () => issues.filter((issue) => [issue.key, issue.summary, issue.assignee, issue.epic, issue.release].join(" ").toLowerCase().includes(search.toLowerCase())),
    [issues, search],
  );
  const sprintPoints = issues.filter((issue) => issue.sprint === "Sprint 24").reduce((sum, issue) => sum + issue.storyPoints, 0);
  const completedPoints = issues.filter((issue) => issue.sprint === "Sprint 24" && issue.status === "Done").reduce((sum, issue) => sum + issue.storyPoints, 0);

  useEffect(() => {
    localStorage.setItem("karyaflow-software-issues", JSON.stringify(issues));
  }, [issues]);

  const onDragStart = (event: DragStartEvent) => setActiveId(event.active.id as number);
  const onDragEnd = (event: DragEndEvent) => {
    setActiveId(null);
    if (!event.over) return;
    const targetStatus = String(event.over.id).startsWith("lane-")
      ? String(event.over.id).replace("lane-", "")
      : issues.find((issue) => issue.id === event.over?.id)?.status;
    if (!targetStatus) return;
    setIssues((items) => items.map((issue) => (issue.id === event.active.id ? { ...issue, status: targetStatus as WorkIssue["status"] } : issue)));
  };

  const createIssue = () => {
    const nextId = Math.max(...issues.map((issue) => issue.id)) + 1;
    const nextIssue: WorkIssue = {
      id: nextId,
      key: `KAR-${100 + nextId}`,
      type: "Task",
      summary: "New actionable work item",
      status: "Backlog",
      priority: "Medium",
      assignee: "Unassigned",
      reporter: "Current User",
      storyPoints: 3,
      sprint: "Backlog",
      epic: "Planning",
      release: "v2.4",
      dueDate: "2026-06-15",
    };
    setIssues((items) => [nextIssue, ...items]);
    setSearch(nextIssue.key);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <h1 className="page-title">Software Delivery</h1>
          <p className="page-description">KaryaFlow planning for backlog, sprints, boards, releases, roadmaps, reports, automation, dependencies, and development workflows.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline"><GitBranch className="h-4 w-4" />Connect repo</Button>
          <Button variant="outline"><Workflow className="h-4 w-4" />Automation</Button>
          <Button onClick={createIssue}><Plus className="h-4 w-4" />Create issue</Button>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        <Metric icon={ListChecks} label="Sprint scope" value={`${sprintPoints} pts`} />
        <Metric icon={CheckCircle2} label="Completed" value={`${completedPoints} pts`} />
        <Metric icon={ShieldAlert} label="Critical bugs" value={issues.filter((issue) => issue.type === "Bug" && issue.priority === "Critical").length} />
        <Metric icon={Rocket} label="Releases" value={workReleases.length} />
        <Metric icon={Activity} label="Automation rules" value={workAutomationRules.length} />
      </div>

      <div className="grid gap-4 xl:grid-cols-4">
        <FeaturePanel title="Goals" icon={Target} rows={workGoals.map((item) => `${item.goal}: ${item.progress} (${item.status})`)} />
        <FeaturePanel title="Request Forms" icon={FileQuestion} rows={workForms.map((item) => `${item.form}: ${item.fields} fields -> ${item.routedTo}`)} />
        <FeaturePanel title="Project Templates" icon={ClipboardList} rows={workTemplates.map((item) => `${item.template}: ${item.includes}`)} />
        <FeaturePanel title="Issue Navigator" icon={Search} rows={workNavigatorFilters.map((item) => `${item.name}: ${item.count} results`)} />
      </div>

      <Card>
        <CardContent className="flex flex-col gap-3 p-3 lg:flex-row lg:items-center">
          <div className="flex min-w-0 flex-1 items-center gap-2 rounded-md border px-3 py-2">
            <Search className="h-4 w-4 text-muted-foreground" />
            <Input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search issues, epics, releases, assignees..." className="border-0 p-0 shadow-none focus-visible:ring-0" />
          </div>
          {["Backlog", "Active sprint", "My open issues", "Critical bugs", "Release v2.3"].map((view) => <Button key={view} variant="outline" size="sm">{view}</Button>)}
        </CardContent>
      </Card>

      <DndContext sensors={sensors} collisionDetection={closestCorners} onDragStart={onDragStart} onDragEnd={onDragEnd}>
        <div className="flex gap-4 overflow-x-auto pb-3">
          {lanes.map((lane) => <IssueLane key={lane} lane={lane} issues={filtered.filter((issue) => issue.status === lane)} />)}
        </div>
        <DragOverlay>{activeIssue ? <IssueCard issue={activeIssue} overlay /> : null}</DragOverlay>
      </DndContext>

      <div className="grid gap-4 xl:grid-cols-[1fr_1fr]">
        <Card>
          <CardHeader><CardTitle>Backlog and Sprint Planning</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {issues.filter((issue) => ["Backlog", "Selected"].includes(issue.status)).map((issue) => (
              <div key={issue.id} className="grid gap-2 rounded-lg border p-3 md:grid-cols-[7rem_1fr_8rem_6rem] md:items-center">
                <Badge variant="outline">{issue.key}</Badge>
                <div><p className="font-medium">{issue.summary}</p><p className="text-sm text-muted-foreground">{issue.epic} / {issue.assignee}</p></div>
                <Badge className={statusColor(issue.priority)}>{issue.priority}</Badge>
                <span className="text-sm font-semibold">{issue.storyPoints} pts</span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Roadmap and Releases</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {workReleases.map((release) => (
              <div key={release.name} className="rounded-lg border p-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2"><Flag className="h-4 w-4 text-primary" /><p className="font-semibold">{release.name}</p></div>
                  <Badge className={statusColor(release.status)}>{release.status}</Badge>
                </div>
                <div className="mt-3 grid grid-cols-3 gap-2 text-sm">
                  <span className="text-muted-foreground">Release {formatDate(release.date)}</span>
                  <span>{release.issues} issues</span>
                  <span className="text-right">{release.risk}</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <FeaturePanel title="Reports" icon={Timer} rows={workReports.map((item) => `${item.name}: ${item.metric} (${item.status})`)} />
        <FeaturePanel title="Automation" icon={Sparkles} rows={workAutomationRules.map((item) => `${item.rule} -> ${item.action}`)} />
        <FeaturePanel title="DevOps and Integrations" icon={Boxes} rows={["Repository links and pull requests", "Deployment status per issue", "Incident and release change log", "App marketplace placeholders", "Webhooks and API tokens"]} />
      </div>

      <div className="grid gap-4 xl:grid-cols-4">
        <FeaturePanel title="Components" icon={Columns3} rows={workComponents.map((item) => `${item.component}: ${item.openIssues} open / lead ${item.lead}`)} />
        <FeaturePanel title="Work Types and Workflows" icon={Workflow} rows={workWorkflowSchemes.map((item) => `${item.workType}: ${item.workflow}`)} />
        <FeaturePanel title="Security and Notifications" icon={ShieldAlert} rows={workSecurityRows.map((item) => `${item.scheme}: ${item.scope}`)} />
        <FeaturePanel title="Advanced Planning" icon={GitBranch} rows={workAdvancedPlanning.map((item) => `${item.plan}: ${item.signal}`)} />
      </div>
    </div>
  );
}

function IssueLane({ lane, issues }: { lane: WorkIssue["status"]; issues: WorkIssue[] }) {
  const { setNodeRef, isOver } = useDroppable({ id: `lane-${lane}` });
  const points = issues.reduce((sum, issue) => sum + issue.storyPoints, 0);
  return (
    <section ref={setNodeRef} className={`flex h-[32rem] w-80 shrink-0 flex-col rounded-lg border bg-muted/30 ${isOver ? "ring-2 ring-primary/40" : ""}`}>
      <header className="border-b bg-background p-3">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">{lane}</h2>
          <Badge variant="outline">{issues.length} / {points} pts</Badge>
        </div>
      </header>
      <SortableContext items={issues.map((issue) => issue.id)} strategy={verticalListSortingStrategy}>
        <div className="flex-1 space-y-3 overflow-y-auto p-3">
          {issues.map((issue) => <IssueCard key={issue.id} issue={issue} />)}
          {!issues.length ? <div className="flex h-24 items-center justify-center rounded-lg border border-dashed bg-background/60 text-sm text-muted-foreground">Drop issue here</div> : null}
        </div>
      </SortableContext>
    </section>
  );
}

function IssueCard({ issue, overlay = false }: { issue: WorkIssue; overlay?: boolean }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: issue.id });
  return (
    <article ref={setNodeRef} style={{ transform: CSS.Transform.toString(transform), transition }} className={`rounded-lg border bg-card p-3 shadow-sm ${isDragging ? "opacity-50" : ""} ${overlay ? "w-72 shadow-xl" : ""}`}>
      <div className="flex gap-2">
        <button type="button" className="rounded p-1 text-muted-foreground hover:bg-muted" {...attributes} {...listeners} aria-label="Drag issue"><GripVertical className="h-4 w-4" /></button>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            {issue.type === "Bug" ? <Bug className="h-4 w-4 text-red-600" /> : <ListChecks className="h-4 w-4 text-blue-600" />}
            <span className="text-xs font-semibold text-muted-foreground">{issue.key}</span>
          </div>
          <h3 className="mt-1 line-clamp-2 text-sm font-semibold">{issue.summary}</h3>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
        <Badge className={statusColor(issue.priority)}>{issue.priority}</Badge>
        <Badge variant="outline">{issue.type}</Badge>
        <Badge variant="outline">{issue.storyPoints} pts</Badge>
      </div>
      <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
        <span>{issue.assignee}</span>
        <span>{issue.release}</span>
      </div>
    </article>
  );
}

function Metric({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string | number }) {
  return <Card><CardContent className="flex items-center gap-3 p-4"><div className="rounded-lg bg-blue-100 p-2 text-blue-700"><Icon className="h-5 w-5" /></div><div><p className="text-sm text-muted-foreground">{label}</p><p className="text-xl font-semibold">{value}</p></div></CardContent></Card>;
}

function FeaturePanel({ title, icon: Icon, rows }: { title: string; icon: React.ElementType; rows: string[] }) {
  return (
    <Card>
      <CardHeader><CardTitle className="flex items-center gap-2 text-base"><Icon className="h-5 w-5 text-primary" />{title}</CardTitle></CardHeader>
      <CardContent className="space-y-3">
        {rows.map((row) => <div key={row} className="rounded-md border bg-muted/30 px-3 py-2 text-sm">{row}</div>)}
      </CardContent>
    </Card>
  );
}

