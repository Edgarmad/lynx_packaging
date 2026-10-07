"""Produce source-backed catalogs, with one photograph per product presentation.

The existing batch renderer is loaded without its authoring loop. Website data
is read only. Source references and crop rectangles remain in the output map.
"""
import json,math,re,hashlib,io,sys,collections
from difflib import SequenceMatcher
from pathlib import Path
import pymupdf
import numpy as np
import cv2
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/pdf';TMP=ROOT/'tmp/pdfs/all-catalogs';TMP.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
base=ROOT/'scripts/catalogs/build_batch1_catalogs.py'
namespace={'__file__':str(base)}
code=base.read_text(encoding='utf-8').split("manifest={'batch':")[0]
code=code.replace("'VASOS Y ACCESORIOS | LYNX' if lang=='es' else 'CUPS AND ACCESSORIES | LYNX'","cfg['group'][lang]")
exec(compile(code,str(base),'exec'),namespace)
for key in ['canvas','background','frame','cover','picture','para','tx','MM','W','H','NAVY','GOLD','WHITE','LIGHT','HexColor','LOGO']:
 globals()[key]=namespace[key]
sources=namespace['sources'];cards=namespace['cards'];media=namespace['media']
products={r['id']:r for r in read(ROOT/'src/data/products.json')}
models=read(ROOT/'docs/inventory/products-models.json')
plan=read(ROOT/'docs/catalog-review/catalog-batches.json')
paper=read(OUT/'Lynx-Catalogo-Papel-manifest.json')
paper_ids=set(paper['coveredSourceIds'])
paper_image_paths={x['image'] for x in paper['assetsAndSources']}
docs={};raster_cache={};ocr_cache={};manifest={'catalogs':[],'aiImageCalls':0,'policy':'No source-panel photograph reused for distinct product cards. ES/EN share the same product photographs. Repeated size presentations grouped with their source rows. Master unpublished.','warnings':[]}
panel_cache={}
def doc(sid):
 if sid not in docs:docs[sid]=pymupdf.open(sources[sid]['path'])
 return docs[sid]
def ocr(sid,pg):
 key=(sid,pg)
 if key not in ocr_cache:ocr_cache[key]=read(ROOT/f'docs/inventory/ocr/{sid}-{pg:03d}.json')
 return ocr_cache[key]
def raster(sid,pg):
 key=(sid,pg)
 if key not in raster_cache:
  p=doc(sid)[pg-1];pix=p.get_pixmap(matrix=pymupdf.Matrix(min(2,2600/p.rect.width),min(2,2600/p.rect.width)))
  raster_cache[key]=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
 return raster_cache[key]
def crop(sid,pg,rect,tag):
 p=doc(sid)[pg-1];im=raster(sid,pg);sx=im.width/p.rect.width;sy=im.height/p.rect.height
 box=(max(0,round(rect[0]*sx)),max(0,round(rect[1]*sy)),min(im.width,round(rect[2]*sx)),min(im.height,round(rect[3]*sy)))
 assert box[2]>box[0] and box[3]>box[1],(sid,pg,box)
 out=TMP/(tag+'.png');im.crop(box).save(out)
 return str(out)
def pixelhash(path):
 with Image.open(path) as im:
  im=im.convert('RGB');return hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest()
def dhash(path):
 with Image.open(path) as im:a=np.asarray(im.convert('L').resize((17,16)))
 return np.packbits(a[:,1:]>a[:,:-1]).tobytes().hex()
def mapped_details(p):
 return compact_details([tx(s['label']['es']+': '+s['value']['es'],s['label']['en']+': '+s['value']['en']) for s in p.get('specifications',[]) if s['value'].get('es') and s['value'].get('en')])
def compact_details(lines):
 replacements={'Dimensiones según catálogo':'Medidas','Catalog dimensions':'Dimensions','Diámetro del borde':'Boca','Rim diameter':'Rim','Intervalo de temperatura indicado':'Temperatura','Listed temperature range':'Temperature','Diámetro de la base':'Base','Base diameter':'Base','Personalización':'Personalizable','Customization':'Customizable'}
 result=[]
 for line in lines:
  d=dict(line)
  for lang in ['es','en']:
   for a,b in replacements.items():d[lang]=d[lang].replace(a,b)
  if result and all(namespace['get_para'](result[-1][l]+' | '+d[l],(W-27*MM)/2-6*MM,6.5,7.8)[1]<=8 for l in ['es','en']):
   result[-1]={l:result[-1][l]+' | '+d[l] for l in ['es','en']}
  else:result.append(d)
 return result
