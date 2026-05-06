import { Settings } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const settings = [
  "Organization profile",
  "Project statuses",
  "Task priorities",
  "Client visibility defaults",
  "Time approval rules",
  "Compact mode",
  "Notification preferences",
  "Import and export settings",
];

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Settings</h1>
        <p className="page-description">Workspace-level preferences and module configuration.</p>
      </div>
      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Settings className="h-5 w-5" />KaryaFlow settings</CardTitle></CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          {settings.map((item) => (
            <label key={item} className="flex items-center justify-between rounded-lg border p-4 text-sm">
              <span>{item}</span>
              <input type="checkbox" className="h-4 w-4" />
            </label>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

