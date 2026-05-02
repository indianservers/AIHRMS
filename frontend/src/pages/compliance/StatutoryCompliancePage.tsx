import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CalendarClock, FileCheck2, Landmark, Plus, RefreshCw, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { statutoryComplianceApi } from "@/services/api";
import { toast } from "@/hooks/use-toast";

type ComplianceEvent = {
  id: number;
  legal_entity_id: number;
  compliance_type: string;
  due_date: string;
  period_month?: number;
  period_year?: number;
  financial_year?: string;
  status: string;
  remarks?: string;
};

type LegalEntity = {
  id: number;
  legal_name: string;
  pan?: string;
  tan?: string;
  pf_establishment_code?: string;
  esi_employer_code?: string;
};

type PortalSubmission = {
  id: number;
  portal_type: string;
  period_month: number;
  period_year: number;
  status: string;
  acknowledgement_number?: string;
};

type Form16 = {
  id: number;
  employee_id: number;
  financial_year: string;
  status: string;
};

export default function StatutoryCompliancePage() {
  useEffect(() => { document.title = "Statutory Compliance · AI HRMS"; }, []);
  const qc = useQueryClient();
  const [showEventForm, setShowEventForm] = useState(false);
  const [eventForm, setEventForm] = useState({
    legal_entity_id: "",
    compliance_type: "TDS",
    period_month: String(new Date().getMonth() + 1),
    period_year: String(new Date().getFullYear()),
    financial_year: "2026-27",
    due_date: "",
    remarks: "",
  });

  const { data: entities } = useQuery({
    queryKey: ["statutory-legal-entities"],
    queryFn: () => statutoryComplianceApi.legalEntities().then((r) => r.data as LegalEntity[]),
  });
  const { data: events, isLoading } = useQuery({
    queryKey: ["statutory-calendar"],
    queryFn: () => statutoryComplianceApi.calendar().then((r) => r.data as ComplianceEvent[]),
  });
  const { data: form16 } = useQuery({
    queryKey: ["statutory-form16"],
    queryFn: () => statutoryComplianceApi.form16().then((r) => r.data as Form16[]),
  });
  const { data: submissions } = useQuery({
    queryKey: ["statutory-submissions"],
    queryFn: () => statutoryComplianceApi.portalSubmissions().then((r) => r.data as PortalSubmission[]),
  });

  const createEvent = useMutation({
    mutationFn: () =>
      statutoryComplianceApi.createCalendarEvent({
        legal_entity_id: Number(eventForm.legal_entity_id),
        compliance_type: eventForm.compliance_type,
        period_month: Number(eventForm.period_month),
        period_year: Number(eventForm.period_year),
        financial_year: eventForm.financial_year || undefined,
        due_date: eventForm.due_date,
        remarks: eventForm.remarks || undefined,
      }),
    onSuccess: () => {
      toast({ title: "Compliance event created" });
      setShowEventForm(false);
      setEventForm({
        legal_entity_id: "",
        compliance_type: "TDS",
        period_month: String(new Date().getMonth() + 1),
        period_year: String(new Date().getFullYear()),
        financial_year: "2026-27",
        due_date: "",
        remarks: "",
      });
      qc.invalidateQueries({ queryKey: ["statutory-calendar"] });
    },
    onError: () => toast({ title: "Unable to create compliance event", variant: "destructive" }),
  });

  const updateEvent = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) => statutoryComplianceApi.updateCalendarEvent(id, { status }),
    onSuccess: () => {
      toast({ title: "Compliance status updated" });
      qc.invalidateQueries({ queryKey: ["statutory-calendar"] });
    },
  });

  const overdue = (events || []).filter((event) => event.status !== "Completed" && new Date(event.due_date) < new Date()).length;
  const dueThisWeek = (events || []).filter((event) => {
    const due = new Date(event.due_date).getTime();
    const now = Date.now();
    return event.status !== "Completed" && due >= now && due <= now + 7 * 86400000;
  }).length;
  const formatPeriod = (event: ComplianceEvent) => {
    if (event.period_month && event.period_year) return `${event.period_month}/${event.period_year}`;
    return event.financial_year || "Unspecified period";
  };

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 rounded-lg border bg-card p-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="page-title">Statutory Compliance</h1>
          <p className="page-description">Track PF, ESI, PT, TDS, Form 16, 24Q, challans, and portal submissions.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => qc.invalidateQueries({ queryKey: ["statutory-calendar"] })}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button size="sm" onClick={() => setShowEventForm((value) => !value)}>
            <Plus className="mr-2 h-4 w-4" />
            New Due Date
          </Button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { label: "Legal Entities", value: entities?.length || 0, icon: Landmark },
          { label: "Due This Week", value: dueThisWeek, icon: CalendarClock },
          { label: "Overdue", value: overdue, icon: FileCheck2 },
          { label: "Portal Submissions", value: submissions?.length || 0, icon: Send },
        ].map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.label}>
              <CardContent className="p-5">
                <Icon className="mb-3 h-5 w-5 text-primary" />
                <p className="text-2xl font-semibold">{item.value}</p>
                <p className="text-sm text-muted-foreground">{item.label}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {showEventForm && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Create Compliance Due Date</CardTitle>
            <CardDescription>Use this calendar to drive alerts and owner follow-up.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-3">
            <div className="space-y-1.5">
              <Label>Legal Entity</Label>
              <select className="h-10 w-full rounded-md border bg-background px-3 text-sm" value={eventForm.legal_entity_id} onChange={(e) => setEventForm({ ...eventForm, legal_entity_id: e.target.value })}>
                <option value="">Select entity</option>
                {(entities || []).map((entity) => <option key={entity.id} value={entity.id}>{entity.legal_name}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <Label>Type</Label>
              <select className="h-10 w-full rounded-md border bg-background px-3 text-sm" value={eventForm.compliance_type} onChange={(e) => setEventForm({ ...eventForm, compliance_type: e.target.value })}>
                {["PF", "ESI", "PT", "TDS", "LWF", "Gratuity"].map((type) => <option key={type}>{type}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <Label>Financial Year</Label>
              <Input value={eventForm.financial_year} onChange={(e) => setEventForm({ ...eventForm, financial_year: e.target.value })} placeholder="2026-27" />
            </div>
            <div className="space-y-1.5">
              <Label>Period Month</Label>
              <Input type="number" min="1" max="12" value={eventForm.period_month} onChange={(e) => setEventForm({ ...eventForm, period_month: e.target.value })} />
            </div>
            <div className="space-y-1.5">
              <Label>Period Year</Label>
              <Input type="number" value={eventForm.period_year} onChange={(e) => setEventForm({ ...eventForm, period_year: e.target.value })} />
            </div>
            <div className="space-y-1.5">
              <Label>Due Date</Label>
              <Input type="date" value={eventForm.due_date} onChange={(e) => setEventForm({ ...eventForm, due_date: e.target.value })} />
            </div>
            <div className="space-y-1.5 sm:col-span-3">
              <Label>Remarks</Label>
              <Input value={eventForm.remarks} onChange={(e) => setEventForm({ ...eventForm, remarks: e.target.value })} placeholder="24Q filing, challan payment, or portal upload" />
            </div>
            <div className="flex gap-2 sm:col-span-3">
              <Button disabled={!eventForm.legal_entity_id || !eventForm.due_date || createEvent.isPending} onClick={() => createEvent.mutate()}>
                Save Due Date
              </Button>
              <Button variant="outline" onClick={() => setShowEventForm(false)}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Compliance Calendar</CardTitle>
            <CardDescription>Open statutory obligations by due date.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {isLoading ? <div className="h-24 rounded-lg bg-muted/40" /> : events?.length ? events.map((event) => (
              <div key={event.id} className="grid gap-3 rounded-lg border p-4 sm:grid-cols-[1fr_auto] sm:items-center">
                <div>
                  <p className="font-medium">{event.compliance_type} compliance</p>
                  <p className="text-sm text-muted-foreground">{formatPeriod(event)} - due {event.due_date}{event.remarks ? ` - ${event.remarks}` : ""}</p>
                </div>
                <div className="flex flex-wrap gap-2 sm:justify-end">
                  <span className="rounded-full bg-muted px-2 py-0.5 text-xs">{event.status}</span>
                  {event.status !== "Completed" && (
                    <Button variant="outline" size="sm" onClick={() => updateEvent.mutate({ id: event.id, status: "Completed" })}>
                      Mark Done
                    </Button>
                  )}
                </div>
              </div>
            )) : <p className="rounded-lg border p-4 text-sm text-muted-foreground">No compliance due dates configured.</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Filing Snapshot</CardTitle>
            <CardDescription>Form 16 and portal submission tracking.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {(form16 || []).slice(0, 4).map((doc) => (
              <div key={`f16-${doc.id}`} className="rounded-lg border p-3">
                <p className="text-sm font-medium">Form 16 - {doc.financial_year}</p>
                <p className="mt-1 text-sm text-muted-foreground">Employee #{doc.employee_id} - {doc.status}</p>
              </div>
            ))}
            {(submissions || []).slice(0, 4).map((row) => (
              <div key={`sub-${row.id}`} className="rounded-lg border p-3">
                <p className="text-sm font-medium">{row.portal_type} - {row.period_month}/{row.period_year}</p>
                <p className="mt-1 text-sm text-muted-foreground">{row.status}{row.acknowledgement_number ? ` - ${row.acknowledgement_number}` : ""}</p>
              </div>
            ))}
            {!form16?.length && !submissions?.length && <p className="rounded-lg border p-4 text-sm text-muted-foreground">No filings or portal submissions yet.</p>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
