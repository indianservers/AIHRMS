import { Link } from "react-router-dom";
import { BriefcaseBusiness, Building2, CheckCircle2, Sparkles, Target } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { getInstalledAppKeys, getSuiteName } from "@/appRegistry";
import { canAccessRoute } from "@/lib/roles";
import { useAuthStore } from "@/store/authStore";

const apps = [
  {
    key: "hrms",
    name: "AI HRMS",
    description: "Employees, payroll, attendance, leave, performance, documents, and HR operations.",
    href: "/hrms/dashboard",
    loginHref: "/hrms/login",
    icon: Building2,
    tone: "bg-blue-50 text-blue-700 border-blue-200",
  },
  {
    key: "crm",
    name: "VyaparaCRM",
    description: "Leads, contacts, companies, deals, sales pipeline, activities, quotations, and support.",
    href: "/crm",
    loginHref: "/crm/login",
    icon: BriefcaseBusiness,
    tone: "bg-emerald-50 text-emerald-700 border-emerald-200",
  },
  {
    key: "project_management",
    name: "KaryaFlow",
    description: "Projects, Kanban boards, tasks, milestones, time logs, files, reports, and client approvals.",
    href: "/project-management",
    loginHref: "/project-management/login",
    icon: Target,
    tone: "bg-violet-50 text-violet-700 border-violet-200",
  },
] as const;

export default function SuiteIndexPage() {
  const installed = getInstalledAppKeys();
  const { user } = useAuthStore();
  const visibleApps = apps.filter((app) => installed.includes(app.key));

  return (
    <div className="mx-auto max-w-6xl space-y-8 py-8">
      <div className="max-w-3xl">
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border bg-card px-3 py-1 text-sm text-muted-foreground">
          <Sparkles className="h-4 w-4 text-primary" />
          Common Business Suite
        </div>
        <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">{getSuiteName()}</h1>
        <p className="mt-3 text-muted-foreground">
          Select your product workspace. HRMS, CRM, and Project Management use separate menus, URLs, users, roles, and module tables while sharing the common platform shell.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {visibleApps.map((app) => {
          const canOpen = canAccessRoute(app.href, user?.role, user?.is_superuser);
          const targetHref = canOpen ? app.href : app.loginHref;
          return (
            <Card key={app.key} className="transition hover:border-primary/40 hover:shadow-md">
              <CardContent className="flex h-full flex-col p-5">
                <div className={`mb-5 flex h-12 w-12 items-center justify-center rounded-lg border ${app.tone}`}>
                  <app.icon className="h-6 w-6" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h2 className="text-lg font-semibold">{app.name}</h2>
                    <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  </div>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">{app.description}</p>
                  {!canOpen ? (
                    <p className="mt-3 rounded-md bg-muted px-3 py-2 text-xs text-muted-foreground">
                      Use this product's separate login to open its workspace.
                    </p>
                  ) : null}
                </div>
                <Button asChild className="mt-6 w-full">
                  <Link to={targetHref}>{canOpen ? "Open" : "Login to"} {app.name}</Link>
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
