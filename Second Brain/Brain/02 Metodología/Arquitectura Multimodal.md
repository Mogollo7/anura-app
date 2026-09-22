---
title: "Arquitectura Multimodal"
proyecto: Anura
tipo: metodología
estado: redactado
tags: [anura, metodología, multimodal, fusión, bioacàºstica]
---

# Arquitectura Multimodal

[[Anura â€” àndice General]] · [[Pipeline del Sistema]] · [[Modelo de Visión â€” BioCLIP]] · [[Open-Set Recognition]]

> [!abstract] Idea central
> Una fotografía no siempre basta para identificar un anuro: hay especies crípticas que solo se separan por el canto, y hay fotos donde el carácter diagnóstico no es visible. La arquitectura multimodal combina **visión + bioacàºstica + contexto geográfico y ambiental** para que la ausencia o debilidad de una fuente no bloquee la identificación (RNF-06).

## 1. Las tres ramas

```
                        OBSERVACIà“N
        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
        â–¼                   â–¼                   â–¼
   ðŸ“· IMAGEN            ðŸŽ™ï¸ AUDIO         ðŸ“ METADATOS
        â”‚                   â”‚                   â”‚
  segmentación        espectrograma        normalización
        â”‚                   â”‚                   â”‚
     BioCLIP          modelo acàºstico          MLP
        â”‚                   â”‚                   â”‚
  embedding 512-d     embedding acàºstico   vector contexto
        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                            â–¼
                    FUSIà“N PONDERADA
                            â–¼
                      RANKING TOP-3
```

### 1.1 Rama visual

| Parámetro | Valor |
| --- | --- |
| Entrada | 224 à— 224 RGB, recorte segmentado del individuo |
| Normalización | Media/desviación calculadas **solo sobre train** |
| Backbone | BioCLIP ViT-B/16 (congelado o parcialmente ajustado) |
| Salida | Embedding 512-d, L2-normalizado |
| Pérdida | Cross-entropy jerárquica (+ [[Implementación de Triplet Loss|triplet]] opcional) |
| Detalle | Ver [[Modelo de Visión â€” BioCLIP]] |

Admite **màºltiples vistas del mismo individuo** (RF-02): dorsal, lateral, ventral. Estrategia de agregación recomendada: calcular el embedding de cada vista y promediarlos (tras normalizar), o mejor, mantenerlos separados y agregar a nivel de evidencia â€” una vista ventral aporta caracteres que la dorsal no puede aportar, y promediar los vectores diluye esa información. La segunda opción es más fiel al diseño de evidencia por regiones del [[Pipeline del Sistema]].

### 1.2 Rama acàºstica

| Parámetro | Valor |
| --- | --- |
| Entrada | WAV mono, 44,1 kHz, 16-bit, ventana 3â€“5 s, SNR â‰¥ 15 dB |
| Representación | Mel-espectrograma ~128 bins à— 256 pasos, replicado a 3 canales |
| Backbone | **Modelo de audio propio y dedicado** (CNN pequeña, 1-3 MB â€” arquitectura por definir, ver [[Modelo de Visión â€” BioCLIP]] §9) |
| Augmentación | SpecAugment: `TimeShift`, `FrequencyMasking`, `TimeMasking` |
| Salida | Embedding o clasificación acàºstica directa + tipo de canto (reproductivo / territorial, RF-07) |
| Detalle | Ver [[Modelo de Visión â€” BioCLIP]] §8â€“9 |

> [!warning] Revisado 2026-09-08: ya no se reutiliza un backbone compartido
> El modelo visual on-device dejó de ser BioCLIP (INT8 fracasó en pruebas reales) y pasó a ser **EdgeNeXt-Tiny**, destilado con un objetivo estrecho (morfología de rana en fotos). Reutilizarlo para espectrogramas es de mayor riesgo que reutilizar BioCLIP (que sí era un modelo fundacional de propósito general), y el ahorro de MB de reutilizar ya no es decisivo a esta escala. **Decisión del autor (C-7, [[Inconsistencias y Decisiones Pendientes]]):** modelo de audio propio y dedicado, por facilidad de implementación. Sigue condicionado a confirmar cobertura de dataset de audio para las 28 especies (punto Go/No-Go del 18 sep en [[Cronograma y Plan de Trabajo]]) antes de invertir tiempo en entrenarlo.

### 1.3 Rama de metadatos

| Campo | Codificación |
| --- | --- |
| Latitud / longitud | Coordenadas cíclicas o celdas H3/geohash |
| Altitud (msnm) | Normalizada; es muy informativa en los Andes |
| Fecha | Mes codificado cíclicamente (sen/cos) â€” captura estacionalidad reproductiva |
| Hora | Cíclica â€” separa especies diurnas de nocturnas |
| Ecosistema / microhábitat | One-hot o embedding aprendido |
| Temperatura, humedad, precipitación | Normalizadas |

Su función **no** es clasificar, sino aportar un *prior* de plausibilidad. Se implementa mejor como una **verosimilitud por especie** dada la ubicación y la época, calculada a partir de los registros de distribución (GBIF, SiB Colombia, colecciones), que como un MLP entrenado con los pocos datos propios. Con 550 observaciones, un MLP sobre metadatos aprendería el sesgo de muestreo del proyecto, no la ecología de las especies.

