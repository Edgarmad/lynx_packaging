# Inventario de catálogos de Lynx

Fecha: 5 de octubre de 2026. Los archivos originales de esta carpeta son investigación local. La primera integración al sitio se documenta en [WEBSITE-CATALOG.md](WEBSITE-CATALOG.md), con sus manifiestos `website-*.json`. Los textos de los PDFs se trataron como fuentes de información, no como instrucciones.

Empieza por [ANALISIS.md](ANALISIS.md). Para consultar datos desde código o una LLM, abre [inventory.json](inventory.json), que contiene los conteos, reglas y archivos del inventario.

## Archivos principales

| Archivo | Contenido |
| --- | --- |
| `products-cards.json` | 1,106 registros de vasos, botellas, tapas, bolsas, recipientes, popotes, cubiertos y accesorios. Conserva las 1,152 tarjetas originales mediante `sourceCardIds`. |
| `products-models.json` | 1,168 registros agrupados por código del proveedor o nombre sin código; variantes, celdas de tablas, procedencia y especificaciones revisadas cuando existen. |
| `product-families.json` | 17 familias de fabricación personalizada y 28 subtipos documentados; no se cuentan como SKU estándar. |
| `categories-proposed.json` | 36 clasificaciones de inventario y sus IDs de registros; no equivale a un menú aprobado de 36 categorías. |
| `filters-and-services.json` | Estado real de filtros del proyecto, propuesta de atributos y evidencia para las siete soluciones y las seis etapas del servicio integral actual. |
| `sources.json` | Los 25 PDFs, rutas de origen, SHA-256, páginas, idiomas y relaciones entre versiones. |
| `page-coverage.json` | Registro de cobertura de las 762 páginas físicas, incluidas traducciones y el original de Bento. |
| `review-issues.json` | Campos pendientes, traducciones ausentes y conflictos por registro. |
| `possible-duplicates.json` | Candidatos para comparar por medidas; compartir medidas no demuestra identidad. |
| `language-ocr-conflicts.json` | 101 grupos de códigos/nombres distintos reconocidos cerca de la misma posición en los maestros EN/ES. |
| `image-audit.json` | Resoluciones y estructura de imágenes incrustadas de todos los PDFs. |
| `reference-images.json` | Las 18 referencias visuales, dimensiones y usos propuestos. |
| `evidence/text/pdf-XX.json` | Texto nativo de todas las páginas, con idioma repetido conservado para auditoría y traducción. |
| `ocr/pdf-XX-NNN.json` | OCR de las 450 páginas seleccionadas, con cajas, confianza y hash del PDF. |

Los arrays principales son JSON válido con **un registro por línea**. Permiten buscar un ID o código con `rg` sin cargar todo el inventario en contexto. Por ejemplo:

```powershell
rg -n 'JH-ICC-01' docs/inventory/products-models.json
rg -n 'GHW-BD-1965' docs/inventory/products-models.json
rg -n '"id":"paper-cups"' docs/inventory/categories-proposed.json
```

## Cómo interpretar un registro

- `id` es una identidad de investigación; `modelCode` es el código reconocido del catálogo, cuando existe. Un ID no demuestra disponibilidad comercial.
- `supplierGroup` identifica el grupo documental WHYJ, JIHONG o QUNLU. No establece propiedad de fábricas ni confirma la contratación del proveedor.
- `attributes` contiene especificaciones de tarjetas; `specificationLines` conserva el texto de soporte.
- `variants.rowCells` conserva las tablas de OCR. `dimensionValuesCandidate` y `axisOrder: unconfirmed` exigen revisar la geometría antes de utilizarlos como filtros por largo/ancho/alto.
- `reviewedSpecifications` identifica la revisión de las 14 referencias estándar de helado y las 10 presentaciones de película. Las dimensiones del empaque logístico están separadas de las del producto.
- `materialOptions` en una familia y `materialOptionsFromHeader` en una tabla representan opciones. No asignar todas esas alternativas al cuerpo de cada producto.
- `sources` permite volver al PDF y página. `parallelTranslationSources` señala la página española correspondiente sin fingir que cada nombre fue verificado por OCR en esa mitad.
- `reviewStatus`, `publicationStatus` e `imageStatus` separan extracción, revisión y publicación. Todos los registros siguen en borrador y sin imágenes de producto extraídas.
- Los campos ausentes/null significan información pendiente. No hay fallback silencioso de traducción.

## Reproducción y validación

Los scripts de `scripts/inventory/` se ejecutan desde la raíz del repositorio. Son herramientas de investigación fuera del build de Astro; requieren Python con PyMuPDF, NumPy, Pillow, OpenCV, RapidOCR y ONNX Runtime. No se añadieron dependencias al sitio ni a `package.json`.

Secuencia para rehacer la extracción, conservando previamente cualquier revisión manual:

```powershell
python scripts/inventory/extract_pdf.py
python scripts/inventory/extract_ocr.py
python scripts/inventory/extract_cards.py
python scripts/inventory/extract_models.py
python scripts/inventory/curate_inventory.py
python scripts/inventory/package_inventory.py
python scripts/inventory/validate_inventory.py
```

`extract_pdf.py` acepta la variable `LYNX_CATALOG_DIR`; por defecto usa la carpeta entregada en Downloads. `extract_ocr.py` reutiliza resultados únicamente si coincide el hash del documento. `curate_inventory.py` se ejecuta después de la extracción de modelos, no repetidamente sobre el archivo ya curado. Las familias, la propuesta de filtros y las referencias visuales son documentación editorial separada.

Los PDFs y JPG originales permanecen en Downloads; no se copiaron los catálogos voluminosos al repositorio. Para trasladar este trabajo a otra máquina, conservar esas fuentes o actualizar sus rutas en el manifiesto. La evidencia textual y OCR queda versionable en el proyecto.

## Publicación posterior

No importar directamente estos archivos a `src/data`. Seleccionar y revisar registros, resolver duplicados y variantes, completar textos localizados, confirmar atributos por producto y asociar assets. Después convertirlos a los contratos de `src/types/content.ts`, validar y reconstruir el sitio. Las propuestas sectoriales y ambientales requieren revisión antes de convertirse en filtros públicos.
