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
    filters?: { status?: string; assignee_id?: number }
  ) => {
    const params = new URLSearchParams();
    params.append("skip", skip.toString());
    params.append("limit", limit.toString());
    if (filters?.status) params.append("status", filters.status);
    if (filters?.assignee_id)
      params.append("assignee_id", filters.assignee_id.toString());

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

// ============= SPRINTS =============
export const sprintsAPI = {
  create: async (projectId: number, data: Omit<PMSSprint, "id" | "project_id" | "created_at" | "updated_at">) => {
    const response = await api.post<PMSSprint>(`${BASE_URL}/projects/${projectId}/sprints`, data);
    return response.data;
  },

  list: async (projectId: number) => {
    const response = await api.get<PMSSprint[]>(`${BASE_URL}/projects/${projectId}/sprints`);
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

