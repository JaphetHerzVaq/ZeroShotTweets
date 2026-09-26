## ADDED Requirements

### Requirement: Carga del corpus desde un archivo del proyecto
El notebook SHALL admitir como entrada un archivo CSV situado en el directorio de trabajo, además de la batería de ejemplo y de los textos pegados a mano, y SHALL localizarlo sin que el usuario escriba una ruta cuando haya exactamente uno.

#### Scenario: Archivo único en el directorio
- **WHEN** el modo de entrada es corpus y hay exactamente un archivo CSV en el directorio de trabajo
- **THEN** SHALL usarlo sin requerir configuración adicional e informar qué archivo tomó y cuántas filas leyó

#### Scenario: Ningún archivo o varios
- **WHEN** no hay ningún CSV o hay más de uno y no se declaró una ruta
- **THEN** la ejecución SHALL detenerse con un mensaje que liste lo encontrado e indique cómo declarar la ruta

#### Scenario: Marca de orden de bytes
- **WHEN** el archivo comienza con una marca de orden de bytes
- **THEN** SHALL leerse sin que esa marca contamine el nombre de la primera columna

### Requirement: Mapeo de columnas declarado y validado
El mapeo entre los campos que el notebook necesita y los nombres de columna del archivo SHALL declararse de forma explícita en la celda de configuración, y SHALL validarse contra el encabezado real antes de evaluar ningún texto.

#### Scenario: Columna ausente
- **WHEN** una columna declarada no existe en el archivo
- **THEN** la ejecución SHALL detenerse antes de cargar ningún modelo, indicando qué columna falta y enumerando las que sí están

#### Scenario: Procedencia poblada
- **WHEN** el archivo aporta identificador, fecha de publicación e idioma
- **THEN** las columnas de procedencia del marco de valores SHALL poblarse con esos datos

#### Scenario: Valores booleanos inconsistentes
- **WHEN** una columna booleana del archivo mezcla distintas capitalizaciones del mismo valor
- **THEN** SHALL interpretarse de forma insensible a mayúsculas y NO SHALL producir categorías espurias

#### Scenario: Filas sin fecha
- **WHEN** una fila carece de fecha de publicación
- **THEN** SHALL cargarse igualmente con la fecha marcada como no disponible, y el número de filas afectadas SHALL informarse

### Requirement: Columna de entrada seleccionable y comparación a tres vías
Cuando el corpus aporte tanto el texto original como una traducción, el notebook SHALL permitir elegir cuál alimenta al modelo, y SHALL producir además la medición del método léxico sobre ambas columnas, por ser una comparación que no consume pasadas de modelo.

#### Scenario: Tres vías en el marco
- **WHEN** el corpus aporta texto original y traducción
- **THEN** el marco de valores SHALL contener el método léxico sobre el original, el método léxico sobre la traducción y el rediseño sobre el original, distinguidos por el valor del método y sin columnas nuevas

#### Scenario: Costo sin incremento
- **WHEN** se informa el costo de la corrida con la comparación a tres vías activa
- **THEN** el número de pasadas de modelo por texto SHALL ser el mismo que sin ella

#### Scenario: Mérito de la traducción declarado
- **WHEN** se presenta la comparación entre el léxico sobre el original y el léxico sobre la traducción
- **THEN** SHALL declararse que la segunda mide el léxico junto con la calidad de una traducción automática y que ambos efectos no pueden separarse

#### Scenario: Fila sin traducción
- **WHEN** una fila carece de traducción
- **THEN** SHALL excluirse de la vía que la requiere y contarse, y NO SHALL sustituirse en silencio por el texto original

### Requirement: Estratos de recolección conservados y desglosados
El marco de valores SHALL conservar como columnas los campos que identifican con qué consulta y en qué modalidad se recolectó cada texto, y toda figura que promedie sobre el corpus SHALL desglosar por estrato o advertir por escrito que no lo hace.

#### Scenario: Estratos en el marco
- **WHEN** la entrada es el corpus
- **THEN** los campos de consulta de origen y de modalidad de recolección SHALL viajar como columnas del marco de valores

