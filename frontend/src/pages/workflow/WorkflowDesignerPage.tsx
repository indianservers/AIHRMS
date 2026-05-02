import * as Dialog from "@radix-ui/react-dialog";
import * as Switch from "@radix-ui/react-switch";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { GitBranch, Plus, Save, Search, Trash2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { workflowDefinitionsApi } from "@/services/api";
import { toast } from "@/hooks/use-toast";
import { cn, formatDate } from "@/lib/utils";

type WorkflowDefinition = {
  id: number;
  name: string;
  module: string;
  trigger_event: string;
  description?: string | null;
  is_active: boolean;
  created_at?: string | null;
  steps?: WorkflowStep[];
};

type WorkflowStep = {
  id: number;
  workflow_id: number;
  step_order: number;
  step_type: string;
  approver_type: string;
  approver_value?: string | null;
  condition_expression?: string | null;
  timeout_hours?: number | null;
  escalation_user_id?: number | null;
  is_required: boolean;
};

type DefinitionDraft = {
  name: string;
  description: string;
  module: string;
  trigger_event: string;
};

const MODULES = [
  "leave_request",
  "attendance_regularization",
  "employee_change_request",
  "recruitment_offer",
  "onboarding_task",
  "exit_request",
  "expense_claim",
];

const TRIGGERS_BY_MODULE: Record<string, string[]> = {
  leave_request: ["on_submit", "on_status_change", "on_due_date"],
  attendance_regularization: ["on_submit", "on_status_change", "on_due_date"],
  employee_change_request: ["on_submit", "on_status_change", "on_due_date"],
  recruitment_offer: ["on_submit", "on_status_change", "on_due_date"],
  onboarding_task: ["on_submit", "on_status_change", "on_due_date"],
  exit_request: ["on_submit", "on_status_change", "on_due_date"],
  expense_claim: ["on_submit", "on_status_change", "on_due_date"],
};

const APPROVER_TYPES = ["specific_user", "role", "manager", "hr", "skip_if_self"];
const ROLE_OPTIONS = ["admin", "hr", "manager", "payroll_approve", "leave_approve"];
const TIMEOUT_ACTIONS = ["escalate", "auto_approve", "auto_reject"];

const moduleLabel = (value: string) =>
  value.split("_").map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");

const triggerLabel = (value: string) => value.replace(/_/g, " ");

const moduleBadgeClass = (module: string) =>
  ({
    leave_request: "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-200",
    attendance_regularization: "bg-orange-100 text-orange-800 dark:bg-orange-950 dark:text-orange-200",
    employee_change_request: "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-200",
    recruitment_offer: "bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-200",
    onboarding_task: "bg-cyan-100 text-cyan-800 dark:bg-cyan-950 dark:text-cyan-200",
    exit_request: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200",
    expense_claim: "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-200",
  }[module] || "bg-muted text-muted-foreground");

const toDefinitionDraft = (definition: WorkflowDefinition): DefinitionDraft => ({
  name: definition.name,
  description: definition.description || "",
  module: definition.module,
  trigger_event: definition.trigger_event,
});

const stepPayload = (step: WorkflowStep) => ({
  step_order: step.step_order,
  step_type: step.step_type || "Approval",
  approver_type: step.approver_type || "role",
  approver_value: step.approver_value || null,
  condition_expression: step.condition_expression || null,
  timeout_hours: step.timeout_hours || null,
  escalation_user_id: step.escalation_user_id || null,
  is_required: step.is_required,
});

function SwitchControl({ checked, onChange }: { checked: boolean; onChange: (checked: boolean) => void }) {
  return (
    <Switch.Root
      checked={checked}
      onCheckedChange={onChange}
      className="relative h-5 w-9 rounded-full bg-muted data-[state=checked]:bg-primary"
    >
      <Switch.Thumb className="block h-4 w-4 translate-x-0.5 rounded-full bg-background shadow transition-transform data-[state=checked]:translate-x-4" />
    </Switch.Root>
  );
}

function SelectField({
  value,
  onChange,
  options,
  className,
}: {
  value: string;
  onChange: (value: string) => void;
  options: string[];
  className?: string;
}) {
  return (
    <select
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className={cn("h-10 rounded-md border bg-background px-3 text-sm", className)}
    >
      {options.map((option) => (
        <option key={option} value={option}>
          {moduleLabel(option)}
        </option>
      ))}
    </select>
  );
}

export default function WorkflowDesignerPage() {
  useEffect(() => { document.title = "Workflow Designer · AI HRMS"; }, []);
  const qc = useQueryClient();
  const [moduleFilter, setModuleFilter] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newWorkflow, setNewWorkflow] = useState<DefinitionDraft>({
    name: "",
    description: "",
    module: "leave_request",
    trigger_event: "on_submit",
  });
  const [definitionDraft, setDefinitionDraft] = useState<DefinitionDraft | null>(null);
  const [stepsDraft, setStepsDraft] = useState<WorkflowStep[]>([]);
  const [timeoutActions, setTimeoutActions] = useState<Record<number, string>>({});

  const definitionsQuery = useQuery({
    queryKey: ["workflow-definitions", moduleFilter],
    queryFn: () =>
      workflowDefinitionsApi
        .list(moduleFilter ? { module: moduleFilter } : undefined)
        .then((response) => response.data as WorkflowDefinition[]),
  });

  const selectedQuery = useQuery({
    queryKey: ["workflow-definition", selectedId],
    queryFn: () => workflowDefinitionsApi.get(selectedId!).then((response) => response.data as WorkflowDefinition),
    enabled: !!selectedId,
  });

  const definitions = definitionsQuery.data || [];
  const selected = selectedQuery.data;
  const filteredTriggers = TRIGGERS_BY_MODULE[newWorkflow.module] || TRIGGERS_BY_MODULE.leave_request;
  const selectedTriggers = definitionDraft ? TRIGGERS_BY_MODULE[definitionDraft.module] || filteredTriggers : filteredTriggers;

  useEffect(() => {
    if (!selectedId && definitions.length) setSelectedId(definitions[0].id);
  }, [definitions, selectedId]);

  useEffect(() => {
    if (selected) {
      setDefinitionDraft(toDefinitionDraft(selected));
      setStepsDraft([...(selected.steps || [])].sort((a, b) => a.step_order - b.step_order));
    }
  }, [selected]);

  const invalidateSelected = () => {
    qc.invalidateQueries({ queryKey: ["workflow-definitions"] });
    qc.invalidateQueries({ queryKey: ["workflow-definition", selectedId] });
  };

  const createDefinition = useMutation({
    mutationFn: () => workflowDefinitionsApi.create(newWorkflow),
    onSuccess: (response) => {
      const created = response.data as WorkflowDefinition;
      toast({ title: "Workflow created" });
      setDialogOpen(false);
      setSelectedId(created.id);
      setNewWorkflow({ name: "", description: "", module: "leave_request", trigger_event: "on_submit" });
      qc.invalidateQueries({ queryKey: ["workflow-definitions"] });
    },
    onError: () => toast({ title: "Unable to create workflow", variant: "destructive" }),
  });

  const updateDefinition = useMutation({
    mutationFn: (draft: DefinitionDraft) => workflowDefinitionsApi.update(selectedId!, draft),
    onSuccess: () => {
      toast({ title: "Workflow saved" });
      invalidateSelected();
    },
    onError: () => toast({ title: "Unable to save workflow", variant: "destructive" }),
  });

  const updateStep = useMutation({
    mutationFn: (step: WorkflowStep) => workflowDefinitionsApi.updateStep(selectedId!, step.id, stepPayload(step)),
    onSuccess: () => {
      toast({ title: "Step saved" });
      invalidateSelected();
    },
    onError: () => toast({ title: "Unable to save step", variant: "destructive" }),
  });

  const addStep = useMutation({
    mutationFn: () => {
      const nextOrder = stepsDraft.length ? Math.max(...stepsDraft.map((step) => step.step_order)) + 1 : 1;
      return workflowDefinitionsApi.addStep(selectedId!, {
        step_order: nextOrder,
        step_type: `Step ${nextOrder}`,
        approver_type: "role",
        approver_value: "hr",
        timeout_hours: 72,
        is_required: true,
      });
    },
    onSuccess: () => {
      toast({ title: "Step added" });
      invalidateSelected();
    },
    onError: () => toast({ title: "Unable to add step", variant: "destructive" }),
  });

  const deleteStep = useMutation({
    mutationFn: (stepId: number) => workflowDefinitionsApi.deleteStep(selectedId!, stepId),
    onSuccess: () => {
      toast({ title: "Step deleted" });
      invalidateSelected();
    },
    onError: () => toast({ title: "Unable to delete step", variant: "destructive" }),
  });

  const toggleActive = useMutation({
    mutationFn: (active: boolean) =>
      active ? workflowDefinitionsApi.activate(selectedId!) : workflowDefinitionsApi.deactivate(selectedId!),
    onSuccess: (_, active) => {
      toast({ title: active ? "Workflow activated" : "Workflow deactivated" });
      invalidateSelected();
    },
    onError: () => toast({ title: "Unable to update workflow status", variant: "destructive" }),
  });

  const updateStepDraft = (stepId: number, patch: Partial<WorkflowStep>) => {
    setStepsDraft((steps) => steps.map((step) => (step.id === stepId ? { ...step, ...patch } : step)));
  };

  const selectedStatus = useMemo(() => (selected?.is_active ? "Active" : "Inactive"), [selected?.is_active]);

  return (
    <div className="flex h-[calc(100vh-7rem)] gap-4">
      <aside className="flex w-80 shrink-0 flex-col rounded-md border bg-background">
        <div className="border-b p-4">
          <div className="flex items-center justify-between gap-3">
            <h1 className="text-base font-semibold">Workflow Definitions</h1>
            <Button size="sm" onClick={() => setDialogOpen(true)}>
              <Plus className="h-4 w-4" />
              New Workflow
            </Button>
          </div>
          <div className="mt-3 flex items-center gap-2 rounded-md border px-3">
            <Search className="h-4 w-4 text-muted-foreground" />
            <select
              value={moduleFilter}
              onChange={(event) => setModuleFilter(event.target.value)}
              className="h-10 flex-1 bg-background text-sm outline-none"
            >
              <option value="">All modules</option>
              {MODULES.map((module) => (
                <option key={module} value={module}>{moduleLabel(module)}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="min-h-0 flex-1 space-y-2 overflow-y-auto p-3">
          {definitionsQuery.isLoading ? (
            Array.from({ length: 5 }).map((_, index) => <div key={index} className="h-24 rounded-md bg-muted/50" />)
          ) : definitions.length ? (
            definitions.map((definition) => (
              <button
                key={definition.id}
                type="button"
                onClick={() => setSelectedId(definition.id)}
                className={cn(
                  "w-full rounded-md border p-3 text-left transition-colors hover:bg-accent",
                  selectedId === definition.id && "border-primary bg-primary/5"
                )}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold">{definition.name}</p>
                    <p className="truncate text-xs text-muted-foreground">{triggerLabel(definition.trigger_event)}</p>
                  </div>
                  <Badge className={moduleBadgeClass(definition.module)}>{moduleLabel(definition.module)}</Badge>
                </div>
                <div className="mt-3 flex items-center justify-between">
                  <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", definition.is_active ? "bg-green-100 text-green-700" : "bg-muted text-muted-foreground")}>
                    {definition.is_active ? "Active" : "Inactive"}
                  </span>
                  <span className="text-xs font-medium text-primary">Edit</span>
                </div>
              </button>
            ))
          ) : (
            <div className="rounded-md border border-dashed p-6 text-center text-sm text-muted-foreground">No workflows found</div>
          )}
        </div>
      </aside>

      <main className="min-w-0 flex-1 overflow-y-auto rounded-md border bg-background p-5">
        {!selectedId ? (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <GitBranch className="h-12 w-12 text-muted-foreground" />
            <h2 className="mt-4 text-lg font-semibold">Select or create a workflow</h2>
          </div>
        ) : selectedQuery.isLoading || !definitionDraft || !selected ? (
          <div className="space-y-4">
            <div className="h-12 rounded-md bg-muted/50" />
            {Array.from({ length: 3 }).map((_, index) => <div key={index} className="h-40 rounded-md bg-muted/50" />)}
          </div>
        ) : (
          <div className="space-y-5">
            <div className="flex flex-wrap items-start justify-between gap-4 border-b pb-4">
              <div className="min-w-72 flex-1 space-y-2">
                <Input
                  value={definitionDraft.name}
                  onChange={(event) => setDefinitionDraft({ ...definitionDraft, name: event.target.value })}
                  onBlur={() => updateDefinition.mutate(definitionDraft)}
                  className="h-11 text-lg font-semibold"
                />
                <div className="grid gap-2 md:grid-cols-2">
                  <SelectField
                    value={definitionDraft.module}
                    options={MODULES}
                    onChange={(module) => {
                      const trigger_event = TRIGGERS_BY_MODULE[module]?.[0] || "on_submit";
                      const nextDraft = { ...definitionDraft, module, trigger_event };
                      setDefinitionDraft(nextDraft);
                      updateDefinition.mutate(nextDraft);
                    }}
                  />
                  <SelectField
                    value={definitionDraft.trigger_event}
                    options={selectedTriggers}
                    onChange={(trigger_event) => {
                      const nextDraft = { ...definitionDraft, trigger_event };
                      setDefinitionDraft(nextDraft);
                      updateDefinition.mutate(nextDraft);
                    }}
                  />
                </div>
                <Input
                  value={definitionDraft.description}
                  onChange={(event) => setDefinitionDraft({ ...definitionDraft, description: event.target.value })}
                  onBlur={() => updateDefinition.mutate(definitionDraft)}
                  placeholder="Description"
                />
              </div>
              <div className="flex items-center gap-3">
                <Badge className={moduleBadgeClass(definitionDraft.module)}>{moduleLabel(definitionDraft.module)}</Badge>
                <span className="text-sm text-muted-foreground">{selectedStatus}</span>
                <SwitchControl checked={selected.is_active} onChange={(checked) => toggleActive.mutate(checked)} />
                <Button onClick={() => updateDefinition.mutate(definitionDraft)} disabled={updateDefinition.isPending}>
                  <Save className="h-4 w-4" />
                  Save
                </Button>
              </div>
            </div>

            <div className="space-y-3">
              {stepsDraft.map((step, index) => {
                const timeoutAction = timeoutActions[step.id] || (step.escalation_user_id ? "escalate" : "escalate");
                return (
                  <div key={step.id}>
                    <Card className="border-l-4 border-l-primary">
                      <CardContent className="grid gap-4 p-4 lg:grid-cols-[auto_1fr_1fr]">
                        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-sm font-semibold text-primary-foreground">
                          {index + 1}
                        </div>
                        <div className="grid gap-3 md:grid-cols-2">
                          <div className="space-y-1.5">
                            <Label>Step name</Label>
                            <Input value={step.step_type} onChange={(event) => updateStepDraft(step.id, { step_type: event.target.value })} onBlur={() => updateStep.mutate(step)} />
                          </div>
                          <div className="space-y-1.5">
                            <Label>Approver type</Label>
                            <SelectField value={step.approver_type} options={APPROVER_TYPES} onChange={(approver_type) => {
                              const patch = { approver_type, approver_value: approver_type === "role" ? "hr" : "" };
                              updateStepDraft(step.id, patch);
                              updateStep.mutate({ ...step, ...patch });
                            }} />
                          </div>
                          {(step.approver_type === "specific_user" || step.approver_type === "role") && (
                            <div className="space-y-1.5">
                              <Label>{step.approver_type === "role" ? "Approver role" : "Approver user ID"}</Label>
                              {step.approver_type === "role" ? (
                                <SelectField value={step.approver_value || "hr"} options={ROLE_OPTIONS} onChange={(approver_value) => {
                                  updateStepDraft(step.id, { approver_value });
                                  updateStep.mutate({ ...step, approver_value });
                                }} />
                              ) : (
                                <Input value={step.approver_value || ""} onChange={(event) => updateStepDraft(step.id, { approver_value: event.target.value })} onBlur={() => updateStep.mutate(step)} placeholder="Search or enter user ID" />
                              )}
                            </div>
                          )}
                          <div className="space-y-1.5">
                            <Label>Timeout (days)</Label>
                            <Input
                              type="number"
                              min={1}
                              value={Math.max(1, Math.round((step.timeout_hours || 72) / 24))}
                              onChange={(event) => updateStepDraft(step.id, { timeout_hours: Number(event.target.value || 1) * 24 })}
                              onBlur={() => updateStep.mutate(step)}
                            />
                          </div>
                          <div className="space-y-1.5">
                            <Label>On timeout</Label>
                            <SelectField
                              value={timeoutAction}
                              options={TIMEOUT_ACTIONS}
                              onChange={(value) => {
                                setTimeoutActions((actions) => ({ ...actions, [step.id]: value }));
                                if (value !== "escalate") {
                                  const nextStep = { ...step, escalation_user_id: null };
                                  updateStepDraft(step.id, { escalation_user_id: null });
                                  updateStep.mutate(nextStep);
                                }
                              }}
                            />
                          </div>
                          {timeoutAction === "escalate" && (
                            <div className="space-y-1.5">
                              <Label>Escalate to</Label>
                              <Input
                                type="number"
                                value={step.escalation_user_id || ""}
                                onChange={(event) => updateStepDraft(step.id, { escalation_user_id: event.target.value ? Number(event.target.value) : null })}
                                onBlur={() => updateStep.mutate(step)}
                                placeholder="Search or enter user ID"
                              />
                            </div>
                          )}
                          <div className="space-y-1.5 md:col-span-2">
                            <Label>Condition expression</Label>
                            <Input
                              value={step.condition_expression || ""}
                              onChange={(event) => updateStepDraft(step.id, { condition_expression: event.target.value })}
                              onBlur={() => updateStep.mutate(step)}
                              placeholder="e.g.: leave_days > 5 or amount > 50000"
                            />
                          </div>
                        </div>
                        <div className="flex justify-end">
                          <Button
                            variant="destructive"
                            size="icon"
                            disabled={stepsDraft.length <= 1 || deleteStep.isPending}
                            onClick={() => deleteStep.mutate(step.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                    {index < stepsDraft.length - 1 && <div className="py-2 text-center text-lg text-muted-foreground">→</div>}
                  </div>
                );
              })}
              <Button variant="outline" onClick={() => addStep.mutate()} disabled={!selectedId || addStep.isPending}>
                <Plus className="h-4 w-4" />
                Add Step
              </Button>
            </div>

            <div className="flex items-center justify-between border-t pt-4">
              <p className="text-sm text-muted-foreground">Last modified {selected.created_at ? formatDate(selected.created_at) : "-"}</p>
              <Button variant={selected.is_active ? "outline" : "default"} onClick={() => toggleActive.mutate(!selected.is_active)}>
                {selected.is_active ? "Deactivate" : "Activate"}
              </Button>
            </div>
          </div>
        )}
      </main>

      <Dialog.Root open={dialogOpen} onOpenChange={setDialogOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-50 bg-black/40" />
          <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-lg border bg-background p-6 shadow-xl">
            <Dialog.Title className="text-lg font-semibold">New Workflow</Dialog.Title>
            <Dialog.Description className="mt-1 text-sm text-muted-foreground">Create a workflow definition and add approval steps next.</Dialog.Description>
            <form
              className="mt-5 space-y-4"
              onSubmit={(event) => {
                event.preventDefault();
                createDefinition.mutate();
              }}
            >
              <div className="space-y-1.5">
                <Label>Name</Label>
                <Input value={newWorkflow.name} onChange={(event) => setNewWorkflow({ ...newWorkflow, name: event.target.value })} required />
              </div>
              <div className="space-y-1.5">
                <Label>Description</Label>
                <Input value={newWorkflow.description} onChange={(event) => setNewWorkflow({ ...newWorkflow, description: event.target.value })} />
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <div className="space-y-1.5">
                  <Label>Module</Label>
                  <SelectField value={newWorkflow.module} options={MODULES} onChange={(module) => setNewWorkflow({ ...newWorkflow, module, trigger_event: TRIGGERS_BY_MODULE[module][0] })} className="w-full" />
                </div>
                <div className="space-y-1.5">
                  <Label>Trigger event</Label>
                  <SelectField value={newWorkflow.trigger_event} options={filteredTriggers} onChange={(trigger_event) => setNewWorkflow({ ...newWorkflow, trigger_event })} className="w-full" />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Dialog.Close asChild>
                  <Button type="button" variant="outline">Cancel</Button>
                </Dialog.Close>
                <Button type="submit" disabled={!newWorkflow.name || createDefinition.isPending}>Create</Button>
              </div>
            </form>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
}
