"""Validate the research inventory without publishing or changing website data."""
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs' / 'inventory'


def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def main():
    errors = []
    sources = read('sources.json')
    source_by_id = {s['id']: s for s in sources}
    records = read('products-cards.json') + read('products-models.json') + read('product-families.json')
    ids = [r['id'] for r in records]
    record_by_id = {r['id']: r for r in records}
    categories = read('categories-proposed.json')
    category_ids = {c['id'] for c in categories}
    if len(ids) != len(set(ids)):
        errors.append('Duplicate inventory record IDs')
    if len(sources) != len(source_by_id):
        errors.append('Duplicate source IDs')

    def check_ref(ref, owner):
        source = source_by_id.get(ref['sourceId'])
        if source is None or not 1 <= ref['page'] <= source['pages']:
            errors.append(f'{owner}: invalid page reference {ref}')

    for record in records:
        rid = record['id']
        if record.get('publicationStatus') != 'draft':
            errors.append(f'{rid}: research records must remain draft')
        if record.get('imageStatus') != 'not-extracted':
            errors.append(f'{rid}: unexpected product image processing')
        if not record.get('sources'):
            errors.append(f'{rid}: missing provenance')
        for ref in record.get('sources', []) + record.get('parallelTranslationSources', []) + record.get('reviewedSpecificationsSources', []):
            check_ref(ref, rid)
        for cid in record.get('categoryIds', []):
            if cid not in category_ids:
                errors.append(f'{rid}: unknown category {cid}')
        if record.get('parentFamilyId') and record['parentFamilyId'] not in record_by_id:
            errors.append(f'{rid}: missing family')
        for variant in record.get('variants', []):
            for ref in variant.get('sources', []) + variant.get('partialOcrSources', []):
                check_ref(ref, rid)
            if not all(math.isfinite(v) and v >= 0 for v in variant.get('dimensionValuesCandidate', [])):
                errors.append(f'{rid}: nonfinite or negative candidate dimension')
        if record['recordKind'] == 'catalog-card' and not all(record['name'].get(lang) for lang in ['es', 'en']):
            errors.append(f'{rid}: missing bilingual card label')

    for category in categories:
        if category['recordCount'] != len(category['recordIds']):
            errors.append(f'{category["id"]}: count mismatch')
        for rid in category['recordIds']:
            if rid not in record_by_id or category['id'] not in record_by_id[rid].get('categoryIds', []):
                errors.append(f'{category["id"]}: invalid member {rid}')

    coverage = read('page-coverage.json')
    expected = {(s['id'], page) for s in sources for page in range(1, s['pages'] + 1)}
    actual = {(p['sourceId'], p['page']) for p in coverage}
    if expected != actual or len(actual) != len(coverage):
        errors.append('Page coverage is incomplete or duplicated')
    for page in coverage:
        if any(rid not in record_by_id for rid in page['recordIds']):
            errors.append(f'Coverage {page["sourceId"]}/{page["page"]}: invalid record')
        ev = page['ocrEvidence']
        if not (OUT / 'ocr' / f'{ev["sourceId"]}-{ev["page"]:03}.json').exists():
            errors.append(f'Missing OCR evidence: {ev}')

    for issue in read('review-issues.json'):
        if issue['recordId'] not in record_by_id:
            errors.append(f'Unknown issue record {issue["recordId"]}')
    for filename in ['possible-duplicates.json', 'language-ocr-conflicts.json']:
        for group in read(filename):
            if any(rid not in record_by_id for rid in group['recordIds']):
                errors.append(f'{filename}: invalid related ID')

    for source in sources:
        path = Path(source['path'])
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            errors.append(f'{source["id"]}: original missing or hash changed')
        pages = read(f'evidence/text/{source["id"]}.json')
        if len(pages) != source['pages']:
            errors.append(f'{source["id"]}: native page count mismatch')
    ocr_count = 0
    for path in (OUT / 'ocr').glob('*.json'):
        page = json.loads(path.read_text(encoding='utf-8'))
        check_ref(page, path.name)
        if page['sourceSha256'] != source_by_id[page['sourceId']]['sha256']:
            errors.append(f'{path.name}: stale OCR evidence')
        for line in page['lines']:
            if not 0 <= line['confidence'] <= 1 or len(line['bbox']) != 4:
                errors.append(f'{path.name}: invalid OCR line')
        ocr_count += 1
    counts = read('inventory.json')['counts']
    if counts['sourcePages'] != len(coverage) or counts['ocrPages'] != ocr_count:
        errors.append('Manifest coverage counts mismatch')
    if counts['inventoryRecordsExcludingFamilies'] != sum(r['recordKind'] not in ['custom-family', 'family-subtype'] for r in records):
        errors.append('Manifest inventory count mismatch')
    if counts['proposedCategoryCount'] != len(categories):
        errors.append('Manifest category count mismatch')
    for path in OUT.rglob('*.json'):
        json.loads(path.read_text(encoding='utf-8'))
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Inventory valid: {len(sources)} PDFs, {len(coverage)} source pages, {ocr_count} OCR pages, {len(records)} records including families. All remain draft.')


if __name__ == '__main__':
    main()
