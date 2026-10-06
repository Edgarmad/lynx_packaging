"""Apply the audited Excel classification to local runtime JSON."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT/'src/data'
AUDIT = ROOT/'docs/inventory'
def read(path): return json.loads(path.read_text(encoding='utf8'))
def write(path, value): path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n',encoding='utf8')
taxonomy = read(AUDIT/'products-menu-taxonomy.json')['nodes']
mapping = {r['productId']:r for r in read(AUDIT/'products-menu-classification.json')['products']}
products = read(DATA/'products.json')
old_categories = read(DATA/'categories.json')
# Keep one vocabulary of actual filter labels, including when the script is rerun.
filters = {}
for c in old_categories:
    for f in c['filters']:
        target = filters.setdefault(f['key'], {'key':f['key'],'label':f['label'],'values':{}})
        target['values'].update({v['id']:v for v in f['values']})
filters['product-type']['values'].update({c['id']:{'id':c['id'],'label':c['name']} for c in read(AUDIT/'categories-proposed.json')})
for p in products:
    r = mapping[p['id']]
    p['categoryIds'] = list(dict.fromkeys(i for path in r['paths'] for i in path))
    p['classification'] = {'basis':r['assignmentBasis'],'reviewRecommended':r['reviewRecommended']}
    p['status']='published' if r['offered'] else 'draft'
    if not r['offered']:
        p['solutionIds']=[]
        p['caseIds']=[]
    else:
        p['solutionIds']=['food-beverage']
assert set(mapping)=={p['id'] for p in products}
root_media = {
 'paper':'/images/products/category-cups.webp',
 'plastic':'/images/products/category-food-containers.webp',
}
# Use an actual representative packshot; empty groups keep honest placeholders.
categories = []
for order,n in enumerate(taxonomy):
    items = [p for p in products if n['id'] in p['categoryIds'] and p['status']=='published']
    media = copy.deepcopy(items[0]['gallery'][0]) if items else {
        'type':'image','placeholder':True,'ratio':1.8,'alt':n['title']}
    media['alt']=n['title']
    if n['id'] in root_media:
        # Prefer existing editorial assets only when present.
        asset = ROOT/'public'/root_media[n['id']].lstrip('/')
        if asset.exists():
            media={'type':'image','placeholder':False,'src':root_media[n['id']],
                'ratio':1.8,'fit':'cover','alt':n['title'],
                'caption':{'es':'Composición ilustrativa de packaging.','en':'Illustrative packaging composition.'}}
    category_filters=[]
    for f in filters.values():
        used = {v for p in items for v in p['attributes'].get(f['key'],[])}
        if used:
            assert used <= set(f['values']), (n['id'],f['key'],used-set(f['values']))
            category_filters.append({'key':f['key'],'label':f['label'],'values':[v for id_,v in f['values'].items() if id_ in used]})
    categories.append({'id':n['id'],'slug':'golden-container' if n['id']=='golen-container' else n['id'],'parentId':n['parentId'],'level':n['level'],
        'title':n['title'],'description':{'es':'Explora '+n['title']['es'].lower()+' y sus opciones de materiales, tipos y medidas.',
            'en':'Explore '+n['title']['en'].lower()+' and available materials, types and sizes.'},
        'status':'published','order':order,'media':media,'filters':category_filters,'sourceCell':n['sourceCell']})
write(DATA/'categories.json',categories)
(DATA/'products.json').write_text('[\n'+',\n'.join(json.dumps(p,ensure_ascii=False,separators=(',',':')) for p in products)+'\n]\n',encoding='utf8')
nav=read(DATA/'navigation.json')
next(n for n in nav if n['id']=='catalogs')['path']='catalogs'
write(DATA/'navigation.json',nav)
solutions=read(DATA/'solutions.json')
for solution in solutions:
    solution['productIds']=[p['id'] for p in products if solution['id'] in p['solutionIds']]
    if solution['id']=='food-beverage':
        solution['description']={'es':'Vasos de papel, envases plásticos para alimentos y vajilla de origen vegetal. Explora las opciones y medidas disponibles para tu proyecto.',
            'en':'Paper cups, plastic food containers and plant-based tableware. Explore available options and sizes for your project.'}
    elif solution['id'] in {'retail','custom'}:
        solution['description']={'es':'Consulta las necesidades de tu proyecto y las opciones de empaque dentro de nuestro catálogo actual.',
            'en':'Discuss your project requirements and packaging options within our current catalog.'}
write(DATA/'solutions.json',solutions)
for name in ['products-menu-taxonomy.json','products-menu-classification.json','products-menu-review.json']:
    report=read(AUDIT/name)
    report['metadata']['navigationImplemented']=True
    report['metadata']['runtimeCategoryCount']=sum(c['status']=='published' for c in categories)
    write(AUDIT/name,report)
print(f'Applied {sum(p["status"]=="published" for p in products)} public products, {sum(c["status"]=="published" for c in categories)} public categories, {sum(c["level"]==1 and c["status"]=="published" for c in categories)} roots; archive retained.')
