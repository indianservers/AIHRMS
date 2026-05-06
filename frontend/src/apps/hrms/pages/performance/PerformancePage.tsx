import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Target, Plus, Star, TrendingUp, CheckCircle2, RefreshCw, MessageSquareText
} from "lucide-react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { performanceApi } from "@/services/api";
import { formatDate, statusColor } from "@/lib/utils";
import { usePageTitle } from "@/hooks/use-page-title";
import { toast } from "@/hooks/use-toast";

interface Cycle {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  status: string;
}

interface Goal {
  id: number;
  title: string;
  description?: string;
  target_value?: number;
  current_value?: number;
  unit?: string;
  due_date?: string;
  status: string;
  priority?: string;
  progress_pct?: number;
}

interface GoalForm {
  title: string;
  description?: string;
  due_date?: string;
  target_value?: number;
  unit?: string;
  priority?: string;
  cycle_id?: number;
}

interface ReviewForm {
  rating: number;
  self_comments?: string;
  goals_achieved?: number;
  cycle_id?: number;
}

interface Feedback360Request {
  id: number;
  employee_id: number;
  reviewer_id: number;
  relationship_type: string;
  due_date?: string;
  status: string;
  overall_rating?: number;
  comments?: string;
  created_at: string;
}

export default function PerformancePage() {
  usePageTitle("Performance");
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState<"goals" | "reviews" | "360">("goals");
  const [showGoalForm, setShowGoalForm] = useState(false);
  const [selectedCycle, setSelectedCycle] = useState<number | "">("");

  const { data: cycles } = useQuery({
    queryKey: ["perf-cycles"],
    queryFn: () => performanceApi.cycles().then((r) => r.data),
  });

  const { data: goals, isLoading: loadingGoals, refetch: refetchGoals } = useQuery({
    queryKey: ["goals", selectedCycle],
    queryFn: () =>
      performanceApi.goals(selectedCycle ? Number(selectedCycle) : undefined).then((r) => r.data),
  });

  const { data: feedback360, isLoading: loading360 } = useQuery({
    queryKey: ["feedback-360-requests"],
    queryFn: () => performanceApi.feedback360Requests().then((r) => r.data as Feedback360Request[]),
    retry: false,
  });

  const { register: regGoal, handleSubmit: submitGoal, reset: resetGoal, formState: { errors: goalErrors } } = useForm<GoalForm>();
  const { register: regReview, handleSubmit: submitReview, reset: resetReview } = useForm<ReviewForm>({
    defaultValues: { rating: 3, goals_achieved: 0 },
  });

  const createGoalMutation = useMutation({
    mutationFn: (data: GoalForm) =>
      performanceApi.createGoal({
        ...data,
        cycle_id: selectedCycle ? Number(selectedCycle) : undefined,
        target_value: data.target_value ? Number(data.target_value) : undefined,
      }),
    onSuccess: () => {
      toast({ title: "Goal created!" });
      resetGoal();
      setShowGoalForm(false);
      refetchGoals();
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Failed";
      toast({ title: "Error", description: msg, variant: "destructive" });
    },
  });

  const updateGoalMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Goal> }) =>
      performanceApi.updateGoal(id, data),
    onSuccess: () => {
      toast({ title: "Goal updated" });
      refetchGoals();
    },
  });

  const submitReviewMutation = useMutation({
    mutationFn: (data: ReviewForm) =>
      performanceApi.submitReview({
        cycle_id: selectedCycle ? Number(selectedCycle) : undefined,
        review_type: "Self",
        overall_rating: Number(data.rating),
        comments: data.self_comments,
        strengths: `Goals achieved: ${Number(data.goals_achieved || 0)} of ${totalGoals}`,
      }),
    onSuccess: () => {
      toast({ title: "Review submitted!" });
      resetReview();
    },
    onError: (e: unknown) => {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Failed";
      toast({ title: "Error", description: msg, variant: "destructive" });
    },
  });

  const completedGoals = (goals as Goal[])?.filter((g) => g.status === "Completed").length ?? 0;
  const totalGoals = (goals as Goal[])?.length ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Performance</h1>
          <p className="page-description">Manage goals, track progress, and submit reviews.</p>
        </div>
        {activeTab === "goals" && (
          <Button size="sm" onClick={() => setShowGoalForm((v) => !v)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Goal
          </Button>
        )}
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Total Goals", value: totalGoals, color: "text-blue-600" },
          { label: "Completed", value: completedGoals, color: "text-green-600" },
          { label: "In Progress", value: (goals as Goal[])?.filter((g) => g.status === "In Progress").length ?? 0, color: "text-orange-600" },
          { label: "Overdue", value: (goals as Goal[])?.filter((g) => g.status === "Overdue").length ?? 0, color: "text-red-600" },
        ].map((s) => (
          <Card key={s.label}>
            <CardContent className="p-4 text-center">
              <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
              <p className="text-xs text-muted-foreground mt-1">{s.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Cycle selector */}
      <div className="flex items-center gap-3">
        <Label className="text-sm">Review Cycle</Label>
        <select
          value={selectedCycle}
          onChange={(e) => setSelectedCycle(e.target.value ? Number(e.target.value) : "")}
          className="flex h-9 rounded-md border border-input bg-background px-3 py-2 text-sm"
        >
          <option value="">All Cycles</option>
          {(cycles as Cycle[])?.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b">
        {(["goals", "reviews", "360"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-2 px-1 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab === "goals" ? "My Goals" : tab === "reviews" ? "Submit Review" : "360 Reviews"}
          </button>
        ))}
      </div>

      {activeTab === "goals" && (
        <div className="space-y-4">
          {/* Create goal form */}
          {showGoalForm && (
            <Card>
              <CardHeader><CardTitle className="text-base">New Goal</CardTitle></CardHeader>
              <CardContent>
                <form
                  onSubmit={submitGoal((data) => createGoalMutation.mutate(data))}
                  className="grid grid-cols-1 sm:grid-cols-2 gap-4"
                >
                  <div className="sm:col-span-2 space-y-1.5">
                    <Label>Goal Title *</Label>
                    <Input {...regGoal("title", { required: "Required" })} placeholder="e.g. Complete Q2 product launch" />
                    {goalErrors.title && <p className="text-xs text-red-500">{goalErrors.title.message}</p>}
                  </div>
                  <div className="sm:col-span-2 space-y-1.5">
                    <Label>Description</Label>
                    <textarea
                      {...regGoal("description")}
                      rows={2}
                      className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none"
                      placeholder="Describe the goal..."
                    />
                  </div>
                  <div className="space-y-1.5">
                    <Label>Target Value</Label>
                    <Input type="number" {...regGoal("target_value")} placeholder="e.g. 100" />
                  </div>
                  <div className="space-y-1.5">
                    <Label>Unit</Label>
                    <Input {...regGoal("unit")} placeholder="e.g. %, deals, tasks" />
                  </div>
                  <div className="space-y-1.5">
                    <Label>Due Date</Label>
                    <Input type="date" {...regGoal("due_date")} />
                  </div>
                  <div className="space-y-1.5">
                    <Label>Priority</Label>
                    <select
                      {...regGoal("priority")}
                      className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="">Normal</option>
                      <option value="High">High</option>
                      <option value="Medium">Medium</option>
                      <option value="Low">Low</option>
                    </select>
                  </div>
                  <div className="sm:col-span-2 flex gap-3">
                    <Button type="submit" disabled={createGoalMutation.isPending}>
                      {createGoalMutation.isPending ? "Creating..." : "Create Goal"}
                    </Button>
                    <Button type="button" variant="outline" onClick={() => setShowGoalForm(false)}>Cancel</Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {/* Goals list */}
          {loadingGoals ? (
            Array.from({ length: 4 }).map((_, i) => (
              <Card key={i}><CardContent className="p-5"><div className="h-16 skeleton rounded" /></CardContent></Card>
            ))
          ) : !(goals as Goal[])?.length ? (
            <Card>
              <CardContent className="p-12 text-center text-muted-foreground">
                <Target className="h-10 w-10 mx-auto mb-3 opacity-30" />
                <p>No goals yet. Add your first goal!</p>
              </CardContent>
            </Card>
          ) : (
            (goals as Goal[]).map((goal) => {
              const progress = goal.progress_pct ?? (goal.target_value && goal.current_value != null
                ? Math.min(100, (goal.current_value / goal.target_value) * 100)
                : 0);

              return (
                <Card key={goal.id}>
                  <CardContent className="p-5">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h3 className="font-semibold text-sm">{goal.title}</h3>
                          {goal.priority && (
                            <span className={`text-xs px-1.5 py-0.5 rounded ${statusColor(goal.priority)}`}>
                              {goal.priority}
                            </span>
                          )}
                        </div>
                        {goal.description && (
                          <p className="text-xs text-muted-foreground">{goal.description}</p>
                        )}
                        {goal.target_value && (
                          <p className="text-xs text-muted-foreground">
                            Progress: {goal.current_value ?? 0} / {goal.target_value} {goal.unit || ""}
                          </p>
                        )}
                        <div className="h-1.5 bg-muted rounded-full overflow-hidden w-full max-w-xs">
                          <div
                            className="h-full bg-primary rounded-full transition-all"
                            style={{ width: `${progress}%` }}
                          />
                        </div>
                        <p className="text-xs text-muted-foreground">{Math.round(progress)}% complete</p>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${statusColor(goal.status)}`}>
                          {goal.status}
                        </span>
                        {goal.due_date && (
                          <span className="text-xs text-muted-foreground">Due {formatDate(goal.due_date)}</span>
                        )}
                        {goal.status !== "Completed" && (
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-7 text-xs"
                            onClick={() => updateGoalMutation.mutate({ id: goal.id, data: { status: "Completed" } })}
                          >
                            <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
                            Mark Done
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })
          )}
        </div>
      )}

      {activeTab === "reviews" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Self Review</CardTitle>
            <CardDescription>Submit your performance self-assessment</CardDescription>
          </CardHeader>
          <CardContent>
            <form
              onSubmit={submitReview((data) => submitReviewMutation.mutate(data))}
              className="space-y-6"
            >
              {/* Star rating */}
              <div className="space-y-2">
                <Label>Overall Rating *</Label>
                <div className="flex gap-3">
                  {[1, 2, 3, 4, 5].map((r) => (
                    <label key={r} className="cursor-pointer">
                      <input
                        type="radio"
                        value={r}
                        {...regReview("rating")}
                        className="sr-only"
                      />
                      <Star className="h-8 w-8 text-yellow-400 fill-yellow-400 hover:scale-110 transition-transform" />
                    </label>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">Rating: 1 (Needs Improvement) â€“ 5 (Exceptional)</p>
              </div>

              <div className="space-y-1.5">
                <Label>Goals Achieved</Label>
                <Input
                  type="number"
                  min={0}
                  max={totalGoals}
                  {...regReview("goals_achieved")}
                  placeholder={`Out of ${totalGoals} goals`}
                />
              </div>

              <div className="space-y-1.5">
                <Label>Self Comments</Label>
                <textarea
                  {...regReview("self_comments")}
                  rows={4}
                  className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none"
                  placeholder="Summarize your achievements, challenges, and areas for growth..."
                />
              </div>

              <Button type="submit" disabled={submitReviewMutation.isPending}>
                {submitReviewMutation.isPending ? "Submitting..." : "Submit Review"}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {activeTab === "360" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">360 Reviews</CardTitle>
            <CardDescription>Pending and submitted feedback requests</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {loading360 ? (
              Array.from({ length: 3 }).map((_, i) => <div key={i} className="h-16 skeleton rounded" />)
            ) : !(feedback360 || []).length ? (
              <div className="rounded-lg border p-8 text-center text-sm text-muted-foreground">
                <MessageSquareText className="mx-auto mb-3 h-8 w-8 opacity-40" />
                No 360 feedback requests assigned.
              </div>
            ) : (
              (feedback360 || []).map((item) => (
                <div key={item.id} className="flex flex-col gap-3 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm font-medium">Employee #{item.employee_id} feedback</p>
                    <p className="text-xs text-muted-foreground">
                      {item.relationship_type} review {item.due_date ? `due ${formatDate(item.due_date)}` : "with no due date"}
                    </p>
                    {item.comments && <p className="mt-2 text-xs text-muted-foreground">{item.comments}</p>}
                  </div>
                  <Badge variant={item.status === "Submitted" ? "default" : "secondary"}>{item.status}</Badge>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
