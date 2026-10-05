"""Prepare the website catalog from audited extraction records and local PDF assets.

Run with the Python runtime documented in docs/inventory/WEBSITE-CATALOG.md.
PDFs are read only at preparation time, never by the website.
"""
import collections
import copy
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import cv2
import pymupdf as fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'docs/inventory'
ASSETS = ROOT / 'public/images/products'
ASSETS.mkdir(parents=True, exist_ok=True)

def read(name):
    return json.loads((AUDIT / name).read_text(encoding='utf8'))

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

def loc(es, en):
    return {'es': es, 'en': en}

sources = {s['id']: s for s in read('sources.json')}
docs = {}
pages = {}

def page(sid, number):
    if sid not in docs:
        docs[sid] = fitz.open(sources[sid]['path'])
    return docs[sid][number - 1]

def raster(sid, number):
    key = (sid, number)
    if key not in pages:
        p = page(sid, number)
        # Render at the embedded raster's resolution, with no artificial upscaling.
        images = p.get_images(full=True)
        width = max((i[2] for i in images), default=int(p.rect.width * 2))
        width = min(width, 5000)
        pix = p.get_pixmap(matrix=fitz.Matrix(width / p.rect.width, width / p.rect.width))
        pages[key] = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    return pages[key]

media_log = []
previous_media={m['productId']:m for m in read('website-media.json')} if (AUDIT/'website-media.json').exists() else {}

def save_image(pid, sid, number, rect, title, caption=None):
    p = page(sid, number)
    im = raster(sid, number)
    sx, sy = im.width / p.rect.width, im.height / p.rect.height
    coords = (max(0, int(rect[0]*sx)), max(0, int(rect[1]*sy)), min(im.width, int(rect[2]*sx)), min(im.height, int(rect[3]*sy)))
    crop = im.crop(coords)
    crop.thumbnail((900, 900), Image.Resampling.LANCZOS)
    target = ASSETS / (pid + '.webp')
    pixel_hash=hashlib.sha256(crop.tobytes()).hexdigest()
    if not target.exists() or previous_media.get(pid,{}).get('pixelSha256')!=pixel_hash:
        crop.save(target, 'WEBP', quality=86, method=6)
    media_log.append({'productId': pid, 'src': '/images/products/' + target.name, 'sourceId': sid, 'page': number, 'bbox': [round(v, 3) for v in rect], 'width': crop.width, 'height': crop.height, 'pixelSha256':pixel_hash, 'method': 'PDF crop; resize down only; no AI geometry changes', 'sourceSha256': sources[sid]['sha256']})
    # A fixed square canvas in the UI keeps the grid stable; object-fit contain
    # preserves the original geometry and the full crop.
    media = {'type': 'image', 'placeholder': False, 'src': media_log[-1]['src'], 'alt': title, 'ratio': 1, 'fit': 'contain', 'width': crop.width, 'height': crop.height}
    if caption:
        media['caption'] = caption
    return media

def card_rect(record):
    s = record['sources'][0]
    p = page(s['sourceId'], s['page'])
    im = raster(s['sourceId'], s['page'])
    scale = im.width/p.rect.width
    x0,y0,x1,_ = s['bbox']
    if s['sourceId']=='pdf-05' and s['page']==5:
        return [x0-146,y0-5,x0-6,y0+109]
    if s['sourceId']=='pdf-06' and s['page']==2 and y0>300:
        return [x0+1,y0-(x1-x0)*.98,x1-1,y0-5]
    left,right = int((x0+1)*scale),int((x1-1)*scale)
    end = int((y0-4)*scale)
    width = right-left
    # Backgrounds of the catalog photos are separated by white gutters.
    # Find the contiguous photo region above the title, ignoring the bottom gap.
    start = max(0,end-int(width*1.7))
    arr = np.asarray(im)[start:end,left:right]
    density = (arr.min(axis=2)<225).mean(axis=1)
    occupied = np.where(density>.35)[0]
    if len(occupied):
        last = occupied[-1]
        top = last
        blank = 0
        for y in range(last,-1,-1):
            blank = blank+1 if density[y]<.08 else 0
            if blank>=max(3,int(2*scale)):
                top=y+blank
                break
        height=last-top+1
        if height>=width*.35:
            start += top
            end = start+height
        else:
            start = end-int(width*1.2)
    else:
        start=end-int(width*1.2)
    return [left/scale,max(0,start)/scale,right/scale,end/scale]

