import type { Deal, DealStage } from '@/types';
import Card from '@/components/common/Card';

const stageColors: Record<DealStage, string> = {
  LEAD: 'bg-gray-100 text-gray-700',
  QUALIFIED: 'bg-blue-100 text-blue-700',
  PROPOSAL: 'bg-yellow-100 text-yellow-700',
  NEGOTIATION: 'bg-orange-100 text-orange-700',
  CLOSED_WON: 'bg-green-100 text-green-700',
  CLOSED_LOST: 'bg-red-100 text-red-700',
};

interface Props {
  deal: Deal;
}

export default function DealCard({ deal }: Props) {
  const contactName = deal.contact
    ? `${deal.contact.firstName} ${deal.contact.lastName}`
    : '—';

  return (
    <Card className="p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="font-semibold text-gray-900 truncate">{deal.title}</p>
          <p className="text-xs text-gray-500 truncate">{contactName}</p>
        </div>
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium whitespace-nowrap ${stageColors[deal.stage]}`}
        >
          {deal.stage.replace('_', ' ')}
        </span>
      </div>
      <div className="mt-3 flex items-center justify-between text-sm">
        <span className="font-bold text-gray-900">
          {deal.currency} {deal.value.toLocaleString()}
        </span>
        <span className="text-gray-500">{deal.probability}% likely</span>
      </div>
    </Card>
  );
}
