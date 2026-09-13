---
title: "Arquitectura Multimodal"
proyecto: Anura
tipo: metodologÃ­a
estado: redactado
tags: [anura, metodologÃ­a, multimodal, fusiÃ³n, bioacÃºstica]
---

# Arquitectura Multimodal

[[Anura â€” Ãndice General]] Â· [[Pipeline del Sistema]] Â· [[Modelo de VisiÃ³n â€” BioCLIP]] Â· [[Open-Set Recognition]]

> [!abstract] Idea central
> Una fotografÃ­a no siempre basta para identificar un anuro: hay especies crÃ­pticas que solo se separan por el canto, y hay fotos donde el carÃ¡cter diagnÃ³stico no es visible. La arquitectura multimodal combina **visiÃ³n + bioacÃºstica + contexto geogrÃ¡fico y ambiental** para que la ausencia o debilidad de una fuente no bloquee la identificaciÃ³n (RNF-06).

## 1. Las tres ramas

```
                        OBSERVACIÃ“N
        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
        â–¼                   â–¼                   â–¼
   ðŸ“· IMAGEN            ðŸŽ™ï¸ AUDIO         ðŸ“ METADATOS
        â”‚                   â”‚                   â”‚
  segmentaciÃ³n        espectrograma        normalizaciÃ³n
        â”‚                   â”‚                   â”‚
     BioCLIP          modelo acÃºstico          MLP
        â”‚                   â”‚                   â”‚
  embedding 512-d     embedding acÃºstico   vector contexto
        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                            â–¼
                    FUSIÃ“N PONDERADA
                            â–¼
                      RANKING TOP-3
```

### 1.1 Rama visual

| ParÃ¡metro | Valor |
| --- | --- |
| Entrada | 224 Ã— 224 RGB, recorte segmentado del individuo |
| NormalizaciÃ³n | Media/desviaciÃ³n calculadas **solo sobre train** |
| Backbone | BioCLIP ViT-B/16 (congelado o parcialmente ajustado) |
| Salida | Embedding 512-d, L2-normalizado |
| PÃ©rdida | Cross-entropy jerÃ¡rquica (+ [[ImplementaciÃ³n de Triplet Loss|triplet]] opcional) |
| Detalle | Ver [[Modelo de VisiÃ³n â€” BioCLIP]] |

Admite **mÃºltiples vistas del mismo individuo** (RF-02): dorsal, lateral, ventral. Estrategia de agregaciÃ³n recomendada: calcular el embedding de cada vista y promediarlos (tras normalizar), o mejor, mantenerlos separados y agregar a nivel de evidencia â€” una vista ventral aporta caracteres que la dorsal no puede aportar, y promediar los vectores diluye esa informaciÃ³n. La segunda opciÃ³n es mÃ¡s fiel al diseÃ±o de evidencia por regiones del [[Pipeline del Sistema]].

### 1.2 Rama acÃºstica

| ParÃ¡metro | Valor |
| --- | --- |
| Entrada | WAV mono, 44,1 kHz, 16-bit, ventana 3â€“5 s, SNR â‰¥ 15 dB |
| RepresentaciÃ³n | Mel-espectrograma ~128 bins Ã— 256 pasos, replicado a 3 canales |
| Backbone | **Modelo de audio propio y dedicado** (CNN pequeÃ±a, 1-3 MB â€” arquitectura por definir, ver [[Modelo de VisiÃ³n â€” BioCLIP]] Â§9) |
| AugmentaciÃ³n | SpecAugment: `TimeShift`, `FrequencyMasking`, `TimeMasking` |
| Salida | Embedding o clasificaciÃ³n acÃºstica directa + tipo de canto (reproductivo / territorial, RF-07) |
| Detalle | Ver [[Modelo de VisiÃ³n â€” BioCLIP]] Â§8â€“9 |

> [!warning] Revisado 2026-09-08: ya no se reutiliza un backbone compartido
> El modelo visual on-device dejÃ³ de ser BioCLIP (INT8 fracasÃ³ en pruebas reales) y pasÃ³ a ser **EdgeNeXt-Tiny**, destilado con un objetivo estrecho (morfologÃ­a de rana en fotos). Reutilizarlo para espectrogramas es de mayor riesgo que reutilizar BioCLIP (que sÃ­ era un modelo fundacional de propÃ³sito general), y el ahorro de MB de reutilizar ya no es decisivo a esta escala. **DecisiÃ³n del autor (C-7, [[Inconsistencias y Decisiones Pendientes]]):** modelo de audio propio y dedicado, por facilidad de implementaciÃ³n. Sigue condicionado a confirmar cobertura de dataset de audio para las 28 especies (punto Go/No-Go del 18 sep en [[Cronograma y Plan de Trabajo]]) antes de invertir tiempo en entrenarlo.

### 1.3 Rama de metadatos

| Campo | CodificaciÃ³n |
| --- | --- |
| Latitud / longitud | Coordenadas cÃ­clicas o celdas H3/geohash |
| Altitud (msnm) | Normalizada; es muy informativa en los Andes |
| Fecha | Mes codificado cÃ­clicamente (sen/cos) â€” captura estacionalidad reproductiva |
| Hora | CÃ­clica â€” separa especies diurnas de nocturnas |
| Ecosistema / microhÃ¡bitat | One-hot o embedding aprendido |
| Temperatura, humedad, precipitaciÃ³n | Normalizadas |

