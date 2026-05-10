import { ChangeEvent, useMemo, useRef, useState } from "react";
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
  AlertTriangle,
  ArrowUpDown,
  BarChart3,
  Bell,
  Building2,
  CalendarDays,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock,
  Download,
  FileCheck2,
  Filter,
  GripVertical,
  IndianRupee,
  LayoutGrid,
  ListFilter,
  Mail,
  Megaphone,
  Phone,
  Plus,
  Search,
  Sparkles,
  Target,
  Upload,
  Users,
  X,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ProductWorkflowCenter } from "@/components/product/ProductWorkflowCenter";
import { exportRows } from "@/lib/export";
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
  | "leadCash"
  | "forecasting"
  | "customer360"
  | "importExport"
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
  leadCash: "Lead-to-Cash",
  forecasting: "Forecasting",
  customer360: "Customer 360",
  importExport: "Import & Export",
  settings: "CRM Settings",
  admin: "CRM Admin",
};

const savedViews = ["My records", "Hot pipeline", "Due this week", "No follow-up", "Recently updated"];
type CRMFilters = { owner: string; status: string; type: string };
type SortState = { key: string; direction: "asc" | "desc" } | null;
type AutomationCard = [title: string, value: string, detail: string, Icon: React.ElementType];

export default function CRMWorkspacePage({ kind }: { kind: CRMPageKind }) {
  if (kind === "pipeline") return <PipelinePage />;
  if (kind === "dashboard") return <CRMDashboard />;
  if (kind === "reports") return <CRMReports />;
  if (kind === "automation") return <SalesAutomationPage />;
  if (kind === "leadCash") return <LeadToCashPage />;
  if (kind === "forecasting") return <ForecastingPage />;
  if (kind === "customer360") return <Customer360Page />;
  if (kind === "importExport") return <ImportExportPage />;
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

      <ProductWorkflowCenter product="crm" />
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
  const [filters, setFilters] = useState<CRMFilters>({ owner: "all", status: "all", type: "all" });
  const [showFilters, setShowFilters] = useState(kind === "calendar");
  const [selectedRecord, setSelectedRecord] = useState<CRMRecord | null>(null);
  const [records, setRecords] = useState<CRMRecord[]>(() => rowsFor(kind));
  const [contacts, setContacts] = useState<CRMRecord[]>(() => rowsFor("contacts"));
  const [showCreate, setShowCreate] = useState(false);
  const rows = useMemo(() => filterRecords(records, search, selectedView, filters), [records, search, selectedView, filters]);
  const owners = useMemo(() => uniqueValues(records, "owner"), [records]);
  const statuses = useMemo(() => uniqueValues(records, "status"), [records]);
  const types = useMemo(() => uniqueValues(records, "type"), [records]);

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
      <Toolbar
        search={search}
        onSearch={setSearch}
        selectedView={selectedView}
        onViewChange={setSelectedView}
        onToggleFilters={() => setShowFilters((value) => !value)}
        contacts={contacts}
        onImportContacts={(items) => setContacts(items)}
      />
      {showFilters ? (
        <FilterPanel
          filters={filters}
          onChange={setFilters}
          owners={owners}
          statuses={statuses}
          types={types}
          onClear={() => setFilters({ owner: "all", status: "all", type: "all" })}
        />
      ) : null}
      <div className="grid gap-4 xl:grid-cols-[1fr_22rem]">
        <SmartCRMTable rows={rows} title={pageTitles[kind]} onSelect={setSelectedRecord} />
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

function LeadToCashPage() {
  const flow = [
    ["Lead", "Qualified", `${crmLeads.filter((lead) => lead.status === "Qualified").length} qualified leads`, "/crm/leads"],
    ["Contact", "Created", `${crmLeads.filter((lead) => lead.status === "Converted").length || 1} converted contacts`, "/crm/contacts"],
    ["Company", "Linked", `${crmCompanies.length} accounts`, "/crm/companies"],
    ["Deal", "Open", `${crmDeals.filter((deal) => !["Won", "Lost"].includes(deal.stage)).length} active deals`, "/crm/deals"],
    ["Quotation", "Sent", `${crmQuotations.filter((quote) => quote.status === "Sent").length} sent quotes`, "/crm/quotations"],
    ["Order/Invoice", "Handoff", "Ready for finance handoff", "/crm/lead-to-cash"],
  ];
  const handoffRows = [
    { item: "QT-1003", customer: "HealthBridge Clinics", amount: 380000, status: "Accepted", next: "Create order and invoice draft" },
    { item: "Training Program Partnership", customer: "BrightPath Academy", amount: 540000, status: "Won", next: "Send order confirmation" },
    { item: "Real Estate CRM Setup", customer: "GreenField Realty", amount: 650000, status: "Negotiation", next: "Convert quote after approval" },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Lead-to-Cash" description="Convert leads into contacts, companies, deals, quotations, and order/invoice handoff without leaving CRM." action="Convert lead" />
      <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
        {flow.map(([label, status, detail, path], index) => (
          <Card key={label}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between gap-2">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">{index + 1}</div>
                <Badge variant="outline">{status}</Badge>
              </div>
              <p className="mt-3 font-semibold">{label}</p>
              <p className="mt-1 text-sm text-muted-foreground">{detail}</p>
              <a className="mt-3 inline-flex text-xs font-medium text-primary" href={path}>Open stage</a>
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="grid gap-4 xl:grid-cols-[1fr_22rem]">
        <Card>
          <CardHeader><CardTitle>Conversion Workbench</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {crmLeads.slice(0, 5).map((lead) => (
              <div key={lead.id} className="grid gap-3 rounded-lg border p-4 md:grid-cols-[1fr_9rem_9rem_auto] md:items-center">
                <div><p className="font-medium">{lead.name}</p><p className="text-sm text-muted-foreground">{lead.company} / {lead.source}</p></div>
                <Badge className={statusColor(lead.rating)}>{lead.rating}</Badge>
                <span className="text-sm font-medium">{formatCurrency(lead.value)}</span>
                <Button size="sm">Convert</Button>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Invoice Handoff Queue</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {handoffRows.map((row) => (
              <div key={row.item} className="rounded-lg border p-3">
                <div className="flex items-start justify-between gap-3">
                  <div><p className="font-medium">{row.item}</p><p className="text-sm text-muted-foreground">{row.customer}</p></div>
                  <Badge>{row.status}</Badge>
                </div>
                <p className="mt-2 text-sm font-semibold">{formatCurrency(row.amount)}</p>
                <p className="mt-1 text-xs text-muted-foreground">{row.next}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function SalesAutomationPage() {
  const automationCards: AutomationCard[] = [
    ["Reminders", "18 active", "Follow-up reminders from leads, deals, quotations, and tickets.", Bell],
    ["SLA follow-ups", "4 at risk", "Escalate customer replies and support-linked sales tasks before breach.", Clock],
    ["Stale deal alerts", "3 stale", "Detect opportunities without activity or next step updates.", AlertTriangle],
    ["Auto-assignment", "Round robin", "Route website, campaign, and partner leads to available owners.", Users],
    ["Email sequences", "6 live", "Drip campaigns for nurture, proposal follow-up, and renewal.", Mail],
    ["WhatsApp sequences", "5 live", "Message templates for demo reminders and quote expiry nudges.", Phone],
  ];
  const rules = [
    { rule: "Qualified lead follow-up", trigger: "Status = Qualified", action: "Create task + WhatsApp reminder", owner: "Sales Ops" },
    { rule: "Stale negotiation", trigger: "No activity for 5 days", action: "Alert owner and manager", owner: "Sales Manager" },
    { rule: "Quote expiry", trigger: "Expiry in 2 days", action: "Email sequence + task", owner: "Revenue Ops" },
    { rule: "Critical customer ticket", trigger: "Priority = Critical", action: "Pause renewal ask and notify owner", owner: "Support Lead" },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Sales Automation" description="Reminders, SLA follow-ups, stale deal alerts, auto-assignment, email sequences, and WhatsApp sequences." action="Create rule" />
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {automationCards.map(([title, value, detail, Icon]) => (
          <Card key={String(title)}>
            <CardContent className="flex gap-3 p-4">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary"><Icon className="h-5 w-5" /></div>
              <div><p className="font-semibold">{title}</p><p className="text-2xl font-semibold">{value}</p><p className="text-sm text-muted-foreground">{detail}</p></div>
            </CardContent>
          </Card>
        ))}
      </div>
      <Card>
        <CardHeader><CardTitle>Automation Rules</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {rules.map((row) => (
            <div key={row.rule} className="grid gap-3 rounded-lg border p-4 md:grid-cols-[1fr_13rem_15rem_9rem] md:items-center">
              <p className="font-medium">{row.rule}</p>
              <span className="text-sm text-muted-foreground">{row.trigger}</span>
              <span className="text-sm">{row.action}</span>
              <Badge variant="outline">{row.owner}</Badge>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

function ForecastingPage() {
  const weighted = crmDeals.reduce((sum, deal) => sum + (deal.amount * deal.probability) / 100, 0);
  const target = 6500000;
  const commit = crmDeals.filter((deal) => deal.probability >= 70).reduce((sum, deal) => sum + deal.amount, 0);
  const bestCase = crmDeals.filter((deal) => deal.probability >= 40).reduce((sum, deal) => sum + deal.amount, 0);
  const atRisk = crmDeals.filter((deal) => deal.probability < 40 && !["Won", "Lost"].includes(deal.stage)).reduce((sum, deal) => sum + deal.amount, 0);
  const forecastRows = [
    { view: "Commit", amount: commit, confidence: "High", owner: "Sales Manager" },
    { view: "Best case", amount: bestCase, confidence: "Medium", owner: "Revenue Ops" },
    { view: "At risk", amount: atRisk, confidence: "Low", owner: "Deal owners" },
    { view: "Weighted pipeline", amount: weighted, confidence: "Model", owner: "CRM Forecast" },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Forecasting" description="Weighted pipeline, monthly targets, quota tracking, and commit/best-case/at-risk sales views." action="Export forecast" />
      <div className="grid gap-3 md:grid-cols-4">
        <Metric icon={Target} label="Monthly target" value={formatCurrency(target)} tone="blue" />
        <Metric icon={IndianRupee} label="Weighted forecast" value={formatCurrency(weighted)} tone="emerald" />
        <Metric icon={CheckCircle2} label="Commit" value={formatCurrency(commit)} tone="violet" />
        <Metric icon={AlertTriangle} label="At risk" value={formatCurrency(atRisk)} tone="red" />
      </div>
      <Card>
        <CardHeader><CardTitle>Forecast Views</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {forecastRows.map((row) => (
            <div key={row.view} className="grid gap-3 rounded-lg border p-4 md:grid-cols-[1fr_12rem_8rem_10rem] md:items-center">
              <p className="font-medium">{row.view}</p>
              <span className="font-semibold">{formatCurrency(row.amount)}</span>
              <Badge variant={row.confidence === "Low" ? "destructive" : "outline"}>{row.confidence}</Badge>
              <span className="text-sm text-muted-foreground">{row.owner}</span>
            </div>
          ))}
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>Quota Tracking</CardTitle></CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          {["Ananya Rao", "Karan Shah", "Meera Iyer"].map((owner) => {
            const amount = crmDeals.filter((deal) => deal.owner === owner).reduce((sum, deal) => sum + (deal.amount * deal.probability) / 100, 0);
            const pct = Math.min(100, Math.round((amount / 2000000) * 100));
            return (
              <div key={owner} className="rounded-lg border p-4">
                <div className="flex items-center justify-between"><p className="font-medium">{owner}</p><Badge>{pct}%</Badge></div>
                <div className="mt-3 h-2 rounded-full bg-muted"><div className="h-2 rounded-full bg-primary" style={{ width: `${pct}%` }} /></div>
                <p className="mt-2 text-sm text-muted-foreground">{formatCurrency(amount)} weighted quota coverage</p>
              </div>
            );
          })}
        </CardContent>
      </Card>
    </div>
  );
}

function Customer360Page() {
  const customers = crmCompanies.map((company) => customer360For(String(company.name)));
  return (
    <div className="space-y-6">
      <PageHeader title="Customer 360" description="Contacts, companies, deals, tickets, activities, quotations, files, and campaigns in one customer view." action="Open customer" />
      <div className="grid gap-4 xl:grid-cols-2">
        {customers.map((customer) => (
          <Card key={customer.company}>
            <CardHeader className="flex-row items-start justify-between">
              <div><CardTitle>{customer.company}</CardTitle><p className="text-sm text-muted-foreground">{customer.industry}</p></div>
              <Badge>{customer.status}</Badge>
            </CardHeader>
            <CardContent className="grid gap-3 md:grid-cols-3">
              {customer.metrics.map(([label, value]) => (
                <div key={label} className="rounded-lg border p-3"><p className="text-xs text-muted-foreground">{label}</p><p className="text-lg font-semibold">{value}</p></div>
              ))}
              <div className="md:col-span-3 rounded-lg border bg-muted/30 p-3 text-sm">
                <p className="font-medium">Timeline</p>
                <div className="mt-2 space-y-2">
                  {customer.timeline.map((item) => <TimelineItem key={item} text={item} />)}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

function ImportExportPage() {
  const imports = [
    { file: "crm-contacts-may.csv", rows: 428, duplicates: 12, valid: 409, status: "Preview ready" },
    { file: "partner-leads.xlsx", rows: 96, duplicates: 4, valid: 88, status: "Imported" },
    { file: "company-cleanup.csv", rows: 74, duplicates: 9, valid: 61, status: "Rolled back" },
  ];
  const mapping = [
    ["Full Name", "name", "Required"],
    ["Email Address", "email", "Duplicate key"],
    ["Mobile", "phone", "Normalize"],
    ["Company", "company", "Create if missing"],
    ["Owner Email", "owner", "Assign user"],
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Import & Export Engine" description="Field mapping, duplicate detection, validation preview, rollback, and import history for CRM data." action="Upload import" />
      <div className="grid gap-3 md:grid-cols-5">
        <Metric icon={Upload} label="Imports" value={imports.length} tone="blue" />
        <Metric icon={FileCheck2} label="Valid rows" value={imports.reduce((sum, row) => sum + row.valid, 0)} tone="emerald" />
        <Metric icon={AlertTriangle} label="Duplicates" value={imports.reduce((sum, row) => sum + row.duplicates, 0)} tone="amber" />
        <Metric icon={Download} label="Exports" value="12" tone="violet" />
        <Metric icon={Clock} label="Rollback window" value="24h" tone="red" />
      </div>
      <div className="grid gap-4 xl:grid-cols-[1fr_24rem]">
        <Card>
          <CardHeader><CardTitle>Import History</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {imports.map((row) => (
              <div key={row.file} className="grid gap-3 rounded-lg border p-4 md:grid-cols-[1fr_7rem_7rem_7rem_auto] md:items-center">
                <p className="font-medium">{row.file}</p>
                <span className="text-sm">{row.rows} rows</span>
                <span className="text-sm text-amber-700">{row.duplicates} dupes</span>
                <span className="text-sm text-emerald-700">{row.valid} valid</span>
                <Button variant="outline" size="sm">{row.status === "Imported" ? "Rollback" : "Open"}</Button>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Field Mapping Preview</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {mapping.map(([source, target, rule]) => (
              <div key={source} className="rounded-lg border p-3 text-sm">
                <div className="flex items-center justify-between gap-2"><span className="font-medium">{source}</span><span>{target}</span></div>
                <p className="mt-1 text-xs text-muted-foreground">{rule}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Toolbar({
  search,
  onSearch,
  selectedView,
  onViewChange,
  onToggleFilters,
  contacts,
  onImportContacts,
}: {
  search: string;
  onSearch: (value: string) => void;
  selectedView?: string;
  onViewChange?: (value: string) => void;
  onToggleFilters?: () => void;
  contacts?: CRMRecord[];
  onImportContacts?: (rows: CRMRecord[]) => void;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const handleImport = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !onImportContacts) return;
    file.text().then((text) => {
      const imported = parseCsv(text);
      if (imported.length) onImportContacts(imported);
    });
    event.target.value = "";
  };

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
      <Button variant="outline" onClick={onToggleFilters}><Filter className="h-4 w-4" />Filters</Button>
      <Button variant="outline" onClick={() => exportRows("crm-contacts.csv", contacts || rowsFor("contacts"))}><Download className="h-4 w-4" />Export Contacts</Button>
      <input ref={inputRef} type="file" accept=".csv,text/csv" className="hidden" onChange={handleImport} />
      <Button variant="outline" onClick={() => inputRef.current?.click()}><Upload className="h-4 w-4" />Import Contacts</Button>
    </div>
  );
}

function FilterPanel({
  filters,
  onChange,
  owners,
  statuses,
  types,
  onClear,
}: {
  filters: CRMFilters;
  onChange: (filters: CRMFilters) => void;
  owners: string[];
  statuses: string[];
  types: string[];
  onClear: () => void;
}) {
  const patch = (update: Partial<CRMFilters>) => onChange({ ...filters, ...update });
  return (
    <Card>
      <CardContent className="grid gap-3 p-4 md:grid-cols-[1fr_1fr_1fr_auto] md:items-end">
        <Field label="Owner">
          <select className="h-10 rounded-md border bg-background px-3 text-sm" value={filters.owner} onChange={(event) => patch({ owner: event.target.value })}>
            <option value="all">All owners</option>
            {owners.map((owner) => <option key={owner} value={owner}>{owner}</option>)}
          </select>
        </Field>
        <Field label="Status">
          <select className="h-10 rounded-md border bg-background px-3 text-sm" value={filters.status} onChange={(event) => patch({ status: event.target.value })}>
            <option value="all">All statuses</option>
            {statuses.map((status) => <option key={status} value={status}>{status}</option>)}
          </select>
        </Field>
        <Field label="Type">
          <select className="h-10 rounded-md border bg-background px-3 text-sm" value={filters.type} onChange={(event) => patch({ type: event.target.value })}>
            <option value="all">All types</option>
            {types.map((type) => <option key={type} value={type}>{type}</option>)}
          </select>
        </Field>
        <Button variant="outline" onClick={onClear}>Clear</Button>
      </CardContent>
    </Card>
  );
}

function SmartCRMTable({ rows, title, onSelect }: { rows: CRMRecord[]; title: string; onSelect: (row: CRMRecord) => void }) {
  const [sort, setSort] = useState<SortState>(null);
  const [columnOrder, setColumnOrder] = useState<string[]>([]);
  const [widths, setWidths] = useState<Record<string, number>>({});
  const columns = useMemo(() => {
    const keys = Array.from(rows.reduce((set, row) => {
      Object.keys(row).forEach((key) => set.add(key));
      return set;
    }, new Set<string>()));
    const known = columnOrder.filter((key) => keys.includes(key));
    const fresh = keys.filter((key) => !known.includes(key));
    return [...known, ...fresh];
  }, [rows, columnOrder]);
  const visibleRows = useMemo(() => {
    if (!sort) return rows;
    return [...rows].sort((a, b) => compareValues(a[sort.key], b[sort.key], sort.direction));
  }, [rows, sort]);

  const toggleSort = (key: string) => {
    setSort((current) => {
      if (current?.key !== key) return { key, direction: "asc" };
      if (current.direction === "asc") return { key, direction: "desc" };
      return null;
    });
  };
  const moveColumn = (key: string, direction: -1 | 1) => {
    const current = columns;
    const index = current.indexOf(key);
    const target = index + direction;
    if (target < 0 || target >= current.length) return;
    const next = [...current];
    [next[index], next[target]] = [next[target], next[index]];
    setColumnOrder(next);
  };
  const startResize = (key: string, event: React.MouseEvent) => {
    event.preventDefault();
    const startX = event.clientX;
    const startWidth = widths[key] || 160;
    const onMove = (moveEvent: MouseEvent) => {
      setWidths((current) => ({ ...current, [key]: Math.max(96, startWidth + moveEvent.clientX - startX) }));
    };
    const onUp = () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  };

  return (
    <Card>
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="text-base">{title} Grid</CardTitle>
        <Button variant="outline" size="sm" onClick={() => exportRows(`${title.toLowerCase().replace(/\s+/g, "-")}.csv`, visibleRows)}>
          <Download className="h-4 w-4" />Export Grid
        </Button>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[820px] table-fixed text-sm">
            <thead className="sticky top-0 bg-muted/70 text-left text-xs uppercase tracking-wide text-muted-foreground">
              <tr>
                {columns.map((key) => (
                  <th key={key} style={{ width: widths[key] || 160 }} className="relative px-4 py-3 font-medium">
                    <div className="flex items-center gap-1">
                      <button className="flex min-w-0 items-center gap-1 truncate" onClick={() => toggleSort(key)}>
                        <span className="truncate">{key.replace(/([A-Z])/g, " $1")}</span>
                        <ArrowUpDown className="h-3 w-3 shrink-0" />
                      </button>
                      <button className="rounded p-0.5 hover:bg-background" onClick={() => moveColumn(key, -1)} aria-label={`Move ${key} left`}><ChevronLeft className="h-3 w-3" /></button>
                      <button className="rounded p-0.5 hover:bg-background" onClick={() => moveColumn(key, 1)} aria-label={`Move ${key} right`}><ChevronRight className="h-3 w-3" /></button>
                    </div>
                    <button className="absolute right-0 top-0 h-full w-1 cursor-col-resize bg-border/60 opacity-0 hover:opacity-100" onMouseDown={(event) => startResize(key, event)} aria-label={`Resize ${key}`} />
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {visibleRows.map((row, index) => (
                <tr key={index} className="cursor-pointer border-t hover:bg-muted/35" onClick={() => onSelect(row)}>
                  {columns.map((key) => <td key={key} style={{ width: widths[key] || 160 }} className="truncate px-4 py-3">{renderCell(key, row[key])}</td>)}
                </tr>
              ))}
              {!visibleRows.length ? (
                <tr><td className="px-4 py-12 text-center text-muted-foreground" colSpan={Math.max(columns.length, 1)}>No matching records</td></tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
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
  const customer360 = kind === "contacts" || kind === "companies" ? customer360For(String(record.company || record.name || "")) : null;
  return (
    <Card className="h-fit">
      <CardHeader className="space-y-1">
        <CardTitle className="text-base">{String(record.name || record.company || record.deal || record.subject || record.quote || record.number || record.file || record.rule || pageTitles[kind])}</CardTitle>
        <p className="text-sm text-muted-foreground">Operational detail panel</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid max-h-[28rem] gap-2 overflow-y-auto pr-1">
          {Object.entries(record).map(([key, value]) => (
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
        {customer360 ? (
          <div className="rounded-lg border bg-primary/5 p-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Customer 360</p>
            <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
              {customer360.metrics.map(([label, value]) => (
                <div key={label} className="rounded-md bg-background p-2">
                  <p className="text-xs text-muted-foreground">{label}</p>
                  <p className="font-semibold">{value}</p>
                </div>
              ))}
            </div>
            <div className="mt-3 space-y-2 text-sm">
              {customer360.timeline.slice(0, 3).map((item) => <TimelineItem key={item} text={item} />)}
            </div>
          </div>
        ) : null}
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

function customer360For(companyName: string) {
  const company = crmCompanies.find((item) => String(item.name) === companyName || String(item.company) === companyName);
  const contacts = crmLeads.filter((lead) => lead.company === companyName);
  const deals = crmDeals.filter((deal) => deal.company === companyName);
  const tickets = crmTickets.filter((ticket) => String(ticket.company) === companyName);
  const quotes = crmQuotations.filter((quote) => String(quote.company) === companyName);
  const files = crmFiles.filter((file) => String(file.linkedTo).includes(companyName) || deals.some((deal) => String(file.linkedTo).includes(deal.name)));
  const campaigns = crmCampaigns.filter((campaign) => contacts.some((contact) => String(campaign.campaign).toLowerCase().includes(String(contact.source).toLowerCase().split(" ")[0] || "")));
  const activities = crmActivities.filter((activity) => deals.some((deal) => String(activity.subject).toLowerCase().includes(deal.company.split(" ")[0].toLowerCase())));
  const openValue = deals.filter((deal) => !["Won", "Lost"].includes(deal.stage)).reduce((sum, deal) => sum + deal.amount, 0);

  return {
    company: companyName || "Customer",
    industry: String(company?.industry || contacts[0]?.industry || "Account"),
    status: String(company?.status || contacts[0]?.status || "Active"),
    metrics: [
      ["Contacts", contacts.length || 1],
      ["Deals", deals.length],
      ["Pipeline", formatCurrency(openValue)],
      ["Tickets", tickets.length],
      ["Quotes", quotes.length],
      ["Files", files.length],
      ["Campaigns", campaigns.length],
      ["Activities", activities.length],
    ] as Array<[string, string | number]>,
    timeline: [
      deals[0] ? `Deal: ${deals[0].name} at ${deals[0].stage}` : "No open deal activity",
      quotes[0] ? `Quotation: ${quotes[0].quote} is ${quotes[0].status}` : "No active quotation",
      tickets[0] ? `Ticket: ${tickets[0].number} ${tickets[0].status}` : "No open support ticket",
      contacts[0] ? `Primary contact: ${contacts[0].name}` : "Contact profile ready",
      files[0] ? `File attached: ${files[0].file}` : "No files attached",
    ],
  };
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

function filterRecords(records: CRMRecord[], search: string, view: string, filters: CRMFilters) {
  const text = search.toLowerCase();
  const today = new Date("2026-05-10");
  const weekEnd = new Date("2026-05-17");
  return records.filter((row) => {
    const matchesSearch = Object.values(row).join(" ").toLowerCase().includes(text);
    const matchesOwner = filters.owner === "all" || row.owner === filters.owner;
    const matchesStatus = filters.status === "all" || row.status === filters.status;
    const matchesType = filters.type === "all" || row.type === filters.type;
    const dueValue = String(row.due || row.nextFollowUp || row.closeDate || row.expiryDate || "");
    const dueDate = dueValue ? new Date(dueValue) : null;
    const matchesView =
      view === "Due this week"
        ? !!dueDate && dueDate >= today && dueDate <= weekEnd
        : view === "Hot pipeline"
          ? ["Hot", "High", "Urgent", "Critical", "Negotiation", "Contract Sent"].some((value) => Object.values(row).includes(value))
          : view === "No follow-up"
            ? !dueValue
            : true;
    return matchesSearch && matchesOwner && matchesStatus && matchesType && matchesView;
  });
}

function uniqueValues(records: CRMRecord[], key: string) {
  return Array.from(new Set(records.map((row) => row[key]).filter(Boolean).map(String))).sort();
}

function parseCsv(text: string): CRMRecord[] {
  const lines = text.split(/\r?\n/).filter((line) => line.trim());
  if (lines.length < 2) return [];
  const headers = splitCsvLine(lines[0]);
  return lines.slice(1).map((line) => {
    const values = splitCsvLine(line);
    return headers.reduce<CRMRecord>((row, header, index) => {
      row[header || `field${index + 1}`] = values[index] || "";
      return row;
    }, {});
  });
}

function splitCsvLine(line: string) {
  const values: string[] = [];
  let current = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    const next = line[index + 1];
    if (char === '"' && quoted && next === '"') {
      current += '"';
      index += 1;
    } else if (char === '"') {
      quoted = !quoted;
    } else if (char === "," && !quoted) {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  values.push(current);
  return values.map((value) => value.trim());
}

function compareValues(a: unknown, b: unknown, direction: "asc" | "desc") {
  const multiplier = direction === "asc" ? 1 : -1;
  if (typeof a === "number" && typeof b === "number") return (a - b) * multiplier;
  const dateA = Date.parse(String(a));
  const dateB = Date.parse(String(b));
  if (!Number.isNaN(dateA) && !Number.isNaN(dateB)) return (dateA - dateB) * multiplier;
  return String(a ?? "").localeCompare(String(b ?? "")) * multiplier;
}

function renderCell(key: string, value: string | number | undefined) {
  if (isBadgeField(key)) return <Badge className={statusColor(String(value))}>{String(value)}</Badge>;
  if (key.toLowerCase().includes("date") || key.toLowerCase().includes("due") || key.toLowerCase().includes("followup")) return formatDate(String(value));
  if (typeof value === "number" && isMoneyField(key)) return formatCurrency(value);
  return String(value ?? "");
}

function rowsFor(kind: CRMPageKind): CRMRecord[] {
  if (kind === "leads") return crmLeads.map(toLeadRecord);
  if (kind === "contacts") return crmLeads.map(toContactRecord);
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
  if (kind === "leads") return {
    leadId: `LD-${String(1100 + id).padStart(4, "0")}`,
    name: `${title} ${id}`,
    company: "New Account",
    designation: "Decision Maker",
    email: `lead${id}@newaccount.example`,
    phone: "+91 90000 00000",
    mobile: "+91 90000 00001",
    city: "Bengaluru",
    state: "Karnataka",
    country: "India",
    source: "Website",
    campaign: "Inbound Demo",
    status: "New",
    rating: "Warm",
    lifecycleStage: "Lead",
    owner: "Ananya Rao",
    value: 250000,
    expectedCloseDate: "2026-06-20",
    productInterest: "CRM Starter",
    requirement: "Evaluate CRM workflow",
    budgetRange: "2L-5L",
    decisionMaker: "Yes",
    leadScore: 62,
    probability: "25%",
    nextFollowUp: "2026-05-14",
    lastContacted: "2026-05-10",
    lastActivity: "Created lead",
    preferredChannel: "Email",
    tags: "New, Website",
    notes: "Fresh inbound lead",
  };
  if (kind === "contacts") return {
    contactId: `CT-${String(2100 + id).padStart(4, "0")}`,
    name: `${title} ${id}`,
    company: "New Account",
    title: "Manager",
    department: "Sales",
    email: `contact${id}@newaccount.example`,
    alternateEmail: "",
    phone: "+91 90000 00000",
    mobile: "+91 90000 00001",
    city: "Bengaluru",
    state: "Karnataka",
    country: "India",
    lifecycle: "Opportunity",
    accountType: "Prospect",
    owner: "Ananya Rao",
    status: "Active",
    source: "Manual Entry",
    leadSource: "Website",
    lastContacted: "2026-05-10",
    nextFollowUp: "2026-05-14",
    birthday: "1990-01-01",
    linkedin: "linkedin.com/in/new-contact",
    preferredChannel: "Email",
    emailOptIn: "Yes",
    smsOptIn: "Yes",
    openDeals: 0,
    lifetimeValue: 0,
    supportStatus: "None",
    tags: "New",
    notes: "New CRM contact",
  };
  if (kind === "deals") return { name: `${title} ${id}`, company: "New Account", owner: "Karan Shah", stage: "Prospecting", amount: 500000, probability: "10%", closeDate: "2026-06-15" };
  if (kind === "tickets") return { number: `TCK-${1100 + id}`, subject: "New customer request", priority: "Medium", status: "Open", company: "New Account", owner: "Support Desk" };
  return { name: `${title} ${id}`, owner: "Ananya Rao", status: "New", nextFollowUp: "2026-05-14" };
}

function toLeadRecord(lead: CRMLead): CRMRecord {
  const index = lead.id - 1;
  const designations = ["Founder", "Operations Head", "Director", "Clinic Administrator", "Plant Manager", "Retail Growth Lead", "Managing Partner", "Principal Consultant"];
  const cities = ["Hyderabad", "Kochi", "Pune", "Mumbai", "Chennai", "Bengaluru", "Delhi", "Ahmedabad"];
  const states = ["Telangana", "Kerala", "Maharashtra", "Maharashtra", "Tamil Nadu", "Karnataka", "Delhi", "Gujarat"];
  const campaigns = ["Website Demo", "Referral Connect", "Education Expo", "Healthcare Outreach", "Partner Pipeline", "Retail Growth Ads", "Marketplace Listing", "Social Prospecting"];
  const products = ["CRM Growth", "CRM Starter", "Training Pack", "Support Retainer", "Enterprise Suite", "Marketing Automation", "CRM Growth", "Data Migration"];
  const requirements = [
    "Centralize sales follow-ups and opportunity tracking",
    "Manage site visits, broker leads, and quotation follow-ups",
    "Track admissions enquiries and training partnerships",
    "Improve patient enquiry follow-up and SLA visibility",
    "Connect plant enquiries with ERP implementation pipeline",
    "Automate retail campaigns and lead assignment",
    "Track advisory prospects and compliance-heavy deal notes",
    "Manage consulting proposals and cloud migration leads",
  ];

  return {
    leadId: `LD-${String(1000 + lead.id).padStart(4, "0")}`,
    name: lead.name,
    company: lead.company,
    designation: designations[index] || "Decision Maker",
    email: lead.email,
    phone: lead.phone,
    mobile: lead.phone.replace("110", "220"),
    city: cities[index] || "Bengaluru",
    state: states[index] || "Karnataka",
    country: "India",
    source: lead.source,
    campaign: campaigns[index] || lead.source,
    status: lead.status,
    rating: lead.rating,
    lifecycleStage: lead.status === "Converted" ? "Customer" : "Lead",
    owner: lead.owner,
    value: lead.value,
    expectedCloseDate: ["2026-05-28", "2026-06-10", "2026-06-02", "2026-06-18", "2026-05-24", "2026-05-30", "2026-06-05", "2026-06-12"][index] || "2026-06-20",
    productInterest: products[index] || "CRM Starter",
    requirement: requirements[index] || "Evaluate CRM workflow",
    budgetRange: lead.value >= 800000 ? "8L+" : lead.value >= 400000 ? "4L-8L" : "2L-4L",
    decisionMaker: ["Yes", "No", "Influencer", "Yes", "Yes", "Influencer", "Yes", "No"][index] || "Yes",
    leadScore: [92, 74, 68, 48, 95, 71, 88, 41][index] || 60,
    probability: lead.rating === "Hot" ? "70%" : lead.rating === "Warm" ? "40%" : "15%",
    nextFollowUp: lead.nextFollowUp,
    lastContacted: lead.lastContacted,
    lastActivity: ["Discovery call", "Referral email", "Event scan", "Intro call", "Partner handoff", "Campaign click", "Marketplace enquiry", "Social DM"][index] || "Follow-up",
    preferredChannel: ["Phone", "Email", "WhatsApp", "Phone", "Email", "Email", "Phone", "LinkedIn"][index] || "Email",
    tags: [lead.rating, lead.source, lead.industry].join(", "),
    notes: requirements[index] || "Qualified CRM enquiry",
  };
}

function toContactRecord(lead: CRMLead): CRMRecord {
  const index = lead.id - 1;
  const leadRecord = toLeadRecord(lead);
  const titles = ["Founder", "Sales Director", "Program Head", "Clinic Admin", "Manufacturing Head", "Retail Lead", "Partner", "Consultant"];
  const departments = ["Leadership", "Sales", "Admissions", "Operations", "Manufacturing", "Marketing", "Advisory", "Consulting"];

  return {
    contactId: `CT-${String(2000 + lead.id).padStart(4, "0")}`,
    name: lead.name,
    company: lead.company,
    title: titles[index] || String(leadRecord.designation),
    department: departments[index] || "Sales",
    email: lead.email,
    alternateEmail: lead.email.replace("@", ".alt@"),
    phone: lead.phone,
    mobile: String(leadRecord.mobile),
    city: String(leadRecord.city),
    state: String(leadRecord.state),
    country: "India",
    lifecycle: lead.status === "Converted" ? "Customer" : "Opportunity",
    accountType: lead.status === "Converted" ? "Customer" : "Prospect",
    owner: lead.owner,
    status: lead.status === "Converted" ? "Active" : "Open",
    source: lead.source,
    leadSource: lead.source,
    lastContacted: lead.lastContacted,
    nextFollowUp: lead.nextFollowUp,
    birthday: ["1986-02-14", "1990-08-21", "1982-11-02", "1988-04-18", "1979-07-09", "1992-12-05", "1984-09-27", "1991-03-30"][index] || "1990-01-01",
    linkedin: `linkedin.com/in/${lead.name.toLowerCase().replace(/\s+/g, "-")}`,
    preferredChannel: String(leadRecord.preferredChannel),
    emailOptIn: index % 3 === 0 ? "No" : "Yes",
    smsOptIn: index % 2 === 0 ? "Yes" : "No",
    openDeals: lead.status === "Converted" ? 0 : 1,
    lifetimeValue: lead.status === "Converted" ? lead.value : 0,
    supportStatus: lead.status === "Converted" ? "Active SLA" : "None",
    tags: `${lead.rating}, ${lead.industry}`,
    notes: `Primary contact for ${lead.company}`,
  };
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
    leadCash: "Lead-to-cash conversion from lead to contact, account, deal, quote, and invoice handoff.",
    forecasting: "Weighted pipeline, monthly target tracking, quota coverage, and commit/best-case/at-risk views.",
    customer360: "Unified customer view across contacts, companies, deals, tickets, activities, quotations, files, and campaigns.",
    importExport: "Field mapping, duplicate detection, validation preview, rollback, and import history.",
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