def normalize_records(sid):
 result=[]
 for r in cards:
  refs=[s for s in r['sources'] if s['sourceId']==sid]
  if not refs:continue
  ids=r.get('sourceCardIds',[r['id']])
  for idx,pid in enumerate(ids):
   m=media.get(pid)
   if pid in paper_ids:continue
   if m:
    p=products.get(pid);names=p['title'] if p else r['name'];details=mapped_details(p) if p else namespace['details'](r)
    path=str(ROOT/'public'/m['src'].lstrip('/'));pg=m['page'];rect=m['bbox']
    # Every paper container presentation already has its shared size table in Paper.
    if sid=='pdf-04' and pg==2:continue
   else:
    assert sid=='pdf-14',(sid,pid,'missing photograph')
    ref=refs[min(idx*2,len(refs)-1)];pg=ref['page'];x0,y0,x1,y1=ref['bbox'];p=doc(sid)[pg-1]
    im=raster(sid,pg);scale=im.width/p.rect.width;left=int((x0+1)*scale);right=int((x1-1)*scale);end=int((y0-4)*scale);start=max(0,end-int((right-left)*1.4))
    arr=np.asarray(im)[start:end,left:right];density=(arr.min(axis=2)<225).mean(axis=1);occupied=np.where(density>.35)[0]
    if len(occupied):
     last=occupied[-1];top=last;blank=0
     for y in range(last,-1,-1):
      blank=blank+1 if density[y]<.08 else 0
      if blank>=max(3,int(2*scale)):top=y+blank;break
     if last-top>(right-left)*.3:start+=top;end=start+last-top+1
    rect=[left/scale,start/scale,right/scale,end/scale];path=crop(sid,pg,rect,pid);names=r['name'];details=[]
    # Recover numbers from the raster OCR only when the labeled row is confident.
    od=ocr(sid,pg);sx=p.rect.width/od['width'];sy=p.rect.height/od['height'];ls=od['lines']
    next_titles=[s['bbox'][1] for c in cards for s in c['sources'] if s['sourceId']==sid and s['page']==pg and s['bbox'][1]>y0+20 and abs(s['bbox'][0]-x0)<50]
    stop=min(next_titles,default=p.rect.height)-100
    region=[l for l in ls if x0-5<=l['bbox'][0]*sx<x1 and y1<l['bbox'][1]*sy<min(stop,y1+205)]
    for label,es,en in [('Rim:','Boca','Rim'),('Capacity:','Capacidad','Capacity'),('Weight:','Peso','Weight'),('Pack:','Presentación','Packing')]:
     labels=[l for l in region if label.lower() in l['text'].lower()]
     if not labels:continue
     a=labels[0];vals=[l for l in region if l['bbox'][0]>a['bbox'][2]-5 and abs(sum(l['bbox'][1::2])/2-sum(a['bbox'][1::2])/2)<18 and l['confidence']>.98 and re.search(r'\d',l['text'])]
     if not vals:continue
     text=' '.join(l['text'] for l in vals);nums=re.findall(r'\d+(?:\.\d+)?',text)
     if len(nums)!=1:continue
     unit=' mm' if label=='Rim:' else ' ml' if label=='Capacity:' else ' g' if label=='Weight:' else ''
     if label=='Pack:':details.append(tx('Presentación: '+nums[0]+' piezas/caja','Packing: '+nums[0]+' pcs/carton'))
     else:details.append(tx(es+': '+nums[0]+unit,en+': '+nums[0]+unit))
    if r['attributes'].get('materialRaw'):details.append(tx('Material: '+r['attributes']['materialRaw'],'Material: '+r['attributes']['materialRaw']))
   result.append({'id':pid,'coveredIds':[pid],'name':names,'image':path,'details':details,'source':{'sourceId':sid,'page':pg,'bbox':rect},'variants':[]})
 return result
def cy(l):return (l['bbox'][1]+l['bbox'][3])/2
def cx(l):return (l['bbox'][0]+l['bbox'][2])/2
def panels(sid,pg):
 key=(sid,pg)
 if key in panel_cache:return panel_cache[key]
 im=raster(sid,pg);a=np.asarray(im).astype('int16');hh,ww=a.shape[:2];r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 if sid=='pdf-21':mask=((g-r>7)&(g-b>3)&(g>100)).astype('uint8')*255
 elif sid=='pdf-24':mask=((r-g>4)&(g-b>8)&(r>175)&(b>85)).astype('uint8')*255
 elif sid=='pdf-22' and pg>=10 or sid=='pdf-23':mask=(a.max(axis=2)<120).astype('uint8')*255
 else:
  background_color=np.median(a.reshape(-1,3),axis=0)
  mask=((np.abs(a-background_color).max(axis=2)>40) if background_color.mean()<155 else (a.min(axis=2)<230)).astype('uint8')*255
 mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
 contours,_=cv2.findContours(mask,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE);boxes=[]
 for ct in contours:
  x,y,w,h=cv2.boundingRect(ct)
  if sid in ['pdf-21','pdf-24']:
   ok=.06*ww<w<.12*ww and .06*hh<h<.13*hh and (.75<w/h<1.3 if sid=='pdf-24' else 1.1<w/h<2.2)
  elif sid=='pdf-23':ok=.06*ww<w<.20*ww and .12*hh<h<.2*hh
  else:ok=.04*ww<w<.24*ww and .035*hh<h<.22*hh and y<.98*hh
  if not ok:continue
  if sid in ['pdf-21','pdf-24','pdf-23'] and abs(cv2.contourArea(ct)-w*h)>w*h*.15:continue
  if any(abs(x-q[0])<8 and abs(y-q[1])<8 and abs(x+w-q[2])<10 and abs(y+h-q[3])<10 for q in boxes):continue
  boxes.append([x,y,x+w,y+h])
 boxes=[b for b in boxes if not any(q!=b and q[0]<=b[0] and q[1]<=b[1] and q[2]>=b[2] and q[3]>=b[3] for q in boxes)]
 panel_cache[key]=boxes;return boxes
