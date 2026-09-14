---
title: "Historias de Usuario"
proyecto: Anura
fuente: "Notion â€” Proyecto Identificación de Anuros Colombia"
tags: [anura, proyecto, requisitos]
---

# Historias de Usuario

El ecosistema de historias de usuario de **Anura** abarca desde la captura básica para usuarios comunes hasta el flujo avanzado de investigación, curaduría de datos y publicación científica.

**Arquitectura de Procesos y Flujo de Datos**

```
 [ Rol: Usuario Comàºn ]                       [ Rol: Herpetólogo / Investigador ]

 HU-01: Foto y Detección                     HU-05: Salida de Campo / Transecto
 de Riesgo (IA Básica)                       (Sesión + Metadatos + Clima)
           â”‚                                                â”‚
           â–¼                                                â–¼
 â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
 â”‚                       PROCESAMIENTO Y SEGMENTACIà“N                         â”‚
 â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                   â”‚
                                   â–¼
 â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
 â”‚                     HU-02: Ficha Técnica Específica                        â”‚
 â”‚           (Consulta de taxonomía, estado IUCN, ecología y riesgo)           â”‚
 â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                   â”‚
                                   â–¼
 â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
 â”‚                 HU-03: Explicabilidad y Segmentación Semántica             â”‚
 â”‚    (Análisis de caracteres por regiones anatómicas: tímpano, pliegues, etc.)â”‚
 â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                   â”‚
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚ ¿Resultado erróneo/dudoso?  â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                   â”‚ Sí
                                   â–¼
 â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
 â”‚                HU-03: Evaluacion del resultado y ajuste                    â”‚
 â”‚            (Refutación experta + Polígonos ajustados en campo)             â”‚
 â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                   â”‚
                                   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                   â–¼                        â–¼
 â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
 â”‚  Reentrenamiento del Modelo de Visión    â”‚  â”‚ HU-05: Exportación DwC   â”‚
 â”‚        (Dataset de alta calidad)         â”‚  â”‚    (GBIF / SiB Colombia) â”‚
 â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Resumen Funcional por Modulo**

| **HU** | **Módulo** | **Entradas Clave** | **Salidas / Resultados** |
| --- | --- | --- | --- |
| **HU-01** | Captura y Riesgo | Fotografía | Nivel de toxicidad/peligro y especie probable. |
| **HU-02** | Ficha Técnica | ID de Especie | Documento estructurado con biología, hábitat y conservación. |
| **HU-03** | Explicabilidad AI | Imagen + Segmentación | Máscara de regiones anatómicas y desglose de caracteres. |
| **HU-04** | Muestreo de Campo | GPS, Clima, Microhábitat | Sesión de transecto con registros georreferenciados. |
| **HU-05** | Publicación Científica | Registros de campo (HU-05) | Paquete `DwC-A` listo para repositorios (GBIF/SiB). |

---

## Historia de usuarios

| **Campo** | **Detalle** |
| --- | --- |
| **ID** | HU-01 |
| **Título** | Identificación de riesgo de ranas mediante fotografía |
| **Rol (Como)** | Usuario comàºn de Anura |
| **Acción (Quiero)** | Tomar la foto de una rana que veo |
| **Beneficio (Para)** | Saber inmediatamente si es peligrosa o no |
| **Prioridad** | media |

### Criterios de Aceptación (Gherkin)

- **Caso 1: Identificación exitosa de especie y nivel de peligro**
    - **Dado que** abro la cámara dentro de la aplicación Anura,
    - **Cuando** tomo la foto de una rana y presiono analizar,
    - **Entonces** la aplicación muestra el nombre de la especie y una alerta clara indicando si es peligrosa (venenosa/tóxica) o inofensiva.
- **Caso 2: Imagen borrosa o no identificable**
    - **Dado que** la foto tomada está fuera de foco o la rana no se distingue claramente,
    - **Cuando** el sistema procesa la imagen,
    - **Entonces** muestra un mensaje recomendando tomar una nueva foto con mejor iluminación o enfoque.
- **Caso 3: Sin conexión a Internet**
    - **Dado que** me encuentro en campo sin cobertura o datos móviles,
    - **Cuando** tomo la foto de la rana,
    - **Entonces** la app guarda la foto localmente y me permite procesarla tan pronto recupere la conexión (o usa el modelo local si está disponible offline).

---

| **Campo** | **Detalle** |
| --- | --- |
| **ID** | HU-02 |
| **Título** | Generación de ficha técnica especializada por registro de especie |
| **Rol (Como)** | Herpetólogo, veterinario, zootecnista o estudiante |
| **Acción (Quiero)** | Acceder a una ficha técnica detallada de las especies que registro |
| **Beneficio (Para)** | Consultar datos morfológicos, de hábitat, estado de conservación y manejo especializado |
| **Prioridad** | Alta |

### **Criterios de Aceptación (Gherkin)**

- **Caso 1: Consulta exitosa de ficha técnica completa**
    - **Dado que** realizo o selecciono el registro de una especie identificada,
    - **Cuando** accedo a la opción "Ver ficha técnica",
    - **Entonces** el sistema despliega la información taxonómica (familia, género, especie), estado de conservación (IUCN), rango altitudinal, microhábitat, y datos biológicos/veterinarios clave.
- **Caso 2: Filtrado y navegación por secciones técnicas**
    - **Dado que** estoy visualizando la ficha técnica de un anfibio,
    - **Cuando** navego entre las pestañas de contenido (Taxonomía, Diagnóstico Morfológico, Ecología, Manejo/Riesgo),
    - **Entonces** la aplicación muestra la información organizada sin saturación visual y permite exportar o guardar el resumen en formato legible (PDF/Offline).
- **Caso 3: Registro de especie con taxonomía incierta o no confirmada**
    - **Dado que** la especie registrada está catalogada como *sp.* o requiere validación de campo,
    - **Cuando** el sistema genera la ficha,
    - **Entonces** muestra la información a nivel de género/familia e indica visualmente que los caracteres diagnósticos exactos requieren verificación técnica adicional.

---

| **Campo** | **Detalle** |
| --- | --- |
| **ID** | HU-03 |
| **Título** | Explicabilidad del modelo de clasificación y retroalimentación experta |
| **Rol (Como)** | Herpetólogo |
| **Acción (Quiero)** | Ver los caracteres diagnósticos/evidencia que usó el sistema para clasificar un individuo y poder reevaluar o refutar el resultado |
| **Beneficio (Para)** | Validar la precisión taxonómica del modelo, corregir identificaciones erróneas y aportar al reentrenamiento del sistema |
| **Prioridad** | Alta |

### **Criterios de Aceptación (Gherkin)**

- **Caso 1: Generación de listado de evaluación con segmentación semántica**
    - **Dado que** la aplicación procesa la fotografía de un individuo,
    - **Cuando** consulto la sección "Ver justificación de identificación",
    - **Entonces** el sistema muestra la máscara de segmentación semántica delimitando las regiones anatómicas clave (ej. tímpano, disco digital, pliegue dorsolateral, patrón ventral/dorsal) junto con un listado detallado que relaciona cada región segmentada con los caracteres diagnósticos detectados y la conclusión taxonómica propuesta.
- **Caso 2: Evaluación del desglose y desacuerdo con regiones específicas**
    - **Dado que** estoy revisando el listado de evaluación y la máscara de segmentación semántica del individuo,
    - **Cuando** detecto una falla en la delimitación morfológica o en la conclusión de una estructura (ej. confusión entre tímpano y pliegue),
    - **Entonces** puedo seleccionar la región específica en conflicto, ingresar la especie correcta/carácter observado y enviar la refutación.
- **Caso 3: Registro y almacenamiento para reevaluación del modelo**
    - **Dado que** envío una corrección basada en la segmentación semántica,
    - **Cuando** se completa el envío,
    - **Entonces** el sistema actualiza el registro al estado "En revisión experta", guardando la imagen original, la máscara de segmentación generada y la corrección del usuario para la mejora continua del dataset de segmentación.

---

| **Campo** | **Detalle** |
| --- | --- |
| **ID** | HU-04 |
| **Título** | Agrupación de registros por salida de campo y captura de variables ambientales |
| **Rol (Como)** | Herpetólogo / Investigador de campo |
| **Acción (Quiero)** | Crear sesiones de muestreo/transectos y vincular automáticamente las variables fisicoquímicas y geográficas a cada registro |
| **Beneficio (Para)** | Mantener la trazabilidad de las jornadas de observación y contextualizar los hallazgos con datos ecológicos estandarizados sin depender de registro manual en libreta |
| **Prioridad** | Media |

### **Criterios de Aceptación (Gherkin)**

- **Caso 1: Creación de sesión de muestreo y captura automática de metadatos**
    - **Dado que** inicio una nueva "Salida de campo" en la aplicación,
    - **Cuando** tomo una fotografía de un individuo dentro de dicha sesión,
    - **Entonces** el sistema registra automáticamente las coordenadas GPS, altitud, fecha, hora exacta y consulta las variables meteorológicas actuales (temperatura, humedad relativa y precipitación aproximada).
- **Caso 2: Ingreso y edición manual de variables microambientales offline**
    - **Dado que** me encuentro en campo sin cobertura de red o requiero ingresar datos específicos de microhábitat,
    - **Cuando** abro el formulario de variables ambientales de la fotografía,
    - **Entonces** la aplicación me permite registrar manualmente datos precisos (ej. temperatura del sustrato, tipo de microhábitat: hojarasca, vegetación baja, cuerpo de agua) y guarda la información localmente.
- **Caso 3: Cierre y resumen estructurado del transecto/salida**
    - **Dado que** finalizo la jornada de muestreo y selecciono la opción "Cerrar salida de campo",
    - **Cuando** el sistema procesa la sesión,
    - **Entonces** genera un resumen consolidado con el total de individuos/especies registradas, la ruta o puntos geográficos cubiertos y la variación ambiental durante el evento.

---

| **Campo** | **Detalle** |
| --- | --- |
| **ID** | HU-05 |
| **Título** | Exportación de registros biológicos en estándar Darwin Core (DwC) |
| **Rol (Como)** | Herpetólogo / Investigador |
| **Acción (Quiero)** | Exportar mis registros de campo y fichas técnicas formateados segàºn el estándar Darwin Core |
| **Beneficio (Para)** | Publicar o integrar fácilmente mis hallazgos en repositorios científicos globales y nacionales como GBIF o SiB Colombia sin reprocesamiento manual de datos |
| **Prioridad** | Media |

**Criterios de Aceptación (Gherkin)**

- **Caso 1: Exportación exitosa de conjunto de datos en formato DwC-A (Darwin Core Archive)**
    - **Dado que** selecciono una o varias salidas de campo finalizadas en la aplicación,
    - **Cuando** elijo la opción "Exportar a Darwin Core" y confirmo la descarga,
    - **Entonces** el sistema genera un paquete comprimido (.zip) que incluye el archivo principal de observaciones (`occurrence.txt` o `.csv`) mapeado con los términos clave (ej. *eventDate*, *decimalLatitude*, *decimalLongitude*, *scientificName*, *basisOfRecord*), el archivo de metadatos (`eml.xml`) y la referencia a las fotografías/máscaras asociadas.
- **Caso 2: Validación automática de campos obligatorios antes de exportar**
    - **Dado que** intento exportar registros que carecen de metadatos geográficos o taxonómicos mínimos indispensables para GBIF/SiB Colombia,
    - **Cuando** el sistema procesa la solicitud de exportación,
    - **Entonces** muestra un reporte de validación alertando sobre las celdas o registros incompletos y me permite corregirlos o excluirlos antes de generar el archivo final.
- **Caso 3: Mapeo de taxonomía no confirmada o correcciones expertas**
    - **Dado que** exporto observaciones etiquetadas con incertidumbre o refutaciones en proceso (ej. *Pristimantis sp.*),
    - **Cuando** el sistema construye el archivo de ocurrencias,
    - **Entonces** mapea correctamente el rango taxonómico más específico confirmado en *scientificName* y añade los calificadores correspondientes en el término *identificationQualifier* (ej. "cf." o "aff.").



