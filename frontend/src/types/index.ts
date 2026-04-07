export type Role = 'ADMIN' | 'MEMBER';

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  createdAt: string;
}

export type DealStage =
  | 'LEAD'
  | 'QUALIFIED'
  | 'PROPOSAL'
  | 'NEGOTIATION'
  | 'CLOSED_WON'
  | 'CLOSED_LOST';

export type ActivityType = 'CALL' | 'EMAIL' | 'MEETING' | 'TASK' | 'NOTE';

export interface Contact {
  id: string;
  firstName: string;
  lastName: string;
  email?: string;
  phone?: string;
  company?: string;
  jobTitle?: string;
  notes?: string;
  tags: string[];
  score: number;
  ownerId: string;
  createdAt: string;
  updatedAt: string;
}

export interface Deal {
  id: string;
  title: string;
  value: number;
  currency: string;
  stage: DealStage;
  probability: number;
  closeDate?: string;
  notes?: string;
  ownerId: string;
  contactId: string;
  contact?: Pick<Contact, 'id' | 'firstName' | 'lastName'>;
  createdAt: string;
  updatedAt: string;
}

export interface Activity {
  id: string;
  type: ActivityType;
  subject: string;
  notes?: string;
  dueDate?: string;
  done: boolean;
  ownerId: string;
  contactId?: string;
  dealId?: string;
  contact?: Pick<Contact, 'id' | 'firstName' | 'lastName'>;
  deal?: Pick<Deal, 'id' | 'title'>;
  createdAt: string;
  updatedAt: string;
}

export interface MindMapData {
  id: string;
  label: string;
  type: 'root' | 'deals' | 'activities' | 'tags' | 'leaf';
  children?: MindMapData[];
}

export interface MindMap {
  id: string;
  title: string;
  data: MindMapData;
  createdAt: string;
  updatedAt: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}