def panel_rect(sid,pg,ref):
 p=doc(sid)[pg-1];im=raster(sid,pg);od=ocr(sid,pg);x0,y0,x1,y1=ref['bbox'];rx=im.width/od['width'];ry=im.height/od['height'];tx=(x0+x1)/2*rx;ty=y0*ry
 candidates=[]
 for box in panels(sid,pg):
  bx,by,ex,ey=box
  if sid=='pdf-24':ok=bx-20<=tx<=ex+20 and abs(ey-ty)<35
  else:ok=bx-30<=tx<=ex+30 and -70<ty-ey<max(70,im.height*.06)
  if ok:candidates.append((abs((bx+ex)/2-tx)/im.width+abs(ey-ty)/im.height,box))
 if not candidates:return None
 box=min(candidates)[1];margin=3 if sid in ['pdf-21','pdf-24'] else 1
 # Egg labels are inside the panels; photograph ends above the label.
 end=min(box[3]-margin,ty-8) if sid=='pdf-24' or (sid=='pdf-22' and box[1]<ty<box[3]) else box[3]-margin
 return [(box[0]+margin)*p.rect.width/im.width,(box[1]+margin)*p.rect.height/im.height,(box[2]-margin)*p.rect.width/im.width,end*p.rect.height/im.height]
