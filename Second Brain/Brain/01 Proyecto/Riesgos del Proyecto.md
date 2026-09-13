---
title: "Riesgos del Proyecto"
proyecto: Anura
tipo: proyecto
estado: redactado
tags: [anura, riesgos, gestiÃ³n]
---

# Riesgos del Proyecto

[[Anura â€” Ãndice General]] Â· [[Cronograma y Plan de Trabajo]] Â· [[Inconsistencias y Decisiones Pendientes]] Â· [[Infraestructura]]

Escala: **P** = probabilidad (Alta/Media/Baja) Â· **I** = impacto (Alto/Medio/Bajo). Prioridad = P Ã— I.

## 1. Riesgos tÃ©cnicos

| # | Riesgo | P | I | MitigaciÃ³n | Plan B |
| --- | --- | --- | --- | --- | --- |
| T-1 | **BioCLIP no cabe en 150 MB** tras cuantizar sin perder precisiÃ³n aceptable (RNF-05) | M | **A** | Medir INT8 pronto, no al final; recortar el codificador de texto | DestilaciÃ³n a backbone menor; modo hÃ­brido con red |
| T-2 | ~~Qdrant no funciona embebido en mÃ³vil~~ â†’ **Resuelto**: se sustituye por ObjectBox en el dispositivo | B | M | Validar ObjectBox en el dispositivo de referencia antes de integrarlo en producciÃ³n | BÃºsqueda vectorial por fuerza bruta sobre pocos miles de vectores (viable si ObjectBox fallara) |
| T-3 | Latencia > 4 s en gama baja (RNF-02) | M | M | Elegir dispositivo de referencia realista desde el inicio | Bajar resoluciÃ³n; delegados de hardware |
| T-4 | SegmentaciÃ³n de 16 clases poco fiable con pocas anotaciones | **A** | M | Empezar con clases agrupadas; preanotar y corregir | Reducir a las regiones mÃ¡s diagnÃ³sticas y estables |
| T-5 | DegradaciÃ³n fuerte por cuantizaciÃ³n del ViT | M | M | Pesos INT8 + activaciones FP16; medir siempre | FP16 completo y recortar en otro sitio |
| T-6 | BaterÃ­a > 5 %/hora (RNF-09) | M | M | GPS puntual, no continuo; liberar modelos | Modo ahorro con audio desactivado |
| T-7 | Deriva entre embeddings de mÃ³vil y servidor (versiones distintas) | M | **A** | VersiÃ³n del modelo en el manifiesto; recalcular en servidor si difiere | Un solo modelo en ambos lados |

## 2. Riesgos de datos

| # | Riesgo | P | I | MitigaciÃ³n | Plan B |
| --- | --- | --- | --- | --- | --- |
| D-1 | **Fuga de informaciÃ³n en el split** infla los resultados | M | **A** | `GroupSplit` por individuo y localidad. La Etapa I ya aplicÃ³ esto correctamente (70 individuos/especie, split por individuo, segmentaciÃ³n binaria previa) â€” el riesgo real es **no repetir la misma disciplina al escalar el catÃ¡logo** | Rehacer la evaluaciÃ³n y corregir las cifras publicadas |
| D-2 | Etiquetas errÃ³neas, especialmente en *Pristimantis* | M | **A** | VerificaciÃ³n experta antes de entrenar; revisar los pares mÃ¡s confundidos | Excluir temporalmente las especies dudosas |
| D-3 | **No alcanzar 70 individuos/especie** en varias especies | **A** | M | Complementar con GBIF/iNaturalist con control de calidad. **Actualizado (2026-09-05):** el riesgo no se materializÃ³ para el clasificador â€” el catÃ¡logo de 28 especies del prototipo llega con **70 individuos/especie** para el modelo de identificaciÃ³n, el requisito original, cumplido. El modelo de segmentaciÃ³n anatÃ³mica usa **25â€“30 imÃ¡genes/especie**, dentro del rango 20â€“40 ya previsto para el segmentador en I-5 (es un modelo distinto, con un requisito de volumen menor, no un dÃ©ficit del mismo dataset) | Si alguna especie puntual se queda corta, reducir el catÃ¡logo o completar con fuente secundaria; mantener `GroupSplit` por individuo en ambos conjuntos, identificaciÃ³n y segmentaciÃ³n |
| D-4 | Sesgo geogrÃ¡fico o de fondo (*shortcut learning*) | **A** | M | Diversificar fondos; validar con localidades no vistas | Entrenar sobre recortes segmentados en vez de imagen completa |
| D-5 | Datos de audio insuficientes para entrenar la rama acÃºstica | **A** | M | Al reutilizar BioCLIP (sin entrenar un backbone de audio desde cero) el volumen necesario baja, pero sigue haciendo falta suficiente audio para calibrar y validar; usar AnuraSet como referencia externa | Aplazar el audio a una fase posterior y declararlo en el alcance |
| D-6 | **PÃ©rdida de las anotaciones de CVAT** o de las fotos de campo | B | **CrÃ­tico** | Exportar y respaldar periÃ³dicamente, fuera de la herramienta | No hay: el dato de campo es irrepetible |
| D-7 | Licencias incompatibles en imÃ¡genes de terceros | M | M | Verificar licencia por imagen antes de incorporarla | Excluir las no compatibles |

