---
title: "Riesgos del Proyecto"
proyecto: Anura
tipo: proyecto
estado: redactado
tags: [anura, riesgos, gestión]
---

# Riesgos del Proyecto

[[Anura â€” àndice General]] · [[Cronograma y Plan de Trabajo]] · [[Inconsistencias y Decisiones Pendientes]] · [[Infraestructura]]

Escala: **P** = probabilidad (Alta/Media/Baja) · **I** = impacto (Alto/Medio/Bajo). Prioridad = P à— I.

## 1. Riesgos técnicos

| # | Riesgo | P | I | Mitigación | Plan B |
| --- | --- | --- | --- | --- | --- |
| T-1 | **BioCLIP no cabe en 150 MB** tras cuantizar sin perder precisión aceptable (RNF-05) | M | **A** | Medir INT8 pronto, no al final; recortar el codificador de texto | Destilación a backbone menor; modo híbrido con red |
| T-2 | ~~Qdrant no funciona embebido en móvil~~ â†’ **Resuelto**: se sustituye por ObjectBox en el dispositivo | B | M | Validar ObjectBox en el dispositivo de referencia antes de integrarlo en producción | Bàºsqueda vectorial por fuerza bruta sobre pocos miles de vectores (viable si ObjectBox fallara) |
| T-3 | Latencia > 4 s en gama baja (RNF-02) | M | M | Elegir dispositivo de referencia realista desde el inicio | Bajar resolución; delegados de hardware |
| T-4 | Segmentación de 16 clases poco fiable con pocas anotaciones | **A** | M | Empezar con clases agrupadas; preanotar y corregir | Reducir a las regiones más diagnósticas y estables |
| T-5 | Degradación fuerte por cuantización del ViT | M | M | Pesos INT8 + activaciones FP16; medir siempre | FP16 completo y recortar en otro sitio |
| T-6 | Batería > 5 %/hora (RNF-09) | M | M | GPS puntual, no continuo; liberar modelos | Modo ahorro con audio desactivado |
| T-7 | Deriva entre embeddings de móvil y servidor (versiones distintas) | M | **A** | Versión del modelo en el manifiesto; recalcular en servidor si difiere | Un solo modelo en ambos lados |

## 2. Riesgos de datos

| # | Riesgo | P | I | Mitigación | Plan B |
| --- | --- | --- | --- | --- | --- |
| D-1 | **Fuga de información en el split** infla los resultados | M | **A** | `GroupSplit` por individuo y localidad. La Etapa I ya aplicó esto correctamente (70 individuos/especie, split por individuo, segmentación binaria previa) â€” el riesgo real es **no repetir la misma disciplina al escalar el catálogo** | Rehacer la evaluación y corregir las cifras publicadas |
| D-2 | Etiquetas erróneas, especialmente en *Pristimantis* | M | **A** | Verificación experta antes de entrenar; revisar los pares más confundidos | Excluir temporalmente las especies dudosas |
| D-3 | **No alcanzar 70 individuos/especie** en varias especies | **A** | M | Complementar con GBIF/iNaturalist con control de calidad. **Actualizado (2026-09-05):** el riesgo no se materializó para el clasificador â€” el catálogo de 28 especies del prototipo llega con **70 individuos/especie** para el modelo de identificación, el requisito original, cumplido. El modelo de segmentación anatómica usa **25â€“30 imágenes/especie**, dentro del rango 20â€“40 ya previsto para el segmentador en I-5 (es un modelo distinto, con un requisito de volumen menor, no un déficit del mismo dataset) | Si alguna especie puntual se queda corta, reducir el catálogo o completar con fuente secundaria; mantener `GroupSplit` por individuo en ambos conjuntos, identificación y segmentación |
| D-4 | Sesgo geográfico o de fondo (*shortcut learning*) | **A** | M | Diversificar fondos; validar con localidades no vistas | Entrenar sobre recortes segmentados en vez de imagen completa |
| D-5 | Datos de audio insuficientes para entrenar la rama acàºstica | **A** | M | Al reutilizar BioCLIP (sin entrenar un backbone de audio desde cero) el volumen necesario baja, pero sigue haciendo falta suficiente audio para calibrar y validar; usar AnuraSet como referencia externa | Aplazar el audio a una fase posterior y declararlo en el alcance |
| D-6 | **Pérdida de las anotaciones de CVAT** o de las fotos de campo | B | **Crítico** | Exportar y respaldar periódicamente, fuera de la herramienta | No hay: el dato de campo es irrepetible |
| D-7 | Licencias incompatibles en imágenes de terceros | M | M | Verificar licencia por imagen antes de incorporarla | Excluir las no compatibles |

