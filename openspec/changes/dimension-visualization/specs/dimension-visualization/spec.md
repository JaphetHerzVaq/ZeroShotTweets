## ADDED Requirements

### Requirement: La ausencia se marca, nunca se colapsa ni se oculta
Toda figura que muestre valencia SHALL señalar la región en que la relevancia queda por debajo del umbral configurable de mudez, SHALL informar cuántas observaciones caen en ella, y NO SHALL excluirlas del dibujo ni combinar valencia y relevancia en un solo valor.

#### Scenario: Banda de mudez señalada
- **WHEN** se dibuja una figura que muestra valencia junto a relevancia
- **THEN** la región por debajo del umbral de mudez SHALL quedar delimitada y nombrada, y el número de observaciones dentro SHALL estar impreso

#### Scenario: Observaciones mudas no filtradas
- **WHEN** una observación tiene relevancia por debajo del umbral
- **THEN** SHALL dibujarse igualmente, porque su presencia es la evidencia que la figura existe para mostrar

#### Scenario: Umbral visible como elección
- **WHEN** se muestra la distribución de relevancia de una dimensión
- **THEN** SHALL mostrarse la distribución completa y el umbral superpuesto, de modo que se pueda juzgar qué tan sensible es la lectura al corte elegido

#### Scenario: Umbral reconfigurado
- **WHEN** se cambia el umbral de mudez en la configuración y se reejecuta la sección
- **THEN** todas las figuras SHALL reflejar el nuevo corte sin modificar código

### Requirement: Dispersión del instrumento entre idiomas
El sistema SHALL producir una figura que compare, para un mismo contenido expresado en los seis grupos de idioma, el valor que asigna el método actual contra el que asigna el rediseño, y SHALL mostrar para cada método la medida de dispersión entre idiomas.

#### Scenario: Comparación por idioma
- **WHEN** se dibuja la figura de dispersión para una dimensión
- **THEN** SHALL mostrar un par de valores por idioma, uno por método, sobre la misma escala

#### Scenario: Dispersión como número reportable
- **WHEN** se muestra la figura
- **THEN** SHALL informar para cada método el rango y la desviación entre idiomas, identificados como la magnitud que se reporta, dado que el contenido no varía y una dispersión menor indica un instrumento más justo

#### Scenario: Todas las dimensiones léxicas
- **WHEN** la batería cubre las tres dimensiones que el rediseño convierte de léxico a zero-shot
- **THEN** SHALL poder generarse la figura para cada una de ellas, sin que el conjunto de dimensiones aparezca fijo en el código

#### Scenario: Escritura de derecha a izquierda
- **WHEN** una etiqueta o un texto de la figura está en un idioma de escritura derecha a izquierda
- **THEN** SHALL renderizarse con la forma y el orden correctos

### Requirement: Plano de valencia contra relevancia
El sistema SHALL producir, para cada dimensión que tenga relevancia, una figura que sitúe cada observación según su valencia y su relevancia, de modo que las observaciones que el método actual reduce a un mismo valor queden separadas.

#### Scenario: Separación del cero ambiguo
- **WHEN** dos observaciones reciben valencia cercana a cero, una con relevancia alta y otra con relevancia baja
- **THEN** SHALL aparecer en posiciones distintas de la figura, y la figura SHALL explicar que el método actual les asigna el mismo valor

#### Scenario: Origen de cada observación identificable
- **WHEN** se consulta una observación de la figura
- **THEN** SHALL poder identificarse el texto del que proviene y su idioma

#### Scenario: Dimensión sin relevancia
- **WHEN** una dimensión no produce relevancia, como las que derivan del grupo de violencia y seguridad
- **THEN** SHALL quedar excluida de esta figura, y la exclusión SHALL estar explicada

### Requirement: Valores posibles de cada método
El sistema SHALL producir una figura que contraste el valor asignado por el método actual contra el asignado por el rediseño para las mismas observaciones, y SHALL señalar los valores discretos que el método actual puede tomar en las dimensiones donde su fórmula no incorpora el sentimiento.

#### Scenario: Dimensión escalonada
- **WHEN** se dibuja la figura para una dimensión cuya fórmula actual depende sólo del conteo de palabras
- **THEN** los valores discretos alcanzables SHALL quedar marcados sobre el eje correspondiente

