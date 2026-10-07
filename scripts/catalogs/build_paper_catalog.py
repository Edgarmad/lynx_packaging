"""Build the ES/EN paper catalog from audited local records and existing PDF photographs."""
import json, math, random, io
from pathlib import Path
from PIL import Image
import pymupdf
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'output/pdf'; TMP=ROOT/'tmp/pdfs/paper'
OUT.mkdir(parents=True,exist_ok=True);TMP.mkdir(parents=True,exist_ok=True)
D=json.loads((ROOT/'docs/catalog-review/paper/paper-catalog-content.json').read_text(encoding='utf-8-sig'))
S={s['id']:s for s in json.loads((ROOT/'docs/inventory/sources.json').read_text(encoding='utf-8-sig'))}
F={f['id']:f for f in D['supplierFamilies']+D['existingFamilySubtypes']}
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'));pdfmetrics.registerFont(TTFont('ArialB','C:/Windows/Fonts/arialbd.ttf'))
MM=72/25.4;W,H=210*MM,297*MM
NAVY=HexColor('#182037'); GOLD=HexColor('#c8ab65'); LIGHT=HexColor('#f3dfab'); WHITE=HexColor('#ffffff')
logo=Image.open(ROOT/'public/images/lynx-logo.png').convert('RGBA');logo=logo.crop(logo.getchannel('A').getbbox());LOGO=ImageReader(logo)
image_cache={}; audit=[]
def asset(id):
 if id in ISOLATED:return ISOLATED[id]['path']
 p=ROOT/'public/images/products'/f'{id}.webp'
 if not p.exists() and id.startswith('jihong-family-'):
  parent='-'.join(id.split('-')[:4]);p=ROOT/'public/images/products'/f'{parent}.webp'
 assert p.exists(),p
 return str(p)
def image_reader(p):
 if p not in image_cache:
  im=Image.open(p).convert('RGB');buf=io.BytesIO();im.save(buf,format='JPEG',quality=90,optimize=True);buf.seek(0);image_cache[p]=ImageReader(buf)
 return image_cache[p]
def num(n):return str(int(n)) if float(n).is_integer() else str(n)
def dims(ns):return ' x '.join(num(n) for n in ns)+' mm'
def tx(es,en):return {'es':es,'en':en}
# Individual product photographs taken from labelled source panels, without translation overlays.
ISOLATED={}
CLIPS={
 'jihong-family-c-1-burger':(18,[680,535,810,617]),
 'jihong-family-c-1-popcorn-chicken':(18,[856,534,984,615]),
 'jihong-family-c-1-pie':(18,[1036,535,1151,615]),
 'jihong-family-c-1-fries':(18,[695,657,795,738]),
 'jihong-family-c-1-egg-tart':(18,[857,683,983,737]),
 'jihong-family-c-1-takeaway':(18,[1020,664,1142,740]),
 'jihong-family-d-1-yogurt-auto-sleeve':(21,[71,537,158,610]),
 'jihong-family-d-1-yogurt-manual-sleeve':(21,[201,529,275,610]),
 'jihong-family-d-1-drinks-enclosed':(21,[309,532,414,611]),
 'jihong-family-d-1-beer-carrier':(21,[452,533,531,610]),
 'jihong-family-d-1-drinks-wrap':(21,[65,644,161,721]),
 'jihong-family-d-1-beer-enclosed':(21,[208,645,280,721]),
 'jihong-family-d-1-beer-auto-wrap':(21,[325,645,398,725]),
 'jihong-family-d-1-yogurt-base':(21,[443,654,541,722]),
 'jihong-family-c-3-noodle-bowl':(19,[678,534,820,611]),
 'jihong-family-c-3-snack-tray':(19,[1040,536,1140,609]),
 'jihong-family-c-3-soup-bowl':(19,[692,659,770,730]),
 'jihong-family-c-3-chicken-bucket':(19,[868,655,960,732]),
 'jihong-family-c-3-family-bucket':(19,[1038,641,1146,736]),
 'jihong-family-c-2-aluminum-foil':(19,[294,590,418,656]),
 'jihong-family-c-2-special-shape':(19,[424,588,545,658]),
}
individual_crop_ids=set(CLIPS)
source_media=json.loads((ROOT/'docs/inventory/website-media.json').read_text(encoding='utf-8-sig'))
for media in source_media:
 if media['productId'] in F and media['sourceId']=='pdf-15':CLIPS.setdefault(media['productId'],(media['page'],media['bbox']))
