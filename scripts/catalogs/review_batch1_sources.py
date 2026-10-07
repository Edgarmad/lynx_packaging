import json
from pathlib import Path
from PIL import Image, ImageDraw
import pymupdf

ROOT=Path(__file__).resolve().parents[2]
TMP=ROOT/'tmp/pdfs/lote-1';TMP.mkdir(parents=True,exist_ok=True)
media=json.loads((ROOT/'docs/inventory/website-media.json').read_text(encoding='utf-8'))
items=[m for m in media if m['sourceId'] in ['pdf-10','pdf-11','pdf-13']]
for k in range(0,len(items),30):
    part=items[k:k+30]
    sheet=Image.new('RGB',(1200,((len(part)+4)//5)*215),'white');draw=ImageDraw.Draw(sheet)
    for i,r in enumerate(part):
        im=Image.open(ROOT/'public'/r['src'].lstrip('/')).convert('RGB');im.thumbnail((225,185))
        x=(i%5)*240;y=(i//5)*215
        sheet.paste(im,(x+(240-im.width)//2,y));draw.text((x+4,y+190),r['productId'],fill='black')
    sheet.save(TMP/f'source-contact-{k//30+1}.jpg',quality=94)
sources=json.loads((ROOT/'docs/inventory/sources.json').read_text(encoding='utf-8'))
for s in sources:
    if s['id'] not in ['pdf-10','pdf-11','pdf-13']:continue
    with pymupdf.open(s['path']) as doc:
        for p in range(1,s['pages']//2):
            doc[p].get_pixmap(matrix=pymupdf.Matrix(1.2,1.2)).save(TMP/f"{s['id']}-source-{p+1}.png")
print('165 source assets; 20 source pages prepared for review')