## 2. Cuándo aporta cada modalidad

| Situación de campo | Visión | Audio | Contexto |
| --- | --- | --- | --- |
| Rana quieta, buena luz, vista dorsal | â—â—â— | â—‹ | â—â— |
| Coro nocturno, animal no visible | â—‹ | â—â—â— | â—â— |
| Especies crípticas del mismo género | â—â— | â—â—â— | â—â— |
| Foto de mala calidad | â— | â—â— | â—â— |
| Especie fuera de su rango conocido | â—â—â— | â—â—â— | âš ï¸ contradice |

La àºltima fila es la que más cuidado exige: ver §5.

## 3. Estrategia de fusión

Tres opciones, de menos a más ambiciosa:

| Tipo | Cómo | Ventaja | Inconveniente |
| --- | --- | --- | --- |
| **Late fusion (tardía)** âœ… | Cada rama produce su ranking; se combinan las puntuaciones | Robusta a modalidades ausentes; interpretable; entrenable por partes | No aprende interacciones entre modalidades |
| Early fusion | Concatenar embeddings y clasificar sobre el conjunto | Puede capturar interacciones | Se rompe si falta una modalidad; necesita muchos más datos |
| Fusión por atención | Aprende cuánto pesar cada modalidad por observación | La más potente | Requiere un volumen de datos que este proyecto no tiene |

**Recomendación: late fusion.** Es la àºnica compatible con el RNF-06 (predecir con datos faltantes) sin trucos, y la àºnica que permite justificar en el documento qué aportó cada fuente.

Formulación:

$$S(especie) = w_v \cdot s_{visual} + w_a \cdot s_{audio} + w_c \cdot s_{contexto} + w_m \cdot s_{morfología}$$

con renormalización de los pesos sobre las modalidades **presentes** (si no hay audio, `w_a` se redistribuye). Sobre puntuaciones calibradas â€” log-verosimilitudes o probabilidades tras *temperature scaling* â€” nunca sobre porcentajes crudos de softmax de modelos distintos, que no son comparables entre sí.

Los pesos se ajustan **en el conjunto de validación**, no a mano ni en test.

## 4. El experimento que hay que hacer

Es, probablemente, el resultado más citable del trabajo: cuantificar la aportación real de cada modalidad.

| Configuración | Top-1 | Top-3 | F1 macro | Î” vs. solo imagen |
| --- | --- | --- | --- | --- |
| Solo imagen | | | | â€” |
| Imagen + contexto | | | | |
| Imagen + audio | | | | |
| Imagen + audio + contexto | | | | |
| Imagen + audio + contexto + morfología | | | | |

Con el mismo split y protocolo. Registrar en [[Experimentos y Resultados]] y [[Métricas Offline]].

> [!warning] Sesgo de disponibilidad de audio
> Solo se puede evaluar audio en el subconjunto de observaciones que lo tienen, y probablemente no será una muestra aleatoria (se graba cuando el animal canta, que correlaciona con especie, sexo, época y hora). Comparar "imagen" contra "imagen+audio" sobre conjuntos distintos infla artificialmente la ganancia. La comparación honesta se hace **sobre el mismo subconjunto** que tiene ambas modalidades, y se declara su tamaño.

## 5. El contexto geográfico como prior, nunca como filtro

Regla explícita en las notas originales y que conviene mantener como invariante del diseño:

> La ubicación puede aumentar o disminuir la puntuación de una especie, pero **no debe eliminarla automáticamente**.

Los motivos son biológicos, no técnicos: los mapas de distribución están incompletos, las especies se expanden, y precisamente **los registros más valiosos científicamente son los que aparecen donde no se esperaba**. Un sistema que filtre duro por distribución es un sistema incapaz de detectar una ampliación de rango â€” justo el hallazgo que más interesaría a un herpetólogo.

Implementación segura: el prior geográfico se aplica como un factor acotado (por ejemplo, multiplicador en [0,5 â€“ 1,5]) y se muestra al usuario cuando contradice a la evidencia visual: *"morfológicamente compatible con X, pero fuera de su distribución conocida â€” verificar"*.

## 5.1 Integrado en producción (Antioquia, 2026-09-22)

El prior geográfico de §5 **ya está integrado en la app Android**, no solo diseñado. Ruta real:

- **Origen del prior**: `pipeline_dataset/paquetes_zonales.py` — `P(especie|zona)` con suavizado
  de Laplace sobre ocurrencias reales, `zona` = celda de 0.25° agregada (point-in-polygon DANE,
  [[Dataset Jerárquico de Colombia — Paquetes Departamentales]]). Validado con **control de
  fuga real** (las observaciones de prueba se retiran del conteo del prior antes de evaluar):
  Top-1 **62.9%→72.5%** (+9.6pp), Top-3 82.0%→83.2%, sobre 167 imágenes de prueba de Antioquia
  (`COLOMBIA_ANURA/ANTIOQUIA/reports/packages_v1.0.0.json`).
