import pymupdf as fitz,json,re,hashlib,collections
from pathlib import Path
OUT=Path('docs/inventory');S=json.loads((OUT/'sources.json').read_text(encoding='utf8'))
def norm(t):return re.sub(r'\s+',' ',t).strip()
def blocks(p):
 result=[]
 for b in p.get_text('dict')['blocks']:
  if 'lines' not in b:continue
  for l in b['lines']:
   sp=l['spans']
   result.append({'bbox':l['bbox'],'text':norm(' '.join(s['text'] for s in sp)),'white':all(s['color']==16777215 for s in sp),'size':max(s['size'] for s in sp)})
 return result
def names(p):
 import cv2,numpy as np
 scale=595/p.rect.width;pix=p.get_pixmap(matrix=fitz.Matrix(scale,scale));a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3);r,g,b=a[:,:,0].astype(float),a[:,:,1].astype(float),a[:,:,2].astype(float)
 mask=((g>r*1.04)&(r>50)&(r<175)&(b<100)&(g<200)).astype('uint8')*255
 mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,8),np.uint8));_,_,stats,_=cv2.connectedComponentsWithStats(mask)
 bs=blocks(p);result=[]
 for x,y,w,h,area in stats[1:]:
  if area<200 or w<40 or not 5<h<45 or area/(w*h)<0.9:continue
  rect=fitz.Rect((int(x)-1)/scale,(int(y)-1)/scale,(int(x+w)+1)/scale,(int(y+h)+1)/scale);text=norm(p.get_text(clip=rect));cx=x+w/2
  below=[z for z in bs if 0<=z['bbox'][1]-(y+h)<100 and abs((z['bbox'][0]+z['bbox'][2])/2-cx)<w*.55]
  if text and h<=30:result.append({'bbox':list(rect),'text':text})
 return sorted(result,key=lambda b:(b['bbox'][1],b['bbox'][0]))
products=[]
for s in S[:14]:
 d=fitz.open(s['path']);half=len(d)//2
 for n in range(1,half):
  p=d[n];bs=blocks(p);ns=names(p); esb=blocks(d[n+half]);esn=names(d[n+half])
  for k,b in enumerate(ns):
   x0,y0,x1,y1=b['bbox'];cx=(x0+x1)/2
   row=[a for a in ns if abs(a['bbox'][1]-y0)<20]; centers=sorted((a['bbox'][0]+a['bbox'][2])/2 for a in row);idx=min(range(len(centers)),key=lambda i:abs(centers[i]-cx));left=(centers[idx-1]+cx)/2 if idx else 0;right=(centers[idx+1]+cx)/2 if idx+1<len(centers) else p.rect.width
   if s['id']=='pdf-05' and x1-x0<110:
    left=0 if cx<p.rect.width/2 else p.rect.width/2;right=p.rect.width/2 if cx<p.rect.width/2 else p.rect.width
    region=[a for a in bs if not a['white'] and left<=(a['bbox'][0]+a['bbox'][2])/2<=right and y0-65<a['bbox'][1]<y1]
   else:
    region=[a for a in bs if not a['white'] and left<= (a['bbox'][0]+a['bbox'][2])/2<=right and y1-2<=a['bbox'][1]<min(y1+110*p.rect.width/595,p.rect.height)]
   specs=[a['text'] for a in sorted(region,key=lambda a:a['bbox'][1])]
   diagrams=[a['text'] for a in bs if left<=(a['bbox'][0]+a['bbox'][2])/2<=right and y0-145*p.rect.width/595<a['bbox'][1]<y0 and re.search(r'\d',a['text']) and re.search(r'mm|cm|Ø|Height|Base|Rim|Neck',a['text'],re.I)]
   en=b['text']; es_candidates=sorted(esn,key=lambda a:abs(a['bbox'][1]-y0)+abs((a['bbox'][0]+a['bbox'][2])/2-cx)); es=norm(d[n+half].get_text(clip=fitz.Rect(b['bbox']))) or None
   raw='\n'.join(specs); attrs={};material=re.search(r'Material:\s*([^\n]+)',raw,re.I)
   if material:attrs['materialRaw']=material.group(1)
   for field,pat in [('capacityMl',r'Capacity:\s*([\d.]+)\s*ml'),('weightG',r'Weight:\s*~?([\d.]+)\s*g'),('rimDiameterMm',r'(?:Rim|Diameter):?\s*([\d.]+)\s*mm'),('lengthMm',r'Length:\s*([\d.]+)\s*mm'),('thicknessMicrons',r'Thickness:\s*([\d.]+)\s*[µμu]m')]:
    m=re.search(pat,raw,re.I)
    if m:attrs[field]=float(m.group(1))
   if 'capacityMl' not in attrs:
    m=re.search(r'([\d.]+)\s*ml\b',en,re.I)
    if m:attrs['capacityMl']=float(m.group(1))
   m=re.search(r'Color:\s*([^\n]+)',raw,re.I)
   if m:attrs['colorRaw']=m.group(1)
   m=re.search(r'Size:\s*([^\n]+)',raw,re.I)
   if m:attrs['dimensionsRaw']=m.group(1)
   m=re.search(r'Temp\.:\s*([^\n]+)',raw,re.I)
   if m:attrs['temperatureRaw']=m.group(1)
   if re.search(r'Not customizable',raw,re.I):attrs['customizable']=False
   elif re.search(r'Customizable',raw,re.I):attrs['customizable']=True
   products.append({'id':s['id']+f'-p{n+1:02}-c{k+1:02}','recordKind':'catalog-card','name':{'en':en,'es':es},'attributes':attrs,'specificationLines':specs,'dimensionAnnotations':diagrams,'sources':[{'sourceId':s['id'],'page':n+1,'language':'en','bbox':list(b['bbox'])},{'sourceId':s['id'],'page':n+half+1,'language':'es'}],'publicationStatus':'draft','reviewStatus':'extracted-native-needs-review','supplierGroup':'WHYJ','imageStatus':'not-extracted'})
(OUT/'products-cards.json').write_text(json.dumps(products,ensure_ascii=False,indent=2),encoding='utf8')
print(len(products));print(collections.Counter(p['sources'][0]['sourceId'] for p in products))

