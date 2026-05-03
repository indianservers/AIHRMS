import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Download, FileCheck2, Loader2, Send, TriangleAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { payrollApi, statutoryApi } from "@/services/api";
import { usePageTitle } from "@/hooks/use-page-title";
import { toast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

const TABS = ["Compliance Calendar", "Generate Files", "Submission History"] as const;
const TYPES = ["PF", "ESI", "PT", "LWF", "TDS"];
const FILE_TYPES = [
  ["pf_ecr", "Generate PF ECR"],
  ["esi", "Generate ESI Return"],
  ["pt", "Generate PT Challan"],
  ["tds_24q", "Generate TDS 24Q"],
] as const;

type CalendarItem = {
  id: number;
  statutory_type: string;
  due_date: string;
  period_start?: string;
  period_end?: string;
  description?: string;
  status: string;
};

type Submission = {
  id: number;
  statutory_type: string;
  payroll_run_id: number;
  payroll_period?: string;
  validation_status: string;
  validation_errors_json?: Array<{ row: number; field: string; error: string }>;
  row_count?: number;
  total_amount?: number;
  submitted_at?: string;
  portal_reference?: string;
};

type PayrollRun = {
  id: number;
  month: number;
  year: number;
  status: string;
  total_employees?: number;
  employee_count?: number;
};

const money = (value: unknown) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(Number(value || 0));

export default function StatutoryCompliancePage() {
  usePageTitle("Statutory Compliance");
  const [tab, setTab] = useState<(typeof TABS)[number]>("Compliance Calendar");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Statutory Compliance</h1>
        <p className="page-description">Track due dates, generate statutory files, and monitor portal submission status.</p>
      </div>
      <div className="flex flex-wrap gap-2 border-b">
        {TABS.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setTab(item)}
            className={cn("border-b-2 px-3 py-2 text-sm font-medium", tab === item ? "border-primary text-primary" : "border-transparent text-muted-foreground")}
          >
            {item}
          </button>
        ))}
      </div>
      {tab === "Compliance Calendar" && <CalendarTab />}
      {tab === "Generate Files" && <GenerateTab />}
      {tab === "Submission History" && <HistoryTab />}
    </div>
  );
}

