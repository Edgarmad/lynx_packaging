export type Selection = Record<string, string[]>;
export function matches(attributes: Record<string, string[]>, selection: Selection): boolean {
  return Object.entries(selection).every(([key, values]) => values.length === 0 || values.some(value => attributes[key]?.includes(value)));
}
export function readFilters(search: string, allowed: Record<string, string[]>): Selection {
  const params = new URLSearchParams(search);
  return Object.fromEntries(Object.entries(allowed).map(([key, values]) => [key, params.getAll(key).filter(value => values.includes(value))]));
}
