/**
 * KaryaFlow API Service
 * All API calls for project management
 */
import { api } from "@/services/api";
import {
  PMSProject,
  PMSTask,
  PMSBoard,
  PMSMilestone,
  PMSComment,
  PMSTimeLog,
  PMSFileAsset,
  PMSSprint,
  PMSEpic,
  PMSComponent,
  PMSRelease,
  PMSTaskDependency,
  PMSSavedFilter,
  PMSActivity,
  SprintBurndown,
  ProjectVelocity,
  ReleaseReadiness,
  WorkloadResponse,
  CreateProjectInput,
  CreateTaskInput,
  CreateMilestoneInput,
  CreateCommentInput,
  CreateTimeLogInput,
  CreateFileAssetInput,
  TaskReorderPayload,
  DashboardData,
} from "../types";

const BASE_URL = "/project-management";

// ============= PROJECTS =============
export const projectsAPI = {
  create: async (data: CreateProjectInput) => {
    const response = await api.post<PMSProject>(`${BASE_URL}/projects`, data);
    return response.data;
  },

  list: async (
    skip: number = 0,
    limit: number = 100,
    status?: string
  ) => {
    const params = new URLSearchParams();
    params.append("skip", skip.toString());
    params.append("limit", limit.toString());
    if (status) params.append("status", status);

    const response = await api.get<PMSProject[]>(
      `${BASE_URL}/projects?${params}`
    );
    return response.data;
  },

  get: async (projectId: number) => {
    const response = await api.get<PMSProject>(
      `${BASE_URL}/projects/${projectId}`
    );
    return response.data;
  },

  update: async (projectId: number, data: Partial<CreateProjectInput>) => {
    const response = await api.patch<PMSProject>(
      `${BASE_URL}/projects/${projectId}`,
      data
    );
    return response.data;
  },

  delete: async (projectId: number) => {
    const response = await api.delete(`${BASE_URL}/projects/${projectId}`);
    return response.data;
  },

  getDashboard: async (projectId: number) => {
    const response = await api.get<DashboardData>(
      `${BASE_URL}/dashboard/${projectId}`
    );
    return response.data;
  },
};

// ============= TASKS =============
export const tasksAPI = {
  create: async (projectId: number, data: CreateTaskInput) => {
    const payload = {
      ...data,
      task_key: data.task_key || `${Date.now().toString().slice(-5)}`,
    };
    const response = await api.post<PMSTask>(
      `${BASE_URL}/projects/${projectId}/tasks`,
      payload
    );
    return response.data;
  },

  list: async (
    projectId: number,
    skip: number = 0,
    limit: number = 100,
    filters?: {
      status?: string;
      assignee_id?: number;
      epic_id?: number;
      component_id?: number;
      release_id?: number;
      work_type?: string;
      epic_key?: string;
      component?: string;
      severity?: string;
      fix_version?: string;
      release_name?: string;
      security_level?: string;
      sprint_id?: number;
    }
  ) => {
    const params = new URLSearchParams();
    params.append("skip", skip.toString());
    params.append("limit", limit.toString());
    if (filters?.status) params.append("status", filters.status);
    if (filters?.assignee_id)
      params.append("assignee_id", filters.assignee_id.toString());
    if (filters?.epic_id) params.append("epic_id", filters.epic_id.toString());
    if (filters?.component_id)
      params.append("component_id", filters.component_id.toString());
    if (filters?.release_id)
      params.append("release_id", filters.release_id.toString());
    if (filters?.sprint_id)
      params.append("sprint_id", filters.sprint_id.toString());
    if (filters?.work_type) params.append("work_type", filters.work_type);
    if (filters?.epic_key) params.append("epic_key", filters.epic_key);
    if (filters?.component) params.append("component", filters.component);
    if (filters?.severity) params.append("severity", filters.severity);
    if (filters?.fix_version) params.append("fix_version", filters.fix_version);
    if (filters?.release_name) params.append("release_name", filters.release_name);
    if (filters?.security_level) params.append("security_level", filters.security_level);

    const response = await api.get<PMSTask[]>(
      `${BASE_URL}/projects/${projectId}/tasks?${params}`
    );
    return response.data;
  },

  get: async (taskId: number) => {
    const response = await api.get<PMSTask>(`${BASE_URL}/tasks/${taskId}`);
    return response.data;
  },

  update: async (taskId: number, data: Partial<CreateTaskInput>) => {
    const response = await api.patch<PMSTask>(
      `${BASE_URL}/tasks/${taskId}`,
      data
    );
    return response.data;
  },

  delete: async (taskId: number) => {
    const response = await api.delete(`${BASE_URL}/tasks/${taskId}`);
    return response.data;
  },

  updateStatus: async (taskId: number, status: string) => {
    return tasksAPI.update(taskId, { status: status as any });
  },

  bulkUpdate: async (payload: {
    task_ids: number[];
    status?: string;
    assignee_user_id?: number;
    priority?: string;
    sprint_id?: number;
    release_id?: number;
    component_id?: number;
  }) => {
    const response = await api.patch<{ updated_count: number; tasks: PMSTask[] }>(
      `${BASE_URL}/tasks/bulk`,
      payload
    );
    return response.data;
  },

  addDependency: async (taskId: number, dependsOnTaskId: number, dependencyType = "Finish To Start") => {
    const response = await api.post<PMSTaskDependency>(
      `${BASE_URL}/tasks/${taskId}/dependencies`,
      { depends_on_task_id: dependsOnTaskId, dependency_type: dependencyType }
    );
    return response.data;
  },

  listDependencies: async (taskId: number) => {
    const response = await api.get<PMSTaskDependency[]>(
      `${BASE_URL}/tasks/${taskId}/dependencies`
    );
    return response.data;
  },

  removeDependency: async (taskId: number, dependencyId: number) => {
    const response = await api.delete(`${BASE_URL}/tasks/${taskId}/dependencies/${dependencyId}`);
    return response.data;
  },
};

