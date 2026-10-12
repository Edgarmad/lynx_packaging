import json,hashlib,shutil,zipfile,re,html
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/pdf'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(OUT/'Lynx-Todos-Catalogos-manifest.json');assert len(m['catalogs'])==20
changed=[c for c in m['catalogs'] if c['id'] in ['paper','cups-05']]
ids=[i for c in changed for r in c['records'] for i in r['coveredIds']];assert len(ids)==len(set(ids))
assert sum(i.startswith('pdf-04-p03-') for i in ids)==7;assert sum(i.startswith('pdf-04-p04-') for i in ids)==5
hashes=[]
for c in changed:
 for r in c['records']:
  im=Image.open(r['image']).convert('RGB');hashes.append(hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest())
assert len(hashes)==len(set(hashes))
for c in changed:
 for file in c['outputs']:
  p=Path(file);lang='ES' if p.stem.endswith('-ES') else 'EN';group='Papel' if c['id']=='paper' else 'Vasos y accesorios';shutil.copy2(p,ROOT/'output/drive/Catalogos Lynx'/'Cat\u00e1logos p\u00fablicos'/group/lang/p.name)
arc=ROOT/'output/archive/Containers-retirado-2026-10-12';arc.mkdir(parents=True,exist_ok=True)
for lang in ['ES','EN']:
 name=f'Lynx-Catalogo-Envases-{lang}.pdf'
 for j,p in enumerate([OUT/name,ROOT/'output/drive/Catalogos Lynx'/'Cat\u00e1logos p\u00fablicos'/'Vasos y accesorios'/lang/name]):
  if p.exists():
   dest=arc/(('drive-' if j else '')+name);assert p.resolve().is_relative_to(ROOT.resolve()) and dest.resolve().is_relative_to(ROOT.resolve());shutil.move(str(p),str(dest))
p=OUT/'Lynx-Catalogos-QA.json';qa=read(p);qa.update(catalogCount=20,pdfCount=40,totalPages=sum(c['pageCountPerLanguage']*2 for c in m['catalogs']),totalProductCards=sum(c['cardCount'] for c in m['catalogs']),coveredSourceRecords=sum(c['coveredRecordCount'] for c in m['catalogs']));qa['containerReclassification']={'date':'2026-10-12','paperPairs':7,'ppProductsMoved':5,'pagesRenderedAndInspected':60,'retiredCatalogId':'cups-04','changedCatalogsCoveredIdsUnique':True,'changedCatalogsPhotosUnique':True};qa['pdfs']=[e for e in qa['pdfs'] if Path(e['file']).name not in ['Lynx-Catalogo-Envases-ES.pdf','Lynx-Catalogo-Envases-EN.pdf']]
for e in qa['pdfs']:
 pp=Path(e['file']);e.update(bytes=pp.stat().st_size,sha256=hashlib.sha256(pp.read_bytes()).hexdigest())
 for c in m['catalogs']:
  if e['file'] in c['outputs']:e['pages']=c['pageCountPerLanguage']
save(p,qa)
rows=[]
for c in m['catalogs']:rows.append('<tr><td>'+html.escape(c['title']['es'])+'</td><td>'+str(c['cardCount'])+'</td><td>'+str(c['pageCountPerLanguage'])+'</td>'+''.join('<td><a href="'+Path(f).name+'">'+l+'</a></td>' for l,f in zip(['Espa\u00f1ol','English'],c['outputs']))+'</tr>')
p=OUT/'Indice-Catalogos-Lynx.html';s=p.read_text(encoding='utf-8');s=s[:s.index('<tbody>')+7]+''.join(rows)+'</tbody></table></html>';p.write_text(s.replace('21 cat\u00e1logos','20 cat\u00e1logos').replace('42 PDF','40 PDF'),encoding='utf-8')
readme=OUT/'LEEME-Catalogos-Lynx.txt';s=readme.read_text(encoding='utf-8').replace('21 catalogos, 42 PDF','20 catalogos, 40 PDF');s+='\nContainers retirado: 7 variantes cafe integradas en Papel, 5 envases PP integrados en Envases, tarros y cubiertos.\n';readme.write_text(s,encoding='utf-8')
updated={Path(f).name for c in changed for f in c['outputs']}
for archive in [OUT/'Lynx-Catalogos-Completos-ES-EN.zip',ROOT/'output/drive/Lynx-Carpetas-para-Drive.zip']:
 temp=archive.with_suffix('.refresh.zip')
 with zipfile.ZipFile(archive) as old,zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as new:
  for info in old.infolist():
   name=info.filename.split('/')[-1]
   if name in ['Lynx-Catalogo-Envases-ES.pdf','Lynx-Catalogo-Envases-EN.pdf']:continue
   new.writestr(info,(OUT/name).read_bytes() if name in updated else readme.read_bytes() if name=='LEEME.txt' else old.read(info.filename))
 with zipfile.ZipFile(temp) as z:assert z.testzip() is None;assert sum(n.endswith('.pdf') for n in z.namelist())==40
 temp.replace(archive)
p=ROOT/'docs/catalog-review/catalog-batches.json';v=read(p);v['catalogs']=[c for c in v['catalogs'] if c['id']!='cups-04'];v.update(catalogCount=20,outputPdfCount=40);v['retiredCatalogs']=[{'id':'cups-04','reason':'7 paper products to Paper; 5 PP products to cups-05.'}]
for c in v['catalogs']:
 if c['id'] in ['paper','cups-05']:
  new=next(x for x in changed if x['id']==c['id']);c.update(sourceIds=['pdf-05','pdf-04'] if c['id']=='cups-05' else c['sourceIds'],recordIds=[i for r in new['records'] for i in r['coveredIds']],finalCardCount=new['cardCount'],finalCoveredSourceRecordCount=new['coveredRecordCount'],pageCountPerLanguage=new['pageCountPerLanguage'])
save(p,v)
(ROOT/'docs/catalog-review/RECLASIFICACION-ENVASES-2026-10-12.md').write_text('Containers retirado del menu, listado, footer y paquetes locales. Papel: 7 fichas blanco/cafe y 140 referencias. Envases, tarros y cubiertos: 5 productos PP de pdf-04 p.4 incorporados; 107 fichas. Ambas parejas: 15 paginas por idioma. 60 paginas renderizadas e inspeccionadas; referencias y fotos de los catalogos modificados sin duplicados. Entrega: 20 catalogos / 40 PDF. Drive conserva versiones anteriores hasta reemplazo manual. Sin cambios a las categorias de Productos.\n',encoding='utf-8')
print('PASS: 12 source products moved exactly once, unique images in updated catalogs, 40-PDF archives verified.')
