import { UserCircle } from "lucide-react";
import ModuleShell from "@/components/ModuleShell";
import { useAuthStore } from "@/store/authStore";

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user);

  return (
    <ModuleShell
      title="Self-Service Profile"
      description={user?.email || "Employee profile, documents, attendance, leave, and payslips."}
      icon={UserCircle}
      metrics={[
        { label: "Open tasks", value: "3" },
        { label: "Leave balance", value: "18 days" },
        { label: "Documents", value: "7" },
      ]}
      items={[
        { title: "Personal information", description: "Review personal, job, bank, and document records", status: "ESS" },
        { title: "My attendance", description: "Daily punch, regularization, overtime, and calendar view", status: "Live" },
        { title: "My payslips", description: "Monthly payroll history and downloadable payslips", status: "Secure" },
      ]}
    />
  );
}
