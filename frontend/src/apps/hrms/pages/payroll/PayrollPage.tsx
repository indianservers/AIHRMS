import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  DollarSign, FileText, Play, CheckCircle2, RefreshCw,
  ChevronLeft, ChevronRight, Download, ShieldCheck, Building2,
  ClipboardCheck, Eye, Mail, PauseCircle, Settings2, AlertTriangle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { payrollApi, statutoryComplianceApi } from "@/services/api";
import { assetUrl, formatCurrency, formatDate, statusColor } from "@/lib/utils";
import { toast } from "@/hooks/use-toast";
import { usePageTitle } from "@/hooks/use-page-title";
import { useAuthStore } from "@/store/authStore";

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
  earnings?: { component_name: string; amount: number }[];
  deductions?: { component_name: string; amount: number }[];
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

interface PayrollPreRunCheck {
  id: number;
  check_name: string;
  check_type: string;
  status: string;
  message?: string;
  blocker: boolean;
}

interface PayrollWorksheetRow {
  id: number;
  employee_id: number;
  input_status: string;
  calculation_status: string;
  approval_status: string;
  status: string;
  gross_salary: number;
  total_deductions: number;
  net_salary: number;
  variance_status: string;
  hold_reason?: string;
  skip_reason?: string;
}

interface SalaryComponent {
  id: number;
  name: string;
  code: string;
  component_type: string;
  calculation_type: string;
  amount: number;
  payslip_group: string;
}

interface SalaryStructure {
  id: number;
  name: string;
  version: string;
  components?: unknown[];
}

interface LegalEntity {
  id: number;
  legal_name: string;
  state?: string;
  pan?: string;
  tan?: string;
  is_default?: boolean;
}

const MONTHS = [
  "January","February","March","April","May","June",
  "July","August","September","October","November","December"
];

const normalizeRunStatus = (status?: string) => (status || "draft").toLowerCase().replace(/\s+/g, "_");

type PayrollTab = "wizard" | "run" | "viewer" | "variance" | "inputs" | "setup" | "statutory" | "tax" | "casebook";

