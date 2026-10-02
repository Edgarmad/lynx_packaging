# Lynx Packaging

Prototipo corporativo bilingüe con Astro estático, TypeScript estricto y Tailwind 4. Sin framework de cliente, backend ni CMS.

## Desarrollo

Node 24 LTS (registrado en `.nvmrc`) y npm. Dependencias fijadas en `package-lock.json`.

```sh
npm ci
npm run dev
```

Abrir `http://127.0.0.1:4321/es/`. La raíz dirige a español. ES/EN conserva la entidad con los mismos segmentos técnicos.

```sh
npm run validate:data
npm run check
npm test
npm run build
npm run preview
```

`build` valida datos y produce `dist/`; `preview` sirve ese resultado localmente. En Vercel seleccionar Astro, `npm run build`, salida `dist`, Node 24. No se necesita adapter de servidor ni reescrituras de SPA. La publicación necesita autorización.

## Contenido y mantenimiento

- `src/data/`: JSON de negocio; identificadores compartidos y textos ES/EN.
- `src/types/content.ts`: contratos Zod y tipos inferidos.
- `src/lib/data.ts`: carga, publicación y validación de relaciones.
- `src/i18n/ui.ts`: interfaz traducida.
- `src/styles/global.css`: tokens Tailwind y patrones visuales.
- `src/components/`: navegación, patrones de sección, media, filtros y galerías.
- `src/pages/[lang]/`: plantillas. Productos, categorías y soluciones usan `getStaticPaths()`.
- `docs/diseno-y-pendientes.md`: análisis, fuentes, propuestas y pendientes.

Para agregar un producto, incorporar registro y assets locales, enlazar IDs de categorías y soluciones, completar ES/EN y validar. Un producto publicado no puede referenciar borradores o muestras. No crear un archivo Astro por producto.

Los assets de media viven bajo `public/images/`, con alt localizado y ratio reservado. Cambiar `placeholder` a `false` y completar `src` al recibir material real. Videos disponibles usan controles y no autoplay. El logo se conserva como fue extraído del mockup.

El prototipo tiene `preview: true`, muestras `demo` claramente etiquetadas y `noindex` global. El formulario valida localmente y no envía datos. Los catálogos no tienen enlaces hasta que se reciban URLs de Drive. No hay datos comerciales ficticios, fotos de stock ni assets ajenos incorporados.

Astro sirve HTML navegable sin JavaScript. La mejora con JavaScript añade filtros en query parameters (OR dentro de atributo, AND entre atributos), tabs, galerías y menú móvil. Sin JavaScript se ven todos los productos y paneles; los filtros no se aplican.
