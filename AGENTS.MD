# AGENTS.MD — Lynx Packaging

Documento de contexto e instrucciones para la LLM que implemente el proyecto.
Actualizado el 30 de septiembre de 2026. Idioma de trabajo con Luis: español.

## 1. Misión

Construir el sitio corporativo y catálogo de Lynx Packaging con Astro, TypeScript y Tailwind, como sitio estático desplegado en Vercel. Debe presentar la empresa, sus productos, sus soluciones por sector, su servicio integral, sus recursos de suministro y sus casos de diseño, y conducir al formulario de contacto.

El responsable técnico es Luis. Sus últimos proyectos usan Astro; este proyecto continúa ese enfoque. No es necesario recuperar código de otros proyectos para empezar. El código debe ser limpio, fácil de mantener y extensible mediante datos, componentes y plantillas, sin introducir infraestructura que no se necesita.

La implementación debe parecerse a YUTO en composición, proporciones y recorrido visual. Una landing genérica de packaging ya fue rechazada. No interpretar la referencia solo como una inspiración temática.

## 2. Prioridad de decisiones

1. Instrucciones nuevas y explícitas de Luis.
2. Feedback más reciente de Mila Lin y decisiones de este documento.
3. Documento de estructura actualizado de Lynx.
4. Wireframe y mockup, únicamente donde no contradigan los cambios posteriores.
5. YUTO como referencia visual, adaptada al alcance y contenido de Lynx.

Los mensajes de Mila evolucionaron de cinco a seis elementos de navegación. La última decisión de las 12:17 del 30 de septiembre confirma seis: About, Catalogs, Products, Solutions, Case Studies, Contact.

Los wireframes y mockups anteriores contienen elementos que ya no forman parte del alcance: Sustentabilidad como sección independiente y proveedores con páginas individuales. No trasladarlos al código.

No publicar como aprobadas las propuestas pendientes. Se pueden preparar componentes y datos para ellas, dejando su estado claro en documentación y evitando enlaces públicos a páginas inexistentes.

## 3. Decisiones técnicas obligatorias

- Astro con salida estática (`output: 'static'`).
- Node.js se utiliza para desarrollo y build; no habrá un servidor Node propio en producción.
- Vercel sirve el resultado estático. No introducir SSR, ISR, API routes ejecutadas en servidor, funciones serverless ni middleware de servidor para resolver este alcance.
- No habrá backend, base de datos, CMS, panel de administración, autenticación, carrito, checkout ni pagos.
- Toda la información de negocio será local y versionada en el repositorio. Los archivos JSON alimentan catálogos, productos, categorías y otros contenidos repetibles.
- Los assets serán locales, salvo los enlaces externos de los catálogos en Drive y la futura integración de contacto si se confirma.
- TypeScript estricto. Evitar `any`, duplicación de lógica y componentes que mezclen navegación, datos, filtrado y presentación en un solo archivo.
- Tailwind define los tokens de color, tipografía, espaciado y estilos compartidos. Mantener un punto central de configuración, no repetir valores hexadecimales por componente.
- Priorizar componentes Astro y JavaScript pequeño de navegador. No instalar React, Vue ni otro framework de cliente si no existe una necesidad concreta que Astro y JavaScript no resuelvan bien.
- Usar un solo gestor de paquetes y un solo lockfile. Si se parte de cero, npm es una opción razonable; si existe repositorio, respetar el gestor existente.
- Elegir versiones estables compatibles al iniciar, verificar la documentación oficial y fijarlas mediante lockfile. Usar una versión LTS de Node compatible con Astro y Vercel, registrada en el proyecto. No actualizar dependencias indiscriminadamente durante la implementación.

### Generación de páginas

Para productos, categorías y soluciones, usar rutas parametrizadas y `getStaticPaths()` con los datos locales. No crear un archivo `.astro` por registro.

Ejemplo conceptual: una plantilla de producto atiende todos los productos; el build genera un HTML por URL publicada y por idioma. Tener cien productos puede generar cien páginas estáticas por idioma, pero se mantienen una plantilla y sus componentes, no cien archivos fuente repetidos.

Los JSON se leen y validan durante el build. Modificar un JSON requiere un nuevo build y despliegue. No diseñar como si los datos pudieran guardarse en el servidor después de publicar.

Los filtros y carruseles se ejecutan en el navegador sobre información estática. No convertir el catálogo completo en una SPA para evitar implementar rutas estáticas.

## 4. Idiomas

