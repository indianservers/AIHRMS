import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowRight,
  Banknote,
  CheckCircle2,
  Clock3,
  Cpu,
  Factory,
  FileText,
  Landmark,
  Layers3,
  ShieldCheck,
  Store,
  Target,
  Zap,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { targetsApi } from "@/services/api";
import { toast } from "@/hooks/use-toast";

type IndustryTarget = {
  id: number;
  name: string;
  headline: string;
  description?: string;
  icon?: string;
  color?: string;
};

type FeatureItem = {
  id: number;
  module: string;
  name: string;
  description?: string;
  is_highlight?: boolean;
};

type FeaturePlan = {
  id: number;
  code: string;
  name: string;
  tagline?: string;
  strength?: string;
  features: FeatureItem[];
};

type FeatureStatus = "Live" | "In progress" | "Planned";

const iconMap: Record<string, React.ElementType> = {
  cpu: Cpu,
  factory: Factory,
  landmark: Landmark,
  store: Store,
};

const colorMap: Record<string, string> = {
  blue: "border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-900 dark:bg-blue-950/40 dark:text-blue-300",
  green: "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-300",
  violet: "border-violet-200 bg-violet-50 text-violet-700 dark:border-violet-900 dark:bg-violet-950/40 dark:text-violet-300",
  amber: "border-amber-200 bg-amber-50 text-amber-700 dark:border-amber-900 dark:bg-amber-950/40 dark:text-amber-300",
};

const moduleRoutes: Record<string, { label: string; to: string }> = {
  "Core HR": { label: "Open Employees", to: "/employees" },
  "Time & Attendance": { label: "Open Attendance", to: "/attendance" },
  "Payroll and Expense": { label: "Open Payroll", to: "/payroll" },
  "Employee Self Service": { label: "Open Profile", to: "/profile" },
  "Employee Experience": { label: "Open Helpdesk", to: "/helpdesk" },
  "Business Performance": { label: "Open Performance", to: "/performance" },
  "Employee Performance": { label: "Open Performance", to: "/performance" },
};

const liveKeywords = [
  "org structure",
  "documents",
  "letters",
  "onboarding",
  "employee profiles",
  "access roles",
  "employee exit",
  "reports",
  "leave management",
  "attendance tracking",
  "shift management",
  "payroll automation",
  "statutory compliance",
  "expense management",
  "employee tax",
  "asset tracking",
  "people analytics",
  "custom roles",
  "performance reviews",
  "skills",
];

const inProgressKeywords = [
  "overtime",
  "notification",
  "public praise",
  "polls",
  "announcements",
  "surveys",
  "goals",
  "okrs",
  "feedback",
  "one-on-one",
  "compensation",
  "geo",
  "selfie",
];

const quickWins = [
  { label: "Simplified leave & attendance", value: "Attendance, shifts, regularization, leave", icon: CheckCircle2, to: "/attendance" },
  { label: "Tax and expense in 2 clicks", value: "Payroll, reimbursements, declarations", icon: Banknote, to: "/payroll" },
  { label: "A culture of recognition", value: "Praise, pulse, surveys roadmap", icon: Zap, to: "/performance" },
  { label: "Approvals from one window", value: "Leave, attendance, payroll, helpdesk", icon: ShieldCheck, to: "/dashboard" },
  { label: "Employee preferences", value: "Self-service profile and home", icon: Layers3, to: "/profile" },
  { label: "Faster issue resolution", value: "Helpdesk with AI suggested replies", icon: FileText, to: "/helpdesk" },
];

