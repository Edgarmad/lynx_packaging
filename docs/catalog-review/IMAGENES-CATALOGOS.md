# Identificación de imágenes para los catálogos

Auditoría de assets existentes: 6 de octubre de 2026. No modifica las galerías del sitio.

Revisados automáticamente 1199 registros de imágenes y las galerías de 1199 productos del proyecto. Archivos ausentes: 0; discrepancias de hash fuente contra inventario: 0.

Grupos con píxeles idénticos: 0; recortes de la misma región fuente: 0; rutas compartidas por varios productos del sitio: 0. Estos grupos exigen revisión y no prueban por sí mismos que se trate de productos duplicados.

| Lote | Catálogo | Imagen candidata existente | Repetida / revisar recorte | Extraer de fuente | Papel revisado |
| --- | --- | ---: | ---: | ---: | ---: |
| L0 | Empaques de papel | 0 | 0 | 0 | 281 |
| L1 | Vasos IML | 39 | 0 | 0 | 0 |
| L1 | Vasos por inyección | 52 | 0 | 0 | 0 |
| L1 | Vasos y tapas PET | 74 | 0 | 0 | 0 |
| L2 | Botellas para bebidas calientes | 17 | 0 | 0 | 0 |
| L2 | Botellas PET | 113 | 0 | 0 | 0 |
| L2 | Latas de apertura fácil | 74 | 0 | 0 | 0 |
| L2 | Catálogo PET | 0 | 0 | 119 | 0 |
| L3 | Bolsas y portavasos | 88 | 0 | 0 | 0 |
| L3 | Envases | 12 | 0 | 0 | 0 |
| L3 | Envases, tarros y cubiertos | 65 | 0 | 0 | 0 |
| L3 | Fundas y accesorios | 41 | 0 | 0 | 0 |
| L3 | Popotes | 75 | 0 | 0 | 0 |
| L4 | Tapas por inyección | 193 | 0 | 0 | 0 |
| L4 | Vasos de papel | 144 | 0 | 0 | 0 |
| L5 | Repostería | 0 | 0 | 140 | 0 |
| L5 | Vasos de plástico | 0 | 0 | 17 | 0 |
| L5 | Envases para huevos | 0 | 0 | 52 | 0 |
| L6 | Bento, carne y bandejas | 0 | 0 | 273 | 0 |
| L6 | Frutas y verduras | 0 | 0 | 384 | 0 |
| L7 | Empaques sostenibles | 0 | 0 | 0 | 0 |

## Regla obligatoria antes de maquetar

1. Identificar ahora: producto/modelo → catálogo aprobado → página → región de imagen → asset local. Mantener la ficha de procedencia.
2. Reutilizar el asset del proyecto solo después de confirmar visualmente que contiene el producto correcto y procede del catálogo correspondiente.
3. Para productos diferentes, no reutilizar una foto genérica o el montaje entero. Extraer cada panel; si la fuente no tiene imagen individual, marcar pendiente y no rellenar con otro producto.
4. Si varias medidas comparten una única foto de familia en la fuente, usar una sola ficha con tabla de variantes, como en Papel.
5. Detectar repetición por ruta, píxeles y región fuente dentro de cada catálogo; revisar también parecidos con hash visual y hojas de contacto. Cambiar el nombre del archivo no resuelve la repetición.
6. Usar la misma foto verificada en ES y EN. Conservar productos de fábricas/calidades diferentes entre los catálogos aprobados, revisando la fuente de cada uno.
7. Cerrar identificación visual por lote antes de generar los PDFs. Revisar de nuevo las páginas renderizadas al terminar.

La auditoría automática prepara candidatos y señala anomalías; no equivale a una aprobación visual completa de todas las imágenes. El JSON contiene la relación por registro y los grupos que requieren revisión. Las imágenes del Master existentes para registros también presentes en catálogos públicos se conservan como candidatas secundarias: requieren contraste con la página del catálogo correspondiente antes de reutilizarlas.

## Preparación visual inicial

Hoja de contacto del lote 1 (`catalog-images-L1-contact.jpg`): 24 candidatos, ocho de cada catálogo. Inspeccionada visualmente: los recortes muestran vasos/tapas y sus medidas originales. Hay acabados y formas parecidos que requieren contrastar datos antes de agrupar; no basta con igualdad visual. La inspección detallada de cada página fuente queda dentro de la preparación del lote.