#### Scenario: Dimensión no escalonada
- **WHEN** se dibuja la figura para una dimensión cuya fórmula actual incorpora el sentimiento, que es continuo
- **THEN** la figura SHALL indicar que esa dimensión no es escalonada y por qué, en lugar de marcar valores discretos inexistentes

#### Scenario: Acuerdo entre métodos legible
- **WHEN** se muestra la figura
- **THEN** SHALL incluir la referencia de acuerdo perfecto entre ambos métodos, para que la separación respecto de ella sea legible

### Requirement: Ausencia agregada por dimensión con alerta
El sistema SHALL informar, para cada dimensión con relevancia, qué proporción de las observaciones queda por debajo del umbral de mudez, y SHALL emitir una alerta escrita cuando esa proporción supere un umbral configurable.

#### Scenario: Dimensión mayoritariamente muda
- **WHEN** la proporción de observaciones mudas de una dimensión supera el umbral configurado
- **THEN** el sistema SHALL emitir una alerta escrita indicando que la dimensión apenas mide nada en ese corpus y que su promedio está dominado por observaciones que no hablaron del tema

#### Scenario: Ninguna dimensión muda
- **WHEN** ninguna dimensión supera el umbral
- **THEN** el sistema SHALL indicarlo explícitamente en lugar de no decir nada

#### Scenario: Ausencia no confundida con neutralidad
- **WHEN** se informa la proporción de ausencia
- **THEN** SHALL presentarse como magnitud propia y NO SHALL aparecer apilada junto a los valores de valencia

### Requirement: Descomposición de las probabilidades del modelo
El sistema SHALL producir una figura que muestre, por grupo de hipótesis, cómo se reparte la probabilidad entre sus etiquetas, incluida la de irrelevancia.

#### Scenario: Reparto por grupo
- **WHEN** se dibuja la descomposición de un grupo de tres hipótesis
- **THEN** SHALL mostrarse las tres probabilidades, que suman uno, identificadas por la etiqueta legible y no por la frase completa

#### Scenario: Grupo de cuatro etiquetas
- **WHEN** se dibuja la descomposición del grupo de violencia y seguridad
- **THEN** SHALL mostrarse sus cuatro etiquetas, sin que el número de etiquetas aparezca fijo en el código

#### Scenario: Hipótesis de irrelevancia dominante
- **WHEN** la hipótesis de irrelevancia concentra la mayor parte de la probabilidad en casi todas las observaciones de un grupo
- **THEN** el sistema SHALL señalarlo como indicio de que las frases de ese grupo pueden estar mal calibradas

### Requirement: Cobertura del léxico del método actual
El sistema SHALL producir una figura que muestre, por idioma, en qué proporción de las observaciones el léxico del método actual llegó a activar alguna palabra, y SHALL informar qué proporción de los emparejamientos ocurrió por subcadena en lugar de por palabra completa.

#### Scenario: Idioma sin cobertura léxica
- **WHEN** en un idioma el léxico no activa ninguna palabra en ninguna observación
- **THEN** la figura SHALL mostrarlo como cobertura nula y SHALL explicar que en ese idioma las dimensiones léxicas valen lo mismo por construcción

#### Scenario: Emparejamiento por subcadena
- **WHEN** una palabra del léxico se activa por estar contenida dentro de otra palabra distinta del texto
- **THEN** SHALL contarse aparte de los emparejamientos por palabra completa y SHALL reportarse con ejemplos del corpus cargado

#### Scenario: Fenómeno no observado en el corpus cargado
- **WHEN** ningún emparejamiento por subcadena aparece en el corpus cargado
- **THEN** la figura SHALL indicar que no se observó en ese corpus, y NO SHALL afirmar que el fenómeno no ocurre

#### Scenario: Método actual no modificado
- **WHEN** se mide el emparejamiento por subcadena
- **THEN** la lógica del método actual SHALL permanecer intacta, para que la comparación entre métodos siga reflejando el método en producción

