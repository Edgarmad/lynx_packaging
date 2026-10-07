"""Build batch 1 from source photographs and reviewed bilingual card specifications."""
import hashlib
import io
import json
import math
import random
import re
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

import pymupdf
from PIL import Image, ImageDraw
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/pdf';TMP=ROOT/'tmp/pdfs/lote-1';DOC=ROOT/'docs/catalog-review/lote-1'
for p in [OUT,TMP,DOC]:p.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
cards=read(ROOT/'docs/inventory/products-cards.json')
media={m['productId']:m for m in read(ROOT/'docs/inventory/website-media.json')}
sources={s['id']:s for s in read(ROOT/'docs/inventory/sources.json')}
MM=72/25.4;W,H=210*MM,297*MM
NAVY=HexColor('#182037');GOLD=HexColor('#c8ab65');LIGHT=HexColor('#f3dfab');WHITE=HexColor('#ffffff')
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialB','C:/Windows/Fonts/arialbd.ttf'))
logo=Image.open(ROOT/'public/images/lynx-logo.png').convert('RGBA');logo=logo.crop(logo.getchannel('A').getbbox());LOGO=ImageReader(logo)
image_cache={}
def n(v):return str(int(v)) if float(v).is_integer() else str(v)
def tx(es,en):return {'es':es,'en':en}
configs=[
 {'id':'cups-10','sourceId':'pdf-10','filename':'Vasos-IML','title':tx('Vasos IML','IML cups'),'intro':tx('Acabados tornasol, plateados, dorados y de color en distintos formatos y capacidades.','Rainbow, silver, gold and colored finishes in a range of formats and capacities.'),'families':tx('Tornasol brillante y mate\nPlateado brillante y mate\nDorado brillante y mate\nNaranja y diseños rojo/azul\nNegro y amarillo mate','Glossy and matte rainbow\nGlossy and matte silver\nGlossy and matte gold\nOrange and red/blue designs\nMatte black and yellow')},
 {'id':'cups-11','sourceId':'pdf-11','filename':'Vasos-Inyeccion','title':tx('Vasos por inyección','Injection-molded cups'),'intro':tx('Vasos transparentes y esmerilados, modelos con base elevada, formatos en U, cubetas y otras formas.','Clear and frosted cups, raised-base models, U-shaped formats, buckets and other shapes.'),'families':tx('Transparentes y esmerilados\nBase elevada y vasos rectos\nVasos en U\nCubetas con y sin cierre\nFormatos especiales','Clear and frosted\nRaised bases and straight cups\nU-shaped cups\nLocking and non-locking buckets\nSpecial shapes')},
 {'id':'cups-13','sourceId':'pdf-13','filename':'Vasos-Tapas-PET','title':tx('Vasos y tapas PET','PET cups and lids'),'intro':tx('Vasos, tazones y tapas PET en formatos transparentes y ahumados. Consulta las medidas y características de cada referencia.','PET cups, bowls and lids in clear and smoke finishes. Explore the dimensions and specifications of each reference.'),'families':tx('Vasos transparentes\nTapas planas, domo y para beber\nVasos y tapas ahumados\nTazones y tapas de 117 mm','Clear cups\nFlat, dome and sip lids\nSmoke cups and lids\n117 mm bowls and lids')},
]
style_names={
 'pdf-13-p04-c07':tx('98-16oz A | Estilo para té','98-16oz A | Tea-style cup'),
 'pdf-13-p04-c08':tx('98-16oz B | Estilo para café','98-16oz B | Coffee-style cup'),
 'pdf-13-p04-c09':tx('98-16oz B | Estilo reforzado para café','98-16oz B | Heavy-duty coffee-style cup'),
 'pdf-11-p07-c06':tx('1000 ml | Cubeta con cierre, tapa verde','1000 ml | Locking bucket, green lid'),
 'pdf-11-p07-c07':tx('1000 ml | Cubeta sin cierre, tapa verde','1000 ml | Non-locking bucket, green lid'),
 'pdf-10-p04-c07':tx('700 ml | Dorado brillante, variante 2','700 ml | Glossy gold, variant 2'),
}

