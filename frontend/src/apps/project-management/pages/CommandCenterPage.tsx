import { useMemo, useState } from "react";
import {
  AppWindow,
  BarChart3,
  Bot,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  CircleDot,
  Code2,
  FileText,
  Filter,
  Flag,
  GitBranch,
  Globe2,
  Layers3,
  Link2,
  List,
  LockKeyhole,
  MoreHorizontal,
  Network,
  PanelTop,
  Rocket,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  Target,
  Users,
  Workflow,
  X,
  Zap,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  automationTemplates,
  dependencyLinks,
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
  teamMembers,
  timelineItems,
} from "../workData";

const projectTabs = [
  { label: "Summary", icon: PanelTop },
  { label: "Board", icon: Layers3 },
  { label: "Timeline", icon: GitBranch },
  { label: "List", icon: List },
  { label: "Calendar", icon: CalendarDays },
  { label: "Teams", icon: Users },
  { label: "Releases", icon: Rocket },
  { label: "Dependencies", icon: Network },
  { label: "Goals", icon: Target },
  { label: "Reports", icon: BarChart3 },
  { label: "Automation", icon: Workflow },
  { label: "Forms", icon: FileText },
  { label: "Apps", icon: AppWindow },
];

const karyaflowFeatures = [
  { name: "Scrum and Kanban boards", icon: Layers3, status: "Live", detail: "Drag issues by status, priority, epic, assignee, and sprint." },
  { name: "Backlog and sprint planning", icon: List, status: "Live", detail: "Rank work, estimate story points, split scope, and start or complete sprints." },
  { name: "Timeline and roadmap", icon: GitBranch, status: "Live", detail: "Plan dates, milestones, blockers, releases, and cross-project work." },
  { name: "Goals and outcomes", icon: Target, status: "Added", detail: "Track on-track, at-risk, and off-track objectives with contributing work." },
  { name: "Issue navigator", icon: Search, status: "Live", detail: "Saved filters, advanced query query rows, quick counts, and drill-down views." },
  { name: "Releases and versions", icon: Rocket, status: "Live", detail: "Release health, dates, scope, risk, notes, and deployment readiness." },
  { name: "Dependencies", icon: Network, status: "Live", detail: "Visual blocker links, dependency cards, and critical path warnings." },
  { name: "Reports and dashboards", icon: BarChart3, status: "Live", detail: "Burndown, velocity, cumulative flow, cycle time, and deployment frequency." },
  { name: "Automation rules", icon: Workflow, status: "Live", detail: "No-code triggers, actions, audit log, templates, and AI rule drafting." },
  { name: "Forms and intake", icon: FileText, status: "Live", detail: "Bug, feature, access, approval, support, and client-visible intake forms." },
  { name: "Components", icon: Code2, status: "Live", detail: "Component leads, default assignees, ownership, and open issue counts." },
  { name: "Workflows", icon: GitBranch, status: "Live", detail: "Per-work-type transitions, required fields, approvals, and status schemes." },
  { name: "Permissions and issue security", icon: ShieldCheck, status: "Live", detail: "Project roles, issue security, notifications, and permission schemes." },
  { name: "Teams and capacity", icon: Users, status: "Live", detail: "Capacity, load, ownership, watchers, reviewers, and team planning." },
  { name: "Apps and integrations", icon: AppWindow, status: "Ready", detail: "GitHub, Figma, Slack, Confluence, webhooks, marketplace placeholders." },
  { name: "AI planning assistant", icon: Bot, status: "Added", detail: "Suggest work, assign owners, identify blockers, and draft automations." },
];

const goals = [
  { name: "Increase new website traffic by 5X", status: "On track", work: 3 },
  { name: "Improve customer satisfaction by 7%", status: "On track", work: 3 },
  { name: "Increase global market share 10X", status: "At risk", work: 4 },
  { name: "Deliver product growth in APAC", status: "Off track", work: 2 },
  { name: "Deliver product growth in South America", status: "Off track", work: 3 },
];

