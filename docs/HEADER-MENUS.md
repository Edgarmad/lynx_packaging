# Menús del header

Productos utiliza la jerarquía local de tres niveles. Desktop revela ramas mediante hover o activación; mobile usa acordeones. Las opciones se pueden activar con teclado y Escape cierra el menú. La imagen cambia únicamente al activar una categoría raíz y utiliza su mismo media de la página de productos.

Catálogos tiene cuatro grupos: papel (1), plástico (5: baking, bento, cups, F&V, eggs), sustentables (1), vasos (14). Los nombres definitivos de los 14 PDFs de vasos están pendientes. Cada descarga de catalog-groups.json contiene un ID, título ES/EN y url vacía. Mientras url esté vacía se muestra solo texto, sin enlaces ficticios ni etiquetas de pendiente. Para conectar una descarga, completar su url de Drive. src/lib/catalog-groups.ts valida traducciones, URLs y unicidad de IDs al construir.

## Validación visual

Revisión en navegador local a 390, 768 y 1440 px: menús de Nosotros, Catálogos, Productos y Soluciones; tres niveles de papel y cambio de imagen a plástico; teclado y Escape; acordeones móviles; configuración de 14 espacios de vasos; textos ES/EN. Sin desbordamiento horizontal en las medidas revisadas ni errores de consola. Se corrigió la ocultación previa de los controles de apertura desktop.
