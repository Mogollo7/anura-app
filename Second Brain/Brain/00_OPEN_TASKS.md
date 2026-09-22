# Tareas abiertas

Prioridad solo según urgencia explícita, dependencia bloqueante o riesgo documentado. No se inventan prioridades.

## URGENTE
- [ ] Crear copias de seguridad externas de fotos y anotaciones CVAT antes de la próxima salida; D-6 no tiene plan B. Fuente: [Riesgos](./01 Proyecto/Riesgos del Proyecto.md).
- [ ] Mantener congelado y auditar el split `GroupSplit` por individuo/localidad al escalar el catálogo; una fuga invalidaría las cifras. Fuente: [Estrategia de dataset](./02 Metodología/Estrategia de Construcción del Dataset.md).

## ALTA
- [x] Implementar el prior GPS `w=0,75` en Kotlin y validar que no actúe como filtro — hecho
  2026-09-22 (`KnnVote.candidates(neighbors, geoPrior)`, `PackageVectorIndex.zoneIdFor/zonePrior`).
  Nota: el número medido en el paquete real fue Top-1 **62.9%→72.5%** (+9.6pp, control de fuga,
  167 imágenes de prueba, `COLOMBIA_ANURA/ANTIOQUIA/reports/packages_v1.0.0.json`), distinto del
  +24,9pp de EXP-007 citado aquí antes — EXP-007 midió sobre otro conjunto/condición, no se
  reconcilió cuál es la cifra "oficial" a citar de aquí en adelante.
- [x] Integrar `encoder_anura_fp16.onnx` y `antioquia_v1.sqlite` (ONNX + sqlite-vec) en el
  dispositivo — hecho en sesiones previas (`AnuraIdentifier`/`PackageVectorIndex`/`ImageEncoder`).
  Falta medir latencia/RAM en dispositivo real (pendiente al 2026-09-22, teléfono no siempre
  disponible durante el desarrollo).
- [x] Prior de clima (temperatura/humedad) por especie vía Open-Meteo — integrado 2026-09-22
  pese a evidencia débil (+3.9pp Top-1, n=129, señal frágil) por pedido explícito, no por pasar
  la barra de confiabilidad del prior de zona. Introduce una dependencia de red en tiempo de
  identificación (rompe el diseño offline-first parcialmente). Ver
  [[02 Metodología/Contexto del Paso a Paso — Datos Faltantes]] §Temperatura/Humedad.
  Validar en campo si de verdad ayuda o si conviene revertir.
- [ ] Reentrenar la variante C desde cero con componente conexo mayor y fondo negro; EXP-011–013 solo evaluaron transformaciones en un modelo entrenado con variante A.
- [ ] Revisar manualmente las 50 candidatas de alta confianza de manejo/amplexo generadas por EXP-004.
- [ ] Ejecutar evaluación open-set near/far y congelar umbral en validación; reportar AUROC y FPR@95TPR.

## MEDIA
- [ ] Completar anotación/entrenamiento de segmentación semántica de 16 regiones y medir sus métricas.
- [ ] Implementar el esqueleto Android offline, guardado local, sincronización diferida y búsqueda regional.
- [ ] Definir y medir la rama acústica dedicada; no reutilizar resultados visuales como evidencia de audio.
- [ ] Repetir métricas por especie y ablaciones multimodales en el conjunto congelado.

## BAJA
- [ ] Evaluar QAT si el presupuesto de 150 MB exige algo menor que FP16.
- [ ] Completar audio, módulo comunitario, exportación Darwin Core, iOS y ampliación a 911 especies, explícitamente fuera del alcance mínimo.

## BLOQUEADO
- [ ] Piloto de campo en al menos dos localidades: no hay reportes PP-001/PP-002 con datos.
- [ ] Cierre de la arquitectura acústica: falta experimento y diseño final.
- [ ] Umbral open-set operativo: falta corpus near/far versionado y resultados.

## Trazabilidad
[Estado](./00_PROJECT_STATE.md) · [Decisiones](./15_DECISIONS/DECISION_LOG.md) · [Resultados](./06_EVALUATION/RESULTS_INDEX.md) · [Riesgos](./01 Proyecto/Riesgos del Proyecto.md)