taxonomy = {c['id']: c['name'] for c in read('categories-proposed.json')}
groups = [
    ('cups', loc('Vasos', 'Cups'), ['paper-cups','plastic-cups','iml-cups']),
    ('lids', loc('Tapas', 'Lids'), ['cup-lids','can-lids']),
    ('bottles', loc('Botellas y envases para bebidas', 'Bottles & beverage containers'), ['beverage-bottles','beverage-cans']),
    ('food-containers', loc('Envases para alimentos', 'Food containers'), ['food-containers','dessert-jars','ice-cream-packaging','paper-bowls-buckets','cold-noodle-containers']),
    ('bags', loc('Bolsas y portavasos', 'Bags & cup carriers'), ['paper-bags','food-paper-bags','plastic-bags','cup-carriers']),
    ('accessories', loc('Accesorios y consumibles', 'Accessories & consumables'), ['cup-accessories','straws','cutlery','wrappers-sheets','paper-placemats','cling-film']),
    ('trays', loc('Bandejas', 'Trays'), ['meat-trays','skin-pack-trays','map-trays','frozen-food-containers','food-trays','industrial-trays','trays']),
    ('bakery', loc('Empaques para repostería', 'Bakery packaging'), ['bakery-containers']),
    ('produce', loc('Empaques para frutas y ensaladas', 'Fruit & salad packaging'), ['fruit-vegetable-containers','cut-fruit-containers','salad-containers','egg-containers']),
    ('boxes', loc('Cajas y empaques personalizados', 'Boxes & custom packaging'), ['food-paper-boxes','pizza-boxes','multipacks','printed-cartons','corrugated-cartons']),
]
group_for = {c:gid for gid,_,cs in groups for c in cs}
materials = {
    'pp':loc('Polipropileno (PP)','Polypropylene (PP)'), 'pet':loc('PET','PET'), 'pvc':loc('PVC','PVC'),
    'ps':loc('Poliestireno (PS)','Polystyrene (PS)'), 'as':loc('AS','AS'), 'pla':loc('PLA','PLA'),
    'paper':loc('Papel','Paper'), 'kraft-paper':loc('Papel kraft','Kraft paper'), 'paperboard':loc('Cartulina','Paperboard'),
    'aluminum':loc('Aluminio','Aluminum'), 'greaseproof-paper':loc('Papel antigrasa','Greaseproof paper'),
    'bamboo-paper':loc('Papel de bambú','Bamboo paper'), 'kraft-paperboard':loc('Cartulina kraft','Kraft paperboard'),
    'corrugated-board':loc('Cartón corrugado','Corrugated board'), 'waxed-paper':loc('Papel encerado','Waxed paper'),
    'pe-coated-paper':loc('Papel recubierto de PE','PE-coated paper'), 'newsprint':loc('Papel periódico','Newsprint'),
}
products=[]
deferred=[]
dedup={}

def number(n):
    return f'{n:g}'

def provenance(record):
    refs=dict.fromkeys((s['sourceId'],s['page'],s['language']) for s in record['sources'] if s.get('language') in ('en','es'))
    return [{'sourceId':sid,'page':pn,'language':lang} for sid,pn,lang in refs]

def base(record,title,kind='model'):
    cats = list(dict.fromkeys(group_for[x] for x in record['categoryIds'] if x in group_for))
    if not cats:
        return None
    attrs={'product-type':record['categoryIds'], 'size-mode':['custom' if kind=='family' else 'standard']}
    mats=record.get('materialIds',record.get('materialOptions',[]))
    if mats:
        attrs['material']=mats
    if 'pla' in mats:
        cats.append('sustainable')
    return {'id':record['id'],'slug':record['id'],'title':title,'description':loc(f"{title['es']}. Consulta las características disponibles y contacta a Lynx para definir las condiciones de tu proyecto.",f"{title['en']}. Explore the available specifications and contact Lynx to discuss your project requirements."),'status':'published','kind':kind,'categoryIds':cats,'solutionIds':['food-beverage'],'caseIds':[],'gallery':[],'attributes':attrs,'specifications':[],'source':'; '.join(f"{s['sourceId']} p. {s['page']} ({s.get('language','en')})" for s in record['sources']),'provenance':provenance(record)}

def spec(p,es,en,value,english=None):
    p['specifications'].append({'label':loc(es,en),'value':loc(value,english or value)})

