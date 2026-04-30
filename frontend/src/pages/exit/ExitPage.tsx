import { LogOut } from "lucide-react";
import ModuleShell from "@/components/ModuleShell";

export default function ExitPage() {
  return (
    <ModuleShell
      title="Exit Management"
      description="Resignation, notice period, approvals, clearance checklist, exit interview, and final settlement."
      icon={LogOut}
      metrics={[
        { label: "Open exits", value: "5" },
        { label: "Clearance pending", value: "13" },
        { label: "Settlements", value: "2" },
      ]}
      items={[
        { title: "Exit records", description: "Track resignation dates, last working day, status, and approval", status: "Open" },
        { title: "Clearance checklist", description: "HR, IT, finance, asset, and manager clearances", status: "Workflow" },
        { title: "Exit interviews", description: "Capture feedback, satisfaction scores, and rehire signal", status: "Insight" },
      ]}
    />
  );
}
