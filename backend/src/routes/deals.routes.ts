import { Router } from 'express';
import {
  listDeals,
  getDeal,
  createDeal,
  updateDeal,
  deleteDeal,
} from '../controllers/deals.controller';
import { authenticate } from '../middleware/auth.middleware';

export const dealsRouter = Router();
dealsRouter.use(authenticate);

dealsRouter.get('/', listDeals);
dealsRouter.get('/:id', getDeal);
dealsRouter.post('/', createDeal);
dealsRouter.put('/:id', updateDeal);
dealsRouter.delete('/:id', deleteDeal);