### Requirement: Cada figura declara su escala y advierte cuando no la tiene
Toda figura SHALL mostrar el número de observaciones sobre el que se construyó, y SHALL emitir una advertencia escrita cuando ese número quede por debajo de un umbral configurable de interpretabilidad.

#### Scenario: Muestra insuficiente
- **WHEN** una figura se construye sobre menos observaciones que el umbral configurado
- **THEN** SHALL dibujarse igualmente, acompañada de una advertencia de que a esa escala no es interpretable

#### Scenario: Sin observaciones
- **WHEN** una figura no tiene ninguna observación que dibujar
- **THEN** SHALL mostrar un aviso de ausencia de datos en lugar de un lienzo vacío o un error

#### Scenario: Las figuras describen, no validan
- **WHEN** se presenta el conjunto de figuras
- **THEN** SHALL incluirse la advertencia de que describen el comportamiento del instrumento y no sustituyen la validación contra codificación humana con el umbral de acuerdo que el proyecto ya define

### Requirement: Agregación previa al renderizado
El sistema SHALL calcular en Python los datos que cada figura necesita, una sola vez, y SHALL embeber ese resultado en la página, omitiendo las combinaciones vacías en lugar de emitirlas como cero.

#### Scenario: Datos embebidos
- **WHEN** se genera la página
- **THEN** SHALL contener los valores que las figuras dibujan, y NO SHALL requerir ejecutar Python para redibujarlas

#### Scenario: Combinación sin observaciones
- **WHEN** una combinación de dimensión, método e idioma no tiene observaciones
- **THEN** SHALL omitirse del conjunto embebido en lugar de representarse como cero

#### Scenario: Tamaño informado
- **WHEN** se genera la página
- **THEN** el sistema SHALL informar el tamaño del conjunto embebido

### Requirement: Doble salida, en el notebook y como archivo independiente
El sistema SHALL construir un único documento, SHALL mostrarlo dentro de la salida del notebook y SHALL escribirlo además como archivo autocontenido que funcione al abrirse fuera del notebook.

#### Scenario: Un solo documento, dos destinos
- **WHEN** se generan las figuras
- **THEN** el documento mostrado en el notebook y el archivo escrito SHALL provenir de la misma construcción, sin dos rutas de renderizado que puedan divergir

#### Scenario: Archivo abierto fuera del notebook
- **WHEN** se abre el archivo generado sin el notebook ni su kernel
- **THEN** SHALL mostrar las mismas figuras con sus controles operativos

#### Scenario: Biblioteca de gráficas no disponible
- **WHEN** la biblioteca de gráficas no se puede cargar
- **THEN** la página SHALL mostrar un mensaje que explique la causa, en lugar de quedar en blanco

#### Scenario: Notebook reabierto
- **WHEN** se reabre el notebook guardado sin reejecutar la sección
- **THEN** la documentación de la celda SHALL advertir que las figuras dejan de ser interactivas y que el archivo es el artefacto que sobrevive

### Requirement: Ficha técnica del instrumento embebida
La página SHALL incluir las frases de hipótesis textuales de cada grupo, el idioma de las hipótesis, la plantilla empleada, los identificadores de los modelos y la fecha de la corrida.

#### Scenario: Figura citable
- **WHEN** se consulta la página generada
- **THEN** SHALL poder leerse la redacción exacta de cada hipótesis con la que se produjeron los valores mostrados

#### Scenario: Hipótesis modificadas
- **WHEN** se cambian las frases de las hipótesis y se vuelve a generar la página
- **THEN** la ficha técnica SHALL reflejar las frases nuevas

### Requirement: Salida apta para impresión
Las figuras SHALL exportarse en formato vectorial y SHALL seguir siendo legibles sin color.

#### Scenario: Exportación vectorial
- **WHEN** se exporta una figura desde la página
- **THEN** SHALL obtenerse un archivo vectorial que no se degrade al ampliarse

#### Scenario: Sin color
- **WHEN** se elimina el color de una figura
- **THEN** las series SHALL seguir distinguiéndose por forma o por etiqueta directa, y no únicamente por tono

#### Scenario: Escala de valencia centrada
- **WHEN** se colorea una magnitud de valencia
- **THEN** SHALL usarse una escala divergente con el cero en el centro, distinta de la escala secuencial usada para la relevancia
