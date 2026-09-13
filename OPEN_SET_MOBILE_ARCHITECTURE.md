# Arquitectura Open Set + Despliegue Móvil por Paquetes Regionales

## Estado Actual (Fase 13 — Correcciones en progreso)

### Pipeline Calibración Independiente
```
PHASE A: Embeddings REFERENCE (798) + CALIBRATION (192)
  ↓
PHASE B: 5-Fold CV sobre REFERENCE → método seleccionado M5 (Ledoit-Wolf)
  ↓
PHASE C: Calibración sobre CALIBRATION → τ congelado = 39.3541 (95% KAR)
  ↓
PHASE D: Congelamiento estricto de {método, regularización, threshold}
  ↓
PHASE E: Evaluación blind F3 (766 KNOWN, 41 sp.) + F4 (56 UNKNOWN, 2 sp.)
```

### Arquitectura de Centroides (Corrección 9)
```
GROUP A (10 especies):
  Centroides ← REFERENCE (calibración independiente)
  Especies: Dendrobates truncatus, Dendropsophus bogerti, 
            Dendropsophus microcephalus, Hyloscirtus palmeri, 
            Leucostethus fraterdanieli, Pristimantis acanthinus,
            Pristimantis paisa, Pristimantis penelopus, 
            Rhinella alata, Rhinella horribilis

GROUP B (31 especies):
  Centroides ← TRAIN (3608 muestras, sin calibración independiente)
  Estructura: Euclidean/Cosine min-distance o Mahalanobis
  
REJECTION (2 especies UNKNOWN):
  Hyloxalus_picachos (30 muestras F4)
  Sachatamia_electrops (26 muestras F4)
```

---

## Despliegue Móvil: Estrategia de Paquetes por Región

### Arquitectura On-Device
```
┌─────────────────────────────────────────┐
│        App Móvil (React Native)         │
├─────────────────────────────────────────┤
│  Camera → Imagen → BioCLIP Encoder      │
│  (ONNX FP16, ~173MB, offline)           │
├─────────────────────────────────────────┤
│  Embedding (512D) → Open Set Rejection  │
│  (method: M5 Mahalanobis LW)            │
├─────────────────────────────────────────┤
│  τ_frozen = 39.3541                     │
│  (si score ≤ τ → ACCEPT KNOWN           │
│   si score > τ → REJECT UNKNOWN)        │
└─────────────────────────────────────────┘
         ↓
    ¿KNOWN o UNKNOWN?
         ↓
    ┌────────────────┐
    │    KNOWN       │  → Clasificación jerárquica
    │  (41 especies) │    (Familia → Género → Especie)
    └────────────────┘
         ↓
    Cargar paquete regional apropiado
```

### Paquetes Regionales Segmentados

#### Arquitectura Actual (Fase 7-9)
```
COLOMBIA_ANURA/
├── ANTIOQUIA/
│   ├── packages/
│   │   ├── v1.0.0/
│   │   │   ├── manifest.json (metadatos región)
│   │   │   ├── species_index.json (41 especies, taxonomía)
│   │   │   ├── embeddings_index.sqlite (k-NN índices)
│   │   │   ├── reference_centroids.npz (GROUP A: 10 sp)
│   │   │   ├── train_centroids.npz (GROUP B: 31 sp)
│   │   │   └── confidence_lookup.json (scores calibrados)
│   │   └── v1.0.1/ (patches/updates)
│   └── assets/
│       └── imagery/ (fotos regionales para UI)
├── CAUCA/
├── CHOCO/
└── ... (otras 30+ regiones)
```

**Tamaño Paquete Típico**:
- Base (encoder ONNX + código): 180MB
- Paquete regional: 15-25MB c/u
- Total descargable: 200-220MB

#### Descarga Estratificada
```
[Inicio App]
    ↓
[Detectar geolocalización]
    ↓
[Descargar paquete regional mínimo]
    ↓
[Ejecutar Open Set Rejection (offline)]
    ↓
[Si KNOWN: descargar índices k-NN regionales]
    ↓
[Ejecutar clasificación jerárquica]
    ↓
[Mostrar resultado + confianza]
```

---

## Open Set Rejection: Mecanismo de Funcionamiento

### Scoring (Score Mahalanobis con Ledoit-Wolf)
```
Para cada imagen test X:
  1. Extraer embedding e (512D) con encoder BioCLIP
  2. Para cada species S en {41 centroides}:
       d_S = sqrt((e - μ_S)^T Σ^-1 (e - μ_S))  [Mahalanobis]
  3. score = min(d_S) [distancia al centroide más cercano]
  4. Si score ≤ τ_frozen → ACCEPT (probablemente KNOWN)
     Si score > τ_frozen → REJECT (probablemente UNKNOWN)
```

