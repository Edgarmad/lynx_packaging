"""Validate the complete bilingual set, render every page, and create the delivery bundle."""
import json,hashlib,zipfile,html,subprocess,concurrent.futures,collections
from pathlib import Path
from datetime import datetime,timezone
import pymupdf
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/pdf';TMP=ROOT/'tmp/pdfs/all-catalogs';QA=TMP/'final-qa';QA.mkdir(exist_ok=True)
POPPLER='C:/Users/edmad/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
manifest=read(TMP/'final-generated-manifest.json');paper=read(OUT/'Lynx-Catalogo-Papel-manifest.json');batch1=read(OUT/'Lynx-Lote-1-manifest.json')
paper_records=[]
for r in paper['assetsAndSources']:
 if r['language']=='es':paper_records.append({'id':r['recordId'],'coveredIds':r['coveredRecordIds'],'image':r['image'],'source':r['source'],'name':{'es':r['recordId'],'en':r['recordId']}})
manifest['catalogs'].insert(0,{'id':'paper','group':{'es':'Papel','en':'Paper'},'title':{'es':'Empaques de papel','en':'Paper packaging'},'filename':'Papel','records':paper_records,'cardCount':paper['recordCount'],'coveredRecordCount':paper['coveredSourceRecordCount'],'pageCountPerLanguage':paper['pageCountPerLanguage'],'outputs':[str(OUT/f'Lynx-Catalogo-Papel-{l}.pdf') for l in ['ES','EN']]})
for c in batch1['catalogs']:
 records=[{'id':r['id'],'coveredIds':[r['id']],'name':r['name'],'image':r['images']['en'],'source':{'sourceId':c['sourceId'],'page':r['sourcePages']['en'],'bbox':r['bbox']},'details':r['details'],'variants':[]} for r in c['preparedRecords']]
 manifest['catalogs'].append({**c,'group':{'es':'Vasos y accesorios','en':'Cups and accessories'},'records':records,'cardCount':len(records),'coveredRecordCount':len(records),'outputs':[str(OUT/f"Lynx-Catalogo-{c['filename']}-{l}.pdf") for l in ['ES','EN']]})
assert len(manifest['catalogs'])==21
assert len({c['id'] for c in manifest['catalogs']})==21
files=[Path(f) for c in manifest['catalogs'] for f in c['outputs']];assert len(files)==42 and len(set(files))==42
assert set(files)==set(OUT.glob('Lynx-Catalogo-*.pdf'))
pixels=collections.defaultdict(list);references=collections.defaultdict(list);near=[];checks=[]
for cfg in manifest['catalogs']:
 for r in cfg['records']:
  with Image.open(r['image']) as im:
   im=im.convert('RGB');h=hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest();pixels[h].append([cfg['id'],r['id']]);a=np.asarray(im.convert('L').resize((9,8)));ph=int.from_bytes(np.packbits(a[:,1:]>a[:,:-1]).tobytes(),'big')
   near.append((ph,cfg['id'],r))
  s=r['source']
  if isinstance(s,dict) and s.get('bbox'):references[(s['sourceId'],s['page'],tuple(round(x,1) for x in s['bbox']))].append([cfg['id'],r['id']])
 for target in cfg['outputs']:
  with pymupdf.open(target) as doc:
   assert len(doc)==cfg['pageCountPerLanguage']
   txt='\n'.join(p.get_text() for p in doc)
   for bad in ['\ufffd','REVIEW EDITION','Reference image','Imagen de referencia','Notas de esta edición','TIidt','Sources used']:
    assert bad not in txt,(target,bad)
   for p in doc:
    assert p.get_text().strip()
    for b in p.get_text('blocks'):assert b[0]>=-1 and b[1]>=-1 and b[2]<=p.rect.width+1 and b[3]<=p.rect.height+1,(target,p.number,b[:4])
   checks.append({'file':target,'pages':len(doc),'bytes':Path(target).stat().st_size,'sha256':hashlib.sha256(Path(target).read_bytes()).hexdigest()})
duplicate_pixels=[v for v in pixels.values() if len(v)>1];duplicate_regions=[v for v in references.values() if len(v)>1]
assert not duplicate_pixels,duplicate_pixels
assert not duplicate_regions,duplicate_regions
near_pairs=[]
for i,(ph,cid,r) in enumerate(near):
 for pp,cc,rr in near[:i]:
  dist=(ph^pp).bit_count()
  if dist<=2:near_pairs.append({'distance':dist,'items':[[cid,r['id'],r['name']['en'],r['image']],[cc,rr['id'],rr['name']['en'],rr['image']]]})
(QA/'near-pairs.json').write_text(json.dumps(near_pairs,ensure_ascii=False,indent=2),encoding='utf-8')
for start in range(0,len(near_pairs),8):
 out=Image.new('RGB',(850,8*180),'white');d=ImageDraw.Draw(out)
 for i,pair in enumerate(near_pairs[start:start+8]):
  for k,item in enumerate(pair['items']):
   im=Image.open(item[3]).convert('RGB');im.thumbnail((390,145));x=k*425;y=i*180;out.paste(im,(x,y));d.text((x,y+145),str(start+i)+' '+item[0]+' '+item[2][:42],fill='black');d.text((x,y+160),item[1],fill='black')
 out.save(QA/f'near-review-{start//8+1}.jpg')
