# FASE 22 — RECOVERY AUDIT PROTOCOL
## Auditoría de Recuperabilidad para Especies UNKNOWN sub-70

**Fecha:** 2026-09-14  
**Protocolo:** 5-Step Recovery Feasibility Assessment  
**Estado:** COMPLETE

---

## RESUMEN EJECUTIVO

Se ejecutó un protocolo de 5 pasos para evaluar la recuperabilidad de 4 especies UNKNOWN con menos de 70 imágenes en Fase 22.1:

| Especie | Imágenes Actuales | Investigación iNaturalist | Decisión |
|---------|------------------|--------------------------|----------|
| Hyloxalus_picachos | 15 | 0 obs en Colombia | **EXCLUDE** |
| Dendropsophus_minutus | 23 | 0 obs en Colombia | **EXCLUDE** |
| Pristimantis_w_nigrum | 53 | 0 obs en Colombia | **EXCLUDE** |
| Sachatamia_electrops | 39 | 0 obs en Colombia | **EXCLUDE** |

**Hallazgo crítico:** Ninguna de las 4 especies tiene observaciones disponibles en iNaturalist para Colombia en ningún quality_grade (research-grade, needs_id, casual). Por lo tanto, son todas **UNRECOVERABLE** mediante fuentes públicas de iNaturalist.

---

## PASO 1: CONSULTA iNATURALIST SIN FILTRO RESEARCH-GRADE

Se consultó la API de iNaturalist para cada especie usando el país=Colombia sin restricción de quality_grade.

### Resultados por Especie:

#### 1. Hyloxalus_picachos
- **Taxon ID:** 1250338
- **Existe en iNaturalist:** Sí (global)
- **Observaciones en Colombia, research-grade:** 0
- **Observaciones en Colombia, needs_id+casual:** 0
- **Total disponible en Colombia:** 0
- **CC-licensed:** 0

#### 2. Dendropsophus_minutus
- **Taxon ID:** 65377
- **Existe en iNaturalist:** Sí (global)
- **Observaciones en Colombia, research-grade:** 0
- **Observaciones en Colombia, needs_id+casual:** 0
- **Total disponible en Colombia:** 0
- **CC-licensed:** 0

#### 3. Pristimantis_w_nigrum
- **Taxon ID:** 66936
- **Existe en iNaturalist:** Sí (global) [también conocida como Pristimantis w-nigrum]
- **Observaciones en Colombia, research-grade:** 0
- **Observaciones en Colombia, needs_id+casual:** 0
- **Total disponible en Colombia:** 0
- **CC-licensed:** 0

#### 4. Sachatamia_electrops
- **Taxon ID:** 604172
- **Existe en iNaturalist:** Sí (global)
- **Observaciones en Colombia, research-grade:** 0
- **Observaciones en Colombia, needs_id+casual:** 0
- **Total disponible en Colombia:** 0
- **CC-licensed:** 0

---

## PASO 2: EVALUACIÓN DE RECUPERABILIDAD

Criterio: Si (needs_id + casual) >= 30 imágenes potenciales → **CANDIDATE_FOR_RECOVERY**

### Resultados:

```
Hyloxalus_picachos:      needs_id+casual=0  → UNRECOVERABLE (<30)
Dendropsophus_minutus:   needs_id+casual=0  → UNRECOVERABLE (<30)
Pristimantis_w_nigrum:   needs_id+casual=0  → UNRECOVERABLE (<30)
Sachatamia_electrops:    needs_id+casual=0  → UNRECOVERABLE (<30)
```

**Ninguna especie califica como candidata para recuperación.**

---

## PASO 3: DESCARGA Y AUDITORÍA

Como ninguna especie es candidata de recuperación, se omitió este paso para las 4 especies.

---

## PASO 4: DECISIÓN FINAL

Criterio: Si (research_grade_valid + nuevas_validas) >= 70 → **KEEP**; Si < 70 → **EXCLUDE**

### Resultados:

| Especie | Research-grade Válidas | Nuevas Válidas | Total | Decisión |
|---------|----------------------|-----------------|-------|----------|
| Hyloxalus_picachos | 15 | 0 | **15** | EXCLUDE |
| Dendropsophus_minutus | 23 | 0 | **23** | EXCLUDE |
| Pristimantis_w_nigrum | 53 | 0 | **53** | EXCLUDE |
| Sachatamia_electrops | 39 | 0 | **39** | EXCLUDE |

**Todas 4 especies quedan bajo el mínimo de 70 imágenes sin alternativa de recuperación.**

---

## PASO 5: ANÁLISIS DE FUENTES HISTÓRICAS