def measured(p,a):
    for key,es,en,unit in [('capacityMl','Capacidad','Capacity','ml'),('weightG','Peso','Weight','g'),('rimDiameterMm','Diámetro del borde','Rim diameter','mm'),('lengthMm','Longitud','Length','mm'),('thicknessMicrons','Espesor','Thickness','µm')]:
        n=a.get(key)
        if isinstance(n,(float,int)) and n>0:
            if key=='rimDiameterMm' and 'straws' in p['attributes']['product-type']:es,en='Diámetro','Diameter'
            spec(p,es,en,f'{number(n)} {unit}')
    if a.get('capacityMl',0)>0:
        n=a['capacityMl'];p['attributes']['capacity']=['up-to-250' if n<=250 else '251-500' if n<=500 else '501-1000' if n<=1000 else 'over-1000']
    if a.get('rimDiameterMm',0)>0:
        n=a['rimDiameterMm'];p['attributes']['rim']=['up-to-60' if n<=60 else '61-80' if n<=80 else '81-90' if n<=90 else '91-100' if n<=100 else 'over-100']
    if a.get('dimensionsRaw') and re.search(r'\d',a['dimensionsRaw']):
        spec(p,'Dimensiones según catálogo','Catalog dimensions',a['dimensionsRaw'])
        p['dimensions']={'raw':a['dimensionsRaw'],'axisOrder':'unconfirmed'}
    if a.get('temperatureRangeC') and len(a['temperatureRangeC'])==2:
        lo,hi=a['temperatureRangeC'];spec(p,'Intervalo de temperatura indicado','Listed temperature range',f'{number(lo)} °C – {number(hi)} °C')
    if isinstance(a.get('customizable'),bool):
        yes=a['customizable'];p['attributes']['customization']=['yes' if yes else 'no'];spec(p,'Personalización','Customization','Disponible' if yes else 'No disponible','Available' if yes else 'Unavailable')
    pack=a.get('packing')
    if pack and pack.get('quantity',0)>0:
        esunit='juegos' if pack['unit']=='sets' else 'piezas';esbox='caja' if pack['container']=='carton' else 'paquete'
        spec(p,'Presentación','Packing',f"{number(pack['quantity'])} {esunit}/{esbox}",f"{number(pack['quantity'])} {pack['unit']}/{pack['container']}")

cards=[]
for original in read('products-cards.json'):
    ids=original.get('sourceCardIds',[original['id']])
    if len(ids)>1 and len(original['sources'])==len(ids)*2:
        # The research inventory grouped text-identical entries. Restore each
        # photograph before deciding whether they really represent duplicates.
        for i,pid in enumerate(ids):
            item=copy.deepcopy(original);item['id']=pid;item['sources']=original['sources'][i*2:i*2+2];cards.append(item)
    else:cards.append(original)
