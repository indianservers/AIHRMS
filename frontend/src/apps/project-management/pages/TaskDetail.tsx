import type React from "react";
import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, MessageSquare, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { commentsAPI, tasksAPI } from "../services/api";
import type { PMSComment, PMSTask, TaskPriority, TaskStatus } from "../types";

export default function TaskDetail() {
  const { projectId, taskId } = useParams<{ projectId: string; taskId: string }>();
  const navigate = useNavigate();
  const [task, setTask] = useState<PMSTask | null>(null);
  const [comments, setComments] = useState<PMSComment[]>([]);
  const [comment, setComment] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!taskId) return;
    tasksAPI.get(Number(taskId)).then(setTask);
    commentsAPI.listForTask(Number(taskId)).then(setComments).catch(() => setComments([]));
  }, [taskId]);

  if (!task) return <div className="skeleton h-72 rounded-lg" />;

  const updateTask = async (data: Partial<PMSTask>) => {
    setSaving(true);
    const updated = await tasksAPI.update(task.id, data as any);
    setTask(updated);
    setSaving(false);
  };

  const addComment = async (event: FormEvent) => {
    event.preventDefault();
    if (!comment.trim()) return;
    const created = await commentsAPI.addToTask(task.id, { body: comment, is_internal: true });
    setComments((items) => [created, ...items]);
    setComment("");
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <Button variant="ghost" onClick={() => navigate(`/pms/projects/${projectId}/board`)}>
        <ArrowLeft className="h-4 w-4" />Back to board
      </Button>
      <div className="grid gap-6 lg:grid-cols-[1fr_22rem]">
        <Card>
          <CardHeader>
            <CardTitle>{task.task_key}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="task-title-edit">Title</Label>
              <Input id="task-title-edit" value={task.title} onChange={(event) => setTask({ ...task, title: event.target.value })} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="task-description-edit">Description</Label>
              <textarea id="task-description-edit" value={task.description || ""} onChange={(event) => setTask({ ...task, description: event.target.value })} className="min-h-48 w-full rounded-md border bg-background px-3 py-2 text-sm" />
            </div>
            <Button onClick={() => updateTask({ title: task.title, description: task.description })} disabled={saving}>
              <Save className="h-4 w-4" />{saving ? "Saving..." : "Save changes"}
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Properties</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <Field label="Status">
              <select value={task.status} onChange={(event) => updateTask({ status: event.target.value as TaskStatus })} className="h-10 w-full rounded-md border bg-background px-3 text-sm">
                {["Backlog", "To Do", "In Progress", "In Review", "Blocked", "Done", "Cancelled"].map((item) => <option key={item}>{item}</option>)}
              </select>
            </Field>
            <Field label="Priority">
              <select value={task.priority} onChange={(event) => updateTask({ priority: event.target.value as TaskPriority })} className="h-10 w-full rounded-md border bg-background px-3 text-sm">
                {["Low", "Medium", "High", "Urgent"].map((item) => <option key={item}>{item}</option>)}
              </select>
            </Field>
            <Field label="Due date">
              <Input type="date" value={task.due_date || ""} onChange={(event) => updateTask({ due_date: event.target.value } as any)} />
            </Field>
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><MessageSquare className="h-5 w-5" />Discussion</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={addComment} className="flex gap-2">
            <Input value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Write an internal comment" />
            <Button type="submit">Comment</Button>
          </form>
          {comments.map((item) => (
            <div key={item.id} className="rounded-lg border p-3 text-sm">
              <p>{item.body}</p>
              <p className="mt-2 text-xs text-muted-foreground">{new Date(item.created_at).toLocaleString()}</p>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="space-y-2"><Label>{label}</Label>{children}</div>;
}

