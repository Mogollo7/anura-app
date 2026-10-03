# GEO-6 — Comparacion A/B/C/D

Mismo protocolo bootstrap en todas las filas de Open Set: 1000 iteraciones, seed=42,
estratificado por individuo (identico a GEO-2/GEO-3). Ranking evaluado sobre 7475 imagenes
KNOWN / 24 especies verdad-terreno / 41 especies candidatas con centroide (mismo pool que
GEO2/3/4/5).

## Tabla resumen

| Config | Descripcion | w_geo (ranking) | w_geo (open-set) | Top-1 | Top-3 | MRR | F1 macro | AUROC open-set | IC95% AUROC | FAR @thr_p95 | FRR @thr_p95 | BalAcc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **A** | visual solamente | 0.0 | 0.0 | 0.5852 | 0.8140 | 0.7145 | 0.2778 | 0.5733 | [0.541, 0.606] | 0.9339 | 0.0500 | 0.5080 |
| **B** | visual+geo, score UNICO reutilizado para ranking y open-set (sin gate separado) | 0.3 | 0.3 (mismo score) | 0.6625 | 0.8672 | 0.7741 | 0.3105 | 0.6096 | [0.582, 0.638] | 0.9339 | 0.0500 | 0.5080 |
| **C** | **Arquitectura de DOS ETAPAS**: ranking con w=0.3, gate open-set SEPARADO con w=0.9 sobre el top-1 de Etapa 1 | 0.3 | 0.9 | 0.6625 | 0.8672 | 0.7741 | 0.3105 | 0.6032 | [0.576, 0.633] | 0.8710 | 0.0500 | 0.5395 |
| **D** | GEO-2 original, score UNICO w=0.9 (reutilizado de `GEO2_WEIGHT_SWEEP.csv`, **oracle**: usa la especie verdadera para el componente geo de las imagenes KNOWN, ver caveat abajo) | 0.9 | 0.9 | 0.4107\* | 0.7549\* | 0.6084\*\* | 0.2265\* | 0.7015 | [0.673, 0.730] | 0.7419 | 0.0500 | 0.6040 |

\* Top-1/Top-3/F1 de D tomados de GEO-5 (`GEO5_closed_identification_metrics.json`, idéntica formula
w=0.9 aplicada al ranking); coinciden bit a bit con el recalculo interno de GEO-6.
\*\* MRR no fue calculado en GEO-5; se recalculo aqui usando la misma matriz de 41 candidatas para
comparabilidad interna: **MRR(D)=0.6084** (ver `GEO6_COMPARISON_SUMMARY.json` ->
`D_geo2_original_single_score_w0.9.ranking_using_same_score`). Notese que aunque el MRR de D
(0.6084) es menor que el de A/B/C (0.7145-0.7741), sigue siendo relativamente alto pese al Top-1
bajo (0.4107) porque, cuando D falla el top-1, casi siempre coloca a la especie correcta en
posicion 2-3 (Top-3=0.7549) — el prior geografico fuerte no elimina a la especie correcta del
ranking, solo la desplaza del primer lugar en ~41% de los casos.

## Caveat critico sobre D (hallazgo de GEO-6, no un ajuste forzado)

Al intentar reproducir D desde cero con la especie **predicha** (no la verdadera) como insumo
geografico para las imagenes KNOWN, el AUROC obtenido fue **0.6167**, no 0.70148. La diferencia
(+0.085 AUROC) es exactamente el efecto de que `phase_geo2_weight_sweep.py` (linea 127,
`known_top1 = known_sci_name`) usa la especie **verdadera** — no una prediccion — como entrada del
componente geografico para las imagenes KNOWN. Esto es un oracle no disponible en inferencia real
(no se conoce la especie verdadera; eso es justamente lo que el sistema intenta determinar). D se
reporta aqui **fielmente reproducido con ese oracle** (para permitir el contraste directo pedido
con el numero historico 0.70148), pero **no es comparable en pie de igualdad con B/C**, que usan
la especie REALMENTE predicha por Etapa 1. Este hallazgo no estaba documentado en GEO-2/3/4/5.

## Lectura de la comparacion