colors={'white':'blanco','clear':'transparente','blue':'azul','pink':'rosa','black':'negro','red':'rojo','green':'verde','yellow':'amarillo','orange':'naranja','purple':'morado','gold':'dorado','silver':'plateado','brown':'café'}
prefixes={'cup-lids':('Tapa para vaso','Cup lid',r'tapa|lid'),'can-lids':('Tapa de apertura fácil','Easy-open lid',r'tapa|lid'),'food-containers':('Envase para alimentos','Food container',r'envase|container|box'),'dessert-jars':('Envase para postres','Dessert container',r'envase|jar|container'),'beverage-bottles':('Botella','Bottle',r'botella|bottle'),'beverage-cans':('Envase para bebidas','Beverage container',r'envase|can|container')}
for record in cards:
    sid=record['sources'][0]['sourceId']
    if sid=='pdf-14':
        deferred.append({'id':record['id'],'reason':'Raster specification values missing from native text; overlaps PET catalog. Preserve for a separate visual verification pass.'});continue
    if any(not record['name'].get(lang) or '\ufffd' in record['name'][lang] for lang in ['es','en']):
        deferred.append({'id':record['id'],'reason':'Missing or damaged bilingual title'});continue
    title=dict(record['name'])
    subtype=record['categoryIds'][0]
    if subtype in prefixes:
        es,en,pattern=prefixes[subtype]
        for lang,label in [('es',es),('en',en)]:
            if not re.search(pattern,title[lang],re.I):title[lang]=label+' · '+title[lang]
    single_lid=next((re.fullmatch(r'Lid:\s*([A-Za-z]+)',line) for line in record['specificationLines'] if re.fullmatch(r'Lid:\s*([A-Za-z]+)',line)),None)
    if single_lid and single_lid.group(1).lower() in colors:
        color=single_lid.group(1).lower();title['es']+=' · tapa '+colors[color];title['en']+=' · '+color+' lid'
    if record['categoryIds'][0] in ('paper-cups','plastic-cups','iml-cups'):
        for lang,prefix in [('es','Vaso'),('en','Cup')]:
            if not re.search(r'vaso|cup',title[lang],re.I):title[lang]=prefix+' · '+title[lang]
    p=base(record,title)
    if not p:
        deferred.append({'id':record['id'],'reason':'Taxonomy requires review'});continue
    measured(p,record['attributes'])
    code=re.match(r'^(\d{4,}[A-Za-z]?)(?:\s|$)',record['name']['en'])
    if code and subtype=='cutlery':p['modelCode']=code.group(1);spec(p,'Modelo','Model',code.group(1))
    # Explicitly labeled photo annotations can supplement absent native fields.
    for pattern,es,en in [(r'\b(?:H|Height)\s*:?\s*(\d+(?:\.\d+)?)\s*mm','Altura','Height'),(r'\bBase\s*(?:Ø)?\s*(\d+(?:\.\d+)?)\s*mm','Diámetro de la base','Base diameter')]:
        found={m.group(1) for line in record['dimensionAnnotations'] for m in re.finditer(pattern,line,re.I)}
        if len(found)==1:spec(p,es,en,next(iter(found))+' mm')
    raw=record['attributes'].get('materialRaw','').strip().lower()
    if not record['materialIds'] and raw=='plastic':spec(p,'Material','Material','Plástico (polímero sin especificar)','Plastic (polymer unspecified)')
    mats=record['materialIds']
    if mats:spec(p,'Material','Material',', '.join(materials[x]['es'] for x in mats),', '.join(materials[x]['en'] for x in mats))
    # Color variants can have identical extracted names/specifications. Merge
    # only if the product photograph is also pixel-identical.
    s=record['sources'][0];rect=card_rect(record)
    p['gallery']=[save_image(p['id'],sid,s['page'],rect,title)]
    key=json.dumps([title,p['attributes'],p['specifications'],media_log[-1]['pixelSha256']],sort_keys=True,ensure_ascii=False)
    if key in dedup:
        existing=dedup[key];existing['provenance']+=p['provenance'];deferred.append({'id':p['id'],'reason':'Exact normalized duplicate','mergedInto':existing['id']});continue
    products.append(p);dedup[key]=p

