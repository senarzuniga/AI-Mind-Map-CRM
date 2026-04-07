import { Router } from 'express';
import {
  listActivities,
  createActivity,
  updateActivity,
  deleteActivity,
} from '../controllers/activities.controller';
import { authenticate } from '../middleware/auth.middleware';

export const activitiesRouter = Router();
activitiesRouter.use(authenticate);

activitiesRouter.get('/', listActivities);
activitiesRouter.post('/', createActivity);
activitiesRouter.put('/:id', updateActivity);
activitiesRouter.delete('/:id', deleteActivity);
