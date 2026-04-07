import { Router } from 'express';
import {
  listContacts,
  getContact,
  createContact,
  updateContact,
  deleteContact,
} from '../controllers/contacts.controller';
import { authenticate } from '../middleware/auth.middleware';

export const contactsRouter = Router();
contactsRouter.use(authenticate);

contactsRouter.get('/', listContacts);
contactsRouter.get('/:id', getContact);
contactsRouter.post('/', createContact);
contactsRouter.put('/:id', updateContact);
contactsRouter.delete('/:id', deleteContact);
