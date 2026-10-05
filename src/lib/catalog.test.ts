import assert from 'node:assert/strict';
import { test } from 'node:test';
import { catalogPage, catalogSearch, catalogHighlights } from './catalog';

test('pagination clamps stale and malformed URL values after filtering', () => {
  assert.deepEqual(catalogPage('3', 55), { page: 3, pages: 3, start: 48, end: 55 });
  assert.deepEqual(catalogPage('3', 4), { page: 1, pages: 1, start: 0, end: 4 });
  for (const raw of ['0', '-2', 'Infinity', '2.5', '9999999999999999999999', 'foo']) assert.equal(catalogPage(raw, 55).page, 1);
  assert.deepEqual(catalogPage(null, 0), { page: 1, pages: 1, start: 0, end: 0 });
});
test('search accepts accents, model codes and multiple terms', () => {
  assert.equal(catalogSearch('Vaso de plástico · GHW-1965', 'PLASTICO ghw'), true);
  assert.equal(catalogSearch('Vaso de plástico · GHW-1965', 'papel ghw'), false);
  assert.equal(catalogSearch('Cup PET', '  '), true);
});
test('home selections prioritize different materials before color variants', () => {
  const items=[{id:'a',attributes:{'product-type':['cup'],material:['pp']}},{id:'b',attributes:{'product-type':['cup'],material:['pp']}},{id:'c',attributes:{'product-type':['cup'],material:['paper']}}];
  assert.deepEqual(catalogHighlights(items,2).map(item=>item.id),['a','c']);
  assert.deepEqual(catalogHighlights(items,6).map(item=>item.id),['a','c','b']);
});
