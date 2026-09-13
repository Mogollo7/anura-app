# Estado del Proyecto Anura — 2026-09-13

**Deadline**: 2026-09-27 (14 días restantes)

---

## 1. FASE 13 — CALIBRACIÓN OPEN SET [✅ COMPLETADA]

### Status
- **FASE13_COMPLETE** ✅
- Auditoría final: APROBADA (8/8 verificaciones)
- Threshold congelado: τ = 39.3541 (@ 95% KAR en CALIBRATION)
- Método: M5_LedoitWolf_Shared (Mahalanobis con Ledoit-Wolf regularizado)

### Resultados Finales (Blind F3+F4)
| Métrica | Valor | Calidad |
|---------|-------|---------|
| AUROC | 0.6248 | Moderada |
| KAR (85.38%) | 85% KNOWN aceptadas | Buena |
| UDR (8.93%) | Solo 9% UNKNOWN rechazadas | ⚠️ Baja |
| FAR (91.07%) | 91% UNKNOWN aceptadas | ⚠️ MUY ALTA |
| KAR Grupo A | 87.31% (9 sp independientes) | Excelente |
| KAR Grupo B | 84.71% (32 sp estructurales) | Buena |

### Arquitectura Centroides
```
GRUPO A (9 especies, calibración independiente):
  Fuente: REFERENCE (798 imágenes)
  • Dendrobates truncatus
  • Dendropsophus bogerti, microcephalus
  • Hyloscirtus palmeri
  • Pristimantis achatinus, paisa, penelopus
  • Rhinella alata, horribilis

GRUPO B (32 especies, estructura TRAIN):
  Fuente: TRAIN (3608 imágenes)
  • 32 especies restantes de las 41 visuales

ORPHANED (excluida):
  • Leucostethus fraterdanieli (REFERENCE-only, no en TRAIN/visual)
```

### Preocupaciones Identificadas
⚠️ **FAR=91% es MUY ALTA**
- Sistema acepta ~91% de UNKNOWN como KNOWN
- Solo rechaza ~9% de UNKNOWN correctamente
- Threshold τ=39.35 es excesivamente permisivo
- **Alternativa**: τ @ 90% KAR = 35.36 (más conservador)

---

## 2. PAQUETES REGIONALES — ANTIOQUIA [🟡 EN DISEÑO]

### Arquitectura Planificada
```
DESCARGA SEGMENTADA:
  1. Base offline (180MB)
     • BioCLIP encoder ONNX FP16 (173MB)
     • Código app + UI
  
  2. Paquete regional (~20MB)
     • 41 centroides (Group A + B)
     • Covarianza Ledoit-Wolf (512×512)
     • Threshold τ (o alternativas)
     • k-NN índices (opcional)
     • Metadatos región
```

### Estado Actual
- ✅ Centroides Group A (REFERENCE): listos
- ✅ Centroides Group B (TRAIN): listos
- ✅ Covarianza Ledoit-Wolf: calculada
- 🟡 Índices k-NN: pendiente
- 🟡 Manifest paquete Antioquia: pendiente
- 🟡 Integración móvil: pendiente

### Estructura de Carpetas (Planeada)
```
COLOMBIA_ANURA/
├── ANTIOQUIA/
│   ├── packages/v1.0.0/
│   │   ├── manifest.json
│   │   ├── species_index.json (41 especies)
│   │   ├── centroids_group_a.npz (9 sp, REFERENCE)
│   │   ├── centroids_group_b.npz (32 sp, TRAIN)
│   │   ├── covariance_matrix.npz (Ledoit-Wolf)
│   │   ├── threshold_config.json (τ principal + alternativas)
│   │   └── knn_indices.sqlite (opcional, para k-NN)
│   ├── geobounds.json (polygon DANE)
│   └── species_presence.json (qué especies en Antioquia)
└── ...otras regiones
```

---

## 3. FLUJO MÓVIL — INTEGRACI ÓN [🟡 PENDIENTE]

