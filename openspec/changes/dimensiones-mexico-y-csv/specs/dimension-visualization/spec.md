## MODIFIED Requirements

### Requirement: Dispersión del instrumento entre idiomas
El sistema SHALL producir una figura que compare, para un mismo contenido expresado en varios idiomas, el valor que asigna el método léxico contra el que asigna el rediseño, y SHALL mostrar para cada método la medida de dispersión entre idiomas. El conjunto de idiomas SHALL derivarse de los datos cargados y NO SHALL declararse fijo.

#### Scenario: Comparación por idioma
- **WHEN** se dibuja la figura de dispersión para una dimensión
- **THEN** SHALL mostrar un par de valores por idioma, uno por método, sobre la misma escala

#### Scenario: Dispersión como número reportable
- **WHEN** se muestra la figura
- **THEN** SHALL informar para cada método el rango y la desviación entre idiomas, identificados como la magnitud que se reporta, dado que el contenido no varía y una dispersión menor indica un instrumento más justo

#### Scenario: Todas las dimensiones con método comparable
- **WHEN** la batería cubre las dimensiones que el rediseño convierte de léxico a zero-shot
- **THEN** SHALL poder generarse la figura para cada una de ellas, sin que el conjunto de dimensiones aparezca fijo en el código

#### Scenario: Escritura de derecha a izquierda
- **WHEN** una etiqueta o un texto de la figura está en un idioma de escritura derecha a izquierda
- **THEN** SHALL renderizarse con la forma y el orden correctos

#### Scenario: Demostración sobre perspectiva política
- **WHEN** se ejecuta la batería y se imprime la demostración de sesgo entre idiomas
- **THEN** SHALL construirse sobre la dimensión de perspectiva política, y el valor que reporta SHALL coincidir con el que recalcula la figura correspondiente

#### Scenario: Inversión de signo visible
- **WHEN** el método léxico asigna a un mismo contenido valores de signo opuesto en distintos idiomas
- **THEN** la figura SHALL hacerlo visible como tal, por ser un resultado más fuerte que la mera dispersión

#### Scenario: Idiomas sin observaciones suficientes
- **WHEN** un idioma presente en los datos tiene menos observaciones que el mínimo declarado
- **THEN** SHALL indicarse su número de observaciones o quedar excluido de forma explícita, y NO SHALL dibujarse como si fuera comparable

## ADDED Requirements

### Requirement: Los agregados sobre el corpus se desglosan por estrato
Toda figura que promedie una dimensión sobre el corpus SHALL desglosar por estrato de recolección o SHALL advertir por escrito que no lo hace, y SHALL señalar cuándo un agregado mezcla estratos cuya consulta buscaba expresamente la dimensión promediada.

#### Scenario: Agregado dirigido por la consulta
- **WHEN** una parte del corpus se recolectó con consultas dirigidas a la dimensión que se está promediando
- **THEN** SHALL emitirse una alerta escrita indicando qué proporción del corpus proviene de esas consultas y que el promedio no es reportable como hallazgo sobre la población

#### Scenario: Desglose disponible
- **WHEN** el marco de valores trae estratos poblados
- **THEN** las figuras agregadas SHALL poder presentarse por estrato sin cambios de código

### Requirement: Comparación entre texto original y traducción
Cuando el corpus aporte traducción, el sistema SHALL producir una figura que compare el método léxico sobre el texto original contra el mismo método sobre la traducción, y SHALL declarar qué mide esa comparación.

#### Scenario: Tres métodos en la misma figura
- **WHEN** se dibuja la comparación sobre una dimensión con método léxico
- **THEN** SHALL distinguir el léxico sobre el original, el léxico sobre la traducción y el rediseño, por forma de marcador y etiqueta directa además del tono

#### Scenario: Efecto de la traducción declarado
- **WHEN** se presenta esa figura
- **THEN** SHALL declararse que la vía traducida mide el léxico junto con la calidad de una traducción automática, y que ambos efectos no pueden separarse sin traducciones de referencia

#### Scenario: Idiomas invisibles para el léxico
- **WHEN** un idioma del corpus carece de cualquier palabra en las listas del método léxico
- **THEN** la figura de cobertura léxica SHALL informar cuántos textos son invisibles para el método actual por construcción, distinguiéndolo de "no observado en este corpus"
