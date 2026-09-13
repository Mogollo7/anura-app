---
title: "Dataset JerÃ¡rquico de Colombia â€” Paquetes Departamentales"
proyecto: Anura
tipo: metodologÃ­a
estado: piloto-antioquia-ejecutado
tags: [anura, dataset, taxonomia, departamentos, antioquia, taxon-id, merlin, sqlite-vec]
---

# Dataset JerÃ¡rquico de Colombia â€” Paquetes Departamentales

[[Anura â€” Ãndice General]] Â· [[Base Vectorial (SQLite-vec)]] Â· [[Estrategia de ConstrucciÃ³n del Dataset]] Â· [[Proceso de Crecimiento del CatÃ¡logo Post-Despliegue]]

> [!abstract] El cambio de fondo
> Anura deja de tratarse como una colecciÃ³n de carpetas de imÃ¡genes y pasa a ser un **dataset jerÃ¡rquico de biodiversidad**: `Colombia â†’ Departamentos â†’ Especies â†’ Zonas biogeogrÃ¡ficas opcionales`. La diferencia no es cosmÃ©tica: determina quÃ© preguntas puede responder el sistema.

## 1. Las preguntas que el dataset debe poder responder

| Nivel | Pregunta |
| --- | --- |
| Nacional | Â¿QuÃ© especies de anuros hay en Colombia? |
| Departamental | Â¿QuÃ© especies hay en Antioquia? |
| GeogrÃ¡fico | Â¿DÃ³nde dentro de Antioquia se registrÃ³ cada una? |
| Endemismo | Â¿CuÃ¡les estÃ¡n restringidas a Ã¡reas particulares? |
| Dataset | Â¿CuÃ¡les tienen fotos suficientes para BioCLIP? |
| Calidad | Â¿CuÃ¡les necesitan mÃ¡s fotografÃ­as o revisiÃ³n manual? |
| Usuario | Â¿CuÃ¡les son relevantes para dÃ³nde estÃ¡ el usuario? |

Una estructura plana de carpetas por nombre cientÃ­fico no responde ninguna.

## 2. Principio de identidad taxonÃ³mica

> [!important] El nombre cientÃ­fico NUNCA es la identidad permanente del dataset
> Cada especie recibe un identificador interno estable â€” `COL_ANURA_0001` â€” que sobrevive a cambios de nombre, de gÃ©nero, a que un sinÃ³nimo pase a ser el nombre aceptado y a cualquier revisiÃ³n taxonÃ³mica. El nombre cientÃ­fico, la autorÃ­a, los sinÃ³nimos y el estado taxonÃ³mico viven como **metadatos** en la guÃ­a central, no como identidad.

**Por quÃ© importa aquÃ­ y no en abstracto.** Las carpetas histÃ³ricas de este proyecto tienen nombres cientÃ­ficos mal escritos:

| Carpeta histÃ³rica | Nombre correcto |
| --- | --- |
| `Boana cinereansis` | *Boana cinerascens* |
| `Boana xeraphyla` | *Boana xerophylla* |
| `Dendrosophus reticulatus` | *Dendropsophus reticulatus* |
| `Pristimantis acanthinus` | *Pristimantis achatinus* |
| `Rhinella SF margatiferas` | *Rhinella margaritifera* |

Con identidad basada en el nombre del directorio, cada correcciÃ³n ortogrÃ¡fica rompe la trazabilidad de todo lo que apunte a esa especie. Con `taxon_id`, corregir el nombre es editar un campo.

**Estabilidad garantizada por cÃ³digo:** `construir_guia_taxonomica.py` carga los ids ya asignados en cada ejecuciÃ³n y solo entrega ids nuevos a especies nuevas. Un id nunca se reasigna ni se reordena.

### GuÃ­a taxonÃ³mica central

`COLOMBIA_ANURA/taxonomy/taxonomy_guide.csv` â€” la referencia que consume todo lo demÃ¡s:

```
taxon_id, order, family, genus, species, scientific_name, authorship,
accepted_name, synonyms, taxonomic_status, common_name_es,
inaturalist_taxon_id, source, last_verified, directory_legacy
```

Estado actual: **43 especies, 8 familias, 15 gÃ©neros**. Los campos `authorship`, `synonyms` y `taxonomic_status` quedan en `UNVERIFIED` â€” los llenarÃ¡ la validaciÃ³n contra Batrachia y GBIF.

## 3. Presencia no es lo mismo que datos

> [!warning] Una especie sin fotos NO se omite del paquete
> Si hay evidencia de ocurrencia en el departamento, la especie entra al paquete aunque no tenga una sola fotografÃ­a utilizable, marcada con su estado real. Confundir *"no tenemos fotos"* con *"la especie no estÃ¡ aquÃ­"* corrompe el paquete como documento biolÃ³gico â€” y es exactamente el error que cometerÃ­a un pipeline que solo mira carpetas de imÃ¡genes.

Dos ejes independientes, que se reportan por separado:

