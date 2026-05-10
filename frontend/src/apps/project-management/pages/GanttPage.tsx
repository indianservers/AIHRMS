import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { formatDate } from "@/lib/utils";
import { projectsAPI, tasksAPI } from "../services/api";
import type { PMSProject, PMSTask } from "../types";

export default function GanttPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [projects, setProjects] = useState<PMSProject[]>([]);
  const [tasks, setTasks] = useState<PMSTask[]>([]);

  useEffect(() => {
    const load = async () => {
      const projectItems = projectId ? [await projectsAPI.get(Number(projectId))] : await projectsAPI.list();
      setProjects(projectItems);
      const taskGroups = await Promise.all(projectItems.map((project) => tasksAPI.list(project.id).catch(() => [])));
      setTasks(taskGroups.flat());
    };
    load();
  }, [projectId]);

  const rows = useMemo(() => {
    const dated = tasks.filter((task) => task.start_date || task.due_date);
    return dated.map((task, index) => ({
      task,
      offset: (index * 17) % 58,
      width: 24 + ((index * 11) % 35),
    }));
  }, [tasks]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="page-title">Gantt</h1>
          <p className="page-description">Timeline planning with start/end dates and dependency placeholders.</p>
        </div>
        {projects[0] ? <Button asChild variant="outline"><Link to={`/pms/projects/${projects[0].id}/board`}>Open board</Link></Button> : null}
      </div>
      <Card>
        <CardContent className="overflow-x-auto p-5">
          <div className="min-w-[760px] space-y-3">
            <div className="grid grid-cols-[16rem_1fr] gap-4 border-b pb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
              <span>Task</span>
              <div className="grid grid-cols-4"><span>Week 1</span><span>Week 2</span><span>Week 3</span><span>Week 4</span></div>
            </div>
            {rows.map(({ task, offset, width }) => (
              <div key={task.id} className="grid grid-cols-[16rem_1fr] items-center gap-4">
                <div>
                  <p className="truncate text-sm font-medium">{task.title}</p>
                  <p className="text-xs text-muted-foreground">{formatDate(task.start_date || null)} - {formatDate(task.due_date || null)}</p>
                </div>
                <div className="relative h-9 rounded bg-muted">
                  <div className="absolute top-1.5 h-6 rounded bg-primary shadow-sm" style={{ left: `${offset}%`, width: `${Math.min(width, 100 - offset)}%` }} />
                </div>
              </div>
            ))}
            {!rows.length ? <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">Add task start or due dates to populate the Gantt timeline.</div> : null}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

