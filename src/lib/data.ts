import { z } from 'zod';
import { categorySchema, productSchema, solutionSchema, stageSchema, catalogSchema, caseSchema, localized } from '../types/content';
import siteData from '../data/site.json';
import categoryData from '../data/categories.json';
import productData from '../data/products.json';
import solutionData from '../data/solutions.json';
import catalogData from '../data/catalogs.json';
import caseData from '../data/case-studies.json';
import serviceData from '../data/capabilities.json';
import navigationData from '../data/navigation.json';
import homeData from '../data/home.json';
import aboutData from '../data/about.json';
import supplyData from '../data/supply-chain-resources.json';
import { mediaSchema } from '../types/content';

export const site = z.object({ name: z.string(), preview: z.boolean(), publicUrl: z.url().nullable(), logo: z.string(), contact: z.object({ endpoint: z.url().nullable() }) }).parse(siteData);
export const categories = z.array(categorySchema).parse(categoryData);
export const products = z.array(productSchema).parse(productData);
export const solutions = z.array(solutionSchema).parse(solutionData);
export const catalogs = z.array(catalogSchema).parse(catalogData);
export const cases = z.array(caseSchema).parse(caseData);
export const service = z.object({ title: localized, intro: localized, stages: z.array(stageSchema) }).parse(serviceData);
export const home = z.object({ title: localized, introTitle: localized, intro: localized, hero: mediaSchema }).parse(homeData);
export const about = z.object({ title: localized, description: localized, paragraphs: z.array(localized).min(1), culture: z.object({ title: localized, values: z.array(z.object({ id: z.string().min(1), title: localized })).length(4) }), source: z.string().min(1) }).parse(aboutData);
export const supply = z.object({ title: localized, intro: localized, resources: z.array(z.object({ id: z.string(), description: localized, gallery: z.array(mediaSchema), source: z.string() })) }).parse(supplyData);
export const navigation = z.array(z.object({ id: z.string(), title: localized, path: z.string().nullable(), group: z.enum(['about', 'catalogs', 'products', 'solutions']).nullable() })).parse(navigationData);
export function visible(status: string): boolean { return status === 'published' || (site.preview && status === 'demo'); }
export const visibleCategories = categories.filter(item => visible(item.status)).sort((a,b) => a.order-b.order);
export const visibleProducts = products.filter(item => visible(item.status));
export const visibleSolutions = solutions.filter(item => visible(item.status));
export const publishedCatalogs = catalogs.filter(item => item.status === 'published').sort((a,b) => a.order-b.order);
export const publishedCases = cases.filter(item => item.status === 'published' && item.permission);

export function validateRelations(): void {
  const groups = [categories, products, solutions, catalogs, cases, service.stages, supply.resources];
  for (const group of groups) {
    const ids = group.map(item => item.id);
    if (new Set(ids).size !== ids.length) throw new Error('IDs duplicados');
    const slugs = group.flatMap(item => 'slug' in item ? [item.slug] : []);
    if (new Set(slugs).size !== slugs.length) throw new Error('Slugs duplicados');
  }
  const requireRefs = (ids: string[], collection: {id: string; status?: string}[], origin: string, status = 'published') => {
    for (const id of ids) {
      const target = collection.find(item => item.id === id);
      if (!target) throw new Error(`${origin}: referencia inexistente ${id}`);
      if (status === 'published' && target.status && target.status !== 'published') throw new Error(`${origin}: referencia publicada a borrador/demo ${id}`);
    }
  };
  for (const product of products) {
    requireRefs(product.categoryIds, categories, product.id, product.status);
    requireRefs(product.solutionIds, solutions, product.id, product.status);
    requireRefs(product.caseIds, cases, product.id, product.status);
    for (const category of categories.filter(c => product.categoryIds.includes(c.id))) {
      for (const filter of category.filters) {
        for (const value of product.attributes[filter.key] ?? []) {
          if (!filter.values.some(option => option.id === value)) throw new Error(`${product.id}: valor de filtro inválido ${value}`);
        }
      }
    }
  }
  for (const solution of solutions) {
    requireRefs(solution.productIds, products, solution.id, solution.status);
    requireRefs(solution.caseIds, cases, solution.id, solution.status);
  }
  for (const stage of service.stages) requireRefs(stage.caseIds, cases, stage.id);
  for (const item of cases) if (item.status === 'published' && !item.permission) throw new Error(`${item.id}: falta autorización`);
  if (!site.preview && !site.publicUrl) throw new Error('Producción requiere dominio público real');
}
validateRelations();
