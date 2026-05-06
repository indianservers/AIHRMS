import { useMemo, useState } from "react";
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
import { SortableContext, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import {
  Activity,
  BarChart3,
  CalendarDays,
  CheckCircle2,
  Filter,
  GripVertical,
  IndianRupee,
  LayoutGrid,
  ListFilter,
  Mail,
  Phone,
  Plus,
  Search,
  SlidersHorizontal,
  Sparkles,
  Users,
  X,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { formatCurrency, formatDate, statusColor } from "@/lib/utils";
import {
  crmActivities,
  crmAdminRows,
  crmAutomationRules,
  crmCampaigns,
  crmCompanies,
  crmDeals,
  crmFiles,
  crmLeads,
  crmProducts,
  crmQuotations,
  crmSettingsRows,
  crmTickets,
  pipelineStages,
  type CRMDeal,
  type CRMLead,
  type CRMRecord,
} from "./data";

type CRMPageKind =
  | "dashboard"
  | "leads"
  | "contacts"
  | "companies"
  | "deals"
  | "pipeline"
  | "activities"
  | "tasks"
  | "calendar"
  | "campaigns"
  | "products"
  | "quotations"
  | "tickets"
  | "files"
  | "reports"
  | "automation"
  | "settings"
  | "admin";

const pageTitles: Record<CRMPageKind, string> = {
  dashboard: "CRM Dashboard",
  leads: "Leads",
  contacts: "Contacts",
  companies: "Companies",
  deals: "Deals",
  pipeline: "Sales Pipeline",
  activities: "Activities",
  tasks: "CRM Tasks",
  calendar: "Calendar",
  campaigns: "Campaigns",
  products: "Products",
  quotations: "Quotations",
  tickets: "Support Tickets",
  files: "Files",
  reports: "Reports",
  automation: "Automation",
  settings: "CRM Settings",
  admin: "CRM Admin",
};

const savedViews = ["My records", "Hot pipeline", "Due this week", "No follow-up", "Recently updated"];

export default function CRMWorkspacePage({ kind }: { kind: CRMPageKind }) {
  if (kind === "pipeline") return <PipelinePage />;
  if (kind === "dashboard") return <CRMDashboard />;
  if (kind === "reports") return <CRMReports />;
  return <CRMListPage kind={kind} />;
}

function CRMDashboard() {
  const wonRevenue = crmDeals.filter((deal) => deal.stage === "Won").reduce((sum, deal) => sum + deal.amount, 0);
  const pipelineValue = crmDeals.filter((deal) => !["Won", "Lost"].includes(deal.stage)).reduce((sum, deal) => sum + deal.amount, 0);
  const weighted = crmDeals.reduce((sum, deal) => sum + (deal.amount * deal.probability) / 100, 0);
  const overdueFollowUps = crmLeads.filter((lead) => new Date(lead.nextFollowUp) < new Date("2026-05-07") && lead.status !== "Converted").length;
  const chartData = pipelineStages.map((stage) => ({
    stage,
    value: crmDeals.filter((deal) => deal.stage === stage).reduce((sum, deal) => sum + deal.amount, 0),
  }));
  const sourceData = ["Website", "Referral", "Event", "Partner", "Phone Call", "Email Campaign"].map((source) => ({
    name: source,
    value: crmLeads.filter((lead) => lead.source === source).length,
  }));
  const revenueTrend = [
    { month: "Jan", revenue: 18, forecast: 24 },
    { month: "Feb", revenue: 22, forecast: 28 },
    { month: "Mar", revenue: 31, forecast: 35 },
    { month: "Apr", revenue: 27, forecast: 38 },
    { month: "May", revenue: 42, forecast: 48 },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="VyaparaCRM" description="Sales command center for leads, accounts, deals, pipeline, activities, quotations, support, automation, and analytics." action="Quick create" />
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        <Metric icon={Users} label="Total leads" value={crmLeads.length} tone="blue" />
        <Metric icon={LayoutGrid} label="Open deals" value={crmDeals.filter((deal) => !["Won", "Lost"].includes(deal.stage)).length} tone="emerald" />
        <Metric icon={IndianRupee} label="Pipeline value" value={formatCurrency(pipelineValue)} tone="violet" />
        <Metric icon={BarChart3} label="Expected revenue" value={formatCurrency(weighted)} tone="amber" />
        <Metric icon={Activity} label="Overdue follow-ups" value={overdueFollowUps} tone="red" />
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.4fr_0.9fr]">
        <Card>
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle>Pipeline by stage</CardTitle>
            <Badge variant="outline">{formatCurrency(wonRevenue)} won</Badge>
          </CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="stage" tickLine={false} axisLine={false} interval={0} angle={-18} textAnchor="end" height={70} />
                <YAxis tickFormatter={(value) => `${Number(value) / 100000}L`} tickLine={false} axisLine={false} />
                <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                <Bar dataKey="value" fill="hsl(var(--primary))" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Leads by source</CardTitle></CardHeader>
          <CardContent className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={sourceData} dataKey="value" nameKey="name" innerRadius={58} outerRadius={104}>
                  {sourceData.map((_, index) => <Cell key={index} fill={["#2563eb", "#16a34a", "#f59e0b", "#7c3aed", "#dc2626", "#0891b2"][index]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_0.9fr]">
        <Card>
          <CardHeader><CardTitle>Revenue trend and forecast</CardTitle></CardHeader>
          <CardContent className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={revenueTrend}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="month" tickLine={false} axisLine={false} />
                <YAxis tickFormatter={(value) => `${value}L`} tickLine={false} axisLine={false} />
                <Tooltip formatter={(value) => `₹${value}L`} />
                <Line type="monotone" dataKey="revenue" stroke="#16a34a" strokeWidth={3} dot={false} />
                <Line type="monotone" dataKey="forecast" stroke="#2563eb" strokeWidth={3} strokeDasharray="4 4" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>AI Insights</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <Insight text="5 hot leads need follow-up this week. Assign backup owners before Friday." />
            <Insight text="Negotiation holds the highest weighted revenue. Two deals need discount approval." />
            <Insight text="4 quotations expire within 7 days; one accepted quote is ready for invoice conversion." />
            <Insight text="Critical support ticket TCK-1045 should be escalated to the support manager." />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function PipelinePage() {
  const [deals, setDeals] = useState(crmDeals);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [filter, setFilter] = useState("");
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 8 } }));
  const activeDeal = deals.find((deal) => deal.id === activeId);
  const visibleDeals = deals.filter((deal) => [deal.name, deal.company, deal.owner].join(" ").toLowerCase().includes(filter.toLowerCase()));

  const onDragStart = (event: DragStartEvent) => setActiveId(event.active.id as number);
  const onDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);
    if (!over) return;
    const targetStage = String(over.id).startsWith("stage-") ? String(over.id).replace("stage-", "") : deals.find((deal) => deal.id === over.id)?.stage;
    if (!targetStage) return;
    setDeals((items) => items.map((deal) => (deal.id === active.id ? { ...deal, stage: targetStage, probability: stageProbability(targetStage) } : deal)));
  };

  return (
    <div className="space-y-6">
      <PageHeader title="Sales Pipeline" description="Drag deals between stages. Probability and weighted forecast update with the target stage." action="Quick create deal" />
      <Toolbar search={filter} onSearch={setFilter} />
      <DndContext sensors={sensors} collisionDetection={closestCorners} onDragStart={onDragStart} onDragEnd={onDragEnd}>
        <div className="flex gap-4 overflow-x-auto pb-4">
          {pipelineStages.map((stage) => {
            const stageDeals = visibleDeals.filter((deal) => deal.stage === stage);
            return <PipelineColumn key={stage} stage={stage} deals={stageDeals} />;
          })}
        </div>
        <DragOverlay>{activeDeal ? <DealCard deal={activeDeal} overlay /> : null}</DragOverlay>
      </DndContext>
    </div>
  );
}