def details(r):
 a=r['attributes'];lines=[]
 common=[]
 if a.get('materialRaw'):common.append(tx('Material: '+a['materialRaw'],'Material: '+a['materialRaw']))
 if 'rimDiameterMm' in a:common.append(tx('Boca: '+n(a['rimDiameterMm'])+' mm','Rim: '+n(a['rimDiameterMm'])+' mm'))
 if common:lines.append(tx(' | '.join(x['es'] for x in common),' | '.join(x['en'] for x in common)))
 common=[]
 if 'capacityMl' in a:common.append(tx('Capacidad: '+n(a['capacityMl'])+' ml','Capacity: '+n(a['capacityMl'])+' ml'))
 if 'weightG' in a:common.append(tx('Peso: '+n(a['weightG'])+' g','Weight: '+n(a['weightG'])+' g'))
 if common:lines.append(tx(' | '.join(x['es'] for x in common),' | '.join(x['en'] for x in common)))
 temp=a.get('temperatureRangeC')
 if not temp:
  raw=next((s for s in r['specificationLines'] if 'Temperature:' in s),'')
  numbers=re.findall(r'-?\d+(?:\.\d+)?',raw)
  if len(numbers)==2:temp=list(map(float,numbers))
 if temp:lines.append(tx(f'Temperatura: {n(temp[0])} a {n(temp[1])} °C',f'Temperature: {n(temp[0])} to {n(temp[1])} °C'))
 packing=a.get('packing')
 if packing:lines.append(tx(n(packing['quantity'])+' piezas/caja',n(packing['quantity'])+' pcs/carton'))
 dim=[];lid_height=None;top_values=[]
 for annotation in r.get('dimensionAnnotations',[]):
  match=re.search(r'Lid H\s+(\d+(?:\.\d+)?)\s*mm',annotation)
  if match:
   lid_height=match[1];continue
  match=re.search(r'Top\s+(\d+(?:\.\d+)?)\s*mm',annotation)
  if match:top_values.append(match[1]);continue
  match=re.search(r'Base\s+(\d+(?:\.\d+)?)\s*mm',annotation)
  if match:dim.append(tx('Base: '+match[1]+' mm','Base: '+match[1]+' mm'))
  match=re.search(r'\bH\s+(\d+(?:\.\d+)?)\s*mm',annotation)
  if match:dim.append(tx('Altura: '+match[1]+' mm','Height: '+match[1]+' mm'))
 if top_values:dim.insert(0,tx('Parte superior: '+' x '.join(top_values)+' mm','Top: '+' x '.join(top_values)+' mm'))
 if dim:lines.append(tx(' | '.join(x['es'] for x in dim),' | '.join(x['en'] for x in dim)))
 for extra in r['specificationLines']:
  if extra=='Large white lid: 8.8 g':lines.append(tx('Tapa blanca: 8,8 g'+(' | Altura: '+lid_height+' mm' if lid_height else ''),'White lid: 8.8 g'+(' | Height: '+lid_height+' mm' if lid_height else '')))
  if extra=='Lid: clear':lines.append(tx('Tapa: transparente','Lid: clear'))
  if extra=='Lid: green':lines.append(tx('Tapa: verde','Lid: green'))
 return lines

def get_para(text,width,size=8,leading=9.5,bold=False,color=LIGHT):
 style=ParagraphStyle('card',fontName='ArialB' if bold else 'Arial',fontSize=size,leading=leading,textColor=color)
 p=Paragraph(escape(text.replace('–','-').replace('—','-')),style);_,h=p.wrap(width,1000);return p,h
def para(c,text,x,y,w,size=8,leading=9.5,bold=False,color=LIGHT):
 p,h=get_para(text,w,size,leading,bold,color);p.drawOn(c,x,y-h);return h

