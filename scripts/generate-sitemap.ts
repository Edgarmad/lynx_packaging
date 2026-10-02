import { writeFileSync } from 'node:fs';
import { site, visibleCategories, visibleProducts, visibleSolutions } from '../src/lib/data';
import { languages } from '../src/types/content';
import { route } from '../src/lib/routes';

if (!site.preview && site.publicUrl) {
  const paths = ['', 'about/overview', 'about/one-stop-service', 'about/supply-chain-resources', 'products', 'solutions', 'contact',
    ...visibleCategories.filter(c=>c.status==='published').map(c=>`products/categories/${c.slug}`),
    ...visibleProducts.filter(p=>p.status==='published').map(p=>`products/${p.slug}`),
    ...visibleSolutions.filter(s=>s.status==='published').map(s=>`solutions/${s.slug}`)];
  const escape=(value:string)=>value.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
  const urls=languages.flatMap(lang=>paths.map(path=>`<url><loc>${escape(new URL(route(lang,path),site.publicUrl!).href)}</loc></url>`));
  writeFileSync('dist/sitemap.xml',`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls.join('')}</urlset>`);
  writeFileSync('dist/robots.txt',`User-agent: *\nAllow: /\nSitemap: ${new URL('/sitemap.xml',site.publicUrl).href}\n`);
} else {
  writeFileSync('dist/robots.txt','User-agent: *\nDisallow: /\n');
}