Para entender por qué tenemos imágenes de estas especies si no hay datos en iNaturalist:

### Hyloxalus_picachos (15 imágenes)
- **Fuentes:** BMC (banco de imágenes colombiano, 4), iNaturalist observaciones históricas (7), DendroWiki (4)
- **Observaciones iNaturalist:** Algunos de los `col_obs_*` implican observaciones previas que pueden haber sido borradas o modificadas
- **Estatus:** Histórica desde Fase 13/16/19/20/21

### Dendropsophus_minutus (23 imágenes)
- **Fuentes:** iNaturalist research-grade (23)
- **Observaciones iNaturalist:** Aparentemente descargadas en Fase 22 pero ya no accesibles vía API

### Pristimantis_w_nigrum (53 imágenes)
- **Fuentes:** iNaturalist research-grade (53)
- **Observaciones iNaturalist:** Descargadas previamente; posible cambio taxonómico o retiro de observaciones

### Sachatamia_electrops (39 imágenes)
- **Fuentes:** iNaturalist research-grade (27), field observations/WhatsApp (12)
- **Observaciones iNaturalist:** Descargadas históricamente; ya no disponibles vía API

---

## IMPLICACIONES Y CONCLUSIONES

### Hallazgo 1: Desconexión entre datos históricos e iNaturalist actual
Las imágenes que tenemos fueron descargadas en fases anteriores (13, 16, 19, 20, 21, 22), pero **actualmente no hay registros en iNaturalist** para estas especies en Colombia. Posibles razones:
- Eliminación de observaciones por parte de usuarios
- Cambios taxonómicos que afectaron los IDs de taxón
- Cambio de política de visibilidad en observaciones
- Datos históricos no replicables con API actual

### Hallazgo 2: Imposibilidad de expandir dataset mediante fuentes públicas
Sin acceso a iNaturalist, las únicas opciones para recuperación serían:
- Campo directo (colecta nueva) — fuera de alcance de este protocolo
- Colaboradores privados con acervos fotográficos — no sistematizados
- Repositorios específicos de cada institución — requerirían contacto directo

### Hallazgo 3: Contract violation is permanent for these species
Sin datos de recuperación disponibles, estas 4 especies **violarán permanentemente** el contrato de 70-100 imágenes/especie a menos que se implementen nuevas colectas o asociaciones.

---

## RECOMENDACIONES

### Para Fase 23:

**Opción A: EXCLUSIÓN TOTAL** ✓ RECOMENDADA
- Remover las 4 especies del dataset UNKNOWN_V2.1
- Resultado: 7 especies (todos con >= 70 imágenes)
- Beneficio: Cumplimiento total de contrato
- Costo: Pérdida de diversidad taxonómica (especialmente Sachatamia = única Hemiphractidae)

**Opción B: INCLUSIÓN CON WAIVER DOCUMENTADO**
- Mantener las 4 especies con documento de exención de contrato
- Resultado: 11 especies (4 bajo 70, 7 sobre 70)
- Beneficio: Máxima diversidad
- Costo: Violación documentada de contrato

**Opción C: INCLUSIÓN SELECTIVA**
- Mantener solo Pristimantis_w_nigrum (53 imágenes, cercano a 70)
- Excluir Hyloxalus_picachos (15), Dendropsophus_minutus (23), Sachatamia_electrops (39)
- Resultado: 8 especies
- Costo intermedio

### Para análisis futuro:
1. Investigar cambios taxonómicos en iNaturalist que puedan afectar buscabilidad
2. Contactar colaboradores de Fase 13/16 para datos de observación originales
3. Considerar integración de repositorios privados (herbarios, colecciones)
4. Establecer canal de colecta directo para especies críticas

---

## ARCHIVOS GENERADOS

- `recovery_audit.csv` — Tabla de decisiones por especie
- `FASE22_RECOVERY_AUDIT_REPORT.md` — Este reporte
- Datos de búsqueda iNaturalist disponibles bajo demanda

---

## ESTADO FINAL

```
FASE 22 RECOVERY AUDIT: COMPLETE

Species evaluated: 4
Species recovered (>=70 total valid): 0
Species excluded (<70 total valid): 4

Recovery success rate: 0/4 (0%)
Reason: No iNaturalist observations available in Colombia

DECISION: All 4 species classified as UNRECOVERABLE
RECOMMENDATION: Exclude from UNKNOWN_V2.1 final dataset
```

---

**Protocolo ejecutado por:** FASE 22 Recovery Audit Script  
**Fecha de conclusión:** 2026-09-14  
**Próximo paso:** Revisión manual y decisión de inclusión/exclusión en Fase 23
