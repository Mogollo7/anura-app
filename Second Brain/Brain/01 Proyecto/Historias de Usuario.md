---
title: "Historias de Usuario"
proyecto: Anura
fuente: "Notion â€” Proyecto IdentificaciÃ³n de Anuros Colombia"
tags: [anura, proyecto, requisitos]
---

# Historias de Usuario

El ecosistema de historias de usuario de **Anura** abarca desde la captura bÃ¡sica para usuarios comunes hasta el flujo avanzado de investigaciÃ³n, curadurÃ­a de datos y publicaciÃ³n cientÃ­fica.

**Arquitectura de Procesos y Flujo de Datos**

```
 [ Rol: Usuario ComÃºn ]                       [ Rol: HerpetÃ³logo / Investigador ]

 HU-01: Foto y DetecciÃ³n                     HU-05: Salida de Campo / Transecto
 de Riesgo (IA BÃ¡sica)                       (SesiÃ³n + Metadatos + Clima)
           â”‚                                                â”‚
           â–¼                                                â–¼
 â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
 â”‚                       PROCESAMIENTO Y SEGMENTACIÃ“N                         â”‚
 â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                   â”‚
                                   â–¼
 â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
 â”‚                     HU-02: Ficha TÃ©cnica EspecÃ­fica                        â”‚
 â”‚           (Consulta de taxonomÃ­a, estado IUCN, ecologÃ­a y riesgo)           â”‚
 â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                   â”‚
                                   â–¼
 â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
 â”‚                 HU-03: Explicabilidad y SegmentaciÃ³n SemÃ¡ntica             â”‚
 â”‚    (AnÃ¡lisis de caracteres por regiones anatÃ³micas: tÃ­mpano, pliegues, etc.)â”‚
 â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                   â”‚
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚ Â¿Resultado errÃ³neo/dudoso?  â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                   â”‚ SÃ­
                                   â–¼
 â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
 â”‚                HU-03: Evaluacion del resultado y ajuste                    â”‚
 â”‚            (RefutaciÃ³n experta + PolÃ­gonos ajustados en campo)             â”‚
 â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                   â”‚
                                   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                   â–¼                        â–¼
 â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
 â”‚  Reentrenamiento del Modelo de VisiÃ³n    â”‚  â”‚ HU-05: ExportaciÃ³n DwC   â”‚
 â”‚        (Dataset de alta calidad)         â”‚  â”‚    (GBIF / SiB Colombia) â”‚
 â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Resumen Funcional por Modulo**

| **HU** | **MÃ³dulo** | **Entradas Clave** | **Salidas / Resultados** |
| --- | --- | --- | --- |
| **HU-01** | Captura y Riesgo | FotografÃ­a | Nivel de toxicidad/peligro y especie probable. |
| **HU-02** | Ficha TÃ©cnica | ID de Especie | Documento estructurado con biologÃ­a, hÃ¡bitat y conservaciÃ³n. |
| **HU-03** | Explicabilidad AI | Imagen + SegmentaciÃ³n | MÃ¡scara de regiones anatÃ³micas y desglose de caracteres. |
| **HU-04** | Muestreo de Campo | GPS, Clima, MicrohÃ¡bitat | SesiÃ³n de transecto con registros georreferenciados. |
| **HU-05** | PublicaciÃ³n CientÃ­fica | Registros de campo (HU-05) | Paquete `DwC-A` listo para repositorios (GBIF/SiB). |

---

## Historia de usuarios

| **Campo** | **Detalle** |
| --- | --- |
| **ID** | HU-01 |
| **TÃ­tulo** | IdentificaciÃ³n de riesgo de ranas mediante fotografÃ­a |
| **Rol (Como)** | Usuario comÃºn de Anura |
| **AcciÃ³n (Quiero)** | Tomar la foto de una rana que veo |
| **Beneficio (Para)** | Saber inmediatamente si es peligrosa o no |
| **Prioridad** | media |

### Criterios de AceptaciÃ³n (Gherkin)

- **Caso 1: IdentificaciÃ³n exitosa de especie y nivel de peligro**
    - **Dado que** abro la cÃ¡mara dentro de la aplicaciÃ³n Anura,
    - **Cuando** tomo la foto de una rana y presiono analizar,
    - **Entonces** la aplicaciÃ³n muestra el nombre de la especie y una alerta clara indicando si es peligrosa (venenosa/tÃ³xica) o inofensiva.
- **Caso 2: Imagen borrosa o no identificable**
    - **Dado que** la foto tomada estÃ¡ fuera de foco o la rana no se distingue claramente,
    - **Cuando** el sistema procesa la imagen,
    - **Entonces** muestra un mensaje recomendando tomar una nueva foto con mejor iluminaciÃ³n o enfoque.
- **Caso 3: Sin conexiÃ³n a Internet**
    - **Dado que** me encuentro en campo sin cobertura o datos mÃ³viles,
    - **Cuando** tomo la foto de la rana,
    - **Entonces** la app guarda la foto localmente y me permite procesarla tan pronto recupere la conexiÃ³n (o usa el modelo local si estÃ¡ disponible offline).

---

| **Campo** | **Detalle** |
| --- | --- |
| **ID** | HU-02 |
| **TÃ­tulo** | GeneraciÃ³n de ficha tÃ©cnica especializada por registro de especie |
| **Rol (Como)** | HerpetÃ³logo, veterinario, zootecnista o estudiante |
| **AcciÃ³n (Quiero)** | Acceder a una ficha tÃ©cnica detallada de las especies que registro |
| **Beneficio (Para)** | Consultar datos morfolÃ³gicos, de hÃ¡bitat, estado de conservaciÃ³n y manejo especializado |
| **Prioridad** | Alta |

### **Criterios de AceptaciÃ³n (Gherkin)**

- **Caso 1: Consulta exitosa de ficha tÃ©cnica completa**
    - **Dado que** realizo o selecciono el registro de una especie identificada,
    - **Cuando** accedo a la opciÃ³n "Ver ficha tÃ©cnica",
    - **Entonces** el sistema despliega la informaciÃ³n taxonÃ³mica (familia, gÃ©nero, especie), estado de conservaciÃ³n (IUCN), rango altitudinal, microhÃ¡bitat, y datos biolÃ³gicos/veterinarios clave.
- **Caso 2: Filtrado y navegaciÃ³n por secciones tÃ©cnicas**
    - **Dado que** estoy visualizando la ficha tÃ©cnica de un anfibio,
    - **Cuando** navego entre las pestaÃ±as de contenido (TaxonomÃ­a, DiagnÃ³stico MorfolÃ³gico, EcologÃ­a, Manejo/Riesgo),
    - **Entonces** la aplicaciÃ³n muestra la informaciÃ³n organizada sin saturaciÃ³n visual y permite exportar o guardar el resumen en formato legible (PDF/Offline).
- **Caso 3: Registro de especie con taxonomÃ­a incierta o no confirmada**
    - **Dado que** la especie registrada estÃ¡ catalogada como *sp.* o requiere validaciÃ³n de campo,
    - **Cuando** el sistema genera la ficha,
    - **Entonces** muestra la informaciÃ³n a nivel de gÃ©nero/familia e indica visualmente que los caracteres diagnÃ³sticos exactos requieren verificaciÃ³n tÃ©cnica adicional.

---

| **Campo** | **Detalle** |
| --- | --- |
| **ID** | HU-03 |
| **TÃ­tulo** | Explicabilidad del modelo de clasificaciÃ³n y retroalimentaciÃ³n experta |
| **Rol (Como)** | HerpetÃ³logo |
| **AcciÃ³n (Quiero)** | Ver los caracteres diagnÃ³sticos/evidencia que usÃ³ el sistema para clasificar un individuo y poder reevaluar o refutar el resultado |
| **Beneficio (Para)** | Validar la precisiÃ³n taxonÃ³mica del modelo, corregir identificaciones errÃ³neas y aportar al reentrenamiento del sistema |
| **Prioridad** | Alta |

### **Criterios de AceptaciÃ³n (Gherkin)**

- **Caso 1: GeneraciÃ³n de listado de evaluaciÃ³n con segmentaciÃ³n semÃ¡ntica**
    - **Dado que** la aplicaciÃ³n procesa la fotografÃ­a de un individuo,
    - **Cuando** consulto la secciÃ³n "Ver justificaciÃ³n de identificaciÃ³n",
    - **Entonces** el sistema muestra la mÃ¡scara de segmentaciÃ³n semÃ¡ntica delimitando las regiones anatÃ³micas clave (ej. tÃ­mpano, disco digital, pliegue dorsolateral, patrÃ³n ventral/dorsal) junto con un listado detallado que relaciona cada regiÃ³n segmentada con los caracteres diagnÃ³sticos detectados y la conclusiÃ³n taxonÃ³mica propuesta.
- **Caso 2: EvaluaciÃ³n del desglose y desacuerdo con regiones especÃ­ficas**
    - **Dado que** estoy revisando el listado de evaluaciÃ³n y la mÃ¡scara de segmentaciÃ³n semÃ¡ntica del individuo,
    - **Cuando** detecto una falla en la delimitaciÃ³n morfolÃ³gica o en la conclusiÃ³n de una estructura (ej. confusiÃ³n entre tÃ­mpano y pliegue),
    - **Entonces** puedo seleccionar la regiÃ³n especÃ­fica en conflicto, ingresar la especie correcta/carÃ¡cter observado y enviar la refutaciÃ³n.
- **Caso 3: Registro y almacenamiento para reevaluaciÃ³n del modelo**
    - **Dado que** envÃ­o una correcciÃ³n basada en la segmentaciÃ³n semÃ¡ntica,
    - **Cuando** se completa el envÃ­o,
    - **Entonces** el sistema actualiza el registro al estado "En revisiÃ³n experta", guardando la imagen original, la mÃ¡scara de segmentaciÃ³n generada y la correcciÃ³n del usuario para la mejora continua del dataset de segmentaciÃ³n.

---

| **Campo** | **Detalle** |
| --- | --- |
| **ID** | HU-04 |
| **TÃ­tulo** | AgrupaciÃ³n de registros por salida de campo y captura de variables ambientales |
| **Rol (Como)** | HerpetÃ³logo / Investigador de campo |
| **AcciÃ³n (Quiero)** | Crear sesiones de muestreo/transectos y vincular automÃ¡ticamente las variables fisicoquÃ­micas y geogrÃ¡ficas a cada registro |
| **Beneficio (Para)** | Mantener la trazabilidad de las jornadas de observaciÃ³n y contextualizar los hallazgos con datos ecolÃ³gicos estandarizados sin depender de registro manual en libreta |
| **Prioridad** | Media |

### **Criterios de AceptaciÃ³n (Gherkin)**

- **Caso 1: CreaciÃ³n de sesiÃ³n de muestreo y captura automÃ¡tica de metadatos**
    - **Dado que** inicio una nueva "Salida de campo" en la aplicaciÃ³n,
    - **Cuando** tomo una fotografÃ­a de un individuo dentro de dicha sesiÃ³n,
    - **Entonces** el sistema registra automÃ¡ticamente las coordenadas GPS, altitud, fecha, hora exacta y consulta las variables meteorolÃ³gicas actuales (temperatura, humedad relativa y precipitaciÃ³n aproximada).
- **Caso 2: Ingreso y ediciÃ³n manual de variables microambientales offline**
    - **Dado que** me encuentro en campo sin cobertura de red o requiero ingresar datos especÃ­ficos de microhÃ¡bitat,
    - **Cuando** abro el formulario de variables ambientales de la fotografÃ­a,
    - **Entonces** la aplicaciÃ³n me permite registrar manualmente datos precisos (ej. temperatura del sustrato, tipo de microhÃ¡bitat: hojarasca, vegetaciÃ³n baja, cuerpo de agua) y guarda la informaciÃ³n localmente.
- **Caso 3: Cierre y resumen estructurado del transecto/salida**
    - **Dado que** finalizo la jornada de muestreo y selecciono la opciÃ³n "Cerrar salida de campo",
    - **Cuando** el sistema procesa la sesiÃ³n,
    - **Entonces** genera un resumen consolidado con el total de individuos/especies registradas, la ruta o puntos geogrÃ¡ficos cubiertos y la variaciÃ³n ambiental durante el evento.

---

| **Campo** | **Detalle** |
| --- | --- |
| **ID** | HU-05 |
| **TÃ­tulo** | ExportaciÃ³n de registros biolÃ³gicos en estÃ¡ndar Darwin Core (DwC) |
| **Rol (Como)** | HerpetÃ³logo / Investigador |
| **AcciÃ³n (Quiero)** | Exportar mis registros de campo y fichas tÃ©cnicas formateados segÃºn el estÃ¡ndar Darwin Core |
| **Beneficio (Para)** | Publicar o integrar fÃ¡cilmente mis hallazgos en repositorios cientÃ­ficos globales y nacionales como GBIF o SiB Colombia sin reprocesamiento manual de datos |
| **Prioridad** | Media |

**Criterios de AceptaciÃ³n (Gherkin)**

- **Caso 1: ExportaciÃ³n exitosa de conjunto de datos en formato DwC-A (Darwin Core Archive)**
    - **Dado que** selecciono una o varias salidas de campo finalizadas en la aplicaciÃ³n,
    - **Cuando** elijo la opciÃ³n "Exportar a Darwin Core" y confirmo la descarga,
    - **Entonces** el sistema genera un paquete comprimido (.zip) que incluye el archivo principal de observaciones (`occurrence.txt` o `.csv`) mapeado con los tÃ©rminos clave (ej. *eventDate*, *decimalLatitude*, *decimalLongitude*, *scientificName*, *basisOfRecord*), el archivo de metadatos (`eml.xml`) y la referencia a las fotografÃ­as/mÃ¡scaras asociadas.
- **Caso 2: ValidaciÃ³n automÃ¡tica de campos obligatorios antes de exportar**
    - **Dado que** intento exportar registros que carecen de metadatos geogrÃ¡ficos o taxonÃ³micos mÃ­nimos indispensables para GBIF/SiB Colombia,
    - **Cuando** el sistema procesa la solicitud de exportaciÃ³n,
    - **Entonces** muestra un reporte de validaciÃ³n alertando sobre las celdas o registros incompletos y me permite corregirlos o excluirlos antes de generar el archivo final.
- **Caso 3: Mapeo de taxonomÃ­a no confirmada o correcciones expertas**
    - **Dado que** exporto observaciones etiquetadas con incertidumbre o refutaciones en proceso (ej. *Pristimantis sp.*),
    - **Cuando** el sistema construye el archivo de ocurrencias,
    - **Entonces** mapea correctamente el rango taxonÃ³mico mÃ¡s especÃ­fico confirmado en *scientificName* y aÃ±ade los calificadores correspondientes en el tÃ©rmino *identificationQualifier* (ej. "cf." o "aff.").