// ============= KANBAN BOARD (DRAG & DROP) =============
export const kanbanAPI = {
  getBoard: async (projectId: number) => {
    const response = await api.get<PMSBoard>(
      `${BASE_URL}/projects/${projectId}/board`
    );
    return response.data;
  },

  reorderTask: async (projectId: number, payload: TaskReorderPayload) => {
    const response = await api.post(
      `${BASE_URL}/projects/${projectId}/board/reorder`,
      payload
    );
    return response.data;
  },
};

// ============= COMMENTS (COLLABORATION) =============
export const commentsAPI = {
  addToTask: async (taskId: number, data: CreateCommentInput) => {
    const response = await api.post<PMSComment>(
      `${BASE_URL}/tasks/${taskId}/comments`,
      data
    );
    return response.data;
  },

  listForTask: async (taskId: number) => {
    const response = await api.get<PMSComment[]>(
      `${BASE_URL}/tasks/${taskId}/comments`
    );
    return response.data;
  },

  update: async (commentId: number, data: Partial<CreateCommentInput>) => {
    const response = await api.patch<PMSComment>(
      `${BASE_URL}/comments/${commentId}`,
      data
    );
    return response.data;
  },

  delete: async (commentId: number) => {
    const response = await api.delete(`${BASE_URL}/comments/${commentId}`);
    return response.data;
  },
};

// ============= MILESTONES =============
export const milestonesAPI = {
  create: async (projectId: number, data: CreateMilestoneInput) => {
    const response = await api.post<PMSMilestone>(
      `${BASE_URL}/projects/${projectId}/milestones`,
      data
    );
    return response.data;
  },

  list: async (
    projectId: number,
    skip: number = 0,
    limit: number = 100
  ) => {
    const params = new URLSearchParams();
    params.append("skip", skip.toString());
    params.append("limit", limit.toString());

    const response = await api.get<PMSMilestone[]>(
      `${BASE_URL}/projects/${projectId}/milestones?${params}`
    );
    return response.data;
  },

  submitApproval: async (milestoneId: number) => {
    const response = await api.post(`${BASE_URL}/milestones/${milestoneId}/submit-approval`);
    return response.data;
  },

  approve: async (milestoneId: number) => {
    const response = await api.post(`${BASE_URL}/milestones/${milestoneId}/approve`);
    return response.data;
  },

  reject: async (milestoneId: number, remarks: string) => {
    const response = await api.post(`${BASE_URL}/milestones/${milestoneId}/reject`, {
      status: "Rejected",
      remarks,
    });
    return response.data;
  },
};

// ============= PLANNING OBJECTS =============
export const planningAPI = {
  createEpic: async (projectId: number, data: Partial<PMSEpic>) => {
    const response = await api.post<PMSEpic>(
      `${BASE_URL}/projects/${projectId}/epics`,
      data
    );
    return response.data;
  },

  listEpics: async (projectId: number, status?: string) => {
    const params = new URLSearchParams();
    if (status) params.append("status", status);
    const response = await api.get<PMSEpic[]>(
      `${BASE_URL}/projects/${projectId}/epics?${params}`
    );
    return response.data;
  },

  createComponent: async (projectId: number, data: Partial<PMSComponent>) => {
    const response = await api.post<PMSComponent>(
      `${BASE_URL}/projects/${projectId}/components`,
      data
    );
    return response.data;
  },

  listComponents: async (projectId: number, activeOnly: boolean = true) => {
    const response = await api.get<PMSComponent[]>(
      `${BASE_URL}/projects/${projectId}/components?active_only=${activeOnly}`
    );
    return response.data;
  },

  createRelease: async (projectId: number, data: Partial<PMSRelease>) => {
    const response = await api.post<PMSRelease>(
      `${BASE_URL}/projects/${projectId}/releases`,
      data
    );
    return response.data;
  },

  listReleases: async (projectId: number, status?: string) => {
    const params = new URLSearchParams();
    if (status) params.append("status", status);
    const response = await api.get<PMSRelease[]>(
      `${BASE_URL}/projects/${projectId}/releases?${params}`
    );
    return response.data;
  },

  getReleaseReadiness: async (releaseId: number) => {
    const response = await api.get<ReleaseReadiness>(
      `${BASE_URL}/releases/${releaseId}/readiness`
    );
    return response.data;
  },
};

