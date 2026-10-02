import { existsSync } from 'node:fs';
import { categories, products, solutions, service, supply, site, validateRelations } from '../src/lib/data';

validateRelations();
const media = [...categories.map(c=>c.media), ...products.flatMap(p=>p.gallery), ...solutions.map(s=>s.media), ...service.stages.map(s=>s.media), ...supply.resources.flatMap(r=>r.gallery)];
for (const item of media) for (const path of [item.src, item.poster]) {
  if (path && !existsSync(`public${path}`)) throw new Error(`Asset inexistente: ${path}`);
}
if (!existsSync(`public${site.logo}`)) throw new Error('Logo inexistente');
console.log(`Datos válidos: ${products.length} productos, ${categories.length} categorías, ${solutions.length} soluciones. Modo ${site.preview ? 'prototipo (noindex)' : 'producción'}.`);