def model_records(sid,cfg):
 result=[];limit=next(s['pages'] for s in sources.values() if s['id']==sid) if False else len(doc(sid))//2
 for r in models:
  if sid=='pdf-23' and r['modelCode']:r={**r,'modelCode':re.sub(r'0Z$','OZ',r['modelCode'])}
  if sid=='pdf-20' and r['id'] in ['qunlu-32626df7d780','qunlu-c405fd1117e8']:
   manifest['warnings'].append({'id':r['id'],'catalogId':cfg['id'],'reason':'OCR sidebar category is not an individual product; actual product panels retained.'});continue
  refs=[s for s in r['sources'] if s['sourceId']==sid and (sid in ['pdf-23','pdf-24'] or s['page']<=limit) and (sid!='pdf-24' or s['page']==85)]
  if not refs:continue
  candidates=[]
  for s in refs:
   p=doc(sid)[s['page']-1];od=ocr(sid,s['page']);x0,y0,x1,y1=s['bbox'];yn=y0/od['height']
   if sid=='pdf-21':ok=.08<yn<.9
   elif sid=='pdf-24':ok=(yn<.395 if x0/od['width']>.5 else yn<.97)
   elif sid=='pdf-23':ok=.08<yn<.95
   else:ok=.09<yn<(.98 if (sid=='pdf-20' and s['page']>=32) or (sid=='pdf-22' and s['page']>=13) else .48)
   # Table labels are not product photo captions. A matched diagram/photo
   # panel can admit uncoded lower-row presentations in the compact grids.
   if ok or (sid in ['pdf-20','pdf-22'] and panel_rect(sid,s['page'],s)):candidates.append(s)
  if sid in ['pdf-20','pdf-22']:
   # Some inventory rows only retained the table mention. Locate the actual
   # labeled photo in that same source page, including uncoded families.
   normalize=lambda text:re.sub(r'[^a-z0-9]','',text.lower())
   needle=normalize(r['modelCode'] or r['name']['en'])
   for pn in sorted({x['page'] for x in refs}):
    od=ocr(sid,pn)
    for line in od['lines']:
     if not .08<line['bbox'][1]/od['height']<.90:continue
     hay=normalize(line['text'])
     if r['modelCode']:
      if hay!=needle and not hay.startswith(needle):continue
     else:
      if re.findall(r'\d+',needle)!=re.findall(r'\d+',hay):continue
      if SequenceMatcher(None,needle,hay).ratio()<.78:continue
     ref={'sourceId':sid,'page':pn,'bbox':line['bbox'],'raw':line['text'],'confidence':line['confidence']}
     if panel_rect(sid,pn,ref) or line['bbox'][1]/od['height']<.52:candidates.append(ref)
  overrides={'qunlu-c45193e2eff1':(2,[2075,175,2300,347]),'qunlu-af41c9113ee7':(20,[205,740,630,1030]),'qunlu-49b3bf9c5fa2':(8,[1995,278,2280,532])}
  override=overrides.get(r['id']) if sid=='pdf-20' else None
  if override:candidates=[{'sourceId':sid,'page':override[0],'bbox':[override[1][0],override[1][3]+12,override[1][2],override[1][3]+35]}]
  if not candidates and sid=='pdf-24':
   # Four uncoded products have only a table caption in the research inventory.
   candidates=refs[:1]
  if not candidates:
   manifest['warnings'].append({'id':r['id'],'catalogId':cfg['id'],'reason':'No top product-photo caption found; use source row/panel review.'});continue
  s=min(candidates,key=lambda x:(x['page'],x['bbox'][1]));pg=s['page'];p=doc(sid)[pg-1];od=ocr(sid,pg);sx=p.rect.width/od['width'];sy=p.rect.height/od['height'];x0,y0,x1,y1=s['bbox'];c=(x0+x1)/2
  if sid=='pdf-21':w=od['width']*.095;h=od['height']*.087;c=x0+w/2
  elif sid=='pdf-24':w=od['width']*.09;h=od['height']*.090
  elif sid=='pdf-23':w=od['width']*.097;h=od['height']*.20
  else:w=od['width']*.185;h=od['height']*.19
  prior=[]
  for other in models:
   for a in other['sources']:
    if a['sourceId']==sid and a['page']==pg and y0-h*1.5<a['bbox'][1]<y0-45 and abs((a['bbox'][0]+a['bbox'][2])/2-c)<w*.4:prior.append(a['bbox'][3])
  top=max(y0-h,max(prior,default=0)+15)
  rect=[(c-w/2)*sx,top*sy,(c+w/2)*sx,(y0-12)*sy]
  exact=panel_rect(sid,pg,s)
  if exact:rect=exact
  if override:rect=override[1]
  # Cups source consists of a montage: use the large dimensioned cup on its right.
  if sid=='pdf-23':
   # The alternate montage places its main cup on the left for two sizes.
   left_main=r['modelCode'] in ['QL90-16OZ','QL92-12OZ','QL92-16OZ','QL95-16OZ','GHW-32OZ']
   pw=rect[2]-rect[0]
   if left_main:rect[2]=rect[0]+pw*.44
   else:rect[0]=rect[0]+pw*.61
   main_cups={
    'QL90-12OZ':[365,389,560,645],'QL90-16OZ':[675,382,860,650],
    'QL92-9OZ':[375,1320,545,1505],'QL92-12OZ':[665,1270,863,1530],
    'QL92-14OZ':[1628,28,1803,273],'QL92-16OZ':[1885,27,2058,276],
    'QL95-12OZ':[1635,890,1805,1170],'QL95-16OZ':[1895,870,2065,1172],
    'QL98-12OZ':[2650,64,2780,226],'QL98-16OZ':[2945,37,3090,235],
    'QL98-18OZ':[3250,66,3390,236],'QL98-20OZ':[3568,48,3710,236],
    'GHW-8OZ':[2674,903,2848,1041],'GHW-12OZ':[3073,890,3244,1040],
    'GHW-16OZ':[3475,879,3650,1040],'GHW-24OZ':[2669,1355,2850,1521],
    'GHW-32OZ':[2895,1306,3062,1520]}
   rect=main_cups[r['modelCode']]
  if sid=='pdf-24' and not exact:
   labels={
    '1-pc Egg Boxes':(0,0),'With handle D28':(1,6),'4-pc egg tray':(2,6),'10-pc egg tray':(3,6),'24-pc quail eggs':(8,1)}
   name=r['name']['en'];mapping=next((v for k,v in labels.items() if k.lower()==name.lower()),None)
   if mapping:
    col,row=mapping;left=185+col*194 if col<5 else 1348+(col-5)*194;top=170+row*194 if col<5 else 80+row*194
    rect=[left+4,top+4,left+179,top+150]
  path=crop(sid,pg,rect,cfg['id']+'-'+r['id'])
  variants=[]
  for v in r.get('variants',[]):
   vs=[x for x in v['sources'] if x['sourceId']==sid and (sid not in ['pdf-24','pdf-23'] and x['page']<=limit or sid in ['pdf-24','pdf-23'] and x['page']==pg)]
   if not vs:continue
   vals=v.get('dimensionValuesCandidate',[])
   if vals:
    val=' x '.join(f'{x:g}' for x in vals)+' mm'
    if val not in [x['values'] for x in variants]:variants.append({'code':r['modelCode'],'values':val,'source':vs})
  details=[]
  if len(variants)==1:details.append(tx('Medidas: '+variants[0]['values'],'Dimensions: '+variants[0]['values']));variants=[]
  mats=r.get('materialIds',[])
  if len(mats)==1:details.append(tx('Material: '+mats[0].upper(),'Material: '+mats[0].upper()))
  name=tx(r['modelCode'],r['modelCode']) if r['modelCode'] else dict(r['name'])
  if r['id']=='qunlu-49b3bf9c5fa2':name=tx('Inserto circular | Ø 170 mm','Circular insert | Ø 170 mm');details=[tx('Diámetro: 170 mm','Diameter: 170 mm')]
  if r['id']=='qunlu-ded674fa02c2':name=tx('Tapa y base QL-09','QL-09 lid and base')
  if not name.get('es') and sid in ['pdf-20','pdf-21','pdf-22']:
   other=doc(sid)[pg-1+len(doc(sid))//2];box=pymupdf.Rect(x0*sx-15,y0*sy-5,x1*sx+15,y1*sy+8)
   name['es']=other.get_text(clip=box).strip().replace('\n',' ')
  if not name.get('es'):name['es']=r['modelCode'] or 'Envase '+str(len(result)+1)
  result.append({'id':cfg['id']+'-'+r['id'],'coveredIds':[r['id']],'name':name,'image':path,'details':details,'variants':variants,'source':{'sourceId':sid,'page':pg,'bbox':rect}})
 if sid=='pdf-20':
  # Two dimensions use the same six-compartment photograph in the source.
  target=next((r for r in result if 'qunlu-db26fc470c38' in r['coveredIds']),None)
  alias=next(r for r in models if r['id']=='qunlu-83817ea9ab57')
  if target:
   target['coveredIds'].append(alias['id'])
   target['variants']=[{'code':'GHW-16-60T/B','values':'200 x 200 x 72 mm'},{'code':'GHW-16-60T/B','values':'152 x 152 x 60 mm'}]
   target['details']=[]
 return result
def supplement_grid_panels(sid,items):
 """Cover grid product panels that the earlier code-centric inventory omitted."""
 if sid not in ['pdf-20','pdf-21','pdf-22']:return items
 offset=len(doc(sid))//2
 page_numbers=range(32,offset) if sid=='pdf-20' else range(12,offset+1) if sid=='pdf-22' else range(2,offset)
 clean=lambda text:re.sub(r'[^a-z0-9]','',text.lower())
 lookup={clean(r['name']['en']):r for r in items}
 for pg in page_numbers:
  p=doc(sid)[pg-1];im=raster(sid,pg);sx=p.rect.width/im.width;sy=p.rect.height/im.height;od=ocr(sid,pg)
  for i,b in enumerate(panels(sid,pg)):
   if sid=='pdf-21' and pg not in [2,3,4,5,6,7,10,12,13,14,15]:continue
   rect=[b[0]*sx,b[1]*sy,b[2]*sx,b[3]*sy]
   # Already represented source panel, allowing tighter product silhouettes.
   represented=False
   for r in items:
    ref=r['source']
    if not isinstance(ref,dict) or ref.get('sourceId')!=sid or ref.get('page')!=pg:continue
    a=ref['bbox'];intersection=max(0,min(a[2],rect[2])-max(a[0],rect[0]))*max(0,min(a[3],rect[3])-max(a[1],rect[1]))
    area=min((a[2]-a[0])*(a[3]-a[1]),(rect[2]-rect[0])*(rect[3]-rect[1]))
    if area>0 and intersection/area>.72:represented=True;break
   if represented:continue
   # Preserve only photograph-sized rectangles with an actual product caption.
   inside=sid=='pdf-22' and pg in [12,13]
   cr=pymupdf.Rect(rect[0]-5,rect[3]-(30 if inside else 7),rect[2]+5,rect[3]+38)
   lines=p.get_text(clip=cr).strip().splitlines()
   names=[s.strip() for s in lines if s.strip() and not re.search(r'^(?:Size|Inner|Box|Qty|Capacity|ctn|slv|Dia\.|\d+(?:[.*x×]\d+)+(?:mm)?)',s.strip(),re.I)]
   if not names:
    # Use the OCR caption when it is embedded in the original raster.
    names=[l['text'] for l in od['lines'] if rect[0]-4<=l['bbox'][0]*p.rect.width/od['width']<=rect[2] and cr.y0<=l['bbox'][1]*p.rect.height/od['height']<=cr.y1 and l['confidence']>.95 and not re.search(r'^(?:Size|Inner|Box|Qty|Capacity|ctn|slv|Dia\.)|mm$',l['text'],re.I)]
   if not names:continue
   en=' '.join(names).strip();key=clean(en)
   if key in lookup:
    lookup[key].setdefault('additionalSourcePanels',[]).append({'sourceId':sid,'page':pg,'bbox':rect});continue
   es=doc(sid)[pg-1+offset].get_text(clip=cr).strip().replace('\n',' ')
   if not es:es=en if re.match(r'^(GHW|GH|QL|SR|DW|XL|XY|TS|LDF)',en) or re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9/()._-]*',en) else None
   if not es:
    manifest['warnings'].append({'sourceId':sid,'page':pg,'bbox':rect,'name':en,'reason':'Supplemental panel caption needs Spanish text'});continue
   details=[]
   region=p.get_text(clip=pymupdf.Rect(rect[0]-5,rect[3],rect[2]+5,min(p.rect.height,rect[3]+145)))
   dim=re.search(r'(?:\d+(?:\.\d+)?\s*[*x×]\s*){1,3}\d+(?:\.\d+)?',region)
   if dim:
    value=re.sub(r'\s*[*x×]\s*',' x ',dim.group())+' mm';details.append(tx('Medidas: '+value,'Dimensions: '+value))
   tag=f'{sid}-p{pg:02d}-panel-{i+1:02d}'
   # For captions inside a black panel, the last strip is explanatory text.
   if inside:rect[3]=min(rect[3],cr.y0)
   path=crop(sid,pg,[rect[0]+2,rect[1]+2,rect[2]-2,rect[3]-2],tag)
   r={'id':tag,'coveredIds':[tag],'name':tx(es,en),'image':path,'details':details,'variants':[],'source':{'sourceId':sid,'page':pg,'bbox':rect},'supplementalSourcePanel':True}
   items.append(r);lookup[key]=r
 return items
