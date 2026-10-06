"""Read the customer's menu and prepare an auditable mapping; no runtime edits."""
import collections
import hashlib
import json
import re
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/inventory'
SOURCE = Path('C:/Users/edmad/Downloads/Products menu.xlsx')
PRODUCTS = ROOT / 'src/data/products.json'

def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

def loc(es, en): return {'es': es, 'en': en}

# Stable IDs and Spanish labels. Original English labels and exact cells remain below.
labels = {
 'C3': ('paper', 'Empaques de papel'), 'C27': ('plastic', 'Empaques de plástico'),
 'C40': ('plant', 'Vajilla de origen vegetal'), 'C43': ('metal', 'Empaques de metal'),
 'C44': ('glass', 'Empaques de vidrio'), 'C45': ('packaging-accessories', 'Accesorios de empaque'),
 'D3': ('paper-food', 'Empaques de papel para alimentos'), 'D9': ('paper-nonfood', 'Empaques de papel para otros usos'),
 'D27': ('plastic-food', 'Empaques de plástico para alimentos'), 'D38': ('plastic-nonfood', 'Empaques de plástico para otros usos'),
 'D40': ('sugarcane-tableware', 'Vajilla de pulpa de caña'), 'D41': ('corn-starch-tableware', 'Vajilla de almidón de maíz'),
 'D42': ('kraft-tableware', 'Vajilla de papel kraft'), 'D43': ('metal-products', 'Tipos de empaque metálico'),
 'D44': ('glass-products', 'Botellas y frascos de vidrio'), 'D45': ('packaging-accessory-products', 'Tipos de accesorio de empaque'),
 'E3': ('paper-food-boxes', 'Cajas de papel para alimentos'), 'E4': ('paper-bowls', 'Tazones y cubetas de papel'),
 'E5': ('paper-cups', 'Vasos de papel'), 'E6': ('paper-food-tubes', 'Tubos y botes de papel para alimentos'),
 'E7': ('pulp-food-trays', 'Bandejas alimentarias de pulpa moldeada'), 'E8': ('paper-food-bags', 'Bolsas de papel para alimentos'),
 'E9': ('corrugated-cartons', 'Cajas de cartón corrugado'), 'E13': ('folding-cartons', 'Cajas impresas y plegadizas'),
 'E17': ('paper-nonfood-bags', 'Bolsas de papel'), 'E21': ('paper-nonfood-tubes', 'Tubos y botes de papel'),
 'E22': ('pulp-inserts', 'Insertos de pulpa moldeada'), 'E23': ('auxiliary-paper', 'Productos auxiliares de papel'),
 'E27': ('salad-containers', 'Envases para ensaladas'), 'E28': ('bakery-containers', 'Empaques para repostería'),
 'E29': ('bento-boxes', 'Cajas bento'), 'E30': ('fruit-containers', 'Envases para frutas'),
 'E31': ('pet-cups', 'Vasos PET'), 'E32': ('fruit-cups', 'Vasos para frutas'),
 'E33': ('cut-fruit-containers', 'Envases para fruta cortada'), 'E34': ('golen-container', 'Golden Container'),
 'E35': ('egg-boxes', 'Cajas para huevos'), 'E36': ('meat-containers', 'Envases para carne'),
 'E37': ('other-food-plastic', 'Otros empaques de plástico para alimentos'),
 'E38': ('flexible-nonfood', 'Empaques flexibles'), 'E39': ('rigid-nonfood', 'Empaques de plástico rígido'),
}

w = openpyxl.load_workbook(SOURCE, data_only=False)
s = w['Sheet1']
def anchor(row, col):
    for merged in s.merged_cells.ranges:
        if merged.min_row <= row <= merged.max_row and merged.min_col <= col <= merged.max_col:
            return s.cell(merged.min_row, merged.min_col)
    return s.cell(row, col)

