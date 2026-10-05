# Análisis de productos, clasificaciones e imágenes

## Resultado y alcance

Se inventariaron **25 PDFs, 762 páginas físicas y 18 imágenes de referencia**. Se extrajo el texto nativo de todas las páginas y se aplicó OCR a **450 páginas**: las mitades inglesas de los bilingües, la hoja de vasos y los dos maestros separados EN/ES. Las mitades españolas permanecen en la evidencia y están relacionadas con sus originales. El PDF original de Bento se relacionó con su versión traducida; se revisó visualmente una muestra de su composición.

La entrega contiene **2,274 registros de trabajo**: 1,106 tarjetas después de eliminar 46 duplicados exactos, más 1,168 registros de modelos o productos sin código. Hay además **17 familias personalizadas y 28 subtipos**, separados de los productos estándar. Son unidades de extracción, **no un total confirmado de SKU comerciales únicos**: quedan solapamientos entre catálogos y variantes que deben resolverse antes de publicar.

El inventario está clasificado y tiene trazabilidad a archivo y página. No se sustituyeron los productos demo del sitio, no se crearon páginas y no se extrajeron ni generaron assets de producto. Los renders temporales se utilizaron solamente para análisis visual.

## Qué contienen los catálogos

| Grupo documental | Cobertura principal | Tratamiento |
| --- | --- | --- |
| WHYJ: `pdf-01` a `pdf-14` | Bolsas y portavasos; botellas AS/PP/PET; recipientes; tarros; cubiertos; fundas y accesorios; envases de apertura fácil; popotes; tapas; vasos IML, inyectados, de papel y PET | Tarjetas bilingües por presentación. Se conservaron color, peso, capacidad, dimensiones, diámetro, temperatura, personalización y embalaje cuando aparecen. |
| Jihong: `pdf-15` y `pdf-16` | Bolsas comerciales y alimentarias, vasos, boles, cubetas, cajas para alimentos y pizza, envolturas, manteles, multipacks, cajas impresas y corrugadas | Familias personalizadas, rangos y subtipos. Las tablas de bolsas añaden 36 códigos de modelo, algunos con medidas diferentes bajo el mismo código. |
| Jihong helados: `pdf-17` y `pdf-18` | Vasos, boles, cubetas, tapas, fundas para conos y cajas | Los mismos 14 códigos se agruparon; se revisaron dimensiones, presentación y datos de cartón mediante las tablas nativas. |
| QUNLU: `pdf-19` a `pdf-25` | Bento, fideos fríos, carne, skin pack, atmósfera modificada, congelados, repostería, fruta, ensalada, bandejas, huevos, vasos y película | Cruce por modelo, tablas y tarjetas con OCR. El maestro EN/ES se compara por código y posición; las diferencias de reconocimiento permanecen identificadas. |

Las 36 clasificaciones propuestas son una taxonomía para consultar el inventario. Conviene agruparlas para la navegación pública; no convertir cada sección del proveedor en un elemento del header. Las soluciones por sector permanecen independientes de las categorías de producto.

## Medidas y atributos

El contenido permite organizar materiales PET, PP, PS, PLA, PVC, AS, PE, papel, kraft y cartón, además de opciones de recubrimientos y laminados. Un envase transparente no se clasificó como PET solo por su apariencia. Las columnas PP/PET con marcas de selección difíciles de distinguir conservan las alternativas y la duda.

Las capacidades explícitas en ml se conservan como tales; los litros conocidos se normalizan a ml. Las onzas nominales permanecen separadas: varios códigos en oz presentan capacidades comerciales en ml que no deben reemplazarse mediante una conversión teórica. La capacidad del vaso que cabe en una bolsa se distingue de la capacidad del envase.

No se mezclan las siguientes medidas:

- Bolsas: ancho, fuelle y alto; también existen bolsas planas de dos dimensiones.
- Vasos y boles: diámetro superior, diámetro inferior y altura.
- Cajas: largo, ancho y alto cuando el encabezado lo confirma.
- Fundas de cono: diámetro, generatriz y ángulo; el tercer valor puede ser grados.
- Película: ancho del rollo y longitud en metros o yardas.
- Logística: dimensiones del cartón, piezas por cartón, MOQ y carga por contenedor.

