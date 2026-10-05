import json,re,hashlib,collections
from pathlib import Path
O=Path('docs/inventory')
def read(n):return json.loads((O/n).read_text(encoding='utf8'))
def write(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
cards=read('products-cards.json');models=read('products-models.json');families=read('product-families.json');sources=read('sources.json')
labels={
'paper-bags':('Bolsas de papel','Paper bags'),'food-paper-bags':('Bolsas de papel para alimentos','Food paper bags'),'cup-carriers':('Portavasos y bandejas','Cup carriers and trays'),'plastic-bags':('Bolsas de plástico','Plastic bags'),'beverage-bottles':('Botellas para bebidas','Beverage bottles'),'paper-cups':('Vasos de papel','Paper cups'),'plastic-cups':('Vasos de plástico','Plastic cups'),'iml-cups':('Vasos IML','IML cups'),'cup-lids':('Tapas para vasos','Cup lids'),'beverage-cans':('Envases para bebidas con apertura fácil','Easy-open beverage containers'),'can-lids':('Tapas de apertura fácil','Easy-open lids'),'straws':('Popotes','Straws'),'cutlery':('Cubiertos','Cutlery'),'cup-accessories':('Fundas y accesorios','Sleeves and accessories'),'food-containers':('Recipientes para alimentos','Food containers'),'dessert-jars':('Tarros y recipientes para postres','Dessert jars and containers'),'paper-bowls-buckets':('Boles y cubetas de papel','Paper bowls and buckets'),'food-paper-boxes':('Cajas de papel para alimentos','Paper food cartons'),'pizza-boxes':('Cajas para pizza','Pizza boxes'),'wrappers-sheets':('Envolturas y manteles de papel','Paper wrappers and placemats'),'printed-cartons':('Cajas de cartón impresas','Printed cartons'),'corrugated-cartons':('Cajas de cartón corrugado','Corrugated cartons'),'multipacks':('Empaques multipack','Multipacks'),'ice-cream-packaging':('Empaques para helados','Ice cream packaging'),'cold-noodle-containers':('Envases para fideos fríos y comidas','Cold noodle containers'),'meat-trays':('Envases para carnes y alimentos frescos','Meat and fresh-food containers'),'skin-pack-trays':('Bandejas para envasado skin','Vacuum skin-pack trays'),'map-trays':('Envases de atmósfera modificada','Modified-atmosphere containers'),'frozen-food-containers':('Bandejas para congelados','Frozen-food trays'),'bakery-containers':('Envases para repostería','Bakery containers'),'fruit-vegetable-containers':('Envases para frutas y verduras','Fruit and vegetable containers'),'cut-fruit-containers':('Envases para fruta cortada','Cut-fruit containers'),'salad-containers':('Envases para ensaladas','Salad containers'),'food-trays':('Bandejas para alimentos','Food trays'),'egg-containers':('Envases para huevos','Egg containers'),'cling-film':('Película para alimentos','Cling film')}
def category(p):
 sid=p['sources'][0]['sourceId'];name=p['name']['en'].lower();mat=p['attributes'].get('materialRaw','').lower()
 if sid=='pdf-01':return 'cup-carriers' if re.search(r'tray|carrier',name) else 'paper-bags' if re.search(r'kraft|paper',name) else 'plastic-bags'
 if sid in ['pdf-02','pdf-03']:return 'beverage-bottles'
 if sid=='pdf-04':return 'food-containers'
 if sid=='pdf-05':return 'cutlery' if p['sources'][0]['page']>=11 else 'dessert-jars' if 'jar' in name else 'food-containers'
 if sid=='pdf-06':return 'cup-accessories'
 if sid=='pdf-07':return 'can-lids' if p['sources'][0]['page']==8 else 'beverage-cans'
 if sid=='pdf-08':return 'straws'
 if sid=='pdf-09':return 'cup-lids'
 if sid=='pdf-10':return 'iml-cups'
 if sid=='pdf-11':return 'plastic-cups'
 if sid=='pdf-12':return 'paper-cups'
 if sid in ['pdf-13','pdf-14']:return 'cup-lids' if re.search(r'lid|insert',name) else 'dessert-jars' if re.search(r'dessert|bowl',name) else 'plastic-cups'
 return 'food-containers'
def materials(raw):
 vals=[]
 for mat in ['PET','PP','PS','PLA','PVC','AS','PE','OPS','CPET','RPET']:
  if re.search(r'\b'+mat+r'\b',raw,re.I):vals.append(mat.lower())
 if re.search(r'kraft',raw,re.I):vals.append('kraft-paper')
 elif re.search(r'cardstock|cardboard',raw,re.I):vals.append('paperboard')
 elif re.search(r'paper|pulp',raw,re.I):vals.append('paper')
 if re.search(r'aluminum',raw,re.I):vals.append('aluminum')
 return sorted(set(vals))
for p in cards:
 cat=category(p);p['categoryIds']=[cat];a=p['attributes'];en=p['name']['en'];p['materialIds']=materials(a.get('materialRaw',''));p['materialEvidence']='specification' if p['materialIds'] else None
 if not p['materialIds'] and re.search(r'\bPET\b|\bPP\b|\bPLA\b|\bAS\b',en,re.I):p['materialIds']=materials(en);p['materialEvidence']='product-name'
 if not p['materialIds'] and cat=='paper-cups':p['materialIds']=['paper'];p['materialEvidence']='catalog-title; coating unspecified'
 if cat in ['plastic-bags','paper-bags','cup-carriers'] and 'capacityMl' in a:a['compatibleCupCapacityMl']=a.pop('capacityMl')
 if 'dimensionsRaw' in a:
  raw=a['dimensionsRaw'];unit='cm' if re.search(r'\bcm\b',raw) else 'mm' if re.search(r'\bmm\b',raw) else None;vec=re.search(r'(\d+(?:\.\d+)?(?:\s*[x×*]\s*\d+(?:\.\d+)?){1,2})',raw)
  if unit and vec:a['dimensionValuesMm']=[float(x)*(10 if unit=='cm' else 1) for x in re.findall(r'\d+(?:\.\d+)?',vec.group())];a['dimensionAxisOrder']='unconfirmed'
 m=re.search(r'(-?\d+(?:\.\d+)?)\s*°?C\s*(?:to|[-–])\s*(-?\d+(?:\.\d+)?)\s*°?C',a.get('temperatureRaw',''),re.I)
 if m:a['temperatureRangeC']=[float(m.group(1)),float(m.group(2))]
 raw='\n'.join(p['specificationLines']);m=re.search(r'([\d,]+)\s*(pcs|sets)\s*/\s*(carton|pack|bag|bundle)',raw,re.I)
 if m:a['packing']={'quantity':int(m.group(1).replace(',','')),'unit':m.group(2).lower(),'container':m.group(3).lower()}
 p['proposedSolutionIds']=['food-beverage'];p['solutionMappingStatus']='proposed-from-catalog-use'
 p['sourceCardIds']=[p['id']]
# Merge exact duplicates only within WHYJ group; preserve every source and card ID.
unique={}
for p in cards:
 key=json.dumps([p['name']['en'].lower(),p['attributes'],p['specificationLines'],p['dimensionAnnotations']],sort_keys=True)
 if key in unique:
  unique[key]['sources'].extend(p['sources']);unique[key]['sourceCardIds'].append(p['id'])
 else:unique[key]=p
cards=list(unique.values())
# Reconcile strict suffix OCR fragments only where exactly one complete tuple exists.
for p in models:
 for v in list(p['variants']):
  parts=v['dimensionsRaw'].replace('Φ','').replace('Ø','').split('x')
  matches=[z for z in p['variants'] if z is not v and len(z['dimensionsRaw'].split('x'))>len(parts) and z['dimensionsRaw'].endswith('x'+v['dimensionsRaw'])]
  fulls={z['dimensionsRaw'] for z in matches}
  if len(fulls)==1:
   matches[0]['partialOcrSources']=matches[0].get('partialOcrSources',[])+v['sources'];p['variants'].remove(v)
 p['materialIds']=sorted({m.lower() for v in p['variants'] for m in v.get('materialOptionsFromHeader',[]) if len(v.get('materialOptionsFromHeader',[]))==1})
 p['materialAssignmentStatus']='from-single-material-table-header; review per variant' if p['materialIds'] else 'unconfirmed'
 p['proposedSolutionIds']=['food-beverage'];p['solutionMappingStatus']='proposed-from-catalog-section'
# Native table review of every Jihong ice-cream SKU, not carton-size inference.
ice=[
('JH-ICC-01','Vaso para helado 200 ml','Ice cream cup 200 ml',[85,70,54],[515,430,480],1500,8,5,{'capacityMl':200}),
('JH-ICC-02','Vaso para helado 250 ml','Ice cream cup 250 ml',[74,53,86],[600,390,500],2000,8,5,{'capacityMl':250}),
('JH-FRP-03','Bol de borde plano 390 ml','Flat-rim bowl 390 ml',[102,72,78],[630,530,580],1200,8,5,{'capacityMl':390}),
('JH-ICT-01','Cubeta para helado 6 L','Ice cream tub 6 L',[223,223,175],[691,469,605],18,9,6,{'capacityMl':6000}),
('JH-ICT-02','Cubeta para helado 7 L','Ice cream tub 7 L',[223,223,195],[691,469,545],18,9,6,{'capacityMl':7000}),
('JH-ICTL-01','Tapa para cubeta de helado','Ice cream tub lid',[227,28],None,None,9,6,{'dimensionAxisOrder':'diameter-height'}),
('JH-PCS-01','Funda de cono para helado 70 g','Ice cream cone sleeve 70 g',[64.5,165.5,22],[565,430,365],6600,9,6,{'dimensionAxisOrder':'top-diameter-slant-length-cone-angle; mm-mm-degrees','nominalServingMassG':70}),
('JH-PCS-02','Funda de cono para helado 73 g','Ice cream cone sleeve 73 g',[65.5,170,22],[565,430,365],6600,9,6,{'dimensionAxisOrder':'top-diameter-slant-length-cone-angle; mm-mm-degrees','nominalServingMassG':73}),
('JH-PCS-03','Funda de cono para helado 85 g','Ice cream cone sleeve 85 g',[58.15,150,22],[575,380,365],6600,9,6,{'dimensionAxisOrder':'top-diameter-slant-length-cone-angle; mm-mm-degrees','nominalServingMassG':85}),
('JH-PCS-07','Funda pequeña para cono de helado','Small ice cream cone sleeve',[41,106,22],[540,280,280],6600,9,6,{'dimensionAxisOrder':'top-diameter-slant-length-cone-angle; mm-mm-degrees'}),
('JH-PCSC-01','Tapa pequeña para funda de cono','Small cone sleeve lid',[38],[245,205,315],24000,9,6,{'dimensionAxisOrder':'diameter'}),
('JH-SSC-01','Vaso de forma especial 11 oz','Special-shaped cup 11 oz',[89,67,103],[465,375,300],500,10,7,{'nominalCapacityOz':11}),
('JH-ICB-01','Caja para helado número 1','Ice cream carton number 1',[145,70,177],[465,320,223],250,10,7,{'dimensionAxisOrder':'length-width-height'}),
('JH-ICB-02','Caja para helado número 2','Ice cream carton number 2',[176,65.5,132],[550,265,200],300,10,7,{'dimensionAxisOrder':'length-width-height'})]
for code,es,en,dims,carton,qty,p17,p18,extra in ice:
 p=next(r for r in models if r['modelCode']==code);p['name']={'en':en,'es':es};p['reviewedSpecifications']={'dimensionValues':dims,'dimensionAxisOrder':'top-diameter-bottom-diameter-height','unit':'mm','cartonDimensionsMm':carton,'quantityPerCarton':qty,'printingColorsMax':8,**extra};p['reviewedSpecificationsSources']=[{'sourceId':sid,'page':pg,'language':lang} for sid,pg,lang in [('pdf-17',p17,'en'),('pdf-17',p17+11,'es'),('pdf-18',p18,'en'),('pdf-18',p18+7,'es')]];p['reviewStatus']='native-specifications-reviewed; imagery-pending';p['variants']=[];p['materialIds']=['paper'];p['materialAssignmentStatus']='paperboard/laminate options in source; coating requires selection'
# Cling films are listed by width/roll length, not three product dimensions.
for mat,width,length,unit in [('pvc',30,400,'yd'),('pvc',35,400,'yd'),('pvc',35,300,'yd'),('pvc',45,400,'yd'),('pvc',35,500,'yd')]+[('pe',w,500,'m') for w in [25,30,35,40,45]]:
 rid=f'qunlu-film-{mat}-{width}-{length}-{unit}';models.append({'id':rid,'recordKind':'uncoded-product','supplierGroup':'QUNLU','modelCode':None,'name':{'es':f'Película {mat.upper()} {width} cm × {length} {unit}','en':f'{mat.upper()} cling film {width} cm × {length} {unit}'},'categoryIds':['cling-film'],'materialIds':[mat],'reviewedSpecifications':{'rollWidthMm':width*10,'rollLength':length,'rollLengthUnit':unit,'rollsPerCarton':6},'variants':[],'sources':[{'sourceId':'pdf-24','page':86,'language':'en'},{'sourceId':'pdf-25','page':86,'language':'es'}],'publicationStatus':'draft','reviewStatus':'visually-reviewed','imageStatus':'not-extracted','proposedSolutionIds':['food-beverage']})
write('products-cards.json',cards);write('products-models.json',models)
categories=[]
for cid,(es,en) in labels.items():
 refs=[p['id'] for p in cards+models+families if cid in p.get('categoryIds',[])];categories.append({'id':cid,'name':{'es':es,'en':en},'status':'proposed','recordIds':refs,'recordCount':len(refs),'note':'Taxonomía de inventario; no supone menú público aprobado.'})
write('categories-proposed.json',categories)
issues=[]
for p in cards+models:
 tags=[]
 if not p['name'].get('es') or not p['name'].get('en'):tags.append('missing-localized-name')
 if not p.get('materialIds'):tags.append('material-unconfirmed')
 if p.get('recordKind')=='uncoded-product' and p.get('reviewStatus')!='visually-reviewed':tags.append('uncoded-name-needs-visual-review')
 if p.get('variants') and len({v['dimensionsRaw'] for v in p['variants']})>1:tags.append('multiple-dimensions-or-ocr-conflict')
 if p.get('recordKind')=='supplier-model' and not p.get('variants') and not p.get('reviewedSpecifications'):tags.append('model-mention-without-readable-specifications')
 if tags:issues.append({'recordId':p['id'],'issues':tags})
write('review-issues.json',issues)
# Candidate cross-file duplicate groups: compare, never merge solely by dimensions.
groups=collections.defaultdict(list)
for p in cards+models:
 if p.get('attributes',{}).get('dimensionValuesMm'):groups[tuple(p['attributes']['dimensionValuesMm'])].append(p['id'])
 for v in p.get('variants',[]):
  if len(v.get('dimensionValuesCandidate',[]))>=2:groups[tuple(v['dimensionValuesCandidate'])].append(p['id'])
write('possible-duplicates.json',[{'dimensionValues':list(k),'recordIds':sorted(set(v)),'action':'compare model, material, color, structure and supplier; do not merge by size alone'} for k,v in groups.items() if len(set(v))>1])
print('cards',len(cards),'models',len(models),'families',len(families),'issues',len(issues))