export default function PayrollPage() {
  usePageTitle("Payroll");
  const qc = useQueryClient();
  const { user } = useAuthStore();
  const isEmployee = user?.role === "employee" && !user?.is_superuser;
  const today = new Date();
  const [activeTab, setActiveTab] = useState<PayrollTab>(isEmployee ? "viewer" : "wizard");
  const [wizardStep, setWizardStep] = useState(0);
  const [slipMonth, setSlipMonth] = useState(today.getMonth() + 1);
  const [slipYear, setSlipYear] = useState(today.getFullYear());
  const [runMonth, setRunMonth] = useState(today.getMonth() + 1);
  const [runYear, setRunYear] = useState(today.getFullYear());
  const [selectedRun, setSelectedRun] = useState<PayrollRun | null>(null);
  const [payGroupName, setPayGroupName] = useState("India Monthly");
  const [payGroupCode, setPayGroupCode] = useState("IN-MONTHLY");
  const [taxSection, setTaxSection] = useState("80C");
  const [taxAmount, setTaxAmount] = useState("150000");
  const [taxProofUrl, setTaxProofUrl] = useState("");
  const [inputPeriodId, setInputPeriodId] = useState("");
  const [lopEmployeeId, setLopEmployeeId] = useState("");
  const [lopDays, setLopDays] = useState("1");
  const [otEmployeeId, setOtEmployeeId] = useState("");
  const [otHours, setOtHours] = useState("2");
  const [encashEmployeeId, setEncashEmployeeId] = useState("");
  const [encashDays, setEncashDays] = useState("1");
  const [statutoryState, setStatutoryState] = useState("Telangana");
  const [ruleEffectiveFrom, setRuleEffectiveFrom] = useState(`${today.getFullYear()}-04-01`);
  const [ptAmount, setPtAmount] = useState("200");
  const [lwfEmployeeAmount, setLwfEmployeeAmount] = useState("10");
  const [lwfEmployerAmount, setLwfEmployerAmount] = useState("20");
  const [paymentBatchId, setPaymentBatchId] = useState("");
  const [templateName, setTemplateName] = useState("Default Salary Template");
  const [templateCode, setTemplateCode] = useState("DEFAULT-SALARY");
  const [legalName, setLegalName] = useState("Indian Servers Pvt Ltd");
  const [legalState, setLegalState] = useState("Telangana");
  const [legalPan, setLegalPan] = useState("");
  const [legalTan, setLegalTan] = useState("");
  const [componentName, setComponentName] = useState("Basic Salary");
  const [componentCode, setComponentCode] = useState("BASIC");
  const [componentType, setComponentType] = useState("Earning");
  const [componentAmount, setComponentAmount] = useState("50000");
  const [structureName, setStructureName] = useState("India Monthly Structure");
  const [structureVersion, setStructureVersion] = useState("1.0");
  const [selectedRecordId, setSelectedRecordId] = useState<number | null>(null);
  const visibleTabs: PayrollTab[] = isEmployee
    ? ["viewer"]
    : ["wizard", "run", "viewer", "variance", "inputs", "statutory", "tax", "casebook"];

  useEffect(() => {
    if (isEmployee && activeTab !== "viewer") setActiveTab("viewer");
  }, [activeTab, isEmployee]);

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

  const { data: preRunChecks } = useQuery({
    queryKey: ["payroll-pre-run-checks", selectedRun?.id],
    queryFn: () => payrollApi.preRunChecks(selectedRun!.id).then((r) => r.data),
    enabled: !!selectedRun,
  });

  const { data: payGroups } = useQuery({
    queryKey: ["payroll-pay-groups"],
    queryFn: () => payrollApi.payGroups().then((r) => r.data),
  });

  const { data: legalEntities } = useQuery({
    queryKey: ["payroll-legal-entities"],
    queryFn: () => statutoryComplianceApi.legalEntities().then((r) => r.data),
  });

  const { data: salaryComponents } = useQuery({
    queryKey: ["salary-components"],
    queryFn: () => payrollApi.components().then((r) => r.data),
  });

  const { data: salaryStructures } = useQuery({
    queryKey: ["salary-structures"],
    queryFn: () => payrollApi.structures().then((r) => r.data),
  });

  const { data: setupStatutoryProfiles } = useQuery({
    queryKey: ["payroll-setup-statutory-profiles", (legalEntities as LegalEntity[] | undefined)?.[0]?.id],
    queryFn: () => payrollApi.setupStatutoryProfiles({ legal_entity_id: (legalEntities as LegalEntity[])[0].id }).then((r) => r.data),
    enabled: Boolean((legalEntities as LegalEntity[] | undefined)?.[0]?.id),
  });

  const { data: salaryTemplates } = useQuery({
    queryKey: ["salary-templates"],
    queryFn: () => payrollApi.salaryTemplates().then((r) => r.data),
  });

  const { data: payrollPeriods } = useQuery({
    queryKey: ["payroll-periods", runYear],
    queryFn: () => payrollApi.payrollPeriods({ year: runYear }).then((r) => r.data),
  });

  const selectedInputPeriod = Number(inputPeriodId || ((payrollPeriods as { id: number }[] | undefined)?.[0]?.id || 0));

  const { data: payrollInputs } = useQuery({
    queryKey: ["payroll-inputs", selectedInputPeriod],
    queryFn: () => payrollApi.payrollAttendanceInputs({ period_id: selectedInputPeriod }).then((r) => r.data),
    enabled: !!selectedInputPeriod,
  });

  const { data: lopAdjustments } = useQuery({
    queryKey: ["lop-adjustments", selectedInputPeriod],
    queryFn: () => payrollApi.lopAdjustments({ period_id: selectedInputPeriod }).then((r) => r.data),
    enabled: !!selectedInputPeriod,
  });

  const { data: overtimeLines } = useQuery({
    queryKey: ["overtime-lines", selectedInputPeriod],
    queryFn: () => payrollApi.overtimeLines({ period_id: selectedInputPeriod }).then((r) => r.data),
    enabled: !!selectedInputPeriod,
  });

  const { data: encashmentLines } = useQuery({
    queryKey: ["encashment-lines", selectedInputPeriod],
    queryFn: () => payrollApi.leaveEncashmentLines({ period_id: selectedInputPeriod }).then((r) => r.data),
    enabled: !!selectedInputPeriod,
  });

  const { data: worksheetRows } = useQuery({
    queryKey: ["payroll-worksheet", selectedRun?.id],
    queryFn: () => payrollApi.runWorksheet(selectedRun!.id).then((r) => r.data),
    enabled: !!selectedRun,
  });

  const { data: paymentBatches } = useQuery({
    queryKey: ["payment-batches", selectedRun?.id],
    queryFn: () => payrollApi.paymentBatches({ payroll_run_id: selectedRun!.id }).then((r) => r.data),
    enabled: !!selectedRun,
  });

  const { data: accountingJournals } = useQuery({
    queryKey: ["accounting-journals", selectedRun?.id],
    queryFn: () => payrollApi.accountingJournals(selectedRun!.id).then((r) => r.data),
    enabled: !!selectedRun,
  });

  const { data: taxCycles } = useQuery({
    queryKey: ["tax-cycles"],
    queryFn: () => payrollApi.taxCycles().then((r) => r.data),
  });

  const { data: pfRules } = useQuery({
    queryKey: ["payroll-pf-rules"],
    queryFn: () => payrollApi.pfRules().then((r) => r.data),
  });

  const { data: esiRules } = useQuery({
    queryKey: ["payroll-esi-rules"],
    queryFn: () => payrollApi.esiRules().then((r) => r.data),
  });

  const { data: ptSlabs } = useQuery({
    queryKey: ["payroll-pt-slabs"],
    queryFn: () => payrollApi.ptSlabs().then((r) => r.data),
  });

  const { data: lwfSlabs } = useQuery({
    queryKey: ["payroll-lwf-slabs"],
    queryFn: () => payrollApi.lwfSlabs().then((r) => r.data),
  });

  const { data: gratuityRules } = useQuery({
    queryKey: ["payroll-gratuity-rules"],
    queryFn: () => payrollApi.gratuityRules().then((r) => r.data),
  });

  const { data: challans } = useQuery({
    queryKey: ["payroll-statutory-challans"],
    queryFn: () => payrollApi.statutoryChallans().then((r) => r.data),
  });

  const activeTaxCycle = Array.isArray(taxCycles) ? taxCycles[0] : null;

  const { data: taxDeclarations } = useQuery({
    queryKey: ["tax-declarations", activeTaxCycle?.id],
    queryFn: () => payrollApi.taxDeclarations({ cycle_id: activeTaxCycle.id }).then((r) => r.data),
    enabled: !!activeTaxCycle,
  });

  const { data: taxProjection } = useQuery({
    queryKey: ["tax-projection", activeTaxCycle?.id],
    queryFn: () => payrollApi.taxProjection({ cycle_id: activeTaxCycle.id }).then((r) => r.data),
    enabled: !!activeTaxCycle,
    retry: false,
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

  const runStatusMutation = useMutation({
    mutationFn: ({ id, action, forceApprove }: { id: number; action: "approve" | "lock" | "paid"; forceApprove?: boolean }) =>
      payrollApi.approveRun(id, { action, force_approve: Boolean(forceApprove), remarks: forceApprove ? "Force approved from payroll console" : `${action} from payroll console` }),
    onSuccess: (response, variables) => {
      const title = variables.action === "approve" ? "Payroll run approved" : variables.action === "lock" ? "Payroll run locked" : "Payroll run marked paid";
      toast({ title });
      qc.invalidateQueries({ queryKey: ["payroll-runs"] });
      if (selectedRun?.id === variables.id) {
        setSelectedRun({ ...selectedRun, status: response.data.status });
      }
    },
    onError: (e: unknown) => {
      const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      const msg = typeof detail === "string" ? detail : "Approve blocked until payroll inputs are approved and locked";
      toast({ title: "Payroll approval blocked", description: msg, variant: "destructive" });
    },
  });

  const reconcileMutation = useMutation({
    mutationFn: () => payrollApi.reconcilePayrollAttendance({ period_id: selectedInputPeriod, approve_inputs: true }),
    onSuccess: () => {
      toast({ title: "Attendance inputs reconciled" });
      qc.invalidateQueries({ queryKey: ["payroll-inputs"] });
      qc.invalidateQueries({ queryKey: ["overtime-lines"] });
    },
    onError: () => toast({ title: "Could not reconcile attendance", variant: "destructive" }),
  });

  const worksheetMutation = useMutation({
    mutationFn: (runId: number) => payrollApi.processRunWorksheet(runId),
    onSuccess: () => {
      toast({ title: "Payroll worksheet processed" });
      qc.invalidateQueries({ queryKey: ["payroll-worksheet"] });
      qc.invalidateQueries({ queryKey: ["payroll-runs"] });
    },
    onError: () => toast({ title: "Could not process worksheet", variant: "destructive" }),
  });

  const worksheetRowMutation = useMutation({
    mutationFn: ({ runId, rowId, action, reason }: { runId: number; rowId: number; action: "hold" | "skip" | "clear" | "approve"; reason?: string }) =>
      payrollApi.updateWorksheetRow(runId, rowId, { action, reason }),
    onSuccess: () => {
      toast({ title: "Worksheet row updated" });
      qc.invalidateQueries({ queryKey: ["payroll-worksheet"] });
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Could not update worksheet row";
      toast({ title: "Worksheet update failed", description: msg, variant: "destructive" });
    },
  });

  const lopMutation = useMutation({
    mutationFn: () => payrollApi.createLopAdjustment({
      period_id: selectedInputPeriod,
      employee_id: Number(lopEmployeeId),
      adjustment_days: lopDays,
      reason: "Payroll input adjustment",
      status: "Approved",
    }),
    onSuccess: () => {
      toast({ title: "LOP adjustment added" });
      qc.invalidateQueries({ queryKey: ["lop-adjustments"] });
    },
  });

  const otMutation = useMutation({
    mutationFn: () => payrollApi.createOvertimeLine({
      period_id: selectedInputPeriod,
      employee_id: Number(otEmployeeId),
      hours: otHours,
      multiplier: "1.5",
      status: "Approved",
    }),
    onSuccess: () => {
      toast({ title: "Overtime line added" });
      qc.invalidateQueries({ queryKey: ["overtime-lines"] });
    },
  });

  const encashMutation = useMutation({
    mutationFn: () => payrollApi.createLeaveEncashmentLine({
      period_id: selectedInputPeriod,
      employee_id: Number(encashEmployeeId),
      days: encashDays,
      status: "Approved",
    }),
    onSuccess: () => {
      toast({ title: "Leave encashment line added" });
      qc.invalidateQueries({ queryKey: ["encashment-lines"] });
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

  const legalEntityMutation = useMutation({
    mutationFn: () =>
      statutoryComplianceApi.createLegalEntity({
        legal_name: legalName,
        state: legalState,
        pan: legalPan || undefined,
        tan: legalTan || undefined,
        registered_address: "Registered office",
        is_default: true,
      }),
    onSuccess: () => {
      toast({ title: "Legal entity created" });
      qc.invalidateQueries({ queryKey: ["payroll-legal-entities"] });
      setWizardStep(1);
    },
    onError: () => toast({ title: "Could not create legal entity", variant: "destructive" }),
  });

  const payGroupMutation = useMutation({
    mutationFn: () =>
      payrollApi.createPayGroup({
        name: payGroupName,
        code: payGroupCode,
        description: "Default payroll group",
        pay_frequency: "Monthly",
        legal_entity_id: (legalEntities as LegalEntity[] | undefined)?.[0]?.id,
        state: legalState,
        is_default: true,
      }),
    onSuccess: () => {
      toast({ title: "Pay group created" });
      qc.invalidateQueries({ queryKey: ["payroll-pay-groups"] });
      setWizardStep(2);
    },
    onError: () => toast({ title: "Could not create pay group", variant: "destructive" }),
  });

  const componentMutation = useMutation({
    mutationFn: () =>
      payrollApi.createComponent({
        name: componentName,
        code: componentCode,
        component_type: componentType,
        calculation_type: "Fixed",
        amount: componentAmount,
        payslip_group: componentType === "Deduction" ? "Deductions" : "Earnings",
        display_sequence: componentType === "Deduction" ? 200 : 100,
        is_taxable: componentType === "Earning",
        appears_in_ctc: true,
        appears_in_payslip: true,
      }),
    onSuccess: () => {
      toast({ title: "Salary component created" });
      qc.invalidateQueries({ queryKey: ["salary-components"] });
      setWizardStep(3);
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Could not create component";
      toast({ title: "Component failed", description: msg, variant: "destructive" });
    },
  });

  const structureMutation = useMutation({
    mutationFn: () =>
      payrollApi.createStructure({
        name: structureName,
        version: structureVersion,
        effective_from: `${today.getFullYear()}-04-01`,
        components: (salaryComponents as SalaryComponent[] | undefined || []).slice(0, 8).map((component, index) => ({
          component_id: component.id,
          amount: component.amount || 0,
          order_sequence: index + 1,
        })),
      }),
    onSuccess: () => {
      toast({ title: "Salary structure created" });
      qc.invalidateQueries({ queryKey: ["salary-structures"] });
      setWizardStep(4);
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Create at least one component first";
      toast({ title: "Structure failed", description: msg, variant: "destructive" });
    },
  });

  const salaryTemplateMutation = useMutation({
    mutationFn: () =>
      payrollApi.createSalaryTemplate({
        name: templateName,
        code: templateCode,
        pay_group_id: (payGroups as { id: number }[] | undefined)?.[0]?.id,
        components: [],
      }),
    onSuccess: () => {
      toast({ title: "Salary template created" });
      qc.invalidateQueries({ queryKey: ["salary-templates"] });
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Could not create salary template";
      toast({ title: "Template failed", description: msg, variant: "destructive" });
    },
  });

  const taxCycleMutation = useMutation({
    mutationFn: () =>
      payrollApi.createTaxCycle({
        name: `FY ${today.getFullYear()}-${String(today.getFullYear() + 1).slice(-2)}`,
        financial_year: `${today.getFullYear()}-${String(today.getFullYear() + 1).slice(-2)}`,
        start_date: `${today.getFullYear()}-04-01`,
        end_date: `${today.getFullYear() + 1}-03-31`,
        proof_due_date: `${today.getFullYear() + 1}-01-31`,
      }),
    onSuccess: () => {
      toast({ title: "Tax cycle opened" });
      qc.invalidateQueries({ queryKey: ["tax-cycles"] });
      setWizardStep(5);
    },
    onError: () => toast({ title: "Could not open tax cycle", variant: "destructive" }),
  });

  const setupStatutoryProfileMutation = useMutation({
    mutationFn: () =>
      payrollApi.createSetupStatutoryProfile({
        legal_entity_id: (legalEntities as LegalEntity[] | undefined)?.[0]?.id,
        pf_establishment_code: "PF-SETUP",
        pf_signatory: "Payroll Manager",
        esi_employer_code: "ESI-SETUP",
        pt_registration_number: "PT-SETUP",
        tan_circle: legalState,
        effective_from: ruleEffectiveFrom,
      }),
    onSuccess: () => {
      toast({ title: "Statutory profile created" });
      qc.invalidateQueries({ queryKey: ["payroll-setup-statutory-profiles"] });
      setWizardStep(5);
    },
    onError: () => toast({ title: "Could not create statutory profile", variant: "destructive" }),
  });

  const taxDeclarationMutation = useMutation({
    mutationFn: () =>
      payrollApi.createTaxDeclaration({
        cycle_id: activeTaxCycle.id,
        section: taxSection,
        declared_amount: taxAmount,
        description: "Employee tax declaration",
      }),
    onSuccess: () => {
      toast({ title: "Tax declaration submitted" });
      qc.invalidateQueries({ queryKey: ["tax-declarations"] });
      qc.invalidateQueries({ queryKey: ["tax-projection"] });
    },
    onError: () => toast({ title: "Could not submit declaration", variant: "destructive" }),
  });

  const taxProofMutation = useMutation({
    mutationFn: (declarationId: number) =>
      payrollApi.submitTaxProof({
        declaration_id: declarationId,
        file_url: taxProofUrl || "/uploads/tax/proof-placeholder.pdf",
        original_filename: taxProofUrl.split("/").pop() || "proof-placeholder.pdf",
      }),
    onSuccess: () => {
      toast({ title: "Tax proof submitted" });
      setTaxProofUrl("");
      qc.invalidateQueries({ queryKey: ["tax-declarations"] });
    },
    onError: () => toast({ title: "Could not submit proof", variant: "destructive" }),
  });

  const seedStatutoryMutation = useMutation({
    mutationFn: async () => {
      await payrollApi.createPfRule({ name: `PF ${today.getFullYear()}`, wage_ceiling: "15000", employee_rate: "12", employer_rate: "12", effective_from: ruleEffectiveFrom });
      await payrollApi.createEsiRule({ name: `ESI ${today.getFullYear()}`, wage_threshold: "21000", employee_rate: "0.75", employer_rate: "3.25", effective_from: ruleEffectiveFrom });
      await payrollApi.createPtSlab({ state: statutoryState, salary_from: "20000", employee_amount: ptAmount, effective_from: ruleEffectiveFrom });
      await payrollApi.createLwfSlab({ state: statutoryState, salary_from: "0", employee_amount: lwfEmployeeAmount, employer_amount: lwfEmployerAmount, deduction_month: 12, effective_from: ruleEffectiveFrom });
      await payrollApi.createGratuityRule({ name: `Gratuity ${today.getFullYear()}`, days_per_year: "15", wage_days_divisor: "26", min_service_years: "5", effective_from: ruleEffectiveFrom });
    },
    onSuccess: () => {
      toast({ title: "Statutory rules created" });
      ["payroll-pf-rules", "payroll-esi-rules", "payroll-pt-slabs", "payroll-lwf-slabs", "payroll-gratuity-rules"].forEach((key) =>
        qc.invalidateQueries({ queryKey: [key] })
      );
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Could not create statutory rules";
      toast({ title: "Rule creation failed", description: msg, variant: "destructive" });
    },
  });

  const paymentBatchMutation = useMutation({
    mutationFn: (runId: number) => payrollApi.createPaymentBatch({ payroll_run_id: runId }),
    onSuccess: () => {
      toast({ title: "Payment batch generated" });
      qc.invalidateQueries({ queryKey: ["payment-batches"] });
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Could not generate payment batch";
      toast({ title: "Payment batch failed", description: msg, variant: "destructive" });
    },
  });

  const paymentStatusMutation = useMutation({
    mutationFn: () => payrollApi.importPaymentStatus(Number(paymentBatchId), { lines: [] }),
    onSuccess: () => {
      toast({ title: "Payment status import checked" });
      qc.invalidateQueries({ queryKey: ["payment-batches"] });
    },
  });

  const journalMutation = useMutation({
    mutationFn: (runId: number) => payrollApi.generateAccountingJournal(runId),
    onSuccess: () => {
      toast({ title: "Accounting journal generated" });
      qc.invalidateQueries({ queryKey: ["accounting-journals"] });
    },
  });

  const statutoryValidationMutation = useMutation({
    mutationFn: (fileType: string) => payrollApi.validateStatutoryFile({ payroll_run_id: selectedRun!.id, file_type: fileType }),
    onSuccess: (response) => {
      toast({ title: "Statutory validation complete", description: `${response.data.status}: ${response.data.error_count} errors` });
    },
  });

  const statutoryTemplateMutation = useMutation({
    mutationFn: (templateType: string) => payrollApi.generateStatutoryTemplate(templateType),
    onSuccess: (response) => {
      toast({ title: "Template generated", description: response.data.file_url });
    },
  });

  const generatePdfMutation = useMutation({
    mutationFn: (recordId: number) => payrollApi.generatePayslipPdf(recordId),
    onSuccess: (response) => {
      toast({ title: "Payslip PDF generated", description: response.data.payslip_pdf_url });
      qc.invalidateQueries({ queryKey: ["run-records"] });
    },
    onError: () => toast({ title: "Could not generate payslip PDF", variant: "destructive" }),
  });

  const publishPayslipsMutation = useMutation({
    mutationFn: (runId: number) => payrollApi.publishPayslips(runId, { send_email: true }),
    onSuccess: (response) => {
      toast({ title: "Payslips published", description: `${response.data.total_payslips} payslips queued for email` });
    },
    onError: () => toast({ title: "Could not publish payslips", variant: "destructive" }),
  });

  const prevSlipMonth = () => {
    if (slipMonth === 1) { setSlipMonth(12); setSlipYear((y) => y - 1); }
    else setSlipMonth((m) => m - 1);
  };
  const nextSlipMonth = () => {
    if (slipMonth === 12) { setSlipMonth(1); setSlipYear((y) => y + 1); }
    else setSlipMonth((m) => m + 1);
  };
  const selectedPayslipRecord = (runRecords as PayslipRecord[] | undefined || []).find((record) => record.id === selectedRecordId);
  const selectedRunStatus = normalizeRunStatus(selectedRun?.status);
  const worksheetAction = (row: PayrollWorksheetRow, action: "hold" | "skip" | "clear" | "approve") => {
    if (!selectedRun) return;
    const needsReason = action === "hold" || action === "skip";
    const reason = needsReason ? window.prompt(`${action === "hold" ? "Hold" : "Skip"} reason for employee #${row.employee_id}`) : undefined;
    if (needsReason && !reason) return;
    worksheetRowMutation.mutate({ runId: selectedRun.id, rowId: row.id, action, reason: reason || undefined });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Payroll</h1>
        <p className="page-description">Configure salary setup, run monthly payroll, publish payslips, and review variance.</p>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b">
        {visibleTabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab === "wizard" ? "Setup Wizard" : tab === "run" ? "Run Payroll" : tab === "viewer" ? "Payslip Viewer" : tab === "variance" ? "Variance" : tab === "inputs" ? "Inputs" : tab === "statutory" ? "Statutory" : tab === "tax" ? "Tax" : "Real Cases"}
          </button>
        ))}
      </div>

      {activeTab === "viewer" && (
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

          <Card>
            <CardHeader>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <CardTitle className="text-base">Run Payslip Browser</CardTitle>
                  <CardDescription>Select a payroll run to render employee payslips, generate PDFs, and bulk publish by email.</CardDescription>
                </div>
                <Button
                  variant="outline"
                  disabled={!selectedRun || publishPayslipsMutation.isPending}
                  onClick={() => selectedRun && publishPayslipsMutation.mutate(selectedRun.id)}
                >
                  <Mail className="mr-2 h-4 w-4" />
                  Bulk publish
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex flex-wrap gap-2">
                {(runs as PayrollRun[] | undefined || []).slice(0, 8).map((run) => (
                  <Button
                    key={run.id}
                    variant={selectedRun?.id === run.id ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedRun(run)}
                  >
                    {MONTHS[run.month - 1]} {run.year}
                  </Button>
                ))}
              </div>
              {selectedRun && (
                <div className="overflow-x-auto rounded-md border">
                  <table className="w-full text-sm">
                    <thead className="border-b bg-muted/50">
                      <tr>
                        {["Employee", "Gross", "Deductions", "Net", "Status", "Actions"].map((h) => (
                          <th key={h} className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(runRecords as PayslipRecord[] | undefined || []).map((record) => (
                        <tr key={record.id} className={`border-b ${selectedRecordId === record.id ? "bg-muted/40" : ""}`}>
                          <td className="px-4 py-3 font-medium">{record.employee?.first_name} {record.employee?.last_name}<p className="text-xs text-muted-foreground">{record.employee?.employee_id}</p></td>
                          <td className="px-4 py-3">{formatCurrency(record.gross_salary)}</td>
                          <td className="px-4 py-3">{formatCurrency(record.total_deductions)}</td>
                          <td className="px-4 py-3 font-medium text-green-600">{formatCurrency(record.net_salary)}</td>
                          <td className="px-4 py-3"><Badge variant="outline">{record.status}</Badge></td>
                          <td className="px-4 py-3">
                            <div className="flex flex-wrap gap-2">
                              <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => setSelectedRecordId(record.id)}>
                                <Eye className="mr-1 h-3 w-3" /> Preview
                              </Button>
                              <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => generatePdfMutation.mutate(record.id)}>
                                PDF
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>

          {selectedPayslipRecord && (
            <Card className="payslip-print">
              <CardHeader>
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <CardTitle>Employee Payslip Preview</CardTitle>
                    <CardDescription>{selectedPayslipRecord.employee?.first_name} {selectedPayslipRecord.employee?.last_name} | {selectedRun ? `${MONTHS[selectedRun.month - 1]} ${selectedRun.year}` : "Selected run"}</CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => generatePdfMutation.mutate(selectedPayslipRecord.id)}>
                    <Download className="mr-2 h-4 w-4" />
                    Generate PDF
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-3 rounded-md bg-muted/30 p-4 text-sm sm:grid-cols-3">
                  <div><p className="text-muted-foreground">Employee</p><p className="font-medium">{selectedPayslipRecord.employee?.employee_id}</p></div>
                  <div><p className="text-muted-foreground">Gross</p><p className="font-medium">{formatCurrency(selectedPayslipRecord.gross_salary)}</p></div>
                  <div><p className="text-muted-foreground">Net Pay</p><p className="font-medium text-green-600">{formatCurrency(selectedPayslipRecord.net_salary)}</p></div>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="rounded-md border p-4">
                    <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">Earnings</h3>
                    {(selectedPayslipRecord.earnings || []).length === 0 ? (
                      <p className="text-sm text-muted-foreground">No earning components</p>
                    ) : (
                      <div className="space-y-2">
                        {(selectedPayslipRecord.earnings || []).map((item, index) => (
                          <div key={`${item.component_name}-${index}`} className="flex justify-between text-sm">
                            <span>{item.component_name}</span>
                            <span>{formatCurrency(item.amount)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="rounded-md border p-4">
                    <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">Deductions</h3>
                    {(selectedPayslipRecord.deductions || []).length === 0 ? (
                      <p className="text-sm text-muted-foreground">No deduction components</p>
                    ) : (
                      <div className="space-y-2">
                        {(selectedPayslipRecord.deductions || []).map((item, index) => (
                          <div key={`${item.component_name}-${index}`} className="flex justify-between text-sm">
                            <span>{item.component_name}</span>
                            <span>{formatCurrency(item.amount)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    <div className="mt-3 flex justify-between border-t pt-3 text-sm font-medium"><span>Total deductions</span><span>{formatCurrency(selectedPayslipRecord.total_deductions)}</span></div>
                  </div>
                  <div className="rounded-md border p-4">
                    <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">Employer Contributions</h3>
                    {(selectedPayslipRecord.employer_contributions || []).length === 0 ? (
                      <p className="text-sm text-muted-foreground">No employer contribution components</p>
                    ) : (
                      <div className="space-y-2">
                        {(selectedPayslipRecord.employer_contributions || []).map((item, index) => (
                          <div key={`${item.component_name}-${index}`} className="flex justify-between text-sm">
                            <span>{item.component_name}</span>
                            <span>{formatCurrency(item.amount)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="rounded-md border p-4">
                    <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">YTD</h3>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div><p className="text-muted-foreground">Gross</p><p className="font-medium">{formatCurrency(selectedPayslipRecord.ytd?.gross_salary || 0)}</p></div>
                      <div><p className="text-muted-foreground">Net</p><p className="font-medium">{formatCurrency(selectedPayslipRecord.ytd?.net_salary || 0)}</p></div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {loadingSlip ? (
            <Card><CardContent className="p-8 text-center"><div className="h-40 skeleton rounded" /></CardContent></Card>
          ) : !payslip ? (
            <Card className="payslip-print">
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
                <Button variant="outline" size="sm" className="no-print mt-3" onClick={() => window.print()}>
                  Print payslip
                </Button>
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
                      <p className="font-medium">{payslip.working_days ?? "-"}</p>
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

      {!isEmployee && activeTab === "run" && (
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

          <div className="grid gap-4 md:grid-cols-4">
            {[
              ["Selected run", selectedRun ? `${MONTHS[selectedRun.month - 1]} ${selectedRun.year}` : "Choose a run"],
              ["Employees", selectedRun?.total_employees ?? 0],
              ["Gross", formatCurrency(selectedRun?.total_gross || 0)],
              ["Net", formatCurrency(selectedRun?.total_net || 0)],
            ].map(([label, value]) => (
              <Card key={label}>
                <CardContent className="p-4">
                  <p className="text-sm text-muted-foreground">{label}</p>
                  <p className="mt-1 text-xl font-semibold">{value}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {selectedRun && (
            <Card>
              <CardHeader>
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <CardTitle className="text-base">Pre-Run Checks Dashboard</CardTitle>
                    <CardDescription>Blockers must be cleared before approval and publish.</CardDescription>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Button variant="outline" size="sm" onClick={() => worksheetMutation.mutate(selectedRun.id)} disabled={worksheetMutation.isPending}>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Reprocess
                    </Button>
                    <Button size="sm" onClick={() => runStatusMutation.mutate({ id: selectedRun.id, action: "approve" })} disabled={runStatusMutation.isPending || selectedRunStatus !== "calculated"}>
                      <CheckCircle2 className="mr-2 h-4 w-4" />
                      Approve run
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => runStatusMutation.mutate({ id: selectedRun.id, action: "approve", forceApprove: true })} disabled={runStatusMutation.isPending || selectedRunStatus !== "calculated"}>
                      Force approve
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => runStatusMutation.mutate({ id: selectedRun.id, action: "lock" })} disabled={runStatusMutation.isPending || selectedRunStatus !== "approved"}>
                      Lock
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => runStatusMutation.mutate({ id: selectedRun.id, action: "paid" })} disabled={runStatusMutation.isPending || selectedRunStatus !== "locked"}>
                      Mark paid
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="grid gap-3 md:grid-cols-3">
                {(preRunChecks as PayrollPreRunCheck[] | undefined || []).map((check) => (
                  <div key={check.id} className="rounded-md border p-3 text-sm">
                    <div className="flex items-center justify-between gap-3">
                      <p className="font-medium">{check.check_name}</p>
                      <Badge variant={check.status === "Passed" ? "secondary" : check.blocker ? "destructive" : "outline"}>{check.status}</Badge>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">{check.message || check.check_type}</p>
                  </div>
                ))}
                {!(preRunChecks as PayrollPreRunCheck[] | undefined)?.length && (
                  <div className="rounded-md border p-4 text-sm text-muted-foreground md:col-span-3">
                    No pre-run checks generated yet. Run payroll or process the worksheet to populate checks.
                  </div>
                )}
              </CardContent>
            </Card>
          )}

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
                            {normalizeRunStatus(run.status) === "calculated" && (
                              <Button
                                size="sm"
                                className="bg-green-600 hover:bg-green-700 h-7 text-xs"
                                onClick={(e) => { e.stopPropagation(); runStatusMutation.mutate({ id: run.id, action: "approve" }); }}
                                disabled={runStatusMutation.isPending}
                              >
                                <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
                                Approve
                              </Button>
                            )}
                            {normalizeRunStatus(run.status) === "approved" && (
                              <Button
                                variant="outline"
                                size="sm"
                                className="h-7 text-xs"
                                onClick={(e) => { e.stopPropagation(); runStatusMutation.mutate({ id: run.id, action: "lock" }); }}
                                disabled={runStatusMutation.isPending}
                              >
                                Lock
                              </Button>
                            )}
                            {normalizeRunStatus(run.status) === "locked" && (
                              <Button
                                variant="outline"
                                size="sm"
                                className="h-7 text-xs"
                                onClick={(e) => { e.stopPropagation(); runStatusMutation.mutate({ id: run.id, action: "paid" }); }}
                                disabled={runStatusMutation.isPending}
                              >
                                Paid
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
          {selectedRun && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <CardTitle className="text-base">Payroll Worksheet</CardTitle>
                    <CardDescription>Per-employee calculation status, input status, and approval readiness.</CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => worksheetMutation.mutate(selectedRun.id)} disabled={worksheetMutation.isPending}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Process worksheet
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="border-b bg-muted/50">
                      <tr>
                        {["Employee", "Input", "Calculation", "Approval", "Net", "Worksheet Actions"].map((h) => (
                          <th key={h} className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {(worksheetRows as PayrollWorksheetRow[] | undefined || []).map((row) => (
                        <tr key={row.id} className="border-b">
                          <td className="px-4 py-3">
                            <span className="font-medium">#{row.employee_id}</span>
                            <p className="text-xs text-muted-foreground">{row.status}</p>
                          </td>
                          <td className="px-4 py-3"><Badge variant="outline">{row.input_status}</Badge></td>
                          <td className="px-4 py-3">{row.calculation_status}</td>
                          <td className="px-4 py-3"><Badge variant={row.approval_status === "Approved" ? "secondary" : row.approval_status === "On Hold" || row.approval_status === "Skipped" ? "destructive" : "outline"}>{row.approval_status}</Badge></td>
                          <td className="px-4 py-3">{formatCurrency(row.net_salary)}</td>
                          <td className="px-4 py-3">
                            <div className="flex flex-wrap items-center gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                className="h-7 text-xs"
                                onClick={() => worksheetAction(row, "approve")}
                                disabled={worksheetRowMutation.isPending || !!row.hold_reason || !!row.skip_reason || row.approval_status === "Approved"}
                              >
                                Approve
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                className="h-7 text-xs"
                                onClick={() => worksheetAction(row, "hold")}
                                disabled={worksheetRowMutation.isPending || row.approval_status === "Approved"}
                              >
                                <PauseCircle className="mr-1 h-3 w-3" />
                                Hold
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                className="h-7 text-xs"
                                onClick={() => worksheetAction(row, "skip")}
                                disabled={worksheetRowMutation.isPending || row.approval_status === "Approved"}
                              >
                                Skip
                              </Button>
                              {(row.hold_reason || row.skip_reason) && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-7 text-xs"
                                  onClick={() => worksheetAction(row, "clear")}
                                  disabled={worksheetRowMutation.isPending}
                                >
                                  Clear
                                </Button>
                              )}
                              <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => worksheetMutation.mutate(selectedRun.id)} disabled={worksheetMutation.isPending}>
                                Reprocess
                              </Button>
                            </div>
                            {row.hold_reason && <p className="mt-1 text-xs text-muted-foreground">{row.hold_reason}</p>}
                            {row.skip_reason && <p className="mt-1 text-xs text-muted-foreground">{row.skip_reason}</p>}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {selectedRun && (
            <div className="grid gap-4 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <CardTitle className="text-base">Payments</CardTitle>
                      <CardDescription>Generate bank advice, track UTR status, and failed payouts.</CardDescription>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => paymentBatchMutation.mutate(selectedRun.id)} disabled={paymentBatchMutation.isPending}>
                      Generate batch
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  {(paymentBatches as { id: number; total_amount: number; status: string; generated_file_url?: string }[] | undefined || []).map((batch) => (
                    <div key={batch.id} className="flex items-center justify-between rounded-md border p-3 text-sm">
                      <div>
                        <p className="font-medium">Batch #{batch.id} - {formatCurrency(batch.total_amount)}</p>
                        <p className="text-muted-foreground">{batch.generated_file_url || "File pending"}</p>
                      </div>
                      <Badge variant="outline">{batch.status}</Badge>
                    </div>
                  ))}
                  <div className="flex gap-2">
                    <Input placeholder="Batch ID for status import" value={paymentBatchId} onChange={(event) => setPaymentBatchId(event.target.value)} />
                    <Button variant="outline" onClick={() => paymentStatusMutation.mutate()} disabled={!paymentBatchId}>
                      Check import
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <CardTitle className="text-base">Accounting</CardTitle>
                      <CardDescription>Generate balanced payroll GL journals for finance posting.</CardDescription>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => journalMutation.mutate(selectedRun.id)} disabled={journalMutation.isPending}>
                      Generate journal
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  {(accountingJournals as { id: number; total_debit: number; total_credit: number; status: string }[] | undefined || []).map((journal) => (
                    <div key={journal.id} className="flex items-center justify-between rounded-md border p-3 text-sm">
                      <div>
                        <p className="font-medium">Journal #{journal.id}</p>
                        <p className="text-muted-foreground">
                          Dr {formatCurrency(journal.total_debit)} / Cr {formatCurrency(journal.total_credit)}
                        </p>
                      </div>
                      <Badge variant="outline">{journal.status}</Badge>
                    </div>
                  ))}
                  <div className="flex flex-wrap gap-2">
                    {["pf_ecr", "esi", "pt", "tds_24q", "form_16"].map((type) => (
                      <Button key={type} variant="outline" size="sm" onClick={() => statutoryValidationMutation.mutate(type)}>
                        Validate {type}
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {selectedRun && runRecords && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">
                  {MONTHS[selectedRun.month - 1]} {selectedRun.year} - Employee Records
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

      {!isEmployee && activeTab === "variance" && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <CardTitle className="text-base">Variance Report</CardTitle>
                  <CardDescription>Compare each payroll run against previous month and flag large deviations.</CardDescription>
                </div>
                <Button variant="outline" size="sm" onClick={() => refetchVariance()} disabled={!selectedRun}>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh variance
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-2">
                {(runs as PayrollRun[] | undefined || []).slice(0, 10).map((run) => (
                  <Button key={run.id} variant={selectedRun?.id === run.id ? "default" : "outline"} size="sm" onClick={() => setSelectedRun(run)}>
                    {MONTHS[run.month - 1]} {run.year}
                  </Button>
                ))}
              </div>
              <div className="grid gap-3 md:grid-cols-4">
                {[
                  ["Rows", (runVariance as unknown[] | undefined)?.length || 0],
                  ["High/Critical", (runVariance as PayrollVariance[] | undefined || []).filter((item) => ["High", "Critical"].includes(item.severity)).length],
                  ["Current gross", formatCurrency(selectedRun?.total_gross || 0)],
                  ["Current net", formatCurrency(selectedRun?.total_net || 0)],
                ].map(([label, value]) => (
                  <div key={label} className="rounded-md border p-3 text-sm">
                    <p className="text-muted-foreground">{label}</p>
                    <p className="mt-1 text-xl font-semibold">{value}</p>
                  </div>
                ))}
              </div>
              <div className="overflow-x-auto rounded-md border">
                <table className="w-full text-sm">
                  <thead className="border-b bg-muted/50">
                    <tr>
                      {["Employee", "Gross Previous", "Gross Current", "Net Previous", "Net Current", "Deviation", "Flag"].map((h) => (
                        <th key={h} className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-muted-foreground">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(runVariance as PayrollVariance[] | undefined || []).map((item) => (
                      <tr key={item.id} className="border-b hover:bg-muted/30">
                        <td className="px-4 py-3">#{item.employee_id}</td>
                        <td className="px-4 py-3">{formatCurrency(item.previous_gross)}</td>
                        <td className="px-4 py-3">{formatCurrency(item.current_gross)}</td>
                        <td className="px-4 py-3">{formatCurrency(item.previous_net)}</td>
                        <td className="px-4 py-3">{formatCurrency(item.current_net)}</td>
                        <td className="px-4 py-3">
                          <p>{Number(item.gross_delta_percent).toFixed(1)}% gross</p>
                          <p className="text-xs text-muted-foreground">{Number(item.net_delta_percent).toFixed(1)}% net</p>
                        </td>
                        <td className="px-4 py-3">
                          <Badge variant={["High", "Critical"].includes(item.severity) ? "destructive" : "outline"}>
                            {item.severity}
                          </Badge>
                          {item.reason && <p className="mt-1 text-xs text-muted-foreground">{item.reason}</p>}
                        </td>
                      </tr>
                    ))}
                    {!(runVariance as PayrollVariance[] | undefined)?.length && (
                      <tr><td colSpan={7} className="px-4 py-10 text-center text-muted-foreground">Select a run to view month-on-month payroll variance.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {!isEmployee && activeTab === "inputs" && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <CardTitle className="text-base">Payroll Inputs</CardTitle>
                  <CardDescription>Reconcile attendance, LOP, overtime, and leave encashment before payroll approval.</CardDescription>
                </div>
                <div className="flex flex-wrap items-end gap-2">
                  <div className="space-y-1.5">
                    <Label>Period</Label>
                    <select
                      className="h-10 rounded-md border bg-background px-3 text-sm"
                      value={inputPeriodId || selectedInputPeriod || ""}
                      onChange={(event) => setInputPeriodId(event.target.value)}
                    >
                      {(payrollPeriods as { id: number; month: number; year: number; status: string }[] | undefined || []).map((period) => (
                        <option key={period.id} value={period.id}>
                          {MONTHS[period.month - 1]} {period.year} - {period.status}
                        </option>
                      ))}
                    </select>
                  </div>
                  <Button onClick={() => reconcileMutation.mutate()} disabled={!selectedInputPeriod || reconcileMutation.isPending}>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Reconcile and lock
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 md:grid-cols-4">
                {[
                  ["Inputs", (payrollInputs as unknown[] | undefined)?.length || 0],
                  ["LOP Adjustments", (lopAdjustments as unknown[] | undefined)?.length || 0],
                  ["OT Lines", (overtimeLines as unknown[] | undefined)?.length || 0],
                  ["Encashment", (encashmentLines as unknown[] | undefined)?.length || 0],
                ].map(([label, count]) => (
                  <div key={label} className="rounded-md border p-3 text-sm">
                    <p className="text-muted-foreground">{label}</p>
                    <p className="text-2xl font-semibold">{count}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">LOP Adjustment</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input placeholder="Employee ID" value={lopEmployeeId} onChange={(event) => setLopEmployeeId(event.target.value)} />
                <Input placeholder="Days" value={lopDays} onChange={(event) => setLopDays(event.target.value)} />
                <Button onClick={() => lopMutation.mutate()} disabled={!selectedInputPeriod || !lopEmployeeId}>
                  Add LOP
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Overtime Pay</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input placeholder="Employee ID" value={otEmployeeId} onChange={(event) => setOtEmployeeId(event.target.value)} />
                <Input placeholder="Hours" value={otHours} onChange={(event) => setOtHours(event.target.value)} />
                <Button onClick={() => otMutation.mutate()} disabled={!selectedInputPeriod || !otEmployeeId}>
                  Add OT
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Leave Encashment</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Input placeholder="Employee ID" value={encashEmployeeId} onChange={(event) => setEncashEmployeeId(event.target.value)} />
                <Input placeholder="Days" value={encashDays} onChange={(event) => setEncashDays(event.target.value)} />
                <Button onClick={() => encashMutation.mutate()} disabled={!selectedInputPeriod || !encashEmployeeId}>
                  Add Encashment
                </Button>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Attendance Inputs</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b bg-muted/50">
                    <tr>
                      {["Employee", "Working", "Payable", "Paid Leave", "LOP", "OT", "Status"].map((h) => (
                        <th key={h} className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(payrollInputs as { id: number; employee_id: number; working_days: number; payable_days: number; paid_leave_days: number; lop_days: number; ot_hours: number; source_status: string }[] | undefined || []).map((item) => (
                      <tr key={item.id} className="border-b">
                        <td className="px-4 py-3">#{item.employee_id}</td>
                        <td className="px-4 py-3">{item.working_days}</td>
                        <td className="px-4 py-3">{item.payable_days}</td>
                        <td className="px-4 py-3">{item.paid_leave_days}</td>
                        <td className="px-4 py-3">{item.lop_days}</td>
                        <td className="px-4 py-3">{item.ot_hours}</td>
                        <td className="px-4 py-3"><Badge variant="outline">{item.source_status}</Badge></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {!isEmployee && activeTab === "wizard" && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Payroll Setup Wizard</CardTitle>
              <CardDescription>Complete the minimum production setup in order: legal entity, pay group, components, structure, tax, statutory profile.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 md:grid-cols-6">
                {[
                  ["Legal Entity", (legalEntities as unknown[] | undefined)?.length || 0],
                  ["Pay Group", (payGroups as unknown[] | undefined)?.length || 0],
                  ["Components", (salaryComponents as unknown[] | undefined)?.length || 0],
                  ["Structures", (salaryStructures as unknown[] | undefined)?.length || 0],
                  ["Tax Config", (taxCycles as unknown[] | undefined)?.length || 0],
                  ["Statutory Profile", (setupStatutoryProfiles as unknown[] | undefined)?.length || 0],
                ].map(([label, count], index) => (
                  <button
                    key={label}
                    type="button"
                    onClick={() => setWizardStep(index)}
                    className={`rounded-md border p-3 text-left text-sm transition-colors ${wizardStep === index ? "border-primary bg-primary/5" : "hover:bg-muted/50"}`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{label}</span>
                      {Number(count) > 0 ? <CheckCircle2 className="h-4 w-4 text-green-600" /> : <AlertTriangle className="h-4 w-4 text-amber-600" />}
                    </div>
                    <p className="mt-2 text-2xl font-semibold">{count}</p>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
            {wizardStep === 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base"><Building2 className="h-4 w-4" /> Legal Entity</CardTitle>
                  <CardDescription>Required for statutory filings, Form 16, challans, and payroll grouping.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div className="space-y-1.5"><Label>Legal name</Label><Input value={legalName} onChange={(event) => setLegalName(event.target.value)} /></div>
                    <div className="space-y-1.5"><Label>State</Label><Input value={legalState} onChange={(event) => setLegalState(event.target.value)} /></div>
                    <div className="space-y-1.5"><Label>PAN</Label><Input value={legalPan} onChange={(event) => setLegalPan(event.target.value.toUpperCase())} /></div>
                    <div className="space-y-1.5"><Label>TAN</Label><Input value={legalTan} onChange={(event) => setLegalTan(event.target.value.toUpperCase())} /></div>
                  </div>
                  <Button onClick={() => legalEntityMutation.mutate()} disabled={legalEntityMutation.isPending || !legalName}>
                    Create legal entity
                  </Button>
                </CardContent>
              </Card>
            )}
            {wizardStep === 1 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base"><ClipboardCheck className="h-4 w-4" /> Pay Group</CardTitle>
                  <CardDescription>Defines pay frequency, cutoffs, tax regime, and legal entity mapping.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div className="space-y-1.5"><Label>Pay group name</Label><Input value={payGroupName} onChange={(event) => setPayGroupName(event.target.value)} /></div>
                    <div className="space-y-1.5"><Label>Code</Label><Input value={payGroupCode} onChange={(event) => setPayGroupCode(event.target.value.toUpperCase())} /></div>
                  </div>
                  <Button onClick={() => payGroupMutation.mutate()} disabled={payGroupMutation.isPending || !(legalEntities as LegalEntity[] | undefined)?.length}>
                    Create pay group
                  </Button>
                </CardContent>
              </Card>
            )}
            {wizardStep === 2 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base"><DollarSign className="h-4 w-4" /> Salary Components</CardTitle>
                  <CardDescription>Create earnings, deductions, reimbursements, and statutory payslip lines.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div className="space-y-1.5"><Label>Name</Label><Input value={componentName} onChange={(event) => setComponentName(event.target.value)} /></div>
                    <div className="space-y-1.5"><Label>Code</Label><Input value={componentCode} onChange={(event) => setComponentCode(event.target.value.toUpperCase())} /></div>
                    <div className="space-y-1.5">
                      <Label>Type</Label>
                      <select className="h-10 rounded-md border bg-background px-3 text-sm" value={componentType} onChange={(event) => setComponentType(event.target.value)}>
                        {["Earning", "Deduction", "Statutory", "Reimbursement"].map((type) => <option key={type}>{type}</option>)}
                      </select>
                    </div>
                    <div className="space-y-1.5"><Label>Monthly amount</Label><Input value={componentAmount} onChange={(event) => setComponentAmount(event.target.value)} /></div>
                  </div>
                  <Button onClick={() => componentMutation.mutate()} disabled={componentMutation.isPending}>
                    Create component
                  </Button>
                </CardContent>
              </Card>
            )}
            {wizardStep === 3 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base"><Settings2 className="h-4 w-4" /> Salary Structure</CardTitle>
                  <CardDescription>Build a structure from active components. Formula and cap/floor rules remain in backend setup.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div className="space-y-1.5"><Label>Structure name</Label><Input value={structureName} onChange={(event) => setStructureName(event.target.value)} /></div>
                    <div className="space-y-1.5"><Label>Version</Label><Input value={structureVersion} onChange={(event) => setStructureVersion(event.target.value)} /></div>
                  </div>
                  <Button onClick={() => structureMutation.mutate()} disabled={structureMutation.isPending || !(salaryComponents as SalaryComponent[] | undefined)?.length}>
                    Create structure from active components
                  </Button>
                </CardContent>
              </Card>
            )}
            {wizardStep === 4 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base"><FileText className="h-4 w-4" /> Tax Config</CardTitle>
                  <CardDescription>Open the current financial-year declaration/projection cycle.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button onClick={() => taxCycleMutation.mutate()} disabled={taxCycleMutation.isPending}>
                    Open current FY tax cycle
                  </Button>
                  {activeTaxCycle && <p className="rounded-md border p-3 text-sm">Active cycle: <span className="font-medium">{activeTaxCycle.name}</span></p>}
                </CardContent>
              </Card>
            )}
            {wizardStep === 5 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base"><ShieldCheck className="h-4 w-4" /> Statutory Profiles</CardTitle>
                  <CardDescription>Bind PF/ESI/PT/TDS registration details to the legal entity.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div className="space-y-1.5"><Label>State / TAN circle</Label><Input value={legalState} onChange={(event) => setLegalState(event.target.value)} /></div>
                    <div className="space-y-1.5"><Label>Effective from</Label><Input type="date" value={ruleEffectiveFrom} onChange={(event) => setRuleEffectiveFrom(event.target.value)} /></div>
                  </div>
                  <Button onClick={() => setupStatutoryProfileMutation.mutate()} disabled={setupStatutoryProfileMutation.isPending || !(legalEntities as LegalEntity[] | undefined)?.length}>
                    Create statutory profile
                  </Button>
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Setup Health</CardTitle>
                <CardDescription>What payroll can use right now.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  ...(legalEntities as LegalEntity[] | undefined || []).map((item) => ({ id: `le-${item.id}`, title: item.legal_name, detail: `${item.state || "-"} | PAN ${item.pan || "-"}`, type: "Legal Entity" })),
                  ...(payGroups as { id: number; name: string; code: string; pay_frequency: string }[] | undefined || []).map((item) => ({ id: `pg-${item.id}`, title: item.name, detail: `${item.code} | ${item.pay_frequency}`, type: "Pay Group" })),
                  ...(salaryComponents as SalaryComponent[] | undefined || []).slice(0, 6).map((item) => ({ id: `sc-${item.id}`, title: item.name, detail: `${item.code} | ${formatCurrency(item.amount || 0)}`, type: item.component_type })),
                  ...(salaryStructures as SalaryStructure[] | undefined || []).map((item) => ({ id: `ss-${item.id}`, title: item.name, detail: `v${item.version} | ${item.components?.length || 0} components`, type: "Structure" })),
                ].slice(0, 12).map((item) => (
                  <div key={item.id} className="flex items-center justify-between rounded-md border p-3 text-sm">
                    <div><p className="font-medium">{item.title}</p><p className="text-muted-foreground">{item.detail}</p></div>
                    <Badge variant="outline">{item.type}</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Pay Groups and Calendar</CardTitle>
              <CardDescription>Set up monthly payroll groups before running payroll.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <Label>Pay group name</Label>
                  <Input value={payGroupName} onChange={(event) => setPayGroupName(event.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label>Code</Label>
                  <Input value={payGroupCode} onChange={(event) => setPayGroupCode(event.target.value)} />
                </div>
              </div>
              <Button onClick={() => payGroupMutation.mutate()} disabled={payGroupMutation.isPending}>
                Create pay group
              </Button>
              <div className="space-y-2">
                {(payGroups as { id: number; name: string; code: string; pay_frequency: string }[] | undefined)?.map((item) => (
                  <div key={item.id} className="flex items-center justify-between rounded-md border p-3 text-sm">
                    <span className="font-medium">{item.name}</span>
                    <Badge variant="outline">{item.code} - {item.pay_frequency}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Salary Templates</CardTitle>
              <CardDescription>Create salary structure shells and assign components from backend setup.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <Label>Template name</Label>
                  <Input value={templateName} onChange={(event) => setTemplateName(event.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label>Code</Label>
                  <Input value={templateCode} onChange={(event) => setTemplateCode(event.target.value)} />
                </div>
              </div>
              <Button onClick={() => salaryTemplateMutation.mutate()} disabled={salaryTemplateMutation.isPending}>
                Create template
              </Button>
              <div className="space-y-2">
                {(salaryTemplates as { id: number; name: string; code: string; components?: unknown[] }[] | undefined || []).map((item) => (
                  <div key={item.id} className="flex items-center justify-between rounded-md border p-3 text-sm">
                    <span className="font-medium">{item.name}</span>
                    <Badge variant="outline">{item.code} - {item.components?.length || 0} components</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="text-base">Periods and Accounting Setup</CardTitle>
              <CardDescription>Pay periods, bank advice, payment batches, and GL journals are now available through payroll setup flows.</CardDescription>
            </CardHeader>
            <CardContent className="grid gap-3 md:grid-cols-4">
              {[
                ["Periods", (payrollPeriods as unknown[] | undefined)?.length || 0],
                ["Pay Groups", (payGroups as unknown[] | undefined)?.length || 0],
                ["Templates", (salaryTemplates as unknown[] | undefined)?.length || 0],
                ["Current Year", runYear],
              ].map(([label, count]) => (
                <div key={label} className="rounded-md border p-3 text-sm">
                  <p className="text-muted-foreground">{label}</p>
                  <p className="text-2xl font-semibold">{count}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
        </div>
      )}

      {!isEmployee && activeTab === "statutory" && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <CardTitle className="text-base">Statutory Engine</CardTitle>
                  <CardDescription>PF, ESI, PT, LWF, gratuity rules, challans, and return validation.</CardDescription>
                </div>
                <Button onClick={() => seedStatutoryMutation.mutate()} disabled={seedStatutoryMutation.isPending}>
                  <ShieldCheck className="h-4 w-4 mr-2" />
                  Create rules
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3 md:grid-cols-5">
                {[
                  ["PF Rules", (pfRules as unknown[] | undefined)?.length || 0],
                  ["ESI Rules", (esiRules as unknown[] | undefined)?.length || 0],
                  ["PT Slabs", (ptSlabs as unknown[] | undefined)?.length || 0],
                  ["LWF Slabs", (lwfSlabs as unknown[] | undefined)?.length || 0],
                  ["Gratuity", (gratuityRules as unknown[] | undefined)?.length || 0],
                ].map(([label, count]) => (
                  <div key={label} className="rounded-md border p-3 text-sm">
                    <p className="text-muted-foreground">{label}</p>
                    <p className="text-2xl font-semibold">{count}</p>
                  </div>
                ))}
              </div>
              <div className="grid gap-3 md:grid-cols-5">
                <div className="space-y-1.5">
                  <Label>State</Label>
                  <Input value={statutoryState} onChange={(event) => setStatutoryState(event.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label>Effective from</Label>
                  <Input type="date" value={ruleEffectiveFrom} onChange={(event) => setRuleEffectiveFrom(event.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label>PT amount</Label>
                  <Input value={ptAmount} onChange={(event) => setPtAmount(event.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label>LWF employee</Label>
                  <Input value={lwfEmployeeAmount} onChange={(event) => setLwfEmployeeAmount(event.target.value)} />
                </div>
                <div className="space-y-1.5">
                  <Label>LWF employer</Label>
                  <Input value={lwfEmployerAmount} onChange={(event) => setLwfEmployerAmount(event.target.value)} />
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {["pf_ecr", "esi", "pt", "tds_24q", "form_16"].map((type) => (
                  <Button key={type} variant="outline" size="sm" onClick={() => statutoryTemplateMutation.mutate(type)}>
                    Template {type}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Active Rules</CardTitle>
                <CardDescription>Current statutory setup used by payroll calculations.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  ...(pfRules as { id: number; name: string; wage_ceiling?: number; employee_rate?: number }[] | undefined || []).map((item) => ({
                    id: `pf-${item.id}`,
                    title: item.name,
                    detail: `PF ceiling ${formatCurrency(item.wage_ceiling || 0)} at ${item.employee_rate}%`,
                    type: "PF",
                  })),
                  ...(esiRules as { id: number; name: string; wage_threshold?: number; employee_rate?: number }[] | undefined || []).map((item) => ({
                    id: `esi-${item.id}`,
                    title: item.name,
                    detail: `ESI threshold ${formatCurrency(item.wage_threshold || 0)} at ${item.employee_rate}%`,
                    type: "ESI",
                  })),
                  ...(ptSlabs as { id: number; state: string; salary_from?: number; employee_amount?: number }[] | undefined || []).map((item) => ({
                    id: `pt-${item.id}`,
                    title: `${item.state} PT`,
                    detail: `From ${formatCurrency(item.salary_from || 0)} deduct ${formatCurrency(item.employee_amount || 0)}`,
                    type: "PT",
                  })),
                  ...(lwfSlabs as { id: number; state: string; employee_amount?: number; employer_amount?: number }[] | undefined || []).map((item) => ({
                    id: `lwf-${item.id}`,
                    title: `${item.state} LWF`,
                    detail: `Employee ${formatCurrency(item.employee_amount || 0)}, employer ${formatCurrency(item.employer_amount || 0)}`,
                    type: "LWF",
                  })),
                  ...(gratuityRules as { id: number; name: string; days_per_year?: number; min_service_years?: number }[] | undefined || []).map((item) => ({
                    id: `gratuity-${item.id}`,
                    title: item.name,
                    detail: `${item.days_per_year} days after ${item.min_service_years} years`,
                    type: "Gratuity",
                  })),
                ].slice(0, 12).map((item) => (
                  <div key={item.id} className="flex items-center justify-between rounded-md border p-3 text-sm">
                    <div>
                      <p className="font-medium">{item.title}</p>
                      <p className="text-muted-foreground">{item.detail}</p>
                    </div>
                    <Badge variant="outline">{item.type}</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Challans</CardTitle>
                <CardDescription>Generated statutory payment records and validation status.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {(challans as { id: number; challan_type: string; amount: number; due_date: string; status: string }[] | undefined)?.length ? (
                  (challans as { id: number; challan_type: string; amount: number; due_date: string; status: string }[]).map((item) => (
                    <div key={item.id} className="flex items-center justify-between rounded-md border p-3 text-sm">
                      <div>
                        <p className="font-medium">{item.challan_type} - {formatCurrency(item.amount)}</p>
                        <p className="text-muted-foreground">Due {formatDate(item.due_date)}</p>
                      </div>
                      <Badge variant="outline">{item.status}</Badge>
                    </div>
                  ))
                ) : (
                  <div className="rounded-md border p-6 text-center text-sm text-muted-foreground">
                    No challans generated yet
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {!isEmployee && activeTab === "tax" && (
        <div className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Tax Declarations</CardTitle>
              <CardDescription>Declare investments and submit proof links for payroll verification.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {!activeTaxCycle ? (
                <Button onClick={() => taxCycleMutation.mutate()} disabled={taxCycleMutation.isPending}>
                  Open current FY cycle
                </Button>
              ) : (
                <>
                  <div className="rounded-md border p-3 text-sm">
                    <p className="font-medium">{activeTaxCycle.name}</p>
                    <p className="text-muted-foreground">Proof due {formatDate(activeTaxCycle.proof_due_date)}</p>
                  </div>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div className="space-y-1.5">
                      <Label>Section</Label>
                      <Input value={taxSection} onChange={(event) => setTaxSection(event.target.value)} />
                    </div>
                    <div className="space-y-1.5">
                      <Label>Amount</Label>
                      <Input value={taxAmount} onChange={(event) => setTaxAmount(event.target.value)} />
                    </div>
                  </div>
                  <Button onClick={() => taxDeclarationMutation.mutate()} disabled={taxDeclarationMutation.isPending}>
                    Submit declaration
                  </Button>
                </>
              )}

              {taxProjection && (
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="rounded-md border p-3">
                    <p className="text-muted-foreground">Declared</p>
                    <p className="font-semibold">{formatCurrency(taxProjection.declared_amount)}</p>
                  </div>
                  <div className="rounded-md border p-3">
                    <p className="text-muted-foreground">Projected TDS</p>
                    <p className="font-semibold">{formatCurrency(taxProjection.projected_tds)}</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Proof Workflow</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Input
                value={taxProofUrl}
                onChange={(event) => setTaxProofUrl(event.target.value)}
                placeholder="/uploads/tax/80c-proof.pdf"
              />
              {(taxDeclarations as { id: number; section: string; declared_amount: number; status: string; proofs?: unknown[] }[] | undefined)?.map((item) => (
                <div key={item.id} className="flex flex-col gap-3 rounded-md border p-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-medium">{item.section} - {formatCurrency(item.declared_amount)}</p>
                    <p className="text-sm text-muted-foreground">{item.status} - {item.proofs?.length || 0} proof(s)</p>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => taxProofMutation.mutate(item.id)}>
                    Submit proof
                  </Button>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      )}

      {!isEmployee && activeTab === "casebook" && (
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
