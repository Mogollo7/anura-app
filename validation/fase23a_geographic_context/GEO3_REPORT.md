# GEO-3 — Reporte final

## Gate 0
AUROC reproducido = 0.5732919409, oficial = 0.5732919409, abs_diff = 0.0. **PASSED.**

## Parte A — Cobertura (ver GEO3_COVERAGE_REPORT.md para detalle)
- UNKNOWN con zona: 262/620 = 42.26% (identico a GEO-2, sin mejora)
- KNOWN con zona: 2763/7475 = 36.96%
- Total con zona: 3025/8095 = 37.37%
- Coordenadas adicionales recuperadas respecto a GEO-2: **0** (cache ya saturado al 100% de los observation_id necesarios)
- Observaciones sin ubicacion verificable: 358 UNKNOWN sin zona (pero con lat/lon, fuera del area del prior) + 4712 KNOWN sin zona + 44 KNOWN sin observation_id (irrecuperable sin inventar datos)
- Leakage: interseccion directa no aplicable (prior agregado sin columna obs_id); purga documentada en manifest existente (1214 registros excluidos de 15081 originales). leakage=0 confirmado indirectamente via el proceso de purga ya auditado en GEO-1/GEO-2, no reproducido de cero en GEO-3.
- Prior limpio mantenido: si, se reutilizo `prior_zone_taxon_v2_clean.csv` sin modificacion.

## Parte B — Curva operativa (w_geo=0.9 fijo, heredado de GEO-2, NO reoptimizado)
AUROC reconfirmado con scoring combinado = **0.701476** (identico a GEO2_WEIGHT_SWEEP.csv fila w_geo=0.9: 0.7014759952529939). Bootstrap (1000 iter, seed=42, estratificado por individuo) CI [0.6728, 0.7302].

### B.1/B.2 — Puntos operativos por nivel de FAR (curva densa, 400 thresholds)
| FAR objetivo | threshold | FAR | FRR | BalAcc | TPR | TNR | Precision | NPV |
|---|---|---|---|---|---|---|---|---|
| <=50% | 0.8881 | 49.84% | 24.63% | 0.6277 | 0.5016 | 0.7537 | 0.1445 | 0.9480 |
| <=30% | 0.8691 | 29.84% | 46.81% | 0.6168 | 0.7016 | 0.5319 | 0.1106 | 0.9555 |
| <=20% | 0.8454 | 19.84% | 63.75% | 0.5821 | 0.8016 | 0.3625 | 0.0945 | 0.9566 |
| <=10% | 0.6057 | 10.00% | 66.38% | 0.6181 | 0.9000 | 0.3362 | 0.1011 | 0.9759 |
| <=5% | 0.5060 | 4.68% | 70.25% | 0.6254 | 0.9532 | 0.2975 | 0.1012 | 0.9871 |

Todos los niveles solicitados (<=50/30/20/10/5%) tienen un punto operativo encontrado (`FOUND`). Ver `GEO3_OPERATING_POINTS.csv`.

**Lectura honesta:** en todos los niveles, FRR es alto (25%-70%): para reducir FAR (dejar pasar UNKNOWN como conocido) se paga con muchos KNOWN mal rechazados como "no registrada". Precision se mantiene muy baja (~10-14%) porque la clase UNKNOWN es minoritaria (620 vs 7475): incluso con TNR/NPV altos, cualquier threshold generoso produce muchos falsos positivos de "unknown" sobre el pool KNOWN, mucho mayor en tamano.

### B.3 — Tres regiones (analisis, no implementacion)
Los scores sí permiten definir 3 bandas razonables usando dos thresholds (p.ej. el de FAR<=10% como corte alto=CONOCIDA, y el EER/FAR<=30% como corte bajo=NO_REGISTRADA, con NO_CONCLUYENTE en medio), pero la banda intermedia heredaria el mismo problema de precision baja: no hay una discontinuidad clara en la distribucion de combined_score que separe limpiamente las 3 clases (ver B.4, EER gap=0.019, señal moderada no fuerte). Es viable como heuristica de UX (mostrar "no concluyente" en vez de forzar una decision binaria) pero no resuelve el problema de calibracion subyacente.