- Sitio público: español e inglés.
- Chino simplificado: idioma de revisión documental para la clienta; no se ha solicitado una tercera versión del sitio.
- Usar identificadores comunes e información localizada; no mantener dos catálogos independientes que puedan divergir.
- Separar textos de interfaz de textos de negocio. Cada página debe recibir un idioma explícito.
- ES/EN debe abrir la misma entidad en el idioma elegido, conservando contexto cuando exista traducción.
- Propuesta inicial de rutas: `/es/` y `/en/`, con ruta raíz estática que dirija a español sin depender de geolocalización o cookies. Esta convención es una decisión técnica propuesta, no una URL ya aprobada por la clienta.
- Para empezar, se pueden mantener segmentos técnicos iguales en ambos idiomas y localizar el contenido. Si se eligen slugs traducidos, centralizar su correspondencia por ID y no construir enlaces mediante reemplazos de cadenas.
- No mostrar español accidentalmente dentro de una página inglesa. Si falta una traducción necesaria, marcar el registro como incompleto y aplicar la política de publicación; no ocultar la falta mediante un fallback silencioso.

## 5. Identidad visual

| Token | Valor | Uso |
| --- | --- | --- |
| Brand primary | `#182037` | Sustituye el naranja de YUTO; botones, superficies principales y elementos activos |
| Brand accent | `#BACAD7` | Acentos, bordes, indicadores y detalles secundarios |
| Brand white | `#FFFFFF` | Texto sobre superficies azules y fondos blancos |

Luis pidió explícitamente: donde YUTO utiliza naranja, utilizar azul; letras blancas en los elementos azules y algunos acentos con el otro azul. El texto sobre fondo blanco necesita contraste legible: utilizar el azul marino, no blanco sobre blanco. El azul claro no debe convertirse en texto pequeño de bajo contraste.

El logo fue entregado como `image(20260930-142943).png`. Contiene un símbolo de Lynx, el nombre y “Packaging Solutions”, con detalles dorados. Conservar el logo recibido sin recolorear sus detalles ni rediseñarlo. Solicitar o utilizar una variante transparente/vectorial cuando esté disponible, sin inventar una variante oficial. Importar el asset local al proyecto; no enlazar a rutas temporales del entorno de trabajo.

Hasta tener imágenes y videos, dejar espacios blancos con proporciones reservadas y etiquetas del tipo “Here's gonna be an image” o “Here's gonna be a video”. No añadir stock arbitrario, imágenes generadas ni fotos de YUTO como si fueran fábricas o productos de Lynx. El placeholder debe ser un componente reutilizable que permita sustituir el asset sin rehacer el layout.

La tipografía exacta todavía no está aprobada. Elegir una sans serif corporativa legible, definirla mediante tokens y mantenerla sustituible. Registrar esa elección como propuesta. Evitar dependencias de fuentes externas durante la visita si se puede alojar la fuente localmente con licencia válida.

## 6. Navegación definitiva y agrupaciones

| Elemento del header | Comportamiento y contenido |
| --- | --- |
| Acerca de nosotros / About | General. Se propone agrupar Ability aquí, con Servicio integral y Recursos de la cadena de suministro |
| Catálogos / Catalogs | Despliega lista de catálogos; cada entrada abre directamente su enlace de Drive |
| Productos / Products | Acceso al resumen general y submenú de categorías; categoría → producto individual |
| Soluciones / Solutions | Resumen general y submenú de las siete soluciones por sector |
| Casos de estudio / Case Studies | Sección propia; se propone listado y páginas de casos individuales |
| Contacto / Contact | Enlace directo al formulario, sin submenú |

- Respetar el orden: About, Catalogs, Products, Solutions, Case Studies, Contact.
- No agregar Ability como séptimo elemento del header sin nueva instrucción.
- La ubicación de Ability dentro de About y los nombres públicos de sus páginas siguen como propuesta por validar.
- No hay páginas internas de Catálogos. No confundir los PDFs en Drive con las páginas internas de categorías de productos.
- No hay páginas individuales por proveedor. Una sola página reúne recursos de la cadena de suministro y fotos de fábricas.
- Productos sustentables es una categoría dentro de Productos. No hay elemento independiente de Sustentabilidad, página corporativa independiente ni variante sustentable separada asumida por defecto.
- No hay noticias, eventos ni inversionistas.
- Mantener header y footer únicos y reutilizables. La navegación debe derivarse de una configuración central y las entidades publicadas.
- Menús desktop amplios inspirados en YUTO. Mobile: panel con acordeones. El padre de Productos y Soluciones debe permitir navegar al resumen además de desplegar su submenú.

## 7. Plantillas y rutas propuestas

Base actual: once tipos de plantilla. Una ficha individual de caso sería el duodécimo tipo si se valida.