En el OCR general se conservan las tuplas sin asignar ejes que no se hayan confirmado. Los textos alrededor de diagramas también quedan disponibles, pero no se convierten automáticamente en largo/ancho/alto del producto.

## Duplicados y revisión

Se evitaron duplicados automáticos por idioma en las tarjetas. En los modelos se agruparon códigos iguales dentro del grupo documental; se conservaron variantes y referencias de archivos solapados. Las dos versiones de helados comparten los mismos 14 códigos.

La revisión pendiente está identificada en JSON, no escondida:

| Situación | Registros/grupos | Interpretación |
| --- | --- | --- |
| Material sin asignación confirmada | 1,046 registros | Puede faltar en la tarjeta o aparecer como alternativa de tabla. No significa que se haya ignorado el material declarado en la familia. |
| Nombre localizado pendiente | 310 registros | La fuente está disponible, pero el nombre español o inglés todavía no quedó vinculado de forma segura. |
| Medidas múltiples o conflicto OCR | 82 registros | Puede tratarse de variantes reales, reutilización de código o lectura incorrecta. |
| Nombre sin código por revisar visualmente | 77 registros | Incluye productos descritos por uso/forma y fragmentos OCR que deben comprobarse. |
| Mención de modelo sin especificaciones legibles vinculadas | 81 registros | Se conserva el modelo y su evidencia; no se inventan medidas. |
| Diferencias cerca de la misma posición EN/ES | 101 grupos | Comparar los códigos en la imagen antes de fusionar; evitar contar ambos como productos comerciales diferentes. |

Estos conjuntos se solapan; no se suman para calcular productos pendientes. El inventario es suficiente para consultar y preparar la selección editorial, pero no representa una base de publicación totalmente depurada.

Un conflicto concreto: `JHXMDK001` aparece en dos familias de bolsas con medidas **220 × 90 × 280 mm** y **240 × 90 × 320 mm**; `JHXMDK002` también se reutiliza. El código solo no puede ser la identidad final de esas fichas. En los archivos hay evidencia de las dos medidas.

## Filtros y servicios del proyecto

En el código actual existen filtros únicamente en las categorías de productos, con el atributo demo `sample`. Las páginas de soluciones y servicio integral **no tienen filtros implementados**. La lógica existente es OR dentro de un atributo y AND entre atributos distintos.

La propuesta más útil para productos dentro de una solución es: **tipo, material, aplicación, capacidad, diámetro de boca, medidas, compartimentos y personalización**. Color/acabado y presentación por caja funcionan como filtros secundarios cuando el volumen y la consistencia los justifiquen. Los filtros numéricos requieren ampliar deliberadamente el contrato actual, que hoy admite valores enumerados.

La cobertura de **alimentos y bebidas** es amplia. Para **retail** hay bolsas documentadas; para **cosmética** y **electrónica** hay cajas impresas personalizadas mencionadas como familia, no un inventario específico de frascos cosméticos o interiores protectores. Los regalos premium y aplicaciones industriales necesitan más evidencia comercial por producto. Las referencias visuales no sustituyen esa evidencia.

Para el servicio integral, los catálogos aportan materiales, estructuras, colores y opciones de impresión a Diseño creativo; MOQ y presentaciones a Producción; pruebas y documentación del proveedor a Calidad; dimensiones del cartón y cargas 20GP/40GP/40HQ de helados a Logística. No aportan stock mexicano, rutas, tiempos, precios, cobertura de entrega ni condiciones comerciales de Lynx.

Las afirmaciones ambientales deben conservar su origen y condiciones. Papel, PLA o un texto «degradable» no establecen automáticamente una certificación ni una condición de compostaje. Productos sustentables puede prepararse como colección transversal, sin duplicar fichas ni crear una sección corporativa independiente. Las certificaciones del proveedor requieren verificar vigencia y alcance antes de atribuirlas a un producto o a Lynx.

La propuesta completa y las referencias concretas están en `filters-and-services.json`.

## Plan de imágenes

### Recomendación

