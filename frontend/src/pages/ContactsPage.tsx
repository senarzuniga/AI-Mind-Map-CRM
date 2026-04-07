import { useContacts } from '@/hooks/useContacts';
import ContactCard from '@/components/crm/ContactCard';
import Spinner from '@/components/common/Spinner';

export default function ContactsPage() {
  const { data: contacts, isLoading } = useContacts();

  if (isLoading) {
    return (
      <div className="p-6 flex justify-center">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Contacts</h1>
      </div>

      {contacts?.length === 0 && (
        <p className="text-gray-500">No contacts yet. Add your first contact via the API.</p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {contacts?.map((c) => <ContactCard key={c.id} contact={c} />)}
      </div>
    </div>
  );
}
