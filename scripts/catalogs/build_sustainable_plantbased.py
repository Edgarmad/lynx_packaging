"""Replace the mistaken Upack catalog using the supplied plant-based source."""
import json,re,hashlib,io,importlib.util,sys
from pathlib import Path
import pymupdf
from PIL import Image,ImageOps,ImageDraw
ROOT=Path(__file__).resolve().parents[2];TMP=ROOT/'tmp/pdfs/sustainable-plantbased';TMP.mkdir(parents=True,exist_ok=True)
SOURCE=Path('C:/Users/edmad/Downloads/SUSTAINABLE-Plantbased.pdf');DOC=pymupdf.open(SOURCE);SHA=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
tx=lambda es,en:{'es':es,'en':en}
SECTIONS={'bagasse':tx('Vajilla de bagazo de ca\u00f1a','Sugarcane pulp tableware'),'paper':tx('Cubiertos de papel','Paper cutlery'),'kraft':tx('Vajilla de papel kraft','Kraft paper tableware'),'corn':tx('Vajilla de almid\u00f3n de ma\u00edz','Corn starch tableware'),'industrial':tx('Empaques industriales de pulpa','Industrial pulp packaging')}
TRANS=[('Chinese soup spoon','Cuchara para sopa china'),('paper ice cream spoon','Cuchara de papel para helado'),('Single Wall Cup','Vaso de pared sencilla'),('Double Wall Cup','Vaso de doble pared'),('Corrugated cup','Vaso corrugado'),('round plate','Plato redondo'),('rippled plate','Plato de borde ondulado'),('round bowl','Bol redondo'),('Hexagonal bowl','Bol hexagonal'),('square plate','Plato cuadrado'),('Cake plate','Plato para pastel'),('triangle Pizza','Plato triangular para pizza'),('triangle plate','Plato triangular'),('Oval','ovalado'),('Clamshell','con tapa abatible'),('clamshell','con tapa abatible'),('container','Recipiente'),('plate','Plato'),('bowl','Bol'),('paper box','Caja de papel'),('french fry box','Caja para papas fritas'),('paper boat','Bandeja tipo barca'),('paper cup','Vaso de papel'),('bagasse cup','Vaso de bagazo'),('cup lid','Tapa para vaso'),('sushi box','Bandeja para sushi'),('salad','ensalada'),('Cheese','queso'),('Lock box','Envase con cierre'),('lock box','Envase con cierre'),('ice cream box','Envase para helado'),('Tray','Bandeja'),('tray','Bandeja'),('Paper Knife','Cuchillo de papel'),('Paper Fork','Tenedor de papel'),('Paper Spoon','Cuchara de papel'),('Knife','Cuchillo'),('knife','Cuchillo'),('fork','Tenedor'),('soup spoon','Cuchara para sopa'),('tea spoon','Cucharita'),('dessert spoon','Cuchara para postre'),('spoon','Cuchara'),('paper straw','Popote de papel'),('PLA straw','Popote PLA'),('sharp','con punta'),('lid','Tapa'),('compt','compartimentos'),('compartment','compartimentos'),('inch','pulgadas'),('round','redondo'),('square','cuadrado'),('rectangular','rectangular'),('with','con'),('mould','molde'),('Four gaid','4 compartimentos')]
TRANS += [('Clamshell box','Envase con tapa abatible'),('wide mouth','boca ancha'),('Chinese spoon','Cuchara china'),('box','Caja')]
TRANS += [('Kraft box with Window','Caja kraft con ventana'),('sauce cup','Vaso para salsas'),('soup cup','Vaso para sopa'),('Corn starch','Almid\u00f3n de ma\u00edz'),('wide mouth','boca ancha')]
def translate(en):
 s=en
 for a,b in sorted(TRANS,key=lambda x:-len(x[0])):s=re.sub(re.escape(a),b,s,flags=re.I)
 s=re.sub(r'^(\d+(?:\.\d+)?\s*pulgadas)\s+(.+)$',r'\2 de \1',s,flags=re.I)
 s=re.sub(r'^(\d+(?:/\d+)?)(ml|oz)\s+(.+)$',r'\3 de \1 \2',s,flags=re.I)
 return s[:1].upper()+s[1:]
