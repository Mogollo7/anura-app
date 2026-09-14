---
title: "Reportes de Pruebas Piloto"
proyecto: Anura
tipo: evaluación
estado: plantilla
tags: [anura, evaluación, piloto, reportes]
---

# Reportes de Pruebas Piloto

[[Anura â€” àndice General]] · [[Evaluación y Métricas â€” àndice]] · [[Evaluación en Campo Real]]

Un reporte por salida. Copiar la plantilla y rellenar **el mismo día** â€” lo que no se anota esa noche se pierde.

## àndice de reportes

| # | Fecha | Lugar | Participantes | Versión app | Registros | Top-1 | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |

---

## Plantilla de reporte

```markdown
### Reporte PP-000 â€” [Localidad], [Fecha]

**Contexto**
- Lugar / coordenadas aproximadas:
- Fecha y franja horaria:
- Clima y condiciones: (temperatura, humedad, lluvia reciente, fase lunar)
- Participantes (perfil, no nombre): 
- Herpetólogo de referencia:
- Versión app / modelo / paquete regional:
- Dispositivos usados:

**Resultados cuantitativos**
| Métrica | Valor | Objetivo | ¿Cumple? |
| --- | --- | --- | --- |
| Observaciones registradas | | â‰¥ 30 | |
| Top-1 accuracy | | â‰¥ 70 % | |
| Top-3 accuracy | | â‰¥ 85 % | |
| Latencia media / p95 | | â‰¤ 4 s | |
| Fallos de la app | | < 2 % | |
| Batería consumida por hora | | â‰¤ 5 % | |
| Desconocidos detectados correctamente | | | |
| Reintentos de foto por observación | | | |

**Especies registradas**
| Especie (experto) | N | Aciertos Top-1 | Aciertos Top-3 | Observaciones |
| --- | --- | --- | --- | --- |

**Hallazgos**
1. 
2. 

**Problemas detectados**
| # | Descripción | Severidad | Componente | Acción |
| --- | --- | --- | --- | --- |
| | | crítica/alta/media/baja | app/modelo/datos/UX | |

**Citas de usuarios**
> 

**Casos difíciles para análisis posterior**
| Obs. ID | Especie real | Predicho | Por qué es interesante |
| --- | --- | --- | --- |

**Acciones siguientes**
- [ ] 
```

---

## Consolidado entre pilotos

Se actualiza tras cada salida; es la vista que muestra si el sistema mejora.

| Métrica | PP-001 | PP-002 | PP-003 | Tendencia |
| --- | --- | --- | --- | --- |
| Top-1 | | | | |
| Top-3 | | | | |
| Latencia p95 | | | | |
| Fallos | | | | |
| SUS | | | | |

### Problemas recurrentes

Los que aparecen en â‰¥ 2 pilotos. Son los que importan; un problema que aparece una vez puede ser anecdótico.

| Problema | Pilotos | Estado |
| --- | --- | --- |
| | | abierto / en curso / resuelto |

### Lecciones aprendidas

| Lección | Origen | Aplicada en |
| --- | --- | --- |
| | | |

Ver también: [[Experimentos y Resultados]] · [[Riesgos del Proyecto]]



