import { useParams, useNavigate } from 'react-router-dom';
import { useContact } from '@/hooks/useContacts';
import { aiService } from '@/services/ai.service';
import Spinner from '@/components/common/Spinner';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';
import { useState } from 'react';
import { ArrowLeft, Sparkles } from 'lucide-react';

export default function ContactDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: contact, isLoading } = useContact(id!);
  const [summary, setSummary] = useState('');
  const [loadingSummary, setLoadingSummary] = useState(false);

  async function handleSummarize() {
    setLoadingSummary(true);
    try {
      const text = await aiService.summarizeContact(id!);
      setSummary(text);
    } finally {
      setLoadingSummary(false);
    }
  }

  if (isLoading) return <div className="p-6 flex justify-center"><Spinner /></div>;
  if (!contact) return <div className="p-6 text-gray-500">Contact not found.</div>;

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4"
      >
        <ArrowLeft size={16} /> Back
      </button>

      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {contact.firstName} {contact.lastName}
          </h1>
          {contact.jobTitle && (
            <p className="text-gray-500">
              {contact.jobTitle}{contact.company ? ` @ ${contact.company}` : ''}
            </p>
          )}
        </div>
        <Button onClick={handleSummarize} disabled={loadingSummary} size="sm">
          <Sparkles size={14} />
          {loadingSummary ? 'Analyzing…' : 'AI Summary'}
        </Button>
      </div>

      {summary && (
        <Card className="p-4 mb-6 bg-indigo-50 border-indigo-200">
          <p className="text-sm text-indigo-900">{summary}</p>
        </Card>
      )}

      <div className="grid grid-cols-2 gap-4 mb-6">
        {contact.email && (
          <Card className="p-4">
            <p className="text-xs text-gray-400 mb-1">Email</p>
            <p className="text-sm font-medium">{contact.email}</p>
          </Card>
        )}
        {contact.phone && (
          <Card className="p-4">
            <p className="text-xs text-gray-400 mb-1">Phone</p>
            <p className="text-sm font-medium">{contact.phone}</p>
          </Card>
        )}
      </div>

      {contact.notes && (
        <Card className="p-4 mb-6">
          <p className="text-xs text-gray-400 mb-1">Notes</p>
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{contact.notes}</p>
        </Card>
      )}
    </div>
  );
}
