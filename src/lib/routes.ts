import type { Language } from '../types/content';

export function route(lang: Language, path = ''): string {
  return `/${lang}/${path.replace(/^\/+|\/+$/g, '')}${path ? '/' : ''}`;
}
export function alternate(lang: Language, path: string): string {
  return route(lang === 'es' ? 'en' : 'es', path);
}
