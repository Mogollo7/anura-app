---
title: "Consideraciones Ecológicas y Éticas"
proyecto: Anura
tipo: proyecto
estado: redactado-pendiente-validación-experta
tags: [anura, ética, bioseguridad, campo, conservación]
---

# Consideraciones Ecológicas y Éticas

[[Anura â€” àndice General]] · [[Evaluación en Campo Real]] · [[Estrategia de Construcción del Dataset]] · [[Riesgos del Proyecto]]

> [!warning] Validación pendiente
> Este documento recoge buenas prácticas ampliamente establecidas en trabajo de campo con anfibios, pero **debe ser revisado y ajustado por el herpetólogo del equipo y por la instancia institucional correspondiente** antes de aplicarse. Las referencias normativas colombianas están señaladas para verificación, no como afirmación jurídica.

## 1. Bioseguridad: la responsabilidad más seria del proyecto

Un proyecto que mueve gente entre humedales fotografiando anfibios **es un vector potencial de patógenos**. No es un riesgo teórico: la propia [[Bibliografía|bibliografía del proyecto]] documenta la presencia de *Batrachochytrium dendrobatidis* (Bd) en los Andes colombianos (Ruiz & Rueda-Almonacid, 2008; Flechas et al., 2013) y su papel en declives globales de anfibios (Fisher et al., 2009).

Sería una contradicción grave que un trabajo orientado a la conservación contribuyera a dispersar quitridiomicosis por descuido de campo.

### Protocolo mínimo entre localidades

| Momento | Acción |
| --- | --- |
| Antes de salir | Botas, equipo y material limpios y secos |
| **Entre cuerpos de agua o localidades** | Desinfectar calzado y equipo; retirar barro antes de desinfectar (la materia orgánica inactiva los desinfectantes) |
| Manipulación | **Guantes nuevos por individuo**, sin excepción. Un guante reutilizado entre dos ranas es exactamente el mecanismo de transmisión que se quiere evitar |
| Agua y sustrato | No trasladar agua, barro ni hojarasca entre sitios |
| Al terminar | Secado completo del equipo; el secado prolongado es en sí una medida eficaz |

Concretar el desinfectante, la concentración y el tiempo de contacto con el criterio del herpetólogo del equipo y las guías vigentes de bioseguridad en anfibios.

## 2. Manejo de los individuos

Principio rector: **la fotografía no justifica el estrés del animal**. La mayoría de los caracteres del esquema de anotación se pueden registrar sin manipulación o con manipulación mínima.

- **Preferir la fotografía in situ**, sin capturar, siempre que sea posible.
- Si hay manipulación: manos limpias y hàºmedas o guantes nuevos; tiempo mínimo; nunca sujetar por las extremidades.
- **Evitar el flash directo a los ojos**; la iluminación lateral o difusa da mejores fotos y molesta menos.
- **Liberar en el punto exacto de captura**, en el mismo microhábitat y la misma noche.
- No manipular individuos evidentemente enfermos, heridos o con signos de estrés, ni hembras con puesta.
- No manipular especies con secreciones cutáneas tóxicas (Dendrobatidae, Bufonidae) sin la precaución adecuada â€” riesgo para la persona y para el animal.
- Registrar cualquier incidente (escape, lesión, mortalidad accidental) en el reporte de la salida.

## 3. Perturbación del hábitat

- No remover hojarasca, troncos ni rocas más allá de lo imprescindible; devolver todo a su posición original.
- Circular por senderos existentes.
- Limitar la exposición lumínica: las linternas potentes alteran el comportamiento nocturno. Preferir luz roja o intensidad baja cuando sea viable â€” que además favorece la adaptación visual del observador ([[App Móvil]] §4).
- No usar reproducción de cantos (*playback*) para atraer individuos sin justificación metodológica: interfiere con el comportamiento reproductivo.

## 4. Marco legal y permisos

**A verificar con la institución antes de cualquier colecta o salida formal.** Elementos que normalmente aplican en Colombia:

- Permiso de recolección de especímenes de especies silvestres con fines de investigación científica (marco nacional, ANLA / autoridad ambiental competente).
- Autorización de la Corporación Autónoma Regional correspondiente al área de trabajo.
- Permiso del propietario o de la comunidad si el predio es privado o territorio colectivo.
- Aval del comité de ética o de investigación de la institución cuando el trabajo lo requiera.
- Normativa aplicable si se trabaja en áreas protegidas del SINAP.