source_doc=pymupdf.open(S['pdf-15']['path']);original_pages={}
for id,(pg,clip) in CLIPS.items():
 if pg not in original_pages:
  info=max(source_doc[pg-1].get_image_info(xrefs=True),key=lambda v:(v['bbox'][2]-v['bbox'][0])*(v['bbox'][3]-v['bbox'][1]))
  original_pages[pg]=(Image.open(io.BytesIO(source_doc.extract_image(info['xref'])['image'])).convert('RGB'),info['bbox'])
 original,box=original_pages[pg];sx=original.width/(box[2]-box[0]);sy=original.height/(box[3]-box[1])
 pixels=[(clip[0]-box[0])*sx,(clip[1]-box[1])*sy,(clip[2]-box[0])*sx,(clip[3]-box[1])*sy]
 target=TMP/(id+'.png');original.crop(tuple(round(v) for v in pixels)).save(target)
 ISOLATED[id]={'path':str(target),'sourceId':'pdf-15','page':pg,'bbox':clip,'individualProductCrop':id in individual_crop_ids,'method':'Lossless crop of embedded original page raster; individual types matched to source panel labels.'}

# Extract the relevant photograph areas directly from the original ice-cream PDF.
ice_clips={'cups':(8,[238,291,404,388]),'bowl':(8,[44,659,400,777]),'tub':(9,[322,261,579,399]),'cone':(9,[310,614,423,800]),'cone-lid':(9,[201,740,299,785]),'snack':(10,[267,241,582,406]),'box':(10,[120,644,423,800])}
doc=pymupdf.open(S['pdf-17']['path'])
for key,(pg,rect) in ice_clips.items():
 p=TMP/f'ice-{key}.png';doc[pg-1].get_pixmap(matrix=pymupdf.Matrix(2,2),clip=pymupdf.Rect(rect)).save(p)
sections={s['id']:{'meta':s,'items':[]} for s in D['sections']}
def add(sec,id,name,image,details,ref=False,source=None):
 assert name.get('es') and name.get('en'),id
 sections[sec]['items'].append({'id':id,'name':name,'image':image,'details':details,'representativeImage':ref,'source':source})
def addfam(sec,f):
 op=f.get('options',{});lines=[]
 if op.get('paperWeightGsm'):lines.append(tx('Gramaje: '+'-'.join(map(str,op['paperWeightGsm']))+' g/m²','Paper weight: '+'-'.join(map(str,op['paperWeightGsm']))+' gsm'))
 if op.get('printingColorsMax'):lines.append(tx('Impresión: hasta '+str(op['printingColorsMax'])+' colores','Printing: up to '+str(op['printingColorsMax'])+' colors'))
 if not lines:lines=[tx('Formato personalizado según requerimiento','Customized format to suit requirements')]
 add(sec,f['id'],f['name'],asset(f['id']),lines,True,f['sources'])
addfam('corrugated',F['jihong-family-d-3'])
for key in ['jihong-family-d-2','jihong-family-c-4']:addfam('folding',F[key])
for f in D['existingFamilySubtypes']:
 if f['id'].startswith(('jihong-family-c-1-','jihong-family-d-1-')):addfam('folding',f)
# Each standard bag table row is retained, including the two supplier codes reused for different dimensions.
for b in D['bagTableRows']:
 s=b['sources'][0];pg=s['page'];right=s.get('bbox',[0])[0]>600
 family={13:'a-1-1',14:'a-1-3' if right else 'a-1-2',15:'a-2-2' if right else 'a-2-1',17:'b-2' if right else 'b-1'}[pg]
 f=F['jihong-family-'+family]
 add('bags',b['id'],f['name'],asset(f['id']),[tx('Modelo: '+b['code'],'Model: '+b['code']),tx('Medidas: '+dims(b['dimensionsMm']),'Dimensions: '+dims(b['dimensionsMm']))],True,b['sources'])
