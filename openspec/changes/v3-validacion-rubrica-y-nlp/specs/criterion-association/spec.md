## ADDED Requirements

### Requirement: Asociación por pares sobre presencia binaria
El notebook SHALL medir la asociación entre cada par de criterios usando la presencia binaria (nivel mayor que 0), excluyendo del par los tuits con faltante en cualquiera de los dos criterios, y SHALL mostrar la tabla de contingencia con sus frecuencias esperadas.

#### Scenario: Seis pares
- **WHEN** hay cuatro criterios
- **THEN** SHALL producirse una tabla de 2×2 por cada uno de los seis pares, con observados, esperados y el número de tuits excluidos por faltante

### Requirement: Prueba exacta con corrección por comparaciones múltiples
La prueba principal de asociación SHALL ser la prueba exacta de Fisher bilateral, con valores p corregidos por Holm sobre el conjunto de pares, y la chi cuadrada SHALL reportarse solo como referencia, marcada cuando alguna frecuencia esperada sea menor que 5.

#### Scenario: Esperados bajos
- **WHEN** alguna frecuencia esperada de una tabla es menor que 5
- **THEN** la chi cuadrada de esa tabla SHALL marcarse como no válida y la conclusión SHALL basarse en la prueba exacta

#### Scenario: Corrección aplicada
- **WHEN** se informan los valores p
- **THEN** SHALL mostrarse el valor sin corregir y el corregido por Holm

### Requirement: Tamaño de efecto con intervalo
Cada par SHALL informar el coeficiente phi y la razón de momios con intervalo de confianza, aplicando una corrección de continuidad cuando la tabla tenga celdas con cero.

#### Scenario: Celda con cero
- **WHEN** una tabla tiene alguna celda con frecuencia cero
- **THEN** la razón de momios y su intervalo SHALL calcularse con la corrección declarada y SHALL indicarse que se aplicó

#### Scenario: Matriz de efectos
- **WHEN** se muestran los resultados
- **THEN** SHALL dibujarse una matriz de los seis coeficientes phi con el valor en cada celda

### Requirement: Tres lecturas de la asociación
La asociación SHALL calcularse sobre el corpus completo, sobre el grupo de calificados y estratificada por tipo de consulta, y la lectura sobre calificados SHALL advertir que condicionar a la presencia de algún criterio induce asociación negativa artificial.

#### Scenario: Corpus completo
- **WHEN** se calcula la lectura sobre el corpus
- **THEN** SHALL advertirse que la gran mayoría de tuits sin ningún criterio presente infla la asociación

#### Scenario: Solo calificados
- **WHEN** se calcula la lectura sobre calificados
- **THEN** SHALL advertirse el sesgo por condicionamiento junto a los resultados

#### Scenario: Estratificada
- **WHEN** se calcula la lectura estratificada
- **THEN** SHALL informarse la razón de momios común de Mantel–Haenszel y una prueba de homogeneidad entre estratos, con el tamaño de cada estrato y la regla con la que se asignaron

### Requirement: Traslape definicional declarado
Cuando las definiciones de dos criterios en la rúbrica compartan contenido, la asociación de ese par SHALL presentarse con una nota que lo declare, para que no se lea como hallazgo sobre el discurso.

#### Scenario: Perspectiva política y violencia
- **WHEN** se presenta el par entre perspectiva política y saliencia de violencia
- **THEN** SHALL indicarse que la definición de perspectiva política incluye la gestión de seguridad

### Requirement: Resultados de asociación exportables
Los resultados de las tres lecturas SHALL poder escribirse a un archivo con una fila por par y lectura.

#### Scenario: Archivo de asociación
- **WHEN** se ejecuta la exportación
- **THEN** SHALL escribirse un archivo con par, lectura, n, observados, esperado mínimo, phi, razón de momios con intervalo, p exacto, p corregido y p de chi cuadrada con su marca de validez
