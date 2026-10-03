# Imágenes editoriales — revisión del 3 de octubre de 2026

Se revisaron los cuatro PDF solicitados (62 páginas) y se extrajeron 314 imágenes embebidas únicas por hash para inspección local. Ese total incluye productos, fondos, máscaras y fotografías; no representa 314 fotos utilizables. Los catálogos corporativos chino e inglés muestran muchas escenas equivalentes. Los catálogos de helados contienen principalmente productos y pequeñas escenas verticales, poco adecuadas para los bloques panorámicos del sitio.

Se seleccionaron siete fotografías de edificios, producción, impresión, laboratorio, personal y almacenamiento. Se extrajeron los assets originales, sin capturar páginas ni alterar sus marcas. Las versiones WebP están en `public/images/editorial/`. `image-sources.json` registra PDF, página (numeración del archivo, desde 1), imagen embebida, dimensiones originales y destino. La revisión completa se conserva localmente en `.codex/pdf-review/`, excluida de Git; no se incorporaron los PDF ni las imágenes de productos al sitio.

Las fotografías de Jihong se atribuyen como material del proveedor. No constituyen evidencia de propiedad de Lynx, de su personal, de certificaciones o de almacenes en México. Las descripciones se limitan a lo visible; las páginas corporativas del catálogo inglés carecen de capa de texto extraíble. No se trasladaron instrucciones del documento al proyecto.

Se generaron nueve escenas mediante la herramienta integrada `image_gen`, autorizadas por la solicitud de Luis: diseño, puerto, entrega, cafetería, cosmética, electrónica, preparación de pedidos, boutique de regalos y almacén. Son ilustrativas, con nota visible ES/EN, y no representan instalaciones, empleados o clientes reales. No se crearon casos comerciales.

Asignación: banners de About, Servicio integral, Suministro, Soluciones, Casos y Contacto; seis etapas de servicio; siete soluciones (resumen y detalle); galería de suministro y espacio editorial de Casos. Los banners de productos, categorías, fichas, catálogos y espacios de video conservan su estado anterior. La Home conserva sus espacios de video y producto.

## Prompts de generación (herramienta integrada)

- design: Wide editorial photograph of two packaging designers collaborating at a clean studio desk, drawing structural sketches with pencils and laptop, natural daylight, realistic hands, no readable text no logos. Landscape corporate website image. Illustrative fictional people.
- logistics: Wide realistic editorial photograph of a container ship beside cranes at a commercial seaport, daylight, understated navy and neutral colors, no company logos or readable text. Landscape corporate website international logistics illustration, no specific location.
- delivery: Wide realistic editorial photograph of a delivery worker beside a plain white delivery van outside a small cafe, carrying an unbranded shipping carton, daylight, no logos no readable text. Illustrative fictional last mile scene.
- food-beverage: Wide editorial realistic photograph of a cafe kitchen with staff preparing food and coffee, emphasis on people and environment rather than products, natural daylight, no logos no readable text. Corporate sector illustration.
- personal-care: Wide realistic editorial photograph of a clean cosmetics research laboratory with two professionals working, neutral daylight, no logos no readable text, emphasis on people and environment not product photography. Corporate sector illustration.
- electronics: Wide realistic editorial photograph of technicians in an electronics assembly workspace, circuit assembly benches, natural neutral lighting, no brand logos no readable text, people and environment, no packaging product photography.
- retail: Wide realistic editorial photograph of a retail order fulfillment workspace with worker reviewing orders at computer and shelving behind, no logos or readable text, corporate website, people and environment, no product closeups.
- premium-gifts: Wide realistic editorial photograph of a tasteful boutique gift wrapping workspace with florist arranging flowers and ribbons, warm natural daylight, no logos no readable text, focus on environment and craft not packaging product shots.
- local-storage: Wide realistic editorial photograph of an unbranded distribution warehouse with tall pallet racks and a worker scanning inventory, neutral natural daylight, no readable text no logos, focus on space and inventory workflow. Landscape corporate website illustration, fictional facility, no specific location.