nodes = []
for cell, (id_, es) in labels.items():
    c = s[cell]
    level = c.column - 2
    parent = None if level == 1 else labels[anchor(c.row, c.column-1).coordinate][0]
    en = re.sub(r'^\s*(?:[A-F]\.|[abc]-\d\.|\d+\.)\s*', '', str(c.value).strip()).strip()
    if cell == 'E34': en = 'Golden Container'
    examples = []
    if cell in ['D43', 'D44', 'D45']:
        examples = [x.strip() for x in re.split(r'[,\r\n]+', str(c.value)) if x.strip()]
        en = {'D43':'Metal packaging types','D44':'Glass bottles and jars','D45':'Packaging accessory types'}[cell]
    if level == 3:
        for row in range(c.row, 46):
            if anchor(row, 5).coordinate != cell: break
            if s.cell(row, 6).value:
                examples.extend(x.strip() for x in re.split(r'[,\r\n]+', str(s.cell(row,6).value)) if x.strip())
    nodes.append({'id':id_, 'parentId':parent,'level':level,'title':loc(es,en),'sourceCell':cell,
                  'sourceLabel':str(c.value),'examples':examples,'labelStatus':'client-clarified' if cell=='E34' else 'translated-proposal'})
    if cell == 'E34':
        nodes[-1]['clarification']={'source':'Client message supplied by user, 2026-10-05',
            'imagePath':'C:/Users/edmad/AppData/Local/Temp/codex-clipboard-f0b56309-cfc1-47f6-96a0-c3fcfca1a5ac.png',
            'meaning':'Golden PET plate; golden items distributed across 12 factory folders can be grouped together.',
            'rule':'Group by PET material and golden finish, regardless of original folder. Do not infer metal from golden appearance.'}
byid = {n['id']: n for n in nodes}
# D43-D45 contain individual menu-2 types separated by line breaks, not one
# invented category called "types". Keep each actual customer classification.
split_groups = {
 'metal-products': [('tin-box','Caja de hojalata','Tin box'),('tin-can','Lata de hojalata','Tin can'),('aluminum-box','Caja de aluminio','Aluminum box'),('aluminum-can','Lata de aluminio','Aluminum can'),('aluminum-foil','Papel de aluminio','Aluminum foil'),('metal-pail','Cubeta metálica','Metal pail')],
 'glass-products': [('glass-bottle','Botella de vidrio','Glass bottle'),('glass-jar','Frasco de vidrio','Glass jar')],
 'packaging-accessory-products': [('packing-tape','Cinta de empaque','Packing tape'),('strapping-band','Fleje','Strapping band'),('strap-buckle','Hebilla para fleje','Strap buckle'),('accessory-stretch-film','Película estirable','Stretch film'),('desiccant','Desecante','Desiccant'),('anti-rust-bag','Bolsa anticorrosiva','Anti-rust bag'),('security-seal','Sello de seguridad','Security seal'),('ribbon','Listón','Ribbon')],
}
for original, entries in split_groups.items():
    n = byid[original]
    nodes.remove(n)
    for id_,es,en in entries:
        nodes.append({**n,'id':id_,'title':loc(es,en),'examples':[]})
byid = {n['id']: n for n in nodes}
def path(id_):
    result = []
    while id_:
        result.insert(0,id_)
        id_ = byid[id_]['parentId']
    return result

cards = json.loads((OUT/'products-cards.json').read_text(encoding='utf8'))
card_by_id = {id_: c for c in cards for id_ in c.get('sourceCardIds',[c['id']])}
products = json.loads(PRODUCTS.read_text(encoding='utf8'))
paper = {'paper','paperboard','kraft-paper','kraft-paperboard','corrugated-board','bamboo-paper','greaseproof-paper','waxed-paper','pe-coated-paper','newsprint'}
plastic = {'pp','pet','pvc','ps','as','pe','opp'}

