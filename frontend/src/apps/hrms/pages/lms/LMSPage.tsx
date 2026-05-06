import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Award, BookOpenCheck, GraduationCap, Plus, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { lmsApi } from "@/services/api";
import { usePageTitle } from "@/hooks/use-page-title";
import { toast } from "@/hooks/use-toast";

type Course = {
  id: number;
  code: string;
  title: string;
  category?: string;
  delivery_mode: string;
  duration_hours: string | number;
  is_mandatory: boolean;
};

type Assignment = {
  id: number;
  course_id: number;
  employee_id: number;
  status: string;
  due_date?: string;
  score?: string | number;
};

type Certification = {
  id: number;
  employee_id: number;
  title: string;
  status: string;
  expires_on?: string;
};

export default function LMSPage() {
  usePageTitle("Learning");
  const qc = useQueryClient();
  const [showCourseForm, setShowCourseForm] = useState(false);
  const [courseForm, setCourseForm] = useState({
    code: "",
    title: "",
    category: "Compliance",
    delivery_mode: "Online",
    duration_hours: "1",
    is_mandatory: true,
  });

  const { data: courses, isLoading } = useQuery({
    queryKey: ["lms-courses"],
    queryFn: () => lmsApi.courses().then((r) => r.data as Course[]),
  });
  const { data: assignments } = useQuery({
    queryKey: ["lms-assignments"],
    queryFn: () => lmsApi.assignments().then((r) => r.data as Assignment[]),
  });
  const { data: certifications } = useQuery({
    queryKey: ["lms-certifications"],
    queryFn: () => lmsApi.certifications().then((r) => r.data as Certification[]),
  });

  const createCourse = useMutation({
    mutationFn: () =>
      lmsApi.createCourse({
        ...courseForm,
        duration_hours: Number(courseForm.duration_hours || 0),
      }),
    onSuccess: () => {
      toast({ title: "Course published" });
      setShowCourseForm(false);
      setCourseForm({
        code: "",
        title: "",
        category: "Compliance",
        delivery_mode: "Online",
        duration_hours: "1",
        is_mandatory: true,
      });
      qc.invalidateQueries({ queryKey: ["lms-courses"] });
    },
    onError: () => toast({ title: "Unable to publish course", variant: "destructive" }),
  });

  const completed = (assignments || []).filter((item) => item.status === "Completed").length;
  const pending = (assignments || []).filter((item) => item.status !== "Completed").length;
  const courseTitleById = new Map((courses || []).map((course) => [course.id, course.title]));
  const expiring = (certifications || []).filter((cert) => {
    if (!cert.expires_on) return false;
    const days = (new Date(cert.expires_on).getTime() - Date.now()) / 86400000;
    return days >= 0 && days <= 45;
  }).length;

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 rounded-lg border bg-card p-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="page-title">Learning Management</h1>
          <p className="page-description">Courses, employee assignments, mandatory training, certifications, and renewal tracking.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => qc.invalidateQueries({ queryKey: ["lms-courses"] })}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button size="sm" onClick={() => setShowCourseForm((value) => !value)}>
            <Plus className="mr-2 h-4 w-4" />
            New Course
          </Button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { label: "Courses", value: courses?.length || 0, icon: GraduationCap },
          { label: "Pending Assignments", value: pending, icon: BookOpenCheck },
          { label: "Completed", value: completed, icon: Award },
          { label: "Certificates Expiring", value: expiring, icon: RefreshCw },
        ].map((item) => {
          const Icon = item.icon;
          return (
            <Card key={item.label}>
              <CardContent className="p-5">
                <Icon className="mb-3 h-5 w-5 text-primary" />
                <p className="text-2xl font-semibold">{item.value}</p>
                <p className="text-sm text-muted-foreground">{item.label}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {showCourseForm && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Publish Course</CardTitle>
            <CardDescription>Create a course that HR can assign by employee or role.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-3">
            <div className="space-y-1.5">
              <Label>Code</Label>
              <Input value={courseForm.code} onChange={(e) => setCourseForm({ ...courseForm, code: e.target.value })} placeholder="POSH-101" />
            </div>
            <div className="space-y-1.5 sm:col-span-2">
              <Label>Title</Label>
              <Input value={courseForm.title} onChange={(e) => setCourseForm({ ...courseForm, title: e.target.value })} />
            </div>
            <div className="space-y-1.5">
              <Label>Category</Label>
              <Input value={courseForm.category} onChange={(e) => setCourseForm({ ...courseForm, category: e.target.value })} />
            </div>
            <div className="space-y-1.5">
              <Label>Delivery</Label>
              <select className="h-10 w-full rounded-md border bg-background px-3 text-sm" value={courseForm.delivery_mode} onChange={(e) => setCourseForm({ ...courseForm, delivery_mode: e.target.value })}>
                {["Online", "Classroom", "Blended", "External"].map((mode) => <option key={mode}>{mode}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <Label>Hours</Label>
              <Input type="number" value={courseForm.duration_hours} onChange={(e) => setCourseForm({ ...courseForm, duration_hours: e.target.value })} />
            </div>
            <div className="flex gap-2 sm:col-span-3">
              <Button disabled={!courseForm.code || !courseForm.title || createCourse.isPending} onClick={() => createCourse.mutate()}>
                Publish
              </Button>
              <Button variant="outline" onClick={() => setShowCourseForm(false)}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Course Catalog</CardTitle>
            <CardDescription>Role-based and compliance learning content.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {isLoading ? <div className="h-24 rounded-lg bg-muted/40" /> : courses?.length ? courses.map((course) => (
              <div key={course.id} className="grid gap-3 rounded-lg border p-4 sm:grid-cols-[1fr_auto] sm:items-center">
                <div>
                  <p className="font-medium">{course.title}</p>
                  <p className="text-sm text-muted-foreground">{course.code} - {course.category || "General"} - {course.delivery_mode}</p>
                </div>
                <div className="flex flex-wrap gap-2 sm:justify-end">
                  <span className="rounded-full bg-muted px-2 py-0.5 text-xs">{course.duration_hours} hrs</span>
                  {course.is_mandatory && <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-800">Mandatory</span>}
                </div>
              </div>
            )) : <p className="rounded-lg border p-4 text-sm text-muted-foreground">No courses published yet.</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Learning Queue</CardTitle>
            <CardDescription>Recent assignments and certificate renewals.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {(assignments || []).slice(0, 5).map((item) => (
              <div key={item.id} className="rounded-lg border p-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-medium">Employee #{item.employee_id}</p>
                  <span className="rounded-full bg-muted px-2 py-0.5 text-xs">{item.status}</span>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">{courseTitleById.get(item.course_id) || `Course ${item.course_id}`}{item.due_date ? ` due ${item.due_date}` : ""}</p>
              </div>
            ))}
            {(certifications || []).slice(0, 4).map((cert) => (
              <div key={`cert-${cert.id}`} className="rounded-lg border p-3">
                <p className="text-sm font-medium">{cert.title}</p>
                <p className="mt-1 text-sm text-muted-foreground">Employee #{cert.employee_id}{cert.expires_on ? ` expires ${cert.expires_on}` : ""}</p>
              </div>
            ))}
            {!assignments?.length && !certifications?.length && <p className="rounded-lg border p-4 text-sm text-muted-foreground">No learning activity yet.</p>}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
