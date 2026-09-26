## ADDED Requirements

### Requirement: Conjunto de dimensiones medidas
El notebook SHALL medir cinco dimensiones —ambiente, imagen cultural, perspectiva política, prominencia de violencia y seguridad percibida— y NO SHALL medir hospitalidad. Cada dimensión de las tres primeras SHALL formularse como tres hipótesis en competencia: positiva, negativa y de irrelevancia.

#### Scenario: Dimensiones declaradas
- **WHEN** se inspecciona la definición de las dimensiones
- **THEN** SHALL contener exactamente ambiente, imagen cultural y perspectiva política como dimensiones de tres hipótesis, más el grupo de violencia y seguridad de cuatro etiquetas

#### Scenario: Costo derivado del número de etiquetas
- **WHEN** se informa el costo de una corrida
- **THEN** el número de pasadas por texto SHALL derivarse del número de etiquetas declaradas y NO SHALL escribirse como constante

#### Scenario: Hospitalidad retirada
- **WHEN** se busca la dimensión de hospitalidad en cualquier marco, figura o tabla
- **THEN** NO SHALL aparecer, y ninguna celda SHALL fallar por su ausencia

### Requirement: El ancla geográfica no altera el reparto entre hipótesis
El ancla que sitúa la medición en México SHALL residir en la plantilla de hipótesis, de modo que sea idéntica para las tres etiquetas de un mismo grupo, y NO SHALL redactarse dentro de las etiquetas individuales.

#### Scenario: Ancla constante entre etiquetas
- **WHEN** se construyen las hipótesis de una dimensión
- **THEN** la referencia a México SHALL aparecer una sola vez en la plantilla compartida y las etiquetas SHALL quedar redactadas sin ella

#### Scenario: Efecto del ancla verificado y no supuesto
- **WHEN** se evalúa la batería con el ancla en la plantilla y con el ancla en las etiquetas
- **THEN** SHALL informarse la distribución de relevancia de ambas variantes, de modo que la elección quede respaldada por la comparación y no por el argumento

#### Scenario: Irrelevancia no inflada por redacción
- **WHEN** una dimensión supera el umbral que la declara muda
- **THEN** SHALL poder distinguirse si la causa es el corpus o la redacción de las hipótesis, porque la variante alternativa del ancla está medida

### Requirement: Una sola lengua de hipótesis para todo el corpus
Las hipótesis SHALL formularse en una única lengua para todos los textos, sea cual sea el idioma de cada texto, y esa lengua SHALL quedar declarada en la ficha técnica junto con la plantilla y las frases textuales.

#### Scenario: Lengua única
- **WHEN** se evalúan textos en idiomas distintos
- **THEN** SHALL usarse el mismo conjunto de hipótesis en la misma lengua para todos, de modo que el instrumento sea idéntico entre idiomas

#### Scenario: Instrumento citable
- **WHEN** se produce la salida de figuras
- **THEN** SHALL embeber la lengua de las hipótesis, la plantilla y el texto literal de cada hipótesis, para que el instrumento pueda citarse en la tesis como se cita un libro de códigos

### Requirement: Dimensión sin método comparable declarada como tal
Una dimensión que no tenga equivalente en el método léxico SHALL declarar que solo la produce el rediseño, y las figuras que comparan métodos SHALL excluirla por esa declaración y SHALL explicar la exclusión en la propia figura.

#### Scenario: Imagen cultural sin léxico equivalente
- **WHEN** se construye una figura que compara el método actual contra el rediseño
- **THEN** la dimensión de imagen cultural SHALL quedar excluida por no tener método léxico, y NO SHALL dibujarse como un hueco ni como un cero

#### Scenario: Exclusión explicada
- **WHEN** una dimensión queda fuera de una figura comparativa
- **THEN** la figura SHALL indicar por escrito que la dimensión no tiene equivalente en el método actual