| Plantilla | Ruta relativa propuesta bajo el idioma | Origen |
| --- | --- | --- |
| Inicio | `/` | Contenido local de Home |
| General | `/about/overview/` | Contenido corporativo local |
| Servicio integral | `/about/one-stop-service/` | Contenido recibido de Mila |
| Recursos de suministro | `/about/supply-chain-resources/` | Texto recibido y fábricas extraídas de PDFs |
| Productos general | `/products/` | Categorías locales |
| Categoría | `/products/categories/[slug]/` | JSON de categorías y productos |
| Producto individual | `/products/[slug]/` | JSON de productos |
| Soluciones general | `/solutions/` | JSON de soluciones |
| Solución individual | `/solutions/[slug]/` | JSON de soluciones y relaciones |
| Casos de estudio | `/case-studies/` | Casos aprobados disponibles |
| Contacto | `/contact/` | Textos y configuración de contacto |
| Caso individual propuesto | `/case-studies/[slug]/` | Solo publicar si se valida este recorrido |

La página de recursos es una sola ruta, aunque sus bloques provengan de varios registros de fábricas. Las soluciones y categorías usan plantillas independientes: una solución por sector no equivale automáticamente a una categoría de producto.

## 8. Composición visual por página

### Inicio

La fidelidad estructural de la Home es prioritaria:

1. Hero de video a ancho completo, casi toda la primera pantalla; objetivo aproximado 85–95 vh, ajustado por viewport y contenido. Header superpuesto al hero y sólido al avanzar por scroll. Texto principal grande hacia la izquierda. No añadir CTA o tarjetas flotantes sin una razón aprobada.
2. Presentación de Lynx centrada, con descripción amplia y bastante espacio vertical. No convertirla en una sección genérica de texto a un lado y foto al otro.
3. Indicadores corporativos solo si hay cifras reales. El mapa o bloque de presencia de YUTO también es condicional a datos reales; no inventar cobertura o instalaciones.
4. Productos con título centrado, pestañas de categorías y carrusel de imágenes grandes. La categoría sustentable participa en Productos cuando haya datos aprobados.
5. Bloque de capacidades sobre imagen o video, con texto superpuesto y accesos coherentes con el Servicio integral confirmado. Evitar confundir capacidades con los sectores de Soluciones.
6. Accesos a soluciones o casos cuando sean útiles, manteniendo la escala y ritmo de la referencia y sin introducir secciones fuera del alcance.
7. Footer compartido. No replicar noticias o eventos de YUTO.

El antiguo bloque independiente de Sustentabilidad de la Home no debe crear una sección o ruta que contradiga la nueva navegación. Si se conserva un acceso visual a productos sustentables, debe conducir a su categoría dentro de Productos.

### General

Banner interior panorámico más bajo que el hero de Home, breadcrumb y título hacia la izquierda. Introducción con título centrado y texto amplio. Indicadores y video corporativo solo si existen. Cultura o historia se incorporan únicamente con contenido real.

### Servicio integral

Una sola página presenta el proceso completo. Reutilizar secciones amplias de texto e imagen, con alternancia cuando corresponda, sin convertir cada etapa en una página. Relacionar Diseño creativo con casos de estudio aprobados.

### Recursos de la cadena de suministro

Una sola página con introducción, fotos de fábricas y descripciones. Puede contener múltiples bloques o galerías por recurso; ninguno necesita una URL individual. No inventar nombres, certificaciones, propiedad de fábricas o capacidades no documentadas.

### Productos general

Banner con gran tarjeta blanca de texto superpuesta a la izquierda. Introducción centrada. Bloques de categoría con imágenes grandes y tarjetas de texto superpuestas, alternando izquierda y derecha. No sustituirlos por una cuadrícula de mini tarjetas; esa cuadrícula pertenece al listado de categoría.

### Categoría

Layout propio de catálogo clásico integrado a la identidad de YUTO: título, descripción, filtros derivados de datos y cuadrícula de imágenes consistentes. Desktop puede usar filtros laterales; mobile un panel de filtros. Adaptar columnas y paginación al volumen real, no a cantidades inventadas.

### Producto individual

Seguir la referencia de YUTO: breadcrumb, nombre centrado, descripción amplia, fondo introductorio suave y galería horizontal protagonista con flechas e indicadores. Especificaciones disponibles debajo y productos relacionados. No usar layout de tienda con precio, carrito o compra.

### Soluciones

Resumen con banner interior, título centrado y bloques amplios. Detalle de solución con explicación del sector, ejemplos y productos aplicables. Los filtros del sitio de YUTO no son requisitos automáticos: incluirlos solo cuando existan datos suficientes y una utilidad clara.