> [!danger] D-6 no tiene plan B
> Es el àºnico riesgo del proyecto sin recuperación posible. Las copias de seguridad deben existir **antes** de la próxima salida de campo, no después de la primera pérdida. Ver [[Infraestructura]] §6.

## 3. Riesgos de alcance y planificación

| # | Riesgo | P | I | Mitigación | Plan B |
| --- | --- | --- | --- | --- | --- |
| P-1 | **Alcance excesivo para un trabajo de grado**: visión + audio + contexto + segmentación + open-set + app offline + web comunitaria | **A** | **A** | Priorizar: nàºcleo visual + offline es lo defendible; el resto, "trabajo futuro" | Recortar audio y módulo comunitario |
| P-2 | Fase 2 (móvil) sin tiempo tras la Fase 1 | **A** | **A** | Empezar la app con un modelo provisional, en paralelo | Demostrador móvil funcional con alcance reducido |
| P-3 | Dependencia de disponibilidad del herpetólogo para validar | M | **A** | Agendar las validaciones como hitos, no como favores | Validación asíncrona por lotes documentados |
| P-4 | Documentación desincronizada del código | **A** | M | Esta bóveda como fuente àºnica; registrar decisiones al tomarlas | â€” |

> [!important] P-1 es el riesgo más probable de todos
> El proyecto documentado es ambicioso incluso para un equipo profesional. La conversación honesta a tener pronto: **cuál es el nàºcleo mínimo defendible** y qué se declara explícitamente como trabajo futuro. Recortar por decisión es muy distinto de quedarse a medias por falta de tiempo, y solo lo primero se puede defender en una sustentación.

## 4. Riesgos operativos, legales y éticos

| # | Riesgo | P | I | Mitigación |
| --- | --- | --- | --- | --- |
| O-1 | Permisos de investigación/colecta no tramitados a tiempo | M | **A** | Iniciar los trámites con antelación â†’ [[Consideraciones Ecológicas y Éticas]] |
| O-2 | Dispersión accidental de Bd entre localidades | M | **A** | Protocolo de bioseguridad obligatorio y verificado |
| O-3 | Filtración de coordenadas de especies amenazadas (RNF-13) | M | **A** | Ofuscación aplicada en serialización, no manual |
| O-4 | Falso "inofensiva" en especie tóxica (HU-01) | B | **A** | Umbral conservador; advertir ante incertidumbre |
| O-5 | Coste de infraestructura por encima del presupuesto | M | M | Capas gratuitas; CPU en vez de GPU; alarma de gasto |
| O-6 | Uso de la app para localizar especies con fines de extracción | B | **A** | Ofuscación + no publicar rutas de muestreo detalladas |

## 5. Top a vigilar

Los que decidirían el resultado del proyecto. T-2 se retira de esta lista: ya está resuelto (ObjectBox).

1. **P-1** â€” alcance excesivo â†’ definir el nàºcleo mínimo defendible.
2. **D-6** â€” pérdida de datos de campo â†’ copias de seguridad ahora (sigue sin plan B).
3. **T-1** â€” tamaño del modelo â†’ medir la cuantización de BioCLIP cuanto antes.
4. **D-1** â€” mantener la disciplina de `GroupSplit` + segmentación binaria al escalar el catálogo, no repetir el rigor de la Etapa I por casualidad.
5. **D-3** â€” cumplido para identificación (70/especie); vigilar solo las especies puntuales que se queden cortas al escalar el catálogo más allá de las 28 actuales.

## 6. Registro de materialización

Cuando un riesgo ocurre, se anota. Sirve para ajustar las estimaciones y para la sección de dificultades del documento.

| Fecha | Riesgo | Qué pasó | Impacto real | Respuesta |
| --- | --- | --- | --- | --- |
| | | | | |



