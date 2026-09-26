## MODIFIED Requirements

### Requirement: El tipo de escala se declara por criterio
Cada criterio SHALL declarar si su escala es de valencia o de presencia binaria, y la paleta, el orden de niveles, las figuras y **las tablas** SHALL derivarse de esa declaración. Ninguna tabla SHALL presentar la cuenta de un criterio de presencia en la misma columna que un nivel de valencia.

#### Scenario: Criterio de valencia
- **WHEN** un criterio se declara de valencia
- **THEN** sus niveles 1 a 5 SHALL dibujarse con una paleta divergente de muy negativo a muy positivo, con el nivel neutro en un tono neutro

#### Scenario: Criterio binario
- **WHEN** un criterio se declara de presencia binaria
- **THEN** su nivel positivo SHALL dibujarse con un color propio que NO SHALL coincidir con el de un nivel de valencia negativa, y NO SHALL presentarse como una distribución de valencia

#### Scenario: Cuenta de presencia fuera de las columnas de valencia
- **WHEN** una tabla resume los niveles de todos los criterios
- **THEN** la cuenta de un criterio de presencia SHALL ocupar una columna propia, y NO SHALL colocarse bajo el encabezado de un nivel de valencia

#### Scenario: Columna de valencia sumable
- **WHEN** un lector recorre de arriba abajo la columna de un nivel de valencia
- **THEN** todos los números de esa columna SHALL significar lo mismo, de modo que su suma tenga sentido