- **Combinación** (nunca filtro duro, cumple la regla de §5): `score(s) = voto_kNN(s) · P(s|z)^0.75`
  — un multiplicador acotado por la ley de potencia, no una eliminación. Especies sin registro en
  la zona usan `p_unobserved` (Laplace), nunca cero.
- **Dónde vive el código**: los 4 paquetes de prior por zona (`antioquia_zone_00X_v1.0.0.sqlite`,
  ya construidos en `COLOMBIA_ANURA/ANTIOQUIA/packages/v1.0.0/zones/`, 16-24 KB cada uno) se
  fusionaron dentro del `package.sqlite` que ya se empaqueta en la app (tablas `zone_prior_meta` +
  `zone_prior`), en vez de enviarse como archivos separados — evita tocar el instalador de
  paquetes. Lectura en `PackageVectorIndex.zoneIdFor()`/`zonePrior()`, combinación en
  `KnnVote.candidates(neighbors, geoPrior)`, hilado desde las coordenadas GPS ya capturadas en el
  Paso 1 del wizard (`AnuraRepository.identifyDraftPhoto()` → `AnuraIdentifier.identify(...)`).
- **Qué NO se tocó**: el rechazo Open Set (Mahalanobis, τ=39.35 congelado en Fase 13) es
  independiente de este prior — decide sobre la distancia al centroide más cercano, no sobre el
  ganador del voto k-NN. Sin coordenadas o fuera de la cobertura del paquete (4 zonas de
  Antioquia), el resultado es idéntico al voto puramente visual de siempre.

⚠️ Nota importante para no repetir un experimento ya cerrado: usar **OpenTopoData por punto
exacto** (elevación/pendiente/orientación en tiempo real) para mejorar el *rechazo* Open Set
**ya se probó y dio `NO_GO`** (`validation/open_set_topography_v1/TOPOGRAPHIC_CONTEXT_REPORT.md`):
FAR 36.94%→36.77%, "un único caso", sin evidencia suficiente. El prior de zona de arriba es
distinto — mejora el *ranking* de especies (Top-1), no el rechazo — y por eso sí se integró.

## 5.2 Incidente real en campo y corrección (2026-09-22)

**Lo que pasó**: §5.1 aplicó el prior de zona (y luego el de clima, §5.1 clima) directamente a la
**decisión oficial** (qué especie queda identificada), no solo a la visualización. Esto violó la
regla de §5 ("factor acotado, p. ej. [0.5–1.5]") sin que nadie lo notara en su momento: el
multiplicador real `P(s|z)^0.75` no está acotado — para *Dendropsophus bogerti* vs. *Dendrobates
truncatus* en la zona de tierras bajas la razón de prior es ~5× (0.0455 vs. 0.0090), suficiente
para voltear un voto visual correcto y seguro. Caso real reportado: la misma foto de una *D.
bogerti* identificada correctamente por Foto ID (voto puramente visual) dio *D. truncatus* al
pasar por el paso a paso completo (con coordenadas → prior de zona aplicado a la decisión).

**Corrección**: la especie identificada (`taxonId`, lo que decide aceptar/rechazar y lo que se
guarda en la observación) sale **siempre** del voto k-NN puramente visual — sin excepción, sin
importar contexto disponible. El prior de zona y el de clima **solo** reordenan/matizan las
candidatas alternativas mostradas y el porcentaje de confianza mostrado — nunca la identidad de
la especie. Esto es literalmente la regla que §5 ya pedía; la implementación de §5.1 simplemente
no la siguió al pie de la letra. Código: `AnuraIdentifier.kt`, `official = KnnVote.candidates(neighbors)`
sin `geoPrior`/`weatherMultiplier` — esos dos parámetros solo entran en la lista de candidatas de
visualización (`broader`), nunca en `official`.

**Lección para futuros priors de contexto** (SVL, ecosistema, microhábitat, hora — ver
[[Contexto del Paso a Paso — Datos Faltantes]]): cualquier prior nuevo debe evaluarse no solo por
Top-1 agregado (que puede mejorar en conjunto aunque falle en casos individuales confiados), sino
por si puede voltear una identificación visual de alta confianza — y si puede, debe limitarse a
afectar solo candidatas/porcentajes mostrados, no la decisión oficial, hasta que se demuestre
explícitamente que acotarlo (factor en rango fijo, o solo activarse cuando el margen visual es
estrecho) no pierde la mejora medida en PC.

## 6. Qué falta por decidir o medir

- [ ] Elegir backbone acàºstico (B0 propio vs. preentrenado vs. AnuraSet).
- [ ] Definir cómo se agregan màºltiples vistas del mismo individuo.
- [x] Construir la fuente de verosimilitud geográfica (GBIF/SiB) por especie — hecho para
  Antioquia (§5.1), pendiente para el resto de departamentos.
- [ ] Calibrar las puntuaciones de cada rama antes de fusionar.
- [ ] Ejecutar la tabla de ablación de §4.
- [ ] Validar en dispositivo real la integración de §5.1 (pendiente al momento de esta nota).



