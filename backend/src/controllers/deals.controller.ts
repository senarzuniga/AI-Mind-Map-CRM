import { Response, NextFunction } from 'express';
import { prisma } from '../utils/prisma';
import { AuthRequest } from '../middleware/auth.middleware';
import { createError } from '../middleware/error.middleware';

export async function listDeals(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const deals = await prisma.deal.findMany({
      where: { ownerId: req.userId },
      include: { contact: { select: { id: true, firstName: true, lastName: true } } },
      orderBy: { updatedAt: 'desc' },
    });
    res.json({ success: true, data: deals });
  } catch (err) {
    next(err);
  }
}

export async function getDeal(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const deal = await prisma.deal.findFirst({
      where: { id: req.params.id, ownerId: req.userId },
      include: {
        contact: true,
        activities: { orderBy: { createdAt: 'desc' } },
      },
    });
    if (!deal) return next(createError('Deal not found', 404));
    res.json({ success: true, data: deal });
  } catch (err) {
    next(err);
  }
}

export async function createDeal(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const deal = await prisma.deal.create({
      data: { ...req.body, ownerId: req.userId as string },
    });
    res.status(201).json({ success: true, data: deal });
  } catch (err) {
    next(err);
  }
}

export async function updateDeal(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const existing = await prisma.deal.findFirst({
      where: { id: req.params.id, ownerId: req.userId },
    });
    if (!existing) return next(createError('Deal not found', 404));

    const deal = await prisma.deal.update({ where: { id: req.params.id }, data: req.body });
    res.json({ success: true, data: deal });
  } catch (err) {
    next(err);
  }
}

export async function deleteDeal(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const existing = await prisma.deal.findFirst({
      where: { id: req.params.id, ownerId: req.userId },
    });
    if (!existing) return next(createError('Deal not found', 404));

    await prisma.deal.delete({ where: { id: req.params.id } });
    res.json({ success: true, message: 'Deal deleted' });
  } catch (err) {
    next(err);
  }
}
