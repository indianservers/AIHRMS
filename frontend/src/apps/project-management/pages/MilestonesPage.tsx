import { FormEvent, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Flag, Plus } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { formatDate, statusColor } from "@/lib/utils";
import { milestonesAPI } from "../services/api";
import type { MilestoneStatus, PMSMilestone } from "../types";

export default function MilestonesPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = Number(projectId || 0);
  const [milestones, setMilestones] = useState<PMSMilestone[]>([]);
  const [name, setName] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [status, setStatus] = useState<MilestoneStatus>("Not Started");

  useEffect(() => {
    if (id) milestonesAPI.list(id).then(setMilestones);
  }, [id]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!name.trim()) return;
    const created = await milestonesAPI.create(id, { name, due_date: dueDate || undefined, status });
    setMilestones((items) => [created, ...items]);
    setName("");
    setDueDate("");
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Milestones</h1>
        <p className="page-description">Plan deliverables, approval gates, and client-visible outcomes.</p>
      </div>
      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Plus className="h-5 w-5" />Create milestone</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={submit} className="grid gap-4 md:grid-cols-[1fr_12rem_12rem_auto] md:items-end">
            <div className="space-y-2">
              <Label htmlFor="milestone-name">Name</Label>
              <Input id="milestone-name" value={name} onChange={(event) => setName(event.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="milestone-due">Due date</Label>
              <Input id="milestone-due" type="date" value={dueDate} onChange={(event) => setDueDate(event.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>Status</Label>
              <select value={status} onChange={(event) => setStatus(event.target.value as MilestoneStatus)} className="h-10 w-full rounded-md border bg-background px-3 text-sm">
                {["Not Started", "In Progress", "At Risk", "Completed", "Delayed"].map((item) => <option key={item}>{item}</option>)}
              </select>
            </div>
            <Button type="submit">Add</Button>
          </form>
        </CardContent>
      </Card>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {milestones.map((milestone) => (
          <Card key={milestone.id}>
            <CardContent className="p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-violet-100 p-2 text-violet-700"><Flag className="h-5 w-5" /></div>
                  <div>
                    <h2 className="font-semibold">{milestone.name}</h2>
                    <p className="text-sm text-muted-foreground">Due {formatDate(milestone.due_date || null)}</p>
                  </div>
                </div>
                <Badge className={statusColor(milestone.status)}>{milestone.status}</Badge>
              </div>
              <div className="mt-5">
                <div className="mb-2 flex justify-between text-xs text-muted-foreground"><span>Progress</span><span>{milestone.progress_percent}%</span></div>
                <div className="h-2 rounded-full bg-muted"><div className="h-2 rounded-full bg-violet-600" style={{ width: `${milestone.progress_percent}%` }} /></div>
              </div>
              <p className="mt-4 text-sm text-muted-foreground">Client approval: {milestone.client_approval_status}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