# OCR-only models are admitted only when the code and dimensions agree between
# EN/ES master rows, there is one material and one dimension tuple, and a distinct
# high-confidence photo caption is available above the dimension diagrams.
conflicts={pid for issue in read('language-ocr-conflicts.json') for pid in issue['recordIds']}
for record in read('products-models.json'):
    if record['supplierGroup']!='QUNLU':
        deferred.append({'id':record['id'],'reason':'Supplier model retained for individual image/specification verification'});continue
    variants=record.get('variants',[])
    if record['id'] in conflicts or len(variants)!=1 or len(record['materialIds'])!=1:
        deferred.append({'id':record['id'],'reason':'OCR conflict, material alternatives or ambiguous/missing dimension variants'});continue
    v=variants[0]
    if len(v.get('dimensionValuesCandidate',[]))!=3 or not {'pdf-24','pdf-25'}.issubset({s['sourceId'] for s in v['sources']}):
        deferred.append({'id':record['id'],'reason':'Dimensions lack paired EN/ES master evidence'});continue
    cells=v.get('rowCells',[])
    if any(c['confidence']<.97 for c in cells if re.search(r'\d.*[x*].*\d',c['text'])):
        deferred.append({'id':record['id'],'reason':'Dimension OCR confidence below threshold'});continue
    candidates=[]
    for s in record['sources']:
        if s['sourceId']!='pdf-24' or s.get('confidence',0)<.98:continue
        pg=page('pdf-24',s['page']);x0,y0,x1,y1=s['bbox']
        if .09*pg.rect.height<y0<.46*pg.rect.height and x1-x0>.035*pg.rect.width:
            candidates.append(s)
    if not candidates:
        deferred.append({'id':record['id'],'reason':'No unambiguous product photo caption'});continue
    subtype=record['categoryIds'][0]
    if subtype not in group_for or subtype not in taxonomy:
        deferred.append({'id':record['id'],'reason':'Taxonomy requires review'});continue
    title=loc(taxonomy[subtype]['es']+' · '+record['modelCode'],taxonomy[subtype]['en']+' · '+record['modelCode'])
    p=base(record,title);p['modelCode']=record['modelCode']
    spec(p,'Modelo','Model',record['modelCode'])
    measured(p,{'dimensionsRaw':' × '.join(number(x) for x in v['dimensionValuesCandidate'])+' mm'})
    mat=materials[record['materialIds'][0]];spec(p,'Material','Material',mat['es'],mat['en'])
    s=candidates[0];pg=page('pdf-24',s['page']);x0,y0,x1,y1=s['bbox'];cx=(x0+x1)/2
    # Width of a photo column is 1/6 of the spread, capped below the neighboring
    # caption spacing; exclude the model text and keep only the photograph.
    w=pg.rect.width*.185;h=pg.rect.height*.18
    prior=[]
    for other in read('products-models.json'):
        for ref in other['sources']:
            if ref['sourceId']=='pdf-24' and ref['page']==s['page'] and ref.get('confidence',0)>.95:
                ax,ay,bx,by=ref['bbox']
                if .09*pg.rect.height<ay<y0-.03*pg.rect.height and abs((ax+bx)/2-cx)<pg.rect.width*.07 and bx-ax>pg.rect.width*.035:
                    prior.append(by)
    top=max(y0-h,.09*pg.rect.height,max(prior,default=0)+pg.rect.height*.015)
    left=max(cx-w/2,.08*pg.rect.width);right=min(cx+w/2,.93*pg.rect.width)
    rect=[left,top,right,y0-pg.rect.height*.007]
    # Strip thin colored column dividers from the outer edge of a crop.
    im=raster('pdf-24',s['page']);scale=im.width/pg.rect.width
    region=np.asarray(im)[int(rect[1]*scale):int(rect[3]*scale),int(left*scale):int(right*scale)]
    chroma=region.max(axis=2).astype(int)-region.min(axis=2).astype(int)
    line=(chroma>60).mean(axis=0)>.7
    for ix in np.where(line)[0]:
        if ix<region.shape[1]*.12:rect[0]=max(rect[0],left+(ix+5)/scale)
        if ix>region.shape[1]*.88:rect[2]=min(rect[2],left+(ix-5)/scale)
    # Isolate the central product silhouette, excluding neighboring photos,
    # previous-row captions and page divider lines. No product pixels are painted.
    region=np.asarray(im)[int(rect[1]*scale):int(rect[3]*scale),int(rect[0]*scale):int(rect[2]*scale)]
    mask=(region.min(axis=2)<240).astype('uint8')*255
    mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    _,_,stats,_=cv2.connectedComponentsWithStats(mask)
    candidates=[]
    rh,rw=mask.shape
    for ax,ay,bw,bh,area in stats[1:]:
        if area<rw*rh*.015 or bw<rw*.15 or bh<rh*.15:continue
        dx=(ax+bw/2-rw/2)/rw;dy=(ay+bh/2-rh*.65)/rh
        candidates.append((area/(1+12*dx*dx+3*dy*dy),(ax,ay,bw,bh)))
    if candidates:
        ax,ay,bw,bh=max(candidates)[1];padding=8
        old=list(rect);rect=[old[0]+max(0,ax-padding)/scale,old[1]+max(0,ay-padding)/scale,old[0]+min(rw,ax+bw+padding)/scale,old[1]+min(rh,ay+bh+padding)/scale]
    p['gallery']=[save_image(p['id'],'pdf-24',s['page'],rect,title)]
    products.append(p)

