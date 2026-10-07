# Estimación de imágenes IA para el catálogo de papel

Consulta de tarifas: 6 de octubre de 2026. Estimación previa a generación; no se generaron imágenes.

## Alcance y recuento

El conteo se usa como carga de trabajo, no como total definitivo de SKUs. Hay duplicados editoriales y solapamientos entre familias, modelos y fichas; no se suman los 17 grupos y 28 subtipos a todos los modelos.

| Bloque | Presentaciones candidatas |
|---|---:|
| Bolsas: 38 filas Jihong + 10 presentaciones WHYJ | 48 |
| Vasos WHYJ: fichas candidatas, pendientes de depuración | 144 |
| Recipientes: 14 presentaciones WHYJ + 14 modelos para helados | 28 |
| Portavasos WHYJ | 14 |
| Accesorios de papel: 28 menos un accesorio mixto | 27 |
| Base antes de depuración | **261** |

Los ocho popotes de papel opcionales quedan fuera de esta base. Los siete registros WHYJ de recipientes se sustituyen por sus 14 presentaciones blanco/kraft; no se cuentan ambos conjuntos. Para cajas, complementos y tipos pedidos por Mila sin ficha, se reserva provisionalmente otras 20–35 imágenes, sin sumarlo como inventario verificado. Resultado para una imagen por presentación: aproximadamente **280–300 imágenes**. La lista final podría bajar al depurar o subir si se exigen vistas adicionales.

Las 144 fichas de vasos corresponden a **26 grupos nominales de diseño/acabado** al quitar el prefijo de capacidad. Esto no prueba que todas las proporciones sean idénticas: reutilizar una ilustración requiere presentarla como representativa y conservar capacidades y medidas en tablas. No basta con estirar una imagen para crear otro tamaño.

## Consumo dentro de Codex

La documentación oficial indica que la generación integrada usa GPT Image 2, comparte los límites generales de Codex y consume esos límites, en promedio, entre tres y cinco veces más rápido que turnos similares sin imágenes. No existe en esa documentación una equivalencia universal imagen → porcentaje de cuenta. El modelo, resolución y calidad exactos usados por la herramienta no están expuestos como parámetros en esta conversación. Por tanto, las cifras API siguientes son un escenario comparable, no una factura garantizada de esta herramienta.

## Base del cálculo API

Modelo de referencia: GPT Image 2; 1024×1024; una imagen por generación. Salida: aproximadamente USD 0.053 por imagen medium y USD 0.211 high según la tabla oficial. Se asume 50% adicional de intentos para correcciones: 100 imágenes aprobadas → 150 generaciones. Esta reserva es una hipótesis de planificación, no una tasa de éxito medida.

| Escenario | Imágenes finales | Generaciones con reserva | USD medium, solo salida | USD high, solo salida |
|---|---:|---:|---:|---:|
| Muestra de estilo | 8–16 | 12–24 | 0.64–1.27 | 2.53–5.06 |
| Catálogo con imágenes representativas — propuesta | 90–120 | 135–180 | 7.15–9.54 | 28.48–37.98 |
| Una imagen por presentación y alcance adicional — provisional | 280–300 | 420–450 | 22.26–23.85 | 88.62–94.95 |

Estos importes excluyen texto de entrada, imágenes de referencia, consumo del modelo conversacional, impuestos y trabajo de revisión. Cada edición o generación descartada también puede consumir recursos. Cambiar calidad, dimensiones, modelo o número de vistas cambia el cálculo. Si fueran dos intentos por imagen aprobada, los costos serían 33% mayores que en la tabla.

Para expresar el orden de magnitud en tokens: la documentación publica USD 30 por millón de tokens de salida de imagen. Dividiendo los importes redondeados de la tabla por esa tarifa, se obtienen aproximadamente 1,767 tokens por imagen medium y 7,033 high. Son tokens de imagen, no palabras ni tokens de texto. El conteo real debe obtenerse de usage de cada petición.

Con reserva, 90–120 imágenes representativas suponen aproximadamente 0.24–0.32 millones de tokens de salida medium o 0.95–1.27 millones high. El escenario completo, con 420–450 generaciones, supone 0.74–0.80 millones medium o 2.95–3.17 millones high. Se añaden las entradas y el análisis; estas cifras no son tokens consumidos por esta conversación.

Los créditos comprados Standard de Codex tienen una tarifa publicada de 750 créditos por millón de tokens de salida de imagen de GPT Image 2. Eso daría, únicamente para la salida y bajo la configuración comparable, unos 713–950 créditos para el escenario representativo high y 2,216–2,374 para el completo high. No equivale a porcentaje del límite incluido ni a dinero: el precio de compra de créditos depende del plan/acuerdo.

## Estrategia propuesta

1. Probar ocho imágenes individuales en la página aprobada. Con 12 intentos presupuestados, salida high ≈ USD 2.53, más entradas. Obtener primero la aprobación visual de Mila evita repetir cientos de imágenes por un cambio de estilo.
2. Usar fondo, iluminación y encuadre constantes; generar cada producto como asset separado y maquetar títulos, medidas, marcos y marca de agua con código. No regenerar una página entera para corregir una etiqueta.
3. Reutilizar exactamente los mismos assets para español e inglés; el idioma se resuelve en la maquetación. Esto no duplica la generación.
4. Proponer a Mila imágenes representativas por forma/acabado y variantes técnicas en tablas, conservando todos los productos. Para planear el proyecto, estimar 90–120 assets aprobados; aún no hay una lista depurada que garantice esa reducción.
5. Para el escenario representativo high, reservar provisionalmente USD 40–60 vía API como presupuesto de planificación (salida calculada USD 28.49–37.98 más margen para entradas y correcciones). No es un tope contratado ni autorización para gastar.

Una cuadrícula con ocho productos generada como una sola imagen no garantiza una reducción de ocho veces: importa la resolución y puede obligar a regenerar el conjunto. Además reduce el control sobre etiquetas, logo y productos independientes.

## Fuentes oficiales

- [Generación de imágenes y costos API](https://developers.openai.com/api/docs/guides/image-generation)
- [Uso de generación integrada en Codex](https://learn.chatgpt.com/docs/image-generation)
- [Créditos y tarifas de Codex](https://learn.chatgpt.com/docs/pricing)

Inventario local: [Extracción de papel](EXTRACCION-PAPEL.md) y [contenido estructurado](paper-catalog-content.json).
