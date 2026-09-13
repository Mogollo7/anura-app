---
title: "Reglas Generales de Calidad"
tipo: guÃ­a
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotaciÃ³n, segmentaciÃ³n]
---

# Reglas Generales de Calidad

â† [[06 Flujo de Trabajo Operativo]] Â· [[GuÃ­a CVAT â€” Ãndice]] Â· [[08 Glosario de TÃ©rminos AnatÃ³micos]] â†’

- Ajuste: ajusta los polÃ­gonos al borde real de la estructura anatÃ³mica, sin incluir fondo innecesario ni recortar la estructura.

- Oclusiones: si una estructura estÃ¡ parcialmente cubierta por vegetaciÃ³n u otra parte del cuerpo, delimita Ãºnicamente la porciÃ³n realmente visible â€” no â€œcompletesâ€ el contorno adivinando la parte oculta.

- Consistencia de lado: asigna siempre izquierdo/derecho tomando como referencia la perspectiva anatÃ³mica del espÃ©cimen (como si fueras la rana mirando hacia adelante), nunca la perspectiva de la cÃ¡mara.

- No inventar datos: ante cualquier duda genuina, usa el valor no_determinable / no_evaluable / no_aplica correspondiente en vez de forzar una respuesta.

- Un paquete de imÃ¡genes por especie comparte caracterÃ­sticas fÃ­sicas: si estÃ¡s anotando varias fotos del mismo individuo o de la misma sesiÃ³n, los rasgos anatÃ³micos estables (forma de hocico, tipo de glÃ¡ndulas) deberÃ­an ser consistentes entre esas imÃ¡genes â€” una discrepancia es seÃ±al de revisar el criterio, no de que la rana cambiÃ³ de forma.