def background(c):
 c.beginForm('lynxbg',0,0,W,H);c.setFillColor(HexColor('#171a20'));c.rect(0,0,W,H,fill=1,stroke=0)
 for k in range(240):
  f=max(0,1-abs(k/239-.48)/.52);c.setFillColor(Color((17+26*f)/255,(24+33*f)/255,(39+44*f)/255));c.rect(k*W/240,H-48*MM,W/240+.2,48*MM,fill=1,stroke=0)
 rnd=random.Random(42)
 for _ in range(4800):
  x=rnd.uniform(0,W);y=rnd.uniform(0,H);v=rnd.uniform(.08,.15) if y<H-48*MM else rnd.uniform(.09,.2)
  c.setFillColor(Color(v,v+.008,v+.02));c.circle(x,y,.12,fill=1,stroke=0)
 c.setStrokeColor(GOLD);c.setLineWidth(.55);c.line(0,H-48*MM,W,H-48*MM)
 c.setFillColor(NAVY);c.rect(0,0,W,17*MM,fill=1,stroke=0);c.line(0,17*MM,W,17*MM);c.endForm()

def frame(c,cfg,lang,page,total):
 c.doForm('lynxbg');c.saveState();c.setFillAlpha(.035);c.drawImage(LOGO,150,290,width=300,height=200,preserveAspectRatio=True,mask='auto');c.restoreState()
 c.drawImage(LOGO,(W-170)/2,H-122,width=170,height=99,preserveAspectRatio=True,anchor='c',mask='auto')
 title=cfg['title'][lang];c.setFillColor(LIGHT);c.setFont('ArialB',19 if len(title)<35 else 16);c.drawCentredString(W/2,H-48*MM-25,title)
 c.setFont('Arial',6.4);c.drawCentredString(W/2,H-48*MM-38,'VASOS Y ACCESORIOS | LYNX' if lang=='es' else 'CUPS AND ACCESSORIES | LYNX')
 c.setFont('Arial',7);c.drawString(12*MM,21,'Lynx Packaging Solutions');c.drawRightString(W-12*MM,21,f'{page:02d} / {total:02d}')

def cover(c,cfg,lang,total):
 frame(c,cfg,lang,1,total);x=14*MM;w=W-28*MM;y=H-86*MM
 y-=para(c,cfg['intro'][lang],x,y,w,19,25,True)+35
 c.setStrokeColor(GOLD);c.line(x,y,x+w,y);y-=30
 y-=para(c,'Formatos disponibles' if lang=='es' else 'Available formats',x,y,w,12,16,True)+20
 for line in cfg['families'][lang].split('\n'):
  y-=para(c,line,x,y,w,11,15,color=WHITE)+12
 c.showPage()

def picture(c,path,x,y,width,height):
 if path not in image_cache:
  with Image.open(path) as im:
   buf=io.BytesIO();im.convert('RGB').save(buf,format='JPEG',quality=94,optimize=True);buf.seek(0);image_cache[path]=ImageReader(buf)
 c.drawImage(image_cache[path],x,y,width=width,height=height,preserveAspectRatio=True,anchor='c')

