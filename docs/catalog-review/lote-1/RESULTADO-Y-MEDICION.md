# Lote 1: resultado y medición

Fecha: 6 de octubre de 2026. Inicio registrado: 21:35:20 UTC (15:35:20 México). Cierre de producción, revisión y lectura de consumo: 21:43:42 UTC (15:43:42 México). Intervalo: **8 minutos y 22 segundos**, más el cierre documental y la entrega. Aproximadamente nueve minutos para esta ejecución completa.

| Catálogo | Fuente | Registros | Páginas por idioma | Archivos |
| --- | --- | ---: | ---: | ---: |
| Vasos IML | pdf-10 | 39 | 6 | 2 |
| Vasos por inyección | pdf-11 | 52 | 8 | 2 |
| Vasos y tapas PET | pdf-13 | 74 | 11 | 2 |
| Total | | 165 | 25 | 6 |

## Consumo observado

- Límite de cinco horas de la cuenta: pasó del 17 % al 24 % consumido; diferencia de **7 puntos porcentuales**.
- Límite semanal: pasó del 26 % al 27 %; diferencia de **1 punto porcentual**.
- Lecturas de límites con la misma ventana y fecha de reinicio; porcentajes redondeados. Son datos compartidos de la cuenta, no una factura ni un contador exclusivo de este chat. Actividad simultánea de otros chats puede afectar la diferencia.
- Generación de imágenes con IA: **0 llamadas**. Se recortaron las fotografías existentes de los catálogos. No se realizaron llamadas externas de generación de imágenes ni compras de créditos.
- Tokens exactos y costo monetario atribuible al lote: no disponibles mediante el medidor expuesto. No convertir estos porcentajes a tokens o dólares.

## Tratamiento aplicado

- Un PDF ES y otro EN por catálogo, con ocho fichas por página de productos salvo la última, logo oficial, fondo azul con acabado y marca de agua Lynx.
- Portadas comerciales propias, sin notas internas ni elementos de las portadas del proveedor.
- 165 productos asociados a su fuente, página y región de imagen. Los recortes ES proceden de la página española y los EN de la inglesa, conservando las anotaciones técnicas localizadas.
- Corrección del límite superior de 39 recortes IML: se recupera el borde del vaso sin cambiar la geometría ni crear imágenes nuevas.
- Variantes con títulos iguales conservadas y distinguidas por diámetro, tapa, acabado o estilo documentado. Los estilos PET para té, café y café reforzado se mantienen separados.
- En el vaso rectangular se separa la altura de la tapa (26 mm) de la altura del vaso (170 mm), y se conserva la parte superior de 80 x 60 mm.
- El título conflictivo del tercer vaso naranja se ajusta a la capacidad de 700 ml de su especificación, decisión ya registrada en el inventario original.

## Verificación

- Los tres hashes de los PDFs fuente coinciden con el inventario.
- Cobertura íntegra: 39, 52 y 74 registros en ambos idiomas; 330 fichas entre los seis PDFs.
- No hay recortes con píxeles idénticos entre fichas dentro de cada PDF. Productos parecidos conservan su foto específica de la fuente.
- Las líneas técnicas preparadas aparecen en el PDF correspondiente, sin recortes de texto fuera de página ni etiquetas internas de revisión.
- Las 50 páginas finales se renderizaron con Poppler y se inspeccionaron en diez hojas de contacto, además de revisar páginas completas representativas y la corrección de la tapa rectangular en ES/EN.
- La inspección no sustituye la validación comercial de disponibilidad por parte de Mila; conserva la información de los documentos entregados.

## Qué cambia en la estimación

La estimación anterior de cuatro a ocho horas era demasiado amplia para estos catálogos WHYJ, cuyo inventario e imágenes ya estaban extraídos. Esta ejecución confirma que podemos procesar lotes similares en decenas de minutos, usando datos revisados y scripts reproducibles. No extrapolar automáticamente a QUNLU: hay más conflictos OCR, imágenes pendientes y registros exclusivos del Master. El lote 2 permitirá medir un segundo grupo WHYJ antes de afinar el total.

Estado de alcance: Papel y lote 1 generados, ocho PDFs en total. Quedan **17 catálogos / 34 PDFs**, incluido Sostenible, cuya fuente sigue pendiente de localizar.

Archivos técnicos: `output/pdf/Lynx-Lote-1-manifest.json`, `output/pdf/Lynx-Lote-1-QA.json` y `content-and-image-map.json` en esta carpeta. Los scripts permiten regenerar el lote; las imágenes intermedias quedan organizadas en `tmp/pdfs/lote-1` para revisión.

No se subieron los PDFs a Drive ni se enviaron a Mila en esta ejecución.
