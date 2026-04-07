import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import type { Activity, ApiResponse } from '@/types';
import Spinner from '@/components/common/Spinner';
import Card from '@/components/common/Card';
import { CheckCircle2, Circle } from 'lucide-react';

export default function ActivitiesPage() {
  const { data: activities, isLoading } = useQuery({
    queryKey: ['activities'],
    queryFn: () =>
      api.get<ApiResponse<Activity[]>>('/activities').then((r) => r.data.data),
  });

  if (isLoading) return <div className="p-6 flex justify-center"><Spinner /></div>;

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Activities</h1>
      <div className="space-y-3">
        {activities?.map((a) => (
          <Card key={a.id} className="p-4 flex items-start gap-3">
            {a.done ? (
              <CheckCircle2 size={20} className="text-green-500 mt-0.5 flex-shrink-0" />
            ) : (
              <Circle size={20} className="text-gray-400 mt-0.5 flex-shrink-0" />
            )}
            <div className="flex-1 min-w-0">
              <p className={`text-sm font-medium ${a.done ? 'line-through text-gray-400' : 'text-gray-900'}`}>
                {a.subject}
              </p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">
                  {a.type}
                </span>
                {a.contact && (
                  <span className="text-xs text-gray-500">
                    {a.contact.firstName} {a.contact.lastName}
                  </span>
                )}
                {a.dueDate && (
                  <span className="text-xs text-gray-400">
                    {new Date(a.dueDate).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          </Card>
        ))}
        {!activities?.length && (
          <p className="text-gray-400 text-sm">No activities yet.</p>
        )}
      </div>
    </div>
  );
}
