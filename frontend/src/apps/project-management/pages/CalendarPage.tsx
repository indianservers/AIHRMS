import { useEffect, useMemo, useState } from "react";
import { CalendarDays, Flag, ListChecks } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { formatDate, statusColor } from "@/lib/utils";
import { milestonesAPI, projectsAPI, tasksAPI } from "../services/api";
import type { PMSMilestone, PMSProject, PMSTask } from "../types";

type CalendarItem = {
  id: string;
  title: string;
  date?: string;
  type: "Task" | "Milestone" | "Project";
  status: string;
};

export default function CalendarPage() {
  const [projects, setProjects] = useState<PMSProject[]>([]);
  const [tasks, setTasks] = useState<PMSTask[]>([]);
  const [milestones, setMilestones] = useState<PMSMilestone[]>([]);

  useEffect(() => {
    projectsAPI.list().then(async (projectItems) => {
      setProjects(projectItems);
      const [taskGroups, milestoneGroups] = await Promise.all([
        Promise.all(projectItems.map((project) => tasksAPI.list(project.id).catch(() => []))),
        Promise.all(projectItems.map((project) => milestonesAPI.list(project.id).catch(() => []))),
      ]);
      setTasks(taskGroups.flat());
      setMilestones(milestoneGroups.flat());
    });
  }, []);

  const items = useMemo<CalendarItem[]>(() => {
    const taskItems = tasks.map((task) => ({
      id: `task-${task.id}`,
      title: task.title,
      date: task.due_date,
      type: "Task" as const,
      status: task.status,
    }));
    const milestoneItems = milestones.map((milestone) => ({
      id: `milestone-${milestone.id}`,
      title: milestone.name,
      date: milestone.due_date,
      type: "Milestone" as const,
      status: milestone.status,
    }));
    const projectItems = projects.map((project) => ({
      id: `project-${project.id}`,
      title: project.name,
      date: project.due_date,
      type: "Project" as const,
      status: project.status,
    }));
    return [...taskItems, ...milestoneItems, ...projectItems]
      .filter((item) => item.date)
      .sort((a, b) => String(a.date).localeCompare(String(b.date)));
  }, [milestones, projects, tasks]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Calendar</h1>
        <p className="page-description">Unified schedule for task due dates, milestones, and project deadlines.</p>
      </div>
      <div className="grid gap-4 lg:grid-cols-7">
        {items.slice(0, 21).map((item) => (
          <Card key={item.id} className="lg:min-h-40">
            <CardContent className="p-4">
              <div className="mb-3 flex items-center justify-between">
                <span className="inline-flex items-center gap-1 text-xs font-medium text-muted-foreground">
                  {item.type === "Milestone" ? <Flag className="h-3.5 w-3.5" /> : item.type === "Task" ? <ListChecks className="h-3.5 w-3.5" /> : <CalendarDays className="h-3.5 w-3.5" />}
                  {formatDate(item.date || null)}
                </span>
              </div>
              <p className="line-clamp-3 text-sm font-semibold">{item.title}</p>
              <Badge className={`mt-3 ${statusColor(item.status)}`}>{item.status}</Badge>
            </CardContent>
          </Card>
        ))}
      </div>
      {!items.length ? <Empty text="No dated tasks, milestones, or deadlines yet." /> : null}
    </div>
  );
}

function Empty({ text }: { text: string }) {
  return <div className="rounded-lg border bg-card p-8 text-center text-sm text-muted-foreground">{text}</div>;
}

