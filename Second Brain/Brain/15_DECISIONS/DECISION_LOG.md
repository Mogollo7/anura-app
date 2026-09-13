# Registro de decisiones técnicas

Decisiones extraídas de los Markdown de la bóveda. **Adoptada** significa que existe una elección explícita; **descartada** que la evidencia la cerró negativamente; **pendiente** que no hay experimento o aprobación final. Las fechas son las que aparecen en las fuentes.

| ID | Fecha/fuente | Decisión | Estado y evidencia |
| --- | --- | --- | --- |
| C-2 | fuente de arquitectura; revisada 2026-09-12 | Usar BioCLIP como backbone visual del servidor, sustituyendo EfficientNet-B0 | **ADOPTADA**. [Modelo BioCLIP](../04 Desarrollo Técnico/Modelo de Visión — BioCLIP.md) y Plan de Acción. |
| C-5 | antecedente citado; confirmado EXP-006/010, 2026-09-12 | No desplegar INT8 estándar en ViT; mantener FP16 | **DESCARTADA INT8 / ADOPTADA FP16**. INT8 dinámico −5,4 pp; estático 3,5–8,2 % o falla de memoria. |
| C-7 | 2026-09-08, Modelo BioCLIP §8 | Audio tendrá modelo acústico dedicado, no backbone visual compartido | **ADOPTADA**, aún sin entrenamiento ni métrica. |
| C-10 | 2026-09-12, Experimentos | No usar MobileNetV3-Small destilado como modelo on-device | **DESCARTADA**: 57,7 % teacher → 24,3 % student. |
| C-11 | roadmap y notas de implementación | Priorizar núcleo visual/offline antes de audio, comunidad y funcionalidades futuras | **ADOPTADA** como orden de alcance; app y piloto aún no están demostrados. |
| C-13 | 2026-09-12, EXP-011 | El resultado negativo de segmentación a 41 especies corresponde al segmentador binario, no al semántico de 16 regiones | **ADOPTADA** como aclaración de evidencia. La variante C requiere reentrenamiento para concluir. |
| C-15 | 2026-09-13, EXP-014/015 | Mantener ruta B k-NN con paquetes regionales; no reemplaza sin más al clasificador global | **ADOPTADA CONDICIONALMENTE**. Antioquia: +11,8 pp Top-1 sobre el clasificador de 41 clases; falta integración móvil. |
| — | 2026-09-12, EXP-007 | Combinar prior geográfico suavizado con peso `w=0,75` | **ADOPTADA** para implementación; 57 % → 81 % en test completo, +15,3 pp en aislado. |
| — | 2026-09-12, EXP-008/009 | Artefacto de producción ONNX FP16; medir dispositivo por RAM/latencia | **ADOPTADA**: 165,6 MB, 100 % predicciones idénticas; ~405 MB pico, 403 ms/1 hilo y 154 ms/4 hilos. |
| — | Open-Set Recognition §3–4 | Elegir umbral solo en validación y reportar near-OOD/far-OOD separados | **POLÍTICA ADOPTADA**, resultados aún pendientes. |
| C-16 | 2026-09-13, Fase 13 | Umbral Open Set congelado mediante Mahalanobis Ledoit-Wolf (M5), calibrado en CALIBRATION, evaluado ciego en F3+F4 | **ADOPTADA CONDICIONALMENTE**. τ@95%KAR=39.35 congelado, pero FAR=91% (muy permisivo). Candidato piloto τ@90%KAR=35.36 pendiente de validación de campo en Antioquia. Ver [[05_OPEN_SET/FASE_13_CALIBRACION_INDEPENDIENTE\|Fase 13 — Calibración Independiente]]. |

## Decisiones no cerradas
QAT para reducir tamaño, reentrenamiento de variante C, arquitectura acústica concreta, **umbral open-set de producción (39.35 vs 35.36, pendiente de validación de campo)**, validación de SQLite-vec en dispositivo, y catálogo regional definitivo. Ver [Inconsistencias y decisiones pendientes](../07 Notas de Trabajo/Inconsistencias y Decisiones Pendientes.md).