export default function TargetsPage() {
  const queryClient = useQueryClient();
  const [activePlan, setActivePlan] = useState<string>("essential");
  const [statusFilter, setStatusFilter] = useState<FeatureStatus | "All">("All");

  const { data: industries, isLoading: loadingIndustries } = useQuery({
    queryKey: ["target-industries"],
    queryFn: () => targetsApi.industries().then((r) => r.data as IndustryTarget[]),
  });

  const { data: plans, isLoading: loadingPlans, isError } = useQuery({
    queryKey: ["target-plans"],
    queryFn: () => targetsApi.plans().then((r) => r.data as FeaturePlan[]),
  });

  const highlightMutation = useMutation({
    mutationFn: ({ feature, value }: { feature: FeatureItem; value: boolean }) =>
      targetsApi.updateFeature(feature.id, { is_highlight: value }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["target-plans"] });
      toast({ title: "Target feature updated" });
    },
    onError: (err: any) => {
      toast({
        title: "Could not update target",
        description: err?.response?.data?.detail || "You may need target management permission.",
        variant: "destructive",
      });
    },
  });

  const selectedPlan = useMemo(
    () => plans?.find((plan) => plan.code === activePlan) || plans?.[0],
    [activePlan, plans]
  );

  const allFeatures = selectedPlan?.features || [];
  const filteredFeatures = allFeatures.filter((feature) => {
    if (statusFilter === "All") return true;
    return getFeatureStatus(feature) === statusFilter;
  });

  const groupedFeatures = useMemo(() => {
    const groups: Record<string, FeatureItem[]> = {};
    filteredFeatures.forEach((feature) => {
      groups[feature.module] = groups[feature.module] || [];
      groups[feature.module].push(feature);
    });
    return groups;
  }, [filteredFeatures]);

  const statusCounts = useMemo(() => {
    return allFeatures.reduce(
      (acc, feature) => {
        acc[getFeatureStatus(feature)] += 1;
        return acc;
      },
      { Live: 0, "In progress": 0, Planned: 0 } as Record<FeatureStatus, number>
    );
  }, [allFeatures]);

  return (
    <div className="space-y-5">
      <section className="overflow-hidden rounded-lg border bg-card">
        <div className="grid gap-0 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="border-b p-5 lg:border-b-0 lg:border-r">
            <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
              <div>
                <Badge variant="outline" className="mb-3">Target Operating Model</Badge>
                <h1 className="text-2xl font-semibold tracking-tight">HRMS feature implementation tracker</h1>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
                  Track the target capabilities inside the current HRMS, jump to the working module, and mark
                  the most important items for delivery focus.
                </p>
              </div>
              <Button variant="outline" size="sm" asChild>
                <Link to="/settings">Configure HRMS</Link>
              </Button>
            </div>
            <div className="mt-5 grid gap-3 sm:grid-cols-3">
              <Metric value={String(industries?.length || 0)} label="Industry targets" />
              <Metric value={String(plans?.length || 0)} label="Feature packages" />
              <Metric value={String(allFeatures.length)} label="Current controls" />
            </div>
          </div>
          <div className="bg-muted/30 p-5">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Experience targets</p>
            <div className="mt-4 grid gap-3">
              {quickWins.map((item) => (
                <Link key={item.label} to={item.to} className="flex items-center gap-3 rounded-lg border bg-background p-3 transition-colors hover:bg-muted">
                  <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/10 text-primary">
                    <item.icon className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">{item.label}</p>
                    <p className="text-xs text-muted-foreground">{item.value}</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-4">
        {loadingIndustries
          ? Array.from({ length: 4 }).map((_, index) => <div key={index} className="h-44 rounded-lg border skeleton" />)
          : industries?.map((industry) => {
              const Icon = iconMap[industry.icon || "cpu"] || Target;
              return (
                <Card key={industry.id} className="overflow-hidden">
                  <CardContent className="p-5">
                    <div className={`mb-4 inline-flex h-10 w-10 items-center justify-center rounded-md border ${colorMap[industry.color || "blue"]}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <h2 className="text-base font-semibold">{industry.name}</h2>
                    <p className="mt-2 text-sm leading-6 text-muted-foreground">{industry.headline}</p>
                    <p className="mt-4 line-clamp-3 text-xs leading-5 text-muted-foreground">{industry.description}</p>
                  </CardContent>
                </Card>
              );
            })}
      </section>

      <section className="rounded-lg border bg-card">
        <div className="flex flex-col gap-4 border-b p-4 xl:flex-row xl:items-center xl:justify-between">
          <div>
            <h2 className="text-lg font-semibold">Feature Packages</h2>
            <p className="text-sm text-muted-foreground">Use this as the implementation plan for target capabilities.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {plans?.map((plan) => (
              <button
                key={plan.code}
                onClick={() => setActivePlan(plan.code)}
                className={`rounded-md border px-3 py-2 text-sm font-medium transition-colors ${
                  selectedPlan?.code === plan.code
                    ? "border-primary bg-primary text-primary-foreground"
                    : "bg-background hover:bg-muted"
                }`}
              >
                {plan.name}
              </button>
            ))}
          </div>
        </div>

        {isError && (
          <div className="p-5 text-sm text-destructive">
            Targets could not be loaded. Check API permissions or run the backend database seed.
          </div>
        )}

        {loadingPlans ? (
          <div className="p-5"><div className="h-72 rounded-lg skeleton" /></div>
        ) : selectedPlan ? (
          <div className="grid gap-0 lg:grid-cols-[320px_1fr]">
            <div className="border-b p-5 lg:border-b-0 lg:border-r">
              <Badge>{selectedPlan.name}</Badge>
              <h3 className="mt-3 text-xl font-semibold">{selectedPlan.tagline}</h3>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">{selectedPlan.strength}</p>
              <div className="mt-5 grid gap-3">
                {(["Live", "In progress", "Planned"] as FeatureStatus[]).map((status) => (
                  <button
                    key={status}
                    type="button"
                    onClick={() => setStatusFilter(statusFilter === status ? "All" : status)}
                    className={`flex items-center justify-between rounded-md border px-3 py-2 text-left text-sm transition-colors ${
                      statusFilter === status ? "border-primary bg-primary/10" : "bg-background hover:bg-muted"
                    }`}
                  >
                    <span>{status}</span>
                    <Badge variant={status === "Live" ? "success" : status === "In progress" ? "warning" : "secondary"}>
                      {statusCounts[status]}
                    </Badge>
                  </button>
                ))}
              </div>
            </div>
            <div className="grid gap-4 p-5 md:grid-cols-2 xl:grid-cols-3">
              {Object.entries(groupedFeatures).map(([module, features]) => {
                const route = moduleRoutes[module] || { label: "Open Dashboard", to: "/dashboard" };
                return (
                  <Card key={module}>
                    <CardHeader className="border-b p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <CardTitle className="text-sm">{module}</CardTitle>
                          <p className="mt-1 text-xs text-muted-foreground">{features.length} capabilities</p>
                        </div>
                        <Button variant="outline" size="sm" asChild>
                          <Link to={route.to}>{route.label}</Link>
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-2 p-3">
                      {features.map((feature) => {
                        const status = getFeatureStatus(feature);
                        return (
                          <div key={feature.id} className="rounded-md border bg-background p-3">
                            <div className="flex items-start gap-2">
                              {status === "Live" ? (
                                <CheckCircle2 className="mt-0.5 h-4 w-4 text-green-600" />
                              ) : status === "In progress" ? (
                                <Clock3 className="mt-0.5 h-4 w-4 text-yellow-600" />
                              ) : (
                                <Target className="mt-0.5 h-4 w-4 text-muted-foreground" />
                              )}
                              <div className="min-w-0 flex-1">
                                <p className="text-sm font-medium">{feature.name}</p>
                                <div className="mt-2 flex flex-wrap items-center gap-2">
                                  <Badge variant={status === "Live" ? "success" : status === "In progress" ? "warning" : "secondary"}>
                                    {status}
                                  </Badge>
                                  {feature.is_highlight && <Badge variant="info">Priority</Badge>}
                                </div>
                              </div>
                            </div>
                            <div className="mt-3 flex justify-end">
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={() => highlightMutation.mutate({ feature, value: !feature.is_highlight })}
                                disabled={highlightMutation.isPending}
                              >
                                {feature.is_highlight ? "Remove priority" : "Make priority"}
                              </Button>
                            </div>
                          </div>
                        );
                      })}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="p-5 text-sm text-muted-foreground">No target plans found. Run database initialization to seed the target roadmap.</div>
        )}
      </section>
    </div>
  );
}

function Metric({ value, label }: { value: string; label: string }) {
  return (
    <div className="rounded-lg border bg-background p-4">
      <p className="text-2xl font-semibold">{value}</p>
      <p className="text-xs uppercase tracking-wide text-muted-foreground">{label}</p>
    </div>
  );
}

function getFeatureStatus(feature: FeatureItem): FeatureStatus {
  const name = feature.name.toLowerCase();
  if (liveKeywords.some((keyword) => name.includes(keyword))) return "Live";
  if (inProgressKeywords.some((keyword) => name.includes(keyword))) return "In progress";
  return "Planned";
}
