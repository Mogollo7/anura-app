Implementar una estructura taxonómica jerárquica (familia, género y especie) combinada con **sqlite-vec** como base de datos vectorial local resuelve de manera elegante el problema del almacenamiento y la búsqueda offline en dispositivos móviles.

### **1\. Estructura de la Base de Datos SQLite con sqlite-vec**

Al estructurar las tablas en SQLite, cada registro de embedding anatómico o global no solo almacena el vector matemático, sino también los metadatos taxonómicos explícitos en columnas separadas. Una tabla típica luce así:

SQL  
CREATE TABLE anfibios\_vectores (  
    id INTEGER PRIMARY KEY AUTOINCREMENT,  
    especie TEXT NOT NULL,  
    genero TEXT NOT NULL,  
    familia TEXT NOT NULL,  
    zona\_anatomica TEXT NOT NULL, \-- Ej: 'ojo', 'dorso\_flancos', 'anuro\_completo'  
    vector BLOB NOT NULL         \-- Almacenado mediante la extensión sqlite-vec  
);

### **2\. Ventajas de sqlite-vec en Entornos Móviles**

* **Ejecución 100% Local y Sin Servidor:** Al ser una extensión directa de SQLite, no requiere motores pesados ni conexiones de red. Funciona perfectamente en Android e iOS dentro del almacenamiento privado de la aplicación.  
* **Búsqueda de Vecinos Más Cercanos (k-NN) Eficiente:** Permite calcular la similitud vectorial (como la distancia de Coseno o L2) directamente desde SQL utilizando operadores optimizados por la extensión, manteniendo tiempos de respuesta de pocos milisegundos incluso con miles de registros regionales.  
* **Bajo Consumo de Memoria:** Se integra de forma nativa con los manejadores de bases de datos móviles estándar (como SQLite en Flutter, React Native o desarrollo nativo), evitando sobrecargas de RAM.

### **3\. Estrategia de Identificación Jerárquica (Familia $\\rightarrow$ Género $\\rightarrow$ Especie)**

Tener la taxonomía separada en columnas permite implementar un **sistema de decisión en cascada** cuando el modelo local realiza la consulta vectorial:

> 1. **Consulta Vectorial Amplia (Nivel Especie):** La app busca los vectores más cercanos en sqlite-vec y obtiene los candidatos principales a nivel de especie con su respectivo puntaje de similitud.  
> 2. **Respaldo Jerárquico por Incertidumbre:** Si la similitud para una especie específica está en una zona gris (por ejemplo, debido a una foto borrosa o iluminación deficiente en campo), el motor no falla de forma absoluta. Agrupa los resultados por su columna genero o familia:  
   * *Ejemplo de salida:* "No se puede confirmar la especie exacta *Pristimantis acanthinus*, pero el sistema identifica con alta certeza que pertenece al género ***Pristimantis*** y a la familia ***Strabomantidae***".  
> 3. **Filtro Geográfico Cruzado:** Como los embeddings se descargan por regiones (ej. paquete de Caldas), la consulta SQL en sqlite-vec se puede acotar instantáneamente con un WHERE basado en la ubicación GPS actual, reduciendo el espacio de búsqueda y mejorando la precisión del matching.