manifest={'batch':'L1','createdAt':datetime.now(timezone.utc).isoformat(),'aiImageCalls':0,'catalogs':[],'assetsAndSources':[],'editorialDecisions':['Preserve distinct product panels and dimensions even when titles match.','PET coffee/tea styles differentiated using original source labels.','IML duplicate glossy-gold design preserved as source variant 2.','Source capacity field takes precedence over conflicting orange-cup source title; extraction already reviewed.','Diagrams localized with matching EN/ES source page crops.']}
for cfg in configs:
 sid=cfg['sourceId'];source=sources[sid]
 assert hashlib.sha256(Path(source['path']).read_bytes()).hexdigest()==source['sha256'],sid
 records=[r for r in cards if any(s['sourceId']==sid for s in r['sources'])]
 total=1+math.ceil(len(records)/8)
 prepared=[]
 with pymupdf.open(source['path']) as doc:
  for r in records:
   m=media[r['id']];assert m['sourceId']==sid
   rect=list(m['bbox'])
   if sid=='pdf-10':
    first_count={2:4,3:4,4:4,5:5,6:4}[m['page']];index=int(r['id'].split('-c')[-1]);rect[1]=300 if index<=first_count else 570;rect[3]=444 if index<=first_count else 712
   item={'id':r['id'],'name':style_names.get(r['id'],r['name']).copy(),'details':details(r),'images':{},'sourcePages':{},'bbox':rect}
   if r['name']['en'] in ['500 ml Frosted raised-base cup','500 ml U-shaped PP cup','700 ml U-shaped PP cup']:
    for lang in ['es','en']:item['name'][lang]+=' | Ø '+n(r['attributes']['rimDiameterMm'])+' mm'
   for lang in ['es','en']:
    pg=next(s['page'] for s in r['sources'] if s['sourceId']==sid and s['language']==lang)
    target=TMP/f"{r['id']}-{lang}.png"
    doc[pg-1].get_pixmap(matrix=pymupdf.Matrix(3,3),clip=pymupdf.Rect(rect)).save(target)
    item['images'][lang]=str(target);item['sourcePages'][lang]=pg
   prepared.append(item)
 for lang in ['es','en']:
  hashes=[]
  for r in prepared:
   with Image.open(r['images'][lang]) as im:hashes.append(hashlib.sha256(im.tobytes()).hexdigest())
  assert len(set(hashes))==len(hashes),(sid,lang,'repeated photo')
  target=OUT/f"Lynx-Catalogo-{cfg['filename']}-{lang.upper()}.pdf"
  c=canvas.Canvas(str(target),pagesize=(W,H),pageCompression=1);c.setTitle('Lynx - '+cfg['title'][lang]);c.setAuthor('Lynx Packaging Solutions');background(c);cover(c,cfg,lang,total)
  for start in range(0,len(prepared),8):
   page=2+start//8;frame(c,cfg,lang,page,total)
   gap=3*MM;left=12*MM;top=H-70*MM;cw=(W-24*MM-gap)/2;ch=(210*MM-3*gap)/4
   for slot,r in enumerate(prepared[start:start+8]):
    x=left+(slot%2)*(cw+gap);y=top-(slot//2)*(ch+gap)-ch
    c.setFillColor(NAVY);c.setStrokeColor(GOLD);c.setLineWidth(.55);c.rect(x,y,cw,ch,fill=1,stroke=1)
    ph=24*MM;py=y+ch-ph;c.setFillColor(HexColor('#f5f3ee'));c.rect(x+.4,py,cw-.8,ph-.4,fill=1,stroke=0)
    picture(c,r['images'][lang],x+3*MM,py+1.5*MM,cw-6*MM,ph-3*MM)
    c.saveState();c.setFillAlpha(.10);c.drawImage(LOGO,x+cw-31*MM,py+2*MM,width=27*MM,height=16*MM,preserveAspectRatio=True,mask='auto');c.restoreState()
    cy=py-2.3*MM;cy-=para(c,r['name'][lang],x+3*MM,cy,cw-6*MM,8.0,9.5,True)+3
    for line in r['details']:cy-=para(c,line[lang],x+3*MM,cy,cw-6*MM,6.5,7.8,color=HexColor('#d9e0eb'))
    assert cy>=y+2,(r['id'],lang,'caption overflow',cy-y)
    manifest['assetsAndSources'].append({'catalogId':cfg['id'],'recordId':r['id'],'language':lang,'outputPage':page,'image':r['images'][lang],'sourceId':sid,'sourcePage':r['sourcePages'][lang],'bbox':r['bbox'],'name':r['name'][lang],'details':[d[lang] for d in r['details']],'sourceSha256':source['sha256']})
   c.showPage()
  c.save()
  with pymupdf.open(target) as d:
   assert len(d)==total
   text=''.join(p.get_text() for p in d)
   for bad in ['REVIEW EDITION','Reference image','Imagen de referencia','Notes','Notas','Print unclear','�']:assert bad not in text,(target,bad)
   for p in d:
    for b in p.get_text('blocks'):
     assert b[0]>=-1 and b[1]>=-1 and b[2]<=W+1 and b[3]<=H+1,(target,p.number,b[:4])
  print(target.name,total,'pages',target.stat().st_size,'bytes')
 cfg['recordCount']=len(records);cfg['pageCountPerLanguage']=total;cfg['recordIds']=[r['id'] for r in records];cfg['preparedRecords']=prepared;manifest['catalogs'].append(cfg)
(OUT/'Lynx-Lote-1-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(DOC/'content-and-image-map.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('L1: 165 product records, 6 PDFs, 0 AI images')
