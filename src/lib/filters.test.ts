import { test } from 'node:test';
import { strict as assert } from 'node:assert';
import { matches, readFilters } from './filters';
import { route, alternate } from './routes';

test('OR dentro del atributo, AND entre atributos y vacío sin restricción', () => {
  const attributes = { sample: ['a'], shape: ['b'] };
  assert.equal(matches(attributes, { sample: ['a', 'c'], shape: ['b'] }), true);
  assert.equal(matches(attributes, { sample: ['a'], shape: ['d'] }), false);
  assert.equal(matches(attributes, { sample: [] }), true);
});
test('restauración ignora valores y claves ajenos al catálogo', () => {
  assert.deepEqual(readFilters('?sample=a&sample=c&sample=unknown&foreign=x', { sample: ['a', 'c'] }), { sample: ['a', 'c'] });
});
test('ES/EN conserva entidad y normaliza delimitadores', () => {
  assert.equal(alternate('es', 'products/categories/sample'), '/en/products/categories/sample/');
  assert.equal(route('es', '/contact/'), '/contact/');
  assert.equal(route('es'), '/');
  assert.equal(route('es', '/'), '/');
  assert.equal(alternate('en', 'products/categories/sample'), '/products/categories/sample/');
  assert.equal(alternate('en', ''), '/');
  assert.equal(route('en'), '/en/');
});