export default function CommandCenterPage() {
  const [activeTab, setActiveTab] = useState("Summary");
  const [showGoals, setShowGoals] = useState(true);
  const [query, setQuery] = useState("");
  const filteredFeatures = useMemo(() => {
    const value = query.trim().toLowerCase();
    if (!value) return karyaflowFeatures;
    return karyaflowFeatures.filter((feature) => `${feature.name} ${feature.detail} ${feature.status}`.toLowerCase().includes(value));
  }, [query]);

  return (
    <div className="min-h-screen bg-[#f4f6fb]">
      <div className="border-b bg-white px-5 py-4">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="flex h-9 w-9 items-center justify-center rounded-md bg-blue-50 text-blue-700"><Globe2 className="h-5 w-5" /></span>
              <h1 className="text-2xl font-semibold tracking-tight text-slate-950">Travel Company</h1>
              <span className="text-amber-500">★</span>
              <Badge variant="outline">KaryaFlow PMS</Badge>
            </div>
            <div className="mt-3 flex gap-5 overflow-x-auto text-sm font-medium text-slate-600">
              {projectTabs.map((tab) => (
                <button
                  key={tab.label}
                  type="button"
                  onClick={() => {
                    setActiveTab(tab.label);
                    if (tab.label === "Goals") setShowGoals(true);
                  }}
                  className={`inline-flex shrink-0 items-center gap-1.5 border-b-2 pb-3 ${activeTab === tab.label ? "border-blue-600 text-blue-700" : "border-transparent hover:text-slate-950"}`}
                >
                  <tab.icon className="h-4 w-4" />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button variant="outline" size="sm"><Sparkles className="h-4 w-4" />AI plan</Button>
            <Button size="sm"><Zap className="h-4 w-4" />Create work</Button>
            <Button variant="ghost" size="icon" className="h-9 w-9"><MoreHorizontal className="h-4 w-4" /></Button>
          </div>
        </div>
      </div>

      <div className="space-y-5 p-5">
        <section className="grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
          <Card>
            <CardContent className="p-5">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <div className="flex items-center gap-2 text-sm font-medium text-slate-600">
                    <CalendarDays className="h-4 w-4" />
                    1 Feb - 12 Mar 2025
                  </div>
                  <h2 className="mt-6 text-xl font-semibold">Status overview</h2>
                  <p className="mt-2 max-w-xl text-sm leading-6 text-muted-foreground">
                    View project progress, status, dependencies, goals, releases, and sprint health from one KaryaFlow command surface.
                  </p>
                </div>
                <Button variant="outline" size="sm" onClick={() => setShowGoals(true)}><Target className="h-4 w-4" />Open goals</Button>
              </div>
              <div className="mt-6 grid gap-5 lg:grid-cols-[15rem_1fr]">
                <div className="relative mx-auto h-52 w-52 rounded-full bg-[conic-gradient(#2f855a_0_33%,#1d4ed8_33%_58%,#7c3aed_58%_74%,#a16207_74%_88%,#cbd5e1_88%_100%)]">
                  <div className="absolute inset-12 flex flex-col items-center justify-center rounded-full bg-white">
                    <span className="text-4xl font-semibold text-emerald-700">33%</span>
                    <span className="text-sm font-medium text-slate-500">Done</span>
                  </div>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <Metric label="Open issues" value={WorkIssues.filter((issue) => issue.status !== "Done").length.toString()} />
                  <Metric label="Sprint velocity" value="31 pts" />
                  <Metric label="Releases" value={workReleases.length.toString()} />
                  <Metric label="Blocked links" value={dependencyLinks.length.toString()} danger />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold">AI work planner</h2>
                  <p className="mt-1 text-sm text-muted-foreground">Break ideas into tasks, owners, estimates, and dependency-safe sequences.</p>
                </div>
                <Bot className="h-8 w-8 text-blue-600" />
              </div>
              <div className="mt-5 rounded-lg border bg-blue-50 p-4">
                <p className="text-sm font-medium text-blue-950">Suggested work items</p>
                <div className="mt-3 space-y-2">
                  {WorkIssues.slice(0, 4).map((issue) => (
                    <div key={issue.key} className="flex items-center justify-between rounded-md bg-white px-3 py-2 text-sm shadow-sm">
                      <span className="font-medium">{issue.key} {issue.summary}</span>
                      <Badge variant="outline">{issue.storyPoints} pts</Badge>
                    </div>
                  ))}
                </div>
                <Button className="mt-4 w-full">Create all suggested work</Button>
              </div>
            </CardContent>
          </Card>
        </section>

        <section className="grid gap-4 xl:grid-cols-[1fr_22rem]">
          <Card>
            <CardContent className="p-5">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <h2 className="text-lg font-semibold">KaryaFlow feature coverage in PMS</h2>
                  <p className="mt-1 text-sm text-muted-foreground">All major project delivery modules are exposed as PMS components, routes, and work surfaces.</p>
                </div>
                <div className="flex gap-2">
                  <div className="relative w-full sm:w-72">
                    <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search features" className="pl-9" />
                  </div>
                  <Button variant="outline" size="icon"><Filter className="h-4 w-4" /></Button>
                </div>
              </div>
              <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {filteredFeatures.map((feature) => (
                  <div key={feature.name} className="rounded-lg border bg-white p-4 shadow-sm">
                    <div className="flex items-start justify-between gap-3">
                      <span className="flex h-10 w-10 items-center justify-center rounded-md bg-slate-100 text-blue-700"><feature.icon className="h-5 w-5" /></span>
                      <Badge className={feature.status === "Live" ? "bg-emerald-100 text-emerald-800 hover:bg-emerald-100" : "bg-blue-100 text-blue-800 hover:bg-blue-100"}>{feature.status}</Badge>
                    </div>
                    <h3 className="mt-4 font-semibold">{feature.name}</h3>
                    <p className="mt-2 text-sm leading-6 text-muted-foreground">{feature.detail}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <div className="space-y-4">
            <SidePanel title="Releases" icon={Rocket} rows={workReleases.map((item) => `${item.name} - ${item.status}`)} />
            <SidePanel title="Reports" icon={BarChart3} rows={workReports.map((item) => `${item.name}: ${item.metric}`)} />
          </div>
        </section>

        <section className="grid gap-4 xl:grid-cols-3">
          <TableCard title="Teams and Capacity" icon={Users} rows={teamMembers.map((member) => [member.name, member.role, `${member.capacity}h`])} />
          <TableCard title="Components" icon={Code2} rows={workComponents.map((item) => [item.component, item.lead, `${item.openIssues} open`])} />
          <TableCard title="Workflows" icon={Workflow} rows={workWorkflowSchemes.map((item) => [item.workType, item.workflow, item.status])} />
          <TableCard title="Forms" icon={FileText} rows={workForms.map((item) => [item.form, `${item.fields} fields`, item.status])} />
          <TableCard title="Templates" icon={Flag} rows={workTemplates.map((item) => [item.template, item.includes, item.status])} />
          <TableCard title="Security" icon={LockKeyhole} rows={workSecurityRows.map((item) => [item.scheme, item.scope, item.status])} />
          <TableCard title="Plans" icon={Network} rows={workAdvancedPlanning.map((item) => [item.plan, item.signal, item.action])} />
          <TableCard title="Saved Filters" icon={Search} rows={workNavigatorFilters.map((item) => [item.name, item.query, `${item.count}`])} />
          <TableCard title="Automation" icon={Workflow} rows={[...workAutomationRules.map((item) => [item.rule, item.trigger, item.status]), ...automationTemplates.slice(0, 2).map((item) => [item.title, item.category, "Template"])]} />
        </section>
      </div>

      {showGoals ? <GoalsModal onClose={() => setShowGoals(false)} /> : null}
    </div>
  );
}

function GoalsModal({ onClose }: { onClose: () => void }) {
  const counts = {
    onTrack: goals.filter((goal) => goal.status === "On track").length,
    atRisk: goals.filter((goal) => goal.status === "At risk").length,
    offTrack: goals.filter((goal) => goal.status === "Off track").length,
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-blue-950/40 p-4">
      <div className="w-full max-w-3xl rounded-2xl bg-white p-6 shadow-2xl">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold text-slate-950">Goals</h2>
          <Button variant="ghost" size="icon" onClick={onClose}><X className="h-4 w-4" /></Button>
        </div>
        <div className="mt-7 grid h-16 grid-cols-[2fr_1fr_1fr] gap-1.5">
          <div className="rounded-md bg-emerald-400" />
          <div className="rounded-md bg-amber-400" />
          <div className="rounded-md bg-orange-500" />
        </div>
        <div className="mt-4 flex flex-wrap gap-7 text-sm text-slate-700">
          <Legend count={counts.onTrack} label="On track" tone="bg-emerald-100 text-emerald-700" />
          <Legend count={counts.atRisk} label="At risk" tone="bg-amber-100 text-amber-700" />
          <Legend count={counts.offTrack} label="Off track" tone="bg-red-100 text-red-700" />
        </div>
        <div className="mt-8 grid grid-cols-[1fr_11rem] gap-4 text-sm font-semibold text-muted-foreground">
          <span>Goal</span>
          <span className="text-right">Contributing work</span>
        </div>
        <div className="mt-3 space-y-4">
          {goals.map((goal) => (
            <div key={goal.name} className="grid grid-cols-[1fr_11rem] items-center gap-4">
              <div className="flex min-w-0 items-center gap-3">
                <GoalIcon status={goal.status} />
                <span className="truncate text-lg font-medium text-slate-800">{goal.name}</span>
              </div>
              <div className="flex justify-end gap-1">
                {Array.from({ length: goal.work }).map((_, index) => (
                  <span key={index} className={`flex h-8 w-8 items-center justify-center rounded-md ${index === 1 && goal.status !== "On track" ? "bg-orange-100 text-orange-600" : "bg-violet-100 text-violet-700"}`}>
                    {index === 1 && goal.status !== "On track" ? <CircleDot className="h-5 w-5" /> : <Zap className="h-5 w-5" />}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-6 flex justify-end">
          <Button variant="outline" onClick={onClose}>View all</Button>
        </div>
      </div>
    </div>
  );
}

function GoalIcon({ status }: { status: string }) {
  const className =
    status === "On track"
      ? "bg-emerald-50 text-emerald-600"
      : status === "At risk"
        ? "bg-orange-50 text-orange-600"
        : "bg-red-50 text-red-600";
  return (
    <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${className}`}>
      <Target className="h-6 w-6" />
    </span>
  );
}

function Legend({ count, label, tone }: { count: number; label: string; tone: string }) {
  return (
    <span className="inline-flex items-center gap-2">
      <span className={`rounded px-2 py-1 text-sm font-semibold ${tone}`}>{count}</span>
      {label}
    </span>
  );
}

function Metric({ label, value, danger = false }: { label: string; value: string; danger?: boolean }) {
  return (
    <div className="rounded-lg border bg-white p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className={`mt-2 text-2xl font-semibold ${danger ? "text-red-700" : "text-slate-950"}`}>{value}</p>
    </div>
  );
}

function SidePanel({ title, icon: Icon, rows }: { title: string; icon: React.ElementType; rows: string[] }) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between">
          <h3 className="flex items-center gap-2 font-semibold"><Icon className="h-4 w-4 text-blue-700" />{title}</h3>
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="mt-4 space-y-2">
          {rows.slice(0, 4).map((row) => (
            <div key={row} className="flex items-center gap-2 rounded-md bg-slate-50 px-3 py-2 text-sm">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              <span className="truncate">{row}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function TableCard({ title, icon: Icon, rows }: { title: string; icon: React.ElementType; rows: string[][] }) {
  return (
    <Card>
      <CardContent className="p-4">
        <h3 className="flex items-center gap-2 font-semibold"><Icon className="h-4 w-4 text-blue-700" />{title}</h3>
        <div className="mt-4 space-y-2">
          {rows.slice(0, 4).map((row) => (
            <div key={row.join("-")} className="rounded-md border bg-white p-3 text-sm">
              <p className="font-medium text-slate-900">{row[0]}</p>
              <p className="mt-1 line-clamp-1 text-xs text-muted-foreground">{row[1]}</p>
              <p className="mt-2 text-xs font-semibold text-blue-700">{row[2]}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