# Other source cards; keep optional straws and mixed elastic accessory out of the paper catalog.
container_cards=[]
for c in D['paperCandidateCards']:
 sid=c['sources'][0]['sourceId'];pg=c['sources'][0]['page'];a=c['attributes']
 if c['paperScope']!='paper-candidate':continue
 if sid=='pdf-04':container_cards.append(c);continue
 section='bags' if sid=='pdf-01' and pg==9 else 'complementary' if sid=='pdf-06' else 'containers'
 name=c['name'];lines=[]
 if sid=='pdf-06':
  idx=int(c['id'][-2:]);labels={2:tx('Funda decorativa de cartulina','Decorative paperboard sleeve'),3:tx('Funda para vasos','Cup sleeve'),4:tx('Funda decorativa de papel','Decorative paper sleeve'),5:tx('Accesorio de papel','Paper accessory')}
  if pg==3 and idx<=2:name=tx('Funda de kraft corrugado'+(' dorada' if idx==2 else ''),'Corrugated kraft sleeve'+(' - gold' if idx==2 else ''))
  elif pg==5:
   names={1:tx('Tarjetas azules para fundas','Blue sleeve cards'),2:tx('Tarjetas verdes para fundas','Green sleeve cards'),4:tx('Adornos florales de papel','Paper flower decorations'),5:tx('Adornos de frutas de papel','Paper fruit decorations'),6:tx('Funda para botella cuadrada','Square-bottle sleeve')};name=names[idx]
  else:name={l:labels[pg][l]+' - '+str(idx).zfill(2) for l in ['es','en']}
 if a.get('capacityMl') is not None:lines.append(tx('Capacidad: '+num(a['capacityMl'])+' ml','Capacity: '+num(a['capacityMl'])+' ml'))
 if a.get('rimDiameterMm') is not None:lines.append(tx('Diámetro superior: '+num(a['rimDiameterMm'])+' mm','Rim diameter: '+num(a['rimDiameterMm'])+' mm'))
 if a.get('dimensionsRaw'):lines.append(tx('Medidas declaradas: '+a['dimensionsRaw'],'Declared dimensions: '+a['dimensionsRaw']))
 if not lines:lines=[tx('Diseño y presentación de referencia','Reference design and presentation')]
 if sid=='pdf-01' and pg==9:
  idx=int(c['id'][-2:]);idx=(idx-1)%5
  measures=([[119,100,270],[210,110,270],[280,150,280],[250,135,270],[210,140,270]] if 'white' in c['name']['en'] else [[119,100,220],[210,110,270],[280,150,280],[250,135,270],[210,140,270]])[idx]
  lines=[tx('Ancho x fuelle x alto: '+dims(measures),'Width x gusset x height: '+dims(measures))]
 add(section,c['id'],name,asset(c['id']),lines,False,c['sources'])
for c in container_cards:
 label=c['name']['en'];r=next(r for r in D['restoredContainerPresentations'] if r['sourceLabel']==label)
 add('containers',c['id'],tx('Recipiente de papel '+label,'Paper container '+label),asset(c['id']),[tx('Capacidad: '+str(r['capacityMl'])+' ml','Capacity: '+str(r['capacityMl'])+' ml'),tx('Ø sup. x Ø inf. x alto: '+dims(r['dimensionsMm']),'Top Ø x base Ø x height: '+dims(r['dimensionsMm'])),tx('Opciones: blanco / kraft marrón','Options: white / brown kraft')],True,c['sources'])
for m in D['iceCreamModels']:
 code=m['code'];sp=m['specifications'];key='cone-lid' if 'PCSC' in code else 'cone' if 'PCS' in code else 'tub' if 'ICT' in code else 'box' if 'ICB' in code else 'snack' if 'SSC' in code else 'bowl' if 'FRP' in code else 'cups'
 lines=[tx('Modelo: '+code,'Model: '+code)]
 if 'capacityMl'in sp:lines.append(tx('Capacidad: '+str(sp['capacityMl'])+' ml','Capacity: '+str(sp['capacityMl'])+' ml'))
 vals=sp['dimensionValues'];axis=sp['dimensionAxisOrder']
 if 'cone-angle' in axis:lines.append(tx('Ø '+num(vals[0])+' mm; generatriz '+num(vals[1])+' mm; '+num(vals[2])+'°','Ø '+num(vals[0])+' mm; slant '+num(vals[1])+' mm; '+num(vals[2])+'°'))
 else:lines.append(tx('Medidas: '+dims(vals),'Dimensions: '+dims(vals)))
 add('containers',m['id'],m['name'],str(TMP/f'ice-{key}.png'),lines,True,m['sources'])
