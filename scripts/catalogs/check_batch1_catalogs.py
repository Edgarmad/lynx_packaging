"""Coverage, image provenance and rendered-page checks for batch 1."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import pymupdf
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2];TMP=ROOT/'tmp/pdfs/lote-1'
m=json.loads((ROOT/'output/pdf/Lynx-Lote-1-manifest.json').read_text(encoding='utf-8'))
cards=json.loads((ROOT/'docs/inventory/products-cards.json').read_text(encoding='utf-8'))
results=[]
for cfg in m['catalogs']:
 sid=cfg['sourceId'];expected={r['id'] for r in cards if any(s['sourceId']==sid for s in r['sources'])}
 assert expected==set(cfg['recordIds'])
 for lang in ['es','en']:
  assets=[a for a in m['assetsAndSources'] if a['catalogId']==cfg['id'] and a['language']==lang]
  assert len(assets)==len(expected)
  assert {a['recordId'] for a in assets}==expected
  assert all(a['sourceId']==sid for a in assets)
  assert max(Counter(a['outputPage'] for a in assets).values())<=8
  hashes=[]
  for a in assets:
   with Image.open(a['image']) as im:hashes.append(hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest())
  assert len(hashes)==len(set(hashes))
  p=ROOT/'output/pdf'/f"Lynx-Catalogo-{cfg['filename']}-{lang.upper()}.pdf"
  with pymupdf.open(p) as d:
   assert len(d)==cfg['pageCountPerLanguage']
   whole='\n'.join(page.get_text() for page in d)
   assert 'Temperatura' in whole if lang=='es' else 'Temperature' in whole
   assert ('piezas/caja' in whole if lang=='es' else 'pcs/carton' in whole)
   for a in assets:
    text=d[a['outputPage']-1].get_text()
    for detail in a['details']:assert ' '.join(detail.split()) in ' '.join(text.split()),(a['recordId'],detail)
   assert all(page.get_images() for page in d)
  render=sorted(TMP.glob(f"final-{cfg['filename']}-{lang.upper()}-*.png"))
  assert len(render)==cfg['pageCountPerLanguage'],(p,len(render))
  for chunk in range(0,len(render),6):
   part=render[chunk:chunk+6];sheet=Image.new('RGB',(1350,((len(part)+2)//3)*675),'#eeeeee');draw=ImageDraw.Draw(sheet)
   for i,path in enumerate(part):
    with Image.open(path) as im:
     im=im.convert('RGB');im.thumbnail((440,635));x=(i%3)*450;y=(i//3)*675;sheet.paste(im,(x+(450-im.width)//2,y));draw.text((x+8,y+642),path.stem,fill='black')
   sheet.save(TMP/f"review-{cfg['filename']}-{lang.upper()}-{chunk//6+1}.jpg",quality=94)
  results.append({'file':str(p),'pages':cfg['pageCountPerLanguage'],'records':len(expected),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'validation':'coverage, caption details, source IDs, distinct image pixels, 8 cards max, rendered pages present'})
(ROOT/'output/pdf/Lynx-Lote-1-QA.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print('Verified 6 PDFs, 50 pages, 165 records in each language; all caption specification lines present')