# Family images are explicitly reviewed crops, in normalized full-spread units.
family_crops={
 'a-1-1':(.55,.20,.78,.37),'a-1-2':(.05,.19,.31,.40),'a-1-3':(.55,.17,.82,.40),
 'a-2-1':(.05,.17,.32,.39),'a-2-2':(.55,.19,.82,.38),'a-3':(.05,.47,.44,.74),
 'b-1':(.05,.32,.43,.51),'b-2':(.57,.32,.94,.54),'c-1':(.55,.33,.82,.52),
 'c-2':(.06,.30,.44,.46),'c-3':(.56,.32,.95,.57),'c-4':(.07,.32,.42,.56),
 'c-5':(.57,.18,.77,.43),'c-6':(.55,.63,.77,.88),'d-1':(.05,.36,.42,.54),
 'd-2':(.57,.24,.94,.45),'d-3':(.6,.68,.91,.84),
}
for r in read('product-families.json'):
    if r['recordKind']!='custom-family':continue
    p=base(r,r['name'],'family')
    if not p:
        deferred.append({'id':r['id'],'reason':'Family taxonomy requires review'});continue
    p['attributes']['customization']=['yes']
    p['description']=loc('Familia de empaques personalizados. Las medidas, el material y la impresión se definen para cada proyecto; los intervalos indicados son opciones de fabricación.', 'Custom packaging family. Dimensions, material and printing are defined for each project; the listed ranges are manufacturing options.')
    spec(p,'Tipo de oferta','Offering type','Fabricación personalizada','Custom manufacturing')
    mats=r['materialOptions'];spec(p,'Materiales disponibles','Available materials',', '.join(materials[x]['es'] for x in mats),', '.join(materials[x]['en'] for x in mats))
    labels={'paperWeightGsm':('Gramaje disponible','Available paper weight','g/m²'),'widthMm':('Ancho disponible','Available width','mm'),'heightMm':('Altura disponible','Available height','mm'),'gussetMm':('Fuelle disponible','Available gusset','mm'),'lengthMm':('Longitud disponible','Available length','mm')}
    for k,(es,en,unit) in labels.items():
        if k in r['options']:spec(p,es,en,'–'.join(number(x) for x in r['options'][k])+' '+unit)
    if 'printingColorsMax' in r['options']:
        n=r['options']['printingColorsMax'];spec(p,'Opciones de impresión','Printing options',f'Hasta {n} colores',f'Up to {n} colors')
    sid=r['sources'][0]['sourceId'];pn=r['sources'][0]['page'];pg=page(sid,pn);norm=family_crops[r['id'].removeprefix('jihong-family-')]
    rect=[norm[0]*pg.rect.width,norm[1]*pg.rect.height,norm[2]*pg.rect.width,norm[3]*pg.rect.height]
    p['gallery']=[save_image(p['id'],sid,pn,rect,p['title'],loc('Ejemplos de la familia; diseño y tamaño según proyecto.','Family examples; design and size depend on the project.'))]
    p['solutionIds']=['food-beverage','custom']
    if p['categoryIds'][0]=='bags':p['solutionIds'].append('retail')
    if r['id'].startswith('jihong-family-d-'):p['solutionIds']=['retail','custom']
    products.append(p)

# Remove empty navigation categories and derive filter values from actual records.
filters=[('material',loc('Material','Material'),materials),('product-type',loc('Tipo de producto','Product type'),taxonomy),
 ('capacity',loc('Capacidad','Capacity'),{'up-to-250':loc('Hasta 250 ml','Up to 250 ml'),'251-500':loc('251–500 ml','251–500 ml'),'501-1000':loc('501–1,000 ml','501–1,000 ml'),'over-1000':loc('Más de 1,000 ml','Over 1,000 ml')}),
 ('rim',loc('Diámetro del borde','Rim diameter'),{'up-to-60':loc('Hasta 60 mm','Up to 60 mm'),'61-80':loc('61–80 mm','61–80 mm'),'81-90':loc('81–90 mm','81–90 mm'),'91-100':loc('91–100 mm','91–100 mm'),'over-100':loc('Más de 100 mm','Over 100 mm')}),
 ('size-mode',loc('Tamaños','Sizes'),{'standard':loc('Medidas de catálogo','Catalog sizes'),'custom':loc('A medida','Custom dimensions')}),
 ('customization',loc('Personalización','Customization'),{'yes':loc('Disponible','Available'),'no':loc('No disponible','Unavailable')})]