for f in D['existingFamilySubtypes']:
 if f['id'].startswith('jihong-family-c-3-') and not f['id'].endswith('ice-cream-bowl'):addfam('containers',f)
 if f['id'].endswith(('c-2-aluminum-foil','c-2-special-shape')):addfam('containers',f)
for key in ['jihong-family-c-5','jihong-family-c-6']:addfam('complementary',F[key])
# Group dimensional variants sharing a family photograph. Keep every original record in its table.
original_record_ids={r['id'] for sec in sections.values() for r in sec['items']}
bag_groups={};bag_others=[]
for r in sections['bags']['items']:
 if not r['id'].startswith('jihong-'):
  bag_others.append(r);continue
 b=next(v for v in D['bagTableRows'] if v['id']==r['id']);key=r['image']
 if key not in bag_groups:
  bag_groups[key]={**r,'id':'bag-group-'+Path(key).stem,'details':[],'variants':[],'tableKind':'bag'}
 bag_groups[key]['variants'].append({'id':b['id'],'code':b['code'],'values':dims(b['dimensionsMm']),'source':b['sources']})
sections['bags']['items']=list(bag_groups.values())+bag_others
addfam('bags',F['jihong-family-a-3'])
# The source picture includes tubs with their lid: one presentation with separate rows for both tub sizes and lid.
ice_groups={};container_others=[]
for r in sections['containers']['items']:
 if not r['id'].startswith('jihong-') or not any(v['id']==r['id'] for v in D['iceCreamModels']):
  container_others.append(r);continue
 m=next(v for v in D['iceCreamModels'] if v['id']==r['id']);sp=m['specifications'];key=r['image'];stem=Path(key).stem
 if key not in ice_groups:
  names={'ice-cups':tx('Vasos para helado','Ice cream cups'),'ice-cone':tx('Fundas para conos de helado','Ice cream cone sleeves'),'ice-tub':tx('Cubetas para helado y tapa','Ice cream tubs and lid'),'ice-box':tx('Cajas para helado','Ice cream cartons')}
  ice_groups[key]={**r,'id':'ice-group-'+stem,'name':names.get(stem,r['name']),'details':[],'variants':[],'tableKind':'ice'}
 rowvals=dims(sp['dimensionValues'])
 if 'cone-angle' in sp['dimensionAxisOrder']:rowvals=num(sp['dimensionValues'][0])+' / '+num(sp['dimensionValues'][1])+' mm / '+num(sp['dimensionValues'][2])+'°'
 caps={l:(num(sp['capacityMl'])+' ml' if 'capacityMl' in sp else '') for l in ['es','en']}
 ice_groups[key]['variants'].append({'id':r['id'],'code':m['code'],'values':rowvals,'capacity':caps,'source':r['source']})
# Only multi-model families need a variants table; standalone models keep their original technical caption.
for key,r in list(ice_groups.items()):
 if len(r['variants'])==1:
  original=next(v for v in sections['containers']['items'] if v['id']==r['variants'][0]['id']);ice_groups[key]=original
sections['containers']['items']=container_others+list(ice_groups.values())
covered_ids={v['id'] for sec in sections.values() for r in sec['items'] for v in r.get('variants',[{'id':r['id']}])}
assert original_record_ids.issubset(covered_ids)
# Resolve inherited capabilities without duplicating parent montages.
for sec in sections.values():
 for r in sec['items']:
  if r['id'] in ISOLATED:r['image']=ISOLATED[r['id']]['path'];r['representativeImage']=False
  if r['id'] in F and '-' in r['id'][len('jihong-family-'):]:
   parent='-'.join(r['id'].split('-')[:4]);op=F.get(parent,{}).get('options',{})
   if not F[r['id']].get('options') and op.get('paperWeightGsm'):
    r['details']=[tx('Gramaje: '+'-'.join(map(str,op['paperWeightGsm']))+' g/m²','Paper weight: '+'-'.join(map(str,op['paperWeightGsm']))+' gsm'),tx('Impresión: hasta '+str(op['printingColorsMax'])+' colores','Printing: up to '+str(op['printingColorsMax'])+' colors')]

