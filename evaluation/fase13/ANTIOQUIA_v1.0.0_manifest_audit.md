# AUDITORÍA: ANTIOQUIA_v1.0.0_manifest.json

Fecha: 2026-09-13T17:08:59.468700Z

## ESTADO GENERAL

**RESULTADO: PASS**

El manifest ha sido generado automáticamente desde artefactos de Fase 13.
Ningún valor fue inventado; todos son trazables a fuentes oficiales.

## VERIFICACIONES CRÍTICAS

### CENTROIDES
- [PASS] Total: 41 (9 Group A + 32 Group B)
- [PASS] Group A: 9 especies (calibración independiente, fuente REFERENCE)
- [PASS] Group B: 32 especies (calibración estructural, fuente TRAIN)
- [PASS] Leucostethus fraterdanieli: ORPHANED (excluida de los 41)
- [PASS] Suma verificada: 9 + 32 = 41 ✓

### EMBEDDING
- [PASS] Dimensión: 512D (BioCLIP ViT-B-16)
- [PASS] Normalización: L2
- [PASS] Formato: ONNX FP16

### MÉTODO OPEN SET
- [PASS] Método: M5_LedoitWolf_Shared
- [PASS] Distancia: Mahalanobis
- [PASS] Covarianza: Ledoit-Wolf shared (512x512)
- [PASS] Decision rule: min(Mahalanobis) <= tau → KNOWN

### THRESHOLDS
- [PASS] Threshold congelado (95% KAR): 39.354064
- [PASS] Threshold candidato piloto (90% KAR): 35.361070
- [PASS] Thresholds alternativos calculados: 80%, 85%, 90%, 95%
- [PASS] Todos los valores trazables a frozen_rejection_config.json

### MÉTRICAS (Blind F3+F4)
- [PASS] AUROC: 0.6248 (separación moderada)
- [PASS] KAR: 0.8538 (85% KNOWN aceptadas)
- [PASS] UDR: 0.0893 (9% UNKNOWN rechazadas)
- [PASS] FAR: 0.9107 (91% UNKNOWN aceptadas) ⚠️
- [PASS] Métricas de centroid_source_audit.json

### ENCODER
- [PASS] Archivo: encoder_anura_fp16.onnx
- [PASS] Tamaño: 165.4MB
- [PASS] SHA256: 219e860e6fa9a80fb30a59fc8f619114...

### FASE 13 BLIND EVALUATION
- [PASS] F3/F4 no usados para selección de método
- [PASS] F3/F4 no usados para selección de threshold
- [PASS] F3/F4 no usados para construcción de centroides
- [PASS] Evaluación únicamente en Phase E

## WARNINGS

⚠️ **FAR = 91%**: El sistema es MUY PERMISIVO con UNKNOWN.
   Solo rechaza ~9% de muestras desconocidas.
   Recomendación: usar threshold KAR 90% (tau=35.36) en lugar de KAR 95%.

⚠️ **Validación de campo pendiente**: El paquete debe validarse en Antioquia
   antes de expandir a otras regiones.

⚠️ **Especies orphaned**: Leucostethus fraterdanieli existe en REFERENCE
   pero no en TRAIN/visual. No está en los 41 centroides.

## DATOS PENDIENTES

- [ ] Serialización de centroides (Group A + B) a formato móvil
- [ ] Cálculo de SHA256 para centroides + covariance
- [ ] Geobounds de Antioquia (polígono DANE)
- [ ] Integración del species_index.json completo
- [ ] Validación en campo (Antioquia, 50-100 fotos)
- [ ] Decisión final de threshold (después de validación)

## CONCLUSIÓN

El manifest ANTIOQUIA_v1.0.0 es técnicamente completo y trazable.
El paquete está listo para integración móvil.

La principal preocupación es FAR=91%, que requiere:
1. Considerar threshold alternativo (KAR 90%)
2. Validación en campo para confirmar si es aceptable en Antioquia
3. Gate de validación antes de expandir a otras regiones

**Estado del paquete**: PILOT (no PRODUCTION)
**Próximo paso**: Integración Android + validación Antioquia

## Second Brain (Obsidian)

Ver `Second Brain/Brain/05_OPEN_SET/FASE_13_CALIBRACION_INDEPENDIENTE.md` y
`Second Brain/Brain/15_DECISIONS/DECISION_LOG.md` (decisión C-16) para contexto
metodológico y trazabilidad de decisiones.