Su funciÃ³n **no** es clasificar, sino aportar un *prior* de plausibilidad. Se implementa mejor como una **verosimilitud por especie** dada la ubicaciÃ³n y la Ã©poca, calculada a partir de los registros de distribuciÃ³n (GBIF, SiB Colombia, colecciones), que como un MLP entrenado con los pocos datos propios. Con 550 observaciones, un MLP sobre metadatos aprenderÃ­a el sesgo de muestreo del proyecto, no la ecologÃ­a de las especies.

## 2. CuÃ¡ndo aporta cada modalidad

| SituaciÃ³n de campo | VisiÃ³n | Audio | Contexto |
| --- | --- | --- | --- |
| Rana quieta, buena luz, vista dorsal | â—â—â— | â—‹ | â—â— |
| Coro nocturno, animal no visible | â—‹ | â—â—â— | â—â— |
| Especies crÃ­pticas del mismo gÃ©nero | â—â— | â—â—â— | â—â— |
| Foto de mala calidad | â— | â—â— | â—â— |
| Especie fuera de su rango conocido | â—â—â— | â—â—â— | âš ï¸ contradice |

La Ãºltima fila es la que mÃ¡s cuidado exige: ver Â§5.

## 3. Estrategia de fusiÃ³n

Tres opciones, de menos a mÃ¡s ambiciosa:

| Tipo | CÃ³mo | Ventaja | Inconveniente |
| --- | --- | --- | --- |
| **Late fusion (tardÃ­a)** âœ… | Cada rama produce su ranking; se combinan las puntuaciones | Robusta a modalidades ausentes; interpretable; entrenable por partes | No aprende interacciones entre modalidades |
| Early fusion | Concatenar embeddings y clasificar sobre el conjunto | Puede capturar interacciones | Se rompe si falta una modalidad; necesita muchos mÃ¡s datos |
| FusiÃ³n por atenciÃ³n | Aprende cuÃ¡nto pesar cada modalidad por observaciÃ³n | La mÃ¡s potente | Requiere un volumen de datos que este proyecto no tiene |

**RecomendaciÃ³n: late fusion.** Es la Ãºnica compatible con el RNF-06 (predecir con datos faltantes) sin trucos, y la Ãºnica que permite justificar en el documento quÃ© aportÃ³ cada fuente.

FormulaciÃ³n:

$$S(especie) = w_v \cdot s_{visual} + w_a \cdot s_{audio} + w_c \cdot s_{contexto} + w_m \cdot s_{morfologÃ­a}$$

con renormalizaciÃ³n de los pesos sobre las modalidades **presentes** (si no hay audio, `w_a` se redistribuye). Sobre puntuaciones calibradas â€” log-verosimilitudes o probabilidades tras *temperature scaling* â€” nunca sobre porcentajes crudos de softmax de modelos distintos, que no son comparables entre sÃ­.

Los pesos se ajustan **en el conjunto de validaciÃ³n**, no a mano ni en test.

## 4. El experimento que hay que hacer

Es, probablemente, el resultado mÃ¡s citable del trabajo: cuantificar la aportaciÃ³n real de cada modalidad.

| ConfiguraciÃ³n | Top-1 | Top-3 | F1 macro | Î” vs. solo imagen |
| --- | --- | --- | --- | --- |
| Solo imagen | | | | â€” |
| Imagen + contexto | | | | |
| Imagen + audio | | | | |
| Imagen + audio + contexto | | | | |
| Imagen + audio + contexto + morfologÃ­a | | | | |

Con el mismo split y protocolo. Registrar en [[Experimentos y Resultados]] y [[MÃ©tricas Offline]].

> [!warning] Sesgo de disponibilidad de audio
> Solo se puede evaluar audio en el subconjunto de observaciones que lo tienen, y probablemente no serÃ¡ una muestra aleatoria (se graba cuando el animal canta, que correlaciona con especie, sexo, Ã©poca y hora). Comparar "imagen" contra "imagen+audio" sobre conjuntos distintos infla artificialmente la ganancia. La comparaciÃ³n honesta se hace **sobre el mismo subconjunto** que tiene ambas modalidades, y se declara su tamaÃ±o.

## 5. El contexto geogrÃ¡fico como prior, nunca como filtro

Regla explÃ­cita en las notas originales y que conviene mantener como invariante del diseÃ±o:

> La ubicaciÃ³n puede aumentar o disminuir la puntuaciÃ³n de una especie, pero **no debe eliminarla automÃ¡ticamente**.

Los motivos son biolÃ³gicos, no tÃ©cnicos: los mapas de distribuciÃ³n estÃ¡n incompletos, las especies se expanden, y precisamente **los registros mÃ¡s valiosos cientÃ­ficamente son los que aparecen donde no se esperaba**. Un sistema que filtre duro por distribuciÃ³n es un sistema incapaz de detectar una ampliaciÃ³n de rango â€” justo el hallazgo que mÃ¡s interesarÃ­a a un herpetÃ³logo.

ImplementaciÃ³n segura: el prior geogrÃ¡fico se aplica como un factor acotado (por ejemplo, multiplicador en [0,5 â€“ 1,5]) y se muestra al usuario cuando contradice a la evidencia visual: *"morfolÃ³gicamente compatible con X, pero fuera de su distribuciÃ³n conocida â€” verificar"*.

## 6. QuÃ© falta por decidir o medir

- [ ] Elegir backbone acÃºstico (B0 propio vs. preentrenado vs. AnuraSet).
- [ ] Definir cÃ³mo se agregan mÃºltiples vistas del mismo individuo.
- [ ] Construir la fuente de verosimilitud geogrÃ¡fica (GBIF/SiB) por especie.
- [ ] Calibrar las puntuaciones de cada rama antes de fusionar.
- [ ] Ejecutar la tabla de ablaciÃ³n de Â§4.