# Mila, 6 October: paper cups belong in their separate cup catalog.
moved_cups=[]
for sec in sections.values():
 retained=[]
 for r in sec['items']:
  if r['id'].startswith('pdf-12-') or r['id'] in ['jihong-family-c-2-aluminum-foil','jihong-family-c-2-special-shape','ice-group-ice-cups']:
   moved_cups.append(r)
  else:retained.append(r)
 sec['items']=retained
moved_ids={v['id'] for r in moved_cups for v in r.get('variants',[{'id':r['id']}])}
original_record_ids-=moved_ids
covered_ids-=moved_ids
(OUT/'paper-cups-moved.json').write_text(json.dumps(moved_cups,ensure_ascii=False,indent=2),encoding='utf-8')
for sec in sections.values():assert len({r['id'] for r in sec['items']})==len(sec['items'])
# A reusable vector background gives the satin navy and fine grain finish without AI assets.
def background(c):
 c.beginForm('paperbg',0,0,W,H);c.setFillColor(HexColor('#171a20'));c.rect(0,0,W,H,fill=1,stroke=0)
 header_y=H-48*MM
 c.saveState();p=c.beginPath();p.rect(0,header_y,W,48*MM);c.clipPath(p,stroke=0,fill=0)
 for k in range(240):
  t=k/239;f=1-abs(t-.48)/.52;f=max(0,f);c.setFillColor(Color((17+26*f)/255,(24+33*f)/255,(39+44*f)/255));c.rect(k*W/240,header_y,W/240+.2,48*MM,fill=1,stroke=0)
 c.restoreState()
 rnd=random.Random(42)
 for i in range(4800):
  x=rnd.uniform(0,W);y=rnd.uniform(0,H);v=rnd.uniform(.08,.15) if y<header_y else rnd.uniform(.09,.2)
  c.setFillColor(Color(v,v+.008,v+.02));c.circle(x,y,.12,fill=1,stroke=0)
 c.setStrokeColor(GOLD);c.setLineWidth(.55);c.line(0,header_y,W,header_y)
 
 c.setFillColor(NAVY);c.rect(0,0,W,17*MM,fill=1,stroke=0);c.setStrokeColor(GOLD);c.line(0,17*MM,W,17*MM)
 c.endForm()
def para(c,text,x,y,w,size=10,leading=None,color=LIGHT,bold=False):
 text=text.replace('–','-').replace('—','-');style=ParagraphStyle('x',fontName='ArialB' if bold else 'Arial',fontSize=size,leading=leading or size*1.2,textColor=color)
 p=Paragraph(escape(text),style);_,h=p.wrap(w,1000);p.drawOn(c,x,y-h);return h

def frame(c,title,lang,page,total):
 c.doForm('paperbg');c.saveState();c.setFillAlpha(.035);c.drawImage(LOGO,150,290,width=300,height=200,preserveAspectRatio=True,mask='auto');c.restoreState();c.drawImage(LOGO,(W-170)/2,H-122,width=170,height=99,preserveAspectRatio=True,anchor='c',mask='auto')
 c.setFillColor(LIGHT);c.setFont('ArialB',19 if len(title)<35 else 16);c.drawCentredString(W/2,H-48*MM-25,title)
 c.setFont('Arial',6.4);c.setFillColor(HexColor('#d2c49c'));c.drawCentredString(W/2,H-48*MM-38,'PAPER PACKAGING | LYNX' if lang=='en' else 'EMPAQUES DE PAPEL | LYNX')
 c.setFillColor(LIGHT);c.setFont('Arial',7);c.drawString(12*MM,21,'Lynx Packaging Solutions');c.drawRightString(W-12*MM,21,f'{page:02d} / {total:02d}')

