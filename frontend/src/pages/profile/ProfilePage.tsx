import { useQuery } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { authApi, employeeApi } from "@/services/api";
import { formatDate } from "@/lib/utils";

export default function ProfilePage() {
  const me = useQuery({ queryKey: ["me"], queryFn: () => authApi.me().then((r) => r.data) });
  const employee = useQuery({
    queryKey: ["my-employee-profile"],
    queryFn: () => employeeApi.me().then((r) => r.data),
    retry: false,
  });
  const employeeId = me.data?.employee_id;

  return (
    <div className="space-y-5">
      <div className="rounded-lg border bg-card p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Profile</p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">My profile</h1>
        <p className="mt-1 text-sm text-muted-foreground">Account, role, and employee master information.</p>
      </div>

      <div className="grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
        <Card>
          <CardHeader><CardTitle className="text-base">Account</CardTitle><CardDescription>Login identity and access role</CardDescription></CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between gap-4"><span className="text-muted-foreground">Email</span><span className="font-medium">{me.data?.email || "-"}</span></div>
            <div className="flex justify-between gap-4"><span className="text-muted-foreground">Role</span><Badge variant="outline">{me.data?.role?.name || "User"}</Badge></div>
            <div className="flex justify-between gap-4"><span className="text-muted-foreground">Superuser</span><span>{me.data?.is_superuser ? "Yes" : "No"}</span></div>
            <div className="flex justify-between gap-4"><span className="text-muted-foreground">Employee profile</span><span>{employeeId || "Not linked"}</span></div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">Employee details</CardTitle><CardDescription>From employee master</CardDescription></CardHeader>
          <CardContent>
            {employee.data ? (
              <div className="grid gap-3 text-sm sm:grid-cols-2">
                <div><p className="text-muted-foreground">Name</p><p className="font-medium">{employee.data.first_name} {employee.data.last_name}</p></div>
                <div><p className="text-muted-foreground">Employee ID</p><p className="font-medium">{employee.data.employee_id}</p></div>
                <div><p className="text-muted-foreground">Email</p><p className="font-medium">{employee.data.personal_email || "-"}</p></div>
                <div><p className="text-muted-foreground">Phone</p><p className="font-medium">{employee.data.phone_number || "-"}</p></div>
                <div><p className="text-muted-foreground">Joining date</p><p className="font-medium">{formatDate(employee.data.date_of_joining)}</p></div>
                <div><p className="text-muted-foreground">Status</p><Badge variant="secondary">{employee.data.status}</Badge></div>
                <div><p className="text-muted-foreground">Employment type</p><p className="font-medium">{employee.data.employment_type}</p></div>
                <div><p className="text-muted-foreground">Work location</p><p className="font-medium">{employee.data.work_location}</p></div>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">{employeeId ? "Loading employee details..." : "No employee profile is linked to this login."}</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
