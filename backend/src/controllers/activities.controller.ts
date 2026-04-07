import { Response, NextFunction } from 'express';
import { prisma } from '../utils/prisma';
import { AuthRequest } from '../middleware/auth.middleware';
import { createError } from '../middleware/error.middleware';

export async function listActivities(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const activities = await prisma.activity.findMany({
      where: { ownerId: req.userId },
      include: {
        contact: { select: { id: true, firstName: true, lastName: true } },
        deal: { select: { id: true, title: true } },
      },
      orderBy: { dueDate: 'asc' },
    });
    res.json({ success: true, data: activities });
  } catch (err) {
    next(err);
  }
}

export async function createActivity(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const activity = await prisma.activity.create({
      data: { ...req.body, ownerId: req.userId as string },
    });
    res.status(201).json({ success: true, data: activity });
  } catch (err) {
    next(err);
  }
}

export async function updateActivity(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const existing = await prisma.activity.findFirst({
      where: { id: req.params.id, ownerId: req.userId },
    });
    if (!existing) return next(createError('Activity not found', 404));

    const activity = await prisma.activity.update({
      where: { id: req.params.id },
      data: req.body,
    });
    res.json({ success: true, data: activity });
  } catch (err) {
    next(err);
  }
}

export async function deleteActivity(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const existing = await prisma.activity.findFirst({
      where: { id: req.params.id, ownerId: req.userId },
    });
    if (!existing) return next(createError('Activity not found', 404));

    await prisma.activity.delete({ where: { id: req.params.id } });
    res.json({ success: true, message: 'Activity deleted' });
  } catch (err) {
    next(err);
  }
}
