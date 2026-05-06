import type React from "react";
import { FormEvent, useEffect, useState } from "react";
import { Activity } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { formatDate, statusColor } from "@/lib/utils";
import { projectsAPI, sprintsAPI } from "../services/api";
import type { PMSProject, PMSSprint } from "../types";

export default function SprintsPage() {
  const [projects, setProjects] = useState<PMSProject[]>([]);
  const [projectId, setProjectId] = useState("");
  const [sprints, setSprints] = useState<PMSSprint[]>([]);
  const [name, setName] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  useEffect(() => {
    projectsAPI.list().then((items) => {
      setProjects(items);
      const firstId = String(items[0]?.id || "");
      setProjectId(firstId);
      if (firstId) sprintsAPI.list(Number(firstId)).then(setSprints);
    });
  }, []);

  const switchProject = (value: string) => {
    setProjectId(value);
    if (value) sprintsAPI.list(Number(value)).then(setSprints);
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!projectId || !name || !startDate || !endDate) return;
    const sprint = await sprintsAPI.create(Number(projectId), {
      name,
      goal: "Planned delivery increment",
      status: "Planned",
      start_date: startDate,
      end_date: endDate,
    } as any);
    setSprints((items) => [sprint, ...items]);
    setName("");
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Sprints</h1>
        <p className="page-description">Plan agile delivery windows, capacity, and velocity tracking.</p>
      </div>
      <Card>
        <CardHeader><CardTitle>Create sprint</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={submit} className="grid gap-4 md:grid-cols-[1fr_1fr_11rem_11rem_auto] md:items-end">
            <Field label="Project"><select value={projectId} onChange={(event) => switchProject(event.target.value)} className="h-10 w-full rounded-md border bg-background px-3 text-sm">{projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}</select></Field>
            <Field label="Sprint name"><Input value={name} onChange={(event) => setName(event.target.value)} /></Field>
            <Field label="Start"><Input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} /></Field>
            <Field label="End"><Input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} /></Field>
            <Button type="submit">Create</Button>
          </form>
        </CardContent>
      </Card>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {sprints.map((sprint) => (
          <Card key={sprint.id}>
            <CardContent className="p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3"><div className="rounded-lg bg-primary/10 p-2 text-primary"><Activity className="h-5 w-5" /></div><div><h2 className="font-semibold">{sprint.name}</h2><p className="text-sm text-muted-foreground">{formatDate(sprint.start_date)} - {formatDate(sprint.end_date)}</p></div></div>
                <Badge className={statusColor(sprint.status)}>{sprint.status}</Badge>
              </div>
              <p className="mt-4 text-sm text-muted-foreground">{sprint.goal || "No sprint goal defined."}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="space-y-2"><Label>{label}</Label>{children}</div>;
}

