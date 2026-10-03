import type { Language } from '../types/content';

export function route(lang: Language, path = ''): string {
  const segment = path.replace(/^\/+|\/+$/g, '');
  const prefix = lang === 'en' ? '/en/' : '/';
  return `${prefix}${segment}${segment ? '/' : ''}`;
}
export function alternate(lang: Language, path: string): string {
  return route(lang === 'es' ? 'en' : 'es', path);
}
