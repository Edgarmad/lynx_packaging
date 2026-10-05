import json,re,hashlib,collections
from pathlib import Path
OUT=Path('docs/inventory')
codepat=re.compile(r'\b(?:JH[A-Z]{2,}\d+|JH-[A-Z]+-\d+|(?:SR|TS)\d+[A-Z0-9]*|(?:DW|XY|OHM)[ -]+[A-Z0-9-]+|(?:GHW|QL|XL|SR|GH)[A-Z0-9]*[- ][A-Z0-9][A-Z0-9./()_-]*(?:T/B|L/B)?|QL\d{2,3}-\d+(?:OZ|Z))',re.I)
dimpat=re.compile(r'(?:[ØΦ]?\d+(?:\.\d+)?\s*[*xX×]\s*){1,3}[\d.]+(?:°)?')
def clean(t):return re.sub(r'\s+',' ',t).strip()
def cy(l):return (l['bbox'][1]+l['bbox'][3])/2
def cx(l):return (l['bbox'][0]+l['bbox'][2])/2
def category(sid,p,text):
 if sid in ['pdf-15','pdf-16']:return 'paper-bags'
 if sid in ['pdf-17','pdf-18']:return 'ice-cream-packaging'
 if sid=='pdf-20':
  return 'food-containers' if p<=4 else 'cold-noodle-containers' if p<=8 else 'meat-trays' if p<=17 else 'skin-pack-trays' if p<=22 else 'map-trays' if p<=30 else 'frozen-food-containers'
 if sid=='pdf-21':return 'fruit-vegetable-containers'
 if sid=='pdf-22':return 'bakery-containers'
 if sid=='pdf-23':return 'plastic-cups'
 if sid in ['pdf-24','pdf-25']:
  if p<=6:return 'food-containers'
  if p<=10:return 'cold-noodle-containers'
  if p<=15:return 'plastic-cups'
  if p<=37:return 'meat-trays'
  if p<=49:return 'bakery-containers'
  if p<=65:return 'fruit-vegetable-containers'
  if p<=72:return 'cut-fruit-containers'
  if p<=77:return 'salad-containers'
  if p<=84:return 'food-trays'
  if p==85:return 'egg-containers'
  if p==86:return 'cling-film'
  return 'non-product-content'
 return 'unclassified'