def classify(p):
    t = p['attributes']['product-type'][0]
    mats = set(p['attributes'].get('material',[]))
    title = p['title']['en'].lower()
    raw = card_by_id.get(p['id'],{}).get('attributes',{}).get('materialRaw','')
    assigned, proposed, reason = [], [], ''
    direct = {'paper-cups':'paper-cups','food-paper-bags':'paper-food-bags',
        'food-paper-boxes':'paper-food-boxes','pizza-boxes':'paper-food-boxes',
        'paper-bowls-buckets':'paper-bowls','printed-cartons':'folding-cartons',
        'corrugated-cartons':'corrugated-cartons','bakery-containers':'bakery-containers',
        'fruit-vegetable-containers':'fruit-containers','cut-fruit-containers':'cut-fruit-containers',
        'meat-trays':'meat-containers'}
    if 'golden' in title and mats == {'pet'}:
        assigned=['golen-container']; reason='PET y acabado dorado documentados; categoría aclarada por la clienta.'
    elif t in direct and mats and (mats <= paper or mats <= plastic):
        assigned=[direct[t]]; reason='Tipo y materiales documentados coinciden con la rama del Excel.'
    elif t=='paper-bags':
        assigned=['paper-nonfood-bags' if p['kind']=='family' else 'paper-food-bags']
        reason='Familia de bolsas comerciales de papel.' if p['kind']=='family' else 'Bolsa del catálogo de portavasos y bebidas; material papel confirmado.'
    elif t=='beverage-cans' and mats=={'aluminum'}:
        assigned=['aluminum-can']; reason='Lata de aluminio documentada; categoría incluida en D43.'
    elif t=='can-lids' and mats=={'aluminum'}:
        proposed=['aluminum-can']; reason='Tapa para lata de aluminio: se agrupa con el envase compatible por similitud.'
    elif t=='cup-carriers' and 'pulp' in title:
        assigned=['pulp-food-trays']; reason='Título de fuente identifica bandeja de pulpa para vasos. No se afirma pulpa de caña.'
    elif t in {'plastic-cups','iml-cups'} and mats=={'pet'}:
        assigned=['pet-cups']; reason='Vaso con PET confirmado.'
    elif t=='food-containers' and mats <= paper and mats:
        proposed=['paper-bowls']; reason='Papel confirmado; revisar forma: el tipo genérico de envase no distingue tazón, cubeta o caja.'
    elif t=='plastic-bags' and mats <= plastic and mats:
        assigned=['other-food-plastic']; reason='Bolsa plástica para portavasos/bebidas. Flexible Packaging del Excel pertenece a usos no alimentarios.'
    elif mats and mats <= plastic and t in {'beverage-bottles','beverage-cans','dessert-jars','cutlery','straws','cup-lids','plastic-cups','iml-cups','food-containers','cold-noodle-containers','skin-pack-trays','map-trays','cup-accessories'}:
        assigned=['other-food-plastic']; reason='Aplicación alimentaria y plástico documentados; no hay subtipo específico del Excel.'
    elif raw.lower() in {'plastic','food-use opp'}:
        assigned=['other-food-plastic']; reason='La fuente confirma plástico de uso alimentario sin requerir inferir polímero.'
    elif t=='wrappers-sheets':
        reason='Envolturas/individuales de papel para alimentos: falta esa rama. Auxiliary paper products está bajo usos no alimentarios.'
    elif t in {'cup-carriers','cup-accessories','straws'} and mats and mats <= paper:
        reason='Accesorio alimentario de papel sin rama específica en el Excel; no convertirlo en bandeja de pulpa o accesorio logístico.'
    elif t=='multipacks':
        proposed=['folding-cartons']; reason='Multipack de cartón: confirmar aplicación y estructura antes de colocarlo en cajas plegadizas no alimentarias.'
    elif 'pla' in mats:
        reason='PLA confirmado; no prueba almidón de maíz ni origen de la materia prima. Falta rama para PLA.'
    elif not mats:
        reason='Falta material confirmado para esta taxonomía basada en material.'
        if t in {'cup-lids','iml-cups','plastic-cups','food-containers','beverage-bottles','dessert-jars','cutlery','cup-accessories','can-lids','plastic-bags'}:
            proposed=['other-food-plastic'] if t!='can-lids' else ['aluminum-can']
    else:
        reason='No hay rama inequívoca con la evidencia actual.'
    original_reason = reason
    basis = 'documented-match'
    if not assigned:
        basis = 'nearest-excel-category'
        if proposed:
            assigned = proposed
        elif 'pla' in mats:
            assigned = ['corn-starch-tableware']
        elif mats and mats <= paper and t in {'cup-carriers','cup-accessories','straws','wrappers-sheets'}:
            assigned = ['auxiliary-paper']
        else:
            raise ValueError(f'{p["id"]}: falta regla de categoría más cercana')
        proposed = []
        reason = 'Asignación por similitud autorizada por el usuario; no modifica material ni aplicación documentados. ' + original_reason
    status = 'classified' if basis == 'documented-match' else 'assigned-by-similarity'
    # Latest client scope: yellow branches only. Move compatible food formats
    # from Others by actual type/source context, never beverage bottles to cups.
    closest = None
    if t == 'food-containers' and not (mats and mats <= paper):
        closest = 'bento-boxes' if ('box' in title or p['id'].startswith('qunlu-')) else 'salad-containers'
    elif t == 'cold-noodle-containers': closest = 'bento-boxes'
    elif t in {'skin-pack-trays','map-trays'}: closest = 'meat-containers'
    elif t == 'dessert-jars': closest = 'bakery-containers'
    if closest:
        assigned=[closest]; basis='nearest-excel-category'; status='assigned-by-similarity'
        reason='Rama amarilla más cercana por formato alimentario: '+t+'. Se conservan dimensiones, material y uso originales; la asignación comercial puede ajustarse.'
    return {'productId':p['id'],'title':p['title'],'status':status,'nodeIds':assigned,
        'assignmentBasis':basis,'reviewRecommended':basis=='nearest-excel-category',
        'paths':[path(i) for i in assigned],'candidateNodeIds':proposed,'reason':reason,
        'evidence':{'productType':t,'materialIds':sorted(mats),'materialRaw':raw or None,'sources':p['provenance']},
        'currentCategoryIds':p['categoryIds']}