// ============= SPRINTS =============
export const sprintsAPI = {
  create: async (projectId: number, data: Partial<Omit<PMSSprint, "id" | "project_id" | "created_at" | "updated_at">>) => {
    const response = await api.post<PMSSprint>(`${BASE_URL}/projects/${projectId}/sprints`, data);
    return response.data;
  },

  list: async (projectId: number) => {
    const response = await api.get<PMSSprint[]>(`${BASE_URL}/projects/${projectId}/sprints`);
    return response.data;
  },

  start: async (sprintId: number) => {
    const response = await api.post<PMSSprint>(`${BASE_URL}/sprints/${sprintId}/start`);
    return response.data;
  },

  complete: async (sprintId: number, carryForwardSprintId?: number) => {
    const response = await api.post<PMSSprint>(`${BASE_URL}/sprints/${sprintId}/complete`, {
      carry_forward_sprint_id: carryForwardSprintId,
    });
    return response.data;
  },

  burndown: async (sprintId: number) => {
    const response = await api.get<SprintBurndown>(`${BASE_URL}/sprints/${sprintId}/burndown`);
    return response.data;
  },

  velocity: async (projectId: number) => {
    const response = await api.get<ProjectVelocity>(`${BASE_URL}/projects/${projectId}/velocity`);
    return response.data;
  },
};

// ============= SAVED FILTERS, ACTIVITY, REPORTS =============
export const savedFiltersAPI = {
  create: async (projectId: number, data: Partial<PMSSavedFilter>) => {
    const response = await api.post<PMSSavedFilter>(`${BASE_URL}/projects/${projectId}/saved-filters`, data);
    return response.data;
  },

  list: async (projectId: number, viewType?: string) => {
    const params = new URLSearchParams();
    if (viewType) params.append("view_type", viewType);
    const response = await api.get<PMSSavedFilter[]>(`${BASE_URL}/projects/${projectId}/saved-filters?${params}`);
    return response.data;
  },

  update: async (filterId: number, data: Partial<PMSSavedFilter>) => {
    const response = await api.patch<PMSSavedFilter>(`${BASE_URL}/saved-filters/${filterId}`, data);
    return response.data;
  },

  delete: async (filterId: number) => {
    const response = await api.delete(`${BASE_URL}/saved-filters/${filterId}`);
    return response.data;
  },
};

export const activityAPI = {
  list: async (projectId: number, filters?: { task_id?: number; limit?: number }) => {
    const params = new URLSearchParams();
    if (filters?.task_id) params.append("task_id", filters.task_id.toString());
    if (filters?.limit) params.append("limit", filters.limit.toString());
    const response = await api.get<PMSActivity[]>(`${BASE_URL}/projects/${projectId}/activity?${params}`);
    return response.data;
  },
};

export const reportsAPI = {
  workload: async (projectId: number, filters?: { group_by?: "user" | "sprint"; sprint_id?: number }) => {
    const params = new URLSearchParams();
    if (filters?.group_by) params.append("group_by", filters.group_by);
    if (filters?.sprint_id) params.append("sprint_id", filters.sprint_id.toString());
    const response = await api.get<WorkloadResponse>(`${BASE_URL}/projects/${projectId}/workload?${params}`);
    return response.data;
  },
};

// ============= FILES =============
export const filesAPI = {
  create: async (data: CreateFileAssetInput & { project_id?: number; task_id?: number; milestone_id?: number }) => {
    const response = await api.post<PMSFileAsset>(`${BASE_URL}/files`, data);
    return response.data;
  },

  list: async (filters?: { project_id?: number; task_id?: number }) => {
    const params = new URLSearchParams();
    if (filters?.project_id) params.append("project_id", filters.project_id.toString());
    if (filters?.task_id) params.append("task_id", filters.task_id.toString());
    const response = await api.get<PMSFileAsset[]>(`${BASE_URL}/files?${params}`);
    return response.data;
  },
};

// ============= TIME TRACKING =============
export const timeLogsAPI = {
  create: async (data: CreateTimeLogInput) => {
    const response = await api.post<PMSTimeLog>(`${BASE_URL}/time-logs`, data);
    return response.data;
  },

  list: async (
    skip: number = 0,
    limit: number = 100,
    filters?: { project_id?: number; user_id?: number }
  ) => {
    const params = new URLSearchParams();
    params.append("skip", skip.toString());
    params.append("limit", limit.toString());
    if (filters?.project_id)
      params.append("project_id", filters.project_id.toString());
    if (filters?.user_id) params.append("user_id", filters.user_id.toString());

    const response = await api.get<PMSTimeLog[]>(
      `${BASE_URL}/time-logs?${params}`
    );
    return response.data;
  },
};

// ============= MODULE INFO =============
export const moduleAPI = {
  getInfo: async () => {
    const response = await api.get(`${BASE_URL}/module-info`);
    return response.data;
  },
};

