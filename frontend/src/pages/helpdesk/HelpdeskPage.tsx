import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  LifeBuoy, Plus, MessageSquare, RefreshCw, Send, ChevronDown
} from "lucide-react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { helpdeskApi } from "@/services/api";
import { formatDateTime, statusColor } from "@/lib/utils";
import { toast } from "@/hooks/use-toast";

interface Ticket {
  id: number;
  ticket_number: string;
  subject: string;
  description: string;
  category?: { name: string };
  priority: string;
  status: string;
  created_at: string;
  updated_at: string;
}

interface Reply {
  id: number;
  message: string;
  is_internal: boolean;
  created_at: string;
  author?: { first_name: string; last_name: string };
}

interface TicketForm {
  subject: string;
  description: string;
  priority: string;
  category_id?: number;
}

const PRIORITIES = ["Low", "Medium", "High", "Critical"];
const STATUSES = ["Open", "In Progress", "Resolved", "Closed"];

export default function HelpdeskPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);
  const [replyText, setReplyText] = useState("");
  const [statusFilter, setStatusFilter] = useState("Open");

  const { data: tickets, isLoading, refetch } = useQuery({
    queryKey: ["tickets", statusFilter],
    queryFn: () =>
      helpdeskApi.tickets({ status: statusFilter || undefined }).then((r) => r.data),
  });

  const { data: categories } = useQuery({
    queryKey: ["helpdesk-categories"],
    queryFn: () => helpdeskApi.categories().then((r) => r.data),
  });

  const { data: replies, refetch: refetchReplies } = useQuery({
    queryKey: ["ticket-replies", selectedTicket?.id],
    queryFn: () => helpdeskApi.getReplies(selectedTicket!.id).then((r) => r.data),
    enabled: !!selectedTicket,
  });

  const { register, handleSubmit, reset, formState: { errors } } = useForm<TicketForm>({
    defaultValues: { priority: "Medium" },
  });

  const createMutation = useMutation({
    mutationFn: (data: TicketForm) =>
      helpdeskApi.createTicket({
        subject: data.subject,
        description: data.description,
        priority: data.priority,
        category_id: data.category_id,
      }),
    onSuccess: () => {
      toast({ title: "Ticket raised successfully!" });
      reset();
      setShowForm(false);
      refetch();
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Failed";
      toast({ title: "Error", description: msg, variant: "destructive" });
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      helpdeskApi.updateStatus(id, status),
    onSuccess: (_, { status }) => {
      toast({ title: `Ticket ${status}` });
      refetch();
      if (selectedTicket) {
        setSelectedTicket((t) => t ? { ...t, status } : null);
      }
    },
  });

  const replyMutation = useMutation({
    mutationFn: (message: string) =>
      helpdeskApi.addReply(selectedTicket!.id, message),
    onSuccess: () => {
      setReplyText("");
      refetchReplies();
    },
    onError: () => toast({ title: "Failed to send reply", variant: "destructive" }),
  });

  const priorityBadge: Record<string, string> = {
    Low: "bg-green-100 text-green-800",
    Medium: "bg-yellow-100 text-yellow-800",
    High: "bg-orange-100 text-orange-800",
    Critical: "bg-red-100 text-red-800",
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Helpdesk</h1>
          <p className="page-description">Raise and track support tickets.</p>
        </div>
        <Button size="sm" onClick={() => setShowForm((v) => !v)}>
          <Plus className="h-4 w-4 mr-2" />
          New Ticket
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {STATUSES.map((s) => (
          <Card key={s}>
            <CardContent className="p-4 text-center">
              <p className="text-2xl font-bold">
                {(tickets as Ticket[])?.filter((t) => t.status === s).length ?? 0}
              </p>
              <p className="text-xs text-muted-foreground mt-1">{s}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Create ticket form */}
      {showForm && (
        <Card>
          <CardHeader><CardTitle className="text-base">Raise a Ticket</CardTitle></CardHeader>
          <CardContent>
            <form
              onSubmit={handleSubmit((data) => createMutation.mutate(data))}
              className="grid grid-cols-1 sm:grid-cols-2 gap-4"
            >
              <div className="sm:col-span-2 space-y-1.5">
                <Label>Subject *</Label>
                <Input {...register("subject", { required: "Required" })} placeholder="Brief description of the issue" />
                {errors.subject && <p className="text-xs text-red-500">{errors.subject.message}</p>}
              </div>
              <div className="space-y-1.5">
                <Label>Category</Label>
                <select
                  {...register("category_id")}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">Select category</option>
                  {(categories as { id: number; name: string }[])?.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Priority</Label>
                <select
                  {...register("priority")}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  {PRIORITIES.map((p) => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
              <div className="sm:col-span-2 space-y-1.5">
                <Label>Description *</Label>
                <textarea
                  {...register("description", { required: "Required" })}
                  rows={4}
                  className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none"
                  placeholder="Describe your issue in detail..."
                />
                {errors.description && <p className="text-xs text-red-500">{errors.description.message}</p>}
              </div>
              <div className="sm:col-span-2 flex gap-3">
                <Button type="submit" disabled={createMutation.isPending}>
                  {createMutation.isPending ? "Submitting..." : "Raise Ticket"}
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Ticket list */}
        <div className="lg:col-span-1 space-y-4">
          <div className="flex gap-2">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="flex h-9 flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="">All</option>
              {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
            <Button variant="ghost" size="icon" className="h-9 w-9" onClick={() => refetch()}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>

          <div className="space-y-2">
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <Card key={i}><CardContent className="p-4"><div className="h-16 skeleton rounded" /></CardContent></Card>
              ))
            ) : !(tickets as Ticket[])?.length ? (
              <Card>
                <CardContent className="p-8 text-center text-muted-foreground">
                  <LifeBuoy className="h-8 w-8 mx-auto mb-2 opacity-30" />
                  <p className="text-sm">No tickets found</p>
                </CardContent>
              </Card>
            ) : (
              (tickets as Ticket[]).map((t) => (
                <Card
                  key={t.id}
                  className={`cursor-pointer hover:shadow-md transition-shadow ${selectedTicket?.id === t.id ? "ring-2 ring-primary" : ""}`}
                  onClick={() => setSelectedTicket(selectedTicket?.id === t.id ? null : t)}
                >
                  <CardContent className="p-4 space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-medium leading-tight">{t.subject}</p>
                      <span className={`shrink-0 inline-flex items-center rounded-full px-1.5 py-0.5 text-xs font-medium ${priorityBadge[t.priority] || ""}`}>
                        {t.priority}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-muted-foreground">{t.ticket_number}</span>
                      <span className={`inline-flex items-center rounded-full px-1.5 py-0.5 text-xs font-medium ${statusColor(t.status)}`}>
                        {t.status}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">{formatDateTime(t.created_at)}</p>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </div>

        {/* Ticket detail */}
        <div className="lg:col-span-2">
          {!selectedTicket ? (
            <Card className="h-full">
              <CardContent className="flex h-64 items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <MessageSquare className="h-10 w-10 mx-auto mb-3 opacity-30" />
                  <p>Select a ticket to view details</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <CardTitle className="text-base">{selectedTicket.subject}</CardTitle>
                    <CardDescription>{selectedTicket.ticket_number} · {selectedTicket.category?.name}</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <select
                      value={selectedTicket.status}
                      onChange={(e) => updateStatusMutation.mutate({ id: selectedTicket.id, status: e.target.value })}
                      className="text-xs h-8 rounded border border-input bg-background px-2"
                    >
                      {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Description */}
                <div className="p-4 bg-muted/30 rounded-lg">
                  <p className="text-sm">{selectedTicket.description}</p>
                  <p className="text-xs text-muted-foreground mt-2">{formatDateTime(selectedTicket.created_at)}</p>
                </div>

                {/* Replies */}
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold">Conversation</h3>
                  {(replies as Reply[])?.map((r) => (
                    <div
                      key={r.id}
                      className={`p-3 rounded-lg text-sm ${
                        r.is_internal
                          ? "bg-yellow-50 border border-yellow-200 dark:bg-yellow-900/20"
                          : "bg-muted/40"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-xs">
                          {r.author ? `${r.author.first_name} ${r.author.last_name}` : "System"}
                          {r.is_internal && <span className="ml-1 text-yellow-600">(Internal)</span>}
                        </span>
                        <span className="text-xs text-muted-foreground">{formatDateTime(r.created_at)}</span>
                      </div>
                      <p>{r.message}</p>
                    </div>
                  ))}
                </div>

                {/* Reply input */}
                {selectedTicket.status !== "Closed" && (
                  <div className="flex gap-2">
                    <Input
                      value={replyText}
                      onChange={(e) => setReplyText(e.target.value)}
                      placeholder="Type a reply..."
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey && replyText.trim()) {
                          e.preventDefault();
                          replyMutation.mutate(replyText.trim());
                        }
                      }}
                    />
                    <Button
                      size="icon"
                      disabled={!replyText.trim() || replyMutation.isPending}
                      onClick={() => replyText.trim() && replyMutation.mutate(replyText.trim())}
                    >
                      <Send className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
