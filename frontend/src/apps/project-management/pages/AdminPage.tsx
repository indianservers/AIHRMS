import { ShieldCheck } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const adminItems = [
  "Manage organizations",
  "Manage users and roles",
  "Project templates",
  "Task workflows",
  "Notification templates",
  "Audit logs",
  "Subscription plans placeholder",
  "Automation rules placeholder",
];

export default function AdminPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Admin</h1>
        <p className="page-description">Administrative controls for KaryaFlow configuration and governance.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {adminItems.map((item) => (
          <Card key={item}>
            <CardHeader><CardTitle className="flex items-center gap-2 text-base"><ShieldCheck className="h-4 w-4 text-primary" />{item}</CardTitle></CardHeader>
            <CardContent className="text-sm text-muted-foreground">Configuration workspace placeholder ready for CRUD wiring.</CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