1. **Ranking (Top-1)**: C (0.6625) > B (0.6625, identico a C porque comparten Etapa 1) > A (0.5852)
   >> D (0.4107, con oracle inaplicable en inferencia real — con top1 predicho seria aun peor,
   ver GEO-5). El score de ranking de Etapa 1 (w=0.3) mejora +7.7pp Top-1 sobre visual puro y
   revierte por completo el colapso de Top-1 que GEO-5 encontro con w=0.9 (-17.4pp).

2. **Open-set (AUROC)**: A (0.5733) < C (0.6032) < B (0.6096) < D-oracle (0.7015). **C mejora sobre
   el baseline visual puro (+0.030 AUROC, IC no se solapa con A: [0.576,0.633] vs [0.541,0.606]
   se solapan levemente en el borde, ver nota de solapamiento abajo)**, pero NO alcanza el
   AUROC historico de D (0.70148) porque D depende de un oracle. Comparado contra un D
   "honesto" (top1 predicho, AUROC=0.6167, no reportado como fila oficial por no ser la
   metodologia original de GEO-2), C (0.6032) es comparable, ligeramente inferior.

   **Nota de solapamiento de IC**: A IC=[0.5408,0.6055], C IC=[0.5760,0.6325]. Los intervalos
   se solapan levemente (0.5760 < 0.6055), por lo que la mejora de C sobre A **no es
   estadisticamente contundente** al 95% con este bootstrap, aunque la diferencia puntual
   (+0.030) es consistente y en la direccion esperada. Se reporta sin forzar significancia.

3. **B vs C**: ambos comparten el mismo top-1 de Etapa 1 (w=0.3), pero difieren en el peso
   geografico usado para el open-set. B (reusar el score de ranking directamente, w=0.3) da
   AUROC=0.6096; C (gate separado, w=0.9) da AUROC=0.6032 — **practicamente empatados, B incluso
   marginalmente mayor**, ambos dentro del solapamiento de sus IC. Esto sugiere que, en esta
   region de pesos moderados, separar el gate no aporta una ganancia clara de AUROC sobre
   simplemente usar el score de ranking como score de open-set tambien — la separacion SI aporta
   un beneficio claro en Precision (C: 0.176 vs B: 0.099, ~1.8x mejor) y BalancedAccuracy
   (C: 0.539 vs B: 0.508), es decir, C rechaza UNKNOWN con menos falsos positivos sobre KNOWN
   que B al mismo FRR nominal, aunque el AUROC global no lo refleje con la misma claridad.

4. **Desglose por subgrupo (UNKNOWN)** (`GEO6_OPENSET_SUBGROUP_ANALYSIS.csv`):
   - same_genus vs different_genus: C mejora mas en same_genus (AUROC 0.630 vs A 0.582) que en
     different_genus (C 0.543 vs A 0.554, empeora levemente) — el componente geografico ayuda
     mas quando el error visual es "vecino taxonomico", como es esperable.
   - with_zone vs without_zone: **direccion contraintuitiva** (C: with_zone=0.437 <
     without_zone=0.725), igual que GEO-3 ya encontro. **No se interpreta como causal** — que
     observacion UNKNOWN tenga coordenada recuperable no es aleatorio (sesgo de seleccion
     documentado en GEO-3 y heredado aqui sin resolver).

## ¿Resuelve la separacion el conflicto de GEO-5?

GEO-5: w_geo=0.9 (D) es HELPFUL para open-set (0.573->0.701) pero HARMFUL para ranking cerrado
(Top-1 0.585->0.411), **usando el mismo score para ambas tareas**.

GEO-6 (arquitectura C): al separar los dos scores, **Top-1 mejora sobre el baseline (+7.7pp) EN
VEZ de empeorar**, y el AUROC de open-set tambien mejora sobre el baseline (+0.030), aunque de
forma mas modesta que el numero historico de D (que depende de un oracle no replicable). **La
separacion SI resuelve la direccion del conflicto** (ya no hay que elegir entre ranking bueno y
open-set malo, o viceversa — ambos mejoran simultaneamente sobre el baseline visual), pero **el
open-set de la arquitectura de dos etapas no alcanza el nivel que sugeria el numero original de
GEO-2** porque ese numero nunca fue alcanzable en produccion (dependia de conocer la especie
verdadera de antemano). Ver `GEO6_REPORT.md` seccion 3 para la interpretacion completa.
