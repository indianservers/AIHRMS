import { FormEvent, useEffect, useState } from "react";
import { Timer } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { formatDate } from "@/lib/utils";
import { projectsAPI, timeLogsAPI } from "../services/api";
import type { PMSProject, PMSTimeLog } from "../types";

export default function TimeTrackingPage() {
  const [projects, setProjects] = useState<PMSProject[]>([]);
  const [logs, setLogs] = useState<PMSTimeLog[]>([]);
  const [projectId, setProjectId] = useState("");
  const [minutes, setMinutes] = useState("60");
  const [description, setDescription] = useState("");

  useEffect(() => {
    projectsAPI.list().then((items) => {
      setProjects(items);
      setProjectId(String(items[0]?.id || ""));
    });
    timeLogsAPI.list().then(setLogs);
  }, []);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!projectId) return;
    const created = await timeLogsAPI.create({
      project_id: Number(projectId),
      log_date: new Date().toISOString().slice(0, 10),
      duration_minutes: Number(minutes),
      description,
      is_billable: true,
    });
    setLogs((items) => [created, ...items]);
    setDescription("");
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Time tracking</h1>
        <p className="page-description">Log billable and non-billable effort against projects.</p>
      </div>
      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Timer className="h-5 w-5" />Manual time entry</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={submit} className="grid gap-4 md:grid-cols-[1fr_10rem_1fr_auto] md:items-end">
            <div className="space-y-2">
              <Label>Project</Label>
              <select value={projectId} onChange={(event) => setProjectId(event.target.value)} className="h-10 w-full rounded-md border bg-background px-3 text-sm">
                {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="duration">Minutes</Label>
              <Input id="duration" type="number" min="1" value={minutes} onChange={(event) => setMinutes(event.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Input id="description" value={description} onChange={(event) => setDescription(event.target.value)} />
            </div>
            <Button type="submit">Log time</Button>
          </form>
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle>Recent time logs</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {logs.map((log) => (
            <div key={log.id} className="flex items-center justify-between rounded-lg border p-3 text-sm">
              <div>
                <p className="font-medium">{log.description || "Time entry"}</p>
                <p className="text-muted-foreground">{formatDate(log.log_date)} - {log.approval_status}</p>
              </div>
              <p className="font-semibold">{Math.round(log.duration_minutes / 60 * 10) / 10}h</p>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