Usar **fotografías/recortes de los productos originales para las fichas**, y el estilo de las referencias para composiciones editoriales de categorías o soluciones. La mejora con IA debe evaluarse sobre cada recorte conservando geometría, borde, cierre, textura y transparencia. Generar algo «similar» no asegura que corresponda al modelo inventariado.

| Material disponible | Hallazgo | Ruta recomendada |
| --- | --- | --- |
| WHYJ, la mayoría de los catálogos | Páginas raster de 2,480 × 3,508 px. Las fotos suelen estar integradas a la página y sus recortes son menores. | Recortar la foto del archivo original, separar texto/fondo y probar uniformidad; restauración moderada solo si preserva el modelo. |
| Tapas de inyección (`pdf-09`) | Resolución variable; una página de muestra tiene 1,240 × 1,754 px, aunque otras llegan a 3,174 × 4,490. | Evaluar por página y modelo; buscar la mejor aparición antes de decidir sobre IA. |
| Vasos de papel (`pdf-12`) | Páginas de solo 909 × 1,286 px; varias fotos individuales son muy pequeñas. | Solicitar originales del proveedor cuando sea posible. Probar unas pocas restauraciones y rechazar resultados que inventen forma/acabado. |
| Segundo catálogo PET (`pdf-14`) | Páginas de 1,323 × 1,871 px. | Buscar el mismo modelo en fuentes de mayor resolución; no asumir que 89 y 90 mm son equivalentes. |
| Jihong general (`pdf-15/16`) | Páginas de aproximadamente 2,410 × 1,645 px, con composiciones y modelos personalizados. | Útiles para categorías/familias. Una composición no demuestra un SKU concreto. |
| Jihong helados (`pdf-17/18`) | Hay múltiples imágenes incrustadas independientes, varias de gran tamaño. | Preferir esos assets originales a una captura de página; asociarlos con código y revisión visual. |
| Bento original (`pdf-19`) y traducido (`pdf-20`) | Original de aproximadamente 4,961 × 3,508 px por pliego; traducción de 3,000 × 2,121 px. | Recortar del **original**; usar la traducción para identificar modelo y contenido. |
| QUNLU fruta, repostería y maestros | Pliegos próximos a 4,961 × 3,508 px; la hoja de vasos llega a 7,442 × 3,508 px. | Recortes de originales generalmente más prometedores. Revisar densidad de cada página, transparencia y cierres. |
| 18 JPG de referencia | 13 composiciones cuadradas de 1,600 px y 5 pósters de 1,131 × 1,600 px, con marca Lynx. | Definen paleta, iluminación, fondos y dirección de arte. No sirven para asignar medidas/modelos del inventario. |

### Prueba propuesta para la siguiente etapa

1. Elegir 12–20 modelos representativos: vaso PET transparente, tapa, vaso de papel de baja resolución, botella, bento, bandeja, envase de fruta y un producto de helado.
2. Registrar recorte original, PDF/página/modelo y tamaño real en píxeles. No medir la calidad por el tamaño del pliego completo.
3. Comparar recorte limpio y restauración moderada a la escala de listado y galería. Revisar especialmente labios, enganches, divisiones y transparencia.
4. Aceptar la extracción cuando conserve detalle suficiente. Pedir originales cuando la información visual no alcance; la IA no recupera especificaciones ausentes.
5. Usar generación desde las referencias para composiciones editoriales aprobadas, claramente separadas de la representación exacta de un producto.

No se ejecutó esta prueba, no se generaron imágenes y no se incorporaron recortes al sitio. La decisión sobre esa etapa queda para el siguiente encargo.

## Verificación

Se revisaron visualmente pliegos representativos de todos los grupos, tarjetas de recipientes, tablas de huevos y película del maestro, y las 18 referencias en conjunto. Los catálogos raster se procesaron con OCR conservando cajas y confianza; esa confianza no sustituye la comprobación de cada especificación.

La validación del inventario comprueba IDs, relaciones, referencias de página, cobertura, hashes y borradores. El sitio conserva su catálogo demo. Sus comandos `validate:data`, `check` y `build` finalizaron correctamente; Astro check reportó cero errores y advertencias y el build generó 73 páginas estáticas.