### Casos de estudio

La sección está confirmada. El listado y fichas individuales se proponen. Los casos completos deben vivir en un solo lugar y enlazarse desde Diseño creativo y las soluciones relevantes; no duplicar contenidos completos. No inventar clientes, resultados, métricas o casos comerciales para rellenar la sección.

### Contacto

Banner interior. Texto introductorio a la izquierda y formulario en dos columnas a la derecha en desktop, apilado en mobile. Propuesta inicial de campos: nombre, apellido, correo, teléfono, empresa, país/región y mensaje. Validar cuáles son obligatorios y la configuración final antes de conectarlo.

## 9. Contenido de negocio recibido

### Servicio integral o One Stop Service

La propuesta es un solo socio de cadena de suministro que gestione todo el proceso desde la idea inicial hasta la entrega: diseño, muestras, producción, inspección de calidad, logística internacional y almacenamiento local, hasta recibir los productos.

Cinco bloques principales:

1. **Diseño creativo.** Traducir necesidades de marca en soluciones fabricables. Trabajar estrategia y posicionamiento de marca, características del producto y escenarios de uso. Planificar desde concepto hasta familias de empaques. Cubrir gráficos, estructura, forma, materiales y acabados para aportar valor comercial y atender objetivos de costo. Mostrar imágenes de diseño y casos reales cuando estén disponibles.
2. **Producción eficiente y control de calidad.** Seleccionar fábricas según requisitos, estándares de calidad, volumen y presupuesto. Supervisar confirmación previa a producción, verificación de materiales y colores, seguimiento de producción, inspección de producto terminado y control previo al embarque. Imagen prevista: taller de fábrica.
3. **Logística internacional.** Coordinar desde las fábricas proveedoras hacia México. Organizar transporte marítimo, terrestre y procedimientos relacionados según tipo de producto, cantidad, calendario y destino. Imagen prevista: fábrica en China → contenedor → puerto → transporte marítimo → puerto mexicano. No convertir la secuencia en una promesa de rutas específicas aún no documentadas.
4. **Almacenamiento local.** Almacenamiento y gestión de inventario para acercar la cadena de suministro al negocio. Ajustar a ciclos de compra y demanda, reducir tiempos de respuesta, mejorar reposición y apoyar continuidad de pedidos. Imagen prevista: almacén local.
5. **Entrega de última milla.** Desde almacenes locales en México hasta instalaciones del cliente. Transporte según volumen, frecuencia y destinos; clientes mencionados: restaurantes, hoteles, cafeterías, tiendas y otros negocios. Imagen prevista: vehículo de reparto.

La clienta ya entregó este contenido. No volver a preguntar qué capacidades ofrece como si aún fueran desconocidas. Quedan por completar detalles comerciales concretos y material visual.

### Recursos de la cadena de suministro

La clienta describe una red sólida de proveedores de largo plazo con años de cooperación. Para empaques de papel, plástico y consumibles complementarios, Lynx busca recursos de producción adecuados y equilibra calidad, plazo y costo. La red permite atender diversas necesidades de packaging.

Extraer fotos de fábricas y sus descripciones de los PDFs que se entreguen. Mostrar todo en una sola página. No afirmar que Lynx es dueña de las fábricas si los documentos no lo indican.

### Soluciones por sector

| Español | English | Referencia china recibida |
| --- | --- | --- |
| Empaques para alimentos y bebidas | Food & Beverage Packaging | 食品饮料包装 |
| Empaques para cosmética y cuidado personal | Cosmetics & Personal Care Packaging | 日化美妆包装 |
| Empaques para electrónica | Electronics Packaging | 电子产品包装 |
| Empaques para comercio electrónico y retail | E-commerce & Retail Packaging | 电商零售包装 |
| Empaques premium para regalos | Premium Gift Packaging | 礼品精装包装 |
| Empaques industriales | Industrial Packaging | 工业包装 |
| Otros empaques personalizados | Other Custom Packaging | 其他定制类包装 |

Personalización ya no es la única solución conocida. Es parte de la oferta, con opciones y condiciones todavía por detallar. Los sectores de esta tabla no deben copiarse ciegamente al JSON de categorías de productos.

## 10. Organización del repositorio

Estructura sugerida, adaptable si hay un repositorio existente:

