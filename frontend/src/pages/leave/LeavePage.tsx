import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  CalendarDays, Plus, CheckCircle2, XCircle, Clock, RefreshCw
} from "lucide-react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { leaveApi } from "@/services/api";
import { formatDate, statusColor } from "@/lib/utils";
import { toast } from "@/hooks/use-toast";

interface LeaveType {
  id: number;
  name: string;
  color?: string;
}

interface LeaveBalance {
  leave_type_id: number;
  leave_type: LeaveType;
  allocated: number;
  used: number;
  pending: number;
  available: number;
}

interface LeaveRequest {
  id: number;
  leave_type: LeaveType;
  from_date: string;
  to_date: string;
  days_requested: number;
  reason: string;
  status: string;
  applied_on: string;
  review_remarks?: string;
}

interface ApplyForm {
  leave_type_id: number;
  from_date: string;
  to_date: string;
  reason: string;
  leave_mode?: string;
}

export default function LeavePage() {
  const qc = useQueryClient();
  const [showApplyForm, setShowApplyForm] = useState(false);
  const [activeTab, setActiveTab] = useState<"my" | "approvals">("my");

  const { data: balances, isLoading: loadingBalance } = useQuery({
    queryKey: ["leave-balance"],
    queryFn: () => leaveApi.balance().then((r) => r.data),
  });

  const { data: myRequests, isLoading: loadingRequests, refetch } = useQuery({
    queryKey: ["my-leave-requests"],
    queryFn: () => leaveApi.myRequests().then((r) => r.data),
  });

  const { data: allRequests, refetch: refetchAll } = useQuery({
    queryKey: ["all-leave-requests", "Pending"],
    queryFn: () => leaveApi.allRequests({ status: "Pending" }).then((r) => r.data),
    retry: false,
  });

  const { data: leaveTypes } = useQuery({
    queryKey: ["leave-types"],
    queryFn: () => leaveApi.types().then((r) => r.data),
  });

  const { register, handleSubmit, reset, formState: { errors } } = useForm<ApplyForm>();

  const applyMutation = useMutation({
    mutationFn: (data: ApplyForm) =>
      leaveApi.apply({ ...data, leave_type_id: Number(data.leave_type_id) }),
    onSuccess: () => {
      toast({ title: "Leave application submitted!" });
      reset();
      setShowApplyForm(false);
      qc.invalidateQueries({ queryKey: ["leave-balance"] });
      qc.invalidateQueries({ queryKey: ["my-leave-requests"] });
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Failed to apply";
      toast({ title: "Error", description: msg, variant: "destructive" });
    },
  });

  const approveMutation = useMutation({
    mutationFn: ({ id, status, remarks }: { id: number; status: string; remarks?: string }) =>
      leaveApi.approve(id, { status, review_remarks: remarks }),
    onSuccess: (_, { status }) => {
      toast({ title: `Leave ${status}` });
      refetchAll();
    },
    onError: () => toast({ title: "Action failed", variant: "destructive" }),
  });

  const cancelMutation = useMutation({
    mutationFn: (id: number) => leaveApi.cancel(id),
    onSuccess: () => {
      toast({ title: "Leave cancelled" });
      refetch();
      qc.invalidateQueries({ queryKey: ["leave-balance"] });
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Leave Management</h1>
          <p className="page-description">Apply for leaves, track balances, and manage approvals.</p>
        </div>
        <Button size="sm" onClick={() => setShowApplyForm((v) => !v)}>
          <Plus className="h-4 w-4 mr-2" />
          Apply Leave
        </Button>
      </div>

      {/* Leave balance cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        {loadingBalance
          ? Array.from({ length: 4 }).map((_, i) => (
              <Card key={i}><CardContent className="p-4"><div className="h-12 skeleton rounded" /></CardContent></Card>
            ))
          : (balances as LeaveBalance[])?.map((b) => (
              <Card key={b.leave_type_id}>
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground truncate">{b.leave_type?.name}</p>
                  <p className="text-2xl font-bold mt-1">{Number(b.available).toFixed(1)}</p>
                  <p className="text-xs text-muted-foreground">of {Number(b.allocated).toFixed(1)} available</p>
                  <div className="mt-2 h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full"
                      style={{ width: `${Math.min(100, (Number(b.available) / Number(b.allocated)) * 100)}%` }}
                    />
                  </div>
                </CardContent>
              </Card>
            ))}
      </div>

      {/* Apply leave form */}
      {showApplyForm && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Apply for Leave</CardTitle>
          </CardHeader>
          <CardContent>
            <form
              onSubmit={handleSubmit((data) => applyMutation.mutate(data))}
              className="grid grid-cols-1 sm:grid-cols-2 gap-4"
            >
              <div className="space-y-1.5">
                <Label>Leave Type *</Label>
                <select
                  {...register("leave_type_id", { required: "Required" })}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">Select leave type</option>
                  {(leaveTypes as LeaveType[])?.map((t) => (
                    <option key={t.id} value={t.id}>{t.name}</option>
                  ))}
                </select>
                {errors.leave_type_id && <p className="text-xs text-red-500">{errors.leave_type_id.message}</p>}
              </div>

              <div className="space-y-1.5">
                <Label>Mode</Label>
                <select
                  {...register("leave_mode")}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="Full-day">Full Day</option>
                  <option value="Half-day">Half Day</option>
                </select>
              </div>

              <div className="space-y-1.5">
                <Label>From Date *</Label>
                <Input type="date" {...register("from_date", { required: "Required" })} />
                {errors.from_date && <p className="text-xs text-red-500">{errors.from_date.message}</p>}
              </div>

              <div className="space-y-1.5">
                <Label>To Date *</Label>
                <Input type="date" {...register("to_date", { required: "Required" })} />
                {errors.to_date && <p className="text-xs text-red-500">{errors.to_date.message}</p>}
              </div>

              <div className="sm:col-span-2 space-y-1.5">
                <Label>Reason *</Label>
                <textarea
                  {...register("reason", { required: "Required" })}
                  rows={3}
                  className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none"
                  placeholder="Reason for leave..."
                />
                {errors.reason && <p className="text-xs text-red-500">{errors.reason.message}</p>}
              </div>

              <div className="sm:col-span-2 flex gap-3">
                <Button type="submit" disabled={applyMutation.isPending}>
                  {applyMutation.isPending ? "Submitting..." : "Submit Application"}
                </Button>
                <Button type="button" variant="outline" onClick={() => setShowApplyForm(false)}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        {(["my", "approvals"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab === "my" ? "My Requests" : "Pending Approvals"}
            {tab === "approvals" && Array.isArray(allRequests) && allRequests.length > 0 && (
              <span className="ml-2 inline-flex items-center justify-center rounded-full bg-primary text-primary-foreground text-xs h-4 min-w-4 px-1">
                {allRequests.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {activeTab === "my" && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">My Leave Requests</CardTitle>
              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => refetch()}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b bg-muted/50">
                  <tr>
                    {["Type", "From", "To", "Days", "Reason", "Applied On", "Status", ""].map((h) => (
                      <th key={h} className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {loadingRequests ? (
                    Array.from({ length: 5 }).map((_, i) => (
                      <tr key={i} className="border-b">
                        <td colSpan={8} className="px-4 py-3"><div className="h-4 skeleton rounded" /></td>
                      </tr>
                    ))
                  ) : !myRequests || (myRequests as LeaveRequest[]).length === 0 ? (
                    <tr>
                      <td colSpan={8} className="px-4 py-10 text-center text-muted-foreground">
                        <CalendarDays className="h-8 w-8 mx-auto mb-2 opacity-30" />
                        No leave requests yet
                      </td>
                    </tr>
                  ) : (
                    (myRequests as LeaveRequest[]).map((r) => (
                      <tr key={r.id} className="border-b hover:bg-muted/30">
                        <td className="px-4 py-3 font-medium">{r.leave_type?.name}</td>
                        <td className="px-4 py-3">{formatDate(r.from_date)}</td>
                        <td className="px-4 py-3">{formatDate(r.to_date)}</td>
                        <td className="px-4 py-3 text-center">{r.days_requested}</td>
                        <td className="px-4 py-3 max-w-[160px] truncate text-muted-foreground">{r.reason}</td>
                        <td className="px-4 py-3 text-muted-foreground">{formatDate(r.applied_on)}</td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${statusColor(r.status)}`}>
                            {r.status}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          {r.status === "Pending" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-red-500 hover:text-red-700 text-xs h-7"
                              onClick={() => cancelMutation.mutate(r.id)}
                            >
                              Cancel
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === "approvals" && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Pending Approvals</CardTitle>
              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => refetchAll()}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="border-b bg-muted/50">
                  <tr>
                    {["Employee", "Type", "From", "To", "Days", "Reason", "Actions"].map((h) => (
                      <th key={h} className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {!allRequests || (allRequests as (LeaveRequest & { employee?: { first_name: string; last_name: string } })[]).length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-4 py-10 text-center text-muted-foreground">
                        <CheckCircle2 className="h-8 w-8 mx-auto mb-2 opacity-30" />
                        No pending approvals
                      </td>
                    </tr>
                  ) : (
                    (allRequests as (LeaveRequest & { employee?: { first_name: string; last_name: string } })[]).map((r) => (
                      <tr key={r.id} className="border-b hover:bg-muted/30">
                        <td className="px-4 py-3 font-medium">
                          {r.employee ? `${r.employee.first_name} ${r.employee.last_name}` : "—"}
                        </td>
                        <td className="px-4 py-3">{r.leave_type?.name}</td>
                        <td className="px-4 py-3">{formatDate(r.from_date)}</td>
                        <td className="px-4 py-3">{formatDate(r.to_date)}</td>
                        <td className="px-4 py-3 text-center">{r.days_requested}</td>
                        <td className="px-4 py-3 max-w-[160px] truncate text-muted-foreground">{r.reason}</td>
                        <td className="px-4 py-3">
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              className="bg-green-600 hover:bg-green-700 text-white h-7 text-xs"
                              onClick={() => approveMutation.mutate({ id: r.id, status: "Approved" })}
                              disabled={approveMutation.isPending}
                            >
                              <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
                              Approve
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              className="text-red-500 border-red-300 hover:bg-red-50 h-7 text-xs"
                              onClick={() => approveMutation.mutate({ id: r.id, status: "Rejected" })}
                              disabled={approveMutation.isPending}
                            >
                              <XCircle className="h-3.5 w-3.5 mr-1" />
                              Reject
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
