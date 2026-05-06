import { FormEvent, useState } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { tasksAPI } from "../services/api";
import type { PMSTask, TaskPriority, TaskStatus } from "../types";

const statuses: TaskStatus[] = ["Backlog", "To Do", "In Progress", "In Review", "Blocked", "Done"];
const priorities: TaskPriority[] = ["Low", "Medium", "High", "Urgent"];

export default function CreateTaskModal({
  isOpen,
  onClose,
  projectId,
  onTaskCreated,
}: {
  isOpen: boolean;
  onClose: () => void;
  projectId: number;
  onTaskCreated: (task: PMSTask) => void;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<TaskStatus>("To Do");
  const [priority, setPriority] = useState<TaskPriority>("Medium");
  const [dueDate, setDueDate] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!title.trim()) {
      setError("Task title is required.");
      return;
    }
    try {
      setSubmitting(true);
      setError(null);
      const key = title
        .trim()
        .split(/\s+/)
        .map((word) => word[0])
        .join("")
        .slice(0, 3)
        .toUpperCase();
      const task = await tasksAPI.create(projectId, {
        title,
        description: description || undefined,
        task_key: `${key || "TSK"}-${Date.now().toString().slice(-4)}`,
        status,
        priority,
        due_date: dueDate || undefined,
      });
      onTaskCreated(task);
      setTitle("");
      setDescription("");
      setDueDate("");
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || "Failed to create task.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <form onSubmit={submit} className="w-full max-w-lg rounded-lg border bg-background shadow-xl">
        <div className="flex items-center justify-between border-b px-5 py-4">
          <h2 className="text-lg font-semibold">Create task</h2>
          <Button type="button" variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        <div className="space-y-4 p-5">
          {error ? <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}
          <div className="space-y-2">
            <Label htmlFor="task-title">Title</Label>
            <Input id="task-title" value={title} onChange={(event) => setTitle(event.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="task-description">Description</Label>
            <textarea
              id="task-description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              className="min-h-24 w-full rounded-md border bg-background px-3 py-2 text-sm"
            />
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="task-status">Status</Label>
              <select id="task-status" value={status} onChange={(event) => setStatus(event.target.value as TaskStatus)} className="h-10 w-full rounded-md border bg-background px-3 text-sm">
                {statuses.map((item) => <option key={item}>{item}</option>)}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="task-priority">Priority</Label>
              <select id="task-priority" value={priority} onChange={(event) => setPriority(event.target.value as TaskPriority)} className="h-10 w-full rounded-md border bg-background px-3 text-sm">
                {priorities.map((item) => <option key={item}>{item}</option>)}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="task-due">Due date</Label>
              <Input id="task-due" type="date" value={dueDate} onChange={(event) => setDueDate(event.target.value)} />
            </div>
          </div>
        </div>
        <div className="flex justify-end gap-2 border-t px-5 py-4">
          <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          <Button type="submit" disabled={submitting}>{submitting ? "Creating..." : "Create task"}</Button>
        </div>
      </form>
    </div>
  );
}

