import axios, { AxiosError, AxiosResponse } from "axios";
import { useAuthStore } from "@/store/authStore";
import { getApiBaseUrl } from "@/config/runtime";

const BASE_URL = getApiBaseUrl();

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
  me: () => api.get("/employees/me"),
  exportCsv: (params?: Record<string, unknown>) =>
    api.get("/employees/export", { params, responseType: "blob" }),
  importCsv: (formData: FormData) =>
    api.post("/employees/import", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
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
  expiringDocuments: (params?: Record<string, unknown>) =>
    api.get("/employees/documents/expiring", { params }),
  verifyDocument: (employeeId: number, documentId: number, data: unknown) =>
    api.put(`/employees/${employeeId}/documents/${documentId}/verify`, data),
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
  biometricDevices: () => api.get("/attendance/biometric/devices"),
  createBiometricDevice: (data: unknown) => api.post("/attendance/biometric/devices", data),
  importBiometricPunches: (data: unknown) => api.post("/attendance/biometric/import", data),
  geoPolicies: () => api.get("/attendance/geo/policies"),
  createGeoPolicy: (data: unknown) => api.post("/attendance/geo/policies", data),
  geoPunch: (data: unknown) => api.post("/attendance/geo/punch", data),
};

export const customFieldsApi = {
  definitions: (params?: Record<string, unknown>) => api.get("/custom-fields/definitions", { params }),
  createDefinition: (data: unknown) => api.post("/custom-fields/definitions", data),
  values: (params: Record<string, unknown>) => api.get("/custom-fields/values", { params }),
  upsertValue: (data: unknown) => api.put("/custom-fields/values", data),
};

