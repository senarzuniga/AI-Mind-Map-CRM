import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { dealsService } from '@/services/deals.service';
import type { Deal } from '@/types';

export function useDeals() {
  return useQuery({ queryKey: ['deals'], queryFn: dealsService.list });
}

export function useDeal(id: string) {
  return useQuery({ queryKey: ['deals', id], queryFn: () => dealsService.get(id) });
}

export function useCreateDeal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Deal>) => dealsService.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['deals'] }),
  });
}

export function useUpdateDeal(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Deal>) => dealsService.update(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['deals'] });
      qc.invalidateQueries({ queryKey: ['deals', id] });
    },
  });
}

export function useDeleteDeal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => dealsService.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['deals'] }),
  });
}
