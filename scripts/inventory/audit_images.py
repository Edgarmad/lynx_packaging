import json,collections,pymupdf as f
from pathlib import Path
s=json.loads(Path('docs/inventory/sources.json').read_text(encoding='utf8'));out=[]
for x in s:
 d=f.open(x['path']);seen={};refs=0
 for p in d:
  for a in p.get_images(full=True):seen[a[0]]=(a[2],a[3]);refs+=1
 dims=list(seen.values());v={'sourceId':x['id'],'distinctEmbeddedImages':len(dims),'imageOccurrences':refs,'minImageDimensions':min(dims,key=lambda z:z[0]*z[1]) if dims else None,'maxImageDimensions':max(dims,key=lambda z:z[0]*z[1]) if dims else None,'samplePageImages': [{'width':a[2],'height':a[3]} for a in d[min(1,len(d)-1)].get_images(full=True)]};out.append(v)
Path('docs/inventory/image-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('\n'.join(v['sourceId']+' '+str(v['distinctEmbeddedImages'])+' '+str(v['maxImageDimensions'])+' '+str(v['samplePageImages'][:3]) for v in out))
p=json.loads(Path('docs/inventory/products-cards.json').read_text(encoding='utf8'));m=json.loads(Path('docs/inventory/products-models.json').read_text(encoding='utf8'));print('Missing ES cards',sum(not x['name']['es'] for x in p));print('models with dims',sum(bool(x['variants'] or x.get('reviewedSpecifications')) for x in m));print('materials',collections.Counter(a for x in p+m for a in x.get('materialIds',[])))