groups.append(('sustainable',loc('Productos sustentables','Sustainable products'),[]))
categories=[]
category_media=[]
references=read('reference-images.json')
editorial={'cups':'food-packaging-composition','food-containers':'fast-food-composition','bags':'paper-bag-composition','boxes':'kraft-navy-composition','accessories':'food-gift-composition','bakery':'bakery-composition'}
for gid,title,_ in groups:
    items=[p for p in products if gid in p['categoryIds']]
    if not items:continue
    media=dict(items[0]['gallery'][0])
    if gid in editorial:
        ref=next(x for x in references if x['styleTag']==editorial[gid]);im=Image.open(ref['path']).convert('RGB');im.thumbnail((1200,1200));target=ROOT/'public/images/products'/f'category-{gid}.webp';im.save(target,'WEBP',quality=86)
        media={'type':'image','placeholder':False,'src':'/images/products/'+target.name,'ratio':1,'alt':loc('Composición de '+title['es'].lower(),'Composition of '+title['en'].lower()),'caption':loc('Composición ilustrativa de packaging.','Illustrative packaging composition.')}
        category_media.append({'categoryId':gid,'src':media['src'],'sourcePath':ref['path'],'sourceSha256':ref['sha256'],'usage':'User-supplied illustrative category composition; not individual model evidence'})
    description=loc('Explora '+title['es'].lower()+' y compara las opciones disponibles por material, tipo y medidas.','Explore '+title['en'].lower()+' and compare available materials, product types and sizes.')
    if gid=='sustainable':description=loc('Selección de productos identificados como PLA en los catálogos. Consulta las especificaciones y confirma los requisitos de disposición aplicables a tu proyecto.','Products identified as PLA in the catalogs. Review their specifications and confirm the disposal requirements applicable to your project.')
    defs=[]
    for key,label,values in filters:
        used={v for p in items for v in p['attributes'].get(key,[])}
        if len(used)>1:
            defs.append({'key':key,'label':label,'values':[{'id':v,'label':text} for v,text in values.items() if v in used]})
    categories.append({'id':gid,'slug':gid,'title':title,'description':description,'status':'published','order':len(categories)+1,'media':media,'filters':defs})

(ROOT/'src/data/products.json').write_text('[\n'+',\n'.join(json.dumps(p,ensure_ascii=False,separators=(',',':')) for p in products)+'\n]\n',encoding='utf8')
write(ROOT/'src/data/categories.json',categories)
solutions=json.loads((ROOT/'src/data/solutions.json').read_text(encoding='utf8'))
for s in solutions:
    s['productIds']=[p['id'] for p in products if s['id'] in p['solutionIds']]
    if s['id']=='food-beverage':
        s['description']=loc('Vasos, botellas, envases, bandejas y consumibles para alimentos y bebidas. Compara materiales y medidas de catálogo y consulta las opciones de fabricación personalizada para tu negocio.','Cups, bottles, containers, trays and consumables for food and beverages. Compare catalog materials and dimensions, and explore custom manufacturing options for your business.')
    if s['id'] in ('retail','custom'):
        s['description']=loc('Bolsas y cajas de papel y cartón con opciones de fabricación personalizada. El tamaño, material y diseño se definen según los requisitos de cada proyecto.','Paper and board bags and boxes with custom manufacturing options. Size, material and design are defined according to each project’s requirements.')
write(ROOT/'src/data/solutions.json',solutions)
media_log=[m for m in media_log if m['productId'] in {p['id'] for p in products}]
write(AUDIT/'website-media.json',media_log)
write(AUDIT/'website-category-media.json',category_media)
write(AUDIT/'website-deferred.json',deferred)
write(AUDIT/'website-catalog.json',{'schemaVersion':1,'products':len(products),'categories':len(categories),'byCategory':{c['id']:sum(c['id'] in p['categoryIds'] for p in products) for c in categories},'byKind':dict(collections.Counter(p['kind'] for p in products)),'deferred':len(deferred),'productIds':[p['id'] for p in products],'imagePolicy':'Actual PDF photographs for product records; user-supplied compositions only for editorial category media. No AI alterations.'})
# Contact sheets make every extracted asset reviewable without opening 1,000 files.
qa=ROOT/'tmp/catalog-review/website';qa.mkdir(parents=True,exist_ok=True)
for start in range(0,len(media_log),96):
    chunk=media_log[start:start+96];sheet=Image.new('RGB',(1440,1920),'white');draw=ImageDraw.Draw(sheet)
    for i,m in enumerate(chunk):
        im=Image.open(ROOT/'public'/m['src'].lstrip('/'));im.thumbnail((160,135));x=i%8*180;y=i//8*160;sheet.paste(im,(x+(160-im.width)//2,y));draw.text((x,y+137),m['productId'],fill='black')
    sheet.save(qa/f'sheet-{start//96+1:02}.jpg')
print(json.dumps({'products':len(products),'categories':len(categories),'byKind':dict(collections.Counter(p['kind'] for p in products)),'deferred':len(deferred)},ensure_ascii=False))
