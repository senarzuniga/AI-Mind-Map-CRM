import { Router } from 'express';
import {
  summarizeContact,
  suggestNextActions,
  scoreRelationship,
} from '../controllers/ai.controller';
import { authenticate } from '../middleware/auth.middleware';

export const aiRouter = Router();
aiRouter.use(authenticate);

aiRouter.get('/contacts/:contactId/summary', summarizeContact);
aiRouter.get('/contacts/:contactId/score', scoreRelationship);
aiRouter.get('/deals/:dealId/actions', suggestNextActions);