export const logsApi = {
  audit: (params?: Record<string, unknown>) => api.get("/logs/audit", { params }),
  errors: (params?: Record<string, unknown>) => api.get("/logs/errors", { params }),
  analysis: (params?: Record<string, unknown>) => api.get("/logs/analysis", { params }),
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
  calendar: (params?: Record<string, unknown>) =>
    api.get("/leave/calendar", { params }),
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
  cloneStructure: (id: number, params: Record<string, unknown>) =>
    api.post(`/payroll/structures/${id}/clone`, null, { params }),
  previewStructure: (id: number, data: unknown) =>
    api.post(`/payroll/structures/${id}/preview`, data),
  formulaGraph: (id: number) => api.get(`/payroll/structures/${id}/formula-graph`),
  setEmployeeSalary: (data: unknown) => api.post("/payroll/salary", data),
  salaryHistory: (empId: number) => api.get(`/payroll/salary/${empId}`),
  salaryTemplates: (params?: Record<string, unknown>) => api.get("/payroll/salary-templates", { params }),
  createSalaryTemplate: (data: unknown) => api.post("/payroll/salary-templates", data),
  salaryRevisions: (params?: Record<string, unknown>) =>
    api.get("/payroll/salary-revisions", { params }),
  createSalaryRevision: (data: unknown) => api.post("/payroll/salary-revisions", data),
  reviewSalaryRevision: (id: number, data: unknown) =>
    api.put(`/payroll/salary-revisions/${id}/review`, data),
  salaryAudit: (params?: Record<string, unknown>) =>
    api.get("/payroll/salary-audit", { params }),
  runs: () => api.get("/payroll/runs"),
  runPayroll: (data: unknown) => api.post("/payroll/run", data),
  getRun: (id: number) => api.get(`/payroll/runs/${id}`),
  approveRun: (id: number, data: unknown) => api.put(`/payroll/runs/${id}/approve`, data),
  runRecords: (runId: number) => api.get(`/payroll/runs/${runId}/records`),
  runVariance: (runId: number) => api.get(`/payroll/runs/${runId}/variance`),
  exportRun: (runId: number, exportType: string) =>
    api.post(`/payroll/runs/${runId}/exports/${exportType}`),
  runAudit: (runId: number) => api.get(`/payroll/runs/${runId}/audit`),
  preRunChecks: (runId: number) => api.get(`/payroll/runs/${runId}/pre-run-checks`),
  addPreRunCheck: (runId: number, data: unknown) =>
    api.post(`/payroll/runs/${runId}/pre-run-checks`, data),
  manualInputs: (runId: number) => api.get(`/payroll/runs/${runId}/manual-inputs`),
  createManualInput: (runId: number, data: unknown) =>
    api.post(`/payroll/runs/${runId}/manual-inputs`, data),
  reviewManualInput: (id: number, data: unknown) =>
    api.put(`/payroll/manual-inputs/${id}/review`, data),
  createUnlockRequest: (runId: number, data: unknown) =>
    api.post(`/payroll/runs/${runId}/unlock-requests`, data),
  reviewUnlockRequest: (id: number, data: unknown) =>
    api.put(`/payroll/unlock-requests/${id}/review`, data),
  publishPayslips: (runId: number, data: unknown) =>
    api.post(`/payroll/runs/${runId}/payslip-publish`, data),
  payslip: (month: number, year: number, empId?: number) =>
    api.get("/payroll/payslip", { params: { month, year, employee_id: empId } }),
  payGroups: () => api.get("/payroll/setup/pay-groups"),
  createPayGroup: (data: unknown) => api.post("/payroll/setup/pay-groups", data),
  payrollPeriods: (params?: Record<string, unknown>) => api.get("/payroll/setup/periods", { params }),
  createPayrollPeriod: (data: unknown) => api.post("/payroll/setup/periods", data),
  payrollCalendars: (params?: Record<string, unknown>) => api.get("/payroll/setup/calendars", { params }),
  createPayrollCalendar: (data: unknown) => api.post("/payroll/setup/calendars", data),
  complianceRules: (params?: Record<string, unknown>) => api.get("/payroll/setup/compliance-rules", { params }),
  createComplianceRule: (data: unknown) => api.post("/payroll/setup/compliance-rules", data),
  bankAdviceFormats: () => api.get("/payroll/setup/bank-advice-formats"),
  createBankAdviceFormat: (data: unknown) => api.post("/payroll/setup/bank-advice-formats", data),
  pfRules: () => api.get("/payroll/statutory/pf-rules"),
  createPfRule: (data: unknown) => api.post("/payroll/statutory/pf-rules", data),
  esiRules: () => api.get("/payroll/statutory/esi-rules"),
  createEsiRule: (data: unknown) => api.post("/payroll/statutory/esi-rules", data),
  ptSlabs: (params?: Record<string, unknown>) => api.get("/payroll/statutory/pt-slabs", { params }),
  createPtSlab: (data: unknown) => api.post("/payroll/statutory/pt-slabs", data),
  lwfSlabs: (params?: Record<string, unknown>) => api.get("/payroll/statutory/lwf-slabs", { params }),
  createLwfSlab: (data: unknown) => api.post("/payroll/statutory/lwf-slabs", data),
  gratuityRules: () => api.get("/payroll/statutory/gratuity-rules"),
  createGratuityRule: (data: unknown) => api.post("/payroll/statutory/gratuity-rules", data),
  statutoryProfiles: (params?: Record<string, unknown>) => api.get("/payroll/statutory/employee-profiles", { params }),
  createStatutoryProfile: (data: unknown) => api.post("/payroll/statutory/employee-profiles", data),
  calculateStatutory: (data: unknown) => api.post("/payroll/statutory/calculate", data),
  statutoryContributionLines: (params?: Record<string, unknown>) =>
    api.get("/payroll/statutory/contribution-lines", { params }),
  payrollAttendanceInputs: (params?: Record<string, unknown>) =>
    api.get("/payroll/inputs/attendance", { params }),
  createPayrollAttendanceInput: (data: unknown) => api.post("/payroll/inputs/attendance", data),
  reconcilePayrollAttendance: (data: unknown) => api.post("/payroll/inputs/reconcile-attendance", data),
  lopAdjustments: (params?: Record<string, unknown>) => api.get("/payroll/inputs/lop-adjustments", { params }),
  createLopAdjustment: (data: unknown) => api.post("/payroll/inputs/lop-adjustments", data),
  overtimePolicies: () => api.get("/payroll/inputs/overtime-policies"),
  createOvertimePolicy: (data: unknown) => api.post("/payroll/inputs/overtime-policies", data),
  overtimeLines: (params?: Record<string, unknown>) => api.get("/payroll/inputs/overtime-lines", { params }),
  createOvertimeLine: (data: unknown) => api.post("/payroll/inputs/overtime-lines", data),
  leaveEncashmentPolicies: () => api.get("/payroll/inputs/leave-encashment-policies"),
  createLeaveEncashmentPolicy: (data: unknown) => api.post("/payroll/inputs/leave-encashment-policies", data),
  leaveEncashmentLines: (params?: Record<string, unknown>) =>
    api.get("/payroll/inputs/leave-encashment-lines", { params }),
  createLeaveEncashmentLine: (data: unknown) => api.post("/payroll/inputs/leave-encashment-lines", data),
  runWorksheet: (runId: number) => api.get(`/payroll/runs/${runId}/worksheet`),
  processRunWorksheet: (runId: number) => api.post(`/payroll/runs/${runId}/worksheet/process`),
  calculationSnapshots: (runId: number, params?: Record<string, unknown>) =>
    api.get(`/payroll/runs/${runId}/calculation-snapshots`, { params }),
  createArrearRun: (data: unknown) => api.post("/payroll/arrear-runs", data),
  arrearRuns: (params?: Record<string, unknown>) => api.get("/payroll/arrear-runs", { params }),
  createOffCycleRun: (data: unknown) => api.post("/payroll/off-cycle-runs", data),
  offCycleRuns: (params?: Record<string, unknown>) => api.get("/payroll/off-cycle-runs", { params }),
  createPaymentBatch: (data: unknown) => api.post("/payroll/payments/batches", data),
  paymentBatches: (params?: Record<string, unknown>) => api.get("/payroll/payments/batches", { params }),
  importPaymentStatus: (batchId: number, data: unknown) =>
    api.put(`/payroll/payments/batches/${batchId}/status-import`, data),
  accountingLedgers: () => api.get("/payroll/accounting/ledgers"),
  createAccountingLedger: (data: unknown) => api.post("/payroll/accounting/ledgers", data),
  glMappings: () => api.get("/payroll/accounting/gl-mappings"),
  createGlMapping: (data: unknown) => api.post("/payroll/accounting/gl-mappings", data),
  generateAccountingJournal: (runId: number) => api.post(`/payroll/runs/${runId}/accounting-journal`),
  accountingJournals: (runId: number) => api.get(`/payroll/runs/${runId}/accounting-journals`),
  validateStatutoryFile: (data: unknown) => api.post("/payroll/statutory/file-validations", data),
  generateStatutoryTemplate: (templateType: string) => api.post(`/payroll/statutory/templates/${templateType}`),
  statutoryChallans: (params?: Record<string, unknown>) => api.get("/payroll/statutory/challans", { params }),
  generateStatutoryChallan: (data: unknown) => api.post("/payroll/statutory/challans/generate", data),
  statutoryReturnFiles: (params?: Record<string, unknown>) => api.get("/payroll/statutory/return-files", { params }),
  createStatutoryReturnFile: (data: unknown) => api.post("/payroll/statutory/return-files", data),
  taxCycles: () => api.get("/payroll/tax/cycles"),
  createTaxCycle: (data: unknown) => api.post("/payroll/tax/cycles", data),
  taxDeclarations: (params?: Record<string, unknown>) => api.get("/payroll/tax/declarations", { params }),
  createTaxDeclaration: (data: unknown) => api.post("/payroll/tax/declarations", data),
  submitTaxProof: (data: unknown) => api.post("/payroll/tax/proofs", data),
  verifyTaxProof: (id: number, data: unknown) => api.put(`/payroll/tax/proofs/${id}/verify`, data),
  taxProjection: (params: Record<string, unknown>) => api.get("/payroll/tax/projection", { params }),
  taxCompare: (params: Record<string, unknown>) => api.get("/payroll/tax/compare", { params }),
  reimbursements: (params?: Record<string, unknown>) =>
    api.get("/payroll/reimbursements", { params }),
  createReimbursement: (data: unknown) => api.post("/payroll/reimbursements", data),
  reviewReimbursement: (id: number, data: unknown) =>
    api.put(`/payroll/reimbursements/${id}/review`, data),
  reimbursementLedger: (id: number) => api.get(`/payroll/reimbursements/${id}/ledger`),
  loans: (params?: Record<string, unknown>) => api.get("/payroll/loans", { params }),
  createLoan: (data: unknown) => api.post("/payroll/loans", data),
  loanInstallments: (id: number) => api.get(`/payroll/loans/${id}/installments`),
  loanLedger: (id: number) => api.get(`/payroll/loans/${id}/ledger`),
  settlements: (params?: Record<string, unknown>) =>
    api.get("/payroll/settlements", { params }),
  createSettlement: (data: unknown) => api.post("/payroll/settlements", data),
  approveSettlement: (id: number, remarks?: string) =>
    api.put(`/payroll/settlements/${id}/approve`, null, { params: { remarks } }),
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
  escalate: (id: number, data: unknown) => api.put(`/helpdesk/tickets/${id}/escalate`, data),
  slaBreaches: () => api.get("/helpdesk/sla/breaches"),
  escalationRules: () => api.get("/helpdesk/escalation-rules"),
  createEscalationRule: (data: unknown) => api.post("/helpdesk/escalation-rules", data),
  knowledge: (params?: Record<string, unknown>) => api.get("/helpdesk/knowledge", { params }),
  createKnowledge: (data: unknown) => api.post("/helpdesk/knowledge", data),
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
  fieldCatalog: (params?: Record<string, unknown>) => api.get("/reports/field-catalog", { params }),
  definitions: (params?: Record<string, unknown>) => api.get("/reports/definitions", { params }),
  createDefinition: (data: unknown) => api.post("/reports/definitions", data),
  runDefinition: (id: number) => api.post(`/reports/definitions/${id}/run`),
};

