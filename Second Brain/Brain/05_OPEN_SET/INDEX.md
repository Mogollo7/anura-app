# 05_OPEN_SET: consolidación de reconocimiento abierto

## ACTUALIZACIÓN 2026-09-13 — Fase 13 completada
La fase operativa **ya no es NOT_EXECUTED**. Fase 13 calibró y evaluó ciegamente
un umbral Mahalanobis (Ledoit-Wolf) sobre F3 (766 KNOWN, 41 especies) + F4
(56 UNKNOWN, 2 especies): AUROC=0.6248, umbral congelado τ@95%KAR=39.35,
FAR=91% (hallazgo crítico pendiente de resolver). Ver nota completa:
[[05_OPEN_SET/FASE_13_CALIBRACION_INDEPENDIENTE|Fase 13 — Calibración Independiente]]
y [[15_DECISIONS/DECISION_LOG|Decisión C-16]].

La distinción near-OOD/far-OOD descrita abajo **no se implementó tal cual**:
Fase 13 usó un único corpus UNKNOWN (2 especies catalogadas pero fuera del
clasificador visual), no una partición near/far explícita. Sigue siendo una
brecha metodológica real frente al protocolo original.

## Propósito y estado (protocolo original, parcialmente vigente)
El sistema debe distinguir especies conocidas de observaciones que no pertenecen al catálogo. La fuente metodológica exige separar **near-OOD** (otro anuro parecido) de **far-OOD** (hoja, insecto u objeto no anuro); promediarlos ocultaría la dificultad real. Esta separación near/far sigue sin implementarse (ver actualización arriba).

## Protocolo respaldado por las fuentes
1. Construir un conjunto de validación y test con conocidos, near-OOD y far-OOD separados.
2. Calibrar temperatura y umbral únicamente en validación; nunca mirar el test para fijarlo.
3. Comparar MSP como línea base, temperature scaling, energy score y distancia de embeddings/Mahalanobis.
4. Reportar AUROC y FPR@95TPR por separado para near/far, además de exactitud en conocidos.
5. Si la confianza queda por debajo del umbral, mostrar “desconocido” y solicitar más evidencia (otra vista, audio o contexto), no forzar una especie.

## Lo que ya existe y cómo se conecta
- BioCLIP produce embeddings reutilizables para clasificación, búsqueda vectorial y detección de desconocidos: [Modelo BioCLIP](../04 Desarrollo Técnico/Modelo de Visión — BioCLIP.md).
- La Ruta B k-NN ya fue medida: con 41 especies dio 53,9 % Top-1 en 1-NN y 56,4 % con k=5; con paquete Antioquia de 25 especies dio 66,2 % Top-1 y 83,7 % Top-3 sobre 467 imágenes. Esto no es aún open-set, pero aporta la infraestructura de distancia y paquetes regionales: [Experimentos](../05 Evaluación y Métricas/Experimentos y Resultados.md), EXP-014/015.
- `antioquia_v1.sqlite` contiene 2.073 vectores y 25 especies; su filtrado regional reduce candidatos plausibles y mejora el reconocimiento, pero no reemplaza el umbral explícito de desconocido: [Base Vectorial](../05_OPEN_SET/INDEX.md).
- El prior GPS puede elevar Top-1 de 57 % a 81 %, pero está definido como prior, nunca como filtro. Un lugar no debe convertir una especie fuera de rango en imposible: [Arquitectura multimodal](../02 Metodología/Arquitectura Multimodal.md).

## Resultado y limitaciones
**Resultado actual (post-Fase 13):** AUROC=0.6248 y umbral operativo congelado
τ=39.35 (@95%KAR) medidos ciegamente sobre F3+F4. Persisten limitaciones reales:
FAR=91% (el sistema acepta la mayoría de UNKNOWN como KNOWN), sin separación
near-OOD/far-OOD, y solo 9/41 especies con calibración independiente (32/41
usan referencia estructural desde TRAIN). Las cifras de clasificación k-NN
anteriores (53,9%–66,2% Top-1) siguen sin ser detección open-set — son tareas
distintas. Ver [[05_OPEN_SET/FASE_13_CALIBRACION_INDEPENDIENTE|Fase 13]] para detalle completo.

## Fuentes
[Open-Set Recognition](../02 Metodología/Open-Set Recognition.md) · [Métricas offline](../05 Evaluación y Métricas/Métricas Offline.md) · [Decisiones](../15_DECISIONS/DECISION_LOG.md)



