import { useEffect, useState } from "react";
import { BarChart3, Building2, CheckCircle2, Kanban, Users } from "lucide-react";
import { api } from "@/services/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const metrics = [
  { label: "Leads", value: "Ready", icon: Users },
  { label: "Pipeline", value: "Ready", icon: Kanban },
  { label: "Reports", value: "Planned", icon: BarChart3 },
];

type CRMModuleInfo = {
  key: string;
  name: string;
  status: string;
  modules: string[];
};

export default function CRMHomePage() {
  const [moduleInfo, setModuleInfo] = useState<CRMModuleInfo | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<CRMModuleInfo>("/crm/module-info")
      .then((response) => setModuleInfo(response.data))
      .catch((err) => setError(err?.response?.data?.detail || "CRM backend is not reachable."));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-emerald-100 p-3 text-emerald-700">
              <Building2 className="h-6 w-6" />
            </div>
            <div>
              <h1 className="page-title">VyaparaCRM</h1>
              <p className="page-description">Leads, contacts, companies, deals, activities, quotations, campaigns, and support.</p>
            </div>
          </div>
        </div>
        <Badge className={moduleInfo?.status === "installed" ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"}>
          {moduleInfo?.status || "checking"}
        </Badge>
      </div>

      {error ? <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}

      <div className="grid gap-4 md:grid-cols-3">
        {metrics.map((metric) => (
          <Card key={metric.label}>
            <CardContent className="flex items-center gap-4 p-5">
              <div className="rounded-lg bg-emerald-100 p-3 text-emerald-700">
                <metric.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{metric.label}</p>
                <p className="text-xl font-semibold">{metric.value}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Shared CRM Backend Modules</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3 xl:grid-cols-4">
          {(moduleInfo?.modules || ["leads", "contacts", "companies", "deals", "pipelines", "activities"]).map((module) => (
            <div key={module} className="flex items-center gap-2 rounded-lg border bg-card p-3 text-sm">
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
              <span className="capitalize">{module.replace(/-/g, " ")}</span>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
