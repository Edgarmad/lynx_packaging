import json,pymupdf as fitz,numpy as np,os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from rapidocr import RapidOCR
engine=None
out=Path('docs/inventory/ocr');out.mkdir(exist_ok=True)
def run(task):
 global engine
 if engine is None: engine=RapidOCR(params={'EngineConfig.onnxruntime.intra_op_num_threads':1,'EngineConfig.onnxruntime.inter_op_num_threads':1,'Global.max_side_len':3200})
 sid,path,page,source_hash=task;target=out/f'{sid}-{page:03}.json'
 if target.exists() and json.loads(target.read_text(encoding='utf8')).get('sourceSha256')==source_hash:return sid,page,'cached'
 d=fitz.open(path);p=d[page-1];scale=2800/p.rect.width;pix=p.get_pixmap(matrix=fitz.Matrix(scale,scale));a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,3);r=engine(a)
 lines=[]
 if r.txts:
  for box,txt,score in zip(r.boxes,r.txts,r.scores):lines.append({'text':txt,'confidence':round(float(score),4),'bbox':[round(float(box[:,0].min())/scale,2),round(float(box[:,1].min())/scale,2),round(float(box[:,0].max())/scale,2),round(float(box[:,1].max())/scale,2)]})
 target.write_text(json.dumps({'sourceId':sid,'page':page,'sourceSha256':source_hash,'width':p.rect.width,'height':p.rect.height,'lines':lines},ensure_ascii=False,indent=2),encoding='utf8')
 return sid,page,len(lines)
if __name__=='__main__':
 sources=json.loads(Path('docs/inventory/sources.json').read_text(encoding='utf8'));tasks=[]
 for s in sources:
  # Original bento has exact bilingual derivative; OCR derivative. Master both languages are needed.
  if s['id']=='pdf-19':continue
  count=s['pages'] if s['id'] in ['pdf-23','pdf-24','pdf-25'] else s['pages']//2
  for p in range(1,count+1):tasks.append((s['id'],s['path'],p,s['sha256']))
 with ProcessPoolExecutor(max_workers=3) as pool:
  for i,r in enumerate(pool.map(run,tasks)):
   if i%10==0:print(i,len(tasks),r,flush=True)