| Área | Responsabilidad |
| --- | --- |
| `src/pages/` | Entradas de rutas estáticas y parametrizadas; lógica mínima |
| `src/layouts/` | Layout base, SEO, idioma, header y footer |
| `src/components/navigation/` | Header, mega menú, navegación móvil, selector de idioma, breadcrumbs |
| `src/components/ui/` | Botón, contenedor, título de sección, placeholder de media, controles reutilizables |
| `src/components/products/` | Tarjetas, listado, filtros, galería, especificaciones, relacionados |
| `src/components/sections/` | Hero, presentación centrada, bloques superpuestos, secciones alternadas y capacidades |
| `src/data/` | JSON locales de negocio y configuración |
| `src/i18n/` | Textos de interfaz en ES/EN |
| `src/lib/` | Carga y validación, relaciones entre entidades, rutas, SEO y filtrado puro |
| `src/types/` | Tipos y contratos compartidos |
| `src/styles/` | Tokens Tailwind, estilos globales y tipografía |
| `public/` o `src/assets/` | Assets locales según el tratamiento requerido |
| `scripts/` | Validación de datos y tareas de mantenimiento justificadas |
| `docs/` | Decisiones, fuentes y pendientes de contenido |

Evitar una carpeta de componentes gigante sin organización, un JSON único con todo el sitio, o un constructor de páginas genérico con decenas de condiciones. Reutilizar patrones reales; no abstraer cualquier bloque distinto hasta volverlo difícil de entender.

## 11. Modelo de datos local

Propuesta de archivos:

- `site.json`: datos generales, configuración pública, contacto, SEO global.
- `navigation.json`: orden y comportamiento de los menús, referencias a páginas y grupos.
- `catalogs.json`: documentos externos en Drive.
- `categories.json`: categorías, orden y definición de atributos filtrables.
- `products.json`: productos y relaciones.
- `solutions.json`: las siete soluciones y contenidos asociados.
- `case-studies.json`: casos disponibles y estado de publicación.
- `capabilities.json`: Servicio integral y sus etapas.
- `supply-chain-resources.json`: introducción y recursos/fábricas para una sola página.
- `home.json` y `about.json`: textos y selección editorial de bloques.

### Contratos mínimos

| Entidad | Campos y reglas |
| --- | --- |
| Catálogo | ID estable, título ES/EN, URL de Drive, orden, estado, metadatos de fuente si disponibles |
| Categoría | ID, slug o slugs localizados, nombre ES/EN, descripción, media, orden, definiciones de filtros |
| Producto | ID, slug, nombre y descripción ES/EN, IDs de categorías, galería, atributos, especificaciones, relaciones con soluciones/casos, referencias de fuente y estado |
| Solución | ID, slug, título y contenido ES/EN, media, referencias a categorías/productos/casos y estado |
| Caso | ID, slug si se aprueba detalle, título y contenido ES/EN, media, relaciones, permisos/estado de publicación documentados |
| Etapa de servicio | ID, orden, título y descripción ES/EN, media y relaciones con casos |
| Recurso de suministro | ID, descripción ES/EN, galería y referencias a PDFs; no genera una ruta individual |
| Media | Tipo imagen/video, ruta local, alt ES/EN, dimensiones o aspect ratio, poster cuando corresponda, estado de placeholder |

- Separar IDs estables de nombres visibles y URLs. Relacionar entidades mediante IDs, no duplicar objetos completos.
- Los atributos filtrables deben usar claves normalizadas y valores comparables. Localizar etiquetas, no la identidad del atributo.
- Diferenciar material, dimensiones, aplicación y otros atributos; no asumir que todos los productos tienen todos los campos.
- No usar HTML arbitrario en JSON por comodidad. Empezar con textos y bloques estructurados simples; si hay necesidad real de rich text, documentar su formato y escape.
- Referencias de procedencia como PDF, página y observaciones son útiles para auditoría; no mostrarlas automáticamente al visitante.
- Validar JSON en build mediante schemas y tipos compartidos. Zod u otra solución ligera puede usarse si encaja con las dependencias; mantener una sola definición de contratos.
- Validar IDs y slugs únicos, traducciones, referencias existentes, categorías, URLs y rutas de assets. Un registro publicado inconsistente debe hacer fallar la validación.
- Distinguir `draft`, `published` y media pendiente o equivalentes. Las muestras necesarias para el prototipo deben estar claramente documentadas como muestras, no como productos reales.
- No emitir enlaces a entidades borrador. No indexar páginas de demostración con afirmaciones o datos ficticios.

## 12. Extracción de PDFs y mantenimiento

Cuando los PDFs estén disponibles:

