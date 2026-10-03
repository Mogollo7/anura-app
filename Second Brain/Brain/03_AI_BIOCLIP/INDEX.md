# 03_AI_BIOCLIP: consolidación del modelo

## Rol y arquitectura vigente
BioCLIP es el extractor visual del servidor: transforma la imagen en un embedding para cabezas jerárquicas, búsqueda por similitud y open-set. La propuesta histórica de EfficientNet-B0 quedó sustituida. El checkpoint vigente para 41 especies usa **variante A, imagen completa**, no recorte binario.

## Evidencia experimental
- EXP-001 (2026-09-11): Top-1 test 35,3 % zero-shot → 44,2 % con cabezas → 57,0 % con fine-tuning; se adopta `bioclip_anura_mejor.pt`.
- EXP-002/003: clases escasas 53,1 % frente a abundantes 56,7 %; revisión de 97 fallos atribuyó el problema principal a similitud morfológica de *Dendropsophus*, y eliminó una foto de amplexo y una de manejo.
- EXP-006: FP16 56,8→56,7 %; INT8 dinámico −5,4 puntos y sin ventaja suficiente. EXP-010: INT8 estático entre 3,5 % y 8,2 % o fallo de memoria.
- EXP-007: prior GPS `w=0,75`, 57 %→81 % Top-1 global y +15,3 pp en test geográficamente aislado.
- EXP-008/009: `anura_clasificador_fp16.onnx` (165,6 MB), predicciones 100 % idénticas a PyTorch; ~405 MB pico, 403 ms a 1 hilo y 154 ms a 4 hilos.
- EXP-011–013: la segmentación binaria no sostuvo el resultado al escalar; en evaluación pareada de 150 imágenes, completa 60,7 %, zoom 50,7 %, fondo negro 44,7 %. Falta reentrenar con la distribución de recorte antes de concluir.
- EXP-014/015: k-NN regional Antioquia (25 especies) 66,2 % Top-1 y 83,7 % Top-3; `encoder_anura_fp16.onnx` validado con similitud coseno 0,999999 en 64 imágenes.

## Decisiones de despliegue
FP16 es el formato aceptado; INT8 estándar y MobileNetV3 destilado están descartados. Audio se diseña como rama dedicada, todavía sin arquitectura final ni resultados. BioCLIP v1 y v2 no mezclan embeddings: el índice y el dispositivo deben compartir versión.

## Pendientes y límites
Reentrenar variante C con componente conexo mayor y fondo enmascarado; documentar formalmente el segmentador binario de Etapa I; medir open-set; integrar prior GPS y paquetes regionales en Kotlin; validar tamaño, RAM, batería y latencia en dispositivo real. La Etapa I (~99 % con 10 especies) no se extrapola a las 41 especies.

## Fuentes
[Modelo completo](../04 Desarrollo Técnico/Modelo de Visión — BioCLIP.md) · [Bitácora](../05 Evaluación y Métricas/Experimentos y Resultados.md) · [Estado](../00_PROJECT_STATE.md)