def group_identical(items):
 grouped={};out=[]
 for r in items:
  h=pixelhash(r['image'])
  if h in grouped:
   old=grouped[h];old['coveredIds']+=r['coveredIds']
   if not old['variants']:old['variants']=[{'code':old['name'],'values':{l:'; '.join(x[l] for x in old['details']) for l in ['es','en']}}]
   old['variants'].append({'code':r['name'],'values':{l:'; '.join(x[l] for x in r['details']) for l in ['es','en']}})
  else:grouped[h]=r;out.append(r)
 return out
def variant_label(v,lang):return v['code'][lang] if isinstance(v['code'],dict) else v['code']
def group_reviewed_photos(items):
 groups=[
  ('pdf-01-p05-c01','pdf-01-p05-c04',tx('Bolsa transparente para un vaso','Clear one-cup bag')),
  ('pdf-01-p05-c02','pdf-01-p05-c05',tx('Bolsa transparente para dos vasos','Clear two-cup bag')),
  ('pdf-01-p05-c03','pdf-01-p05-c06',tx('Bolsa transparente para cuatro vasos','Clear four-cup bag')),
  ('pdf-02-p04-c01','pdf-02-p04-c02',tx('Botella de 500 ml con asa','500 ml handled bottle')),
  ('pdf-03-p09-c03','pdf-03-p09-c04',tx('Botella lisa de 1000 ml','1000 ml smooth bottle')),
  ('pdf-14-p10-c04','pdf-14-p10-c07',tx('Tapas domo PET ahumadas','Smoke PET dome lids')),
  ('pdf-14-p10-c05','pdf-14-p10-c08',tx('Tapas planas PET ahumadas','Smoke PET flat lids')),
  ('plastic-bakery-qunlu-65170f31a728','plastic-bakery-qunlu-96a5571870c3',tx('Cajas cuadradas para pastel','Square cake boxes')),
  ('plastic-bento-qunlu-cbb11591443f','plastic-bento-qunlu-61d8d94a10ac',tx('Bandejas QL-17','QL-17 trays')),
  ('plastic-bento-qunlu-9b62a79066d9','plastic-bento-qunlu-50a41c162db1',tx('Bandejas GHW-2287 / GHW-500','GHW-2287 / GHW-500 trays')),
  ('plastic-bento-qunlu-f5071ea06673','plastic-bento-qunlu-acccb20be7b1',tx('Bandejas QL-16','QL-16 trays')),
  ('plastic-eggs-qunlu-47608fea6f9c','plastic-eggs-qunlu-68384ac1c50e',tx('Envases QL-J-020D / QL-J-020Z','QL-J-020D / QL-J-020Z egg boxes'))]
 lookup={r['id']:r for r in items};removed=set()
 for a,b,name in groups:
  if a not in lookup or b not in lookup:continue
  old,r=lookup[a],lookup[b]
  for rr in [old,r]:
   if not rr['variants']:rr['variants']=[{'code':dict(rr['name']),'values':{l:'; '.join(x[l] for x in rr['details']) for l in ['es','en']}}]
  old['variants']+=r['variants'];old['name']=name;old['details']=[];old['coveredIds']+=r['coveredIds'];old.setdefault('groupedSources',[]).append(r['source']);removed.add(b)
 return [r for r in items if r['id'] not in removed]
