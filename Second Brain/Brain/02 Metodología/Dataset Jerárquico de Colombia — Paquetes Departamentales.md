---
title: "Dataset Jerárquico de Colombia â€” Paquetes Departamentales"
proyecto: Anura
tipo: metodología
estado: piloto-antioquia-ejecutado
tags: [anura, dataset, taxonomia, departamentos, antioquia, taxon-id, merlin, sqlite-vec]
---

# Dataset Jerárquico de Colombia â€” Paquetes Departamentales

[[Anura â€” àndice General]] · [[Base Vectorial (SQLite-vec)]] · [[Estrategia de Construcción del Dataset]] · [[Proceso de Crecimiento del Catálogo Post-Despliegue]]

> [!abstract] El cambio de fondo
> Anura deja de tratarse como una colección de carpetas de imágenes y pasa a ser un **dataset jerárquico de biodiversidad**: `Colombia â†’ Departamentos â†’ Especies â†’ Zonas biogeográficas opcionales`. La diferencia no es cosmética: determina qué preguntas puede responder el sistema.

## 1. Las preguntas que el dataset debe poder responder

| Nivel | Pregunta |
| --- | --- |
| Nacional | ¿Qué especies de anuros hay en Colombia? |
| Departamental | ¿Qué especies hay en Antioquia? |
| Geográfico | ¿Dónde dentro de Antioquia se registró cada una? |
| Endemismo | ¿Cuáles están restringidas a áreas particulares? |
| Dataset | ¿Cuáles tienen fotos suficientes para BioCLIP? |
| Calidad | ¿Cuáles necesitan más fotografías o revisión manual? |
| Usuario | ¿Cuáles son relevantes para dónde está el usuario? |

Una estructura plana de carpetas por nombre científico no responde ninguna.

## 2. Principio de identidad taxonómica

> [!important] El nombre científico NUNCA es la identidad permanente del dataset
> Cada especie recibe un identificador interno estable â€” `COL_ANURA_0001` â€” que sobrevive a cambios de nombre, de género, a que un sinónimo pase a ser el nombre aceptado y a cualquier revisión taxonómica. El nombre científico, la autoría, los sinónimos y el estado taxonómico viven como **metadatos** en la guía central, no como identidad.

**Por qué importa aquí y no en abstracto.** Las carpetas históricas de este proyecto tienen nombres científicos mal escritos:

| Carpeta histórica | Nombre correcto |
| --- | --- |
| `Boana cinereansis` | *Boana cinerascens* |
| `Boana xeraphyla` | *Boana xerophylla* |
| `Dendrosophus reticulatus` | *Dendropsophus reticulatus* |
| `Pristimantis acanthinus` | *Pristimantis achatinus* |
| `Rhinella SF margatiferas` | *Rhinella margaritifera* |

Con identidad basada en el nombre del directorio, cada corrección ortográfica rompe la trazabilidad de todo lo que apunte a esa especie. Con `taxon_id`, corregir el nombre es editar un campo.

**Estabilidad garantizada por código:** `construir_guia_taxonomica.py` carga los ids ya asignados en cada ejecución y solo entrega ids nuevos a especies nuevas. Un id nunca se reasigna ni se reordena.

### Guía taxonómica central

`COLOMBIA_ANURA/taxonomy/taxonomy_guide.csv` â€” la referencia que consume todo lo demás:

```
taxon_id, order, family, genus, species, scientific_name, authorship,
accepted_name, synonyms, taxonomic_status, common_name_es,
inaturalist_taxon_id, source, last_verified, directory_legacy
```

Estado actual: **43 especies, 8 familias, 15 géneros**. Los campos `authorship`, `synonyms` y `taxonomic_status` quedan en `UNVERIFIED` â€” los llenará la validación contra Batrachia y GBIF.

## 3. Presencia no es lo mismo que datos

> [!warning] Una especie sin fotos NO se omite del paquete
> Si hay evidencia de ocurrencia en el departamento, la especie entra al paquete aunque no tenga una sola fotografía utilizable, marcada con su estado real. Confundir *"no tenemos fotos"* con *"la especie no está aquí"* corrompe el paquete como documento biológico â€” y es exactamente el error que cometería un pipeline que solo mira carpetas de imágenes.

Dos ejes independientes, que se reportan por separado:

**Evidencia de ocurrencia** (¿está la especie en el departamento?)

| Estado | Criterio |
| --- | --- |
| `OCCURRENCE_CONFIRMED` | â‰¥ 5 observaciones independientes |
| `OCCURRENCE_PROBABLE` | 2â€“4 observaciones |
| `OCCURRENCE_MARGINAL` | 1 observación |