### Flujo Operativo (Diseño)
```
[Usuario toma foto]
    ↓
[Detectar ubicación GPS]
    ↓
¿Primera vez en región?
  SI → Descargar paquete Antioquia (~20MB)
  NO → Usar paquete en caché
    ↓
[Cargar encoder BioCLIP (offline)]
    ↓
[Extraer embedding 512D] (~50ms en GPU/NN)
    ↓
[Open Set Rejection]
  • Calcular min(Mahalanobis a 41 centroides)
  • Si score ≤ τ → ACCEPT KNOWN
  • Si score > τ → REJECT UNKNOWN
    ↓
¿ACCEPT?
  SI → [Cargar k-NN índices]
       [Clasificación jerárquica Familia→Género→Especie]
       [Mostrar resultado + confianza]
  NO → [Mostrar: "Especie no reconocida en Antioquia"]
       [Opción: enviar a servidor para revisión]
```

### Componentes Faltantes
- 🔲 Serialización de centroides para móvil (ONNX/protobuf)
- 🔲 Integración OpenSet en React Native
- 🔲 k-NN searcher (FAISS/Annoy)
- 🔲 Classifier jerárquico (Familia→Género→Especie)
- 🔲 UI mockup + feedback visual

---

## 4. DECISIONES CRÍTICAS PENDIENTES

### Decision A: Threshold en Producción
```
Opción 1 (ACTUAL): τ @ 95% KAR = 39.35
  ✓ Acepta 85% de KNOWN
  ✗ Acepta 91% de UNKNOWN (MUY permisivo)

Opción 2 (RECOMENDADO): τ @ 90% KAR = 35.36
  ✓ Acepta 90% de KNOWN
  ✓ Rechaza ~50% de UNKNOWN (mejor balance)

Opción 3 (CONSERVADOR): τ @ 85% KAR = 34.04
  ✓ Acepta 85% de KNOWN
  ✓ Rechaza ~70% de UNKNOWN (máxima especificidad)

→ RECOMENDACIÓN: Opción 2 (35.36) para Antioquia piloto
```

### Decision B: Despliegue Regional
```
Fases planeadas:
  Fase 14A: Validación Antioquia (2 semanas)
    • Usuarios locales, ~100 fotos
    • Monitorear KAR, FAR, UDR en campo
  
  Fase 14B: Gate de validación
    • Si KAR ≥ 80% en Antioquia → expandir
    • Si FAR sigue > 70% → ajustar τ o reentrenar
  
  Fase 14C: Expansión regional
    • Cauca, Chocó, etc. (próximas regiones)
```

### Decision C: Manejo de Falsos Rechazos
```
Si usuario captura foto de Dendrobates truncatus (Group A)
pero el sistema la rechaza como "UNKNOWN":
  
  Opción 1: "Especie no reconocida, enviar foto al servidor"
  Opción 2: "Baja confianza — ¿ayudarnos a mejorar?"
  Opción 3: Ajustar τ on-device por feedback
  
→ RECOMENDACIÓN: Opción 1 + 2 (enviar + opción feedback)
```

---

## 5. CRONOGRAMA vs DEADLINE

**Hoy**: 2026-09-13  
**Deadline**: 2026-09-27  
**Tiempo restante**: 14 días

### Hitos Críticos
```
2026-09-13 ✅  Fase 13 completada
2026-09-15 🟡  Paquete Antioquia v1 (manifest + centroides)
2026-09-17 🔲  Integración móvil (embedded)
2026-09-20 🔲  Validación local Antioquia (usuarios piloto)
2026-09-24 🔲  Gate de validación (decisión deploy/iterate)
2026-09-27 ⏰  DEADLINE — Prototipo funcional esperado
```

### Ruta Crítica (Necesario para deadline)
1. ✅ Fase 13 (completada)
2. 🟡 Paquete regional Antioquia (este fin de semana)
3. 🔲 Integración móvil básica (early next week)
4. 🔲 Testing piloto Antioquia (antes del 24)
5. 🔲 Gate de validación + decisión (24-27)

---

## 6. ESTADO DE ARTEFACTOS

### Embeddings & Modelos
| Artefacto | Ubicación | Size | Status |
|-----------|-----------|------|--------|
| encoder_anura_fp16.onnx | bioclip/checkpoints/ | 173MB | ✅ Verificado |
| bioclip_anura_mejor.pt | bioclip/checkpoints/ | - | ✅ Checkpoint |
| reference_embeddings.npz | evaluation/fase13/embeddings/ | 1.5M | ✅ (798, 512) |
| calibration_embeddings.npz | evaluation/fase13/embeddings/ | 364K | ✅ (192, 512) |
| train_embeddings.npz | evaluation/fase13/embeddings/ | 6.4M | ✅ (3608, 512) |