def intro(c,lang,page,total,index):
 frame(c,'Catálogo de papel' if lang=='es' else 'Paper catalog',lang,page,total)
 y=H-80*MM
 h=para(c,'Empaques de papel para distintas necesidades' if lang=='es' else 'Paper packaging for a range of needs',14*MM,y,W-28*MM,22,27,bold=True);y-=h+20
 text=('Bolsas, cajas, recipientes y complementos reunidos en cinco familias. Explora formatos, capacidades y opciones de personalización para tus productos.' if lang=='es' else 'Bags, boxes, containers and accessories arranged in five families. Explore formats, capacities and customization options for your products.')
 y-=para(c,text,14*MM,y,W-28*MM,11,16,color=WHITE)+25
 for sid,start,n in index:
  sec=sections[sid];c.setStrokeColor(GOLD);c.line(14*MM,y,W-14*MM,y);y-=24
  para(c,sec['meta']['title'][lang],14*MM,y,W-65*MM,12,15,bold=True);c.setFont('Arial',9);c.setFillColor(LIGHT);c.drawRightString(W-14*MM,y-10,('Página ' if lang=='es' else 'Page ')+str(start));y-=36
 y-=12
 c.showPage()

def span(r):return 2 if len(r.get('variants',[]))>2 or (r.get('tableKind')=='bag' and any(v['values'].count(' x ')==1 for v in r.get('variants',[]))) else 1

def paginate(records):
 pages=[];cells=[False]*8;page=[]
 for r in records:
  n=span(r);pos=None
  for slot in range(8):
   if cells[slot]:continue
   if n==1 or (slot<6 and not cells[slot+2]):pos=slot;break
  if pos is None:
   pages.append(page);page=[];cells=[False]*8;pos=0
  cells[pos]=True
  if n==2:cells[pos+2]=True
  page.append((r,pos,n))
 if page:pages.append(page)
 return pages

