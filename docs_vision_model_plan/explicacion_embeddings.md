Para optimizar el almacenamiento del dispositivo móvil y acelerar la búsqueda vectorial, los embeddings de las zonas anatómicas se organizan mediante **fragmentación geográfica (*geographic sharding*)** y se filtran en tiempo de ejecución utilizando el **contexto de ubicación GPS** del usuario.  
La arquitectura para implementar este sistema descargable por regiones funciona a través de las siguientes fases:

### **1\. Particionamiento Geográfico de los Embeddings (Servidor / Nube)**

En lugar de empaquetar los vectores de las 28 especies en un único archivo pesado que deba descargarse completo, la base de datos vectorial se divide por zonas biogeográficas (por ejemplo, dividiendo por departamentos o ecorregiones como la región Andina/Caldas, la Costa Caribe o la Orinoquía):

* **Agrupamiento por Rango de Distribución:** Utilizando datos históricos de ocurrencia (como los registros de GBIF mencionados en la estrategia de campo), filtras qué especies de las 28 realmente habitan en cada zona geográfica específica.  
* **Generación de Paquetes Regionales:** Creas matrices de embeddings exclusivas para cada región. Por ejemplo, el paquete embeddings\_caldas\_v1.zip solo contendrá los vectores de las especies nativas o reportadas en esa zona específica, reduciendo drásticamente el tamaño del archivo.

### **2\. Estructura del Manifiesto Remoto (manifest.json)**

Para que la aplicación móvil sepa qué descargar según el lugar donde se encuentre el usuario, se aloja un archivo de control ligero en la nube:

JSON  
{  
  "regiones": \[  
    {  
      "id": "co\_caldas",  
      "nombre": "Ecorregión Andina \- Caldas",  
      "bounding\_box": {  
        "lat\_min": 4.85, "lat\_max": 5.60,  
        "lon\_min": \-75.90, "lon\_max": \-74.60  
      },  
      "version": "1.0.2",  
      "download\_url": "https://tuservidor.com/bundles/embeddings\_caldas\_v1.0.2.zip",  
      "file\_size\_kb": 1420  
    }  
  \]  
}

### **3\. Automatización de Descarga por Ubicación en la App Móvil**

El flujo operativo dentro de la aplicación (desarrollada en Flutter o React Native) gestiona el contexto de ubicación de forma transparente:

> 1. **Captura de Coordenadas GPS:** Al abrir la app o al activar el modo de campo, el dispositivo obtiene la latitud y longitud actual mediante el GPS nativo del teléfono.  
> 2. **Validación Espacial (Bounding Box):** Un script local revisa las coordenadas contra las cajas delimitadoras (*bounding boxes*) definidas en el manifest.json remoto para identificar a qué región pertenece el usuario (ej. detecta que se encuentra dentro de los límites de Caldas).  
> 3. **Descarga Selectiva en Segundo Plano:** La aplicación verifica si el paquete de embeddings de esa región ya está almacenado localmente en el directorio privado del teléfono. Si no existe o si el manifiesto indica una nueva versión, descarga únicamente ese .zip regional (de pocos megabytes), evitando saturar el almacenamiento con datos de especies de otras regiones del país.

### **4\. Aplicación del Contexto Geográfico como Filtro en el Motor de Reglas**

Una vez que el usuario toma la fotografía en campo, el contexto de ubicación cumple un rol crítico en la identificación final (conocido en IA como **Geo-Prior**):

* **Restricción del Espacio de Búsqueda:** El modelo local no compara el vector de la rana contra las 28 especies globales, sino **únicamente contra el subconjunto de especies cargado en el paquete regional activo** (las que habitan en esa zona).  
* **Validación Lógica:** Si el modelo de visión arroja una alta similitud visual con una especie que taxonómicamente pertenece a la Amazonía pero el GPS confirma que el usuario está en una zona altoandina de Caldas, el motor de reglas lógicas aplica una penalización estricta o descarta directamente al candidato por incompatibilidad biogeográfica, eliminando falsos positivos antes de mostrar el resultado en pantalla.