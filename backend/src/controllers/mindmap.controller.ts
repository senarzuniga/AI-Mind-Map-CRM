import { Response, NextFunction } from 'express';
import { prisma } from '../utils/prisma';
import { AuthRequest } from '../middleware/auth.middleware';
import { createError } from '../middleware/error.middleware';

export async function listMindMaps(
  _req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const maps = await prisma.mindMap.findMany({ orderBy: { updatedAt: 'desc' } });
    res.json({ success: true, data: maps });
  } catch (err) {
    next(err);
  }
}

export async function getMindMap(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const map = await prisma.mindMap.findUnique({ where: { id: req.params.id } });
    if (!map) return next(createError('Mind map not found', 404));
    res.json({ success: true, data: map });
  } catch (err) {
    next(err);
  }
}

export async function createMindMap(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const map = await prisma.mindMap.create({ data: req.body });
    res.status(201).json({ success: true, data: map });
  } catch (err) {
    next(err);
  }
}

export async function updateMindMap(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const existing = await prisma.mindMap.findUnique({ where: { id: req.params.id } });
    if (!existing) return next(createError('Mind map not found', 404));

    const map = await prisma.mindMap.update({ where: { id: req.params.id }, data: req.body });
    res.json({ success: true, data: map });
  } catch (err) {
    next(err);
  }
}

export async function deleteMindMap(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const existing = await prisma.mindMap.findUnique({ where: { id: req.params.id } });
    if (!existing) return next(createError('Mind map not found', 404));

    await prisma.mindMap.delete({ where: { id: req.params.id } });
    res.json({ success: true, message: 'Mind map deleted' });
  } catch (err) {
    next(err);
  }
}

export async function generateMindMap(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const { aiService } = await import('../services/ai/ai.service');
    const { contactId } = req.body as { contactId: string };

    const contact = await prisma.contact.findFirst({
      where: { id: contactId, ownerId: req.userId },
      include: { deals: true, activities: { take: 10, orderBy: { createdAt: 'desc' } } },
    });
    if (!contact) return next(createError('Contact not found', 404));

    const mapData = await aiService.generateMindMapData(contact);
    const map = await prisma.mindMap.create({
      data: { title: `${contact.firstName} ${contact.lastName}`, data: mapData },
    });
    res.status(201).json({ success: true, data: map });
  } catch (err) {
    next(err);
  }
}