function CalendarTab() {
  const qc = useQueryClient();
  const [filters, setFilters] = useState({ statutory_type: "", status: "", year: String(new Date().getFullYear()) });
  const [marking, setMarking] = useState<CalendarItem | null>(null);
  const [remarks, setRemarks] = useState("");
  const params = { ...filters, statutory_type: filters.statutory_type || undefined, status: filters.status || undefined, year: filters.year || undefined };
  const summary = useQuery({ queryKey: ["statutory-summary"], queryFn: () => statutoryApi.complianceSummary().then((r) => r.data) });
  const calendar = useQuery({ queryKey: ["statutory-calendar", params], queryFn: () => statutoryApi.calendar(params).then((r) => r.data as CalendarItem[]) });
  const markFiled = useMutation({
    mutationFn: () => statutoryApi.markFiled(marking!.id, { review_remarks: remarks || undefined }),
    onSuccess: () => {
      toast({ title: "Marked as filed" });
      setMarking(null);
      setRemarks("");
      qc.invalidateQueries({ queryKey: ["statutory-calendar"] });
      qc.invalidateQueries({ queryKey: ["statutory-summary"] });
    },
    onError: () => toast({ title: "Unable to mark filed", variant: "destructive" }),
  });
  const counts = summary.data?.counts || {};

  return (
    <div className="space-y-5">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Summary label="Pending" value={counts.Pending || 0} className="bg-yellow-50 text-yellow-700" />
        <Summary label="Filed" value={counts.Filed || 0} className="bg-green-50 text-green-700" />
        <Summary label="Overdue" value={counts.Overdue || 0} className="bg-red-50 text-red-700" />
        <Summary label="Upcoming this month" value={summary.data?.upcoming_count || 0} className="bg-blue-50 text-blue-700" />
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Compliance Calendar</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-3">
            <select className="h-10 rounded-md border bg-background px-3 text-sm" value={filters.statutory_type} onChange={(e) => setFilters({ ...filters, statutory_type: e.target.value })}>
              <option value="">All types</option>{TYPES.map((type) => <option key={type}>{type}</option>)}
            </select>
            <select className="h-10 rounded-md border bg-background px-3 text-sm" value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
              <option value="">All statuses</option>{["Pending", "Filed", "Overdue"].map((status) => <option key={status}>{status}</option>)}
            </select>
            <Input value={filters.year} onChange={(e) => setFilters({ ...filters, year: e.target.value })} placeholder="Year" />
          </div>
          {calendar.isLoading ? <div className="h-40 animate-pulse rounded bg-muted" /> : (
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full min-w-[820px] text-sm">
                <thead className="bg-muted/60"><tr><th className="px-3 py-2 text-left">Type</th><th className="px-3 py-2 text-left">Description</th><th className="px-3 py-2 text-left">Period</th><th className="px-3 py-2 text-left">Due Date</th><th className="px-3 py-2 text-left">Status</th><th className="px-3 py-2 text-right">Actions</th></tr></thead>
                <tbody>
                  {(calendar.data || []).map((item) => {
                    const overdue = item.status !== "Filed" && new Date(item.due_date) < new Date();
                    return (
                      <tr key={item.id} className="border-t">
                        <td className="px-3 py-2"><TypeBadge type={item.statutory_type} /></td>
                        <td className="px-3 py-2">{item.description || "Statutory filing"}</td>
                        <td className="px-3 py-2">{item.period_start || "-"} to {item.period_end || "-"}</td>
                        <td className="px-3 py-2">{item.due_date}</td>
                        <td className="px-3 py-2"><StatusBadge status={overdue ? "Overdue" : item.status} /></td>
                        <td className="px-3 py-2 text-right">{item.status !== "Filed" && <Button size="sm" variant="outline" onClick={() => setMarking(item)}>Mark Filed</Button>}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
      {marking && (
        <Modal title="Mark Filed" onClose={() => setMarking(null)}>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">Confirm filing for {marking.statutory_type} due on {marking.due_date}.</p>
            <Input value={remarks} onChange={(e) => setRemarks(e.target.value)} placeholder="Optional remarks" />
            <div className="flex justify-end gap-2"><Button variant="outline" onClick={() => setMarking(null)}>Cancel</Button><Button onClick={() => markFiled.mutate()} disabled={markFiled.isPending}>Confirm</Button></div>
          </div>
        </Modal>
      )}
    </div>
  );
}

function GenerateTab() {
  const qc = useQueryClient();
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [lastResult, setLastResult] = useState<any>(null);
  const [ackSubmission, setAckSubmission] = useState<number | null>(null);
  const [ack, setAck] = useState("");
  const runs = useQuery({ queryKey: ["payroll-runs-statutory"], queryFn: () => payrollApi.runs({ status: "locked,paid" }).then((r) => r.data as PayrollRun[]) });
  const submissions = useQuery({ queryKey: ["statutory-submissions", selectedRunId], queryFn: () => statutoryApi.submissions({ payroll_run_id: selectedRunId }).then((r) => r.data as Submission[]), enabled: !!selectedRunId });
  const generate = useMutation({
    mutationFn: (type: string) => statutoryApi.generate(selectedRunId!, type),
    onSuccess: (response) => {
      setLastResult(response.data);
      toast({ title: "File generated" });
      qc.invalidateQueries({ queryKey: ["statutory-submissions"] });
    },
    onError: () => toast({ title: "Unable to generate file", variant: "destructive" }),
  });
  const markSubmitted = useMutation({
    mutationFn: () => statutoryApi.markSubmitted(ackSubmission!, { portal_reference: ack }),
    onSuccess: () => {
      toast({ title: "Marked as submitted" });
      setAckSubmission(null);
      setAck("");
      qc.invalidateQueries({ queryKey: ["statutory-submissions"] });
    },
  });
  const lockedRuns = (runs.data || []).filter((run) => ["locked", "paid"].includes(run.status));

  return (
    <div className="grid gap-5 xl:grid-cols-[320px_1fr]">
      <Card>
        <CardHeader><CardTitle className="text-base">Payroll Runs</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {runs.isLoading && <div className="h-40 animate-pulse rounded bg-muted" />}
          {lockedRuns.map((run) => (
            <button key={run.id} type="button" onClick={() => setSelectedRunId(run.id)} className={cn("w-full rounded-lg border p-3 text-left", selectedRunId === run.id && "border-primary bg-primary/10")}>
              <p className="font-medium">{run.month}/{run.year}</p>
              <p className="text-sm text-muted-foreground">{run.status} - {run.total_employees || run.employee_count || 0} employees</p>
            </button>
          ))}
        </CardContent>
      </Card>
      <div className="space-y-5">
        <Card>
          <CardHeader><CardTitle className="text-base">Generate Files</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {!selectedRunId && <p className="text-sm text-muted-foreground">Select a locked or paid payroll run to generate files.</p>}
            {selectedRunId && FILE_TYPES.map(([type, label]) => (
              <Button key={type} className="w-full justify-start" variant="outline" onClick={() => generate.mutate(type)} disabled={generate.isPending}>
                {generate.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FileCheck2 className="mr-2 h-4 w-4" />} {label}
              </Button>
            ))}
            {lastResult && (
              <div className="rounded-lg border p-4">
                <div className="mb-3 flex items-center gap-2"><StatusBadge status={lastResult.validation_status} /><span className="text-sm">{lastResult.row_count} rows - {money(lastResult.total_amount)}</span></div>
                {!!lastResult.errors?.length && <ErrorList errors={lastResult.errors} />}
                {!lastResult.errors?.length && <div className="flex gap-2"><Button size="sm" variant="outline" onClick={() => download(lastResult.submission_id)}>Download CSV</Button><Button size="sm" onClick={() => setAckSubmission(lastResult.submission_id)}>Mark as Submitted</Button></div>}
              </div>
            )}
          </CardContent>
        </Card>
        <HistoryTable rows={submissions.data || []} compact onMarkSubmitted={setAckSubmission} />
      </div>
      {ackSubmission && (
        <Modal title="Portal ACK Number" onClose={() => setAckSubmission(null)}>
          <div className="space-y-4">
            <Input value={ack} onChange={(e) => setAck(e.target.value)} placeholder="Acknowledgement number" />
            <div className="flex justify-end gap-2"><Button variant="outline" onClick={() => setAckSubmission(null)}>Cancel</Button><Button disabled={!ack || markSubmitted.isPending} onClick={() => markSubmitted.mutate()}>Save</Button></div>
          </div>
        </Modal>
      )}
    </div>
  );
}

function HistoryTab() {
  const [filters, setFilters] = useState({ statutory_type: "", validation_status: "" });
  const params = { statutory_type: filters.statutory_type || undefined, validation_status: filters.validation_status || undefined };
  const submissions = useQuery({ queryKey: ["statutory-submissions-all", params], queryFn: () => statutoryApi.submissions(params).then((r) => r.data as Submission[]) });
  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2">
        <select className="h-10 rounded-md border bg-background px-3 text-sm" value={filters.statutory_type} onChange={(e) => setFilters({ ...filters, statutory_type: e.target.value })}><option value="">All types</option>{["PF_ECR", "ESI", "PT", "TDS_24Q"].map((type) => <option key={type}>{type}</option>)}</select>
        <select className="h-10 rounded-md border bg-background px-3 text-sm" value={filters.validation_status} onChange={(e) => setFilters({ ...filters, validation_status: e.target.value })}><option value="">All statuses</option>{["valid", "invalid", "submitted"].map((status) => <option key={status}>{status}</option>)}</select>
      </div>
      {submissions.isLoading ? <div className="h-40 animate-pulse rounded bg-muted" /> : <HistoryTable rows={submissions.data || []} />}
    </div>
  );
}

function HistoryTable({ rows, compact, onMarkSubmitted }: { rows: Submission[]; compact?: boolean; onMarkSubmitted?: (id: number) => void }) {
  return (
    <Card>
      <CardHeader><CardTitle className="text-base">{compact ? "Previous Submissions" : "Submission History"}</CardTitle></CardHeader>
      <CardContent>
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full min-w-[840px] text-sm">
            <thead className="bg-muted/60"><tr><th className="px-3 py-2 text-left">Type</th><th className="px-3 py-2 text-left">Payroll Period</th><th className="px-3 py-2 text-left">Status</th><th className="px-3 py-2 text-left">Rows</th><th className="px-3 py-2 text-left">Amount</th><th className="px-3 py-2 text-left">Submitted At</th><th className="px-3 py-2 text-left">ACK Number</th><th className="px-3 py-2 text-right">Actions</th></tr></thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-t">
                  <td className="px-3 py-2"><TypeBadge type={row.statutory_type} /></td>
                  <td className="px-3 py-2">{row.payroll_period || row.payroll_run_id}</td>
                  <td className="px-3 py-2"><StatusBadge status={row.validation_status} />{row.validation_status === "invalid" && <Badge variant="outline" className="ml-2">{row.validation_errors_json?.length || 0} errors</Badge>}</td>
                  <td className="px-3 py-2">{row.row_count || 0}</td>
                  <td className="px-3 py-2">{money(row.total_amount)}</td>
                  <td className="px-3 py-2">{row.submitted_at ? new Date(row.submitted_at).toLocaleString("en-IN") : "-"}</td>
                  <td className="px-3 py-2">{row.portal_reference || "-"}</td>
                  <td className="px-3 py-2 text-right"><Button size="sm" variant="ghost" onClick={() => download(row.id)}><Download className="h-4 w-4" /></Button>{onMarkSubmitted && row.validation_status === "valid" && <Button size="sm" variant="outline" onClick={() => onMarkSubmitted(row.id)}>Submit</Button>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

function Summary({ label, value, className }: { label: string; value: number; className: string }) {
  return <Card><CardContent className="p-5"><div className={cn("mb-3 inline-flex rounded-lg p-2", className)}><TriangleAlert className="h-5 w-5" /></div><p className="text-2xl font-semibold">{value}</p><p className="text-sm text-muted-foreground">{label}</p></CardContent></Card>;
}

function TypeBadge({ type }: { type: string }) {
  return <Badge variant="outline">{type}</Badge>;
}

function StatusBadge({ status }: { status: string }) {
  const lower = status.toLowerCase();
  const cls = lower === "filed" || lower === "valid" || lower === "submitted" ? "bg-green-100 text-green-800" : lower === "overdue" || lower === "invalid" ? "bg-red-100 text-red-800" : "bg-yellow-100 text-yellow-800";
  return <Badge className={cn("border-0 capitalize", cls)}>{status}</Badge>;
}

function ErrorList({ errors }: { errors: Array<{ row: number; field: string; error: string }> }) {
  const [open, setOpen] = useState(false);
  return <div><Button variant="outline" size="sm" onClick={() => setOpen(!open)}>{open ? "Hide" : "Show"} validation errors</Button>{open && <div className="mt-3 max-h-52 overflow-auto rounded border p-3 text-sm">{errors.map((err, index) => <p key={index}>Row {err.row}, {err.field}: {err.error}</p>)}</div>}</div>;
}

function Modal({ title, children, onClose }: { title: string; children: React.ReactNode; onClose: () => void }) {
  return <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"><div className="w-full max-w-md rounded-lg bg-background p-5 shadow-lg"><div className="mb-4 flex items-center justify-between"><h2 className="font-semibold">{title}</h2><Button variant="ghost" size="sm" onClick={onClose}>Close</Button></div>{children}</div></div>;
}

async function download(id: number) {
  const response = await statutoryApi.downloadSubmission(id);
  const url = URL.createObjectURL(response.data);
  const link = document.createElement("a");
  link.href = url;
  link.download = `statutory_submission_${id}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}
