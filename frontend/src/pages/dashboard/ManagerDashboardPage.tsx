import { useQuery } from "@tanstack/react-query";
import { CalendarDays, ClipboardCheck, HelpCircle, Users, UserCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { reportsApi } from "@/services/api";
import { usePageTitle } from "@/hooks/use-page-title";
import { formatDate } from "@/lib/utils";

type TeamDay = {
  date: string;
  leave_count: number;
  leaves: { employee_name?: string; status: string }[];
  holidays: { name: string; type: string }[];
};

export default function ManagerDashboardPage() {
  usePageTitle("Manager Hub");
  const { data } = useQuery({ queryKey: ["manager-dashboard"], queryFn: () => reportsApi.managerDashboard().then((r) => r.data) });
  const days: TeamDay[] = data?.team_calendar || [];
  return (
    <div className="space-y-5">
      <div className="rounded-lg border bg-card p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Manager</p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">Manager Dashboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">Team attendance, approvals, people moments, and leave calendar.</p>
      </div>

      <Card>
        <CardContent className="p-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-sm text-muted-foreground">My Team</p>
              <p className="text-3xl font-semibold">{data?.team_size ?? 0} members</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline"><UserCheck className="mr-1 h-3 w-3" />{data?.present_today ?? 0} Present</Badge>
              <Badge variant="outline">{data?.on_leave_today ?? 0} On Leave</Badge>
              <Badge variant="outline">{data?.wfh_today ?? 0} WFH</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle className="text-base">Pending</CardTitle></CardHeader>
          <CardContent className="grid gap-3 sm:grid-cols-3">
            {[
              ["Leave", data?.pending_leave_approvals ?? 0, CalendarDays],
              ["Regularization", data?.pending_regularizations ?? 0, ClipboardCheck],
              ["Change Requests", data?.pending_change_requests ?? 0, Users],
            ].map(([label, value, Icon]) => (
              <a key={label as string} href={label === "Leave" ? "/leave" : label === "Regularization" ? "/attendance" : "/employees"} className="rounded-lg border p-4 hover:bg-muted/50">
                <Icon className="mb-3 h-5 w-5 text-primary" />
                <p className="text-2xl font-semibold">{value as number}</p>
                <p className="text-xs text-muted-foreground">{label as string}</p>
              </a>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">Birthdays & Anniversaries This Week</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {[...(data?.moments_this_week?.birthdays || []).map((item: any) => ({ ...item, type: "Birthday" })), ...(data?.moments_this_week?.anniversaries || []).map((item: any) => ({ ...item, type: "Anniversary" }))].slice(0, 6).map((item: any) => (
              <a key={`${item.type}-${item.employee_id}`} href={`/employees/${item.employee_id}`} className="flex items-center justify-between rounded-lg border p-3 hover:bg-muted/50">
                <div>
                  <p className="text-sm font-medium">{item.name}</p>
                  <p className="text-xs text-muted-foreground">{item.type}{item.years ? ` â€¢ ${item.years} years` : ""}</p>
                </div>
                <span className="text-xs text-muted-foreground">{formatDate(item.date)}</span>
              </a>
            ))}
            {!data?.moments_this_week?.birthdays?.length && !data?.moments_this_week?.anniversaries?.length && (
              <p className="rounded-lg border p-4 text-sm text-muted-foreground">No birthday or anniversary moments this week.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-base">Team Calendar â€” {data?.calendar_month || ""}</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-7 gap-2 text-xs">
            {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => <div key={day} className="px-2 font-medium text-muted-foreground">{day}</div>)}
            {days.map((day) => {
              const date = new Date(day.date);
              return (
                <div key={day.date} className={`min-h-[76px] rounded-md border p-2 ${day.holidays.length ? "bg-amber-50" : day.leave_count ? "bg-blue-50" : "bg-card"}`}>
                  <div className="mb-1 flex items-center justify-between">
                    <span className="font-medium">{date.getDate()}</span>
                    {day.leave_count > 0 && <Badge variant="secondary">{day.leave_count}</Badge>}
                  </div>
                  {day.holidays.slice(0, 1).map((item) => <p key={item.name} className="truncate text-[11px] text-amber-700">{item.name}</p>)}
                  {day.leaves.slice(0, 2).map((item, idx) => <p key={idx} className="truncate text-[11px] text-blue-700">{item.employee_name || "Team member"} â€¢ {item.status}</p>)}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="text-base">Direct Reports & Support</CardTitle></CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {(data?.team || []).map((item: { id: number; name: string; employee_id: string; status: string }) => (
            <a key={item.id} href={`/employees/${item.id}`} className="flex items-center gap-3 rounded-lg border p-3 hover:bg-muted/50">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted text-sm font-semibold">{item.name.slice(0, 1)}</div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">{item.name}</p>
                <p className="text-xs text-muted-foreground">{item.employee_id}</p>
              </div>
              <Badge variant="outline">{item.status}</Badge>
            </a>
          ))}
          <a href="/helpdesk" className="flex items-center gap-3 rounded-lg border p-3 hover:bg-muted/50">
            <HelpCircle className="h-5 w-5 text-primary" />
            <div><p className="text-sm font-medium">{data?.open_helpdesk_tickets ?? 0} open tickets</p><p className="text-xs text-muted-foreground">Resolve team support requests</p></div>
          </a>
        </CardContent>
      </Card>
    </div>
  );
}
