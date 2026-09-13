---
title: "EvaluaciÃ³n en Campo Real"
proyecto: Anura
tipo: evaluaciÃ³n
estado: protocolo-propuesto
tags: [anura, evaluaciÃ³n, campo, piloto, usabilidad]
---

# EvaluaciÃ³n en Campo Real

[[Anura â€” Ãndice General]] Â· [[EvaluaciÃ³n y MÃ©tricas â€” Ãndice]] Â· [[Reportes de Pruebas Piloto]] Â· [[App MÃ³vil]] Â· [[Consideraciones EcolÃ³gicas y Ã‰ticas]]

> [!abstract] Por quÃ© es una evaluaciÃ³n distinta
> Las [[MÃ©tricas Offline|mÃ©tricas offline]] miden el modelo sobre fotos que alguien ya seleccionÃ³. El campo mide **el sistema completo**: la app, la baterÃ­a, la persona con guantes mojados a las 11 de la noche, la rana que no se queda quieta. Los nÃºmeros serÃ¡n peores que en test, y esa diferencia es en sÃ­ misma un resultado cientÃ­fico relevante.

## 1. DiseÃ±o del piloto

| ParÃ¡metro | Propuesta |
| --- | --- |
| **Lugares** | â‰¥ 2 localidades contrastantes de las ya trabajadas (Antioquia: San Rafael / CaracolÃ­; Guaviare: SerranÃ­a de La Lindosa) |
| **DuraciÃ³n** | 3â€“5 salidas nocturnas por localidad |
| **Participantes** | 6â€“10, mezclando perfiles (ver Â§2) |
| **Registros objetivo** | â‰¥ 150 observaciones con verdad de referencia |
| **Dispositivos** | Al menos 3 modelos distintos, incluyendo gama baja |
| **Condiciones** | Diurnas y nocturnas; con y sin lluvia reciente; con y sin cobertura de red |

**La verdad de referencia la establece un herpetÃ³logo en el momento**, no la app. Sin identificaciÃ³n experta independiente y registrada en campo, no hay evaluaciÃ³n posible â€” solo una recopilaciÃ³n de lo que dijo el modelo.

## 2. Perfiles de participante

Cada perfil revela problemas distintos, y mezclarlos en un solo promedio oculta ambos:

| Perfil | QuÃ© se evalÃºa |
| --- | --- |
| Usuario comÃºn sin formaciÃ³n | Â¿Entiende el resultado? Â¿Toma fotos utilizables? (HU-01) |
| Estudiante de biologÃ­a | Â¿Sustituye o complementa la clave dicotÃ³mica? |
| HerpetÃ³logo | Â¿ConfÃ­a en la evidencia mostrada? Â¿La refutaciÃ³n es usable? (HU-03) |

## 3. Criterios de Ã©xito

Definidos **antes** de empezar, no despuÃ©s de ver los resultados.

| Criterio | Objetivo | Fuente |
| --- | --- | --- |
| Top-3 accuracy en campo | â‰¥ 85 % | RNF-04 |
| Top-1 accuracy en campo | â‰¥ 70 % | Objetivo operativo |
| Tiempo de inferencia | â‰¤ 4 s (p95) | RNF-02 |
| Tasa de fallo de la app | < 2 % de las capturas | â€” |
| Consumo de baterÃ­a | â‰¤ 5 %/hora | RNF-09 |
| Operatividad sin red | 100 % de funciones | RNF-10 |
| SincronizaciÃ³n sin pÃ©rdida | 100 % de registros | RF-13 |
| DetecciÃ³n de desconocidos | â‰¥ 80 % de las especies fuera de catÃ¡logo | [[Open-Set Recognition]] |
| SatisfacciÃ³n (SUS) | â‰¥ 70 | Cuestionario estÃ¡ndar |

## 4. QuÃ© se registra en la app durante el piloto

InstrumentaciÃ³n mÃ­nima, por observaciÃ³n:

- IdentificaciÃ³n del modelo (Top-3 + confianzas) y **identificaciÃ³n del experto**
- Tiempos: captura â†’ resultado, desglosado por etapa
- VersiÃ³n de app, modelo y paquete regional
- Dispositivo, nivel de baterÃ­a al inicio y al final de la sesiÃ³n
- Condiciones: hora, luz, clima, microhÃ¡bitat
- NÂº de reintentos de foto antes de aceptar un resultado
- Si el usuario consultÃ³ la ficha tÃ©cnica y cuÃ¡nto tiempo
- Si refutÃ³ el resultado y quÃ© regiÃ³n anatÃ³mica seÃ±alÃ³

El **nÃºmero de reintentos** es una mÃ©trica infravalorada: mide la fricciÃ³n real. Un sistema que acierta al tercer intento tiene 100 % de acierto en la mÃ©trica y una mala experiencia en la prÃ¡ctica.

## 5. Consentimiento y privacidad

- Consentimiento informado por escrito de los participantes (uso de datos, fotos, grabaciones).
- Las coordenadas de especies amenazadas UICN se ofuscan en cualquier salida pÃºblica (RNF-13).
- Los datos personales de los participantes se disocian de las observaciones para el anÃ¡lisis.
- Si el piloto forma parte de un trabajo de grado, revisar si requiere aval del comitÃ© de Ã©tica institucional. **Conviene consultarlo antes de recoger datos**, no despuÃ©s.
- Permisos de acceso y colecta segÃºn la normativa ambiental colombiana aplicable â†’ [[Consideraciones EcolÃ³gicas y Ã‰ticas]].

## 6. Manejo de casos difÃ­ciles

| Caso | Protocolo |
| --- | --- |
| El experto tampoco estÃ¡ seguro | Registrar como `sp.` con nivel alcanzado; no forzar verdad de referencia |
| Especie fuera del catÃ¡logo | Caso valioso: verifica el open-set en condiciones reales |
| Discrepancia experto â†” modelo | Fotografiar el carÃ¡cter diagnÃ³stico en detalle para anÃ¡lisis posterior |
| Animal que escapa antes de la foto | Registrar como observaciÃ³n sin imagen (dato ecolÃ³gico igualmente) |
| Solo hay canto, sin avistamiento | Prueba directa de la rama acÃºstica |

Los casos difÃ­ciles **no son ruido a descartar**: son la parte mÃ¡s informativa del piloto y alimentan directamente [[Matrices de ConfusiÃ³n]] y el conjunto open-set.

## 7. AnÃ¡lisis posterior

1. MÃ©tricas de campo vs. mÃ©tricas offline: **cuantificar la caÃ­da** y explicarla.
2. Errores por condiciÃ³n: Â¿nocturnas peor que diurnas? Â¿lluvia? Â¿sustrato?
3. Errores por dispositivo: Â¿la gama baja degrada precisiÃ³n o solo velocidad?
4. Diferencias por perfil de usuario.
5. RetroalimentaciÃ³n al dataset: cada foto de campo mal clasificada es material de entrenamiento futuro â€” respetando la separaciÃ³n de splits.

> [!important] La caÃ­da offline â†’ campo es un resultado, no un fracaso
> Casi todos los sistemas de identificaciÃ³n biolÃ³gica publicados rinden peor en campo que en test. Medirlo y explicarlo honestamente es mÃ¡s valioso â€” y mÃ¡s defendible en una sustentaciÃ³n â€” que presentar solo el nÃºmero de laboratorio.

Ver tambiÃ©n: [[Reportes de Pruebas Piloto]] Â· [[Historias de Usuario]] Â· [[Riesgos del Proyecto]]