TRANS += [('ripped plate','Plato de borde ondulado'),('soupcup','Vaso para sopa'),('packaged paper straw','Popote de papel envuelto'),('Food container','Recipiente para alimentos'),('Cup carrier','Portavasos'),('Window','ventana'),('Four gaid tray','Bandeja de 4 compartimentos'),('Semi-circular plate','Plato semicircular'),('Plate','Plato'),('Bowl','Bol'),('Straw','Popote'),('Paper cutlery','Cubiertos de papel'),('Corn starch cutlery','Cubiertos de almid\u00f3n de ma\u00edz')]
def clean(t):return t.replace('\u00d7',' x ').replace('*',' x ').replace('\uff1a',':').strip()
def cx(b):return (b[0]+b[2])/2
def cy(b):return (b[1]+b[3])/2
records=[];audit=[]
for pg in list(range(4,13))+[14,15,16,17,18,19,20,21,22,26]:
 lines=json.loads((ROOT/f'docs/inventory/ocr/sustainable-plantbased-{pg:03d}.json').read_text(encoding='utf-8'))['lines']
 anchors=[(re.search(r'[AB][0-9O]{7}',l['text']).group(0).replace('O','0'),l['bbox']) for l in lines if re.search(r'[AB][0-9O]{7}',l['text'])]
 section='bagasse' if pg<=12 else 'paper' if pg==14 else 'kraft' if pg in [15,16,17,18,26] else 'corn'
 infos=[]
 for inf in DOC[pg-1].get_image_info(xrefs=True):
  b=inf['bbox'];area=(b[2]-b[0])*(b[3]-b[1])
  if inf['xref'] and 250<area<150000 and not any(inf['xref']==v['xref'] and tuple(b)==tuple(v['bbox']) for v in infos):infos.append(inf)
 for idx,(code,b) in enumerate(anchors):
  others=[a[1][1] for a in anchors if a[1][1]>b[1]+10 and abs(a[1][0]-b[0])<40];end=min(others+[b[1]+110])
  local=[l for l in lines if b[1]+7<=l['bbox'][1]<end-3 and abs(l['bbox'][0]-b[0])<45];local.sort(key=lambda x:x['bbox'][1])
  descriptions=[l['text'].split(':',1)[-1].strip() for l in local if re.match(r'Description\s*:',l['text'],re.I)]
  en=next((x for x in descriptions if x),'')
  if not en:
   en={4:'Plate',5:'Plate',6:'Round bowl',7:'Bowl',8:'Clamshell box',9:'Food container',10:'Food container',11:'Straw',12:'Cup carrier' if cx(b)>600 else 'Bagasse cup',14:'Paper cutlery',15:'Paper bowl',16:'Paper box',17:'Paper cup',18:'Paper bowl',19:'Round bowl',20:'Tray or lock box',21:'Food container',22:'Corn starch cutlery',26:'Sushi box'}[pg]
  en=re.sub(r'\s+',' ',en).strip();specs=[]
  for l in local:
   t=clean(l['text'])
   if re.match('Specification:',t,re.I):
    value=t.split(':',1)[1].strip();pack=re.search(r'\d+\s*pcs\s*/\s*CTN',value,re.I)
    if pack:value=value[:pack.start()].strip();specs.append(tx('Empaque: '+pack.group().replace('pcs','piezas').replace('CTN','caja'),'Packing: '+pack.group()))
    if value and re.search(r'\d',value):specs.append(tx('Medidas: '+value,'Dimensions: '+value))
  if pg==6:
   pairs={'A0102001':[117],'A0102002':[119,121],'A0102007':[105,107],'A0102003':[101,103],'A0102004':[99,111],'A0102005':[113,111],'A0102006':[115,111],'A0102030':[109]}
   options=[x for x in infos if x['xref'] in pairs[code] and abs(cx(x['bbox'])-(820 if b[0]<800 else 1070))<90]
   inf=options[0]
  elif pg==12 and code in ['A0106001','A0106003']:
   options=[x for x in infos if x['xref'] in ([252,254] if code=='A0106001' else [252,272]) and abs(cx(x['bbox'])-(210 if code=='A0106001' else 480))<80];inf=options[0]
  elif pg==17:
   inf=infos[0 if code.startswith('A0502') else 1 if code.startswith('A0503') else 2]
  elif pg==14:
   xref=369 if code.startswith('A0201') else 379 if code.startswith('A0202') else 381 if code.startswith('A0203') else 375 if code.startswith('A0204') else 377
   inf=next(x for x in infos if x['xref']==xref)
  elif pg==22:
   pairs={'B0105002':590,'B0105003':588,'B0106002':586,'B0106003':584,'B0107005':592,'B0107003':594,'B0107006':579,'B0107007':576,'B0107004':573};inf=next(x for x in infos if x['xref']==pairs[code])
  else:
   def score(inf):
    ib=inf['bbox'];above=((cx(ib)-(b[0]+45))/1.1)**2+(ib[3]-b[1]+8)**2
    if cx(ib)<b[0] and b[1]-60<cy(ib)<b[1]+80:above=min(above,(b[0]-ib[2])**2+(cy(ib)-b[1]-25)**2)
    return above
   inf=min(infos,key=score)
  target=TMP/f'photo-{inf["xref"]}.png'
  raw=DOC.extract_image(inf['xref']);im=Image.open(io.BytesIO(raw['image'])).convert('RGBA')
  if raw.get('smask'):im.putalpha(Image.open(io.BytesIO(DOC.extract_image(raw['smask'])['image'])).convert('L'))
  bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);bg.convert('RGB').save(target)
  if pg==14 and code.startswith(('A0203','A0204')):
   rect=[105,340,225,485] if code.startswith('A0203') else [120,550,225,670];target=TMP/('paper-spoon-family.png' if code.startswith('A0203') else 'paper-ice-spoon-family.png');DOC[pg-1].get_pixmap(matrix=pymupdf.Matrix(3,3),clip=pymupdf.Rect(rect)).save(target);inf={**inf,'bbox':rect}
  if pg==6 or (pg==12 and code in ['A0106001','A0106003']):
   boxes=[x['bbox'] for x in options];rect=[min(x[0] for x in boxes),min(x[1] for x in boxes),max(x[2] for x in boxes),max(x[3] for x in boxes)];target=TMP/f'composite-{pg}-{code}.png';DOC[pg-1].get_pixmap(matrix=pymupdf.Matrix(3,3),clip=pymupdf.Rect(rect)).save(target);inf={**inf,'bbox':rect}
  material=tx('Pulpa de ca\u00f1a','Sugarcane pulp') if section=='bagasse' else tx('Papel','Paper') if section=='paper' else tx('Papel kraft','Kraft paper') if section=='kraft' else tx('Almid\u00f3n de ma\u00edz','Corn starch')
  if 'pp lid' in en.lower():material=tx('PP','PP')
  elif code.startswith('B080'):material=tx('PLA','PLA')
  elif 'pet' in en.lower():material=tx('PET','PET')
  elif 'paper straw' in en.lower():material=tx('Papel','Paper')
  r={'id':f'sustainable-p{pg:02d}-{idx+1:02d}','coveredIds':[f'sustainable-p{pg:02d}-{idx+1:02d}'],'name':tx(translate(en)+' | '+code,en+' | '+code),'image':str(target),'details':[tx('Material: '+material['es'],'Material: '+material['en'])]+specs,'variants':[],'sectionId':section,'sectionTitle':SECTIONS[section],'source':{'sourceId':'sustainable-plantbased','page':pg,'bbox':list(inf['bbox']),'code':code,'captionBBox':b,'description':en,'sourceSha256':SHA}}
  records.append(r)
