import type { Contact } from '@/types';
import Card from '@/components/common/Card';
import { useNavigate } from 'react-router-dom';
import { Mail, Phone, Building2 } from 'lucide-react';

interface Props {
  contact: Contact;
}

export default function ContactCard({ contact }: Props) {
  const navigate = useNavigate();
  const fullName = `${contact.firstName} ${contact.lastName}`;
  const initials = `${contact.firstName[0]}${contact.lastName[0]}`.toUpperCase();

  return (
    <Card
      className="p-4 cursor-pointer hover:shadow-md transition-shadow"
      onClick={() => navigate(`/contacts/${contact.id}`)}
    >
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm flex-shrink-0">
          {initials}
        </div>
        <div className="min-w-0 flex-1">
          <p className="font-semibold text-gray-900 truncate">{fullName}</p>
          {contact.jobTitle && (
            <p className="text-xs text-gray-500 truncate">{contact.jobTitle}</p>
          )}
          <div className="mt-2 space-y-1">
            {contact.email && (
              <p className="flex items-center gap-1 text-xs text-gray-600 truncate">
                <Mail size={12} /> {contact.email}
              </p>
            )}
            {contact.phone && (
              <p className="flex items-center gap-1 text-xs text-gray-600">
                <Phone size={12} /> {contact.phone}
              </p>
            )}
            {contact.company && (
              <p className="flex items-center gap-1 text-xs text-gray-600 truncate">
                <Building2 size={12} /> {contact.company}
              </p>
            )}
          </div>
          {contact.tags.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {contact.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-full text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="text-right">
          <span
            className={`text-sm font-bold ${
              contact.score >= 70
                ? 'text-green-600'
                : contact.score >= 40
                ? 'text-yellow-600'
                : 'text-red-500'
            }`}
          >
            {contact.score}
          </span>
          <p className="text-xs text-gray-400">score</p>
        </div>
      </div>
    </Card>
  );
}
