# Catálogo conectado al sitio — 5 de octubre de 2026

La instrucción de Luis de comenzar el catálogo y utilizar las imágenes autoriza esta primera integración. No se ha desplegado a producción. El sitio conserva `preview: true` y `noindex`.

## Datos de publicación

`src/data/products.json` contiene **1,199 fichas**: 1,182 modelos o variantes ilustradas y 17 familias de fabricación personalizada. Son referencias de catálogo; este conteo **no representa SKU comerciales únicos, existencias en almacén, disponibilidad ni stock**. Los modelos de distintos proveedores no se fusionan únicamente por compartir medidas.

**Alcance vigente tras aclaración del usuario:** las 1,199 fichas son públicas y se agrupan comercialmente en las 14 ramas amarillas, conservando materiales y tipos originales. Las 54 categorías y seis grupos del Excel siguen visibles; las ramas vacías muestran próximos productos. Véase PRODUCTS-MENU.md y products-menu-scope.json. Las tablas y verificaciones anteriores son históricas.

Verificación de esta aclaración: Astro/TypeScript sin errores, ocho pruebas y build de 2,539 páginas correctos; auditoría de 572,360 referencias locales sin errores. En navegador se verificaron los seis grupos del menú y la categoría de vidrio sin fichas con aviso de próximos productos, sin errores de consola. Capturas: `tmp/catalog-review/all-categories-upcoming.jpg` y `upcoming-category.jpg`. No se realizó despliegue.

| Categoría | Fichas relacionadas |
| --- | ---: |
| Vasos | 273 |
| Tapas | 236 |
| Botellas y envases para bebidas | 193 |
| Envases para alimentos | 75 |
| Bolsas y portavasos | 96 |
| Accesorios y consumibles | 177 |
| Bandejas | 83 |
| Empaques para repostería | 56 |
| Empaques para frutas y ensaladas | 9 |
| Cajas y empaques personalizados | 5 |
| Productos sustentables | 29 |

La categoría sustentable reúne únicamente referencias identificadas como PLA en sus fuentes. No implica certificación de compostabilidad, biodegradación en cualquier ambiente o cumplimiento normativo. Los productos de papel no se clasifican automáticamente como sustentables.

## Selección y normalización

- Se incorporan las tarjetas de los primeros 13 PDFs con sus nombres ES/EN y fotografías. Se recuperan las tarjetas que la investigación había agrupado por textos idénticos, porque imágenes distintas pueden representar colores o presentaciones distintas. La generación solo fusiona registros con nombre, atributos, especificaciones **y fotografía idénticos**.
- Los modelos QUNLU requieren una única tupla de dimensiones, un material único en la tabla, evidencia de la fila en los maestros EN/ES, lectura confiable y una imagen localizable. Se excluyen los códigos afectados por conflictos posicionales. La auditoría conserva las celdas originales para revisar cualquier dato posteriormente.
- Las 17 familias JIHONG presentan opciones de materiales y rangos de fabricación. Los intervalos no se atribuyen a una pieza estándar ni representan medidas de todos los modelos. Las fotos se identifican como ejemplos de familia.
- Se conservan dimensiones en el orden impreso. Cuando el orden de los ejes no está confirmado, la ficha muestra «Dimensiones según catálogo», sin inventar largo, ancho o alto.
- Los atributos desconocidos permanecen ausentes. **378 fichas no tienen polímero/material normalizado confirmado**; no se asigna uno a partir de la apariencia. **39 fichas no tienen especificaciones adicionales publicables**; muestran un mensaje de consulta, sin cifras inventadas.
- La procedencia se guarda en `provenance` con ID del PDF, página física e idioma. La evidencia completa, OCR y variantes permanece en `docs/inventory/`; no se envía al navegador.
- Las soluciones enlazadas son alimentos y bebidas, comercio electrónico/retail y personalización, según los usos documentados. No se atribuyen especificaciones del empaque a servicios de logística, almacén o última milla.

## Imágenes

Se utilizan **fotografías reales extraídas de los PDFs** para las fichas. El recorte elimina títulos, tablas y fotos vecinas cuando es posible; los diagramas que forman parte de la foto se conservan. Se exporta WebP sin aumentar la resolución original ni alterar geometría, acabados o logos con IA. `website-media.json` registra cada recorte, dimensiones y SHA-256 de fuente/píxeles.

Se usan seis composiciones entregadas por Luis para imágenes editoriales de categorías, con la indicación «Composición ilustrativa de packaging». No se usan como evidencia de un modelo específico.

Hay **257 recortes con menos de 220 px de ancho**, principalmente por la resolución del catálogo original. Funcionan como referencia inicial; para una galería final de gran formato conviene solicitar las fotografías originales. La mejora con IA podría limpiar fondos o ruido, pero debe conservar forma, medidas, detalles y marcas mediante revisión humana. Generar un producto parecido no sustituye la fotografía de la referencia real. No se han generado nuevas imágenes en esta integración.

Las imágenes reservan espacio y se cargan de forma diferida. La cuadrícula conserva el producto completo con `object-fit: contain`; no fuerza todas las fotos a un recorte cuadrado. Home selecciona hasta seis referencias variadas por categoría y las fichas muestran hasta seis relacionados.

## Filtros y navegación

Los filtros se generan solo con valores presentes en la categoría: material, tipo de producto, bandas de capacidad, diámetro del borde, medidas de catálogo/a medida y personalización confirmada. Los valores sin confirmar no aparecen como opciones.

