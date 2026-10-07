"""Use product photographs from the approved Upack brochure, not its corporate claims."""
import importlib.util,json,io,hashlib
from pathlib import Path
import pymupdf
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('catalog_renderer',ROOT/'scripts/catalogs/build_all_catalogs.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=m.TMP/'Upack_English_Espanol.pdf';doc=pymupdf.open(source)
cfg={'id':'sustainable','sourceIds':['upack-approved-drive'],'filename':'Sostenible','title':m.tx('Empaques sostenibles','Sustainable packaging'),'group':m.tx('EMPAQUES SOSTENIBLES | LYNX','SUSTAINABLE PACKAGING | LYNX'),'intro':m.tx('Opciones de empaque de papel para bebidas, alimentos y comercios. Descubre presentaciones y aplicaciones para tu proyecto.','Paper packaging options for beverages, food and retail. Explore presentations and applications for your project.'),'families':m.tx('Bolsas de papel\nFundas para bebidas\nEmpaques para alimentos\nBolsas comerciales\nRecipientes con recubrimiento base agua','Paper bags\nBeverage sleeves\nFood packaging\nRetail bags\nContainers with water-based coating')}
items=[]
def add(pid,pg,box,name,details):
 p=doc[pg-1];info=max(p.get_image_info(xrefs=True),key=lambda x:(x['bbox'][2]-x['bbox'][0])*(x['bbox'][3]-x['bbox'][1]));original=Image.open(io.BytesIO(doc.extract_image(info['xref'])['image'])).convert('RGB');b=info['bbox'];sx=original.width/(b[2]-b[0]);sy=original.height/(b[3]-b[1]);target=m.TMP/(pid+'.png');original.crop(tuple(round((v-b[i%2])*([sx,sy][i%2])) for i,v in enumerate(box))).save(target)
 items.append({'id':pid,'coveredIds':[pid],'name':name,'image':str(target),'details':details,'variants':[],'source':{'sourceId':'upack-approved-drive','page':pg,'bbox':box,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest()}})
# The beverage page displays nine distinct paper-bag designs in a photo panel.
for row in range(3):
 for col in range(3):
  add(f'upack-beverage-bag-{row+1}-{col+1}',15,[615+col*76,160+row*105,685+col*76,259+row*105],m.tx(f'Bolsa para bebidas | Diseño {row*3+col+1:02d}',f'Beverage bag | Design {row*3+col+1:02d}'),[m.tx('Material: papel','Material: paper')])
families=[(16,'Fundas de papel para bebidas','Paper beverage sleeves'),(17,'Bolsa para repostería','Bakery bag'),(18,'Bolsas para comida rápida','Fast-food bags'),(19,'Bolsa para snacks','Snack bag'),(20,'Bolsa para comida para llevar','Takeaway food bag'),(21,'Bolsas comerciales','Retail bags'),(22,'Empaques de papel para supermercado','Supermarket paper packaging'),(23,'Bolsas de papel para regalos','Paper gift bags')]
for pg,es,en in families:add('upack-product-'+str(pg),pg,[612,159,844,470],m.tx(es,en),[m.tx('Material: papel','Material: paper')])
# This source explicitly identifies a water-based coating; resistance claims
# and third-party certifications are intentionally kept out of product copy.
add('upack-water-based-containers',28,[420,285,750,440],m.tx('Recipientes de papel con recubrimiento base agua','Paper containers with water-based coating'),[m.tx('Recubrimiento: base agua','Coating: water-based')])
m.author(cfg,items)
(m.TMP/'sustainable-generated-manifest.json').write_text(json.dumps(m.manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'docs/catalog-review/SOSTENIBLE-FUENTE.md').write_text('''# Fuente sostenible localizada

Archivo: Upack_English_Espanol.pdf, 112 páginas (56 EN + 56 ES).
Drive aprobado: https://drive.google.com/file/d/1LGnLMWWRSCKjzKTYhiDuH8un3wxGpw4m/view

El archivo es una presentación corporativa del proveedor, no una lista de SKU.
El catálogo resultante conserva 18 presentaciones fotográficas de empaques.
No se atribuyen a Lynx las fábricas, cifras, clientes ni certificaciones del proveedor.
No se inventan modelos, capacidades, medidas ni garantías de compostabilidad.
Las marcas impresas en las fotos originales son ejemplos del proveedor.
''',encoding='utf-8')
