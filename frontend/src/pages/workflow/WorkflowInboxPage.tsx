import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, CheckCircle2, Clock3, FileCheck2, Inbox, ReceiptText } from "lucide-react";
import { Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { workflowApi } from "@/services/api";
import { formatDateTime } from "@/lib/utils";
import { useAuthStore } from "@/store/authStore";
import { getRoleKey } from "@/lib/roles";

type WorkflowItem = {
  id: string;
  source: string;
  source_id: number;
  title: string;
  requester_name?: string | null;
  status: string;
  priority: string;
  submitted_at?: string | null;
  action_url: string;
  action_label: string;
  role_scope: string;
};

type WorkflowSummary = {
  total: number;
  pending_action: number;
  submitted_by_me: number;
  by_source: Record<string, number>;
  items: WorkflowItem[];
};

const sourceIcon: Record<string, React.ElementType> = {
  leave: Clock3,
  timesheet: FileCheck2,
  attendance: CheckCircle2,
  reimbursement: ReceiptText,
  payroll: ReceiptText,
};

function statusTone(status: string) {
  if (["Approved", "Locked", "Paid"].includes(status)) return "bg-green-100 text-green-800";
  if (["Rejected", "Cancelled"].includes(status)) return "bg-red-100 text-red-800";
  if (["Completed", "Submitted", "Pending"].includes(status)) return "bg-amber-100 text-amber-800";
  return "bg-muted text-muted-foreground";
}

export default function WorkflowInboxPage() {
  const { user } = useAuthStore();
  const roleKey = getRoleKey(user?.role, user?.is_superuser);
  const [mine, setMine] = useState(roleKey === "employee");

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["workflow-inbox", mine],
    queryFn: () => workflowApi.inbox(mine).then((response) => response.data as WorkflowSummary),
  });

  const sourceRows = useMemo(() => Object.entries(data?.by_source || {}), [data]);

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 rounded-lg border bg-card p-5 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            {roleKey === "employee" ? "Employee self service" : "Approvals"}
          </p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight">
            {roleKey === "employee" ? "My requests" : "Workflow inbox"}
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {roleKey === "employee"
              ? "Track leave, timesheets, reimbursements, and submitted HR requests."
              : "Review leave, timesheets, attendance, reimbursements, and payroll actions from one queue."}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {roleKey !== "employee" && (
            <Button variant={mine ? "outline" : "default"} onClick={() => setMine(false)}>
              Team queue
            </Button>
          )}
          <Button variant={mine ? "default" : "outline"} onClick={() => setMine(true)}>
            My submissions
          </Button>
          <Button variant="outline" onClick={() => refetch()}>
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="p-5">
            <Inbox className="mb-3 h-5 w-5 text-primary" />
            <p className="text-2xl font-semibold">{isLoading ? "-" : data?.total ?? 0}</p>
            <p className="text-sm text-muted-foreground">Total items</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <Clock3 className="mb-3 h-5 w-5 text-amber-600" />
            <p className="text-2xl font-semibold">{isLoading ? "-" : data?.pending_action ?? 0}</p>
            <p className="text-sm text-muted-foreground">Pending action</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <FileCheck2 className="mb-3 h-5 w-5 text-green-600" />
            <p className="text-2xl font-semibold">{isLoading ? "-" : data?.submitted_by_me ?? 0}</p>
            <p className="text-sm text-muted-foreground">Submitted by me</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-5 lg:grid-cols-[0.75fr_1.25fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Queue Mix</CardTitle>
            <CardDescription>Grouped by workflow source</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {sourceRows.length === 0 ? (
              <p className="text-sm text-muted-foreground">No active workflow items.</p>
            ) : (
              sourceRows.map(([source, count]) => {
                const Icon = sourceIcon[source] || Inbox;
                return (
                  <div key={source} className="flex items-center justify-between rounded-lg border p-3">
                    <span className="flex items-center gap-3 text-sm font-medium capitalize">
                      <Icon className="h-4 w-4 text-primary" />
                      {source}
                    </span>
                    <Badge variant="outline">{count}</Badge>
                  </div>
                );
              })
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Items</CardTitle>
            <CardDescription>{mine ? "Your submitted requests" : "Requests waiting for review"}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {isLoading ? (
              <div className="h-24 rounded-lg border bg-muted/30" />
            ) : data?.items.length ? (
              data.items.map((item) => {
                const Icon = sourceIcon[item.source] || Inbox;
                return (
                  <div key={item.id} className="flex flex-col gap-3 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex min-w-0 gap-3">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <Icon className="h-5 w-5" />
                      </div>
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="font-medium">{item.title}</p>
                          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusTone(item.status)}`}>
                            {item.status}
                          </span>
                          {item.priority === "High" && <Badge variant="destructive">High</Badge>}
                        </div>
                        <p className="mt-1 text-sm text-muted-foreground">
                          {item.requester_name || "System"} • {formatDateTime(item.submitted_at || null)}
                        </p>
                      </div>
                    </div>
                    <Button asChild variant="outline" size="sm">
                      <Link to={item.action_url}>
                        {item.action_label}
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                );
              })
            ) : (
              <p className="rounded-lg border p-4 text-sm text-muted-foreground">No workflow items found.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
