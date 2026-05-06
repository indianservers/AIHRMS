import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { tasksAPI } from "../services/api";
import type { PMSTask } from "../types";

const colors = ["#2563eb", "#f59e0b", "#7c3aed", "#16a34a", "#dc2626"];

export default function ReportsPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [tasks, setTasks] = useState<PMSTask[]>([]);

  useEffect(() => {
    if (projectId) tasksAPI.list(Number(projectId)).then(setTasks);
  }, [projectId]);

  const statusData = useMemo(
    () => ["Backlog", "To Do", "In Progress", "In Review", "Done"].map((name) => ({
      name,
      value: tasks.filter((task) => task.status === name).length,
    })),
    [tasks]
  );
  const completed = tasks.filter((task) => task.status === "Done").length;
  const overdue = tasks.filter((task) => task.due_date && new Date(task.due_date) < new Date() && task.status !== "Done").length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Project reports</h1>
        <p className="page-description">Delivery metrics, bottlenecks, and export-ready report placeholders.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <ReportMetric label="Tasks" value={tasks.length} />
        <ReportMetric label="Completed" value={completed} />
        <ReportMetric label="Overdue" value={overdue} />
      </div>
      <Card>
        <CardHeader><CardTitle>Task distribution</CardTitle></CardHeader>
        <CardContent className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={statusData} dataKey="value" nameKey="name" innerRadius={70} outerRadius={110} paddingAngle={3}>
                {statusData.map((_, index) => <Cell key={index} fill={colors[index % colors.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}

function ReportMetric({ label, value }: { label: string; value: number }) {
  return <Card><CardContent className="p-5"><p className="text-sm text-muted-foreground">{label}</p><p className="mt-2 text-3xl font-semibold">{value}</p></CardContent></Card>;
}

