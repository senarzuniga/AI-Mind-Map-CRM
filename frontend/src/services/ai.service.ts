import { api } from './api';
import type { ApiResponse } from '@/types';

export const aiService = {
  summarizeContact: (contactId: string) =>
    api
      .get<ApiResponse<{ summary: string }>>(`/ai/contacts/${contactId}/summary`)
      .then((r) => r.data.data.summary),

  scoreContact: (contactId: string) =>
    api
      .get<ApiResponse<{ score: number }>>(`/ai/contacts/${contactId}/score`)
      .then((r) => r.data.data.score),

  suggestDealActions: (dealId: string) =>
    api
      .get<ApiResponse<{ actions: string[] }>>(`/ai/deals/${dealId}/actions`)
      .then((r) => r.data.data.actions),
};
