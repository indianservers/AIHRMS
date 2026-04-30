import { FileText } from "lucide-react";
import ModuleShell from "@/components/ModuleShell";

export default function DocumentsPage() {
  return (
    <ModuleShell
      title="Documents & Letters"
      description="Manage policies, templates, generated letters, offer documents, and acknowledgements."
      icon={FileText}
      metrics={[
        { label: "Templates", value: "14" },
        { label: "Published policies", value: "9" },
        { label: "Generated letters", value: "52" },
      ]}
      items={[
        { title: "Letter templates", description: "Appointment, experience, relieving, increment, and offer letters", status: "Managed" },
        { title: "Policy library", description: "Versioned HR, IT, finance, and compliance policies", status: "Published" },
        { title: "Employee documents", description: "Generated documents and signed acknowledgement records", status: "Audited" },
      ]}
    />
  );
}
