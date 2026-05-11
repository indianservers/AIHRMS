import { useState } from "react";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Clock, CheckCircle2, XCircle, CalendarDays, MapPin,
  RefreshCw, ChevronLeft, ChevronRight, AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { attendanceApi } from "@/services/api";
import { formatDateTime, statusColor } from "@/lib/utils";
import { toast } from "@/hooks/use-toast";
import { usePageTitle } from "@/hooks/use-page-title";

function getMonthDays(year: number, month: number) {
  const days: Date[] = [];
  const d = new Date(year, month - 1, 1);
  while (d.getMonth() === month - 1) {
    days.push(new Date(d));
    d.setDate(d.getDate() + 1);
  }
  return days;
}

const DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const statusDotColor: Record<string, string> = {
  Present: "bg-green-500",
  Absent: "bg-red-400",
  "Half-day": "bg-orange-400",
  WFH: "bg-blue-400",
  Holiday: "bg-purple-400",
  "On Leave": "bg-yellow-400",
};

export default function AttendancePage() {
  usePageTitle("Attendance");
  const qc = useQueryClient();
  const today = new Date();
  const [viewMonth, setViewMonth] = useState(today.getMonth() + 1);
  const [viewYear, setViewYear] = useState(today.getFullYear());

  const { data: todayRecord, isLoading: loadingToday } = useQuery({
    queryKey: ["attendance-today"],
    queryFn: () => attendanceApi.getToday().then((r) => r.data),
  });

  const { data: summary } = useQuery({
    queryKey: ["attendance-summary", viewMonth, viewYear],
    queryFn: () =>
      attendanceApi.monthlySummary(viewMonth, viewYear).then((r) => r.data),
  });

  const fromDate = `${viewYear}-${String(viewMonth).padStart(2, "0")}-01`;
  const lastDay = new Date(viewYear, viewMonth, 0).getDate();
  const toDate = `${viewYear}-${String(viewMonth).padStart(2, "0")}-${lastDay}`;

  const { data: records } = useQuery({
    queryKey: ["attendance-records", viewMonth, viewYear],
    queryFn: () =>
      attendanceApi.myAttendance(fromDate, toDate).then((r) => r.data),
  });

  const checkInMutation = useMutation({
    mutationFn: () => attendanceApi.checkIn({ source: "Web" }),
    onSuccess: () => {
      toast({ title: "Checked in successfully!" });
      qc.invalidateQueries({ queryKey: ["attendance-today"] });
      qc.invalidateQueries({ queryKey: ["attendance-summary"] });
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Check-in failed";
      toast({ title: "Error", description: msg, variant: "destructive" });
    },
  });

  const checkOutMutation = useMutation({
    mutationFn: () => attendanceApi.checkOut({}),
    onSuccess: () => {
      toast({ title: "Checked out successfully!" });
      qc.invalidateQueries({ queryKey: ["attendance-today"] });
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Check-out failed";
      toast({ title: "Error", description: msg, variant: "destructive" });
    },
  });

  const days = getMonthDays(viewYear, viewMonth);
  const firstDow = days[0].getDay();

  const recordsByDate: Record<string, { status: string; check_in?: string; check_out?: string }> = {};
  if (Array.isArray(records)) {
    for (const r of records) {
      const key = r.attendance_date?.slice(0, 10) || "";
      if (key) recordsByDate[key] = r;
    }
  }

  const prevMonth = () => {
    if (viewMonth === 1) { setViewMonth(12); setViewYear((y) => y - 1); }
    else setViewMonth((m) => m - 1);
  };
  const nextMonth = () => {
    if (viewMonth === 12) { setViewMonth(1); setViewYear((y) => y + 1); }
    else setViewMonth((m) => m + 1);
  };

  const isCheckedIn = todayRecord && todayRecord.check_in && !todayRecord.check_out;
  const isCheckedOut = todayRecord && todayRecord.check_out;

  return (
    <div className="space-y-4 sm:space-y-6">
      <div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="page-title">Attendance</h1>
            <p className="page-description">Track your daily attendance and monthly summary.</p>
          </div>
          <Button asChild variant="outline">
            <Link to="/hrms/attendance/shift-roster">
              <CalendarDays className="h-4 w-4" />
              Shift Roster
            </Link>
          </Button>
        </div>
      </div>

      {/* Today's action card */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Today â€” {today.toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}</p>
              {loadingToday ? (
                <div className="h-6 w-40 skeleton rounded" />
              ) : isCheckedOut ? (
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircle2 className="h-5 w-5" />
                  <span className="font-semibold">Completed â€” {formatDateTime(todayRecord.check_in)} â†’ {formatDateTime(todayRecord.check_out)}</span>
                </div>
              ) : isCheckedIn ? (
                <div className="flex items-center gap-2 text-blue-600">
                  <Clock className="h-5 w-5" />
                  <span className="font-semibold">Checked in at {formatDateTime(todayRecord.check_in)}</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <AlertCircle className="h-5 w-5" />
                  <span>Not checked in yet</span>
                </div>
              )}
            </div>
            <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:gap-3">
              {!isCheckedIn && !isCheckedOut && (
                <Button
                  onClick={() => checkInMutation.mutate()}
                  disabled={checkInMutation.isPending}
                  className="w-full bg-green-600 hover:bg-green-700 sm:w-auto"
                >
                  <Clock className="h-4 w-4 mr-2" />
                  Check In
                </Button>
              )}
              {isCheckedIn && (
                <Button
                  onClick={() => checkOutMutation.mutate()}
                  disabled={checkOutMutation.isPending}
                  variant="outline"
                  className="w-full sm:w-auto"
                >
                  <XCircle className="h-4 w-4 mr-2" />
                  Check Out
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Monthly summary stats */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: "Present", value: summary.present ?? 0, color: "text-green-600" },
            { label: "Absent", value: summary.absent ?? 0, color: "text-red-500" },
            { label: "Half-day", value: summary.half_day ?? 0, color: "text-orange-500" },
            { label: "WFH", value: summary.wfh ?? 0, color: "text-blue-600" },
          ].map((s) => (
            <Card key={s.label}>
              <CardContent className="p-4 text-center">
                <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
                <p className="text-xs text-muted-foreground mt-1">{s.label}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Calendar */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle className="text-base">
              {new Date(viewYear, viewMonth - 1).toLocaleString("en", { month: "long", year: "numeric" })}
            </CardTitle>
            <div className="flex items-center gap-2 self-end sm:self-auto">
              <Button variant="outline" size="icon" className="h-8 w-8" onClick={prevMonth}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon" className="h-8 w-8" onClick={nextMonth}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-7 gap-1 text-center mb-2">
            {DAY_LABELS.map((d) => (
              <div key={d} className="text-xs font-medium text-muted-foreground py-1">{d}</div>
            ))}
          </div>
          <div className="grid grid-cols-7 gap-1 text-xs sm:text-sm">
            {Array.from({ length: firstDow }).map((_, i) => (
              <div key={`pad-${i}`} />
            ))}
            {days.map((day) => {
              const key = day.toISOString().slice(0, 10);
              const rec = recordsByDate[key];
              const isToday = key === today.toISOString().slice(0, 10);
              const isFuture = day > today;
              const dot = rec ? statusDotColor[rec.status] : null;

              return (
                <div
                  key={key}
                  className={`relative flex h-9 w-full flex-col items-center justify-center rounded-lg text-xs sm:h-10 sm:text-sm
                    ${isToday ? "bg-primary text-primary-foreground font-bold" : ""}
                    ${!isToday && rec ? "bg-muted/50" : ""}
                    ${isFuture ? "opacity-40" : ""}
                  `}
                >
                  <span>{day.getDate()}</span>
                  {dot && !isToday && (
                    <span className={`absolute bottom-1 h-1.5 w-1.5 rounded-full ${dot}`} />
                  )}
                </div>
              );
            })}
          </div>

          {/* Legend */}
          <div className="flex flex-wrap gap-3 mt-4 pt-4 border-t">
            {Object.entries(statusDotColor).map(([label, cls]) => (
              <div key={label} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                <span className={`h-2.5 w-2.5 rounded-full ${cls}`} />
                {label}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent records table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Attendance Records</CardTitle>
          <CardDescription>
            {new Date(viewYear, viewMonth - 1).toLocaleString("en", { month: "long", year: "numeric" })}
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b bg-muted/50">
                <tr>
                  {["Date", "Status", "Check In", "Check Out", "Hours"].map((h) => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wide">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {!records || records.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">
                      No records for this period
                    </td>
                  </tr>
                ) : (
                  [...records].reverse().map((r: {
                    id: number;
                    attendance_date: string;
                    status: string;
                    check_in?: string;
                    check_out?: string;
                    total_hours?: number;
                  }) => (
                    <tr key={r.id} className="border-b hover:bg-muted/30">
                      <td className="px-4 py-3">
                        {new Date(r.attendance_date).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${statusColor(r.status)}`}>
                          {r.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {r.check_in ? new Date(r.check_in).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }) : "â€”"}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {r.check_out ? new Date(r.check_out).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }) : "â€”"}
                      </td>
                      <td className="px-4 py-3">
                        {r.total_hours != null ? `${r.total_hours.toFixed(1)}h` : "â€”"}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
