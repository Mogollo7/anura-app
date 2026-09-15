# ANURA AI FREEZE REPORT

## 1. Estado general

**AI_FREEZE_FAILED**

`AI_FREEZE_READY = NO`  
`AI_LOGIC_FREEZE = NO`  
`MOBILE_RUNTIME_FREEZE = NO`

La arquitectura está encapsulada y el flujo funcional existe, pero hay dos fallos críticos demostrados: el Open Set oficial acepta UNKNOWN con una tasa inaceptable en la evidencia disponible y una especie retirada puede seguir obteniendo una decisión de especie conocida.

## 2. Gate results

| Gate | Resultado | Evidencia |
|---|---|---|
| 1 — Integridad BioCLIP móvil | BLOCKED | ONNX FP16 real y SHA verificados en desktop. Existe scaffold Kotlin/ONNX Runtime, pero no hay Gradle/wrapper, APK, modelo empaquetado ni paridad Android↔OpenCLIP. |
| 2 — Open Set real | FAIL | Blind Fase 16: AUROC 0.5928, FAR 0.9388, UDR 0.0612. Fase 20: FAR 0.9107 al threshold oficial. Fase 23A: FAR 0.754 en UNKNOWN automático. |
| 3 — Agregar especie | PARTIAL | Lifecycle y membership por release simulados pasan; el fixture de especie sintética no puede aprobar taxonomía/evaluación Open Set ciega. No hay demostración real de imagen D aceptada por un release validado. |
| 4 — Eliminar especie | FAIL | Tras retirar `Dendrobates truncatus` del catálogo activo en memoria, su imagen produjo `ESPECIE_CONOCIDA` con Mahalanobis 25.013 < 39.354. |
| 5 — Reproducibilidad | PASS | Tres ejecuciones offline de los 6 E2E tuvieron el mismo resultado serializado; los 10 tests deterministas también pasan. |
| 6 — Offline | PARTIAL | E2E desktop pasa con HF offline y artefactos locales/cacheados. Android no ha sido empaquetado ni ejecutado; el primer E2E normal emitió aviso de HF Hub. |
| 7 — Stress móvil | BLOCKED | No existe runtime móvil ejecutable. Solo hay mediciones históricas desktop y tamaño ONNX 173.4 MB. |
| 8 — Contrato Kotlin | PARTIAL | Tipos y frontera `IdentificationRequest → IdentificationEngine → IdentificationResult` existen en el scaffold, sin compilación Android. |
| Prueba E2E | PARTIAL | 6/6 funcionales: conocida GEO compatible, GEO incompatible, sin GEO, UNKNOWN y Top-1 no automático. No cubre un caso ambiguo independiente ni alta/baja real completa. |

## 3. BioCLIP

El runtime de referencia ejecutó `encoder_anura_fp16.onnx` mediante ONNX Runtime CPU, con SHA-256 `219e860e6fa9a80fb30a59fc8f61911421bbd53a4537dca831803d3ab446b2ad`, entrada Float32 NCHW 1×3×224×224 y salida L2 512D. El origen PyTorch `bioclip_anura_mejor.pt` tiene el SHA independiente `98a6c54d6edb27e2b0344b8bbbaebd2ab749b1bf5136991ff73b37f66ee2c1ac`.

La compatibilidad Android no está demostrada. El adaptador Kotlin preparado verifica el ONNX y prepara el tensor, pero su escalado debe validarse por paridad contra el transform exacto de OpenCLIP y el proyecto no se ha compilado.

## 4. Open Set

La decisión runtime usa Mahalanobis con threshold congelado `39.35406371422803`; los rechazos se traducen correctamente a `NO_CONCLUYENTE`, no a `NO_REGISTRADA`. El E2E UNKNOWN fue rechazado correctamente en un ejemplo (`44.406 > 39.354`), pero eso no compensa las métricas de evaluación:

- Fase 16 blind: AUROC 0.5928, FAR 0.9388, UDR 0.0612.
- Fase 20 diagnóstico con threshold oficial: FAR 0.9107, AUROC 0.5920.
- Fase 23A, encoder corregido: FAR 0.754 para Mahalanobis oficial en UNKNOWN automático.