La búsqueda reconoce nombres, modelos y etiquetas de atributos ES/EN, incluidas búsquedas sin acentos. El listado muestra 24 referencias por página, guarda filtros/búsqueda/página en la URL y restaura el estado. OR entre valores de un atributo; AND entre atributos. Al cambiar filtros vuelve a la primera página. ES/EN conserva la entidad y sus parámetros.

Todos los enlaces y fichas existen en HTML estático. Sin JavaScript se muestran todas las referencias de la categoría; no hay una API ni servidor de filtrado.

## Registros que siguen fuera del sitio

`website-deferred.json` conserva **1,138 registros**, con el motivo individual:

- 899 con conflictos OCR, alternativas de material o dimensiones ausentes/ambiguas.
- 121 tarjetas del catálogo PET cuyo texto nativo omite valores visibles en el raster, incluidas tarjetas recuperadas del agrupamiento anterior.
- 50 modelos JIHONG u opciones de película que necesitan vincular imagen y especificación individualmente.
- 34 sin fotografía inequívocamente localizable.
- 34 sin evidencia de dimensiones en ambos maestros.

Estos registros requieren revisión de las fuentes; no se presentan como fichas completas ni se reemplazan por productos inventados. Los 28 subtipos de familias siguen como clasificación de investigación, sin 28 URLs adicionales.

## Reproducción y mantenimiento

El script `scripts/inventory/prepare_catalog.py` prepara los JSON, assets y manifiestos fuera del runtime. Requiere Python con PyMuPDF, Pillow, NumPy y OpenCV. Las rutas de los PDFs se toman de `sources.json`; si cambia la ubicación, actualizar ese manifiesto antes de ejecutar. En esta máquina:

```powershell
& 'C:\Users\edmad\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts/inventory/prepare_catalog.py
npm run validate:data
npm run check
npm test
npm run build
```

**El script regenera** `products.json`, `categories.json` y las relaciones/descripciones de las tres soluciones indicadas. Para curación duradera modificar el script o la fuente de investigación, o incorporar un archivo de overrides antes de añadir cambios manuales. No editar el JSON generado y después regenerar esperando que conserve ese cambio.

Después de `prepare_catalog.py`, ejecutar `classify_products_menu.py` y `apply_products_menu.py` con el mismo Python antes de validar o construir. Restablecen la jerarquía del Excel y los campos de clasificación requeridos por el sitio.

El JSON de productos mantiene un registro por línea para consultas de LLM/`rg` y diffs manejables. No copiar los PDFs grandes al repositorio; los catálogos públicos seguirán enlazando Drive cuando se entreguen las URLs.

`website-catalog.json` resume conteos e IDs; `website-media.json` audita imágenes; las hojas de revisión visual se generan bajo `tmp/catalog-review/website/` y no forman parte del sitio.

## Verificación histórica de la integración anterior

- Validación de datos y procedencia, Astro/TypeScript y ocho pruebas de búsqueda, paginación, filtros, rutas y jerarquía del cliente: correctas.
- Build estático actual: 2,539 páginas. Auditoría de 572,680 referencias locales, assets y anchors: sin destinos faltantes; un H1 por documento, IDs únicos y `noindex` de revisión conservado. Repetir con `python scripts/inventory/audit_static_site.py` después del build.
- Navegador: catálogo, filtros y estado vacío, paginación, búsqueda ES/EN conservando parámetros, menú móvil con Escape, detalle nativo, modelo QUNLU, familia personalizada, resumen de productos, Home y contacto. Sin errores de consola observados. Sin desbordamiento horizontal en 390, 768 y 1,440 px.
- El HTML contiene todas las tarjetas y sus enlaces antes de ejecutar JavaScript; el navegador limita la vista a 24 por página. Las fotografías cargan desde assets locales.
- Reclasificación: seis grupos en Productos y Catálogos; header con tres niveles y acordeones móviles anidados. Escape cierra y devuelve foco. Búsqueda ES/EN mantiene parámetros y resultados. PLA conserva su etiqueta de material aunque se agrupe por similitud. Las ramas sin fichas ofrecen contacto y no se indexan; no se inventan productos o enlaces de Drive.
- Capturas de revisión local: `tmp/catalog-review/menu-desktop.jpg` y `menu-mobile.jpg`; las capturas `catalog-desktop.jpg` y `catalog-mobile.jpg` corresponden a la primera integración. La página Catálogos se añade por instrucción posterior del usuario del 2026-10-05, reemplazando la decisión inicial de no tener una página interna. No se realizó despliegue a producción.

## Verificación histórica: primer alcance amarillo

- 415 productos públicos y 784 borradores conservados; 19 categorías públicas bajo tres raíces. Solo las 14 ramas amarillas y sus ancestros se publican.
- Validación de datos, Astro/TypeScript y ocho pruebas correctas. Build: 901 páginas; auditoría de 131,245 referencias locales sin errores.
- Navegador: tres grupos en Productos y Catálogos, diez ramas plásticas sin Others, menú móvil a 390 px sin desbordamiento y Escape devolviendo el foco, listado de 37 vasos PET, ficha con especificaciones y resumen en inglés. Sin errores ni advertencias de consola observados.
- Evidencia: `tmp/catalog-review/yellow-menu-desktop.jpg` y `yellow-menu-mobile.jpg`. No se realizó despliegue.
- Fruit cup, Golden Container, Eggs box, Sugarcane y Kraft tableware todavía no tienen fichas verificadas en este inventario. `products-menu-yellow-candidates.json` conserva candidatos de investigación para revisar fuentes y fotos; no representa disponibilidad de SKU confirmada.
