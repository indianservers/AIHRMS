import { useQuery } from "@tanstack/react-query";

import { CalendarDays, Clock, Download, FileText, HelpCircle, Laptop, Target, Ticket, UserRound } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { employeeApi, leaveApi, reportsApi } from "@/services/api";
import { usePageTitle } from "@/hooks/use-page-title";
import { assetUrl, formatCurrency, formatDate } from "@/lib/utils";

export default function ESSPortalPage() {
  usePageTitle("ESS Portal");
  const completeness = useQuery({ queryKey: ["profile-completeness"], queryFn: () => employeeApi.profileCompleteness().then((r) => r.data), retry: false });
  const summary = useQuery({ queryKey: ["ess-summary"], queryFn: () => reportsApi.essSummary().then((r) => r.data), retry: false });
  const leaveBalance = useQuery({ queryKey: ["ess-leave-balance"], queryFn: () => leaveApi.balance(new Date().getFullYear()).then((r) => r.data), retry: false });

  const actions = [
    ["Profile", "Photo, data completeness, change requests", UserRound, "/profile"],
    ["Apply Leave", "Request leave and track approvals", CalendarDays, "/leave"],
    ["Attendance", "Monthly view and regularization", Clock, "/attendance"],
    ["Helpdesk", "Raise HR or IT support ticket", HelpCircle, "/helpdesk"],
  ];

  return (
    <div className="space-y-4 sm:space-y-5">
      <div className="rounded-lg border bg-card p-4 sm:p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Employee Self Service</p>
        <h1 className="mt-2 text-xl font-semibold tracking-tight sm:text-2xl">ESS Portal</h1>
        <p className="mt-1 text-sm text-muted-foreground">Payslips, leave, attendance, documents, goals, tickets, and assigned assets.</p>
      </div>

      <div className="grid gap-3 sm:gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardContent className="p-4 sm:p-5">
            <div className="mb-2 flex justify-between text-sm"><span>Profile completeness</span><span className="font-semibold">{completeness.data?.percent ?? 0}%</span></div>
            <div className="h-2 rounded-full bg-muted"><div className="h-2 rounded-full bg-primary" style={{ width: `${completeness.data?.percent ?? 0}%` }} /></div>
            {!!completeness.data?.missing?.length && <p className="mt-3 text-xs text-muted-foreground">Missing: {completeness.data.missing.slice(0, 5).join(", ")}</p>}
          </CardContent>
        </Card>
        <Card>
          <CardContent className="grid grid-cols-1 gap-3 p-4 sm:grid-cols-2 sm:p-5">
            {(leaveBalance.data || []).slice(0, 4).map((item: any) => (
              <div key={item.id} className="rounded-lg border p-3">
                <p className="text-xs text-muted-foreground">{item.leave_type?.code || item.leave_type_id}</p>
                <p className="text-xl font-semibold">{item.available ?? item.allocated}</p>
              </div>
            ))}
            {!leaveBalance.data?.length && <p className="col-span-2 text-sm text-muted-foreground">No leave balances assigned yet.</p>}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {actions.map(([label, detail, Icon, href]) => (
          <a key={label as string} href={href as string} className="rounded-lg border bg-card p-4 shadow-sm transition hover:border-primary/50 hover:shadow-md sm:p-5">
            <Icon className="mb-4 h-5 w-5 text-primary" />
            <p className="font-medium">{label as string}</p>
            <p className="mt-1 text-sm text-muted-foreground">{detail as string}</p>
          </a>
        ))}
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="text-base">My Payslips</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {(summary.data?.payslips || []).map((item: any) => (
              <div key={item.record_id} className="flex flex-col gap-3 rounded-lg border p-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-medium">{item.month}/{item.year}</p>
                  <p className="text-xs text-muted-foreground">Net {formatCurrency(Number(item.net_salary || 0))}</p>
                </div>
                {item.pdf_url ? <Button asChild variant="outline" size="sm"><a href={assetUrl(item.pdf_url)} target="_blank" rel="noreferrer"><Download className="h-4 w-4" />PDF</a></Button> : <Badge variant="outline">No PDF</Badge>}
              </div>
            ))}
            {!summary.data?.payslips?.length && <p className="rounded-lg border p-4 text-sm text-muted-foreground">No payslips available yet.</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">My Documents</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {(summary.data?.documents || []).map((item: any) => (
              <div key={item.id} className="flex flex-col gap-3 rounded-lg border p-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-medium">{item.document_name || item.document_type}</p>
                  <p className="text-xs text-muted-foreground">{item.document_type}</p>
                </div>
                {item.file_url && <Button asChild variant="outline" size="sm"><a href={assetUrl(item.file_url)} target="_blank" rel="noreferrer"><FileText className="h-4 w-4" />Open</a></Button>}
              </div>
            ))}
            {!summary.data?.documents?.length && <p className="rounded-lg border p-4 text-sm text-muted-foreground">No generated documents yet.</p>}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 xl:grid-cols-3">
        <Card>
          <CardHeader><CardTitle className="text-base"><Target className="mr-2 inline h-4 w-4" />Goals & Appraisal</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {(summary.data?.goals || []).slice(0, 5).map((item: any) => (
              <div key={item.id} className="rounded-lg border p-3">
                <p className="text-sm font-medium">{item.title}</p>
                <p className="text-xs text-muted-foreground">{item.status} â€¢ target {formatDate(item.target_date)}</p>
              </div>
            ))}
            {(summary.data?.reviews || []).slice(0, 3).map((item: any) => <Badge key={item.id} variant="outline">{item.review_type}: {item.status}</Badge>)}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base"><Ticket className="mr-2 inline h-4 w-4" />Helpdesk</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">Raise HR, payroll, IT, document, or asset support requests and track replies.</p>
            <Button asChild><a href="/helpdesk"><HelpCircle className="h-4 w-4" />Raise ticket</a></Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base"><Laptop className="mr-2 inline h-4 w-4" />IT Assets</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {(summary.data?.assets || []).map((item: any) => (
              <div key={item.id} className="rounded-lg border p-3">
                <p className="text-sm font-medium">{item.name || "Asset"} <span className="text-muted-foreground">({item.asset_tag})</span></p>
                <p className="text-xs text-muted-foreground">Assigned {formatDate(item.assigned_date)} â€¢ {item.condition || "Good"}</p>
              </div>
            ))}
            {!summary.data?.assets?.length && <p className="text-sm text-muted-foreground">No active asset assignments.</p>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