> [!danger] D-6 no tiene plan B
> Es el Ãºnico riesgo del proyecto sin recuperaciÃ³n posible. Las copias de seguridad deben existir **antes** de la prÃ³xima salida de campo, no despuÃ©s de la primera pÃ©rdida. Ver [[Infraestructura]] Â§6.

## 3. Riesgos de alcance y planificaciÃ³n

| # | Riesgo | P | I | MitigaciÃ³n | Plan B |
| --- | --- | --- | --- | --- | --- |
| P-1 | **Alcance excesivo para un trabajo de grado**: visiÃ³n + audio + contexto + segmentaciÃ³n + open-set + app offline + web comunitaria | **A** | **A** | Priorizar: nÃºcleo visual + offline es lo defendible; el resto, "trabajo futuro" | Recortar audio y mÃ³dulo comunitario |
| P-2 | Fase 2 (mÃ³vil) sin tiempo tras la Fase 1 | **A** | **A** | Empezar la app con un modelo provisional, en paralelo | Demostrador mÃ³vil funcional con alcance reducido |
| P-3 | Dependencia de disponibilidad del herpetÃ³logo para validar | M | **A** | Agendar las validaciones como hitos, no como favores | ValidaciÃ³n asÃ­ncrona por lotes documentados |
| P-4 | DocumentaciÃ³n desincronizada del cÃ³digo | **A** | M | Esta bÃ³veda como fuente Ãºnica; registrar decisiones al tomarlas | â€” |

> [!important] P-1 es el riesgo mÃ¡s probable de todos
> El proyecto documentado es ambicioso incluso para un equipo profesional. La conversaciÃ³n honesta a tener pronto: **cuÃ¡l es el nÃºcleo mÃ­nimo defendible** y quÃ© se declara explÃ­citamente como trabajo futuro. Recortar por decisiÃ³n es muy distinto de quedarse a medias por falta de tiempo, y solo lo primero se puede defender en una sustentaciÃ³n.

## 4. Riesgos operativos, legales y Ã©ticos

| # | Riesgo | P | I | MitigaciÃ³n |
| --- | --- | --- | --- | --- |
| O-1 | Permisos de investigaciÃ³n/colecta no tramitados a tiempo | M | **A** | Iniciar los trÃ¡mites con antelaciÃ³n â†’ [[Consideraciones EcolÃ³gicas y Ã‰ticas]] |
| O-2 | DispersiÃ³n accidental de Bd entre localidades | M | **A** | Protocolo de bioseguridad obligatorio y verificado |
| O-3 | FiltraciÃ³n de coordenadas de especies amenazadas (RNF-13) | M | **A** | OfuscaciÃ³n aplicada en serializaciÃ³n, no manual |
| O-4 | Falso "inofensiva" en especie tÃ³xica (HU-01) | B | **A** | Umbral conservador; advertir ante incertidumbre |
| O-5 | Coste de infraestructura por encima del presupuesto | M | M | Capas gratuitas; CPU en vez de GPU; alarma de gasto |
| O-6 | Uso de la app para localizar especies con fines de extracciÃ³n | B | **A** | OfuscaciÃ³n + no publicar rutas de muestreo detalladas |

## 5. Top a vigilar

Los que decidirÃ­an el resultado del proyecto. T-2 se retira de esta lista: ya estÃ¡ resuelto (ObjectBox).

1. **P-1** â€” alcance excesivo â†’ definir el nÃºcleo mÃ­nimo defendible.
2. **D-6** â€” pÃ©rdida de datos de campo â†’ copias de seguridad ahora (sigue sin plan B).
3. **T-1** â€” tamaÃ±o del modelo â†’ medir la cuantizaciÃ³n de BioCLIP cuanto antes.
4. **D-1** â€” mantener la disciplina de `GroupSplit` + segmentaciÃ³n binaria al escalar el catÃ¡logo, no repetir el rigor de la Etapa I por casualidad.
5. **D-3** â€” cumplido para identificaciÃ³n (70/especie); vigilar solo las especies puntuales que se queden cortas al escalar el catÃ¡logo mÃ¡s allÃ¡ de las 28 actuales.

## 6. Registro de materializaciÃ³n

Cuando un riesgo ocurre, se anota. Sirve para ajustar las estimaciones y para la secciÃ³n de dificultades del documento.

| Fecha | Riesgo | QuÃ© pasÃ³ | Impacto real | Respuesta |
| --- | --- | --- | --- | --- |
| | | | | |