**Evidencia de ocurrencia** (Â¿estÃ¡ la especie en el departamento?)

| Estado | Criterio |
| --- | --- |
| `OCCURRENCE_CONFIRMED` | â‰¥ 5 observaciones independientes |
| `OCCURRENCE_PROBABLE` | 2â€“4 observaciones |
| `OCCURRENCE_MARGINAL` | 1 observaciÃ³n |

**Suficiencia de datos** (Â¿podemos entrenar/reconocerla?)

| Estado | Criterio |
| --- | --- |
| `DATA_SUFFICIENT` | â‰¥ 45 individuos independientes con foto curada |
| `DATA_LIMITED` | 10â€“44 individuos |
| `DATA_CRITICAL` | < 10 individuos |
| `MANUAL_REVIEW` | hay un motivo registrado que exige decisiÃ³n humana |

> [!tip] Nota informativa â‰  motivo de revisiÃ³n
> Varias especies fueron submuestreadas a propÃ³sito (el entrenamiento topa los individuos por especie). Marcar eso como problema convertirÃ­a una decisiÃ³n de diseÃ±o en una falsa alarma que entierra los casos que sÃ­ importan. El submuestreo se registra como **nota**; solo escala a `MANUAL_REVIEW` si ademÃ¡s dejÃ³ a la especie sin datos suficientes. En el piloto esto redujo los `MANUAL_REVIEW` de 6 a 1 â€” el Ãºnico real.

## 4. AsignaciÃ³n geogrÃ¡fica: point-in-polygon, no texto libre

La asignaciÃ³n de cada registro a un departamento se hace por **geometrÃ­a exacta** contra los lÃ­mites oficiales con cÃ³digo DANE, no parseando el campo `place_guess` de iNaturalist ni con bounding boxes.

**Los tres mÃ©todos, medidos sobre los mismos datos:**

| MÃ©todo | Especies detectadas en Antioquia |
| --- | --- |
| Bounding box (lat/lon rectangular) | 25 |
| Texto libre `place_guess` | 28 |
| **Point-in-polygon (DANE)** | **29** |

El mÃ©todo riguroso encontrÃ³ **mÃ¡s** especies, no menos â€” el bbox recorta esquinas reales del departamento y el texto libre falla cuando el observador no escribiÃ³ el departamento.

**ValidaciÃ³n del GeoJSON antes de usarlo:** 8/9 puntos de referencia conocidos asignados correctamente (MedellÃ­n, BogotÃ¡, Cali, QuibdÃ³, Barranquilla, Bucaramanga, un punto real del dataset, y un punto oceÃ¡nico correctamente rechazado). El Ãºnico fallo â€”Leticiaâ€” cae a **0,66 km** del polÃ­gono de Amazonas: generalizaciÃ³n de frontera internacional, no error sistemÃ¡tico. El polÃ­gono de Antioquia mide **63.494 kmÂ² contra 63.612 reales: 99,8 % de precisiÃ³n.**

Por esa generalizaciÃ³n se acepta una **tolerancia de frontera de 2 km**, marcada en cada registro como `assignment_method: frontera` para que sea auditable.

Registros con `positional_accuracy` peor que 10 km se descartan: no localizan nada Ãºtil a escala departamental.

## 5. Estructura del paquete

```
COLOMBIA_ANURA/
â”œâ”€â”€ taxonomy/
â”‚   â”œâ”€â”€ taxonomy_guide.csv          â† guÃ­a central, ids estables
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
    â”œâ”€â”€ zones/                        â† vacÃ­o: ver Â§7
    â””â”€â”€ antioquia_v1.sqlite           â† paquete desplegable (sqlite-vec)
```

Los directorios usan `taxon_id`. El nombre legible se obtiene de la guÃ­a.

## 6. Balanceo del set de referencia (hallazgo del piloto)

> [!danger] En k-NN, el nÃºmero de vectores por especie es un sesgo directo
> Una especie con 3.000 fotos de referencia gana vecinos por **densidad**, no por parecido, y aplasta a una con 30. Medido en Antioquia: sin tope por especie el Top-1 cayÃ³ a **59,1 %**; el set balanceado por el tope de individuos del manifiesto daba **66,2 %** con un tercio de los vectores. MÃ¡s datos de referencia empeoraron el resultado.

El muestreo aplica **round-robin por individuo**: se toma la primera foto de cada individuo antes que la segunda de ninguno. Bajo un tope fijo, 300 individuos distintos describen mucho mejor a una especie que 300 fotos de 20 individuos.

**Control de fuga verificado:** de las 7.029 fotos que quedan fuera del manifiesto de entrenamiento y entran como referencia, **0** comparten `obs_id` con las particiones de validaciÃ³n o test. El `GroupSplit` moviÃ³ individuos completos, asÃ­ que el recorte por tope nunca partiÃ³ un individuo entre referencia y evaluaciÃ³n.

## 7. Zonas biogeogrÃ¡ficas finales (v1, 2026-09-13)

