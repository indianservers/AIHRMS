import { useMemo, useState } from "react";
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  DragStartEvent,
  PointerSensor,
  closestCorners,
  useDroppable,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import { SortableContext, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Activity, GripVertical, Plus, Radio, Search, UserPlus, Users } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { statusColor } from "@/lib/utils";
import { WorkIssues, projectStatusCards, teamMembers, ticketCards } from "../workData";
import { useRealtimeStore } from "../realtime";

const projectStatuses = ["Planned", "Active", "On Hold", "Completed"] as const;
const ticketStatuses = ["Open", "In Progress", "Waiting", "Resolved"] as const;

type DragItem =
  | { kind: "project"; id: number; name: string; status: string; manager: string; health: string; progress: number }
  | { kind: "ticket"; id: number; key: string; title: string; status: string; priority: string; owner: string }
  | { kind: "task"; id: number; key: string; summary: string; assignee: string; status: string; priority: string }
  | { kind: "member"; id: number; name: string; role: string; team: string; capacity: number };

export default function LiveWorkManagementPage() {
  const [projects, setProjects] = useState(projectStatusCards);
  const [tickets, setTickets] = useState(ticketCards);
  const [tasks, setTasks] = useState(WorkIssues);
  const [members, setMembers] = useState(teamMembers);
  const [active, setActive] = useState<DragItem | null>(null);
  const [search, setSearch] = useState("");
  const { events, onlineUsers, publish } = useRealtimeStore();
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 8 } }));

  const filteredTasks = useMemo(
    () => tasks.filter((task) => [task.key, task.summary, task.assignee, task.status].join(" ").toLowerCase().includes(search.toLowerCase())),
    [tasks, search],
  );

  const start = (event: DragStartEvent) => {
    const [kind, rawId] = String(event.active.id).split(":");
    const id = Number(rawId);
    if (kind === "project") setActive({ kind, ...projects.find((item) => item.id === id)! });
    if (kind === "ticket") setActive({ kind, ...tickets.find((item) => item.id === id)! });
    if (kind === "task") {
      const task = tasks.find((item) => item.id === id)!;
      setActive({ kind, id: task.id, key: task.key, summary: task.summary, assignee: task.assignee, status: task.status, priority: task.priority });
    }
    if (kind === "member") setActive({ kind, ...members.find((item) => item.id === id)! });
  };

  const end = (event: DragEndEvent) => {
    const activeId = String(event.active.id);
    const overId = event.over ? String(event.over.id) : "";
    setActive(null);
    if (!overId) return;
    const [kind, rawId] = activeId.split(":");
    const id = Number(rawId);

    if (kind === "project" && overId.startsWith("project-status:")) {
      const status = overId.replace("project-status:", "");
      setProjects((items) => items.map((item) => (item.id === id ? { ...item, status } : item)));
      publish({ actor: "You", action: "moved project", target: `${projects.find((item) => item.id === id)?.name} to ${status}` });
    }

    if (kind === "ticket" && overId.startsWith("ticket-status:")) {
      const status = overId.replace("ticket-status:", "");
      setTickets((items) => items.map((item) => (item.id === id ? { ...item, status } : item)));
      publish({ actor: "You", action: "moved ticket", target: `${tickets.find((item) => item.id === id)?.key} to ${status}` });
    }

    if (kind === "task" && overId.startsWith("member:")) {
      const memberId = Number(overId.replace("member:", ""));
      const member = members.find((item) => item.id === memberId);
      if (!member) return;
      setTasks((items) => items.map((item) => (item.id === id ? { ...item, assignee: member.name } : item)));
      publish({ actor: "You", action: "assigned task", target: `${tasks.find((item) => item.id === id)?.key} to ${member.name}` });
    }

    if (kind === "member" && overId.startsWith("team:")) {
      const team = overId.replace("team:", "");
      setMembers((items) => items.map((item) => (item.id === id ? { ...item, team } : item)));
      publish({ actor: "You", action: "moved teammate", target: `${members.find((item) => item.id === id)?.name} to ${team}` });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <h1 className="page-title">Live Work Management</h1>
          <p className="page-description">KaryaFlow drag/drop for project status, tickets, tasks, teammates, and teams with realtime cross-tab activity sync.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline"><UserPlus className="h-4 w-4" />Add teammate</Button>
          <Button><Plus className="h-4 w-4" />Create task</Button>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1fr_22rem]">
        <div className="space-y-4">
          <Card>
            <CardContent className="flex flex-col gap-3 p-3 lg:flex-row lg:items-center">
              <div className="flex min-w-0 flex-1 items-center gap-2 rounded-md border px-3 py-2">
                <Search className="h-4 w-4 text-muted-foreground" />
                <Input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search tasks, tickets, teammates..." className="border-0 p-0 shadow-none focus-visible:ring-0" />
              </div>
              <Badge variant="outline" className="w-fit gap-1"><Radio className="h-3 w-3 text-emerald-600" />Live sync on</Badge>
            </CardContent>
          </Card>

          <DndContext sensors={sensors} collisionDetection={closestCorners} onDragStart={start} onDragEnd={end}>
            <Section title="Projects by Status">
              <div className="grid gap-3 xl:grid-cols-4">
                {projectStatuses.map((status) => (
                  <DropColumn key={status} id={`project-status:${status}`} title={status} count={projects.filter((item) => item.status === status).length}>
                    <SortableContext items={projects.filter((item) => item.status === status).map((item) => `project:${item.id}`)} strategy={verticalListSortingStrategy}>
                      {projects.filter((item) => item.status === status).map((project) => <DraggableCard key={project.id} id={`project:${project.id}`} title={project.name} subtitle={`${project.manager} / ${project.progress}%`} badges={[project.health]} />)}
                    </SortableContext>
                  </DropColumn>
                ))}
              </div>
            </Section>

            <Section title="Tickets by Workflow">
              <div className="grid gap-3 xl:grid-cols-4">
                {ticketStatuses.map((status) => (
                  <DropColumn key={status} id={`ticket-status:${status}`} title={status} count={tickets.filter((item) => item.status === status).length}>
                    <SortableContext items={tickets.filter((item) => item.status === status).map((item) => `ticket:${item.id}`)} strategy={verticalListSortingStrategy}>
                      {tickets.filter((item) => item.status === status).map((ticket) => <DraggableCard key={ticket.id} id={`ticket:${ticket.id}`} title={`${ticket.key} ${ticket.title}`} subtitle={ticket.owner} badges={[ticket.priority]} />)}
                    </SortableContext>
                  </DropColumn>
                ))}
              </div>
            </Section>

            <Section title="Assign Tasks to Teammates">
              <div className="grid gap-3 xl:grid-cols-[1fr_24rem]">
                <Card>
                  <CardContent className="space-y-2 p-3">
                    <SortableContext items={filteredTasks.map((item) => `task:${item.id}`)} strategy={verticalListSortingStrategy}>
                      {filteredTasks.slice(0, 8).map((task) => <DraggableCard key={task.id} id={`task:${task.id}`} title={`${task.key} ${task.summary}`} subtitle={`Assigned to ${task.assignee}`} badges={[task.priority, task.status]} />)}
                    </SortableContext>
                  </CardContent>
                </Card>
                <div className="grid gap-3">
                  {members.map((member) => <MemberDrop key={member.id} member={member} />)}
                </div>
              </div>
            </Section>

            <Section title="Move Teammates Between Teams">
              <div className="grid gap-3 xl:grid-cols-3">
                {["Delivery", "Platform", "Experience", "Quality"].map((team) => (
                  <DropColumn key={team} id={`team:${team}`} title={team} count={members.filter((item) => item.team === team).length}>
                    <SortableContext items={members.filter((item) => item.team === team).map((item) => `member:${item.id}`)} strategy={verticalListSortingStrategy}>
                      {members.filter((item) => item.team === team).map((member) => <DraggableCard key={member.id} id={`member:${member.id}`} title={member.name} subtitle={`${member.role} / ${member.capacity}h`} badges={[member.team]} />)}
                    </SortableContext>
                  </DropColumn>
                ))}
              </div>
            </Section>

            <DragOverlay>{active ? <OverlayCard item={active} /> : null}</DragOverlay>
          </DndContext>
        </div>

        <Card className="h-fit">
          <CardHeader><CardTitle className="flex items-center gap-2"><Activity className="h-5 w-5 text-primary" />Realtime Activity</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Online now</p>
              <div className="mt-2 flex flex-wrap gap-2">{onlineUsers.map((user) => <Badge key={user} variant="outline"><Users className="h-3 w-3" />{user}</Badge>)}</div>
            </div>
            <div className="space-y-3">
              {events.map((event) => (
                <div key={event.id} className="rounded-lg border bg-muted/30 p-3 text-sm">
                  <p><span className="font-semibold">{typeof event.actor === "string" ? event.actor : event.actor?.name || "Someone"}</span> {event.action}</p>
                  <p className="text-muted-foreground">{event.target}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return <div className="space-y-3"><h2 className="text-lg font-semibold">{title}</h2>{children}</div>;
}

function DropColumn({ id, title, count, children }: { id: string; title: string; count: number; children: React.ReactNode }) {
  const { setNodeRef, isOver } = useDroppable({ id });
  return (
    <Card ref={setNodeRef} className={isOver ? "ring-2 ring-primary/40" : ""}>
      <CardHeader className="p-3"><CardTitle className="flex items-center justify-between text-sm">{title}<Badge variant="outline">{count}</Badge></CardTitle></CardHeader>
      <CardContent className="min-h-40 space-y-2 p-3 pt-0">{children}</CardContent>
    </Card>
  );
}

function MemberDrop({ member }: { member: { id: number; name: string; role: string; capacity: number } }) {
  const { setNodeRef, isOver } = useDroppable({ id: `member:${member.id}` });
  return (
    <Card ref={setNodeRef} className={isOver ? "ring-2 ring-primary/40" : ""}>
      <CardContent className="p-3">
        <p className="font-semibold">{member.name}</p>
        <p className="text-sm text-muted-foreground">{member.role} / {member.capacity}h capacity</p>
      </CardContent>
    </Card>
  );
}

function DraggableCard({ id, title, subtitle, badges }: { id: string; title: string; subtitle: string; badges: string[] }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id });
  return (
    <article ref={setNodeRef} style={{ transform: CSS.Transform.toString(transform), transition }} className={`rounded-lg border bg-card p-3 shadow-sm ${isDragging ? "opacity-50" : ""}`}>
      <div className="flex gap-2">
        <button type="button" className="rounded p-1 text-muted-foreground hover:bg-muted" {...attributes} {...listeners} aria-label="Drag item"><GripVertical className="h-4 w-4" /></button>
        <div className="min-w-0 flex-1"><p className="line-clamp-2 text-sm font-semibold">{title}</p><p className="mt-1 text-xs text-muted-foreground">{subtitle}</p></div>
      </div>
      <div className="mt-2 flex flex-wrap gap-1">{badges.map((badge) => <Badge key={badge} className={statusColor(badge)}>{badge}</Badge>)}</div>
    </article>
  );
}

function OverlayCard({ item }: { item: DragItem }) {
  const title = item.kind === "project" ? item.name : item.kind === "ticket" ? `${item.key} ${item.title}` : item.kind === "task" ? `${item.key} ${item.summary}` : item.name;
  return <div className="w-72 rounded-lg border bg-card p-3 shadow-xl"><p className="font-semibold">{title}</p><p className="text-sm text-muted-foreground">Drop to update instantly</p></div>;
}

