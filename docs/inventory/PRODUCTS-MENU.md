# Clasificación vigente del catálogo

Por aclaración del usuario: todas las 1,199 fichas se publican y se asignan a las 14 ramas amarillas. Las 54 categorías del Excel permanecen visibles bajo seis grupos; las ramas restantes muestran próximos productos cuando no tienen fichas.

Las asignaciones por similitud son agrupaciones comerciales. No convierten botellas en vasos, PP en PET ni PLA en almidón. Los materiales, tipos, fotos y especificaciones originales se conservan. La categoría es navegación; los atributos son evidencia técnica.

| Nivel | Categoría | Fichas incluyendo descendientes | Disponible (amarillo/ancestro) |
| --- | --- | ---: | --- |
| 1 | Empaques de papel | 195 | Sí |
| 1 | Empaques de plástico | 885 | Sí |
| 1 | Vajilla de origen vegetal | 119 | Sí |
| 1 | Empaques de metal | 0 | Próximamente |
| 1 | Empaques de vidrio | 0 | Próximamente |
| 1 | Accesorios de empaque | 0 | Próximamente |
| 2 | Empaques de papel para alimentos | 195 | Sí |
| 2 | Empaques de papel para otros usos | 0 | Próximamente |
| 2 | Empaques de plástico para alimentos | 885 | Sí |
| 2 | Empaques de plástico para otros usos | 0 | Próximamente |
| 2 | Vajilla de pulpa de caña | 0 | Sí |
| 2 | Vajilla de almidón de maíz | 79 | Sí |
| 2 | Vajilla de papel kraft | 40 | Sí |
| 3 | Cajas de papel para alimentos | 0 | Próximamente |
| 3 | Tazones y cubetas de papel | 0 | Próximamente |
| 3 | Vasos de papel | 195 | Sí |
| 3 | Tubos y botes de papel para alimentos | 0 | Próximamente |
| 3 | Bandejas alimentarias de pulpa moldeada | 0 | Próximamente |
| 3 | Bolsas de papel para alimentos | 0 | Próximamente |
| 3 | Cajas de cartón corrugado | 0 | Próximamente |
| 3 | Cajas impresas y plegadizas | 0 | Próximamente |
| 3 | Bolsas de papel | 0 | Próximamente |
| 3 | Tubos y botes de papel | 0 | Próximamente |
| 3 | Insertos de pulpa moldeada | 0 | Próximamente |
| 3 | Productos auxiliares de papel | 0 | Próximamente |
| 3 | Envases para ensaladas | 5 | Sí |
| 3 | Empaques para repostería | 77 | Sí |
| 3 | Cajas bento | 98 | Sí |
| 3 | Envases para frutas | 3 | Sí |
| 3 | Vasos PET | 617 | Sí |
| 3 | Vasos para frutas | 0 | Sí |
| 3 | Envases para fruta cortada | 2 | Sí |
| 3 | Golden Container | 0 | Sí |
| 3 | Cajas para huevos | 0 | Sí |
| 3 | Envases para carne | 83 | Sí |
| 3 | Otros empaques de plástico para alimentos | 0 | Próximamente |
| 3 | Empaques flexibles | 0 | Próximamente |
| 3 | Empaques de plástico rígido | 0 | Próximamente |
| 2 | Caja de hojalata | 0 | Próximamente |
| 2 | Lata de hojalata | 0 | Próximamente |
| 2 | Caja de aluminio | 0 | Próximamente |
| 2 | Lata de aluminio | 0 | Próximamente |
| 2 | Papel de aluminio | 0 | Próximamente |
| 2 | Cubeta metálica | 0 | Próximamente |
| 2 | Botella de vidrio | 0 | Próximamente |
| 2 | Frasco de vidrio | 0 | Próximamente |
| 2 | Cinta de empaque | 0 | Próximamente |
| 2 | Fleje | 0 | Próximamente |
| 2 | Hebilla para fleje | 0 | Próximamente |
| 2 | Película estirable | 0 | Próximamente |
| 2 | Desecante | 0 | Próximamente |
| 2 | Bolsa anticorrosiva | 0 | Próximamente |
| 2 | Sello de seguridad | 0 | Próximamente |
| 2 | Listón | 0 | Próximamente |

Golden Container conserva su ID de fuente golen-container y el slug corregido golden-container. Los candidatos de investigación todavía no son fichas verificadas.

products-menu-classification.json contiene la asignación, evidencia, razón y categoría anterior para auditar movimientos. products-menu-review.json reúne las asignaciones por similitud. products-menu-scope.json define las ramas que reciben productos.

Regenerar: classify_products_menu.py y apply_products_menu.py; después validate:data, check, test y build. Para reextracción ejecutar primero prepare_catalog.py. Los scripts no modifican el Excel original.
