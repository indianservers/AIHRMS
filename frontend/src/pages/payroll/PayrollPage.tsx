import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  DollarSign, FileText, Play, CheckCircle2, RefreshCw,
  ChevronLeft, ChevronRight, Download
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { payrollApi } from "@/services/api";
import { formatCurrency, formatDate, statusColor } from "@/lib/utils";
import { toast } from "@/hooks/use-toast";

interface PayrollRun {
  id: number;
  month: number;
  year: number;
  status: string;
  total_gross: number;
  total_net: number;
  total_employees: number;
  created_at: string;
}

interface PayslipRecord {
  id: number;
  employee: { first_name: string; last_name: string; employee_id: string };
  gross_salary: number;
  net_salary: number;
  total_deductions: number;
  status: string;
  employer_contributions?: { component_name: string; amount: number }[];
  reimbursements?: { component_name: string; amount: number }[];
  ytd?: {
    gross_salary: number;
    total_deductions: number;
    net_salary: number;
    reimbursements: number;
    employer_contributions: number;
  };
}

interface PayrollVariance {
  id: number;
  employee_id: number;
  current_gross: number;
  previous_gross: number;
  gross_delta_percent: number;
  current_net: number;
  previous_net: number;
  net_delta_percent: number;
  severity: string;
  reason?: string;
}

const MONTHS = [
  "January","February","March","April","May","June",
  "July","August","September","October","November","December"
];

