import { useAuthStore } from '@/store/auth.store';
import { useContacts } from '@/hooks/useContacts';
import { useDeals } from '@/hooks/useDeals';
import Card from '@/components/common/Card';
import { Users, Briefcase, TrendingUp } from 'lucide-react';

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const { data: contacts } = useContacts();
  const { data: deals } = useDeals();

  const totalValue = deals?.reduce((s, d) => s + d.value, 0) ?? 0;
  const openDeals = deals?.filter((d) => !['CLOSED_WON', 'CLOSED_LOST'].includes(d.stage)).length ?? 0;

  const stats = [
    { label: 'Contacts', value: contacts?.length ?? 0, icon: Users, color: 'text-blue-600 bg-blue-50' },
    { label: 'Open Deals', value: openDeals, icon: Briefcase, color: 'text-indigo-600 bg-indigo-50' },
    {
      label: 'Pipeline Value',
      value: `$${totalValue.toLocaleString()}`,
      icon: TrendingUp,
      color: 'text-green-600 bg-green-50',
    },
  ];

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">
        Welcome back, {user?.name} 👋
      </h1>
      <p className="text-gray-500 mb-6">Here's what's happening today.</p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <Card key={label} className="p-5 flex items-center gap-4">
            <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>
              <Icon size={22} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{value}</p>
              <p className="text-sm text-gray-500">{label}</p>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-5">
          <h2 className="font-semibold text-gray-900 mb-3">Recent Contacts</h2>
          {contacts?.slice(0, 5).map((c) => (
            <div key={c.id} className="flex items-center gap-2 py-2 border-b last:border-0">
              <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-xs font-bold">
                {c.firstName[0]}{c.lastName[0]}
              </div>
              <div>
                <p className="text-sm font-medium">{c.firstName} {c.lastName}</p>
                <p className="text-xs text-gray-500">{c.company ?? '—'}</p>
              </div>
            </div>
          ))}
          {!contacts?.length && <p className="text-sm text-gray-400">No contacts yet.</p>}
        </Card>

        <Card className="p-5">
          <h2 className="font-semibold text-gray-900 mb-3">Recent Deals</h2>
          {deals?.slice(0, 5).map((d) => (
            <div key={d.id} className="flex items-center justify-between py-2 border-b last:border-0">
              <div>
                <p className="text-sm font-medium">{d.title}</p>
                <p className="text-xs text-gray-500">{d.stage.replace('_', ' ')}</p>
              </div>
              <span className="text-sm font-semibold text-gray-900">
                ${d.value.toLocaleString()}
              </span>
            </div>
          ))}
          {!deals?.length && <p className="text-sm text-gray-400">No deals yet.</p>}
        </Card>
      </div>
    </div>
  );
}