records={};unnamed=[];coverage=[]
for f in sorted((OUT/'ocr').glob('*.json')):
 d=json.loads(f.read_text(encoding='utf8'));sid=d['sourceId'];p=d['page']
 if int(sid[-2:])<15:continue
 if sid in ['pdf-15','pdf-16'] and p<13:continue
 if sid in ['pdf-24','pdf-25'] and p>=86:continue
 ls=d['lines'];w=d['width'];h=d['height'];text='\n'.join(l['text'] for l in ls);cat=category(sid,p,text);sup='JIHONG' if int(sid[-2:])<=18 else 'QUNLU';lang='es' if sid=='pdf-25' else 'en';found=[]
 def put(model,ev,dim=None):
  model=clean(model);code=codepat.search(model);key=(sup,code.group().upper().replace(' ','-') if code else model.lower())
  # Align uncoded translations by the position of their row in paired master files.
  if sid=='pdf-25':
   pairs=[]
   for prior_key,prior in records.items():
    for ref in prior['sources']:
     if ref['sourceId']=='pdf-24' and ref['page']==p:
      distance=abs((ref['bbox'][0]+ref['bbox'][2])/2-cx(ev))/w+abs((ref['bbox'][1]+ref['bbox'][3])/2-cy(ev))/h
      if distance<.02:pairs.append((distance,prior_key))
   if pairs:
    prior_key=min(pairs)[1]
    if not code or prior_key[1]==key[1]:key=prior_key
  rid=sup.lower()+'-'+hashlib.sha1(key[1].encode()).hexdigest()[:12]
  rec=records.setdefault(key,{'id':rid,'recordKind':'supplier-model' if code else 'uncoded-product','supplierGroup':sup,'modelCode':key[1] if code else None,'name':{'en':None,'es':None},'categoryIds':[],'variants':[],'sources':[],'publicationStatus':'draft','reviewStatus':'ocr-needs-review','imageStatus':'not-extracted'})
  if cat not in rec['categoryIds']:rec['categoryIds'].append(cat)
  if not rec['name'][lang]:rec['name'][lang]=model
  ref={'sourceId':sid,'page':p,'language':lang,'bbox':ev['bbox'],'raw':ev['text'],'confidence':ev['confidence']}
  if ref not in rec['sources']:rec['sources'].append(ref)
  if dim:
   raw=dim['dimensionsRaw'];existing=next((v for v in rec['variants'] if v['dimensionsRaw']==raw and v['modelLabelRaw'].upper()==model.upper()),None)
   if existing:existing['sources'].append(ref)
   else:rec['variants'].append({**dim,'modelLabelRaw':model,'sources':[ref],'reviewStatus':'ocr-needs-review'})
  found.append(rid)
 # Tables: dimension tuple with model immediately to its left on same row.
 for l in ls:
  m=dimpat.search(l['text'])
  if not m:continue
  # Do not treat inch dimensions as a second metric specification.
  if '"' in l['text'] or 'inches' in l['text'].lower():continue
  x=cx(l);y=cy(l);lo=0 if x<w/2 else w/2;hi=w/2 if x<w/2 else w
  same=[z for z in ls if lo<cx(z)<hi and abs(cy(z)-y)<max(3,h*.004)]
  before=[z for z in same if z['bbox'][2]<=l['bbox'][0]+w*.008 and not re.fullmatch(r'[\d.,\s√Vv-]+',z['text'])]
  model=next((z for z in sorted(before,key=lambda z:z['bbox'][2],reverse=True) if codepat.search(z['text'])),None)
  if model is None:
   model=next((z for z in sorted(before,key=lambda z:z['bbox'][2],reverse=True) if len(z['text'])>3 and not re.search(r'width|size|length|Height|Product|Material|Paper|Weight|ranges|gsm|recommended|mm|g/m|Layer|foil|Kraft|Carton|^Inner:|^Box:|^Salad$|^Egg Boxes$|^Delivery$|^GHW-$',z['text'],re.I)),None)
  if model is None:continue
  intervening=[z for z in same if dimpat.search(z['text']) and z['bbox'][0]>model['bbox'][2] and z['bbox'][0]<l['bbox'][0]]
  if intervening:continue
  # metric dimension tables are mainly below midpoint; Jihong bag tables below 70%.
  table_headers=[z for z in ls if lo<cx(z)<hi and cy(z)<y and re.search(r'^(Model|Modelo|ITEM CODE|Product code|Item Code|Código)',z['text'],re.I)]
  if y<h*.60 and not table_headers:continue
  row=sorted(same,key=lambda z:z['bbox'][0]);raw=m.group().replace('X','x').replace('×','x').replace('*','x').replace(' ','')
  attr={'dimensionsRaw':raw,'dimensionValuesCandidate':[float(v) for v in re.findall(r'\d+(?:\.\d+)?',raw)],'unit':'mm','axisOrder':'unconfirmed','rowCells':[{'text':z['text'],'bbox':z['bbox'],'confidence':z['confidence']} for z in row]}
  # A material header with only one polymer applies to this half table, unlike PP/PET options.
  headers=[z for z in ls if lo<cx(z)<hi and cy(z)<y and re.search(r'Material|Materiales',z['text'],re.I)]
  if headers:
   hdr=max(headers,key=cy)['text'];pol=re.findall(r'\b(?:PET|PP|PS|OPS|PLA|PVC|RPET|CPET)\b',hdr,re.I);attr['materialOptionsFromHeader']=sorted(set(a.upper() for a in pol));attr['materialHeaderRaw']=hdr
  put(model['text'],model,attr)
 # Card format: model followed by its size, pack count etc. Capture code mentions even when table OCR fails.
 for l in ls:
  codes=list(codepat.finditer(l['text']))
  if not codes:continue
  for m in codes:
   if not re.search(r'\d',m.group()):continue
   model=l['text'] if len(codes)==1 else m.group();x=cx(l);y=cy(l)
   below=[z for z in ls if 0<cy(z)-y<h*.08 and abs(cx(z)-x)<w*.055 and re.search(r'size:|ctn:|slv:|tamaño|caja:|尺寸',z['text'],re.I)]
   size=next((z for z in below if dimpat.search(z['text'])),None)
   attr=None
   if size:
    raw=dimpat.search(size['text']).group().replace('X','x').replace('×','x').replace('*','x').replace(' ','');attr={'dimensionsRaw':raw,'dimensionValuesCandidate':[float(v) for v in re.findall(r'\d+(?:\.\d+)?',raw)],'unit':'mm','axisOrder':'unconfirmed','cardSpecificationLines':[z['text'] for z in below]}
   put(model,l,attr)
 coverage.append({'sourceId':sid,'page':p,'categoryId':cat,'detectedRecordIds':sorted(set(found)),'ocrLineCount':len(ls)})
(OUT/'products-models.json').write_text(json.dumps(list(records.values()),ensure_ascii=False,indent=2),encoding='utf8');(OUT/'page-coverage-models.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf8')
print('Models',len(records),'variants',sum(len(r['variants']) for r in records.values()));print(collections.Counter(c for r in records.values() for c in r['categoryIds']))
