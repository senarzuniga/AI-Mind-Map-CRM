import { Response, NextFunction } from 'express';
import { AuthRequest } from '../middleware/auth.middleware';
import { aiService } from '../services/ai/ai.service';
import { prisma } from '../utils/prisma';
import { createError } from '../middleware/error.middleware';

export async function summarizeContact(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const contact = await prisma.contact.findFirst({
      where: { id: req.params.contactId, ownerId: req.userId },
      include: { deals: true, activities: { take: 20, orderBy: { createdAt: 'desc' } } },
    });
    if (!contact) return next(createError('Contact not found', 404));

    const summary = await aiService.summarizeContact(contact);
    res.json({ success: true, data: { summary } });
  } catch (err) {
    next(err);
  }
}

export async function suggestNextActions(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const deal = await prisma.deal.findFirst({
      where: { id: req.params.dealId, ownerId: req.userId },
      include: {
        contact: true,
        activities: { take: 10, orderBy: { createdAt: 'desc' } },
      },
    });
    if (!deal) return next(createError('Deal not found', 404));

    const actions = await aiService.suggestNextActions(deal);
    res.json({ success: true, data: { actions } });
  } catch (err) {
    next(err);
  }
}

export async function scoreRelationship(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const contact = await prisma.contact.findFirst({
      where: { id: req.params.contactId, ownerId: req.userId },
      include: { deals: true, activities: true },
    });
    if (!contact) return next(createError('Contact not found', 404));

    const score = await aiService.scoreRelationship(contact);

    await prisma.contact.update({ where: { id: contact.id }, data: { score } });
    res.json({ success: true, data: { score } });
  } catch (err) {
    next(err);
  }
}
