import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';

import { authRouter } from './routes/auth.routes';
import { contactsRouter } from './routes/contacts.routes';
import { dealsRouter } from './routes/deals.routes';
import { activitiesRouter } from './routes/activities.routes';
import { mindmapRouter } from './routes/mindmap.routes';
import { aiRouter } from './routes/ai.routes';
import { errorHandler } from './middleware/error.middleware';

const app = express();
const PORT = process.env.PORT ?? 3001;

// ─── Security & logging ───────────────────────────────────────────────────────
app.use(helmet());
app.use(cors({
  origin: process.env.CLIENT_ORIGIN
    ? process.env.CLIENT_ORIGIN.split(',')
    : 'http://localhost:5173',
  credentials: true,
}));
app.use(morgan('dev'));
app.use(
  rateLimit({
    windowMs: 15 * 60 * 1000, // 15 min
    max: 300,
    standardHeaders: true,
    legacyHeaders: false,
  }),
);

// ─── Body parsing ─────────────────────────────────────────────────────────────
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));

// ─── Health check ─────────────────────────────────────────────────────────────
app.get('/health', (_req, res) => res.json({ status: 'ok' }));

// ─── API routes ───────────────────────────────────────────────────────────────
const api = express.Router();
api.use('/auth', authRouter);
api.use('/contacts', contactsRouter);
api.use('/deals', dealsRouter);
api.use('/activities', activitiesRouter);
api.use('/mindmap', mindmapRouter);
api.use('/ai', aiRouter);
app.use('/api', api);

// ─── Error handling ───────────────────────────────────────────────────────────
app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`🚀 API running on http://localhost:${PORT}`);
});

export default app;