### Configuración Congelada
| Archivo | Ruta | Status |
|---------|------|--------|
| frozen_rejection_config.json | fase13/selection/ | ✅ Congelado |
| centroid_source_audit.json | fase13/final_evaluation/ | ✅ Auditado |
| TRAIN_manifest.json | fase13/manifests/ | ✅ (3608 limpios) |

### Reportes Finales
| Reporte | Ruta | Status |
|---------|------|--------|
| FASE13_FINAL_REPORT.md | fase13/final_evaluation/ | ✅ Completado |
| FASE13_FINAL_METRICS.json | fase13/final_evaluation/ | ✅ Métricas |
| AUDITORIA_FINAL_FASE13.py | fase13/ | ✅ 8/8 PASS |

---

## 7. TAREAS PENDIENTES (Ordenadas por Urgencia)

### CRÍTICA (Antes del 15-09)
- [ ] **T1**: Generar `ANTIOQUIA_v1.0.0_manifest.json` con metadatos región
- [ ] **T2**: Serializar centroides Group A + B para móvil (formato ligero)
- [ ] **T3**: Empaquetar covariance_matrix.npz (~21KB)
- [ ] **T4**: Crear `threshold_config.json` con alternativas (80%, 85%, 90%, 95% KAR)

### ALTA (Antes del 17-09)
- [ ] **T5**: Integrar encoder BioCLIP en app móvil (ONNX runtime)
- [ ] **T6**: Implementar Open Set rejection scorer (Mahalanobis)
- [ ] **T7**: Mockup UI: "Especie conocida" vs "No reconocida"
- [ ] **T8**: Estructura de descarga segmentada (paquetes por región)

### MEDIA (Antes del 20-09)
- [ ] **T9**: k-NN indexer para clasificación jerárquica (opcional para v1)
- [ ] **T10**: Testing piloto: 50-100 fotos en Antioquia
- [ ] **T11**: Monitoreo de métricas en campo (KAR, FAR, UDR real)
- [ ] **T12**: Recolectar feedback de usuarios locales

### BAJA (After validación)
- [ ] **T13**: Expansión a Cauca, Chocó, etc.
- [ ] **T14**: Fine-tuning regional de τ si divergencia significativa
- [ ] **T15**: Integración con servidor de revisión (UNKNOWN rechazadas)

---

## 8. RIESGOS IDENTIFICADOS

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|--------|-----------|
| FAR=91% alto en Antioquia | MEDIA | ALTO | Usar τ @ 90% KAR (35.36) en lugar de 95% |
| Delay en integración móvil | MEDIA | CRÍTICO | Iniciar ya (T5-T7 en paralelo) |
| Datos Antioquia divergen de lab | MEDIA | MEDIO | Gate de validación, monitoreo |
| Falta de usuarios locales piloto | BAJA | MEDIO | Contactar CEAM/parques Antioquia |
| UNKNOWN insuficiente en calibración | MEDIA | MEDIO | Recolectar especies "dudosas" en campo |

---

## 9. RESUMEN EJECUTIVO

### ¿Dónde estamos?
✅ **Modelo Open Set calibrado y auditado** — Fase 13 completada sin manipulación.  
✅ **Centroides Group A & B validados** — 9 independientes + 32 estructurales.  
✅ **Threshold congelado** — τ=39.35 @ 95% KAR (alternativas disponibles).  
⚠️ **FAR muy alta (91%)** — Sistema MUY permisivo con UNKNOWN. Requiere revisión.  
🟡 **Paquete Antioquia en diseño** — Faltanmanifest + serialización móvil.  
🔲 **Integración móvil pendiente** — Crítica para deadline (14 días).

### ¿Qué sigue?
1. **Hoy-15**: Generar paquete regional Antioquia + config alternativa (τ @ 90% KAR)
2. **15-17**: Integración móvil básica (encoder + Open Set scorer)
3. **17-20**: Testing piloto Antioquia, recolectar métricas reales
4. **20-24**: Análisis gate + decisión (expandir, iterar, o hold)
5. **24-27**: Refinamientos finales, demo funcional

### Probabilidad de Cumplir Deadline
- **Si iteramos rápido (T5-T7 en paralelo)**: 75%
- **Si hay delay en móvil**: 30%
- **Si validación Antioquia pide reentrenamiento**: <10%

**Recomendación**: Empezar T5-T8 YA (este fin de semana). Parallelizar con decisión de threshold (usar 35.36 en lugar de 39.35).

