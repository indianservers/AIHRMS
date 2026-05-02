import { ShieldCheck } from "lucide-react";
import ModuleShell from "@/components/ModuleShell";

export default function BackgroundVerificationPage() {
  return (
    <ModuleShell
      title="Background Verification"
      description="Vendor setup, candidate consent, employee verification checks, events, and webhook callbacks."
      icon={ShieldCheck}
      metrics={[
        { label: "Vendors", value: "Configured" },
        { label: "Requests", value: "Tracked" },
        { label: "Checks", value: "Audited" },
      ]}
      items={[
        { title: "Vendor integrations", description: "Manage BGV vendor details and references", status: "Active" },
        { title: "Verification requests", description: "Initiate, consent, submit, and monitor requests", status: "Active" },
        { title: "Connector events", description: "Track status updates and evidence from providers", status: "Active" },
      ]}
    />
  );
}
