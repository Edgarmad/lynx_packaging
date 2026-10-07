"""Clasificación documental para PDFs; independiente de la taxonomía web."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'docs/inventory'
OUT = ROOT / 'docs/catalog-review'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

sources = read(BASE / 'sources.json')
cards = read(BASE / 'products-cards.json')
models = read(BASE / 'products-models.json')
families = read(BASE / 'product-families.json')
paper = read(ROOT / 'output/pdf/Lynx-Catalogo-Papel-manifest.json')
covered = set(paper['coveredSourceIds'])
cup_titles = [
    'Bolsas y portavasos', 'Botellas para bebidas calientes', 'Botellas PET',
    'Envases', 'Envases, tarros y cubiertos', 'Fundas y accesorios',
    'Latas de apertura fácil', 'Popotes', 'Tapas por inyección',
    'Vasos IML', 'Vasos por inyección', 'Vasos de papel',
    'Vasos y tapas PET', 'Catálogo PET',
]
batch_cups = {1:'L3',2:'L2',3:'L2',4:'L3',5:'L3',6:'L3',7:'L2',8:'L3',9:'L4',10:'L1',11:'L1',12:'L4',13:'L1',14:'L2'}
catalogs = [{'id':'paper','group':'Papel','title':'Empaques de papel','batch':'L0','sourceIds':['pdf-15','pdf-16','pdf-17','pdf-18','pdf-01','pdf-04','pdf-06','pdf-12'],'status':'generated','recordIds':sorted(covered),'galleryCards':243}]
for i, title in enumerate(cup_titles,1):
    sid = f'pdf-{i:02d}'
    ids = [r['id'] for r in cards if any(s['sourceId']==sid for s in r['sources'])]
    catalogs.append({'id':f'cups-{i:02d}','group':'Vasos y accesorios','title':title,'batch':batch_cups[i],'sourceIds':[sid],'status':'classified-needs-editorial-review','recordIds':ids})
plastic = [('plastic-cups','Vasos de plástico',['pdf-23'],'L5'),('plastic-bakery','Repostería',['pdf-22'],'L5'),('plastic-bento','Bento, carne y bandejas',['pdf-20'],'L6'),('plastic-fruit','Frutas y verduras',['pdf-21'],'L6'),('plastic-eggs','Envases para huevos',['pdf-24','pdf-25'],'L5')]
for cid,title,sids,batch in plastic:
    ids = [r['id'] for r in models if ('egg-containers' in r.get('categoryIds',[]) if cid=='plastic-eggs' else any(s['sourceId'] in sids for s in r['sources']))]
    catalogs.append({'id':cid,'group':'Plástico','title':title,'batch':batch,'sourceIds':sids,'status':'classified-needs-editorial-review','recordIds':ids,'sourcePageRestriction':85 if cid=='plastic-eggs' else None})
catalogs.append({'id':'sustainable','group':'Sostenible','title':'Empaques sostenibles','batch':'L7','sourceIds':[],'status':'source-not-located','recordIds':[]})
assert len(catalogs)==21
batch1_manifest=ROOT/'output/pdf/Lynx-Lote-1-manifest.json'
batch1_qa=ROOT/'output/pdf/Lynx-Lote-1-QA.json'
if batch1_manifest.exists() and batch1_qa.exists():
    completed=read(batch1_manifest)
    for c in catalogs:
        match=next((x for x in completed['catalogs'] if x['id']==c['id']),None)
        if match and all((ROOT/'output/pdf'/f"Lynx-Catalogo-{match['filename']}-{lang}.pdf").exists() for lang in ['ES','EN']):
            assert set(c['recordIds'])==set(match['recordIds'])
            c['status']='generated-reviewed'
            c['pageCountPerLanguage']=match['pageCountPerLanguage']
remaining=2*sum(c['status'] not in ['generated','generated-reviewed'] for c in catalogs)
assignments = []
for r in cards+models+families:
    cids = [c['id'] for c in catalogs if r['id'] in c['recordIds']]
    paper_variant_ids = [rid for rid in covered if rid.startswith(r['id']+'-v')]
    if paper_variant_ids and 'paper' not in cids:
        cids.append('paper')
    sids = sorted({s['sourceId'] for s in r.get('sources',[])})
    candidates=[]
    if not cids and set(sids)&{'pdf-24','pdf-25'}:
        cats=set(r.get('categoryIds',[]))
        if cats&{'plastic-cups'}: candidates.append('plastic-cups')
        if cats&{'bakery-containers'}: candidates.append('plastic-bakery')
        if cats&{'fruit-vegetable-containers','cut-fruit-containers'}: candidates.append('plastic-fruit')
        if cats&{'meat-trays','food-trays','food-containers','salad-containers','cold-noodle-containers','map-trays','skin-pack-trays','frozen-food-containers'}: candidates.append('plastic-bento')
    assignments.append({'recordId':r['id'],'recordKind':r['recordKind'],'name':r.get('name'),'supplierGroup':r.get('supplierGroup'),'modelCode':r.get('modelCode'),'sourceIds':sids,'catalogIds':cids,'paperVariantRecordIds':paper_variant_ids,'candidateCatalogIds':candidates,'status':'assigned-by-approved-source' if cids else ('master-only-pending-scope' if set(sids)&{'pdf-24','pdf-25'} else 'paper-source-not-in-current-edition'),'reviewStatus':r.get('reviewStatus')})
master_pending=[a for a in assignments if a['status']=='master-only-pending-scope']
plan={'date':'2026-10-06','policy':'Fuentes aprobadas determinan el catálogo. No usar Excel/menús web. Conteos de extracción, no SKU únicos ni páginas finales. No eliminar cruces entre catálogos/fábricas. Master privado; sus registros exclusivos, salvo huevos, requieren revisión de alcance.','catalogCount':21,'outputPdfCount':42,'remainingPdfCount':remaining,'catalogs':catalogs,'masterPendingRecordCount':len(master_pending),'sustainableSourceLocated':False,'sources':sources,'recordAssignments':assignments}
(OUT/'catalog-batches.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# Plan de producción de catálogos por lotes','', 'Fecha: 6 de octubre de 2026. Clasificación de trabajo para los PDFs, separada del menú de productos del sitio.','', '21 catálogos lógicos, 42 PDFs ES/EN. Papel ya generado: quedan 20 catálogos / 40 archivos. Los títulos son nombres de trabajo basados en los archivos entregados.','', '| Lote | Catálogo | Grupo | Fuente | Registros de extracción |','| --- | --- | --- | --- | ---: |']
for c in sorted(catalogs,key=lambda c:(c['batch'],c['id'])):
    lines.append(f"| {c['batch']} | {c['title']} | {c['group']} | {', '.join(c['sourceIds']) or 'Pendiente de localizar'} | {len(c['recordIds']) if c['sourceIds'] else 'Pendiente'} |")
lines[4]=f'21 catálogos lógicos, 42 PDFs ES/EN. Generados {42-remaining} archivos; quedan {remaining//2} catálogos / {remaining} PDFs. Papel y lote 1 terminados. Los títulos son nombres de trabajo basados en los archivos entregados.' if remaining<40 else lines[4]
lines += ['', '## Orden y propósito de cada lote','', '- **L0 — Papel:** terminado. Se conserva como referencia visual y técnica.', '- **L1 — Vasos IML, inyección y PET con tapas:** primer lote de tres catálogos; adaptar la extracción WHYJ y comprobar la plantilla común.', '- **L2 — Botellas y PET:** cuatro catálogos; reutilizar composición y tablas de capacidades, conservando cada fuente.', '- **L3 — Accesorios y envases:** cinco catálogos; revisar especialmente materiales mixtos, bolsas, cubiertos y fundas.', '- **L4 — Vasos de papel y tapas por inyección:** dos catálogos con mayor volumen; mantener compatibilidades de tapas únicamente si están documentadas.', '- **L5 — Plástico: vasos, repostería y huevos:** tres catálogos; resolver la extracción QUNLU y el recorte del Master.', '- **L6 — Plástico: bento y frutas/verduras:** dos catálogos de mayor volumen, una vez validado el tratamiento QUNLU.', '- **L7 — Sostenible:** un catálogo, condicionado a localizar la fuente específica aprobada.', '', '## Clasificación y cruces', '', '- El grupo “Vasos” incluye sus 14 archivos completos, aunque algunos contengan botellas, envases, bolsas o cubiertos. No reorganizarlos por material ni trasladarlos al menú web.', '- Cada registro conserva sus asignaciones múltiples. Los cruces Papel/Vasos y Plástico/Vasos se mantienen; parecerse no prueba que sean el mismo producto o fábrica.', '- Bento original pdf-19 y traducción pdf-20 son fuentes del mismo catálogo, no dos entregables. Jihong completo/China y helados/V5 alimentan el único catálogo de papel.', '- Huevos: 52 registros de investigación en la página 85 del Master EN y ES. Ese conteo requiere contrastar títulos, códigos y variantes antes de definir las fichas finales.', f'- **{len(master_pending)} registros exclusivos del Master** quedan separados de los catálogos públicos y con categorías candidatas cuando hay evidencia. No se incorporan automáticamente: algunos corresponden a película o presentan conflictos OCR.', '- Sostenible: no hay un PDF específico identificable entre los 25 archivos inventariados de la carpeta entregada. No construirlo agrupando productos que parezcan ecológicos ni inventar certificaciones.', '', '## Ejecución y control por lote', '', '1. Confirmar páginas ES/EN, extraer imágenes originales y asociarlas a registros con procedencia.', '2. Corregir traducciones/OCR, separar fotos de montajes y agrupar variantes solo cuando comparten un producto documentado.', '3. Generar ambas versiones desde un único conjunto de datos; conservar diseño premium y marca de agua Lynx. Retirar notas internas y elementos del proveedor.', '4. Comprobar cobertura de registros, unidades, nombres y tablas. Renderizar y revisar ambos PDFs; cerrar el lote antes de avanzar.', '', 'El número de fichas y páginas se fijará después de revisar variantes y conflictos; los registros de extracción no representan cantidades comerciales únicas. La estimación inicial de 4–8 horas debe revisarse al cerrar L1, con una medida real del tratamiento por lote.', '', '## Archivos de trabajo', '', '- `catalog-batches.json`: 21 catálogos, fuentes y asignación por ID de todos los registros del inventario.', '- `scripts/catalogs/plan_catalog_batches.py`: reproduce esta clasificación sin modificar los datos públicos.', '', 'Esta etapa clasifica y planifica; no genera nuevos PDFs, no sube archivos ni modifica el sitio.']
lines += ['', '## Identificación de imágenes antes de producir cada lote', '', 'Identificar desde ahora: producto/modelo → catálogo aprobado → página → región de foto → asset local. La auditoría inicial se encuentra en IMAGENES-CATALOGOS.md y catalog-image-audit.json.', '', 'Antes de maquetar cada lote, cerrar la correspondencia visual de todos sus productos. No repetir una foto entre fichas de productos diferentes ni reutilizar montajes genéricos: recortar el producto correspondiente del catálogo. Las variantes con una única foto común se agrupan en una ficha con tabla. ES y EN comparten la imagen verificada del mismo producto.', '', 'Contrastar cualquier asset procedente del Master con la página del catálogo público correspondiente. Si falta la foto correcta, dejar pendiente de extracción; no sustituir por otra parecida. Verificar repeticiones por ruta, píxeles y región fuente, y revisar hojas de contacto y páginas finales.']
if remaining<40:lines += ['', '## Lote 1 completado', '', 'IML: 39 registros, 6 páginas por idioma. Inyección: 52 registros, 8 páginas por idioma. PET con tapas: 74 registros, 11 páginas por idioma. Se generaron y revisaron los seis PDFs; 165 registros en ambos idiomas. Medición y decisiones en lote-1/RESULTADO-Y-MEDICION.md. El siguiente lote es L2.']
(OUT/'PLAN-LOTES-CATALOGOS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'catalogs':len(catalogs),'assignments':len(assignments),'masterPending':len(master_pending),'batches':dict(Counter(c['batch'] for c in catalogs))},ensure_ascii=False))
