# Revisión de referencias e implementación inicial

## Fuentes revisadas

- `AGENTS.MD`, completo: instrucción vigente.
- `lynx-packaging-wireframe (1).pdf`: 16 páginas; texto extraído y composiciones revisadas mediante renders.
- `lynx-packaging-mockup.pdf`: 25 páginas, incluyendo desktop, móvil y navegación; texto extraído y composiciones revisadas mediante renders.
- YUTO Home: revisión en navegador en desktop y 390 px. Su geometría y escala sirven de referencia; ningún asset de YUTO se incorpora al proyecto.

## Qué se conserva

| Patrón | Referencia | Implementación |
| --- | --- | --- |
| Hero de video y mensaje a la izquierda | Wireframe 1, mockup 2/14 | Home de 90 svh, sin CTA en el hero |
| Introducción centrada y amplio espacio vertical | Wireframe 2, mockup 2/3 | Intro reutilizada en Home y General |
| Pestañas y tres imágenes protagonistas | Wireframe 3, mockup 2 | Pestañas accesibles, carrusel local, una tarjeta principal en móvil |
| Imágenes grandes con panel superpuesto alternado | Wireframe 8/9, mockup 5/17 | Página general de productos, componente EditorialBlock |
| Catálogo clásico | Wireframe 10, mockup 6/18 | Filtros laterales desktop, acordeón móvil, cuadrícula |
| Descripción centrada y galería horizontal | Wireframe 11, mockup 7/19 | Ficha de producto, galería manual y relacionados |
| Contacto asimétrico | Wireframe 15, mockup 11/23 | Introducción izquierda, campos en dos columnas |
| Header/footer marino, acento azul claro | Mockup completo | Tokens centralizados Tailwind 4 |

El header de Home se superpone al hero. Mantiene fondo marino mientras el video es un placeholder blanco, como el mockup, para asegurar contraste. El estado de scroll está preparado. La transparencia sobre un video real deberá revisarse al recibirlo.

## Cambios que prevalecen sobre los PDFs

- Seis entradas: About, Catalogs, Products, Solutions, Case Studies, Contact.
- Sustentabilidad deja de ser sección corporativa, ruta y entrada de navegación. La categoría de productos sustentables se incorpora cuando existan productos y evidencias.
- Una sola página de recursos de suministro; no se crean fichas individuales por proveedor.
- Se usan las seis etapas de servicio del chat del 01/10 (producción y calidad separadas) y los siete sectores recibidos.
- Se omiten indicadores y mapa porque no hay datos reales.
- Casos de estudio tiene un estado vacío honesto; no se generan casos ni rutas individuales ficticias.

## Assets e inventario

El repositorio original solo contenía AGENTS.MD y los dos PDFs. No se encontraron documentos de estructura, catálogos comerciales, fotos de fábricas, enlaces Drive ni el PNG independiente del logo.

El logo de `public/images/lynx-logo.png` se extrajo directamente de la imagen incrustada en la página 2 del mockup (1249 x 1102), sin recolorear, recortar ni rediseñar. Sustituir por el original o una variante transparente oficial cuando se entregue. No se extrajeron otros assets de las referencias como contenido comercial.

## Estado del prototipo

`src/data/site.json` contiene `preview: true`: todo el sitio lleva `noindex, nofollow`. Las tres categorías y dieciocho productos son muestras explícitas con estado `demo`, sin especificaciones comerciales. Los filtros usan un atributo llamado "Grupo de muestra", sin simular material o certificaciones reales. Las rutas de demostración se generan solo mientras `preview` es verdadero; los registros `draft` nunca generan páginas ni enlaces.

La oferta de siete sectores está confirmada, pero sus descripciones extensas, imágenes y productos aplicables quedan pendientes. General ahora contiene la presentación corporativa EN recibida el 01/10, su traducción ES para revisión y los cuatro valores de cultura ES/EN proporcionados. Home utiliza una síntesis editorial de esa presentación. Ver [contenido del chat](contenido-del-chat.md) para procedencia, decisiones y pendientes actualizados.

La ubicación de Servicio integral y Recursos dentro de About sigue siendo propuesta: se presentan con nota de revisión en General, sin añadir Ability al menú principal. Los nombres de rutas `/es/`, `/en/` y los segmentos técnicos comunes son una propuesta técnica.

Tipografía propuesta: Arial/Helvetica con fallback sans-serif del sistema, sin peticiones a servicios de fuentes. El token `--font-sans` permite reemplazarla por una fuente local aprobada y licenciada.

Contacto permanece en demostración: la validación de nombre, email y mensaje es propuesta. No hay solicitud de red, destino configurado ni mensaje de recepción. El botón confirma únicamente que los campos son válidos. La conexión requiere servicio, destinatario, campos y privacidad aprobados; añadir un endpoint a site.json por sí solo NO activa el formulario.

## Antes de publicación real

1. Recibir catálogos, fotos, nombres de categorías, fichas, especificaciones y relaciones; retirar muestras demo o mantener `preview: false` para excluirlas.
2. Incorporar URLs reales Drive en `catalogs.json` con estado `published`.
3. Validar textos corporativos, traducciones y agrupación de About.
4. Recibir y autorizar casos; el recorrido de caso individual aún no se implementa.
5. Configurar proveedor de formulario y privacidad, e implementar estados de envío/error/éxito a partir de respuestas reales.
6. Confirmar dominio en `site.json.publicUrl`; genera canonical y alternates absolutos. La validación bloquea producción sin dominio.
7. Cambiar `preview` solo cuando el contenido esté listo; construir, revisar y autorizar despliegue. No se ha desplegado a Vercel.

El sitemap se genera en build únicamente para producción con dominio real; el prototipo no entrega URLs indexables. Se mantiene 404 estática.

## Verificación de esta entrega

- `npm run check`: cero errores, warnings o hints en 35 archivos.
- `npm test`: tres pruebas útiles aprobadas para filtros OR/AND, restauración y cambio de idioma.
- `npm run build`: datos válidos y 74 páginas estáticas (incluye las muestras en ES/EN y 404).
- Auditoría del HTML construido: 4,236 enlaces internos comprobados sin rutas rotas, IDs duplicados ni errores de H1/noindex.
- Navegador: Home, productos general, categoría, ficha, navegación móvil y contacto; revisión a 390, 768 y 1440 px. Sin errores ni warnings de consola en las páginas revisadas.
- Interacciones: mega menú por botón y Escape; acordeón de soluciones móvil; pestañas con flechas de teclado; galería manual; filtros con URL, restauración y limpieza; formulario con validación local y mensaje explícito de no envío.
- Corregidos durante QA: limpieza de filtros antes del reset del navegador; colisión de `.container` con la utilidad Tailwind (ahora `.site-container`); campos de contacto apilados en móvil.

La preview de esta sesión está en `http://127.0.0.1:4322/es/`, porque el puerto 4321 estaba ocupado. Esto es un servidor local de revisión; no un despliegue remoto.

## Rutas de idiomas — 2 de octubre de 2026

Por instrucción de Luis, español se sirve directamente en / y sus páginas no llevan prefijo de idioma. Inglés conserva /en/. Esta decisión sustituye la propuesta anterior de /es/. Se elimina la página de redirección de la raíz y el selector ES/EN conserva la misma entidad. Los enlaces antiguos con /es/ deben actualizarse a las nuevas rutas.