1. Inventariar archivos y determinar qué información corresponde a catálogos, productos, soluciones o fábricas.
2. Registrar procedencia de imágenes y textos, incluyendo página del PDF.
3. Extraer y revisar imágenes, evitando capturas de baja calidad cuando pueda obtenerse el asset original.
4. Normalizar nombres, categorías, unidades y valores; no inventar especificaciones.
5. Preparar textos ES/EN conservando significado y condiciones. El chino es fuente/revisión, no idioma público adicional.
6. Definir filtros únicamente con atributos consistentes y útiles para comparar productos.
7. Incorporar datos validados y assets locales; revisar visualmente casos representativos antes de procesar todo el inventario.

El proceso de extracción ocurre fuera del runtime del sitio. No instalar un lector de PDF en el navegador para producir el catálogo en cada visita. No guardar PDFs grandes sin una necesidad clara: los catálogos públicos siguen enlazados a Drive.

Mantenimiento esperado: añadir un producto consiste en agregar su registro, assets y relaciones, validar y reconstruir. Añadir un catálogo consiste en agregar una entrada JSON. Cambiar colores o fuente se hace en tokens; cambiar header/footer se hace una vez en el componente compartido.

## 13. Filtrado y navegación del catálogo

- Filtrado en cliente sobre un índice mínimo y local, limitado a los datos necesarios. No enviar todos los textos corporativos y todas las galerías para filtrar una categoría.
- Todos los productos deben ser navegables en HTML estático y tener URLs propias, aunque JavaScript esté desactivado.
- Controles con etiquetas, estado activo, opción de limpiar y mensaje de resultados vacíos.
- Mantener filtros en query parameters si se implementa, para compartir y restaurar estado. No generar rutas de servidor por combinación de filtros.
- Definir de forma consistente: OR entre valores de un atributo y AND entre distintos atributos, salvo que la interfaz indique otra cosa.
- Elegir paginación o carga local progresiva según volumen. No prometer un contador o total inventado en placeholders.
- Productos sustentables se relacionan con su categoría real, sin duplicar la ficha del mismo producto.
- No implementar filtros de soluciones por copiar los de YUTO si faltan datos.

## 14. Contacto sin backend propio

El formulario es parte del objetivo del sitio, pero el mecanismo de envío todavía no está definido.

- Un sitio estático no envía correos ni persiste mensajes por sí solo. Necesita un servicio externo de formularios con endpoint público preparado para navegador, o una alternativa expresamente aprobada.
- No introducir un backend propio, función de Vercel, SMTP o una base de datos para resolverlo sin cambio de alcance.
- No exponer claves secretas en JavaScript ni en variables públicas.
- Preparar un componente de formulario con validación accesible y configuración central del destino externo; documentar que falta proveedor/destinatario.
- Si no hay endpoint confirmado, mantener un modo de demostración explícito y no mostrar éxito como si la solicitud hubiese sido enviada. El prototipo debe ser honesto sobre ese estado.
- El envío real solo se marca exitoso tras una respuesta efectiva del servicio. Incluir estados de envío, error y éxito; evitar envíos duplicados.
- Un enlace `mailto:` no equivale al formulario solicitado y no debe sustituirlo silenciosamente.
- Antes de publicar el formulario funcional, confirmar destinatario, servicio y texto de privacidad aplicable. No inventar promesas de tratamiento de datos.

## 15. Accesibilidad y responsive

- HTML semántico, un H1 por página, jerarquía de títulos, labels y botones reales.
- Mega menú y acordeones utilizables con teclado, foco visible, `aria-expanded`, Escape para cerrar y manejo razonable del foco en el panel móvil.
- Evitar interacciones que dependan exclusivamente de hover.
- Navegación por categorías y carruseles con controles accesibles; sin reproducción automática agresiva.
- Respetar `prefers-reduced-motion` y la posibilidad de pausar movimiento persistente.
- Para video hero, plantear autoplay muted/playsinline y poster con alternativa; la reproducción puede estar restringida en mobile. No depender de que el video cargue para leer el mensaje.
- Imágenes con dimensiones reservadas para evitar saltos; alt descriptivo o vacío si son decorativas.
- Verificar móvil, tablet y desktop, incluyendo 390 px, 768 px y 1440 px como referencias de QA, sin diseñar exclusivamente para esas tres medidas.
- El logo debe ser legible y proporcionado; no aplastarlo para encajar en el header.

## 16. Rendimiento y SEO