#### Scenario: Promedio que mezcla intenciones de búsqueda
- **WHEN** una figura promedia una dimensión sobre estratos cuyas consultas buscaban expresamente esa dimensión junto a estratos que no
- **THEN** SHALL desglosar por estrato o SHALL emitir una alerta escrita advirtiendo que el promedio está dirigido por la consulta y no es reportable como hallazgo

### Requirement: Muestreo, deduplicación y costo verificable antes de comprometer el corpus
El notebook SHALL permitir limitar el número de textos evaluados, SHALL eliminar registros repetidos antes de evaluar, y SHALL informar el tiempo de la corrida de modo que pueda extrapolarse al corpus completo.

#### Scenario: Muestra acotada
- **WHEN** se declara un tope de textos a evaluar menor que el tamaño del corpus
- **THEN** SHALL evaluarse solo esa cantidad, informando cuántos textos se omitieron

#### Scenario: Registros repetidos
- **WHEN** el corpus contiene filas con el mismo identificador
- **THEN** SHALL conservarse una sola por identificador y SHALL informarse cuántas se descartaron

#### Scenario: Extrapolación del costo
- **WHEN** termina una corrida sobre una muestra
- **THEN** SHALL informarse el tiempo total, el tiempo por texto y el costo estimado del corpus completo

### Requirement: Evaluación por lotes sin alterar los valores
Las llamadas al modelo de inferencia SHALL poder agrupar varios textos por lote, con tamaño configurable, y los valores producidos SHALL ser los mismos que se obtienen evaluando texto por texto.

#### Scenario: Equivalencia de resultados
- **WHEN** se evalúa un mismo conjunto de textos con lotes y sin lotes
- **THEN** los valores de todas las dimensiones SHALL coincidir

#### Scenario: Forma de la salida preservada
- **WHEN** se activa la evaluación por lotes
- **THEN** las funciones que consumen las probabilidades SHALL seguir recibiéndolas por texto y por etiqueta, sin cambios

### Requirement: Los idiomas se derivan del corpus
La lista de idiomas de toda figura SHALL derivarse de los datos cargados y NO SHALL declararse como un conjunto fijo de grupos, y los códigos que indican ausencia de idioma detectable SHALL agruparse en una categoría propia en lugar de tratarse como idiomas.

#### Scenario: Idiomas observados
- **WHEN** se construye una figura que compara idiomas
- **THEN** SHALL usar los idiomas presentes en los datos, con su número de observaciones, y NO SHALL dibujar grupos sin observaciones

#### Scenario: Códigos de ausencia de idioma
- **WHEN** el corpus contiene códigos que indican que no se detectó idioma
- **THEN** SHALL agruparse bajo una categoría explícita de idioma no detectado

#### Scenario: Idioma sin cobertura léxica
- **WHEN** un idioma presente en el corpus no tiene ninguna palabra en las listas del método léxico
- **THEN** SHALL informarse el número de textos afectados como resultado de la medición, por ser textos que el método actual no puede evaluar por construcción

### Requirement: La procedencia de los datos se rotula en tres estados
Toda figura y toda tabla SHALL declarar si se construyó sobre la batería de prueba, sobre textos aportados a mano o sobre el corpus, y el rótulo del corpus SHALL advertir que los resultados son descriptivos y no están validados contra codificación humana.

#### Scenario: Figura sobre el corpus
- **WHEN** una figura se construye sobre el corpus
- **THEN** SHALL rotularse indicando el tamaño del corpus y advirtiendo que ninguna medición ha sido validada contra codificación humana

#### Scenario: Ausencia de codificación humana declarada
- **WHEN** el corpus no aporta columnas de codificación manual pobladas
- **THEN** SHALL declararse explícitamente que la validación de acuerdo entre métodos y codificadores sigue pendiente

#### Scenario: Rótulo correspondiente a cada entrada
- **WHEN** cambia el modo de entrada
- **THEN** el rótulo SHALL corresponder al modo activo, sin conservar el de una corrida anterior
