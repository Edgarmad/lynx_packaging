import assert from 'node:assert/strict';
import { test } from 'node:test';
import { categories, visibleCategories, products, visibleProducts, allVisibleCategories } from './data';
import scope from '../../docs/inventory/products-menu-scope.json';

test('full Excel menu stays visible including upcoming branches',()=>{
  assert.equal(visibleCategories.length,6);
  assert.equal(allVisibleCategories.length,54);
  assert.ok(categories.every(c=>c.status==='published'));
  for(const [parent,count] of [['metal',6],['glass',2],['packaging-accessories',8]] as const)
    assert.equal(categories.filter(c=>c.parentId===parent).length,count);
  assert.equal(categories.find(c=>c.id==='golen-container')?.title.en,'Golden Container');
});
test('all products use available branches and keep factual materials',()=>{
  assert.equal(products.length,1199);
  assert.equal(visibleProducts.length,1199);
  for(const p of products){
    const path=p.categoryIds.map(id=>categories.find(c=>c.id===id)!);
    assert.equal(path[0].level,1);
    assert.ok(path.length>=2&&path.length<=3);
    path.slice(1).forEach((c,index)=>assert.equal(c.parentId,path[index].id));
    assert.equal(p.status,'published');
    assert.ok(scope.offeredLeafIds.includes(path.at(-1)!.id));
    if(p.attributes.material?.includes('pla')) assert.equal(path.at(-1)?.id,'corn-starch-tableware');
  }
  assert.ok(products.filter(p=>p.attributes['product-type']?.includes('beverage-bottles')).every(p=>p.status==='published'));
  for(const category of categories.filter(c=>!scope.offeredLeafIds.includes(c.id)&&!categories.some(child=>child.parentId===c.id)))
    assert.ok(products.every(p=>!p.categoryIds.includes(category.id)));
});
