# Ability: Servicio integral y Recursos de suministro

Implementación local revisada el 12/10/2026. Dos páginas completas dentro de Nosotros / About, en español e inglés:

- `/about/one-stop-service/` y `/en/about/one-stop-service/`.
- `/about/supply-chain-resources/` y `/en/about/supply-chain-resources/`.

Se respetan las rutas existentes: español en raíz e inglés bajo `/en/`. No se cambia la convención del sitio.

## Contenido

Fuente: Mila, 30/09/2026 15:51:01, recuperada en [Ability original](chat-review/ABILITY-ORIGINAL.md). La actualización del 01/10 19:01:51 separa producción y calidad: seis etapas en una sola página, sin rutas individuales. La ubicación dentro de About está confirmada el 05/10 16:41:21.

`capabilities.json` conserva introducción y descripciones breves para Home y añade `pageIntro` y párrafos completos para la página del servicio. Los párrafos EN siguen el contenido recibido; ES es adaptación editorial. El bloque conjunto de producción/calidad se distribuye entre esas dos etapas. Se omite la afirmación promocional de liderazgo sin respaldo adicional. No se agregan plazos, tarifas, certificaciones, direcciones ni capacidades numéricas.

`supply-chain-resources.json` conserva la introducción de red de proveedores y las galerías existentes, ahora organizadas en instalaciones, producción/impresión y laboratorio/almacenamiento. Estos títulos son organización editorial de las fotos, no nuevos servicios recibidos.

## Imágenes

Se reutilizan assets locales; no se generan ni compran imágenes:

| Bloque | Asset | Procedencia |
| --- | --- | --- |
| Diseño y banner de servicio | `design.webp` | Escena ilustrativa IA existente |
| Producción | `production.webp` | Catálogo Jihong |
| Calidad | `quality.webp` | Catálogo Jihong |
| Logística | `logistics.webp` | Escena ilustrativa IA existente |
| Almacenamiento local | `local-storage.webp` | Escena ilustrativa IA existente |
| Última milla | `delivery.webp` | Escena ilustrativa IA existente |
| Recursos: instalaciones | `supplier-campus.webp`, `supplier-building.webp` | Catálogo Jihong |
| Recursos: producción e impresión | `production.webp`, `printing.webp` | Catálogo Jihong |
| Recursos: laboratorio y almacenamiento | `quality.webp`, `laboratory.webp`, `warehouse.webp` | Catálogo Jihong |

Las escenas generales mantienen aviso visible de IA. Las fotos reales tienen atribución al proveedor, y el almacén Jihong no se presenta como almacén mexicano de Lynx. Fuentes detalladas: `docs/image-sources.json` y `docs/imagenes-editoriales.md`.

## Recorrido

Servicio integral tiene introducción centrada, índice de seis enlaces de ancla y secciones amplias alternadas. Recursos tiene introducción y galerías grandes por bloque; no genera páginas por fábrica. Ambas páginas enlazan entre sí y a Contacto. Header y footer ofrecen acceso a las dos rutas en el idioma actual. No se muestran enlaces a casos de diseño si no existen casos publicados y autorizados relacionados con la etapa.

No se añade JavaScript para el índice o las galerías; el contenido y los enlaces funcionan como HTML estático. Se mantienen los tokens compartidos de color, tipo y espaciado.

El formulario conserva su estado de demostración. Este trabajo no implica publicación ni push a GitHub.

## Verificación

- Validación de datos y build estático correctos: 2,539 páginas.
- Astro/TypeScript: 49 archivos, sin errores, advertencias ni hints.
- Ocho pruebas existentes aprobadas.
- Revisión de ambas páginas ES/EN, composiciones a 390, 768 y 1440 px sin desbordamiento horizontal; índice de seis etapas y tres galerías de proveedor.
- Accesos desde menú móvil y desktop, Escape para cerrar, cambio de idioma conservando entidad y enlaces entre las páginas verificados.
- Sin errores o advertencias de consola durante la revisión.
- Evidencia visual local: `tmp/ability-resources-desktop.png`.