export default function PayrollPage() {
  const qc = useQueryClient();
  const today = new Date();
  const [activeTab, setActiveTab] = useState<"payslip" | "runs" | "casebook">("payslip");
  const [slipMonth, setSlipMonth] = useState(today.getMonth() + 1);
  const [slipYear, setSlipYear] = useState(today.getFullYear());
  const [runMonth, setRunMonth] = useState(today.getMonth() + 1);
  const [runYear, setRunYear] = useState(today.getFullYear());
  const [selectedRun, setSelectedRun] = useState<PayrollRun | null>(null);

  const { data: payslip, isLoading: loadingSlip } = useQuery({
    queryKey: ["payslip", slipMonth, slipYear],
    queryFn: () => payrollApi.payslip(slipMonth, slipYear).then((r) => r.data),
    retry: false,
  });

  const { data: runs, isLoading: loadingRuns, refetch: refetchRuns } = useQuery({
    queryKey: ["payroll-runs"],
    queryFn: () => payrollApi.runs().then((r) => r.data),
    retry: false,
  });

  const { data: runRecords } = useQuery({
    queryKey: ["run-records", selectedRun?.id],
    queryFn: () => payrollApi.runRecords(selectedRun!.id).then((r) => r.data),
    enabled: !!selectedRun,
  });

  const { data: runVariance, refetch: refetchVariance } = useQuery({
    queryKey: ["run-variance", selectedRun?.id],
    queryFn: () => payrollApi.runVariance(selectedRun!.id).then((r) => r.data),
    enabled: !!selectedRun,
  });

  const runMutation = useMutation({
    mutationFn: () => payrollApi.runPayroll({ month: runMonth, year: runYear }),
    onSuccess: () => {
      toast({ title: "Payroll run initiated!" });
      refetchRuns();
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Failed to run payroll";
      toast({ title: "Error", description: msg, variant: "destructive" });
    },
  });

  const approveMutation = useMutation({
    mutationFn: (id: number) => payrollApi.approveRun(id, { action: "approve", remarks: "Approved from payroll console" }),
    onSuccess: () => {
      toast({ title: "Payroll run approved!" });
      refetchRuns();
      setSelectedRun(null);
    },
  });

  const exportMutation = useMutation({
    mutationFn: (exportType: string) => payrollApi.exportRun(selectedRun!.id, exportType),
    onSuccess: (response) => {
      toast({ title: "Payroll export generated", description: response.data.output_file_url });
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Export failed";
      toast({ title: "Error", description: msg, variant: "destructive" });
    },
  });

  const prevSlipMonth = () => {
    if (slipMonth === 1) { setSlipMonth(12); setSlipYear((y) => y - 1); }
    else setSlipMonth((m) => m - 1);
  };
  const nextSlipMonth = () => {
    if (slipMonth === 12) { setSlipMonth(1); setSlipYear((y) => y + 1); }
    else setSlipMonth((m) => m + 1);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Payroll</h1>
        <p className="page-description">View payslips and manage payroll runs.</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        {(["payslip", "runs", "casebook"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab === "payslip" ? "My Payslip" : tab === "runs" ? "Payroll Runs" : "Real Cases"}
          </button>
        ))}
      </div>

      {activeTab === "payslip" && (
        <div className="space-y-4">
          {/* Month navigator */}
          <div className="flex items-center gap-3">
            <Button variant="outline" size="icon" className="h-8 w-8" onClick={prevSlipMonth}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm font-medium w-40 text-center">
              {MONTHS[slipMonth - 1]} {slipYear}
            </span>
            <Button variant="outline" size="icon" className="h-8 w-8" onClick={nextSlipMonth}>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>

          {loadingSlip ? (
            <Card><CardContent className="p-8 text-center"><div className="h-40 skeleton rounded" /></CardContent></Card>
          ) : !payslip ? (
            <Card>
              <CardContent className="p-12 text-center text-muted-foreground">
                <FileText className="h-10 w-10 mx-auto mb-3 opacity-30" />
                <p>No payslip available for {MONTHS[slipMonth - 1]} {slipYear}</p>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Pay Slip</CardTitle>
                    <CardDescription>{MONTHS[slipMonth - 1]} {slipYear}</CardDescription>
                  </div>
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColor(payslip.status || "Draft")}`}>
                    {payslip.status || "Draft"}
                  </span>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Employee info */}
                {payslip.employee && (
                  <div className="grid grid-cols-2 gap-4 p-4 bg-muted/30 rounded-lg text-sm">
                    <div>
                      <p className="text-muted-foreground">Employee</p>
                      <p className="font-medium">{payslip.employee.first_name} {payslip.employee.last_name}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Employee ID</p>
                      <p className="font-medium">{payslip.employee.employee_id}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Month</p>
                      <p className="font-medium">{MONTHS[slipMonth - 1]} {slipYear}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Working Days</p>
                      <p className="font-medium">{payslip.working_days ?? "—"}</p>
                    </div>
                  </div>
                )}

                {/* Earnings */}
                <div>
                  <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Earnings</h3>
                  <div className="space-y-2">
                    {(payslip.earnings as { component_name: string; amount: number }[] || []).map((e, i) => (
                      <div key={i} className="flex justify-between text-sm">
                        <span>{e.component_name}</span>
                        <span className="font-medium">{formatCurrency(e.amount)}</span>
                      </div>
                    ))}
                    <div className="flex justify-between text-sm font-semibold border-t pt-2">
                      <span>Gross Salary</span>
                      <span className="text-green-600">{formatCurrency(payslip.gross_salary)}</span>
                    </div>
                  </div>
                </div>

                {/* Deductions */}
                <div>
                  <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Deductions</h3>
                  <div className="space-y-2">
                    {(payslip.deductions as { component_name: string; amount: number }[] || []).map((d, i) => (
                      <div key={i} className="flex justify-between text-sm">
                        <span>{d.component_name}</span>
                        <span className="font-medium text-red-600">{formatCurrency(d.amount)}</span>
                      </div>
                    ))}
                    <div className="flex justify-between text-sm font-semibold border-t pt-2">
                      <span>Total Deductions</span>
                      <span className="text-red-600">{formatCurrency(payslip.total_deductions)}</span>
                    </div>
                  </div>
                </div>

                {Array.isArray(payslip.employer_contributions) && payslip.employer_contributions.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Employer Contributions</h3>
                    <div className="space-y-2">
                      {(payslip.employer_contributions as { component_name: string; amount: number }[]).map((item, i) => (
                        <div key={i} className="flex justify-between text-sm">
                          <span>{item.component_name}</span>
                          <span className="font-medium">{formatCurrency(item.amount)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {Array.isArray(payslip.reimbursements) && payslip.reimbursements.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Reimbursements</h3>
                    <div className="space-y-2">
                      {(payslip.reimbursements as { component_name: string; amount: number }[]).map((item, i) => (
                        <div key={i} className="flex justify-between text-sm">
                          <span>{item.component_name}</span>
                          <span className="font-medium text-blue-600">{formatCurrency(item.amount)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Net */}
                <div className="flex justify-between items-center p-4 bg-primary/10 rounded-lg">
                  <span className="font-semibold">Net Salary</span>
                  <span className="text-xl font-bold text-primary">{formatCurrency(payslip.net_salary)}</span>
                </div>

                {payslip.ytd && (
                  <div>
                    <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wide">Year to Date</h3>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
                      <div className="rounded-md border p-3">
                        <p className="text-muted-foreground">Gross</p>
                        <p className="font-semibold">{formatCurrency(payslip.ytd.gross_salary)}</p>
                      </div>
                      <div className="rounded-md border p-3">
                        <p className="text-muted-foreground">Deductions</p>
                        <p className="font-semibold">{formatCurrency(payslip.ytd.total_deductions)}</p>
                      </div>
                      <div className="rounded-md border p-3">
                        <p className="text-muted-foreground">Net</p>
                        <p className="font-semibold">{formatCurrency(payslip.ytd.net_salary)}</p>
                      </div>
                      <div className="rounded-md border p-3">
                        <p className="text-muted-foreground">Reimbursements</p>
                        <p className="font-semibold">{formatCurrency(payslip.ytd.reimbursements)}</p>
                      </div>
                      <div className="rounded-md border p-3">
                        <p className="text-muted-foreground">Employer Cost</p>
                        <p className="font-semibold">{formatCurrency(payslip.ytd.employer_contributions)}</p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {activeTab === "runs" && (
        <div className="space-y-4">
          {/* Run payroll card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Run Payroll</CardTitle>
              <CardDescription>Process payroll for a specific month</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap items-end gap-4">
                <div className="space-y-1.5">
                  <Label>Month</Label>
                  <select
                    value={runMonth}
                    onChange={(e) => setRunMonth(Number(e.target.value))}
                    className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    {MONTHS.map((m, i) => (
                      <option key={i} value={i + 1}>{m}</option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1.5">
                  <Label>Year</Label>
                  <Input
                    type="number"
                    value={runYear}
                    onChange={(e) => setRunYear(Number(e.target.value))}
                    className="w-24"
                    min={2020}
                    max={2100}
                  />
                </div>
                <Button
                  onClick={() => runMutation.mutate()}
                  disabled={runMutation.isPending}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Play className="h-4 w-4 mr-2" />
                  {runMutation.isPending ? "Processing..." : "Run Payroll"}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Runs list */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Payroll Runs</CardTitle>
                <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => refetchRuns()}>
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b bg-muted/50">
                    <tr>
                      {["Period", "Employees", "Gross", "Net", "Status", "Actions"].map((h) => (
                        <th key={h} className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {loadingRuns ? (
                      Array.from({ length: 5 }).map((_, i) => (
                        <tr key={i} className="border-b">
                          <td colSpan={6} className="px-4 py-3"><div className="h-4 skeleton rounded" /></td>
                        </tr>
                      ))
                    ) : !runs || (runs as PayrollRun[]).length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-4 py-10 text-center text-muted-foreground">
                          No payroll runs yet
                        </td>
                      </tr>
                    ) : (
                      (runs as PayrollRun[]).map((run) => (
                        <tr
                          key={run.id}
                          className={`border-b hover:bg-muted/30 cursor-pointer ${selectedRun?.id === run.id ? "bg-muted/50" : ""}`}
                          onClick={() => setSelectedRun(selectedRun?.id === run.id ? null : run)}
                        >
                          <td className="px-4 py-3 font-medium">
                            {MONTHS[run.month - 1]} {run.year}
                          </td>
                          <td className="px-4 py-3">{run.total_employees}</td>
                          <td className="px-4 py-3">{formatCurrency(run.total_gross)}</td>
                          <td className="px-4 py-3 font-medium text-green-600">{formatCurrency(run.total_net)}</td>
                          <td className="px-4 py-3">
                            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${statusColor(run.status)}`}>
                              {run.status}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            {run.status === "Draft" && (
                              <Button
                                size="sm"
                                className="bg-green-600 hover:bg-green-700 h-7 text-xs"
                                onClick={(e) => { e.stopPropagation(); approveMutation.mutate(run.id); }}
                                disabled={approveMutation.isPending}
                              >
                                <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
                                Approve
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

          {selectedRun && (
            <Card>
              <CardHeader>
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <CardTitle className="text-base">
                      {MONTHS[selectedRun.month - 1]} {selectedRun.year} Payroll Review
                    </CardTitle>
                    <CardDescription>Variance, audit-ready export batches, and statutory stubs</CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => refetchVariance()}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh Variance
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  {[
                    ["pf_ecr", "PF ECR"],
                    ["esi", "ESI"],
                    ["pt", "PT"],
                    ["tds_24q", "TDS 24Q"],
                    ["bank_advice", "Bank Advice"],
                    ["pay_register", "Pay Register"],
                  ].map(([type, label]) => (
                    <Button
                      key={type}
                      variant="outline"
                      size="sm"
                      onClick={() => exportMutation.mutate(type)}
                      disabled={exportMutation.isPending}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      {label}
                    </Button>
                  ))}
                </div>

                <div className="overflow-x-auto border rounded-md">
                  <table className="w-full text-sm">
                    <thead className="border-b bg-muted/50">
                      <tr>
                        {["Employee", "Gross Change", "Net Change", "Severity", "Reason"].map((h) => (
                          <th key={h} className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {!runVariance || (runVariance as PayrollVariance[]).length === 0 ? (
                        <tr>
                          <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">
                            No variance data available
                          </td>
                        </tr>
                      ) : (
                        (runVariance as PayrollVariance[]).map((item) => (
                          <tr key={item.id} className="border-b hover:bg-muted/30">
                            <td className="px-4 py-3">#{item.employee_id}</td>
                            <td className="px-4 py-3">
                              {formatCurrency(item.previous_gross)} to {formatCurrency(item.current_gross)}
                              <p className="text-xs text-muted-foreground">{Number(item.gross_delta_percent).toFixed(1)}%</p>
                            </td>
                            <td className="px-4 py-3">
                              {formatCurrency(item.previous_net)} to {formatCurrency(item.current_net)}
                              <p className="text-xs text-muted-foreground">{Number(item.net_delta_percent).toFixed(1)}%</p>
                            </td>
                            <td className="px-4 py-3">
                              <Badge variant="outline">{item.severity}</Badge>
                            </td>
                            <td className="px-4 py-3 text-muted-foreground">{item.reason}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Run detail */}
          {selectedRun && runRecords && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">
                  {MONTHS[selectedRun.month - 1]} {selectedRun.year} — Employee Records
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="border-b bg-muted/50">
                      <tr>
                        {["Employee", "Gross", "Deductions", "Net", "Status"].map((h) => (
                          <th key={h} className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(runRecords as PayslipRecord[]).map((r) => (
                        <tr key={r.id} className="border-b hover:bg-muted/30">
                          <td className="px-4 py-3">
                            <p className="font-medium">{r.employee?.first_name} {r.employee?.last_name}</p>
                            <p className="text-xs text-muted-foreground">{r.employee?.employee_id}</p>
                          </td>
                          <td className="px-4 py-3">{formatCurrency(r.gross_salary)}</td>
                          <td className="px-4 py-3 text-red-600">{formatCurrency(r.total_deductions)}</td>
                          <td className="px-4 py-3 font-medium text-green-600">{formatCurrency(r.net_salary)}</td>
                          <td className="px-4 py-3">
                            <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${statusColor(r.status)}`}>
                              {r.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {activeTab === "casebook" && (
        <div className="grid gap-4 lg:grid-cols-2">
          {[
            {
              title: "New Joiner Proration",
              detail: "Employee joins mid-month. Payroll should calculate paid days from joining date, include fixed earnings, and exclude LOP outside employment.",
              checks: ["Joining date within month", "Paid days prorated", "PF/ESI on eligible wages"],
            },
            {
              title: "Loss of Pay and Leave",
              detail: "Approved paid leave should not reduce salary; unpaid or excess leave should create LOP deduction before approval.",
              checks: ["Leave balance consumed", "LOP days visible", "Gross to net reconciliation"],
            },
            {
              title: "Bonus and Reimbursement",
              detail: "One-time bonus should be taxable earning; approved reimbursements should be paid separately or marked non-taxable based on policy.",
              checks: ["Bonus as earning", "Receipt-backed reimbursements", "Approval before payroll lock"],
            },
            {
              title: "Payroll Anomaly",
              detail: "AI anomaly detection should flag unusually high net pay, negative net pay, duplicate components, and large month-on-month variance.",
              checks: ["Variance threshold", "Negative net block", "Audit trail retained"],
            },
          ].map((item) => (
            <Card key={item.title}>
              <CardHeader>
                <CardTitle className="text-base">{item.title}</CardTitle>
                <CardDescription>{item.detail}</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  {item.checks.map((check) => (
                    <li key={check} className="flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      {check}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
