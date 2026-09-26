## ADDED Requirements

### Requirement: Los resultados se escriben a disco en dos formas
El notebook SHALL escribir los resultados de cada corrida a disco en dos archivos: uno con una fila por texto y una columna por dimensión y método, y otro con una fila por texto, método y dimensión. Ambos SHALL derivarse del marco de valores y NO SHALL recalcularse desde los resultados en bruto.

#### Scenario: Forma ancha
- **WHEN** termina una corrida
- **THEN** SHALL escribirse un archivo con una fila por texto evaluado, una columna por cada combinación de dimensión y método, y la relevancia en columnas propias separadas de la valencia

#### Scenario: Forma larga
- **WHEN** termina una corrida
- **THEN** SHALL escribirse un archivo con una fila por texto, método y dimensión, con las columnas de procedencia y de estrato disponibles para filtrar y agrupar

#### Scenario: Punto de extracción único preservado
- **WHEN** se construyen los archivos de salida
- **THEN** SHALL leerse del marco de valores y del marco de probabilidades, y NO SHALL volverse a recorrer la estructura de resultados en bruto

### Requirement: El archivo ancho devuelve el corpus enriquecido, no un extracto
Cuando la entrada sea un corpus, el archivo ancho SHALL conservar todas las columnas del archivo original y añadirles las de resultados, y SHALL unirlas por identificador y no por posición.

#### Scenario: Columnas originales conservadas
- **WHEN** la entrada proviene de un archivo de corpus
- **THEN** todas las columnas de ese archivo SHALL aparecer en la salida junto a las de resultados

#### Scenario: Unión por identificador
- **WHEN** la corrida aplicó deduplicación o muestreo, de modo que las filas evaluadas no coinciden en posición con las del archivo
- **THEN** la unión SHALL hacerse por identificador y NO SHALL producir filas duplicadas ni desalineadas

#### Scenario: Sin archivo de origen
- **WHEN** la entrada es la batería de prueba o textos aportados a mano
- **THEN** la exportación SHALL completarse igualmente, adjuntando los atributos que el notebook conoce de cada texto

#### Scenario: Método identificable en cada columna
- **WHEN** se inspecciona una columna de resultados
- **THEN** su nombre SHALL indicar de qué dimensión y de qué método proviene, de modo que dos métodos sobre la misma dimensión no puedan confundirse

### Requirement: Los valores exportados son auditables
La exportación SHALL poder incluir las probabilidades crudas de cada hipótesis como columnas, de modo que cada valor derivado pueda comprobarse sin volver a ejecutar el modelo.

#### Scenario: Probabilidades incluidas
- **WHEN** la opción correspondiente está activa
- **THEN** cada etiqueta de cada grupo de hipótesis SHALL aparecer como una columna con su probabilidad

#### Scenario: Verificación de un valor derivado
- **WHEN** se quiere comprobar la valencia o la relevancia de una dimensión
- **THEN** SHALL poder recalcularse a partir de las columnas de probabilidad presentes en el mismo archivo

### Requirement: La guardia contra el escalar combinado se aplica también a la salida
Ningún archivo exportado SHALL contener una columna que combine valencia y relevancia en un solo número, y la exportación SHALL detenerse si detecta una.

#### Scenario: Columna combinada detectada
- **WHEN** la tabla a exportar contiene una columna cuyo nombre indica ponderación o composición de valencia por relevancia
- **THEN** la exportación SHALL detenerse con un mensaje que explique que ese producto reintroduce el cero ambiguo

#### Scenario: Advertencia legible en la salida
- **WHEN** se completa la exportación
- **THEN** SHALL indicarse que valencia y relevancia no deben multiplicarse y cómo filtrar correctamente

### Requirement: Los archivos son legibles fuera del notebook
Los archivos exportados SHALL escribirse en una codificación que permita abrir correctamente acentos y sistemas de escritura no latinos en una hoja de cálculo, y SHALL poder descargarse desde el entorno de ejecución.

#### Scenario: Apertura en hoja de cálculo
- **WHEN** se abre el archivo ancho en una hoja de cálculo
- **THEN** los acentos y los caracteres no latinos SHALL mostrarse correctamente

#### Scenario: Descarga
- **WHEN** el notebook corre en un entorno que permite descargar archivos
- **THEN** SHALL ofrecerse la descarga de los archivos escritos, y cuando no sea posible SHALL indicarse dónde encontrarlos

### Requirement: Las salidas no interfieren con la entrada
Los archivos que el notebook escribe SHALL quedar fuera del conjunto de archivos candidatos a ser leídos como corpus, de modo que una corrida posterior no falle por la existencia de los resultados de la anterior.

#### Scenario: Segunda corrida consecutiva
- **WHEN** se ejecuta el notebook una segunda vez sobre el mismo directorio, con los archivos de la corrida anterior ya escritos
- **THEN** la autodetección del corpus SHALL seguir encontrando un único archivo de entrada y la ejecución SHALL completarse

#### Scenario: Procedencia declarada al exportar
- **WHEN** se completa la exportación
- **THEN** SHALL indicarse de qué entrada provienen los resultados, cuántas filas se exportaron, y —cuando provengan del corpus— que no están validados contra codificación humana
