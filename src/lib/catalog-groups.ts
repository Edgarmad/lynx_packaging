import { z } from 'zod';
import { localized } from '../types/content';
import data from '../data/catalog-groups.json';

const download = z.object({ id: z.string().min(1), title: localized, url: z.union([z.literal(''), z.url().refine(url => new URL(url).hostname === 'drive.google.com')]) });
export const catalogGroups = z.array(z.object({ id: z.string().min(1), title: localized, downloads: z.array(download).min(1) })).parse(data);
const ids = catalogGroups.flatMap(group => [group.id, ...group.downloads.map(item => item.id)]);
if (new Set(ids).size !== ids.length) throw new Error('Los grupos y descargas deben tener IDs únicos');