records = [classify(p) for p in products]
scope = json.loads((OUT/'products-menu-scope.json').read_text(encoding='utf8'))
offered = set(scope['offeredLeafIds'])
allowed_nodes = {i for leaf in offered for i in path(leaf)}
for r in records:
    if not all(i in offered for i in r['nodeIds']):
        t = r['evidence']['productType']
        mats = set(r['evidence']['materialIds'])
        if 'pla' in mats or t == 'cutlery': target = 'corn-starch-tableware'
        elif mats and mats <= paper: target = 'paper-cups' if t in {'cup-lids','cup-accessories','cup-carriers','straws'} else 'kraft-tableware'
        elif t in {'beverage-bottles','beverage-cans','can-lids','cup-lids','plastic-cups','iml-cups','straws','cup-accessories'}: target = 'pet-cups'
        else: target = 'bento-boxes'
        r['previousNodeIds'] = r['nodeIds']
        r['nodeIds'] = [target]
        r['paths'] = [path(target)]
        r['assignmentBasis'] = 'nearest-excel-category'
        r['status'] = 'assigned-by-similarity'
        r['reviewRecommended'] = True
        r['reason'] = 'Agrupación comercial en la rama disponible más cercana por instrucción del usuario. No afirma que coincidan el material, forma o uso del nombre de la categoría; consultar atributos originales.'
    r['offered'] = all(i in offered for i in r['nodeIds'])
    r['excludedReason'] = None if r['offered'] else 'Fuera de las ramas amarillas confirmadas por la clienta.'
for n in nodes: n['offered'] = n['id'] in allowed_nodes
assert len(records)==1199 and len({r['productId'] for r in records})==len(products)
assert len({n['id'] for n in nodes})==len(nodes)
for n in nodes:
    assert n['parentId'] is None or n['parentId'] in byid
    assert n['parentId'] is None or byid[n['parentId']]['level'] == n['level'] - 1
for r in records:
    assert all(i in byid for i in r['nodeIds']+r['candidateNodeIds'])
    assert r['nodeIds'] and r['status'] in {'classified','assigned-by-similarity'}
    assert not (set(r['nodeIds']) & set(r['candidateNodeIds']))
for n in nodes:
    n['classifiedProductIds']=[r['productId'] for r in records if n['id'] in sum(r['paths'],[])]
    n['similarityProductIds']=[r['productId'] for r in records if r['reviewRecommended'] and n['id'] in sum(r['paths'],[])]
    n['counts']={'assigned':len(n['classifiedProductIds']),'bySimilarity':len(n['similarityProductIds'])}
    n['counts']['public']=sum(r['offered'] and n['id'] in sum(r['paths'],[]) for r in records)