export const timesheetsApi = {
  projects: (params?: Record<string, unknown>) =>
    api.get("/timesheets/projects", { params }),
  createProject: (data: unknown) => api.post("/timesheets/projects", data),
  list: (params?: Record<string, unknown>) =>
    api.get("/timesheets/", { params }),
  create: (data: unknown) => api.post("/timesheets/", data),
  addEntry: (timesheetId: number, data: unknown) =>
    api.post(`/timesheets/${timesheetId}/entries`, data),
  submit: (timesheetId: number) => api.put(`/timesheets/${timesheetId}/submit`),
  review: (timesheetId: number, data: unknown) =>
    api.put(`/timesheets/${timesheetId}/review`, data),
};

export const workflowApi = {
  inbox: (mine?: boolean) => api.get("/workflow/inbox", { params: { mine } }),
};

export const notificationsApi = {
  list: (params?: Record<string, unknown>) => api.get("/notifications/", { params }),
  unreadCount: () => api.get("/notifications/unread-count"),
  markRead: (id: number) => api.put(`/notifications/${id}/read`),
  markAllRead: () => api.put("/notifications/mark-all-read"),
  create: (data: unknown) => api.post("/notifications/", data),
};

export const whatsappEssApi = {
  configs: () => api.get("/whatsapp-ess/configs"),
  createConfig: (data: unknown) => api.post("/whatsapp-ess/configs", data),
  messages: () => api.get("/whatsapp-ess/messages"),
  inboundMessage: (data: unknown) => api.post("/whatsapp-ess/messages/inbound", data),
  templates: () => api.get("/whatsapp-ess/templates"),
  createTemplate: (data: unknown) => api.post("/whatsapp-ess/templates", data),
  upsertOptIn: (data: unknown) => api.post("/whatsapp-ess/opt-ins", data),
  outboundMessage: (data: unknown) => api.post("/whatsapp-ess/messages/outbound", data),
  deliveryCallback: (data: unknown) => api.post("/whatsapp-ess/delivery-callbacks", data),
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
  policyVersions: (policyId: number) => api.get(`/documents/policies/${policyId}/versions`),
  publishPolicyVersion: (policyId: number, data: unknown) =>
    api.post(`/documents/policies/${policyId}/versions`, data),
  generated: (employeeId?: number) =>
    api.get("/documents/generated", { params: { employee_id: employeeId } }),
  createGenerated: (data: unknown) => api.post("/documents/generated", data),
  certificates: (params?: Record<string, unknown>) =>
    api.get("/documents/certificates", { params }),
  uploadCertificate: (formData: FormData) =>
    api.post("/documents/certificates", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  verifyCertificate: (id: number, data: unknown) =>
    api.put(`/documents/certificates/${id}/verify`, data),
  importCertificates: (formData: FormData) =>
    api.post("/documents/certificates/imports", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  certificateBatches: (params?: Record<string, unknown>) =>
    api.get("/documents/certificates/import-export", { params }),
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
