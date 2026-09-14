---
title: "Evaluación en Campo Real"
proyecto: Anura
tipo: evaluación
estado: protocolo-propuesto
tags: [anura, evaluación, campo, piloto, usabilidad]
---

# Evaluación en Campo Real

[[Anura â€” àndice General]] · [[Evaluación y Métricas â€” àndice]] · [[Reportes de Pruebas Piloto]] · [[App Móvil]] · [[Consideraciones Ecológicas y Éticas]]

> [!abstract] Por qué es una evaluación distinta
> Las [[Métricas Offline|métricas offline]] miden el modelo sobre fotos que alguien ya seleccionó. El campo mide **el sistema completo**: la app, la batería, la persona con guantes mojados a las 11 de la noche, la rana que no se queda quieta. Los nàºmeros serán peores que en test, y esa diferencia es en sí misma un resultado científico relevante.

## 1. Diseño del piloto

| Parámetro | Propuesta |
| --- | --- |
| **Lugares** | â‰¥ 2 localidades contrastantes de las ya trabajadas (Antioquia: San Rafael / Caracolí; Guaviare: Serranía de La Lindosa) |
| **Duración** | 3â€“5 salidas nocturnas por localidad |
| **Participantes** | 6â€“10, mezclando perfiles (ver §2) |
| **Registros objetivo** | â‰¥ 150 observaciones con verdad de referencia |
| **Dispositivos** | Al menos 3 modelos distintos, incluyendo gama baja |
| **Condiciones** | Diurnas y nocturnas; con y sin lluvia reciente; con y sin cobertura de red |

**La verdad de referencia la establece un herpetólogo en el momento**, no la app. Sin identificación experta independiente y registrada en campo, no hay evaluación posible â€” solo una recopilación de lo que dijo el modelo.

## 2. Perfiles de participante

Cada perfil revela problemas distintos, y mezclarlos en un solo promedio oculta ambos:

| Perfil | Qué se evalàºa |
| --- | --- |
| Usuario comàºn sin formación | ¿Entiende el resultado? ¿Toma fotos utilizables? (HU-01) |
| Estudiante de biología | ¿Sustituye o complementa la clave dicotómica? |
| Herpetólogo | ¿Confía en la evidencia mostrada? ¿La refutación es usable? (HU-03) |

## 3. Criterios de éxito

Definidos **antes** de empezar, no después de ver los resultados.

| Criterio | Objetivo | Fuente |
| --- | --- | --- |
| Top-3 accuracy en campo | â‰¥ 85 % | RNF-04 |
| Top-1 accuracy en campo | â‰¥ 70 % | Objetivo operativo |
| Tiempo de inferencia | â‰¤ 4 s (p95) | RNF-02 |
| Tasa de fallo de la app | < 2 % de las capturas | â€” |
| Consumo de batería | â‰¤ 5 %/hora | RNF-09 |
| Operatividad sin red | 100 % de funciones | RNF-10 |
| Sincronización sin pérdida | 100 % de registros | RF-13 |
| Detección de desconocidos | â‰¥ 80 % de las especies fuera de catálogo | [[Open-Set Recognition]] |
| Satisfacción (SUS) | â‰¥ 70 | Cuestionario estándar |

## 4. Qué se registra en la app durante el piloto

Instrumentación mínima, por observación:

- Identificación del modelo (Top-3 + confianzas) y **identificación del experto**
- Tiempos: captura â†’ resultado, desglosado por etapa
- Versión de app, modelo y paquete regional
- Dispositivo, nivel de batería al inicio y al final de la sesión
- Condiciones: hora, luz, clima, microhábitat
- Nº de reintentos de foto antes de aceptar un resultado
- Si el usuario consultó la ficha técnica y cuánto tiempo
- Si refutó el resultado y qué región anatómica señaló

El **nàºmero de reintentos** es una métrica infravalorada: mide la fricción real. Un sistema que acierta al tercer intento tiene 100 % de acierto en la métrica y una mala experiencia en la práctica.

## 5. Consentimiento y privacidad

- Consentimiento informado por escrito de los participantes (uso de datos, fotos, grabaciones).
- Las coordenadas de especies amenazadas UICN se ofuscan en cualquier salida pàºblica (RNF-13).
- Los datos personales de los participantes se disocian de las observaciones para el análisis.
- Si el piloto forma parte de un trabajo de grado, revisar si requiere aval del comité de ética institucional. **Conviene consultarlo antes de recoger datos**, no después.
- Permisos de acceso y colecta segàºn la normativa ambiental colombiana aplicable â†’ [[Consideraciones Ecológicas y Éticas]].

## 6. Manejo de casos difíciles

| Caso | Protocolo |
| --- | --- |
| El experto tampoco está seguro | Registrar como `sp.` con nivel alcanzado; no forzar verdad de referencia |
| Especie fuera del catálogo | Caso valioso: verifica el open-set en condiciones reales |
| Discrepancia experto â†” modelo | Fotografiar el carácter diagnóstico en detalle para análisis posterior |
| Animal que escapa antes de la foto | Registrar como observación sin imagen (dato ecológico igualmente) |
| Solo hay canto, sin avistamiento | Prueba directa de la rama acàºstica |

Los casos difíciles **no son ruido a descartar**: son la parte más informativa del piloto y alimentan directamente [[Matrices de Confusión]] y el conjunto open-set.

## 7. Análisis posterior

1. Métricas de campo vs. métricas offline: **cuantificar la caída** y explicarla.
2. Errores por condición: ¿nocturnas peor que diurnas? ¿lluvia? ¿sustrato?
3. Errores por dispositivo: ¿la gama baja degrada precisión o solo velocidad?
4. Diferencias por perfil de usuario.
5. Retroalimentación al dataset: cada foto de campo mal clasificada es material de entrenamiento futuro â€” respetando la separación de splits.

> [!important] La caída offline â†’ campo es un resultado, no un fracaso
> Casi todos los sistemas de identificación biológica publicados rinden peor en campo que en test. Medirlo y explicarlo honestamente es más valioso â€” y más defendible en una sustentación â€” que presentar solo el nàºmero de laboratorio.

Ver también: [[Reportes de Pruebas Piloto]] · [[Historias de Usuario]] · [[Riesgos del Proyecto]]



