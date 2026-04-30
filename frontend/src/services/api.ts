import axios, { AxiosError, AxiosResponse } from "axios";
import { useAuthStore } from "@/store/authStore";

const BASE_URL = import.meta.env.VITE_API_URL || "/api/v1";

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

// Request interceptor: attach access token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handle token refresh
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const original = error.config as typeof error.config & { _retry?: boolean };

    if (error.response?.status === 401 && !original?._retry) {
      original._retry = true;
      const { refreshToken, setTokens, logout } = useAuthStore.getState();

      if (refreshToken) {
        try {
          const res = await axios.post(`${BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          });
          const { access_token, refresh_token } = res.data;
          setTokens(access_token, refresh_token);
          if (original?.headers) {
            original.headers.Authorization = `Bearer ${access_token}`;
          }
          return api(original!);
        } catch {
          logout();
        }
      } else {
        logout();
      }
    }

    return Promise.reject(error);
  }
);

// API service functions
export const authApi = {
  login: (email: string, password: string) =>
    api.post("/auth/login", { email, password }),
  refresh: (refreshToken: string) =>
    api.post("/auth/refresh", { refresh_token: refreshToken }),
  me: () => api.get("/auth/me"),
  changePassword: (currentPassword: string, newPassword: string) =>
    api.post("/auth/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
    }),
  logout: () => api.post("/auth/logout"),
  permissions: () => api.get("/auth/permissions"),
  roles: () => api.get("/auth/roles"),
  createRole: (data: unknown) => api.post("/auth/roles", data),
  updateRole: (id: number, data: unknown) => api.put(`/auth/roles/${id}`, data),
  deleteRole: (id: number) => api.delete(`/auth/roles/${id}`),
};

export const employeeApi = {
  list: (params?: Record<string, unknown>) => api.get("/employees/", { params }),
  create: (data: unknown) => api.post("/employees/", data),
  get: (id: number) => api.get(`/employees/${id}`),
  update: (id: number, data: unknown) => api.put(`/employees/${id}`, data),
  delete: (id: number) => api.delete(`/employees/${id}`),
  stats: () => api.get("/employees/stats"),
  addEducation: (id: number, data: unknown) => api.post(`/employees/${id}/education`, data),
  addExperience: (id: number, data: unknown) => api.post(`/employees/${id}/experience`, data),
  addSkill: (id: number, data: unknown) => api.post(`/employees/${id}/skills`, data),
  uploadDocument: (id: number, formData: FormData) =>
    api.post(`/employees/${id}/documents`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  uploadPhoto: (id: number, formData: FormData) =>
    api.post(`/employees/${id}/photo`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
};

export const companyApi = {
  listCompanies: () => api.get("/company/"),
  createCompany: (data: unknown) => api.post("/company/", data),
  updateCompany: (id: number, data: unknown) => api.put(`/company/${id}`, data),
  deleteCompany: (id: number) => api.delete(`/company/${id}`),
  listBranches: (companyId?: number) =>
    api.get("/company/branches/", { params: { company_id: companyId } }),
  createBranch: (data: unknown) => api.post("/company/branches/", data),
  updateBranch: (id: number, data: unknown) => api.put(`/company/branches/${id}`, data),
  deleteBranch: (id: number) => api.delete(`/company/branches/${id}`),
  listDepartments: (branchId?: number) =>
    api.get("/company/departments/", { params: { branch_id: branchId } }),
  createDepartment: (data: unknown) => api.post("/company/departments/", data),
  updateDepartment: (id: number, data: unknown) => api.put(`/company/departments/${id}`, data),
  deleteDepartment: (id: number) => api.delete(`/company/departments/${id}`),
  listDesignations: (deptId?: number) =>
    api.get("/company/designations/", { params: { department_id: deptId } }),
  createDesignation: (data: unknown) => api.post("/company/designations/", data),
  updateDesignation: (id: number, data: unknown) =>
    api.put(`/company/designations/${id}`, data),
  deleteDesignation: (id: number) => api.delete(`/company/designations/${id}`),
};

export const attendanceApi = {
  checkIn: (data: unknown) => api.post("/attendance/check-in", data),
  checkOut: (data: unknown) => api.post("/attendance/check-out", data),
  getToday: () => api.get("/attendance/today"),
  myAttendance: (fromDate: string, toDate: string) =>
    api.get("/attendance/my", { params: { from_date: fromDate, to_date: toDate } }),
  employeeAttendance: (empId: number, fromDate: string, toDate: string) =>
    api.get(`/attendance/employee/${empId}`, {
      params: { from_date: fromDate, to_date: toDate },
    }),
  monthlySummary: (month: number, year: number, employeeId?: number) =>
    api.get("/attendance/summary/monthly", {
      params: { month, year, employee_id: employeeId },
    }),
  listShifts: () => api.get("/attendance/shifts"),
  createShift: (data: unknown) => api.post("/attendance/shifts", data),
  updateShift: (id: number, data: unknown) => api.put(`/attendance/shifts/${id}`, data),
  deleteShift: (id: number) => api.delete(`/attendance/shifts/${id}`),
  listHolidays: (year?: number) =>
    api.get("/attendance/holidays", { params: { year } }),
  createHoliday: (data: unknown) => api.post("/attendance/holidays", data),
  updateHoliday: (id: number, data: unknown) => api.put(`/attendance/holidays/${id}`, data),
  deleteHoliday: (id: number) => api.delete(`/attendance/holidays/${id}`),
  requestRegularization: (data: unknown) => api.post("/attendance/regularize", data),
  pendingRegularizations: () => api.get("/attendance/regularize/pending"),
  approveRegularization: (id: number, data: unknown) =>
    api.put(`/attendance/regularize/${id}/approve`, data),
};

export const leaveApi = {
  types: () => api.get("/leave/types"),
  createType: (data: unknown) => api.post("/leave/types", data),
  updateType: (id: number, data: unknown) => api.put(`/leave/types/${id}`, data),
  deleteType: (id: number) => api.delete(`/leave/types/${id}`),
  balance: (year?: number) => api.get("/leave/balance", { params: { year } }),
  apply: (data: unknown) => api.post("/leave/apply", data),
  myRequests: (params?: Record<string, unknown>) =>
    api.get("/leave/my-requests", { params }),
  allRequests: (params?: Record<string, unknown>) =>
    api.get("/leave/requests", { params }),
  approve: (id: number, data: unknown) =>
    api.put(`/leave/requests/${id}/approve`, data),
  cancel: (id: number) => api.put(`/leave/requests/${id}/cancel`),
};

export const payrollApi = {
  components: () => api.get("/payroll/components"),
  createComponent: (data: unknown) => api.post("/payroll/components", data),
  updateComponent: (id: number, data: unknown) => api.put(`/payroll/components/${id}`, data),
  deleteComponent: (id: number) => api.delete(`/payroll/components/${id}`),
  structures: () => api.get("/payroll/structures"),
  createStructure: (data: unknown) => api.post("/payroll/structures", data),
  setEmployeeSalary: (data: unknown) => api.post("/payroll/salary", data),
  salaryHistory: (empId: number) => api.get(`/payroll/salary/${empId}`),
  runs: () => api.get("/payroll/runs"),
  runPayroll: (data: unknown) => api.post("/payroll/run", data),
  getRun: (id: number) => api.get(`/payroll/runs/${id}`),
  approveRun: (id: number, data: unknown) => api.put(`/payroll/runs/${id}/approve`, data),
  runRecords: (runId: number) => api.get(`/payroll/runs/${runId}/records`),
  payslip: (month: number, year: number, empId?: number) =>
    api.get("/payroll/payslip", { params: { month, year, employee_id: empId } }),
  reimbursements: (params?: Record<string, unknown>) =>
    api.get("/payroll/reimbursements", { params }),
  createReimbursement: (data: unknown) => api.post("/payroll/reimbursements", data),
};

export const recruitmentApi = {
  jobs: (params?: Record<string, unknown>) => api.get("/recruitment/jobs", { params }),
  createJob: (data: unknown) => api.post("/recruitment/jobs", data),
  getJob: (id: number) => api.get(`/recruitment/jobs/${id}`),
  updateJob: (id: number, data: unknown) => api.put(`/recruitment/jobs/${id}`, data),
  candidates: (params?: Record<string, unknown>) =>
    api.get("/recruitment/candidates", { params }),
  createCandidate: (data: unknown) => api.post("/recruitment/candidates", data),
  getCandidate: (id: number) => api.get(`/recruitment/candidates/${id}`),
  updateCandidateStatus: (id: number, status: string) =>
    api.put(`/recruitment/candidates/${id}/status`, null, { params: { status } }),
  uploadResume: (id: number, formData: FormData) =>
    api.post(`/recruitment/candidates/${id}/resume`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  scheduleInterview: (data: unknown) => api.post("/recruitment/interviews", data),
  getInterviews: (candidateId: number) =>
    api.get(`/recruitment/candidates/${candidateId}/interviews`),
  addFeedback: (interviewId: number, data: unknown) =>
    api.post(`/recruitment/interviews/${interviewId}/feedback`, data),
  createOffer: (data: unknown) => api.post("/recruitment/offers", data),
  updateOfferStatus: (id: number, status: string) =>
    api.put(`/recruitment/offers/${id}/status`, null, { params: { status } }),
};

export const performanceApi = {
  cycles: () => api.get("/performance/cycles"),
  createCycle: (data: unknown) => api.post("/performance/cycles", data),
  goals: (cycleId?: number) =>
    api.get("/performance/goals", { params: { cycle_id: cycleId } }),
  createGoal: (data: unknown) => api.post("/performance/goals", data),
  updateGoal: (id: number, data: unknown) => api.put(`/performance/goals/${id}`, data),
  submitReview: (data: unknown) => api.post("/performance/reviews", data),
  employeeReviews: (empId: number, cycleId?: number) =>
    api.get(`/performance/reviews/${empId}`, { params: { cycle_id: cycleId } }),
};

export const helpdeskApi = {
  categories: () => api.get("/helpdesk/categories"),
  tickets: (params?: Record<string, unknown>) =>
    api.get("/helpdesk/tickets", { params }),
  createTicket: (data: Record<string, unknown>) =>
    api.post("/helpdesk/tickets", null, { params: data }),
  getTicket: (id: number) => api.get(`/helpdesk/tickets/${id}`),
  updateStatus: (id: number, status: string) =>
    api.put(`/helpdesk/tickets/${id}/status`, null, { params: { status } }),
  addReply: (ticketId: number, message: string, isInternal = false) =>
    api.post(`/helpdesk/tickets/${ticketId}/reply`, null, {
      params: { message, is_internal: isInternal },
    }),
  getReplies: (ticketId: number) =>
    api.get(`/helpdesk/tickets/${ticketId}/replies`),
};

export const reportsApi = {
  dashboard: () => api.get("/reports/dashboard"),
  headcountByDept: () => api.get("/reports/headcount-by-department"),
  attendanceTrend: (month: number, year: number) =>
    api.get("/reports/attendance-trend", { params: { month, year } }),
  leaveTrend: (year: number) =>
    api.get("/reports/leave-trend", { params: { year } }),
  payrollSummary: (year: number) =>
    api.get("/reports/payroll-summary", { params: { year } }),
  turnover: (fromDate: string, toDate: string) =>
    api.get("/reports/employee-turnover", { params: { from_date: fromDate, to_date: toDate } }),
  recruitmentFunnel: (jobId?: number) =>
    api.get("/reports/recruitment-funnel", { params: { job_id: jobId } }),
};

export const targetsApi = {
  industries: () => api.get("/targets/industries"),
  createIndustry: (data: unknown) => api.post("/targets/industries", data),
  updateIndustry: (id: number, data: unknown) => api.put(`/targets/industries/${id}`, data),
  deleteIndustry: (id: number) => api.delete(`/targets/industries/${id}`),
  plans: () => api.get("/targets/plans"),
  createPlan: (data: unknown) => api.post("/targets/plans", data),
  updatePlan: (id: number, data: unknown) => api.put(`/targets/plans/${id}`, data),
  deletePlan: (id: number) => api.delete(`/targets/plans/${id}`),
  features: (params?: Record<string, unknown>) => api.get("/targets/features", { params }),
  createFeature: (data: unknown) => api.post("/targets/features", data),
  updateFeature: (id: number, data: unknown) => api.put(`/targets/features/${id}`, data),
  deleteFeature: (id: number) => api.delete(`/targets/features/${id}`),
};

export const aiApi = {
  chat: (message: string, history?: unknown[]) =>
    api.post("/ai/assistant", { message, history }),
  policyQA: (question: string) =>
    api.post("/ai/policy-qa", { question }),
  parseResume: (candidateId: number) =>
    api.post(`/ai/parse-resume/${candidateId}`),
  attritionRisk: (departmentId?: number) =>
    api.get("/ai/attrition-risk", { params: { department_id: departmentId } }),
  employeeAttritionRisk: (empId: number) =>
    api.get(`/ai/attrition-risk/${empId}`),
  detectPayrollAnomalies: (runId: number) =>
    api.post(`/ai/payroll-anomaly/${runId}`),
  helpdeskReply: (ticketId: number) =>
    api.post(`/ai/helpdesk-reply/${ticketId}`),
};

export const assetApi = {
  categories: () => api.get("/assets/categories"),
  createCategory: (data: unknown) => api.post("/assets/categories", data),
  list: (params?: Record<string, unknown>) => api.get("/assets/", { params }),
  create: (data: unknown) => api.post("/assets/", data),
  update: (id: number, data: unknown) => api.put(`/assets/${id}`, data),
  assign: (data: unknown) => api.post("/assets/assignments", data),
  returnAsset: (assignmentId: number, condition?: string) =>
    api.put(`/assets/assignments/${assignmentId}/return`, null, {
      params: { condition_at_return: condition },
    }),
};

export const onboardingApi = {
  templates: () => api.get("/onboarding/templates"),
  createTemplate: (data: unknown) => api.post("/onboarding/templates", data),
  employees: () => api.get("/onboarding/employees"),
  start: (data: unknown) => api.post("/onboarding/employees", data),
  complete: (id: number) => api.put(`/onboarding/employees/${id}/complete`),
  acknowledgePolicy: (data: unknown) =>
    api.post("/onboarding/policy-acknowledgements", data),
};

export const documentsApi = {
  templates: () => api.get("/documents/templates"),
  createTemplate: (data: unknown) => api.post("/documents/templates", data),
  policies: () => api.get("/documents/policies"),
  createPolicy: (data: unknown) => api.post("/documents/policies", data),
  generated: (employeeId?: number) =>
    api.get("/documents/generated", { params: { employee_id: employeeId } }),
  createGenerated: (data: unknown) => api.post("/documents/generated", data),
};

export const exitApi = {
  records: () => api.get("/exit/records"),
  createRecord: (data: unknown) => api.post("/exit/records", data),
  updateRecord: (id: number, data: unknown) => api.put(`/exit/records/${id}`, data),
  approveRecord: (id: number) => api.put(`/exit/records/${id}/approve`),
  createChecklistItem: (data: unknown) => api.post("/exit/checklist", data),
  completeChecklistItem: (id: number, remarks?: string) =>
    api.put(`/exit/checklist/${id}/complete`, null, { params: { remarks } }),
};
