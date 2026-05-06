import { SlidersHorizontal } from "lucide-react";
import { usePageTitle } from "@/hooks/use-page-title";
import ModuleShell from "@/components/ModuleShell";

export default function CustomFieldsPage() {
  usePageTitle("Custom Fields");
  return (
    <ModuleShell
      title="Custom Fields & Forms"
      description="Dynamic fields, custom forms, submissions, approvals, and employee-specific structured data."
      icon={SlidersHorizontal}
      metrics={[
        { label: "Fields", value: "Dynamic" },
        { label: "Forms", value: "Configurable" },
        { label: "Submissions", value: "Reviewable" },
      ]}
      items={[
        { title: "Field definitions", description: "Create module-specific fields with validation", status: "Active" },
        { title: "Custom forms", description: "Build forms for HR workflows and employee data capture", status: "Active" },
        { title: "Review queue", description: "Approve, reject, and audit form submissions", status: "Active" },
      ]}
    />
  );
}
