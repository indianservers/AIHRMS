import { ClipboardCheck } from "lucide-react";
import ModuleShell from "@/components/ModuleShell";

export default function OnboardingPage() {
  return (
    <ModuleShell
      title="Onboarding"
      description="Templates, checklists, document collection, welcome emails, and policy acknowledgement."
      icon={ClipboardCheck}
      metrics={[
        { label: "Active onboardings", value: "11" },
        { label: "Pending docs", value: "19" },
        { label: "Policy acknowledgements", value: "86%" },
      ]}
      items={[
        { title: "New hire checklist", description: "HR, IT, manager, and employee onboarding tasks", status: "In progress" },
        { title: "Document collection", description: "Identity, education, experience, and bank documents", status: "Secure" },
        { title: "Welcome workflow", description: "Offer to onboarding handoff with email triggers", status: "Ready" },
      ]}
    />
  );
}