metadata={'sourcePath':str(SOURCE),'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'sheet':'Sheet1','range':'B2:F45','productSnapshotSha256':hashlib.sha256(PRODUCTS.read_bytes()).hexdigest(),
 'scope':'1199 current website entries; deferred research records excluded',
 'navigationImplemented':False,'levels':3,'rootCount':6,'publicCategoryCount':len(nodes),
 'offeredProductCount':sum(r['offered'] for r in records),
 'excludedProductCount':sum(not r['offered'] for r in records),
 'offeredCategoryCount':len(allowed_nodes),
 'unassignedCount':sum(not r['nodeIds'] for r in records),
 'policy':'Use only Excel categories; place unmatched products in the nearest category without changing factual attributes.',
 'statusCounts':dict(collections.Counter(r['status'] for r in records))}
write('products-menu-taxonomy.json',{'metadata':metadata,'nodes':nodes})
write('products-menu-classification.json',{'metadata':metadata,'products':records})
write('products-menu-review.json',{'metadata':metadata,'products':[r for r in records if r['offered'] and r['status']!='classified']})
# Locate existing extraction candidates in the yellow source families. They
# remain research records until photo/specification ambiguity is resolved.
research_targets={'food-containers':'bento-boxes','cold-noodle-containers':'bento-boxes',
 'meat-trays':'meat-containers','skin-pack-trays':'meat-containers','map-trays':'meat-containers',
 'fruit-vegetable-containers':'fruit-containers','cut-fruit-containers':'cut-fruit-containers',
 'bakery-containers':'bakery-containers','salad-containers':'salad-containers',
 'plastic-cups':'pet-cups','egg-containers':'egg-boxes'}
current_ids={p['id'] for p in products}
candidates=[]
for model in json.loads((OUT/'products-models.json').read_text(encoding='utf8')):
    if model['id'] in current_ids: continue
    targets={research_targets[t] for t in model.get('categoryIds',[]) if t in research_targets}
    if 'golden' in (model.get('modelCode') or '').lower(): targets={'golen-container'}
    if targets:
        candidates.append({'id':model['id'],'candidateNodeIds':sorted(targets),
            'modelCode':model.get('modelCode'),'materialIds':model.get('materialIds',[]),
            'sources':model.get('sources',[]),'status':'research-only-needs-spec-and-photo-verification'})
write('products-menu-yellow-candidates.json',{'note':'Source-family candidates, not confirmed additional available products or published entries. Resolve OCR/spec/photo evidence first. PET cup candidates require PET confirmation.',
    'count':len(candidates),'records':candidates})
lines = ['# Clasificación vigente del catálogo', '',
    'Por aclaración del usuario: todas las 1,199 fichas se publican y se asignan a las 14 ramas amarillas. Las 54 categorías del Excel permanecen visibles bajo seis grupos; las ramas restantes muestran próximos productos cuando no tienen fichas.', '',
    'Las asignaciones por similitud son agrupaciones comerciales. No convierten botellas en vasos, PP en PET ni PLA en almidón. Los materiales, tipos, fotos y especificaciones originales se conservan. La categoría es navegación; los atributos son evidencia técnica.', '',
    '| Nivel | Categoría | Fichas incluyendo descendientes | Disponible (amarillo/ancestro) |',
    '| --- | --- | ---: | --- |']
for n in nodes:
    lines.append(f"| {n['level']} | {n['title']['es']} | {n['counts']['public']} | {'Sí' if n['offered'] else 'Próximamente'} |")
lines += ['', 'Golden Container conserva su ID de fuente golen-container y el slug corregido golden-container. Los candidatos de investigación todavía no son fichas verificadas.', '',
    'products-menu-classification.json contiene la asignación, evidencia, razón y categoría anterior para auditar movimientos. products-menu-review.json reúne las asignaciones por similitud. products-menu-scope.json define las ramas que reciben productos.', '',
    'Regenerar: classify_products_menu.py y apply_products_menu.py; después validate:data, check, test y build. Para reextracción ejecutar primero prepare_catalog.py. Los scripts no modifican el Excel original.']
(OUT/'PRODUCTS-MENU.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print(json.dumps({'nodes':len(nodes),**metadata['statusCounts']},ensure_ascii=False))
