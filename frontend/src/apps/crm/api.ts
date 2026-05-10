import { api } from "@/services/api";

export type CRMApiRecord = Record<string, string | number | boolean | null | undefined>;

export type CRMListParams = {
  page?: number;
  per_page?: number;
  search?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
  owner_id?: number;
  [key: string]: string | number | boolean | undefined;
};

export type CRMPaginatedResponse<T = CRMApiRecord> = {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
};

export const crmApi = {
  moduleInfo: () => api.get("/crm/module-info"),
  list: <T = CRMApiRecord>(entity: string, params?: CRMListParams) =>
    api.get<CRMPaginatedResponse<T>>(`/crm/${entity}`, { params }),
  get: <T = CRMApiRecord>(entity: string, id: number) => api.get<T>(`/crm/${entity}/${id}`),
  create: <T = CRMApiRecord>(entity: string, data: CRMApiRecord) => api.post<T>(`/crm/${entity}`, data),
  update: <T = CRMApiRecord>(entity: string, id: number, data: CRMApiRecord) =>
    api.patch<T>(`/crm/${entity}/${id}`, data),
  delete: (entity: string, id: number) => api.delete(`/crm/${entity}/${id}`),
};
