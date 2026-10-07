import { z } from 'zod';
import { catalogSchema, localized } from '../types/content';
import data from '../data/catalog-groups.json';
import catalogData from '../data/catalogs.json';

const catalogs = z.array(catalogSchema).parse(catalogData);
const groups = z.array(z.object({ id: z.string().min(1), title: localized, downloads: z.array(z.object({ id: z.string().min(1) })).min(1) })).parse(data);
export const catalogGroups = groups.map(group => ({ ...group, downloads: group.downloads.flatMap(reference => {
  const catalog = catalogs.find(item => item.id === reference.id);
  if (!catalog) throw new Error(`Referencia de catálogo inexistente: ${reference.id}`);
  return catalog.status === 'published' ? [catalog] : [];
}) }));
const ids = catalogGroups.flatMap(group => [group.id, ...group.downloads.map(item => item.id)]);
if (new Set(ids).size !== ids.length) throw new Error('Los grupos y descargas deben tener IDs únicos');
