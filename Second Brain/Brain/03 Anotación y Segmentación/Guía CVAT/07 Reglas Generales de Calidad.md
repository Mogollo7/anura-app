---
title: "Reglas Generales de Calidad"
tipo: guía
proyecto: Anura
fuente: "Guia_CVAT_Anuro.docx (v1.0)"
tags: [anura, cvat, anotación, segmentación]
---

# Reglas Generales de Calidad

â† [[06 Flujo de Trabajo Operativo]] · [[Guía CVAT â€” àndice]] · [[08 Glosario de Términos Anatómicos]] â†’

- Ajuste: ajusta los polígonos al borde real de la estructura anatómica, sin incluir fondo innecesario ni recortar la estructura.

- Oclusiones: si una estructura está parcialmente cubierta por vegetación u otra parte del cuerpo, delimita àºnicamente la porción realmente visible â€” no "completes" el contorno adivinando la parte oculta.

- Consistencia de lado: asigna siempre izquierdo/derecho tomando como referencia la perspectiva anatómica del espécimen (como si fueras la rana mirando hacia adelante), nunca la perspectiva de la cámara.

- No inventar datos: ante cualquier duda genuina, usa el valor no_determinable / no_evaluable / no_aplica correspondiente en vez de forzar una respuesta.

- Un paquete de imágenes por especie comparte características físicas: si estás anotando varias fotos del mismo individuo o de la misma sesión, los rasgos anatómicos estables (forma de hocico, tipo de glándulas) deberían ser consistentes entre esas imágenes â€” una discrepancia es señal de revisar el criterio, no de que la rana cambió de forma.