- Mantener JS por página mínimo; cargar funcionalidades solo donde se utilizan.
- Optimizar imágenes en build cuando corresponda. Reservar tamaños, usar formatos y fuentes adecuados; lazy load bajo el primer scroll y priorización razonable del hero.
- No descargar todas las imágenes de un carrusel antes de que sean necesarias.
- Un title y description por página/idioma, canonical correcto, `lang`, enlaces alternativos ES/EN y Open Graph cuando haya assets disponibles.
- Usar la URL pública real cuando se confirme; no dejar dominio de ejemplo como canonical de producción.
- Generar sitemap para páginas publicadas y 404 estática. No indexar borradores o páginas vacías de ejemplo.
- Datos estructurados solo si corresponden a contenido real. No añadir precios, disponibilidad, ratings o certificaciones ficticias.

## 17. Build y Vercel

- Comando de build del proyecto: `npm run build` si se utiliza npm. Astro produce `dist/`.
- Configurar Vercel como Astro y comprobar la salida estática. No añadir adapter SSR por costumbre; el despliegue estático no requiere ese servidor.
- Verificar dependencias compatibles, lockfile y versión Node antes del primer build remoto.
- No introducir `vercel.json` con reescrituras de SPA que intercepten todas las rutas: las páginas están prerenderizadas.
- Conservar previews para revisión de layout y contenido. Publicar a producción únicamente cuando Luis lo solicite o lo autorice dentro del flujo de trabajo.
- Evitar que enlaces internos apunten al dominio de preview; centralizar generación de rutas.
- Cambios de contenido local se despliegan mediante commit y rebuild, no mediante escritura en producción.

## 18. Calidad del código y verificación

- Mantener componentes con responsabilidades claras y props tipadas.
- Extraer funciones puras para rutas, relaciones, filtros y SEO; no duplicarlas entre desktop y mobile.
- Evitar concatenar clases Tailwind con nombres dinámicos que el build no pueda detectar; utilizar mapas de variantes completos.
- No mezclar configuraciones incompatibles de Tailwind 3 y 4. Para un proyecto nuevo, verificar la integración oficial actual; Tailwind 4 usa su integración Vite y tokens centralizados. Si existe proyecto, respetar su versión compatible.
- Documentar comandos reales en README. Scripts sugeridos: dev, build, preview, check y validate:data; implementar cada script antes de mencionarlo como disponible.
- Ejecutar validación de datos, comprobaciones TypeScript/Astro y build antes de entregar cambios.
- Pruebas útiles para lógica de filtros, relaciones y cambio de idioma. Evitar tests que solo repitan la implementación o pruebas triviales por cada bloque visual.
- Revisar en navegador al menos Home, listado, detalle de producto, menú mobile y contacto. Comprobar enlaces, teclado, tamaños, estados vacíos y que no hay errores de consola.
- Si se incorpora una dependencia, explicar su necesidad; no instalar librerías grandes para un botón, un acordeón o un scroll sencillo.

## 19. Orden de implementación sugerido

1. Revisar el repositorio y sus instrucciones. Inventariar documentos, logo, PDFs y assets disponibles sin asumir que existen por haber sido mencionados.
2. Crear o ajustar la base Astro estática, TypeScript, Tailwind, tokens, rutas de idiomas y contratos de datos.
3. Implementar layout compartido, header/mega menú, menú mobile, footer y placeholders de media.
4. Resolver Home fiel a YUTO y el recorrido Productos general → categoría → producto individual con datos locales.
5. Implementar General, Servicio integral y la página única de recursos de suministro.
6. Implementar las siete soluciones mediante datos y plantillas.
7. Implementar Casos de estudio con contenido aprobado; preparar detalle solo según validación del alcance.
8. Preparar contacto y su estado pendiente de integración externa.
9. Incorporar datos reales de PDFs, traducciones, SEO y assets; revisar responsive, accesibilidad y build.
10. Entregar resumen de lo implementado, verificaciones y pendientes concretos. No presentar contenido placeholder como final.

No detener todo el desarrollo por falta de PDFs, imágenes o una decisión de contenido: avanzar con estructura y placeholders donde sea independiente de esa información. No añadir infraestructura para compensar archivos que simplemente no han sido entregados.

## 20. Pendientes reales

- Ubicación pública definitiva de Ability dentro de About y nombres de sus dos páginas.
- PDFs de catálogos/fábricas, productos y assets para extraer información.
- URLs definitivas de los catálogos en Drive.
- Contenido corporativo General y cifras/alcance reales si se mostrarán.
- Detalles de cada solución y opciones o condiciones concretas de personalización.
- Productos sustentables y evidencias/criterios comunicables.
- Casos de diseño publicables, imágenes y permisos; aprobación de listado y detalle.
- Servicio externo y destinatario del formulario.
- Dominio público, datos de contacto y traducciones finales.

