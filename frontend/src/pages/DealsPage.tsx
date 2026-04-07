import { useDeals } from '@/hooks/useDeals';
import DealCard from '@/components/crm/DealCard';
import Spinner from '@/components/common/Spinner';
import type { DealStage } from '@/types';

const STAGES: DealStage[] = ['LEAD', 'QUALIFIED', 'PROPOSAL', 'NEGOTIATION', 'CLOSED_WON', 'CLOSED_LOST'];

export default function DealsPage() {
  const { data: deals, isLoading } = useDeals();

  if (isLoading) return <div className="p-6 flex justify-center"><Spinner /></div>;

  return (
    <div className="p-6 overflow-x-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Deals Pipeline</h1>
      <div className="flex gap-4 min-w-max">
        {STAGES.map((stage) => {
          const stageDeals = deals?.filter((d) => d.stage === stage) ?? [];
          return (
            <div key={stage} className="w-64">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  {stage.replace('_', ' ')}
                </h2>
                <span className="text-xs bg-gray-100 text-gray-500 rounded-full px-2 py-0.5">
                  {stageDeals.length}
                </span>
              </div>
              <div className="space-y-3">
                {stageDeals.map((d) => <DealCard key={d.id} deal={d} />)}
                {stageDeals.length === 0 && (
                  <div className="h-20 border-2 border-dashed border-gray-200 rounded-xl flex items-center justify-center">
                    <p className="text-xs text-gray-400">No deals</p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