function PipelineColumn({ stage, deals }: { stage: string; deals: CRMDeal[] }) {
  const { setNodeRef, isOver } = useDroppable({ id: `stage-${stage}` });
  const value = deals.reduce((sum, deal) => sum + deal.amount, 0);
  const weighted = deals.reduce((sum, deal) => sum + (deal.amount * deal.probability) / 100, 0);
  return (
    <section ref={setNodeRef} className={`flex h-[calc(100vh-14rem)] w-80 shrink-0 flex-col rounded-lg border bg-muted/35 ${isOver ? "ring-2 ring-primary/40" : ""}`}>
      <header className="border-b bg-background p-3">
        <div className="flex items-center justify-between gap-2">
          <h2 className="truncate text-sm font-semibold">{stage}</h2>
          <span className="rounded-full bg-muted px-2 py-0.5 text-xs">{deals.length}</span>
        </div>
        <p className="mt-1 text-xs text-muted-foreground">{formatCurrency(value)} total / {formatCurrency(weighted)} weighted</p>
      </header>
      <SortableContext items={deals.map((deal) => deal.id)} strategy={verticalListSortingStrategy}>
        <div className="flex-1 space-y-3 overflow-y-auto p-3">
          {deals.map((deal) => <DealCard key={deal.id} deal={deal} />)}
          {!deals.length ? <div className="flex h-28 items-center justify-center rounded-lg border border-dashed bg-background/60 text-sm text-muted-foreground">Drop deal here</div> : null}
        </div>
      </SortableContext>
    </section>
  );
}

