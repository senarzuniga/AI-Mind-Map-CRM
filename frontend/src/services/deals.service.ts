import { api } from './api';
import type { Deal, ApiResponse } from '@/types';

export const dealsService = {
  list: () => api.get<ApiResponse<Deal[]>>('/deals').then((r) => r.data.data),
  get: (id: string) => api.get<ApiResponse<Deal>>(`/deals/${id}`).then((r) => r.data.data),
  create: (data: Partial<Deal>) =>
    api.post<ApiResponse<Deal>>('/deals', data).then((r) => r.data.data),
  update: (id: string, data: Partial<Deal>) =>
    api.put<ApiResponse<Deal>>(`/deals/${id}`, data).then((r) => r.data.data),
  remove: (id: string) => api.delete(`/deals/${id}`),
};
