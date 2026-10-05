import { existsSync, readFileSync } from 'node:fs';
import { z } from 'zod';
import { categories, products, solutions, service, supply, site, home, validateRelations } from '../src/lib/data';
import { editorialMedia } from '../src/lib/editorial-media';

validateRelations();
const sourceSchema=z.array(z.object({id:z.string(),pages:z.number().int().positive()}));
const sources=sourceSchema.parse(JSON.parse(readFileSync('docs/inventory/sources.json','utf8')));
for(const product of products){
  for(const ref of product.provenance??[]){
    const source=sources.find(item=>item.id===ref.sourceId);
    if(!source||ref.page>source.pages)throw new Error(`${product.id}: procedencia inválida ${ref.sourceId} p. ${ref.page}`);
  }
  if(product.status==='published'&& !(['es','en'] as const).every(lang=>product.provenance?.some(ref=>ref.language===lang)))throw new Error(`${product.id}: falta evidencia bilingüe`);
}
const media = [home.hero, ...Object.values(editorialMedia), ...categories.map(c=>c.media), ...products.flatMap(p=>p.gallery), ...solutions.map(s=>s.media), ...service.stages.map(s=>s.media), ...supply.resources.flatMap(r=>r.gallery)];
for (const item of media) for (const path of [item.src, item.poster]) {
  if (path && !existsSync(`public${path}`)) throw new Error(`Asset inexistente: ${path}`);
}
if (!existsSync(`public${site.logo}`)) throw new Error('Logo inexistente');
console.log(`Datos válidos: ${products.length} productos, ${categories.length} categorías, ${solutions.length} soluciones. Modo ${site.preview ? 'prototipo (noindex)' : 'producción'}.`);