**Suficiencia de datos** (¿podemos entrenar/reconocerla?)

| Estado | Criterio |
| --- | --- |
| `DATA_SUFFICIENT` | â‰¥ 45 individuos independientes con foto curada |
| `DATA_LIMITED` | 10â€“44 individuos |
| `DATA_CRITICAL` | < 10 individuos |
| `MANUAL_REVIEW` | hay un motivo registrado que exige decisión humana |

> [!tip] Nota informativa â‰  motivo de revisión
> Varias especies fueron submuestreadas a propósito (el entrenamiento topa los individuos por especie). Marcar eso como problema convertiría una decisión de diseño en una falsa alarma que entierra los casos que sí importan. El submuestreo se registra como **nota**; solo escala a `MANUAL_REVIEW` si además dejó a la especie sin datos suficientes. En el piloto esto redujo los `MANUAL_REVIEW` de 6 a 1 â€” el àºnico real.

## 4. Asignación geográfica: point-in-polygon, no texto libre

La asignación de cada registro a un departamento se hace por **geometría exacta** contra los límites oficiales con código DANE, no parseando el campo `place_guess` de iNaturalist ni con bounding boxes.

**Los tres métodos, medidos sobre los mismos datos:**

| Método | Especies detectadas en Antioquia |
| --- | --- |
| Bounding box (lat/lon rectangular) | 25 |
| Texto libre `place_guess` | 28 |
| **Point-in-polygon (DANE)** | **29** |

El método riguroso encontró **más** especies, no menos â€” el bbox recorta esquinas reales del departamento y el texto libre falla cuando el observador no escribió el departamento.

**Validación del GeoJSON antes de usarlo:** 8/9 puntos de referencia conocidos asignados correctamente (Medellín, Bogotá, Cali, Quibdó, Barranquilla, Bucaramanga, un punto real del dataset, y un punto oceánico correctamente rechazado). El àºnico fallo â€”Leticiaâ€” cae a **0,66 km** del polígono de Amazonas: generalización de frontera internacional, no error sistemático. El polígono de Antioquia mide **63.494 km² contra 63.612 reales: 99,8 % de precisión.**

Por esa generalización se acepta una **tolerancia de frontera de 2 km**, marcada en cada registro como `assignment_method: frontera` para que sea auditable.

Registros con `positional_accuracy` peor que 10 km se descartan: no localizan nada àºtil a escala departamental.

## 5. Estructura del paquete

```
COLOMBIA_ANURA/
â”œâ”€â”€ taxonomy/
â”‚   â”œâ”€â”€ taxonomy_guide.csv          â† guía central, ids estables
â”‚   â””â”€â”€ taxonomy_guide.json
â”‚
â””â”€â”€ ANTIOQUIA/
    â”œâ”€â”€ SPECIES/
    â”‚   â”œâ”€â”€ COL_ANURA_0003/
    â”‚   â”‚   â”œâ”€â”€ species.json         â† estados, conteos, evidencia
    â”‚   â”‚   â””â”€â”€ occurrences.json     â† registros en ESTE departamento
    â”‚   â””â”€â”€ ...
    â”œâ”€â”€ metadata/package.json
    â”œâ”€â”€ occurrences/occurrences_antioquia.csv
    â”œâ”€â”€ reports/
    â”‚   â”œâ”€â”€ data_sufficiency.csv
    â”‚   â”œâ”€â”€ zones_analysis.json
    â”‚   â””â”€â”€ vector_package.json
    â”œâ”€â”€ zones/                        â† vacío: ver §7
    â””â”€â”€ antioquia_v1.sqlite           â† paquete desplegable (sqlite-vec)
```

Los directorios usan `taxon_id`. El nombre legible se obtiene de la guía.

## 6. Balanceo del set de referencia (hallazgo del piloto)

> [!danger] En k-NN, el nàºmero de vectores por especie es un sesgo directo
> Una especie con 3.000 fotos de referencia gana vecinos por **densidad**, no por parecido, y aplasta a una con 30. Medido en Antioquia: sin tope por especie el Top-1 cayó a **59,1 %**; el set balanceado por el tope de individuos del manifiesto daba **66,2 %** con un tercio de los vectores. Más datos de referencia empeoraron el resultado.

El muestreo aplica **round-robin por individuo**: se toma la primera foto de cada individuo antes que la segunda de ninguno. Bajo un tope fijo, 300 individuos distintos describen mucho mejor a una especie que 300 fotos de 20 individuos.

