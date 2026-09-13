# **Sistema de Visión Computacional y Segmentación Anatómica para Anuros**

## **1\. Visión General del Sistema y Alcance del Proyecto**

Este documento técnico detalla la arquitectura de un sistema móvil de inteligencia artificial diseñado para la identificación automatizada de 28 especies de anuros (ranas y sapos), optimizado para operar localmente en dispositivos móviles de gama media en entornos de campo (como la región de Caldas, Colombia).  
Dada la restricción de contar con un conjunto de datos acotado (un promedio de 30 imágenes por especie), el sistema implementa una **arquitectura híbrida en cascada** que combina:

> 1. **Segmentación y detección de estado global** (anuro\_completo y atributos de postura/oclusión).  
> 2. **Segmentación anatómica local de alta precisión** basada en un esquema de 17+ partes estructuradas en CVAT.  
> 3. **Generación de embeddings independientes por zonas anatómicas** mediante aprendizaje métrico (*Metric Learning*).  
> 4. **Un motor de reglas lógicas basado en conocimiento biológico (JSON)** que valida la coherencia taxonómica y mitiga los riesgos de sobreajuste (*overfitting*).

## **2\. Estructura de Anotación y Esquema de Datos (CVAT)**

Para estandarizar el entrenamiento, el etiquetado en CVAT se divide en dos niveles jerárquicos: el nivel global del individuo y el nivel local de estructuras anatómicas con atributos categóricos fijos.

### **Esquema Base en JSON para CVAT**

JSON  
\[  
  {  
    "name": "anuro\_completo",  
    "color": "\#54b49e",  
    "type": "any",  
    "attributes": \[  
      {  
        "name": "vista",  
        "input\_type": "select",  
        "mutable": true,  
        "values": \["dorsal", "ventral", "lateral", "frontal", "detalle\_macro"\],  
        "default\_value": "dorsal"  
      },  
      {  
        "name": "calidad\_enfoque",  
        "input\_type": "select",  
        "mutable": true,  
        "values": \["alta", "media", "borrosa\_parcial"\],  
        "default\_value": "alta"  
      },  
      {  
        "name": "postura",  
        "input\_type": "select",  
        "mutable": true,  
        "values": \["extendida", "recogida", "salto", "parcialmente\_oculta"\],  
        "default\_value": "extendida"  
      }  
    \]  
  },  
  {  
    "name": "ojo",  
    "color": "\#f1c40f",  
    "type": "polygon",  
    "attributes": \[  
      {  
        "name": "orientacion",  
        "input\_type": "select",  
        "mutable": false,  
        "values": \["horizontal", "vertical", "oblicua"\],  
        "default\_value": "horizontal"  
      },  
      {  
        "name": "color\_iris",  
        "input\_type": "select",  
        "mutable": false,  
        "values": \["marron\_pardo", "amarillo\_dorado", "rojo\_naranja", "verde", "azul\_turquesa", "gris\_claro", "otro"\],  
        "default\_value": "marron\_pardo"  
      }  
    \]  
  },  
  {  
    "name": "glandulas\_pliegues",  
    "color": "\#16a085",  
    "type": "polygon",  
    "attributes": \[  
      {  
        "name": "tipo",  
        "input\_type": "select",  
        "mutable": false,  
        "values": \["parotoide", "dorsolateral", "cresta\_dorsolateral", "pliegue\_supratimpanico", "inguinal", "femoral", "otra"\],  
        "default\_value": "dorsolateral"  
      },  
      {  
        "name": "prominencia",  
        "input\_type": "select",  
        "mutable": false,  
        "values": \["ausente", "leve", "moderada", "marcada"\],  
        "default\_value": "leve"  
      }  
    \]  
  }  
\]

## **3\. Pipeline de Entrenamiento en Cascada**

Dado el bajo volumen de muestras iniciales (aprox. 840 imágenes en total para las 28 especies), se evita el entrenamiento de una red monolítica desde cero mediante un enfoque de dos fases:

### **Fase A: Segmentación y Contexto Global (anuro\_completo)**

