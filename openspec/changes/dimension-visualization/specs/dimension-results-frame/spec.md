## ADDED Requirements

### Requirement: Punto único de extracción de resultados
El sistema SHALL construir los marcos de datos en una sola pasada sobre los resultados de ambos métodos, y toda figura y toda tabla SHALL leer de esos marcos y no de las estructuras crudas de resultados.

#### Scenario: Construcción única
- **WHEN** se construyen los marcos a partir de los resultados de una corrida
- **THEN** SHALL recorrerse los resultados una sola vez y producirse los marcos de valores, de probabilidades crudas y de emparejamientos léxicos

#### Scenario: Tabla resumen desde el marco
- **WHEN** se muestra la tabla resumen de la comparación entre métodos
- **THEN** SHALL derivarse del marco de valores y NO SHALL reconstruirse a partir de los resultados crudos

#### Scenario: Sin dependencias ocultas entre celdas
- **WHEN** se ejecuta la tabla resumen sin haber ejecutado la sección de demostración entre idiomas
- **THEN** SHALL funcionar sin error, porque no depende de variables creadas en esa sección

### Requirement: Conservación íntegra de las magnitudes medidas
Los marcos SHALL conservar todas las magnitudes que ambos métodos producen —las cinco dimensiones reportadas, la relevancia de cada dimensión léxica, el sentimiento general, el peso de engagement, las probabilidades crudas de cada grupo de hipótesis y las palabras del léxico activadas— sin descartar ninguna.

#### Scenario: Violencia y seguridad conservadas
- **WHEN** se construye el marco de valores
- **THEN** SHALL incluir las dimensiones de prominencia de violencia y de seguridad percibida, que hoy la tabla resumen descarta

#### Scenario: Probabilidades crudas conservadas
- **WHEN** se construye el marco de probabilidades
- **THEN** SHALL incluir la probabilidad de cada etiqueta de cada grupo de hipótesis, para cada texto

#### Scenario: Palabras del léxico conservadas
- **WHEN** se construye el marco de emparejamientos léxicos
- **THEN** SHALL registrar una fila por cada palabra del léxico activada, con su dimensión, su polaridad y el texto en que se activó

### Requirement: Separación entre grupo de hipótesis y dimensión reportada
El sistema SHALL distinguir el grupo de hipótesis con el que se hace cada llamada al modelo de la dimensión que se reporta, porque un mismo grupo puede producir más de una dimensión.

#### Scenario: Un grupo, dos dimensiones
- **WHEN** se procesa el grupo de violencia y seguridad, que tiene cuatro etiquetas y produce tanto la prominencia de violencia como la seguridad percibida
- **THEN** las probabilidades crudas SHALL asociarse al grupo y los dos valores derivados SHALL asociarse cada uno a su dimensión

#### Scenario: Conteo de pasadas verificable
- **WHEN** se informa el costo de una corrida
- **THEN** el número de pasadas de modelo SHALL derivarse del número de etiquetas de cada grupo y no de una constante escrita a mano

### Requirement: Valencia y ausencia como ejes separados
El marco de valores SHALL mantener la valencia y la relevancia como columnas independientes, SHALL declarar para cada dimensión si su escala es de valencia o de prominencia, y NO SHALL producir ninguna columna que combine ambos ejes en un solo escalar.

#### Scenario: Sin producto de valencia por relevancia
- **WHEN** se inspecciona cualquier marco, tabla o dato serializado hacia las figuras
- **THEN** NO SHALL existir ninguna magnitud que resulte de multiplicar la valencia por la relevancia, ni de ponderar una por la otra

#### Scenario: Relevancia ausente para el método actual
- **WHEN** se registran los valores del método actual, que no produce relevancia
- **THEN** la relevancia SHALL quedar marcada como no disponible y NO SHALL sustituirse por cero, que significaría "no habló del tema"

#### Scenario: Escala declarada por dimensión
- **WHEN** una figura necesita saber si una dimensión va de menos uno a uno o de cero a uno
- **THEN** SHALL leerlo del marco y no inferirlo de los valores observados

### Requirement: Columnas de procedencia reservadas para el corpus
El marco de valores SHALL incluir columnas opcionales de identificador de tweet, fecha de publicación e idioma, vacías cuando la entrada sea una lista de textos y pobladas cuando la entrada provenga de un corpus, y ninguna figura SHALL exigir que estén pobladas.

#### Scenario: Entrada sin procedencia
- **WHEN** la entrada es una lista de textos sin identificador ni fecha
- **THEN** las columnas de procedencia SHALL existir vacías y todas las figuras SHALL construirse igualmente

#### Scenario: Entrada con idioma
- **WHEN** la entrada declara el idioma de cada texto, como ocurre con la batería de ejemplo
- **THEN** la columna de idioma SHALL poblarse y las figuras que comparan idiomas SHALL usarla

#### Scenario: Entrada desde corpus
- **WHEN** la entrada proviene de un corpus con identificador y fecha
- **THEN** las columnas de procedencia SHALL poblarse sin que las figuras existentes requieran cambios
