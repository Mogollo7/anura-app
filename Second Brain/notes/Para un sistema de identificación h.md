Para un sistema de identificación herpetológica en campo (especialmente cuando se busca diferenciar especies con vectores de características muy cercanos), los datos de contexto actúan como un filtro bayesiano o de probabilidad prior.
Un modelo de visión por computadora puede dudar entre dos especies crípticas con un 90\% de similitud morfológica, pero el contexto geográfico y ecológico suele reducir el espacio de búsqueda a una sola opción biológicamente viable.
A continuación se presentan los datos de contexto fundamentales, clasificados por su grado de importancia, facilidad de captura y el rol que juegan en el pipeline de identificación:
Tabla de Variables de Contexto y su Impacto
| Variable | Importancia | Captura (¿Quién/Cómo?) | Impacto en el Modelo de IA |
|---|---|---|---|
| 1. Ubicación (GPS) | 🔴 Crítica (10/10) | 🤖 Automática (Sensor GPS del celular) | Filtra el paquete geográfico de especies presentes en la zona. |
| 2. Altitud (msnm) | 🔴 Crítica (10/10) | 🤖 Automática (API de elevación / GPS) | Restringe por pisos térmicos y rangos altitudinales conocidos. |
| 3. Fecha y Hora / Temporada | 🟡 Alta (8/10) | 🤖 Automática (Reloj del sistema) | Determina patrones de actividad (diurna/nocturna) y época de lluvias/reproducción. |
| 4. Microhábitat / Sustrato | 🟡 Alta (8/10) | 👤 Manual (Selección rápida con chips) | Modifica las probabilidades prior según la ecología de la especie. |
| 5. Registro de Canto (Bioacústica) | 🟢 Absoluta (10/10) | 👤 / 🤖 Manual/Audio (Grabación corta) | Desempata especies morfológicamente idénticas (especies gemelas/complejos). |
| 6. Tamaño Aproximado (LRC) | 🔵 Media (6/10) | 👤 Manual (Categoría o slider simple) | Separa estados juveniles de especies grandes vs. adultos de especies pigmeas. |
Detalle de las Variables Fundamentales
1. Ubicación Geográfica (Coordenadas Lat/Long)
 * Grado de importancia: 10 / 10
 * Mecanismo: El sensor del smartphone captura la ubicación sin intervención del usuario (incluso offline si las coordenadas quedaron guardadas en el GPS).
 * Uso en el sistema: Es la clave para cargar en memoria el Paquete Geográfico correspondiente (ej. un shapefile o polígono de distribución de especies). Si la especie A vive únicamente en la Cordillera Central y la especie B en la Costa Pacífica, el sistema descarta instantáneamente a la especie B sin importar la foto.
2. Altitud (Metros sobre el nivel del mar - msnm)
 * Grado de importancia: 10 / 10
 * Mecanismo: Se calcula automáticamente cruzando las coordenadas GPS con un modelo digital de elevación (DEM) almacenado en la app offline, o mediante el barómetro/GPS integrado.
 * Uso en el sistema: En la neotrópica (especialmente en países como Colombia), la altitud determina barreras ecológicas estrictas. Especies del género Pristimantis o Dendropsophus suelen estar fuertemente estratificadas por franjas altitudinales (ej. 1000\text{--}1500\text{ msnm} vs. >2500\text{ msnm}).
3. Microhábitat y Sustrato
 * Grado de importancia: 8 / 10
 * Mecanismo: El usuario selecciona una opción en un menú tipo Chip de un solo toque:
   * [En hoja/vegetación] [En hojarasca/suelo] [Cerca a quebrada/agua] [En roca] [Bajo corteza/tronco]
 * Uso en el sistema: Modifica los pesos de la distribución de probabilidad (Prior Probability). Una rana arbórea e n un riachuelo tiene una matriz de probabilidades muy distinta a una rana fossorial o terrestre hallada bajo troncos en descomposición.
4. Patrón de Actividad (Hora y Temporada)
 * Grado de importancia: 8 / 10
 * Mecanismo: Leído automáticamente desde el sistema del dispositivo.
 * Uso en el sistema: Distingue entre especies estrictamente nocturnas (que pueden encontrarse inactivas/ocultas de día con patrones de coloración de reposo) y especies dendrobátidas diurnas con coloraciones aposemáticas. Además, relaciona la presencia con temporadas de lluvias (época de mayor despliegue reproductor).
5. Señal Bioacústica (Si está disponible)
 * Grado de importancia: 10 / 10 (Para desempaquetar complejos de especies)
 * Mecanismo: Grabación corta de audio de 3 a 5 segundos desde el micrófono.
 * Uso en el sistema: En herpetología, muchas especies son cripticas (invisibles al ojo por ser genéticamente diferentes pero visualmente casi idénticas). El canto de anuncio es el mecanismo evolutivo primario de aislamiento reproductivo. Si la foto genera dudas entre la especie X y la especie Y, el espectrograma del audio desempata la identificación con precisión absoluta.
Integración en la Arquitectura de tu Modelo
Para combinar la información de la imagen con estos datos contextuales sin distorsionar el extractor visual (BioCLIP), el enfoque más robusto es una Arquitectura Multimodal con Fusión Tardía (Late Fusion) o un Filtro Bayesiano Post-Inferencia:
 * Fase 1 (Filtro Geográfico/Altitudinal): El GPS y la altitud reducen la matriz global a la lista corta del paquete geográfico local (K especies).
 * Fase 2 (Similitud Visual): BioCLIP 1 calcula las distancias cosenoidales contra los centroides de esas K especies.
 * Fase 3 (Ponderación Contextual): Se aplican penalizaciones o bonificaciones si el microhábitat seleccionado o la hora coinciden con el perfil ecológico de la especie.