* **Modelo Base:** Red ligera (como MobileNetV3-Small o YOLOv8-seg) con codificador preentrenado (ej. BioCLIP).  
* **Objetivo:** Aislar al individuo del fondo (hojarasca, lodo, agua) y capturar metadatos globales críticos como la **postura**, la **vista** (dorsal/ventral) y el **nivel de oclusión**.  
* **Resultado:** Una máscara ROI (Región de Interés) limpia que elimina el ruido ambiental y centra el procesamiento en el anfibio.

### **Fase B: Segmentación Local de Subpartes y Extracción de Atributos**

* **Modelo Condicionado:** Utiliza el recorte de la Fase A para alimentar una segunda cabeza de red orientada a segmentar las estructuras internas (ojo, tímpano, dorso, glándulas, extremidades).  
* **Cabezas Multitarea (*Multi-Task Learning*):** Capas densas paralelas que predicen simultáneamente las máscaras poligonales y los atributos categóricos (ej. color del iris, textura de la piel).

## **4\. Sistema de Embeddings Independientes por Zonas Anatómicas**

Para evitar la actualización masiva de la aplicación móvil ante cambios taxonómicos, el sistema separa la representación matemática en vectores descargables:

> 1. **Extracción de Características por Recorte (*RoI Pooling / Cropping*):** A partir de las máscaras de segmentación de las partes, la red extrae sub-vectores de características (embeddings de 128 o 256 dimensiones) exclusivos para zonas clave como el ojo, el dorso\_flancos o las glandulas\_pliegues.  
> 2. **Optimización con *Metric Learning*:** Se entrena la red utilizando funciones de pérdida métrica (como *Triplet Loss* o *ArcFace*) para garantizar que los embeddings de una misma estructura para la misma especie se agrupen de forma compacta en el espacio vectorial.  
> 3. **Paquetes Modulares Descargables (.zip/.json):** Los vectores de referencia se almacenan en la nube de forma estructurada. La app móvil descarga únicamente esta matriz de embeddings por región y especie, permitiendo comparar en tiempo real mediante **Similitud Coseno** local y offline.

## **5\. Motor de Reglas Lógicas y Validación Taxonómica (JSON)**

El modelo de visión recopila datos visuales y geométricos, pero la decisión final se valida mediante un motor lógico impulsado por una base de conocimiento biológico.

### **Ejemplo de Estructura de Reglas Biológicas**

JSON  
{  
  "especies": \[  
    {  
      "nombre\_cientifico": "Rhinella horribilis",  
      "perfil\_biologico": {  
        "ojo": {  
          "color\_iris\_permitido": \["amarillo\_dorado", "marron\_pardo"\],  
          "orientacion\_pupila": "horizontal"  
        },  
        "glandulas\_pliegues": {  
          "tipo\_obligatorio": "parotoide",  
          "prominencia": "marcada"  
        },  
        "dorso\_flancos": {  
          "textura\_permitida": \["verrugosa", "granulosa"\]  
        }  
      }  
    }  
  \]  
}

* **Funcionamiento:** Si el modelo visual detecta un espécimen con glándulas parotídeas marcadas y textura verrugosa, el motor cruza las variables con el JSON y confirma la especie, descartando falsos positivos incluso si el margen de confianza visual es estrecho.

## **6\. Despliegue Móvil y Optimización de Rendimiento**

Para garantizar fluidez y bajo consumo de batería en teléfonos de gama media:

* **Formato de Exportación:** Conversión del modelo final a formato **TensorFlow Lite (.tflite)** o **ONNX Runtime Mobile**.  
* **Cuantización INT8:** Reducción de la precisión de punto flotante completo (FP32) a enteros de 8 bits. Esto disminuye el peso del modelo base a un rango de **3 MB a 7 MB** y acelera significativamente la inferencia por fotograma utilizando instrucciones de hardware móvil.  
* **Pipeline en el Dispositivo (App en Flutter/Nativo):**  
  1. Captura de imagen en campo.  
  2. Inferencia TFLite local (Segmentación de ROI y partes).  
  3. Procesamiento geométrico ligero (cálculo de centroides y razones de aspecto mediante matrices o OpenCV Mobile).  
  4. Consulta al motor de reglas local y entrega de diagnóstico taxonómico sin requerir conexión a internet.