El uso de fotografías de terceros (iNaturalist, GBIF) obliga además a respetar la **licencia de cada imagen**: no todas permiten uso derivado o comercial. Es un asunto de cumplimiento, no de cortesía, y afecta directamente a la distribución de la app ([[Riesgos del Proyecto]]).

## 5. Datos sensibles: la ubicación de especies amenazadas

El RNF-13 exige ofuscar (1â€“5 km) las coordenadas de especies amenazadas UICN en vistas pàºblicas. La razón es concreta: **la publicación abierta de localidades precisas de especies raras facilita la extracción ilegal**, un problema documentado en anfibios de colores llamativos como los Dendrobatidae â€” precisamente uno de los grupos del dataset.

Reglas prácticas:

- La coordenada real se conserva para investigación; lo que se controla es **quién puede verla**.
- La ofuscación se aplica en la serialización de la API, no manualmente ([[API Backend]] §5).
- Al exportar a GBIF/SiB (HU-05), usar los campos de incertidumbre geográfica y las políticas de sensibilidad del propio estándar Darwin Core.
- Ante la duda con una especie concreta, **ofuscar por defecto**.

## 6. Ética de la herramienta

Consideraciones propias de un sistema de IA aplicado a biodiversidad, que conviene dejar por escrito en el documento de grado:

- **Anura es apoyo, no autoridad taxonómica.** Ya está afirmado en el [[Referente Teórico]] y debe reflejarse en la interfaz: el resultado es una predicción, no una determinación. El [[Open-Set Recognition|rechazo de desconocidos]] es parte de esa honestidad.
- **Riesgo de erosión del conocimiento experto**: una herramienta que da respuestas rápidas puede desincentivar el aprendizaje de claves taxonómicas. Mitigación deliberada: la explicación por caracteres anatómicos (RF-06) enseña *por qué*, en vez de solo dar un nombre â€” es la diferencia entre una herramienta que sustituye y una que forma.
- **Riesgo de seguridad para el usuario**: la HU-01 promete indicar si una especie es peligrosa. Un falso "inofensiva" tiene consecuencias físicas. Umbral conservador y advertencia ante incertidumbre ([[Matrices de Confusión]] §5).
- **Contribución de datos**: los usuarios deben saber qué pasa con sus observaciones, y las validaciones de los expertos deben quedar acreditadas.

## 7. Indicadores de impacto del proyecto

Para argumentar el valor del trabajo con evidencia y no con intenciones:

| Indicador | Cómo se mide |
| --- | --- |
| Registros àºtiles generados | Nº de observaciones validadas incorporadas a bases de biodiversidad |
| Registros exportados a GBIF / SiB Colombia | Nº de paquetes DwC publicados |
| Reducción de tiempo de identificación | Comparación con clave dicotómica en el piloto |
| Cobertura geográfica | Nº de localidades y municipios con registros nuevos |
| Especies raras o poco registradas documentadas | Nº de registros de especies con pocos datos previos |
| Uso formativo | Nº de estudiantes o cursos que la emplean |
| Apoyo a decisiones de conservación o reubicación | Casos documentados |

## Referencias

- Fisher, Garner & Walker (2009). *Global emergence of Batrachochytrium dendrobatidis and amphibian chytridiomycosis*. [doi:10.1016/j.tim.2009.03.006](https://doi.org/10.1016/j.tim.2009.03.006)
- Flechas et al. (2013). *Characterization of the first Bd isolate from the Colombian Andes*. [doi:10.1007/s10393-013-0830-7](https://doi.org/10.1007/s10393-013-0830-7)
- Scheele et al. (2021). *Conservation translocations for amphibian species threatened by chytrid fungus*. [doi:10.1111/csp2.524](https://doi.org/10.1111/csp2.524)
- Luedtke et al. (2023). *Ongoing declines for the world's amphibians*. [doi:10.1038/s41586-023-06578-4](https://doi.org/10.1038/s41586-023-06578-4)

Ver también: [[Bibliografía]]



