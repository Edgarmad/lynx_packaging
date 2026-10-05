/** Clamp untrusted query parameters before slicing an HTML catalog. */
export function catalogPage(raw: string | null, total: number, size = 24): { page: number; pages: number; start: number; end: number } {
  const pages = Math.max(1, Math.ceil(total / size));
  const parsed = raw && /^\d+$/.test(raw) ? Number(raw) : 1;
  const page = Math.min(pages, Math.max(1, Number.isSafeInteger(parsed) ? parsed : 1));
  return { page, pages, start: (page - 1) * size, end: Math.min(page * size, total) };
}
export function catalogSearch(text: string, query: string): boolean {
  const normalize = (value: string) => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase().trim();
  return normalize(query).split(/\s+/).every(word => normalize(text).includes(word));
}
/** A short editorial selection includes distinct types/materials before variants. */
export function catalogHighlights<T extends { id: string; attributes: Record<string, string[]> }>(items: T[], limit = 6): T[] {
  const types = new Set<string>();
  const selected: T[] = [];
  for (const item of items) {
    const key = `${item.attributes['product-type']?.[0] ?? ''}:${item.attributes.material?.[0] ?? ''}`;
    if (!types.has(key)) { types.add(key); selected.push(item); }
    if (selected.length === limit) return selected;
  }
  for (const item of items) {
    if (!selected.some(other => other.id === item.id)) selected.push(item);
    if (selected.length === limit) break;
  }
  return selected;
}
