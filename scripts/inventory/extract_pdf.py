import pymupdf as fitz,json,hashlib
from pathlib import Path
import os
root=Path(os.environ.get('LYNX_CATALOG_DIR',r'C:/Users/edmad/Downloads/PDFs TRADUCIDOS _ EN-ES'))
out=Path('docs/inventory'); (out/'evidence/text').mkdir(parents=True,exist_ok=True); sources=[]
for n,f in enumerate(sorted(f for f in root.rglob('*.pdf') if f.is_file()),1):
 d=fitz.open(f); sid=f'pdf-{n:02d}'; pages=[]
 for i,p in enumerate(d):
  text='\n'.join(line.strip() for line in p.get_text(sort=True).splitlines() if line.strip())
  images=[{'xref':x[0],'width':x[2],'height':x[3]} for x in p.get_images(full=True)]
  pages.append({'page':i+1,'text':text,'images':images})
 (out/'evidence/text'/f'{sid}.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
 sources.append({'id':sid,'path':str(f),'relativePath':str(f.relative_to(root)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'pages':len(d),'textChars':sum(len(p['text']) for p in pages),'emptyPages':[p['page'] for p in pages if len(p['text'].strip())<30]})
 print(sid,len(d),sources[-1]['textChars'],f.name)
(out/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')

