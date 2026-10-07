# Plan de producción de catálogos por lotes

Fecha: 6 de octubre de 2026. Clasificación de trabajo para los PDFs, separada del menú de productos del sitio.

21 catálogos lógicos, 42 PDFs ES/EN terminados y revisados. Los vasos de papel se separaron del catálogo de papel conforme al último mensaje de Mila. El cuadro siguiente conserva el inventario inicial de planificación; el resultado final figura en el cierre de producción y en el manifiesto final.

| Lote | Catálogo | Grupo | Fuente | Registros de extracción |
| --- | --- | --- | --- | ---: |
| L0 | Empaques de papel | Papel | pdf-15, pdf-16, pdf-17, pdf-18, pdf-01, pdf-04, pdf-06, pdf-12 | 281 |
| L1 | Vasos IML | Vasos y accesorios | pdf-10 | 39 |
| L1 | Vasos por inyección | Vasos y accesorios | pdf-11 | 52 |
| L1 | Vasos y tapas PET | Vasos y accesorios | pdf-13 | 74 |
| L2 | Botellas para bebidas calientes | Vasos y accesorios | pdf-02 | 17 |
| L2 | Botellas PET | Vasos y accesorios | pdf-03 | 113 |
| L2 | Latas de apertura fácil | Vasos y accesorios | pdf-07 | 74 |
| L2 | Catálogo PET | Vasos y accesorios | pdf-14 | 119 |
| L3 | Bolsas y portavasos | Vasos y accesorios | pdf-01 | 88 |
| L3 | Envases | Vasos y accesorios | pdf-04 | 12 |
| L3 | Envases, tarros y cubiertos | Vasos y accesorios | pdf-05 | 65 |
| L3 | Fundas y accesorios | Vasos y accesorios | pdf-06 | 41 |
| L3 | Popotes | Vasos y accesorios | pdf-08 | 75 |
| L4 | Tapas por inyección | Vasos y accesorios | pdf-09 | 193 |
| L4 | Vasos de papel | Vasos y accesorios | pdf-12 | 144 |
| L5 | Repostería | Plástico | pdf-22 | 140 |
| L5 | Vasos de plástico | Plástico | pdf-23 | 17 |
| L5 | Envases para huevos | Plástico | pdf-24, pdf-25 | 52 |
| L6 | Bento, carne y bandejas | Plástico | pdf-20 | 273 |
| L6 | Frutas y verduras | Plástico | pdf-21 | 384 |
| L7 | Empaques sostenibles | Sostenible | Pendiente de localizar | Pendiente |

## Orden y propósito de cada lote

- **L0 — Papel:** terminado. Se conserva como referencia visual y técnica.
- **L1 — Vasos IML, inyección y PET con tapas:** primer lote de tres catálogos; adaptar la extracción WHYJ y comprobar la plantilla común.
- **L2 — Botellas y PET:** cuatro catálogos; reutilizar composición y tablas de capacidades, conservando cada fuente.
- **L3 — Accesorios y envases:** cinco catálogos; revisar especialmente materiales mixtos, bolsas, cubiertos y fundas.
- **L4 — Vasos de papel y tapas por inyección:** dos catálogos con mayor volumen; mantener compatibilidades de tapas únicamente si están documentadas.
- **L5 — Plástico: vasos, repostería y huevos:** tres catálogos; resolver la extracción QUNLU y el recorte del Master.
- **L6 — Plástico: bento y frutas/verduras:** dos catálogos de mayor volumen, una vez validado el tratamiento QUNLU.
- **L7 — Sostenible:** un catálogo, condicionado a localizar la fuente específica aprobada.

## Clasificación y cruces

- El grupo “Vasos” incluye sus 14 archivos completos, aunque algunos contengan botellas, envases, bolsas o cubiertos. No reorganizarlos por material ni trasladarlos al menú web.
- Cada registro conserva sus asignaciones múltiples. Los cruces Papel/Vasos y Plástico/Vasos se mantienen; parecerse no prueba que sean el mismo producto o fábrica.
- Bento original pdf-19 y traducción pdf-20 son fuentes del mismo catálogo, no dos entregables. Jihong completo/China y helados/V5 alimentan el único catálogo de papel.
- Huevos: 52 registros de investigación en la página 85 del Master EN y ES. Ese conteo requiere contrastar títulos, códigos y variantes antes de definir las fichas finales.
- **271 registros exclusivos del Master** quedan separados de los catálogos públicos y con categorías candidatas cuando hay evidencia. No se incorporan automáticamente: algunos corresponden a película o presentan conflictos OCR.
- Sostenible: no hay un PDF específico identificable entre los 25 archivos inventariados de la carpeta entregada. No construirlo agrupando productos que parezcan ecológicos ni inventar certificaciones.

## Ejecución y control por lote

1. Confirmar páginas ES/EN, extraer imágenes originales y asociarlas a registros con procedencia.
2. Corregir traducciones/OCR, separar fotos de montajes y agrupar variantes solo cuando comparten un producto documentado.
3. Generar ambas versiones desde un único conjunto de datos; conservar diseño premium y marca de agua Lynx. Retirar notas internas y elementos del proveedor.
4. Comprobar cobertura de registros, unidades, nombres y tablas. Renderizar y revisar ambos PDFs; cerrar el lote antes de avanzar.

El número de fichas y páginas se fijará después de revisar variantes y conflictos; los registros de extracción no representan cantidades comerciales únicas. La estimación inicial de 4–8 horas debe revisarse al cerrar L1, con una medida real del tratamiento por lote.

## Archivos de trabajo

- `catalog-batches.json`: 21 catálogos, fuentes y asignación por ID de todos los registros del inventario.
- `scripts/catalogs/plan_catalog_batches.py`: reproduce esta clasificación sin modificar los datos públicos.

Esta etapa clasifica y planifica; no genera nuevos PDFs, no sube archivos ni modifica el sitio.

## Identificación de imágenes antes de producir cada lote

Identificar desde ahora: producto/modelo → catálogo aprobado → página → región de foto → asset local. La auditoría inicial se encuentra en IMAGENES-CATALOGOS.md y catalog-image-audit.json.

Antes de maquetar cada lote, cerrar la correspondencia visual de todos sus productos. No repetir una foto entre fichas de productos diferentes ni reutilizar montajes genéricos: recortar el producto correspondiente del catálogo. Las variantes con una única foto común se agrupan en una ficha con tabla. ES y EN comparten la imagen verificada del mismo producto.

Contrastar cualquier asset procedente del Master con la página del catálogo público correspondiente. Si falta la foto correcta, dejar pendiente de extracción; no sustituir por otra parecida. Verificar repeticiones por ruta, píxeles y región fuente, y revisar hojas de contacto y páginas finales.

## Lote 1 completado

IML: 39 registros, 6 páginas por idioma. Inyección: 52 registros, 8 páginas por idioma. PET con tapas: 74 registros, 11 páginas por idioma. Se generaron y revisaron los seis PDFs; 165 registros en ambos idiomas. Medición y decisiones en lote-1/RESULTADO-Y-MEDICION.md. El siguiente lote es L2.