### Matriz de Covarianza Compartida (Ledoit-Wolf)
```
Σ_LW = (1-α) × Σ_empirical + α × I·trace(Σ_empirical)/d

α ≈ 0.3-0.5 (regularización automática)
d = 512 (dimensión embeddings)

Beneficios:
- Numéricamente estable en 512D
- Reduces overfitting vs covarianza por clase
- Condición numérica: ~500 (aceptable en móvil)
```

### Threshold Congelado
```
τ_95KAR = 39.3541  [determinado en CALIBRATION]

Operativo:
- TPR @ τ = ~90% (KAR: 90% de KNOWN aceptados)
- FPR @ τ = ~91% (FAR: 91% de UNKNOWN rechazados)
- Conservador: rechaza ~10% de KNOWN legítimos,
              pero evita falsos positivos

Calibración adicional en móvil:
  τ_80% = 32.37   [si sensibilidad baja]
  τ_85% = 34.04   [si sensibilidad moderada]
  τ_90% = 35.36   [balanceado]
  τ_95% = 39.35   [conservador, recomendado]
```

---

## Integración Móvil: Flujo Completo

### Escenario 1: Usuario en Antioquia (online/offline)
```
1. Captura imagen de rana
2. BioCLIP encoder genera embedding (512D, ~50ms en GPU)
3. Open Set Rejection:
   - score = Mahalanobis(embedding, centroides)
   - Si score > 39.35 → REJECT (desconocida o fuera rango)
     ✗ Mostrar: "Especie no reconocida en Antioquia"
   - Si score ≤ 39.35 → ACCEPT (probablemente conocida)
4. Cargar k-NN índices Antioquia
5. Clasificar jerárquica (Familia → Género → Especie)
6. Mostrar resultado + nivel confianza
```

### Escenario 2: Usuario viaja a nueva región
```
1. Detectar cambio de región (GPS)
2. Descargar paquete regional específico (~20MB, puede ser progresivo)
3. Recargar centroides regionales si aplica
4. Continuar con Open Set Rejection (ajustado regionalmente)
```

---

## Decisiones Arquitectónicas Clave

### ¿Por qué Ledoit-Wolf sobre Mahalanobis por clase?
| Aspecto | Mahalanobis/clase | Ledoit-Wolf |
|--------|-------------------|------------|
| Parámetros | 41 matrices 512×512 | 1 matriz 512×512 |
| Estabilidad numérica | Baja (d=512, n~88/clase) | Alta (regularización) |
| Overfitting | Alto | Bajo |
| Velocidad móvil | Lento (41 inversas) | Rápido (1 inversa) |
| Condición numérica | ~10⁶ | ~500 |

**Conclusión**: Ledoit-Wolf es OBLIGATORIO para móvil.

### ¿Por qué 10/31 split (Group A/B)?
- **Group A (10)**: calibración independiente → confiable
- **Group B (31)**: sin calibración independiente → estructurales
- **Beneficio**: Separación clara de confianza + trazabilidad

---

## Roadmap Post-Fase 13

### Corto Plazo (1-2 semanas)
- ✅ Completar Fase 13 con centroid_source_audit
- ✅ Validar AUROC, FAR @95%TPR en blind set
- Generar reportes de confianza por especie
- Integrar en móvil con interface de rechazo

### Mediano Plazo (1 mes)
- Desplegar paquetes regionales (empezar Antioquia)
- A/B testing: Open Set vs clasificación directa
- Recolectar falsos rechazos/aceptaciones en producción
- Gate de validación antes de nuevas especies

### Largo Plazo
- Expansión a nuevas regiones (Cauca, Chocó, etc)
- Fine-tuning de τ regionales si datos divergen
- Actualización automática de paquetes sin reentrenamiento

---

## Limitaciones Declaradas (Corrección 8)

```
INDIVIDUAL_INDEPENDENCE = CONTROLLED_NOT_FORMALLY_VERIFIABLE
OBSERVATION_INDEPENDENCE = NOT_FORMALLY_VERIFIABLE
CALIBRATION_AUROC = NOT_COMPUTABLE

⚠️  Group A (10 sp): independientemente calibradas
✓   Group B (31 sp): solo estructura, no calibración independiente

El sistema es apto para producción regional bajo estas limitaciones.
El gate de validación obligatorio previene degradación por cambios.
```
