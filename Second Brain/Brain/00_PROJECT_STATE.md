# Estado del proyecto Anura/SITRana

Corte de evidencia: 2026-09-13. Esta síntesis usa únicamente Markdown y artefactos descritos dentro de esta bóveda; los documentos originales no se modifican.

## ACTUAL
- **Modelo visual vigente:** BioCLIP fine-tuned sobre 41 especies, variante A (imagen completa). El checkpoint `bioclip_anura_mejor.pt` alcanza 57,0 % Top-1; fp16 conserva 56,7 % y el artefacto ONNX `anura_clasificador_fp16.onnx` produce predicciones idénticas a PyTorch en validación. Fuente: [Experimentos y Resultados](./05 Evaluación y Métricas/Experimentos y Resultados.md), EXP-001/006/008.
- **Mejor resultado documentado:** prior geográfico con peso `w=0,75` eleva Top-1 de 57 % a 81 % en el test completo y aporta +15,3 puntos en el subconjunto aislado >10 km (n=72). Fuente: [Experimentos y Resultados](./05 Evaluación y Métricas/Experimentos y Resultados.md), Hallazgo 2 y EXP-007.
- **Ruta regional vigente:** k-NN sobre embeddings con paquete Antioquia de 25 especies: 66,2 % Top-1 y 83,7 % Top-3 en 467 imágenes; `antioquia_v1.sqlite` contiene 2.073 vectores y pesa 6,39 MB. Fuente: EXP-015 y [Base Vectorial](./05_OPEN_SET/INDEX.md).
- **Evaluación ya realizada:** test de 766 imágenes, 3.260 embeddings de train para la referencia completa, 41 especies. Se mantiene separación por individuo/localidad cuando la fuente la declara.
- **Diseño preparado:** guía CVAT v1.0 con 16 etiquetas anatómicas; requisitos, historias de usuario, arquitectura multimodal, open-set y roadmap están documentados. La bóveda contiene 94 Markdown y el manifiesto conserva 502 fuentes inventariadas de la generación.

## HISTÓRICO
- La Etapa I, con 10 especies, 70 individuos por especie, segmentación binaria y `GroupSplit` por individuo, obtuvo aproximadamente 99 % de exactitud. Es evidencia válida para ese alcance, no una cifra transferible automáticamente a 41 especies.
- El salto de transferencia/fine-tuning sobre 41 especies fue 35,3 % zero-shot → 44,2 % solo cabezas → 57,0 % fine-tuning. La diferencia entre especies escasas y abundantes fue pequeña (53,1 % vs 56,7 %), por lo que el problema dominante se atribuye a confusiones morfológicas de *Dendropsophus*.
- INT8 dinámico perdió 5,4 puntos sin ventaja suficiente; tres intentos INT8 estáticos quedaron entre 3,5 % y 8,2 % o fallaron por memoria. FP16 es la compresión aceptada sin QAT.
- EXP-014 midió k-NN con las 41 especies (56,4 % Top-1, 77,9 % Top-3) y EXP-015 mostró que el paquete regional cambia la conclusión (+11,8 puntos contra el clasificador de 41 clases).

## DESCARTADO
- EfficientNet-B0 como backbone principal: propuesta histórica sustituida por BioCLIP.
- BioCLIP INT8 y cuantización estática estándar: degradación inutilizable; no se adopta sin quantization-aware training.
- Destilación a MobileNetV3-Small (C-10): 57,7 % teacher → 24,3 % student; descartada.
- Recorte/máscara binaria aplicado solo en inferencia: en 150 imágenes, imagen completa 60,7 %, zoom 50,7 %, fondo negro 44,7 %. No demuestra que la variante sea imposible, pero sí que el modelo debe reentrenarse con esa distribución.
- Audio con backbone visual compartido: la documentación vigente reserva un modelo acústico dedicado (aún sin resultado medido).

## PENDIENTE
- Implementar en Kotlin el prior GPS y probarlo dentro de la app.
- Reentrenar desde cero la variante C real (componente conexo mayor + fondo enmascarado) y compararla con A bajo el mismo split.
- Revisar manualmente las 50 candidatas de alta confianza de fotos de mano/amplexo generadas por EXP-004.
- Completar validación open-set (near-OOD y far-OOD separados), calibrar umbral en validación y reportar AUROC/FPR@95TPR.
- Integrar y medir `antioquia_v1.sqlite` en el dispositivo; documentar encoder ONNX y sincronización de versiones.
- Ejecutar las fases de app offline, audio y piloto de campo que las fuentes describen como futuras.

## BLOQUEADO
- Segmentación semántica de 16 regiones: la guía está definida, pero el modelo de volumen y su evaluación no están documentados como ejecutados.
- Rama acústica: arquitectura por definir y sin métricas en Markdown.
- Validación de campo: las plantillas existen, pero no hay reporte PP-001/PP-002 completado.
- Algunas decisiones de despliegue (QAT, catálogo regional definitivo, umbral open-set) requieren experimentos aún no registrados.

## Fuentes principales
[Mapa de conocimiento](./00_KNOWLEDGE_MAP.md) · [Resultados](./06_EVALUATION/RESULTS_INDEX.md) · [Decisiones](./15_DECISIONS/DECISION_LOG.md) · [Tareas abiertas](./00_OPEN_TASKS.md)