function DealCard({ deal, overlay = false }: { deal: CRMDeal; overlay?: boolean }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: deal.id });
  return (
    <article
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition }}
      className={`rounded-lg border bg-card p-3 shadow-sm ${isDragging ? "opacity-50" : ""} ${overlay ? "w-72 shadow-xl" : ""}`}
    >
      <div className="flex items-start gap-2">
        <button type="button" className="rounded p-1 text-muted-foreground hover:bg-muted" {...attributes} {...listeners} aria-label="Drag deal">
          <GripVertical className="h-4 w-4" />
        </button>
        <div className="min-w-0 flex-1">
          <h3 className="line-clamp-2 text-sm font-semibold">{deal.name}</h3>
          <p className="mt-1 truncate text-xs text-muted-foreground">{deal.company} / {deal.contact}</p>
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between text-xs">
        <span className="font-semibold">{formatCurrency(deal.amount)}</span>
        <Badge variant="outline">{deal.probability}%</Badge>
      </div>
      <p className="mt-2 text-xs text-muted-foreground">Close {formatDate(deal.closeDate)}</p>
      <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">Next: {deal.nextStep}</p>
    </article>
  );
}

function CRMListPage({ kind }: { kind: CRMPageKind }) {
  const [search, setSearch] = useState("");
  const [selectedView, setSelectedView] = useState(savedViews[0]);
  const [selectedRecord, setSelectedRecord] = useState<CRMRecord | null>(null);
  const [records, setRecords] = useState<CRMRecord[]>(() => rowsFor(kind));
  const [showCreate, setShowCreate] = useState(false);
  const rows = useMemo(() => records.filter((row) => Object.values(row).join(" ").toLowerCase().includes(search.toLowerCase())), [records, search]);

  const createRecord = () => {
    const nextId = records.length + 1;
    const title = pageTitles[kind].replace("CRM ", "").replace(/s$/, "");
    const record = defaultRecordFor(kind, nextId, title);
    setRecords((items) => [record, ...items]);
    setSelectedRecord(record);
    setShowCreate(false);
  };

  return (
    <div className="space-y-6">
      <PageHeader title={pageTitles[kind]} description={descriptionFor(kind)} action={actionFor(kind)} onAction={() => setShowCreate(true)} />
      <Toolbar search={search} onSearch={setSearch} selectedView={selectedView} onViewChange={setSelectedView} />
      <div className="grid gap-4 xl:grid-cols-[1fr_22rem]">
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[820px] text-sm">
                <thead className="sticky top-0 bg-muted/70 text-left text-xs uppercase tracking-wide text-muted-foreground">
                  <tr>{Object.keys(rows[0] || { item: "" }).map((key) => <th key={key} className="px-4 py-3 font-medium">{key.replace(/([A-Z])/g, " $1")}</th>)}</tr>
                </thead>
                <tbody>
                  {rows.map((row, index) => (
                    <tr key={index} className="cursor-pointer border-t hover:bg-muted/35" onClick={() => setSelectedRecord(row)}>
                      {Object.entries(row).map(([key, value]) => (
                        <td key={key} className="px-4 py-3">
                          {isBadgeField(key) ? (
                            <Badge className={statusColor(String(value))}>{String(value)}</Badge>
                          ) : key.toLowerCase().includes("date") || key.toLowerCase().includes("due") || key.toLowerCase().includes("followup") ? (
                            formatDate(String(value))
                          ) : typeof value === "number" && isMoneyField(key) ? (
                            formatCurrency(value)
                          ) : (
                            String(value)
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                  {!rows.length ? (
                    <tr><td className="px-4 py-12 text-center text-muted-foreground" colSpan={6}>No matching records</td></tr>
                  ) : null}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
        <RecordPanel record={selectedRecord || rows[0] || null} kind={kind} />
      </div>
      {showCreate ? <CreateRecordDialog kind={kind} onClose={() => setShowCreate(false)} onCreate={createRecord} /> : null}
    </div>
  );
}

function CRMReports() {
  const rows = [
    { report: "Lead conversion report", owner: "Sales Ops", cadence: "Weekly", status: "Ready" },
    { report: "Pipeline forecast", owner: "Sales Manager", cadence: "Daily", status: "Ready" },
    { report: "Overdue follow-ups", owner: "Sales Ops", cadence: "Daily", status: "Ready" },
    { report: "Campaign ROI", owner: "Marketing", cadence: "Monthly", status: "Ready" },
    { report: "Ticket status report", owner: "Support", cadence: "Weekly", status: "Ready" },
  ];
  return (
    <div className="space-y-6">
      <PageHeader title="CRM Reports" description="Sales, activity, revenue, campaign, quotation, and support analytics with drill-down tables." action="Export CSV" />
      <div className="grid gap-4 md:grid-cols-4">
        <Metric icon={CheckCircle2} label="Conversion rate" value="38%" tone="emerald" />
        <Metric icon={IndianRupee} label="Average deal size" value={formatCurrency(826000)} tone="blue" />
        <Metric icon={Activity} label="Open tickets" value={crmTickets.filter((ticket) => ticket.status !== "Resolved").length} tone="red" />
        <Metric icon={CalendarDays} label="Due activities" value={crmActivities.length} tone="amber" />
      </div>
      <Card>
        <CardContent className="p-4">
          {rows.map((row) => (
            <div key={row.report} className="grid gap-3 border-b py-3 last:border-0 md:grid-cols-[1fr_10rem_8rem_7rem] md:items-center">
              <div><p className="font-medium">{row.report}</p><p className="text-sm text-muted-foreground">{row.owner}</p></div>
              <span className="text-sm text-muted-foreground">{row.cadence}</span>
              <Badge className={statusColor(row.status)}>{row.status}</Badge>
              <Button variant="outline" size="sm">Open</Button>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

function Toolbar({ search, onSearch, selectedView, onViewChange }: { search: string; onSearch: (value: string) => void; selectedView?: string; onViewChange?: (value: string) => void }) {
  return (
    <div className="flex flex-col gap-3 rounded-lg border bg-card p-3 lg:flex-row lg:items-center">
      <div className="flex min-w-0 flex-1 items-center gap-2 rounded-md border px-3 py-2">
        <Search className="h-4 w-4 text-muted-foreground" />
        <Input value={search} onChange={(event) => onSearch(event.target.value)} placeholder="Search records, owners, companies..." className="border-0 p-0 shadow-none focus-visible:ring-0" />
      </div>
      {selectedView && onViewChange ? (
        <div className="flex gap-2 overflow-x-auto">
          {savedViews.map((view) => (
            <Button key={view} type="button" size="sm" variant={selectedView === view ? "default" : "outline"} onClick={() => onViewChange(view)}>
              {view}
            </Button>
          ))}
        </div>
      ) : null}
      <Button variant="outline"><Filter className="h-4 w-4" />Filters</Button>
      <Button variant="outline"><SlidersHorizontal className="h-4 w-4" />Columns</Button>
    </div>
  );
}

function PageHeader({ title, description, action, onAction }: { title: string; description: string; action?: string; onAction?: () => void }) {
  return (
    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 className="page-title">{title}</h1>
        <p className="page-description">{description}</p>
      </div>
      {action ? <Button onClick={onAction}><Plus className="h-4 w-4" />{action}</Button> : null}
    </div>
  );
}

function Metric({ icon: Icon, label, value, tone }: { icon: React.ElementType; label: string; value: string | number; tone: "blue" | "emerald" | "violet" | "amber" | "red" }) {
  const tones = {
    blue: "bg-blue-100 text-blue-700",
    emerald: "bg-emerald-100 text-emerald-700",
    violet: "bg-violet-100 text-violet-700",
    amber: "bg-amber-100 text-amber-700",
    red: "bg-red-100 text-red-700",
  };
  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-5">
        <div className={`rounded-lg p-3 ${tones[tone]}`}><Icon className="h-5 w-5" /></div>
        <div><p className="text-sm text-muted-foreground">{label}</p><p className="text-2xl font-semibold">{value}</p></div>
      </CardContent>
    </Card>
  );
}

function RecordPanel({ record, kind }: { record: CRMRecord | null; kind: CRMPageKind }) {
  if (!record) return <Card><CardContent className="p-5 text-sm text-muted-foreground">Select a record to inspect details.</CardContent></Card>;
  return (
    <Card className="h-fit">
      <CardHeader className="space-y-1">
        <CardTitle className="text-base">{String(record.name || record.company || record.deal || record.subject || record.quote || record.number || record.file || record.rule || pageTitles[kind])}</CardTitle>
        <p className="text-sm text-muted-foreground">Operational detail panel</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-2">
          {Object.entries(record).slice(0, 8).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between gap-3 rounded-md border bg-muted/30 px-3 py-2 text-sm">
              <span className="text-muted-foreground">{key.replace(/([A-Z])/g, " $1")}</span>
              <span className="text-right font-medium">{typeof value === "number" && isMoneyField(key) ? formatCurrency(value) : String(value)}</span>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-2 gap-2">
          <Button variant="outline"><Phone className="h-4 w-4" />Log call</Button>
          <Button variant="outline"><Mail className="h-4 w-4" />Log email</Button>
          <Button variant="outline"><CalendarDays className="h-4 w-4" />Schedule</Button>
          <Button variant="outline"><ListFilter className="h-4 w-4" />Task</Button>
        </div>
        <div className="rounded-lg border bg-muted/30 p-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Timeline</p>
          <div className="mt-3 space-y-3 text-sm">
            <TimelineItem text="Record updated by owner" />
            <TimelineItem text="Follow-up task generated" />
            <TimelineItem text="Notification sent to assigned user" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function CreateRecordDialog({ kind, onClose, onCreate }: { kind: CRMPageKind; onClose: () => void; onCreate: () => void }) {
  const title = actionFor(kind) || "Create record";
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/45 p-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="flex-row items-start justify-between">
          <div><CardTitle>{title}</CardTitle><p className="text-sm text-muted-foreground">Fast-create form with required CRM fields.</p></div>
          <Button variant="ghost" size="sm" onClick={onClose}><X className="h-4 w-4" /></Button>
        </CardHeader>
        <CardContent className="space-y-4">
          <Field label="Name"><Input defaultValue={`New ${pageTitles[kind].replace("CRM ", "").replace(/s$/, "")}`} /></Field>
          <Field label="Owner"><Input defaultValue="Ananya Rao" /></Field>
          <Field label="Status"><Input defaultValue={kind === "tickets" ? "Open" : "New"} /></Field>
          <Field label="Next follow-up"><Input type="date" defaultValue="2026-05-14" /></Field>
          <div className="flex justify-end gap-2"><Button variant="outline" onClick={onClose}>Cancel</Button><Button onClick={onCreate}>Create</Button></div>
        </CardContent>
      </Card>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="space-y-2"><Label>{label}</Label>{children}</div>;
}

function TimelineItem({ text }: { text: string }) {
  return <div className="flex gap-2"><span className="mt-1 h-2 w-2 rounded-full bg-primary" /><span>{text}</span></div>;
}

function Insight({ text }: { text: string }) {
  return <div className="rounded-lg border bg-muted/40 p-4 text-sm">{text}</div>;
}

function rowsFor(kind: CRMPageKind): CRMRecord[] {
  if (kind === "leads") return crmLeads.map(({ name, company, source, status, rating, owner, value, nextFollowUp }) => ({ name, company, source, status, rating, owner, value, nextFollowUp }));
  if (kind === "contacts") return crmLeads.map(({ name, company, email, phone, owner, nextFollowUp }) => ({ name, company, email, phone, lifecycle: "Opportunity", owner, nextFollowUp }));
  if (kind === "companies") return crmCompanies;
  if (kind === "deals") return crmDeals.map(({ name, company, owner, stage, amount, probability, closeDate }) => ({ name, company, owner, stage, amount, probability: `${probability}%`, closeDate }));
  if (kind === "activities" || kind === "tasks" || kind === "calendar") return crmActivities;
  if (kind === "campaigns") return crmCampaigns;
  if (kind === "products") return crmProducts;
  if (kind === "tickets") return crmTickets;
  if (kind === "quotations") return crmQuotations;
  if (kind === "files") return crmFiles;
  if (kind === "automation") return crmAutomationRules;
  if (kind === "settings") return crmSettingsRows;
  if (kind === "admin") return crmAdminRows;
  return [{ item: pageTitles[kind], status: "Ready" }];
}

function defaultRecordFor(kind: CRMPageKind, id: number, title: string): CRMRecord {
  if (kind === "leads") return { name: `${title} ${id}`, company: "New Account", source: "Website", status: "New", rating: "Warm", owner: "Ananya Rao", value: 250000, nextFollowUp: "2026-05-14" };
  if (kind === "deals") return { name: `${title} ${id}`, company: "New Account", owner: "Karan Shah", stage: "Prospecting", amount: 500000, probability: "10%", closeDate: "2026-06-15" };
  if (kind === "tickets") return { number: `TCK-${1100 + id}`, subject: "New customer request", priority: "Medium", status: "Open", company: "New Account", owner: "Support Desk" };
  return { name: `${title} ${id}`, owner: "Ananya Rao", status: "New", nextFollowUp: "2026-05-14" };
}

function descriptionFor(kind: CRMPageKind) {
  const descriptions: Record<CRMPageKind, string> = {
    dashboard: "",
    leads: "Capture, qualify, assign, import, export, and convert leads.",
    contacts: "Manage people, lifecycle stages, follow-up dates, and account links.",
    companies: "Account master data with owners, industries, revenue, and status.",
    deals: "Opportunities with amount, probability, products, quotations, and owners.",
    pipeline: "",
    activities: "Calls, emails, meetings, demos, proposals, and follow-up outcomes.",
    tasks: "CRM task queue for owners, teams, reminders, and related records.",
    calendar: "Follow-ups, meetings, expected close dates, campaigns, and quote expiries.",
    campaigns: "Campaign planning, lead generation, ROI, and conversion tracking.",
    products: "Products and services used in deals and quotations.",
    quotations: "Draft, send, accept, reject, and convert quotations.",
    tickets: "Customer support tickets linked to contacts, companies, and deals.",
    files: "Attachments for leads, contacts, accounts, deals, quotes, and tickets.",
    reports: "",
    automation: "Owner assignment, reminders, quote expiry, critical ticket escalation, and stale lead rules.",
    settings: "Lead sources, statuses, pipelines, quote settings, ticket categories, notifications, and import/export.",
    admin: "CRM roles, permissions, teams, audit logs, templates, and system settings.",
  };
  return descriptions[kind];
}

function actionFor(kind: CRMPageKind) {
  if (["leads", "contacts", "companies", "deals", "activities", "tasks", "campaigns", "products", "quotations", "tickets"].includes(kind)) return `Create ${pageTitles[kind].replace("CRM ", "").replace(/s$/, "")}`;
  if (kind === "automation") return "Create rule";
  if (kind === "files") return "Upload metadata";
  return undefined;
}

function isBadgeField(key: string) {
  const lower = key.toLowerCase();
  return ["status", "priority", "rating", "stage", "visibility", "type"].some((item) => lower.includes(item));
}

function isMoneyField(key: string) {
  const lower = key.toLowerCase();
  return ["amount", "value", "revenue", "budget", "price", "total"].some((item) => lower.includes(item));
}

function stageProbability(stage: string) {
  return ({
    Prospecting: 10,
    Qualification: 25,
    "Needs Analysis": 40,
    "Proposal Sent": 55,
    Negotiation: 70,
    "Contract Sent": 85,
    Won: 100,
    Lost: 0,
  } as Record<string, number>)[stage] ?? 0;
}
