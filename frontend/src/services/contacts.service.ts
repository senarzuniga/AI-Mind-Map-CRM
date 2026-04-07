import { api } from './api';
import type { Contact, ApiResponse } from '@/types';

export const contactsService = {
  list: () => api.get<ApiResponse<Contact[]>>('/contacts').then((r) => r.data.data),
  get: (id: string) => api.get<ApiResponse<Contact>>(`/contacts/${id}`).then((r) => r.data.data),
  create: (data: Partial<Contact>) =>
    api.post<ApiResponse<Contact>>('/contacts', data).then((r) => r.data.data),
  update: (id: string, data: Partial<Contact>) =>
    api.put<ApiResponse<Contact>>(`/contacts/${id}`, data).then((r) => r.data.data),
  remove: (id: string) => api.delete(`/contacts/${id}`),
};
