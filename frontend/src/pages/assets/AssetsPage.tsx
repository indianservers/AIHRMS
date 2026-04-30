import { Package } from "lucide-react";
import ModuleShell from "@/components/ModuleShell";

export default function AssetsPage() {
  return (
    <ModuleShell
      title="Asset Management"
      description="Track company assets, assignments, acknowledgements, repair status, and returns."
      icon={Package}
      metrics={[
        { label: "Assets", value: "148" },
        { label: "Assigned", value: "112" },
        { label: "Due returns", value: "6" },
      ]}
      items={[
        { title: "Laptop inventory", description: "Asset tags, serial numbers, warranties, and condition", status: "Tracked" },
        { title: "Employee assignments", description: "Issue, acknowledgement, return, and repair workflow", status: "Active" },
        { title: "Exit clearance", description: "Asset return checks linked to exit management", status: "Linked" },
      ]}
    />
  );
}