**Control de fuga verificado:** de las 7.029 fotos que quedan fuera del manifiesto de entrenamiento y entran como referencia, **0** comparten `obs_id` con las particiones de validación o test. El `GroupSplit` movió individuos completos, así que el recorte por tope nunca partió un individuo entre referencia y evaluación.

## 7. Zonas biogeográficas finales (v1, 2026-09-13)

> [!note] Este resultado reemplaza el diagnóstico anterior
> Con las 29 especies del scrape inicial los datos no justificaban zonas (ninguna celda reunía especies restringidas coincidentes). Ese veredicto dependía de un catálogo incompleto: con el catálogo ampliado desde iNaturalist + GBIF (**291 taxones, 15.081 registros válidos**) la zonificación por recambio de composición (Î²sim) sí encuentra estructura, y está ordenada por elevación.

Tras fusionar las zonas de â‰¤ 2 celdas y reubicar un fragmento de tierras bajas (83 m) que había quedado dentro de la zona montana, quedan **4 zonas finales**:

| Zona | Banda (mediana DEM de sus celdas) | Celdas | Registros | Especies con registro | Origen |
| --- | --- | --- | --- | --- | --- |
| ZONE_005 | Tierras bajas (157 m) | 87 | 8.600 | 175 | ZONE_005 |
| ZONE_006 | Montano (1.950 m) | 18 | 4.868 | 141 | ZONE_006 |
| ZONE_002 | Premontano (1.005 m) | 10 | 819 | 93 | ZONE_002 + ZONE_003 + ZONE_004 |
| ZONE_001 | Montano (1.910 m) | 7 | 794 | 86 | ZONE_001 |

Una especie pertenece a **todas** las zonas donde tiene registros: las zonas particionan el espacio, no el catálogo. Prior por zona, validaciones y paquetes offline: [[Base Biogeográfica de Antioquia v1]].

## 8. Límites vigentes

> [!warning]
> - **Autoridad taxonómica:** los nombres aceptados siguen el backbone de GBIF; falta validarlos contra **Batrachia**. *Pristimantis campesino* y *P. cryptopictus* (registros de iNaturalist) no existen en ese backbone y quedan como taxones sin resolver.
> - **Catálogo â‰  clasificador:** 291 taxones en el catálogo, 30 habilitados visualmente. El resto aporta prior y contexto, no clases.
> - **Muestra GBIF truncada:** la descarga por celdas conservó como máximo 300 registros por celda de consulta (6 de 90 celdas quedaron cortadas). Las especies que solo aparecían en la faceta se completaron con descargas acotadas por especie.
> - Expansión a otros departamentos: fuera del prototipo del 27 de septiembre, por decisión del autor (2026-09-12).

> [!note] Licencia de las referencias visuales â€” decisión del autor (2026-09-13)
> 1.450 de 4.034 vectores de referencia (36 %) no tienen `license_code`/`attribution` resuelto en `reference_images`. **No es bloqueante**: el embedding es una transformación numérica derivada de la foto, no la obra protegida, y el uso del proyecto es académico no comercial. El matiz que sigue vigente: si en el futuro la app muestra las **fotos de referencia** como evidencia visual ("N ejemplares similares"), ahí sí se despliega la obra original y la atribución vuelve a aplicar â€” es un requisito de esa función de UI si se construye, no del paquete vectorial actual.

## 9. Reutilización para los demás departamentos

Nada en el código es específico de Antioquia. El departamento entra por parámetro:

```bash
python pipeline_dataset/construir_paquete_departamental.py --departamento CHOCO
python pipeline_dataset/construir_paquete_vectorial.py --departamento CHOCO
python pipeline_dataset/analizar_zonas.py --departamento CHOCO
```

La distribución nacional ya calculada muestra qué departamentos tienen masa crítica con los datos actuales: Cundinamarca (1.234 registros), Santander (1.117), Risaralda (736), Valle del Cauca (634), Magdalena (522), Boyacá (414), Chocó (386).

El paquete nacional se generará **combinando paquetes departamentales validados**, no reconstruyendo el dataset entero.

## Referencias de fuentes fijadas

- **Batrachia** â€” catálogo maestro de anuros de Colombia. `batrachia.com/orden-anura/`
- **GBIF API** â€” validación taxonómica y ocurrencias. `api.gbif.org/v1/species/`, `/occurrence/search`
- **SiB Colombia** â€” validación institucional local. `ipt.sibcolombia.net` o GBIF con `publishingCountry=CO`
- **iNaturalist API v1** â€” ocurrencias `quality_grade=research`, fotos, licencias. `api.inaturalist.org/v1/observations`
- **Límites departamentales** â€” GeoJSON con códigos DANE (33 features), validado contra 9 puntos de referencia.