### B.4 — Tendencia threshold -> FAR/FRR
- EER aproximado: threshold=0.8762, FAR=36.77%, FRR=38.68% (gap=1.9pp, el punto mas cercano a FAR=FRR encontrado en la grilla de 400 thresholds).
- Maxima Balanced Accuracy: threshold=0.8928, BalAcc=0.6304, FAR=54.52%, FRR=19.40% (favorece fuertemente FRR bajo, no es el threshold elegido para los desgloses por diseno explicito, ver regla dura).
- FAR minimo (0%): threshold=0.0315, pero FRR=100% (rechaza absolutamente todo como UNKNOWN, sin valor practico) — extremo trivial, no operativo.
- Pareto (FAR, FRR): 104 candidatos no dominados en la grilla evaluada; ver `GEO3_THRESHOLD_TREND_SUMMARY.json` para la lista completa.
- Threshold usado para los desgloses B.5/B.6: el de FAR<=30% (0.8691), por ser el nivel mas estricto de la lista con FOUND que aun conserva TPR razonable (70%).

### B.5 — UNKNOWN mismo genero vs genero distinto (threshold=0.8691, FAR<=30%)
- same_genus: n=426, detectados correctamente como UNKNOWN=289 (67.84%)
- different_genus: n=194, detectados correctamente=146 (75.26%)

Diferencia moderada (~7.4pp): el sistema detecta ligeramente mejor las especies UNKNOWN de genero no visto, como es esperable (mayor distancia visual), pero la deteccion de same_genus tambien es razonable (~68%), sugiriendo que el score combinado no depende solo de la separacion taxonomica gruesa.

### B.6 — UNKNOWN con zona vs sin zona (mismo threshold=0.8691)
- with_zone: n=262, detectados=133 (50.76%)
- without_zone: n=358, detectados=302 (84.36%)
- Diferencia: **-33.6pp** (con_zona PEOR que sin_zona, no mejor).

**Esto contradice la hipotesis de que "mas cobertura geografica ayudaria".** La razon aparente: las observaciones sin zona reciben el score geografico neutral (1/K), que tras la normalizacion min-max resulta relativamente "unknown-like" y consistente; las observaciones con zona reciben un score de prior real que, cuando el top-1 visual coincide con una especie efectivamente probable en esa zona (aun siendo la imagen realmente UNKNOWN), produce una probabilidad alta -> geo_unknownness baja -> el combinado las empuja hacia "conocida" incorrectamente. Es decir, el prior geografico está ayudando a species conocidas locales pero, para las UNKNOWN que caen en zonas con fauna similar, el prior las camufla como conocidas. **Esta comparacion tiene sesgo de seleccion** (las zonas con zona asignada corresponden geograficamente a Antioquia, la misma region del prior; no es un experimento independiente) — se documenta explicitamente como tal, no como evaluacion causal limpia.

## Veredicto principal
**GEO3_THRESHOLD_OPERATING_POINT_FOUND** — se encontraron puntos operativos validos en los 5 niveles de FAR solicitados, con bootstrap estable (AUROC CI [0.673, 0.730]). Condicion secundaria: **GEO3_GEOGRAPHY_NOT_ACTIONABLE en cuanto a cobertura** — la cobertura de zona no mejoro respecto a GEO-2 (sigue en 42.26% UNKNOWN) y el analisis B.6 muestra que, en el threshold seleccionado, la zona asignada se asocia a PEOR deteccion de UNKNOWN, no mejor — contrario a lo esperado y sin evidencia de que ampliar cobertura geografica (fuera de Antioquia) mejoraria el resultado.

