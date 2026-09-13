---
title: "Reportes de Pruebas Piloto"
proyecto: Anura
tipo: evaluaciÃ³n
estado: plantilla
tags: [anura, evaluaciÃ³n, piloto, reportes]
---

# Reportes de Pruebas Piloto

[[Anura â€” Ãndice General]] Â· [[EvaluaciÃ³n y MÃ©tricas â€” Ãndice]] Â· [[EvaluaciÃ³n en Campo Real]]

Un reporte por salida. Copiar la plantilla y rellenar **el mismo dÃ­a** â€” lo que no se anota esa noche se pierde.

## Ãndice de reportes

| # | Fecha | Lugar | Participantes | VersiÃ³n app | Registros | Top-1 | Estado |
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
- HerpetÃ³logo de referencia:
- VersiÃ³n app / modelo / paquete regional:
- Dispositivos usados:

**Resultados cuantitativos**
| MÃ©trica | Valor | Objetivo | Â¿Cumple? |
| --- | --- | --- | --- |
| Observaciones registradas | | â‰¥ 30 | |
| Top-1 accuracy | | â‰¥ 70 % | |
| Top-3 accuracy | | â‰¥ 85 % | |
| Latencia media / p95 | | â‰¤ 4 s | |
| Fallos de la app | | < 2 % | |
| BaterÃ­a consumida por hora | | â‰¤ 5 % | |
| Desconocidos detectados correctamente | | | |
| Reintentos de foto por observaciÃ³n | | | |

**Especies registradas**
| Especie (experto) | N | Aciertos Top-1 | Aciertos Top-3 | Observaciones |
| --- | --- | --- | --- | --- |

**Hallazgos**
1. 
2. 

**Problemas detectados**
| # | DescripciÃ³n | Severidad | Componente | AcciÃ³n |
| --- | --- | --- | --- | --- |
| | | crÃ­tica/alta/media/baja | app/modelo/datos/UX | |

**Citas de usuarios**
> 

**Casos difÃ­ciles para anÃ¡lisis posterior**
| Obs. ID | Especie real | Predicho | Por quÃ© es interesante |
| --- | --- | --- | --- |

**Acciones siguientes**
- [ ] 
```

---

## Consolidado entre pilotos

Se actualiza tras cada salida; es la vista que muestra si el sistema mejora.

| MÃ©trica | PP-001 | PP-002 | PP-003 | Tendencia |
| --- | --- | --- | --- | --- |
| Top-1 | | | | |
| Top-3 | | | | |
| Latencia p95 | | | | |
| Fallos | | | | |
| SUS | | | | |

### Problemas recurrentes

Los que aparecen en â‰¥ 2 pilotos. Son los que importan; un problema que aparece una vez puede ser anecdÃ³tico.

| Problema | Pilotos | Estado |
| --- | --- | --- |
| | | abierto / en curso / resuelto |

### Lecciones aprendidas

| LecciÃ³n | Origen | Aplicada en |
| --- | --- | --- |
| | | |

Ver tambiÃ©n: [[Experimentos y Resultados]] Â· [[Riesgos del Proyecto]]



