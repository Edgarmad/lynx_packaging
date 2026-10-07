"""Audita assets existentes y prepara candidatos; no aprueba fotos por similitud."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/catalog-review'
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
plan=read(OUT/'catalog-batches.json')
media=read(ROOT/'docs/inventory/website-media.json')
products=read(ROOT/'src/data/products.json')
sources={s['id']:s for s in plan['sources']}
byrecord=defaultdict(list)
pixels=defaultdict(list)
visual=defaultdict(list)
crop=defaultdict(list)
for m in media:
    p=ROOT/'public'/m['src'].lstrip('/')
    item=dict(m,exists=p.exists())
    if p.exists():
        with Image.open(p) as im:
            im=im.convert('RGB')
            item['decodedPixelHash']=hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest()
            small=im.resize((9,8)).convert('L')
            values=list(small.get_flattened_data()) if hasattr(small,'get_flattened_data') else list(small.getdata())
            bits=''.join('1' if values[y*9+x]>values[y*9+x+1] else '0' for y in range(8) for x in range(8))
            item['dHash']=f'{int(bits,2):016x}'
        pixels[item['decodedPixelHash']].append(m['productId'])
        visual[item['dHash']].append(m['productId'])
    item['sourceHashMatchesInventory']=m.get('sourceSha256')==sources.get(m['sourceId'],{}).get('sha256')
    crop[(m['sourceId'],m['page'],tuple(m['bbox']))].append(m['productId'])
    byrecord[m['productId']].append(item)
paper=read(ROOT/'output/pdf/Lynx-Catalogo-Papel-manifest.json')
paperby=defaultdict(list)
for a in paper['assetsAndSources']:
    if a['language']=='es':
        for rid in a['coveredRecordIds']: paperby[rid].append(a)
assign={a['recordId']:a for a in plan['recordAssignments']}
rows=[]
for c in plan['catalogs']:
    for rid in c['recordIds']:
        if c['id']=='paper':
            rows.append({'catalogId':c['id'],'batch':c['batch'],'recordId':rid,'status':'paper-generated-reviewed','assets':paperby.get(rid,[])})
            continue
        valid=[m for m in byrecord[rid] if m['sourceId'] in c['sourceIds']]
        conflicts=[m for m in valid if len(pixels.get(m.get('decodedPixelHash'),[]))>1 or len(crop[(m['sourceId'],m['page'],tuple(m['bbox']))])>1]
        status='source-image-candidate-needs-visual-check' if valid else 'extract-from-approved-catalog'
        if conflicts: status='repeated-image-or-crop-review-required'
        if any(not m['exists'] or not m['sourceHashMatchesInventory'] for m in valid): status='asset-or-source-integrity-review-required'
        rows.append({'catalogId':c['id'],'batch':c['batch'],'recordId':rid,'name':assign.get(rid,{}).get('name'),'status':status,'assets':valid,'otherSourceAssetsPendingComparison':[m for m in byrecord[rid] if m['sourceId'] not in c['sourceIds']],'sourceRecord':assign.get(rid)})
used=defaultdict(list)
for p in products:
    for g in p.get('gallery',[]):
        if g.get('src'): used[g['src']].append(p['id'])
summary=[]
for c in plan['catalogs']:
    cc=Counter(r['status'] for r in rows if r['catalogId']==c['id'])
    summary.append({'catalogId':c['id'],'title':c['title'],'batch':c['batch'],'statuses':dict(cc)})
result={'date':'2026-10-06','policy':'Correspondencia por ID y fuente como candidato, pendiente de inspección visual. Hash idéntico detecta igualdad; dHash y recorte compartido solo señalan revisión. No sustituir por un producto parecido. ES/EN comparten el asset del mismo producto. Variantes con foto común se agrupan en una ficha con tabla. Cruces aprobados entre catálogos se conservan con su propia fuente.','existingMediaCount':len(media),'websiteProductsCount':len(products),'missingFiles':sum(not x['exists'] for xs in byrecord.values() for x in xs),'sourceHashMismatches':sum(not x['sourceHashMatchesInventory'] for xs in byrecord.values() for x in xs),'samePixelsGroups':[v for v in pixels.values() if len(v)>1],'sameCropGroups':[v for v in crop.values() if len(v)>1],'sameVisualHashCandidateGroups':[v for v in visual.values() if len(v)>1],'websiteSharedPathGroups':[{'src':k,'productIds':v} for k,v in used.items() if len(v)>1],'catalogSummary':summary,'imageAssignments':rows}
(OUT/'catalog-image-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# Identificación de imágenes para los catálogos','', 'Auditoría de assets existentes: 6 de octubre de 2026. No modifica las galerías del sitio.','', f"Revisados automáticamente {len(media)} registros de imágenes y las galerías de {len(products)} productos del proyecto. Archivos ausentes: {result['missingFiles']}; discrepancias de hash fuente contra inventario: {result['sourceHashMismatches']}.", '', f"Grupos con píxeles idénticos: {len(result['samePixelsGroups'])}; recortes de la misma región fuente: {len(result['sameCropGroups'])}; rutas compartidas por varios productos del sitio: {len(result['websiteSharedPathGroups'])}. Estos grupos exigen revisión y no prueban por sí mismos que se trate de productos duplicados.", '', '| Lote | Catálogo | Imagen candidata existente | Repetida / revisar recorte | Extraer de fuente | Papel revisado |','| --- | --- | ---: | ---: | ---: | ---: |']
for c in sorted(summary,key=lambda x:(x['batch'],x['catalogId'])):
    s=c['statuses']
    lines.append(f"| {c['batch']} | {c['title']} | {s.get('source-image-candidate-needs-visual-check',0)} | {s.get('repeated-image-or-crop-review-required',0)} | {s.get('extract-from-approved-catalog',0)} | {s.get('paper-generated-reviewed',0)} |")
lines += ['', '## Regla obligatoria antes de maquetar', '', '1. Identificar ahora: producto/modelo → catálogo aprobado → página → región de imagen → asset local. Mantener la ficha de procedencia.', '2. Reutilizar el asset del proyecto solo después de confirmar visualmente que contiene el producto correcto y procede del catálogo correspondiente.', '3. Para productos diferentes, no reutilizar una foto genérica o el montaje entero. Extraer cada panel; si la fuente no tiene imagen individual, marcar pendiente y no rellenar con otro producto.', '4. Si varias medidas comparten una única foto de familia en la fuente, usar una sola ficha con tabla de variantes, como en Papel.', '5. Detectar repetición por ruta, píxeles y región fuente dentro de cada catálogo; revisar también parecidos con hash visual y hojas de contacto. Cambiar el nombre del archivo no resuelve la repetición.', '6. Usar la misma foto verificada en ES y EN. Conservar productos de fábricas/calidades diferentes entre los catálogos aprobados, revisando la fuente de cada uno.', '7. Cerrar identificación visual por lote antes de generar los PDFs. Revisar de nuevo las páginas renderizadas al terminar.', '', 'La auditoría automática prepara candidatos y señala anomalías; no equivale a una aprobación visual completa de todas las imágenes. El JSON contiene la relación por registro y los grupos que requieren revisión. Las imágenes del Master existentes para registros también presentes en catálogos públicos se conservan como candidatas secundarias: requieren contraste con la página del catálogo correspondiente antes de reutilizarlas.', '', '## Preparación visual inicial', '', 'Hoja de contacto del lote 1 (`catalog-images-L1-contact.jpg`): 24 candidatos, ocho de cada catálogo. Inspeccionada visualmente: los recortes muestran vasos/tapas y sus medidas originales. Hay acabados y formas parecidos que requieren contrastar datos antes de agrupar; no basta con igualdad visual. La inspección detallada de cada página fuente queda dentro de la preparación del lote.']
(OUT/'IMAGENES-CATALOGOS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
sample=[]
for cid in ['cups-10','cups-11','cups-13']:
    sample.extend([r for r in rows if r['catalogId']==cid and r['assets']][:8])
sheet=Image.new('RGB',(1200,((len(sample)+3)//4)*225),'white')
draw=ImageDraw.Draw(sheet)
for i,r in enumerate(sample):
    x=(i%4)*300;y=(i//4)*225
    p=ROOT/'public'/r['assets'][0]['src'].lstrip('/')
    with Image.open(p) as im:
        im=im.convert('RGB');im.thumbnail((280,180));sheet.paste(im,(x+(300-im.width)//2,y))
    draw.text((x+8,y+185),r['recordId'],fill='black')
    draw.text((x+8,y+202),r['catalogId'],fill='black')
sheet.save(OUT/'catalog-images-L1-contact.jpg',quality=90)
print(json.dumps({k:result[k] for k in ['existingMediaCount','websiteProductsCount','missingFiles','sourceHashMismatches']}))
print(json.dumps(summary,ensure_ascii=False))