def gallery(c,lang,sid,placements,page,total):
 sec=sections[sid];frame(c,sec['meta']['title'][lang],lang,page,total)
 gap=3*MM;left=12*MM;top=H-70*MM;width=(W-24*MM-gap)/2;cell_height=(210*MM-3*gap)/4
 for r,slot,rows in placements:
  x=left+(slot%2)*(width+gap);height=rows*cell_height+(rows-1)*gap;y=top-(slot//2)*(cell_height+gap)-height
  c.setFillColor(NAVY);c.setStrokeColor(GOLD);c.setLineWidth(.55);c.rect(x,y,width,height,fill=1,stroke=1)
  picture_h=(36 if rows==2 else 24 if r.get('variants') else 28)*MM;py=y+height-picture_h
  c.setFillColor(HexColor('#f5f3ee'));c.rect(x+.4,py,width-.8,picture_h-.4,fill=1,stroke=0)
  c.drawImage(image_reader(r['image']),x+3*MM,py+2*MM,width=width-6*MM,height=picture_h-4*MM,preserveAspectRatio=True,anchor='c')
  c.saveState();c.setFillAlpha(.10);c.drawImage(LOGO,x+width-31*MM,py+2*MM,width=27*MM,height=16*MM,preserveAspectRatio=True,mask='auto');c.restoreState()
  cy=py-3*MM;th=para(c,r['name'][lang],x+3*MM,cy,width-6*MM,8.6,10,bold=True);cy-=th+3
  if r.get('variants'):
   bag=r['tableKind']=='bag'
   heading=('Medidas (mm)' if lang=='es' else 'Dimensions (mm)') if bag and any(v['values'].count(' x ')==1 for v in r['variants']) else 'A x F x H (mm)' if bag and lang=='es' else 'W x G x H (mm)' if bag else 'Medidas / capacidad' if lang=='es' else 'Dimensions / capacity'
   c.setFont('ArialB',6.2);c.setFillColor(GOLD);c.drawString(x+3*MM,cy-7,'Modelo' if lang=='es' else 'Model');c.drawString(x+26*MM,cy-7,heading);cy-=12
   for v in r['variants']:
    c.setStrokeColor(HexColor('#40506a'));c.setLineWidth(.2);c.line(x+3*MM,cy+2,x+width-3*MM,cy+2)
    c.setFont('Arial',6.1);c.setFillColor(WHITE);c.drawString(x+3*MM,cy-6,v['code'])
    value=v['values'].replace(' mm','') if bag else v['values'];cap=v.get('capacity',{}).get(lang,'')
    if cap:value+=' | '+cap
    # Two short lines if a model has a long dimension/capacity expression.
    cy-=max(10,para(c,value,x+26*MM,cy,width-29*MM,6.1,8,color=WHITE))
   if bag:
    cy-=3;cy-=para(c,('2 medidas: según fuente; 3: ancho x fuelle x alto' if lang=='es' else '2 values: as sourced; 3: width x gusset x height') if any(v['values'].count(' x ')==1 for v in r['variants']) else 'A: ancho; F: fuelle; H: alto' if lang=='es' else 'W: width; G: gusset; H: height',x+3*MM,cy,width-6*MM,5.9,7,color=GOLD)
  else:
   for line in r['details'][:3]:
    text=line[lang].replace('Medidas declaradas:','Medidas:').replace('Declared dimensions:','Dimensions:')
    if text in ['Diseño y presentación de referencia','Reference design and presentation']:continue
    cy-=para(c,text,x+3*MM,cy,width-6*MM,6.9,8.3,color=HexColor('#d9e0eb'))
  assert cy>=y+2,(lang,r['id'],'caption overflow',cy-y)
  covered=r.get('variants',[{'id':r['id'],'source':r['source']}])
  audit.append({'language':lang,'page':page,'recordId':r['id'],'coveredRecordIds':[v['id'] for v in covered],'image':r['image'],'source':r['source'],'variants':r.get('variants',[]),'isolatedPhoto':ISOLATED.get(r['id'])})
 c.showPage()

index=[];nextpage=2;pages_by_section={}
for sid,sec in sections.items():
 pages_by_section[sid]=paginate(sec['items']);n=len(pages_by_section[sid]);index.append((sid,nextpage,n));nextpage+=n
total=nextpage-1
for lang in ['es','en']:
 target=OUT/f'Lynx-Catalogo-Papel-{lang.upper()}.pdf';c=canvas.Canvas(str(target),pagesize=(W,H),pageCompression=1)
 c.setTitle('Lynx - '+('Catálogo de papel' if lang=='es' else 'Paper catalog'));c.setAuthor('Lynx Packaging Solutions');background(c);intro(c,lang,1,total,index)
 for sid,start,n in index:
  for i,placements in enumerate(pages_by_section[sid]):gallery(c,lang,sid,placements,start+i,total)
 c.save()
 with pymupdf.open(target) as check:
  assert len(check)==total
  whole=''.join(pg.get_text() for pg in check)
  for banned in ['VERSIÓN PARA REVISIÓN','REVIEW EDITION','Notas de esta edición','Edition notes','Imagen de referencia','Reference image','Sources used','Fuentes utilizadas']:assert banned not in whole,(lang,banned)
  for pg in check:
   assert pg.get_text().strip()
   for block in pg.get_text('dict')['blocks']:
    if block['type']==0:
     x0,y0,x1,y1=block['bbox'];assert x0>=-1 and x1<=W+1 and y0>=-1 and y1<=H+1,(target.name,pg.number,block['bbox'])
 print(target.name,total,'pages',target.stat().st_size,'bytes')
manifest={'date':'2026-10-06','revision':2,'languages':['es','en'],'recordCount':sum(len(s['items']) for s in sections.values()),'coveredSourceRecordCount':len(covered_ids),'recordsBySection':{k:len(s['items']) for k,s in sections.items()},'pageCountPerLanguage':total,'imagesPolicy':'Individual source-panel photos where available; shared dimensional family images shown once with all model rows. No AI.','variantTableCards':sum(bool(r.get('variants')) for sec in sections.values() for r in sec['items']),'isolatedPhotoCount':len(individual_crop_ids),'originalRasterCrops':len(ISOLATED),'coveredSourceIds':sorted(covered_ids),'assetsAndSources':audit}
assert original_record_ids.issubset(covered_ids)
(OUT/'Lynx-Catalogo-Papel-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in manifest.items() if k not in ['assetsAndSources','coveredSourceIds']},ensure_ascii=False))


