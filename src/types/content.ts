import { z } from 'zod';

export const languages = ['es', 'en'] as const;
export type Language = (typeof languages)[number];
export const localized = z.object({ es: z.string().min(1), en: z.string().min(1) });
export type Localized = z.infer<typeof localized>;
const id = z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/);
const base = { id, slug: id, title: localized, description: localized, status: z.enum(['draft', 'published', 'demo']) };
export const mediaSchema = z.object({
  type: z.enum(['image', 'video']),
  placeholder: z.boolean(),
  src: z.string().optional(),
  poster: z.string().optional(),
  alt: localized,
  ratio: z.number().positive(),
  fit: z.enum(['cover', 'contain']).optional(),
  width: z.number().int().positive().optional(),
  height: z.number().int().positive().optional(),
  caption: localized.optional(),
}).superRefine((media, ctx) => {
  if (!media.placeholder && !media.src) ctx.addIssue({ code: 'custom', message: 'Media real requiere src' });
  if (media.src && !media.src.startsWith('/images/')) ctx.addIssue({ code: 'custom', message: 'Asset debe ser local en /images/' });
});
export type Media = z.infer<typeof mediaSchema>;
export const filterSchema = z.object({ key: id, label: localized, values: z.array(z.object({ id, label: localized })).min(1) });
export const categorySchema = z.object({ ...base, order: z.number().int(), media: mediaSchema, filters: z.array(filterSchema), parentId: id.nullable(), level: z.number().int().min(1).max(3), sourceCell: z.string().min(1) });
export const productSchema = z.object({
  ...base, categoryIds: z.array(id).min(1), solutionIds: z.array(id), caseIds: z.array(id),
  gallery: z.array(mediaSchema).min(1), attributes: z.record(z.string(), z.array(z.string())),
  specifications: z.array(z.object({ label: localized, value: localized })),
  source: z.string().min(1),
  kind: z.enum(['model', 'family']).optional(),
  classification: z.object({basis:z.enum(['documented-match','nearest-excel-category']),reviewRecommended:z.boolean()}),
  modelCode: z.string().min(1).optional(),
  dimensions: z.object({ raw: z.string().min(1), axisOrder: z.string().min(1) }).optional(),
  provenance: z.array(z.object({ sourceId: id, page: z.number().int().positive(), language: z.enum(languages) })).optional(),
});
export const solutionSchema = z.object({ ...base, media: mediaSchema, productIds: z.array(id), caseIds: z.array(id) });
export const stageSchema = z.object({ id, order: z.number(), title: localized, description: localized, media: mediaSchema, caseIds: z.array(id) });
export const catalogSchema = z.object({ id, title: localized, url: z.object({ es: z.url(), en: z.url() }).refine(urls => Object.values(urls).every(url => new URL(url).hostname === 'drive.google.com' && /^\/file\/d\/[^/]+\/view$/.test(new URL(url).pathname)), 'El catálogo debe abrir un PDF de Drive en cada idioma'), status: z.enum(['draft', 'published']), order: z.number(), categoryIds:z.array(id).default([]) });
export const caseSchema = z.object({ ...base, media: mediaSchema, permission: z.boolean() });
export type Category = z.infer<typeof categorySchema>;
export type Product = z.infer<typeof productSchema>;
export type Solution = z.infer<typeof solutionSchema>;
