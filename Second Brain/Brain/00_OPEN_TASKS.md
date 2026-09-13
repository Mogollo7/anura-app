# Tareas abiertas

Prioridad solo según urgencia explícita, dependencia bloqueante o riesgo documentado. No se inventan prioridades.

## URGENTE
- [ ] Crear copias de seguridad externas de fotos y anotaciones CVAT antes de la próxima salida; D-6 no tiene plan B. Fuente: [Riesgos](./01 Proyecto/Riesgos del Proyecto.md).
- [ ] Mantener congelado y auditar el split `GroupSplit` por individuo/localidad al escalar el catálogo; una fuga invalidaría las cifras. Fuente: [Estrategia de dataset](./02 Metodología/Estrategia de Construcción del Dataset.md).

## ALTA
- [ ] Implementar el prior GPS `w=0,75` en Kotlin y validar que no actúe como filtro. EXP-007 ya midió +24,9 pp global y +15,3 pp en aislado.
- [ ] Integrar `encoder_anura_fp16.onnx` y `antioquia_v1.sqlite` en el dispositivo; medir latencia, RAM, tamaño y sincronización de versión.
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