def author(cfg,items):
 titles={
  'ALDI crepe cake box':tx('Caja para pastel de crepas ALDI','ALDI crepe cake box'),
  '4-inch square cake box':tx('Caja cuadrada para pastel de 4 pulgadas','4-inch square cake box'),
  '6-inch square cake box':tx('Caja cuadrada para pastel de 6 pulgadas','6-inch square cake box'),
  'Macaron box':tx('Caja para macarons','Macaron box'),'40-macaron tray':tx('Bandeja para 40 macarons','40-macaron tray'),
  'Triangular cake box A2/B2':tx('Caja triangular para pastel A2/B2','Triangular cake box A2/B2'),
  'Takeaway noodle bowl':tx('Recipiente para fideos para llevar','Takeaway noodle bowl'),
  'Single-compartment meal box':tx('Envase para comida de un compartimento','Single-compartment meal box'),
  'Sanquan 240 g separate tray B/L':tx('Bandeja Sanquan de 240 g | Base y tapa','Sanquan 240 g tray | Base and lid'),
  'Sanquan 380 g separate tray B/L':tx('Bandeja Sanquan de 380 g | Base y tapa','Sanquan 380 g tray | Base and lid'),
  '1-pc Egg Boxes':tx('Envase para un huevo','Single-egg box'),
  'with handle D28':tx('Envase para huevos con asa D28','Egg box with handle D28'),
  '4-pc egg tray':tx('Bandeja para cuatro huevos','Four-egg tray'),
  '10-pc egg tray':tx('Bandeja para diez huevos','Ten-egg tray'),
  '24-pc quail eggs':tx('Envase para 24 huevos de codorniz','24-quail-egg box')}
 for r in items:
  r['name']=titles.get(r['name']['en'],r['name'])
  for v in r.get('variants',[]):
   if isinstance(v['code'],dict):v['code']=titles.get(v['code']['en'],v['code'])
 items=group_identical(group_reviewed_photos(items));assert items,cfg['id']
 # Allow larger tables to use a full row or page rather than dropping variants.
 chunks=[];chunk=[];used=0
 for r in items:
  r['details']=compact_details(r['details'])
  length=max(sum(namespace['get_para'](d[l],(W-27*MM)/2-6*MM,6.5,7.8)[1] for d in r['details']) for l in ['es','en'])
  titleheight=max(namespace['get_para'](r['name'][l],(W-27*MM)/2-6*MM,8,9.5,True)[1] for l in ['es','en'])
  variantheight=max(sum(namespace['get_para'](variant_label(v,l)+' | '+(v['values'][l] if isinstance(v['values'],dict) else v['values'])+' | '+v.get('capacity',{}).get(l,''),(W-27*MM)/2-6*MM,6.3,8)[1]+2 for v in r['variants']) for l in ['es','en'])
  rows=max(1,math.ceil((length+variantheight+titleheight+24*MM+14)/((210*MM-9*MM)/4)))
  rows=min(4,rows)
  if used+rows>8:chunks.append(chunk);chunk=[];used=0
  if used%2 and rows>1:used+=1
  if used+rows*2>8 and rows>1:chunks.append(chunk);chunk=[];used=0
  chunk.append((r,used,rows));used+=1 if rows==1 else rows*2
 if chunk:chunks.append(chunk)
 total=len(chunks)+1;outputs=[]
 for lang in ['es','en']:
  target=OUT/f"Lynx-Catalogo-{cfg['filename']}-{lang.upper()}.pdf";c=canvas.Canvas(str(target),pagesize=(W,H),pageCompression=1);c.setTitle('Lynx - '+cfg['title'][lang]);c.setAuthor('Lynx Packaging Solutions');background(c);cover(c,cfg,lang,total)
  for page,chunk in enumerate(chunks,2):
   frame(c,cfg,lang,page,total);gap=3*MM;left=12*MM;top=H-70*MM;cw=(W-24*MM-gap)/2;ch=(210*MM-3*gap)/4
   for r,slot,rows in chunk:
    wide=rows>1;x=left+(slot%2)*(cw+gap);width=2*cw+gap if wide else cw;height=rows*ch+(rows-1)*gap;y=top-(slot//2)*(ch+gap)-height
    c.setFillColor(NAVY);c.setStrokeColor(GOLD);c.setLineWidth(.55);c.rect(x,y,width,height,fill=1,stroke=1)
    ph=(35 if wide else 24)*MM;py=y+height-ph;c.setFillColor(HexColor('#f5f3ee'));c.rect(x+.4,py,width-.8,ph-.4,fill=1,stroke=0)
    picture(c,r['image'],x+3*MM,py+1.5*MM,width-6*MM,ph-3*MM)
    c.saveState();c.setFillAlpha(.1);c.drawImage(LOGO,x+width-31*MM,py+2*MM,width=27*MM,height=16*MM,preserveAspectRatio=True,mask='auto');c.restoreState()
    yy=py-2.3*MM;yy-=para(c,r['name'][lang],x+3*MM,yy,width-6*MM,8.0,9.5,True)+3
    if not r['variants']:
     for line in r['details']:yy-=para(c,line[lang],x+3*MM,yy,width-6*MM,6.5,7.8,color=HexColor('#d9e0eb'))
    else:
     for v in r['variants']:
      values=v['values'][lang] if isinstance(v['values'],dict) else v['values'];cap=v.get('capacity',{}).get(lang,'');yy-=para(c,variant_label(v,lang)+' | '+values+(' | '+cap if cap else ''),x+3*MM,yy,width-6*MM,6.3,8,color=WHITE)+2
    assert yy>=y+2,(cfg['id'],r['id'],lang,'caption overflow',yy-y)
   c.showPage()
  c.save()
  with pymupdf.open(target) as d:
   assert len(d)==total
   for p in d:
    assert p.get_text().strip()
    for b in p.get_text('blocks'):assert b[0]>=-1 and b[1]>=-1 and b[2]<=W+1 and b[3]<=H+1,(target,p.number,b[:4])
  outputs.append(str(target));print(target.name,total,'pages',len(items),'cards',flush=True)
 cfg.update({'records':items,'outputs':outputs,'pageCountPerLanguage':total,'cardCount':len(items),'coveredRecordCount':sum(len(r['coveredIds']) for r in items)})
 manifest['catalogs'].append(cfg)
 (OUT/'Lynx-Todos-Catalogos-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
def config(c,filename=None):
 groups={'Cups':tx('VASOS Y ACCESORIOS | LYNX','CUPS AND ACCESSORIES | LYNX'),'Plástico':tx('EMPAQUES PLÁSTICOS | LYNX','PLASTIC PACKAGING | LYNX')}
 titles={
 'cups-01':tx('Bolsas y portavasos','Bags and cup carriers'),'cups-02':tx('Botellas para bebidas calientes','Hot beverage bottles'),'cups-03':tx('Botellas PET','PET bottles'),'cups-04':tx('Envases','Containers'),'cups-05':tx('Envases, tarros y cubiertos','Containers, jars and cutlery'),'cups-06':tx('Fundas y accesorios','Sleeves and accessories'),'cups-07':tx('Latas de apertura fácil','Easy-open cans'),'cups-08':tx('Popotes','Straws'),'cups-09':tx('Tapas por inyección','Injection-molded lids'),'cups-12':tx('Vasos de papel','Paper cups'),'cups-14':tx('Catálogo PET','PET catalog'),
 'plastic-cups':tx('Vasos de plástico','Plastic cups'),'plastic-bakery':tx('Empaques para repostería','Bakery packaging'),'plastic-bento':tx('Bento, carne y bandejas','Bento, meat and trays'),'plastic-fruit':tx('Frutas y verduras','Fruit and vegetable packaging'),'plastic-eggs':tx('Envases para huevos','Egg packaging')}
 names={'cups-01':'Bolsas-Portavasos','cups-02':'Botellas-Calientes','cups-03':'Botellas-PET','cups-04':'Envases','cups-05':'Envases-Tarros-Cubiertos','cups-06':'Fundas-Accesorios','cups-07':'Latas-Apertura-Facil','cups-08':'Popotes','cups-09':'Tapas-Inyeccion','cups-12':'Vasos-Papel','cups-14':'PET','plastic-cups':'Plastico-Vasos','plastic-bakery':'Plastico-Reposteria','plastic-bento':'Plastico-Bento-Carne-Bandejas','plastic-fruit':'Plastico-Frutas-Verduras','plastic-eggs':'Plastico-Huevos'}
 title=titles[c['id']]
 return {'id':c['id'],'sourceIds':c['sourceIds'],'filename':filename or names[c['id']],'title':title,'group':groups.get(c['group'],groups['Cups']),'intro':tx('Explora los formatos y características disponibles para seleccionar el empaque adecuado para tu producto.','Explore the available formats and specifications to select the packaging for your product.'),'families':title}
def main():
 selected=set(sys.argv[1:])
 for c in plan['catalogs']:
  cid=c['id']
  if selected and cid not in selected:continue
  if cid in ['paper','sustainable','cups-10','cups-11','cups-13']:continue
  cfg=config(c);sid=c['sourceIds'][0]
  if cid.startswith('plastic-'):items=supplement_grid_panels(sid,model_records(sid,cfg))
  else:items=normalize_records(sid)
  if cid=='cups-12':
   # Standard cup records are supplied by the native source, custom Jihong
   # and ice-cream cups keep their factory-specific source presentations.
   for r in read(OUT/'paper-cups-moved.json'):
    if r['id'].startswith('pdf-12-'):continue
    items.append({**r,'coveredIds':[v['id'] for v in r.get('variants',[{'id':r['id']}])],'variants':r.get('variants',[])})
  author(cfg,items)
if __name__=='__main__':main()
