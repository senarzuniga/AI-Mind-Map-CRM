import { Router } from 'express';
import {
  listMindMaps,
  getMindMap,
  createMindMap,
  updateMindMap,
  deleteMindMap,
  generateMindMap,
} from '../controllers/mindmap.controller';
import { authenticate } from '../middleware/auth.middleware';

export const mindmapRouter = Router();
mindmapRouter.use(authenticate);

mindmapRouter.get('/', listMindMaps);
mindmapRouter.get('/:id', getMindMap);
mindmapRouter.post('/', createMindMap);
mindmapRouter.post('/generate', generateMindMap);
mindmapRouter.put('/:id', updateMindMap);
mindmapRouter.delete('/:id', deleteMindMap);
