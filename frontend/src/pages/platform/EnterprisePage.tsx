import { useEffect } from "react";
import { Network } from "lucide-react";
import ModuleShell from "@/components/ModuleShell";

export default function EnterprisePage() {
  useEffect(() => { document.title = "Enterprise · AI HRMS"; }, []);
  return (
    <ModuleShell
      title="Enterprise Platform"
      description="Integration credentials, webhooks, event queues, consent, privacy requests, retention, and legal holds."
      icon={Network}
      metrics={[
        { label: "Webhooks", value: "Fan-out" },
        { label: "Events", value: "Retryable" },
        { label: "Privacy", value: "Governed" },
      ]}
      items={[
        { title: "Integration events", description: "Queue and retry high-volume webhook events", status: "Active" },
        { title: "Consent and privacy", description: "Track consent, privacy requests, and retention policies", status: "Active" },
        { title: "Legal holds", description: "Preserve records for audit and investigation needs", status: "Active" },
      ]}
    />
  );
}
