import { AlertTriangle, BarChart3, Gauge, ShieldAlert, Target, TrendingDown, TrendingUp, Users } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { usePageTitle } from "@/hooks/use-page-title";

const analytics = [
  {
    title: "Absenteeism Trend",
    value: "6.8%",
    delta: "-1.2%",
    status: "Improving",
    icon: TrendingDown,
    detail: "Unplanned absence rate is trending down after weekly manager nudges.",
    rows: [["Sales", "8.4%", "High"], ["Operations", "6.1%", "Watch"], ["Engineering", "3.9%", "Healthy"]],
  },
  {
    title: "Salary Variance",
    value: "2.4%",
    delta: "+0.6%",
    status: "Watch",
    icon: BarChart3,
    detail: "Variance against approved compensation bands before payroll lock.",
    rows: [["Band L3", "3.1%", "Review"], ["Band L4", "1.8%", "Normal"], ["Band L5", "2.7%", "Review"]],
  },
  {
    title: "Manager Effectiveness",
    value: "82",
    delta: "+5",
    status: "Healthy",
    icon: Users,
    detail: "Blends attrition, goal closure, review timeliness, and team engagement.",
    rows: [["Team A", "88", "Strong"], ["Team B", "79", "Coach"], ["Team C", "73", "Intervene"]],
  },
  {
    title: "Performance Calibration",
    value: "11 gaps",
    delta: "-4",
    status: "Improving",
    icon: Target,
    detail: "Flags rating skew, missing evidence, and moderation outliers.",
    rows: [["High ratings", "4", "Evidence needed"], ["Low ratings", "2", "Normalize"], ["No rating", "5", "Pending"]],
  },
  {
    title: "Payroll Leakage",
    value: "Rs 1.42L",
    delta: "-18%",
    status: "Controlled",
    icon: ShieldAlert,
    detail: "Potential overpayments from LOP mismatch, duplicate allowances, and stale inputs.",
    rows: [["LOP mismatch", "Rs 62K", "Block"], ["Duplicate allowance", "Rs 38K", "Review"], ["Stale inputs", "Rs 42K", "Fix"]],
  },
];

const riskSignals = [
  ["Critical payroll blockers", "3", "Resolve before payroll approval"],
  ["High absenteeism teams", "2", "Manager action required"],
  ["Calibration exceptions", "11", "Moderation pending"],
  ["Compensation band breaches", "7", "HR review required"],
];

export default function AdvancedAnalyticsPage() {
  usePageTitle("Advanced Analytics");

  return (
    <div className="space-y-5">
      <div className="rounded-lg border bg-card p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">HRMS Intelligence</p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">Advanced Analytics</h1>
        <p className="mt-1 max-w-3xl text-sm text-muted-foreground">
          Absenteeism, salary variance, manager effectiveness, performance calibration, and payroll leakage in one decision cockpit.
        </p>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_22rem]">
        <div className="grid gap-4 lg:grid-cols-2">
          {analytics.map((item) => (
            <Card key={item.title}>
              <CardHeader className="flex flex-row items-start justify-between gap-3">
                <div>
                  <CardTitle className="text-base">{item.title}</CardTitle>
                  <p className="mt-1 text-sm text-muted-foreground">{item.detail}</p>
                </div>
                <div className="rounded-lg bg-primary/10 p-2 text-primary">
                  <item.icon className="h-5 w-5" />
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-end justify-between gap-3">
                  <div>
                    <p className="text-3xl font-semibold">{item.value}</p>
                    <p className="text-sm text-muted-foreground">Current signal</p>
                  </div>
                  <Badge variant="outline" className={item.delta.startsWith("-") ? "text-emerald-700" : "text-amber-700"}>
                    {item.delta}
                  </Badge>
                </div>
                <div className="overflow-hidden rounded-lg border">
                  <table className="w-full text-sm">
                    <tbody>
                      {item.rows.map(([name, value, status]) => (
                        <tr key={name} className="border-b last:border-0">
                          <td className="px-3 py-2 font-medium">{name}</td>
                          <td className="px-3 py-2 text-muted-foreground">{value}</td>
                          <td className="px-3 py-2 text-right"><Badge variant="secondary">{status}</Badge></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base"><Gauge className="h-4 w-4" />Executive Score</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-4xl font-semibold">84</p>
              <p className="mt-1 text-sm text-muted-foreground">People operations health score</p>
              <div className="mt-4 h-2 rounded-full bg-muted">
                <div className="h-2 w-[84%] rounded-full bg-primary" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base"><AlertTriangle className="h-4 w-4" />Priority Signals</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {riskSignals.map(([label, value, detail]) => (
                <div key={label} className="rounded-lg border p-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium">{label}</p>
                    <Badge>{value}</Badge>
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">{detail}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base"><TrendingUp className="h-4 w-4" />Recommended Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              {["Block payroll approval until leakage exceptions are cleared.", "Open calibration review for departments with rating skew.", "Schedule manager coaching for high absenteeism clusters."].map((item) => (
                <div key={item} className="rounded-md bg-muted/40 p-3">{item}</div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
