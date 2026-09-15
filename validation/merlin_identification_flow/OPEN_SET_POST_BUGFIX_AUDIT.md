# Re-auditoría de Open Set tras el bugfix `DYNAMIC_REMOVE_SPECIES_FAIL`

Fecha: 2026-09-14
Threshold usado: **39.35406371422803** — el release histórico, **intacto**.
**No se recalibró nada.** No se generaron embeddings nuevos.

Script: `run_open_set_post_bugfix_audit.py` → `open_set_post_bugfix_metrics.json`

---

## 1. Respuesta directa a la pregunta

> ¿El bugfix cambia las métricas de Open Set, o el defecto general persiste?

**El defecto general persiste. Con el catálogo completo activo, las métricas son
idénticas a las de antes del bugfix.**

La hipótesis previa se confirma: el bugfix corrige un fallo de **arquitectura de
catálogo** (qué centroides participan), no mejora la **separabilidad del
embedding** ni la calidad del threshold. Son dos defectos independientes, y solo
uno está arreglado.

Esto no es una decepción del arreglo: eran dos problemas distintos que estaban
mezclados. Ahora están separados, y el que queda está medido.

---

## 2. Lo que el bugfix SÍ corrige, medido

Imagen: `data cleaned/Dendrobates_truncatus/col_obs_135615735_photo_231331908.jpg`
(la especie real solo se usa *después*, para interpretar; nunca entra al runtime).

| Configuración | Mahalanobis mín. | `nearest_species_id` | Centroides activos |
|---|---|---|---|
| *Dendrobates truncatus* **activo** | **25.0126** | `ANU_COL_DEND_TRU_001` | 34 |
| *Dendrobates truncatus* **desactivado** | **38.8330** | `ANU_COL_DEND_TRI_001` | 17 |

**Δ = +13.82.** Antes del bugfix este número no se movía: el centroide del
release seguía presente pasara lo que pasara, y la puntuación se quedaba clavada
en 25.0126. La fuga de catálogo está cerrada y es verificable.

## 3. Lo que el bugfix NO corrige

La decisión sigue siendo `ESPECIE_CONOCIDA` incluso con la especie desactivada,
porque 38.8330 < 39.35406. La causa está medida: para esa imagen, **13 de los 41
centroides del release caen por debajo del threshold**.

Distancias Mahalanobis a los centroides más cercanos:

```
25.013  ANU_COL_DEND_TRU_001  Dendrobates truncatus     <- la especie real
38.619  ANU_COL_DEND_MOL_001  Dendropsophus molitor
38.833  ANU_COL_DEND_TRI_001  Dendropsophus triangulum
38.953  ANU_COL_DEND_EBR_001  Dendropsophus ebraccatus
38.970  ANU_COL_SCIN_RUB_001  Scinax ruber
38.977  ANU_COL_PRIS_PER_001  Pristimantis permixtus
...
                                        threshold = 39.354
```

El centroide correcto es un outlier claro (25.0 frente a una banda compacta en
38.6–41). El threshold calibrado a KAR-95 % cae **dentro** de esa banda, así que
acepta un tercio del catálogo para esta imagen. Desactivar una especie elimina
su centroide, pero el vecino de al lado vuelve a aceptar.

**No se recalibra el threshold** (regla dura). Se reporta tal cual.

---

## 4. Métricas operacionales tras el bugfix

KNOWN: `validation/fase16_clean_open_set/clean_known_embeddings.npz` (7 475).
UNKNOWN: `validation/fase23a_open_set_automatic/embeddings/unknown_embeddings.npz` (620).
En cada configuración, una especie inactiva deja de contar como KNOWN: ya no
pertenece a ese catálogo.

| Configuración | Centroides | KNOWN eval. | KAR | FAR | UDR | AUROC |
|---|---|---|---|---|---|---|
| `FULL_RELEASE_POOL_41` (≡ pre-bugfix) | 41 | 7 475 | 0.8239 | **0.8500** | 0.1500 | **0.5380** |
| `ACTIVE_ANTIOQUIA+CAUCA_34` | 34 | 7 434 | 0.8222 | 0.8242 | 0.1758 | 0.5491 |
| `ACTIVE_CAUCA_ONLY_17` | 17 | 4 073 | 0.7574 | 0.8113 | 0.1887 | **0.4618** |

### Histórico vs operacional actual

| Fuente | FAR |
|---|---|
| Fase 16 (histórico) | ≈ 0.939 |
| Fase 20 (histórico) | ≈ 0.911 |
| Fase 23A (histórico) | ≈ 0.754 |
| `visual_catalog/v1.0.0` `evidence_summary` (histórico) | 0.9107 (AUROC 0.6248, KAR 0.8538) |
| **Operacional post-bugfix, catálogo completo (41)** | **0.8500** (AUROC 0.5380, KAR 0.8239) |

**Advertencia de comparabilidad, para no sacar la conclusión equivocada:** las
cifras históricas provienen de poblaciones y protocolos distintos entre sí (por
eso van de 75 % a 94 %). La fila operacional usa una combinación KNOWN/UNKNOWN
concreta y no es intercambiable con ninguna de ellas. La diferencia entre 0.9107
y 0.8500 refleja el cambio de población evaluada, **no una mejora producida por
el bugfix**. Comparadas correctamente —misma población, mismo threshold, mismo
código, con el catálogo completo activo— las métricas antes y después del
bugfix son **idénticas**, porque con 41 especies activas el conjunto de
centroides es exactamente el mismo.

### Lectura honesta de los números

- **AUROC 0.538** con el catálogo completo está muy cerca del azar (0.5). El
  espacio de embedding, tal como está, casi no separa KNOWN de UNKNOWN por
  distancia Mahalanobis al centroide más cercano.
- **FAR 0.85**: cinco de cada seis imágenes de especies no registradas se
  aceptarían como conocidas. Inaceptable para producción.
- Reducir el catálogo activo **no arregla el Open Set**. Pasar de 41 a 17
  centroides baja FAR solo de 0.850 a 0.811, y el AUROC cae a **0.4618**, es
  decir, *por debajo* del azar. Las medias lo explican: con 17 centroides la
  media KNOWN (34.78) supera a la media UNKNOWN (33.67), porque muchos KNOWN
  quedan lejos de los pocos centroides que sobreviven. Los paquetes regionales
  son útiles para el producto (menos ruido en el ranking, menos peso), pero
  **no deben venderse como mitigación del Open Set**.

---

## 5. Conclusión

1. El bug de arquitectura de catálogo está **corregido y verificado**: un
   centroide desactivado deja de participar (Δ +13.82 en el caso medido), y sin
   especies activas nunca se emite `ESPECIE_CONOCIDA`.
2. El defecto de Open Set **persiste sin cambios**: AUROC ≈ 0.54, FAR ≈ 0.85 con
   el threshold histórico. El sistema **no está listo para producción** en su
   función de rechazo.
3. `NO_REGISTRADA` sigue sin poder emitirse automáticamente, y esta auditoría lo
   refuerza: con AUROC 0.54 no hay evidencia para sostener esa afirmación.
4. Lo que haría falta (fuera del alcance de este trabajo y explícitamente **no**
   ejecutado): mejorar la representación (segmentación, fine-tuning, métrica
   aprendida), no mover el umbral. Recalibrar solo intercambiaría KAR por FAR a
   lo largo de una curva ROC que ya es casi diagonal.
