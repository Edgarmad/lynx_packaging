# Catálogos conectados a Drive

Carpeta recibida: https://drive.google.com/drive/folders/1pkkUF2IYl8nFF-VJeyUBgXdgcPEnMk6B

Fecha de comprobación: 7 de octubre de 2026.

Se identificaron 42 PDFs en Papel, Plástico, Sostenible y Vasos y accesorios, separados en ES y EN. Las vistas de los 42 archivos fueron accesibles sin autenticación y mostraron los nombres esperados. Esta comprobación valida acceso y correspondencia de nombres; no compara bytes descargados con los originales.

`src/data/catalogs.json` centraliza los 21 registros bilingües y sus 42 URLs. `src/data/catalog-groups.json` define los cuatro grupos mediante IDs, sin duplicar títulos ni URLs. Menú desktop/móvil, footer y listado existente seleccionan el archivo según el idioma actual. No se copiaron PDFs a public/ ni se desplegó el sitio.

Los nombres Fuentes privadas y Revisión privada NO restringen acceso: ambas carpetas fueron visibles sin iniciar sesión dentro de la carpeta compartida. Antes de colocar documentos confidenciales, restringir sus permisos o moverlas fuera del padre compartido. Ninguna está enlazada desde la web. No se modificaron permisos ni archivos remotos.

Inventario de IDs y rutas observadas: `drive-catalog-links.json`.
