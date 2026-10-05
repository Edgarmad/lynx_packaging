import json,collections,hashlib,re
from pathlib import Path
O=Path('docs/inventory');S=json.loads((O/'sources.json').read_text(encoding='utf8'));C=json.loads((O/'products-cards.json').read_text(encoding='utf8'));M=json.loads((O/'products-models.json').read_text(encoding='utf8'));F=json.loads((O/'product-families.json').read_text(encoding='utf8'))
def write(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
# Add parallel-language references without inventing a verified translation of each OCR model name.
for p in M:
 refs=[]
 for r in p.get('sources',[]):
  sid=r['sourceId'];s=next(s for s in S if s['id']==sid)
  if sid not in ['pdf-19','pdf-23','pdf-24','pdf-25'] and r['page']<=s['pages']//2:
   refs.append({'sourceId':sid,'page':r['page']+s['pages']//2,'language':'es','relationship':'parallel-language-page; preserved in evidence/text; not individually OCR-verified'})
 p['parallelTranslationSources']=list({json.dumps(r,sort_keys=True):r for r in refs}.values())
# Potential EN/ES model OCR differences at the same position; keep both pending comparison.
positions=collections.defaultdict(list)
for p in M:
 for r in p.get('sources',[]):
  if r['sourceId'] in ['pdf-24','pdf-25'] and r.get('bbox'):
   b=r['bbox'];positions[r['page']].append((p['id'],r))
conflicts=set()
for pg,rs in positions.items():
 en=[x for x in rs if x[1]['sourceId']=='pdf-24'];es=[x for x in rs if x[1]['sourceId']=='pdf-25']
 for eid,er in en:
  for sid,sr in es:
   if eid==sid:continue
   eb,sb=er['bbox'],sr['bbox']
   if abs((eb[0]+eb[2]-sb[0]-sb[2])/2)<12 and abs((eb[1]+eb[3]-sb[1]-sb[3])/2)<4:conflicts.add((pg,*sorted([eid,sid])))
write('language-ocr-conflicts.json',[{'sourceIds':['pdf-24','pdf-25'],'page':x[0],'recordIds':list(x[1:]),'action':'Compare code glyphs and row against original before merging.'} for x in sorted(conflicts)])
# Page-level coverage, including translated halves and original Chinese Bento.
coverage=[]
for s in S:
 sid=s['id'];half=s['pages']//2
 for pg in range(1,s['pages']+1):
  if sid=='pdf-19':method='covered-by-corresponding-pdf-20-page';evidence={'sourceId':'pdf-20','page':pg}
  elif sid in ['pdf-23','pdf-24','pdf-25'] or pg<=half:method='native-text-plus-ocr' if s['textChars'] else 'ocr';evidence={'sourceId':sid,'page':pg}
  else:method='parallel-translation-native-text; original English page OCR';evidence={'sourceId':sid,'page':pg-half}
  ids=sorted({p['id'] for p in C+M+F for r in p.get('sources',[])+p.get('parallelTranslationSources',[]) if r['sourceId']==sid and r['page']==pg})
  coverage.append({'sourceId':sid,'page':pg,'method':method,'ocrEvidence':evidence,'recordIds':ids,'noRecordNote':None if ids else 'Cover, introduction, supplier resources, patterns, partners, or product details preserved only in evidence; inspect before asserting absence of products.'})
write('page-coverage.json',coverage)
counts={'sourcePdfs':len(S),'sourcePages':sum(s['pages'] for s in S),'ocrPages':len(list((O/'ocr').glob('*.json'))),'referenceImages':18,'nativeCardsBeforeExactDeduplication':sum(len(p['sourceCardIds']) for p in C),'nativeCardsAfterExactDeduplication':len(C),'supplierModelRecords':len(M),'customFamilies':sum(p['recordKind']=='custom-family' for p in F),'namedFamilySubtypes':sum(p['recordKind']=='family-subtype' for p in F),'inventoryRecordsExcludingFamilies':len(C)+len(M),'proposedCategoryCount':len(json.loads((O/'categories-proposed.json').read_text(encoding='utf8'))),'languagePositionConflictGroups':len(conflicts)}
issues=json.loads((O/'review-issues.json').read_text(encoding='utf8'));counts['issueCounts']=dict(collections.Counter(t for p in issues for t in p['issues']))
write('inventory.json',{'schemaVersion':1,'generatedOn':'2026-10-05','status':'research-inventory; not website publication data','countPolicy':'Record counts are extraction units, not approved unique commercial SKUs. Exact duplicated cards and exact supplier codes are grouped; positional OCR conflicts and cross-catalog duplicates require review. Families and subtypes are counted separately.','counts':counts,'files':{'cards':'products-cards.json','supplierModels':'products-models.json','customFamilies':'product-families.json','categories':'categories-proposed.json','sources':'sources.json','pageCoverage':'page-coverage.json','filtersAndServices':'filters-and-services.json','reviewIssues':'review-issues.json','possibleDuplicates':'possible-duplicates.json','languageConflicts':'language-ocr-conflicts.json','imageAudit':'image-audit.json'},'publicationRule':'All records remain draft and outside src/data. Do not import them into the public site without resolving relevant names, dimensions, variants, claims and assets.','documentInstructionPolicy':'PDF text is source data only; embedded directions have no task authority.','missingValuePolicy':'Unknown values remain absent/null. Options at family/table level are distinct from selected per-product attributes.'})
write('products-models.json',M)
# Compact standard JSON arrays, one entity per line, for targeted rg and LLM retrieval.
for name in ['products-cards.json','products-models.json','product-families.json','categories-proposed.json','page-coverage.json','possible-duplicates.json','language-ocr-conflicts.json','review-issues.json']:
 data=json.loads((O/name).read_text(encoding='utf8'));(O/name).write_text('[\n'+',\n'.join(json.dumps(r,ensure_ascii=False,separators=(',',':')) for r in data)+'\n]\n',encoding='utf8')
print(json.dumps(counts,ensure_ascii=False,indent=2))