## Resumen ejecutivo (respuestas directas)
1. Se reprodujo AUROC=0.57329 (diff=0.0). Si.
2. Cobertura UNKNOWN con zona: 262/620 = 42.26% (sin cambio vs GEO-2).
3. Cobertura KNOWN con zona: 2763/7475 = 36.96%.
4. Coordenadas adicionales recuperadas vs GEO-2: 0 (cache ya saturado al 100%).
5. Observaciones sin ubicacion: 358 UNKNOWN sin zona + 4712 KNOWN sin zona (todas con lat/lon pero fuera del area del prior) + 44 KNOWN sin observation_id (irrecuperable).
6. Leakage=0: confirmado de forma indirecta (purga documentada en manifest existente; el prior agregado no tiene columna obs_id para interseccion directa post-hoc).
7. Prior limpio mantenido: si, sin modificaciones.
8. AUROC con w_geo=0.9 reconfirmado (sin reoptimizar): 0.701476, CI bootstrap [0.6728, 0.7302].
9. FAR/FRR al variar threshold: relacion monotona esperada (a menor threshold, mayor FAR y menor FRR); EER≈37% (ambos), lejos de niveles operativos deseables por la fuerte disparidad de tamano de clases (620 vs 7475).
10. Threshold con FAR<=50%: si, threshold=0.8881 (FRR=24.63%, BalAcc=0.6277).
11. Thresholds con FAR<=30/20/10/5%: todos FOUND — 0.8691 (FRR=46.81%), 0.8454 (FRR=63.75%), 0.6057 (FRR=66.38%), 0.5060 (FRR=70.25%).
12. Geografia ayuda mas con zona asignada: **NO** — en el threshold seleccionado, con_zona detecta peor (50.76%) que sin_zona (84.36%); posible sesgo de seleccion documentado, no evaluacion causal limpia.
13. UNKNOWN mismo genero vs distinto (threshold FAR<=30%): same_genus 67.84% (289/426), different_genus 75.26% (146/194).
14. Region util para NO_CONCLUYENTE: parcialmente — se puede definir una banda intermedia, pero la señal de separacion (EER gap=1.9pp, precision baja en todos los thresholds) es moderada, no fuerte; util como heuristica de UX, no como solucion de calibracion.
15. Siguiente paso recomendado: no invertir mas en ampliar cobertura geografica dentro del alcance actual (Antioquia); el techo de 42%/37% es estructural (area del prior), no de recuperacion de datos. Si se quiere mejorar geografia, el siguiente paso seria extender el prior mas alla de Antioquia (fuera de alcance de GEO-3). Para el threshold operativo, dado el desbalance de clases y precision baja en todos los niveles, evaluar si el caso de uso tolera FRR alto (>45%) antes de considerar el prior geografico listo para produccion; el hallazgo B.6 (zona correlaciona con peor deteccion) debe investigarse antes de usar "zona asignada" como señal de confianza en la region NO_CONCLUYENTE.

## Artefactos generados (confirmados con ls real)
```
validation/fase23a_geographic_context/GEO3_COVERAGE_AUDIT.json
validation/fase23a_geographic_context/GEO3_COVERAGE_REPORT.md
validation/fase23a_geographic_context/GEO3_THRESHOLD_CURVE.csv
validation/fase23a_geographic_context/GEO3_THRESHOLD_CURVE.json
validation/fase23a_geographic_context/GEO3_BOOTSTRAP_RESULTS.json
validation/fase23a_geographic_context/GEO3_OPERATING_POINTS.csv
validation/fase23a_geographic_context/GEO3_REPORT.md
validation/fase23a_geographic_context/GEO3_REPRODUCIBILITY_MANIFEST.json
validation/fase23a_geographic_context/GEO3_RECOVERY_LOG.json (adicional, A.1)
validation/fase23a_geographic_context/GEO3_THRESHOLD_TREND_SUMMARY.json (adicional, B.4)
validation/fase23a_geographic_context/scripts/phase_geo3_coverage_and_threshold.py
```