# Original industrial examples; no supplier claims or client logos.
industrial=[(602,'Inserto industrial','Industrial insert'),(607,'Inserto para productos premium','Premium product insert'),(606,'Bandeja para productos agr\u00edcolas','Agricultural product tray'),(603,'Protecci\u00f3n para electr\u00f3nica','Electronics protective packaging'),(601,'Inserto para aparatos m\u00e9dicos','Medical appliance insert'),(604,'Bandeja para art\u00edculos cotidianos','Everyday-product tray'),(605,'Protecci\u00f3n para artesan\u00edas','Arts and crafts protective packaging')]
for i,(xref,es,en) in enumerate(industrial):
 target=TMP/f'industrial-{i+1}.png';raw=DOC.extract_image(xref);Image.open(io.BytesIO(raw['image'])).convert('RGB').save(target)
 inf=next(x for x in DOC[22].get_image_info(xrefs=True) if x['xref']==xref)
 pid=f'sustainable-industrial-{i+1}';records.append({'id':pid,'coveredIds':[pid],'name':tx(es,en),'image':str(target),'details':[],'variants':[],'sectionId':'industrial','sectionTitle':SECTIONS['industrial'],'source':{'sourceId':'sustainable-plantbased','page':23,'bbox':list(inf['bbox']),'sourceSha256':SHA}})
records.sort(key=lambda r:list(SECTIONS).index(r['sectionId']))
(TMP/'prepared-records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for start in range(0,len(records),30):
 sheet=Image.new('RGB',(1500,1500),'white');draw=ImageDraw.Draw(sheet)
 for j,r in enumerate(records[start:start+30]):
  x=(j%5)*300;y=(j//5)*250;im=ImageOps.contain(Image.open(r['image']),(280,160));sheet.paste(im,(x,y));draw.text((x,y+164),r['id']+' '+r['source'].get('code',''),fill='black');draw.text((x,y+182),r['name']['en'][:42],fill='black');draw.text((x,y+204),'source p'+str(r['source']['page']),fill='black')
 sheet.save(TMP/f'products-review-{start//30+1}.jpg')
print('Prepared',len(records),'source records; image review sheets created.',flush=True)
if '--author' in sys.argv:
 spec=importlib.util.spec_from_file_location('renderer',ROOT/'scripts/catalogs/build_all_catalogs.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 mainpath=ROOT/'output/pdf/Lynx-Todos-Catalogos-manifest.json';previous=json.loads(mainpath.read_text(encoding='utf-8'))
 cfg={'id':'sustainable','sourceIds':['sustainable-plantbased'],'filename':'Sostenible','title':tx('Empaques sostenibles','Sustainable packaging'),'group':tx('EMPAQUES SOSTENIBLES | LYNX','SUSTAINABLE PACKAGING | LYNX'),'includeIntro':False,'sectioned':True,'revision':2,'revisedAt':'2026-10-12'}
 m.author(cfg,records)
 new=m.manifest['catalogs'][-1];previous['catalogs']=[new if c['id']=='sustainable' else c for c in previous['catalogs']];mainpath.write_text(json.dumps(previous,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (ROOT/'output/pdf/Lynx-Catalogo-Sostenible-manifest.json').write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
