import { Response, NextFunction } from 'express';
import { prisma } from '../utils/prisma';
import { AuthRequest } from '../middleware/auth.middleware';
import { createError } from '../middleware/error.middleware';

export async function listContacts(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const contacts = await prisma.contact.findMany({
      where: { ownerId: req.userId },
      orderBy: { updatedAt: 'desc' },
    });
    res.json({ success: true, data: contacts });
  } catch (err) {
    next(err);
  }
}

export async function getContact(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const contact = await prisma.contact.findFirst({
      where: { id: req.params.id, ownerId: req.userId },
      include: { deals: true, activities: { orderBy: { createdAt: 'desc' } } },
    });
    if (!contact) return next(createError('Contact not found', 404));
    res.json({ success: true, data: contact });
  } catch (err) {
    next(err);
  }
}

export async function createContact(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const contact = await prisma.contact.create({
      data: { ...req.body, ownerId: req.userId as string },
    });
    res.status(201).json({ success: true, data: contact });
  } catch (err) {
    next(err);
  }
}

export async function updateContact(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const existing = await prisma.contact.findFirst({
      where: { id: req.params.id, ownerId: req.userId },
    });
    if (!existing) return next(createError('Contact not found', 404));

    const contact = await prisma.contact.update({
      where: { id: req.params.id },
      data: req.body,
    });
    res.json({ success: true, data: contact });
  } catch (err) {
    next(err);
  }
}

export async function deleteContact(
  req: AuthRequest,
  res: Response,
  next: NextFunction,
): Promise<void> {
  try {
    const existing = await prisma.contact.findFirst({
      where: { id: req.params.id, ownerId: req.userId },
    });
    if (!existing) return next(createError('Contact not found', 404));

    await prisma.contact.delete({ where: { id: req.params.id } });
    res.json({ success: true, message: 'Contact deleted' });
  } catch (err) {
    next(err);
  }
}
