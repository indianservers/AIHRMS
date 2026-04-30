import { Sparkles } from "lucide-react";
import ModuleShell from "@/components/ModuleShell";

export default function AIAssistantPage() {
  return (
    <ModuleShell
      title="AI HR Assistant"
      description="Policy Q&A, resume screening, attrition prediction, payroll anomaly checks, and helpdesk drafts."
      icon={Sparkles}
      metrics={[
        { label: "AI workflows", value: "5" },
        { label: "Policy answers", value: "Instant" },
        { label: "Risk models", value: "2" },
      ]}
      items={[
        { title: "Policy Q&A", description: "Answer employee questions from published company policies", status: "Available" },
        { title: "Resume screening", description: "Parse resumes and score candidates against job requirements", status: "Available" },
        { title: "Payroll anomaly detection", description: "Flag unusual monthly payroll variance before approval", status: "Available" },
      ]}
    />
  );
}