**OPEN_SET_GATE_FAIL.** El threshold no fue cambiado para hacer pasar el gate. `NO_REGISTRADA` sigue correctamente no productivo.

## 5. Catálogo dinámico

Alta: el mecanismo de ID/lifecycle y membership por release pasa para fixtures aislados. El candidate sintético demuestra ensamblado de embeddings/prototipo, pero su evaluación honesta falla/PENDIENTE por taxonomía sintética y ausencia de blind/Open Set propios. Por tanto no prueba alta productiva de D.

Baja: **DYNAMIC_REMOVE_SPECIES_FAIL.** La ruta de ranking filtra la especie retirada, pero `OpenSetReleaseAdapter` conserva los centroides del release congelado. La imagen retirada fue aceptada como conocida y reasignada a otros candidatos. La frontera de catálogo debe versionarse de forma coherente con centroides, covarianza y threshold antes de congelar.

## 6. Offline

| Componente | Estado |
|---|---|
| ONNX desktop, ranking, GEO local, taxonomía y Open Set | OFFLINE_READY en el entorno auditado, con los artefactos presentes |
| Transform OpenCLIP del E2E desktop | OFFLINE_READY después de cache local; primera ejecución normal mostró aviso de HF Hub |
| GEO fuera de Antioquia | OFFLINE_PARTIAL: continúa sin GEO, no se consulta red |
| Runtime Android completo | OFFLINE_PARTIAL: aún no se empaquetó/compiló/ejecutó |

## 7. Reproducibilidad

Los 10 tests deterministas y tres repeticiones de la suite E2E offline pasaron. El JSON final fue idéntico entre repeticiones; los tiempos no se usaron como criterio. Esto valida estabilidad del flujo actual, no su calidad Open Set.

## 8. Stress

No hay estrés Android ejecutable. El ONNX FP16 ocupa 173,414,601 bytes; el paquete vectorial regional auditado declara 3,881 vectores de 512D y 8.72 MB. Las mediciones históricas de `requisitos_movil.json` pertenecen a otro modelo/clasificador y no se presentan como benchmark del encoder Merlin Android.

## 9. Kotlin contract

El scaffold `android-merlin-identification` mantiene la UI desacoplada: `IdentificationRequest`, `IdentificationEngine` e `IdentificationResult` no exponen BioCLIP, embedding, GEO, centroides ni Open Set. La validación de contrato prohíbe emitir `NO_REGISTRADA` sin evidencia explícita. Estado: estructuralmente correcto, no compilado ni integrado en cliente real.

## 10. Integridad metodológica

- No se usó `ground_truth_species` dentro de las llamadas de inferencia E2E; se comprueba su ausencia en el resultado serializado.
- El valor GEO ≈0.701 no se usó. La referencia honesta documentada es ≈0.617 sin oracle; ranking usa solo `w_geo_rank=0.3` experimental.
- No se modificaron thresholds, datasets, pesos, encoder, embeddings, centroides ni artefactos GEO históricos.
- La prueba de eliminación eligió una imagen conocida únicamente como etiqueta posterior de evaluación; el pipeline recibió imagen, evidencia anuro y artefactos, no la especie real.

## 11. Problemas pendientes

1. Corregir la frontera de releases para que retirar una especie elimine simultáneamente su capacidad de aceptación Open Set o, como mínimo, fuerce `NO_CONCLUYENTE`.
2. Obtener evidencia Open Set independiente que satisfaga un rechazo de UNKNOWN aceptable sin recalibración oportunista. El release actual no alcanza ese gate.
3. Compilar y ejecutar el runtime Android con el ONNX empaquetado y una prueba de paridad de preprocesamiento contra el runtime de referencia.
4. Validar una alta de especie real con taxonomía, datos suficientes y evaluación independiente.

## 12. Decisión

**¿Podemos dejar tranquila la IA y comenzar Kotlin? No.**

Bloqueos que deben resolverse antes:

1. **Open Set:** el mecanismo actual no rechaza UNKNOWN de forma suficiente en las evaluaciones disponibles.
2. **Eliminación dinámica:** una especie retirada aún puede inducir `ESPECIE_CONOCIDA` por centroides Open Set antiguos.
3. **Runtime móvil:** falta compilación, ejecución y paridad de preprocesamiento Android.