def render(target):
 path=QA/target.stem;path.mkdir(exist_ok=True)
 subprocess.run([POPPLER,'-jpeg','-scale-to','900',str(target),str(path/'page')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 pages=sorted(path.glob('page-*.jpg'));count=len(pymupdf.open(target));assert len(pages)==count,(target,len(pages),count)
 return target.name,len(pages)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for name,count in pool.map(render,files):print('RENDERED',name,count,flush=True)
rendered=[]
for f in files:
 for page in sorted((QA/f.stem).glob('page-*.jpg')):rendered.append((f.name,page))
for start in range(0,len(rendered),24):
 out=Image.new('RGB',(1200,6*297),'white');d=ImageDraw.Draw(out)
 for i,(name,p) in enumerate(rendered[start:start+24]):
  im=Image.open(p);im.thumbnail((288,273));x=(i%4)*300;y=(i//4)*297;out.paste(im,(x,y));d.text((x,y+273),name.replace('Lynx-Catalogo-','')[:36]+' '+p.stem,fill='black')
 out.save(QA/f'pages-review-{start//24+1:02d}.jpg')
result={'createdAt':datetime.now(timezone.utc).isoformat(),'catalogCount':21,'pdfCount':42,'totalPages':sum(c['pages'] for c in checks),'totalProductCards':sum(c['cardCount'] for c in manifest['catalogs']),'coveredSourceRecords':sum(c['coveredRecordCount'] for c in manifest['catalogs']),'aiImageCalls':0,'exactRepeatedPhotoCount':0,'sharedSourceRegionCount':0,'nearImagePairsForVisualReview':len(near_pairs),'pdfs':checks,'allPagesRendered':True,'visualReviewStatus':'awaiting inspection of latest rendered contact sheets','scopeNotes':['Paper cups separated from Paper.','Shared source photographs displayed once with size/model variants.','Distinct source factories and genuine photo/color variants retained.','Original text inventory supplemented with uncoded product panels.','Sustainable product examples extracted from the approved Upack supplier brochure; supplier corporate claims excluded.','ES and EN intentionally use the same photograph for the same product.','Plastic Master remains private and is not included as a public catalog.']}
(OUT/'Lynx-Catalogos-QA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'Lynx-Todos-Catalogos-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
order={'paper':0,'sustainable':2};manifest['catalogs'].sort(key=lambda c:(order.get(c['id'],1 if c['id'].startswith('plastic-') else 3),c['id']))
rows=[]
for c in manifest['catalogs']:
 rows.append('<tr><td>'+html.escape(c['title']['es'])+'</td><td>'+str(c['cardCount'])+'</td><td>'+str(c['pageCountPerLanguage'])+'</td>'+''.join('<td><a href="'+html.escape(Path(f).name)+'">'+l+'</a></td>' for l,f in zip(['Español','English'],c['outputs']))+'</tr>')
index='''<!doctype html><html lang="es"><meta charset="utf-8"><title>Catálogos Lynx</title><style>body{font:16px Arial;background:#182037;color:#fff;max-width:1100px;margin:40px auto;padding:20px}h1{color:#f3dfab}table{width:100%;border-collapse:collapse}th,td{padding:12px;border-bottom:1px solid #65738d;text-align:left}a{color:#f3dfab}p{line-height:1.6}</style><h1>Catálogos Lynx Packaging</h1><p>21 catálogos · 42 PDF · Español e inglés separados. Los vasos de papel tienen su catálogo propio. Fotografías originales; variantes con una foto compartida reunidas en una tabla.</p><table><thead><tr><th>Catálogo</th><th>Fichas</th><th>Páginas por idioma</th><th>Español</th><th>English</th></tr></thead><tbody>'''+''.join(rows)+'</tbody></table></html>'
(OUT/'Indice-Catalogos-Lynx.html').write_text(index,encoding='utf-8')
readme='''CATÁLOGOS LYNX PACKAGING — 6 DE OCTUBRE DE 2026

21 catálogos / 42 PDF. Español e inglés separados.
Papel: los vasos se separaron en Vasos de papel.
Fotografías extraídas de los PDF originales. No se generaron imágenes de IA.
Cuando la fuente repite una foto para tamaños/pesos/modelos distintos, se muestra una sola ficha con tabla de variantes.
Se conservaron las variantes de color y los productos de fuentes/fábricas diferentes.
Las mismas fotos se usan para el mismo producto en ES y EN.
Se añadieron productos sin código que faltaban en la extracción inicial.
El sostenible contiene ejemplos de empaques de la presentación Upack del Drive aprobado; no transfiere a Lynx cifras, fábricas ni certificaciones del proveedor.
El Master de plástico es privado y no se incluye como catálogo público.
'''
(OUT/'LEEME-Catalogos-Lynx.txt').write_text(readme,encoding='utf-8')
archive=OUT/'Lynx-Catalogos-Completos-ES-EN.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for c in manifest['catalogs']:
  group='01-Papel' if c['id']=='paper' else '02-Plastico' if c['id'].startswith('plastic-') else '03-Sostenible' if c['id']=='sustainable' else '04-Vasos-Accesorios'
  for f in c['outputs']:
   lang='ES' if Path(f).stem.endswith('-ES') else 'EN';z.write(f,group+'/'+lang+'/'+Path(f).name)
 z.writestr('LEEME.txt',readme)
print(json.dumps({k:v for k,v in result.items() if k not in ['pdfs','scopeNotes']},ensure_ascii=False),flush=True)
print('ARCHIVE',archive.stat().st_size,flush=True)