Ya están definidos: Astro, Vercel, sitio estático, sin backend ni admin, JSON locales, reutilización, Tailwind, idiomas ES/EN, paleta, seis elementos del menú, cinco etapas de servicio, siete soluciones y una sola página de recursos de proveedores. No volver a preguntar estas decisiones.

## 21. Referencias disponibles

### Artefactos del proyecto

- `lynx-packaging-estructura-es.docx`: definición actualizada en español, revisión 02.
- `lynx-packaging-estructura-en-zh.docx`: definición actualizada en inglés y chino simplificado.
- `lynx-packaging-wireframe.pdf`: referencia de composición corregida; anterior al feedback que elimina Sustentabilidad independiente y proveedores individuales.
- `lynx-packaging-mockup.pdf`: propuesta visual con paleta actualizada; todavía contiene estructuras anteriores al último cambio de alcance.
- `image(20260930-142943).png`: logo recibido.

Estos nombres identifican artefactos que Luis debe aportar o colocar en el repositorio. No asumir que viven en una ruta local específica. Si falta un archivo, registrar la ausencia y continuar con lo que este documento ya define.

### Referencias visuales YUTO

| Uso | URL |
| --- | --- |
| Inicio | https://www.szyuto.com/ |
| General | https://www.szyuto.com/about/overview |
| Lenguaje visual para servicio y recursos de fábricas | https://www.szyuto.com/about/creative_design |
| Productos general | https://www.szyuto.com/product |
| Producto individual | https://www.szyuto.com/productDetail/9503 |
| Soluciones general | https://www.szyuto.com/solution |
| Solución individual | https://www.szyuto.com/solution/packaging_solutions |
| Contacto | https://www.szyuto.com/contact |

La antigua referencia https://www.szyuto.com/sustainability ya no implica una página equivalente en Lynx. La categoría clásica de productos no tiene una referencia directa en YUTO y requiere diseño propio coherente.

Explorar las referencias en desktop y mobile antes de fijar layouts. Observar geometría, escala, espacios, tarjetas superpuestas, menús y motion; no copiar texto, código o assets ajenos al proyecto.

### Documentación técnica oficial

- Astro routing: https://docs.astro.build/en/guides/routing/
- Astro styles y Tailwind: https://docs.astro.build/en/guides/styling/
- Astro deployment: https://docs.astro.build/en/guides/deploy/
- Astro en Vercel: https://vercel.com/docs/frameworks/frontend/astro

Consultar documentación compatible con las versiones instaladas. Las decisiones de negocio de este documento prevalecen sobre funcionalidades opcionales de las plataformas.

## 22. Criterio de entrega

La implementación está lista para revisión cuando la estructura actual está reflejada, el recorrido de productos funciona, las entidades se generan desde datos locales, el header y footer se mantienen una sola vez, la paleta y composición respetan lo acordado, los idiomas no se mezclan, el build estático funciona y los pendientes se comunican sin simular contenido o envíos reales.

Al cerrar un bloque de trabajo, responder a Luis en español con cambios concretos, comprobaciones realizadas y pendientes relevantes. No afirmar que está publicado o que el formulario envía información si solo existe una preview o un prototipo.

## 23. Aprobación y publicación en GitHub

- Preparar el cambio y presentar el alcance concreto para revisión. No hacer push mientras el cambio no esté aprobado.
- Cuando Luis apruebe explícitamente ese cambio (por ejemplo, «aprobado» o «súbelo»), la aprobación autoriza crear el commit y subirlo directamente a `main` de `origin`, sin pedir una segunda confirmación para commit o push. No se requiere PR para este flujo.
- Antes del push ejecutar `npm run validate:data`, `npm run check`, `npm test` y `npm run build`. No publicar si falla alguna comprobación.
- Revisar el diff y agregar únicamente archivos del alcance aprobado. No incluir cambios previos o ajenos por el hecho de estar presentes en el directorio.
- Consultar el estado remoto antes de integrar. Conservar cambios de otras personas, resolver la integración sin sobrescribirlos y repetir verificaciones si cambia el resultado. No usar force push ni saltarse protecciones de GitHub. Si las protecciones impiden el push directo, informar el bloqueo.
- Reportar el commit y el resultado efectivo del push. Un push exitoso no demuestra que Vercel haya desplegado correctamente.
- Cuando Vercel esté conectado a `main`, la aprobación del push también autoriza el despliegue automático que esa conexión desencadene. La conexión inicial y la configuración de Vercel siguen pendientes de acceso; no afirmar que ya existen.
- Los permisos para ejecutar comandos son independientes de la aprobación del cambio: acceso completo permite trabajar y verificar sin confirmaciones por comando, pero no elimina la aprobación antes de publicar.
