/**
 * KaryaFlow - Project Management Types
 * Complete TypeScript interfaces for all project management entities
 */

// ============= ENUMS & LITERALS =============
export type ProjectStatus = "Draft" | "Planned" | "Active" | "On Hold" | "Completed" | "Cancelled" | "Archived";
export type ProjectPriority = "Low" | "Medium" | "High" | "Critical";
export type ProjectHealth = "Good" | "At Risk" | "Critical" | "Blocked";

export type TaskStatus = "Backlog" | "To Do" | "In Progress" | "In Review" | "Blocked" | "Done" | "Cancelled";
export type TaskPriority = "Low" | "Medium" | "High" | "Urgent";

export type MilestoneStatus = "Not Started" | "In Progress" | "At Risk" | "Completed" | "Delayed" | "Cancelled";
export type ApprovalStatus = "Not Required" | "Pending" | "Approved" | "Rejected";

export type FileVisibility = "Internal" | "Project Team" | "Client Visible" | "Private";
export type TimeApprovalStatus = "Pending" | "Approved" | "Rejected";

// ============= CLIENT TYPES =============
export interface PMSClient {
  id: number;
  organization_id?: number;
  name: string;
  company_name?: string;
  email?: string;
  phone?: string;
  website?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateClientInput {
  name: string;
  company_name?: string;
  email?: string;
  phone?: string;
  website?: string;
  notes?: string;
}

// ============= PROJECT TYPES =============
export interface PMSProject {
  id: number;
  organization_id?: number;
  name: string;
  project_key: string;
  description?: string;
  client_id?: number;
  manager_user_id?: number;
  status: ProjectStatus;
  priority: ProjectPriority;
  health: ProjectHealth;
  start_date?: string;
  due_date?: string;
  completed_at?: string;
  budget_amount?: number;
  actual_cost?: number;
  progress_percent: number;
  is_client_visible: boolean;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectInput {
  name: string;
  project_key: string;
  description?: string;
  client_id?: number;
  manager_user_id?: number;
  status?: ProjectStatus;
  priority?: ProjectPriority;
  start_date?: string;
  due_date?: string;
  budget_amount?: number;
}

// ============= TASK TYPES =============
export interface PMSChecklistItem {
  id: number;
  task_id: number;
  title: string;
  is_completed: boolean;
  position: number;
  created_at: string;
  updated_at: string;
}

export interface CreateChecklistItemInput {
  title: string;
  is_completed?: boolean;
}

export interface PMSTask {
  id: number;
  project_id: number;
  board_id?: number;
  column_id?: number;
  milestone_id?: number;
  sprint_id?: number;
  epic_id?: number;
  component_id?: number;
  release_id?: number;
  parent_task_id?: number;
  title: string;
  description?: string;
  task_key: string;
  work_type: "Epic" | "Story" | "Task" | "Bug" | "Sub-task" | string;
  epic_key?: string;
  initiative?: string;
  component?: string;
  severity?: "S1" | "S2" | "S3" | "S4" | string;
  environment?: string;
  affected_version?: string;
  fix_version?: string;
  release_name?: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignee_user_id?: number;
  reporter_user_id?: number;
  start_date?: string;
  due_date?: string;
  completed_at?: string;
  estimated_hours?: number;
  actual_hours?: number;
  original_estimate_hours?: number;
  remaining_estimate_hours?: number;
  story_points?: number;
  rank?: number;
  security_level: "Internal" | "Client Visible" | "Private" | string;
  development_branch?: string;
  development_commits: number;
  development_prs: number;
  development_deployments: number;
  development_build: "Passing" | "Failing" | "Pending" | string;
  position: number;
  is_client_visible: boolean;
  is_blocking: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskInput {
  title: string;
  description?: string;
  task_key: string;
  work_type?: "Epic" | "Story" | "Task" | "Bug" | "Sub-task" | string;
  epic_key?: string;
  initiative?: string;
  component?: string;
  severity?: "S1" | "S2" | "S3" | "S4" | string;
  environment?: string;
  affected_version?: string;
  fix_version?: string;
  release_name?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  assignee_user_id?: number;
  reporter_user_id?: number;
  epic_id?: number;
  component_id?: number;
  release_id?: number;
  start_date?: string;
  due_date?: string;
  estimated_hours?: number;
  original_estimate_hours?: number;
  remaining_estimate_hours?: number;
  story_points?: number;
  rank?: number;
  security_level?: "Internal" | "Client Visible" | "Private" | string;
  development_branch?: string;
  development_commits?: number;
  development_prs?: number;
  development_deployments?: number;
  development_build?: "Passing" | "Failing" | "Pending" | string;
  is_client_visible?: boolean;
}

// ============= KANBAN TYPES =============
export interface PMSBoardColumn {
  id: number;
  board_id: number;
  name: string;
  status_key: string;
  position: number;
  wip_limit?: number;
  is_collapsed: boolean;
  color?: string;
  tasks?: PMSTask[];
  task_count: number;
}

export interface PMSBoard {
  id: number;
  project_id: number;
  name: string;
  board_type: string; // "Kanban", "Scrum", etc.
  created_at: string;
  columns?: PMSBoardColumn[];
}

export interface TaskReorderPayload {
  task_id: number;
  column_id: number;
  position: number;
}

// ============= MILESTONE TYPES =============
export interface PMSMilestone {
  id: number;
  project_id: number;
  name: string;
  description?: string;
  status: MilestoneStatus;
  owner_user_id?: number;
  start_date?: string;
  due_date?: string;
  completed_at?: string;
  progress_percent: number;
  client_approval_status: ApprovalStatus;
  client_approved_at?: string;
  client_rejected_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateMilestoneInput {
  name: string;
  description?: string;
  status?: MilestoneStatus;
  owner_user_id?: number;
  start_date?: string;
  due_date?: string;
  progress_percent?: number;
}

// ============= COMMENT TYPES (COLLABORATION) =============
export interface PMSComment {
  id: number;
  author_user_id?: number;
  project_id?: number;
  task_id?: number;
  milestone_id?: number;
  parent_comment_id?: number;
  body: string;
  is_internal: boolean;
  is_edited: boolean;
  created_at: string;
  updated_at: string;
  author?: {
    id: number;
    name: string;
    avatar_url?: string;
  };
}

export interface CreateCommentInput {
  body: string;
  is_internal?: boolean;
  parent_comment_id?: number;
}

// ============= FILE TYPES =============
export interface PMSFileAsset {
  id: number;
  uploaded_by_user_id?: number;
  project_id?: number;
  task_id?: number;
  milestone_id?: number;
  file_name: string;
  original_name: string;
  mime_type?: string;
  size_bytes: number;
  storage_path: string;
  version_number: number;
  visibility: FileVisibility;
  created_at: string;
  updated_at: string;
}

export interface CreateFileAssetInput {
  file_name: string;
  original_name: string;
  mime_type?: string;
  size_bytes: number;
  storage_path: string;
  visibility?: FileVisibility;
}

// ============= TIME LOG TYPES =============
export interface PMSTimeLog {
  id: number;
  user_id: number;
  project_id: number;
  task_id?: number;
  log_date: string;
  start_time?: string;
  end_time?: string;
  duration_minutes: number;
  description?: string;
  is_billable: boolean;
  approval_status: TimeApprovalStatus;
  approved_by_user_id?: number;
  approved_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTimeLogInput {
  project_id: number;
  task_id?: number;
  log_date: string;
  duration_minutes: number;
  description?: string;
  is_billable?: boolean;
}

// ============= TAG TYPES =============
export interface PMSTag {
  id: number;
  organization_id?: number;
  name: string;
  color?: string;
  created_at: string;
}

// ============= SPRINT TYPES =============
export interface PMSSprint {
  id: number;
  project_id: number;
  name: string;
  goal?: string;
  status: "Planned" | "Active" | "Completed" | "Cancelled";
  start_date: string;
  end_date: string;
  capacity_hours?: number;
  velocity_points?: number;
  committed_task_count: number;
  committed_story_points: number;
  completed_story_points: number;
  scope_change_count: number;
  carry_forward_task_count: number;
  started_at?: string;
  completed_at?: string;
  commitment_snapshot?: string;
  completion_summary?: string;
  created_at: string;
  updated_at: string;
}

// ============= PROJECT MEMBER TYPES =============
export interface PMSProjectMember {
  id: number;
  project_id: number;
  user_id: number;
  role: "Manager" | "Lead" | "Member" | "Viewer" | "Client";
  created_at: string;
}

// ============= PLANNING OBJECT TYPES =============
export interface PMSEpic {
  id: number;
  project_id: number;
  epic_key: string;
  name: string;
  description?: string;
  status: string;
  owner_user_id?: number;
  color?: string;
  start_date?: string;
  target_date?: string;
  created_at: string;
  updated_at?: string;
}

export interface PMSComponent {
  id: number;
  project_id: number;
  name: string;
  description?: string;
  lead_user_id?: number;
  default_assignee_user_id?: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface PMSRelease {
  id: number;
  project_id: number;
  name: string;
  description?: string;
  status: string;
  release_date?: string;
  owner_user_id?: number;
  readiness_percent: number;
  launch_notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface PMSTaskDependency {
  id: number;
  task_id: number;
  depends_on_task_id: number;
  dependency_type: string;
  created_at: string;
  task_key?: string;
  depends_on_task_key?: string;
  task_title?: string;
  depends_on_task_title?: string;
}

export interface PMSSavedFilter {
  id: number;
  project_id: number;
  user_id?: number;
  name: string;
  view_type: string;
  query: string;
  is_shared: boolean;
  created_at: string;
  updated_at?: string;
}

export interface PMSActivity {
  id: number;
  project_id: number;
  task_id?: number;
  sprint_id?: number;
  actor_user_id?: number;
  action: string;
  entity_type: string;
  entity_id?: number;
  summary: string;
  metadata_json?: string;
  created_at: string;
}

export interface SprintBurndown {
  sprint_id: number;
  committed_story_points: number;
  completed_story_points: number;
  remaining_story_points: number;
  points: Array<{
    date: string;
    ideal_remaining_points: number;
    actual_remaining_points: number;
    completed_points: number;
  }>;
}

export interface ProjectVelocity {
  project_id: number;
  average_velocity_points: number;
  sprints: Array<{ id: number; name: string; end_date: string; velocity_points: number }>;
}

export interface ReleaseReadiness {
  release_id: number;
  release_name: string;
  readiness_percent: number;
  health: string;
  total_tasks: number;
  done_tasks: number;
  open_blockers: number;
  overdue_tasks: number;
  severity_counts: Record<string, number>;
}

export interface WorkloadResponse {
  project_id: number;
  group_by: string;
  items: Array<{
    user_id?: number;
    sprint_id?: number;
    task_count: number;
    story_points: number;
    estimated_hours: number;
    overdue_tasks: number;
    capacity_hours?: number;
    load_percent?: number;
  }>;
}

// ============= DASHBOARD TYPES =============
export interface ProjectMetrics {
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  overdue_projects: number;
  total_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  pending_approvals: number;
  team_utilization: number;
  hours_logged_this_week: number;
  upcoming_milestones: number;
  recent_activities: number;
}

export interface DashboardData {
  project: PMSProject;
  metrics: ProjectMetrics;
}

// ============= API RESPONSE TYPES =============
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

// ============= FILTER & SORT TYPES =============
export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  assignee_id?: number;
  milestone_id?: number;
  sprint_id?: number;
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
  tags?: number[];
}

export interface ProjectFilters {
  status?: ProjectStatus;
  priority?: ProjectPriority;
  client_id?: number;
  manager_id?: number;
}

export interface SortOption {
  field: string;
  direction: "asc" | "desc";
}

