import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import type { MindMap, ApiResponse } from '@/types';
import MindMapViewer from '@/components/mindmap/MindMapViewer';
import Spinner from '@/components/common/Spinner';

export default function MindMapPage() {
  const { id } = useParams<{ id?: string }>();

  const { data: maps, isLoading: loadingList } = useQuery({
    queryKey: ['mindmaps'],
    queryFn: () => api.get<ApiResponse<MindMap[]>>('/mindmap').then((r) => r.data.data),
    enabled: !id,
  });

  const { data: map, isLoading: loadingMap } = useQuery({
    queryKey: ['mindmaps', id],
    queryFn: () => api.get<ApiResponse<MindMap>>(`/mindmap/${id}`).then((r) => r.data.data),
    enabled: !!id,
  });

  if (loadingList || loadingMap) {
    return <div className="p-6 flex justify-center"><Spinner /></div>;
  }

  if (map) {
    return (
      <div className="h-full flex flex-col">
        <div className="p-4 border-b bg-white">
          <h1 className="font-bold text-gray-900">{map.title}</h1>
        </div>
        <div className="flex-1">
          <MindMapViewer data={map.data} />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Mind Maps</h1>
      {maps?.length === 0 && (
        <p className="text-gray-400">No mind maps yet. Generate one from a contact page.</p>
      )}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {maps?.map((m) => (
          <a
            key={m.id}
            href={`/mindmap/${m.id}`}
            className="block p-4 bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
          >
            <p className="font-semibold text-gray-900">{m.title}</p>
            <p className="text-xs text-gray-400 mt-1">
              {new Date(m.updatedAt).toLocaleDateString()}
            </p>
          </a>
        ))}
      </div>
    </div>
  );
}