> [!note] Este resultado reemplaza el diagnÃ³stico anterior
> Con las 29 especies del scrape inicial los datos no justificaban zonas (ninguna celda reunÃ­a especies restringidas coincidentes). Ese veredicto dependÃ­a de un catÃ¡logo incompleto: con el catÃ¡logo ampliado desde iNaturalist + GBIF (**291 taxones, 15.081 registros vÃ¡lidos**) la zonificaciÃ³n por recambio de composiciÃ³n (Î²sim) sÃ­ encuentra estructura, y estÃ¡ ordenada por elevaciÃ³n.

Tras fusionar las zonas de â‰¤ 2 celdas y reubicar un fragmento de tierras bajas (83 m) que habÃ­a quedado dentro de la zona montana, quedan **4 zonas finales**:

| Zona | Banda (mediana DEM de sus celdas) | Celdas | Registros | Especies con registro | Origen |
| --- | --- | --- | --- | --- | --- |
| ZONE_005 | Tierras bajas (157 m) | 87 | 8.600 | 175 | ZONE_005 |
| ZONE_006 | Montano (1.950 m) | 18 | 4.868 | 141 | ZONE_006 |
| ZONE_002 | Premontano (1.005 m) | 10 | 819 | 93 | ZONE_002 + ZONE_003 + ZONE_004 |
| ZONE_001 | Montano (1.910 m) | 7 | 794 | 86 | ZONE_001 |

Una especie pertenece a **todas** las zonas donde tiene registros: las zonas particionan el espacio, no el catÃ¡logo. Prior por zona, validaciones y paquetes offline: [[Base BiogeogrÃ¡fica de Antioquia v1]].

## 8. LÃ­mites vigentes

> [!warning]
> - **Autoridad taxonÃ³mica:** los nombres aceptados siguen el backbone de GBIF; falta validarlos contra **Batrachia**. *Pristimantis campesino* y *P. cryptopictus* (registros de iNaturalist) no existen en ese backbone y quedan como taxones sin resolver.
> - **CatÃ¡logo â‰  clasificador:** 291 taxones en el catÃ¡logo, 30 habilitados visualmente. El resto aporta prior y contexto, no clases.
> - **Muestra GBIF truncada:** la descarga por celdas conservÃ³ como mÃ¡ximo 300 registros por celda de consulta (6 de 90 celdas quedaron cortadas). Las especies que solo aparecÃ­an en la faceta se completaron con descargas acotadas por especie.
> - ExpansiÃ³n a otros departamentos: fuera del prototipo del 27 de septiembre, por decisiÃ³n del autor (2026-09-12).

> [!note] Licencia de las referencias visuales â€” decisiÃ³n del autor (2026-09-13)
> 1.450 de 4.034 vectores de referencia (36 %) no tienen `license_code`/`attribution` resuelto en `reference_images`. **No es bloqueante**: el embedding es una transformaciÃ³n numÃ©rica derivada de la foto, no la obra protegida, y el uso del proyecto es acadÃ©mico no comercial. El matiz que sigue vigente: si en el futuro la app muestra las **fotos de referencia** como evidencia visual ("N ejemplares similares"), ahÃ­ sÃ­ se despliega la obra original y la atribuciÃ³n vuelve a aplicar â€” es un requisito de esa funciÃ³n de UI si se construye, no del paquete vectorial actual.

## 9. ReutilizaciÃ³n para los demÃ¡s departamentos

Nada en el cÃ³digo es especÃ­fico de Antioquia. El departamento entra por parÃ¡metro:

```bash
python pipeline_dataset/construir_paquete_departamental.py --departamento CHOCO
python pipeline_dataset/construir_paquete_vectorial.py --departamento CHOCO
python pipeline_dataset/analizar_zonas.py --departamento CHOCO
```

La distribuciÃ³n nacional ya calculada muestra quÃ© departamentos tienen masa crÃ­tica con los datos actuales: Cundinamarca (1.234 registros), Santander (1.117), Risaralda (736), Valle del Cauca (634), Magdalena (522), BoyacÃ¡ (414), ChocÃ³ (386).

El paquete nacional se generarÃ¡ **combinando paquetes departamentales validados**, no reconstruyendo el dataset entero.

## Referencias de fuentes fijadas

- **Batrachia** â€” catÃ¡logo maestro de anuros de Colombia. `batrachia.com/orden-anura/`
- **GBIF API** â€” validaciÃ³n taxonÃ³mica y ocurrencias. `api.gbif.org/v1/species/`, `/occurrence/search`
- **SiB Colombia** â€” validaciÃ³n institucional local. `ipt.sibcolombia.net` o GBIF con `publishingCountry=CO`
- **iNaturalist API v1** â€” ocurrencias `quality_grade=research`, fotos, licencias. `api.inaturalist.org/v1/observations`
- **LÃ­mites departamentales** â€” GeoJSON con cÃ³digos DANE (33 features), validado contra 9 puntos de referencia.



