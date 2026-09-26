## MODIFIED Requirements

### Requirement: Valencia y ausencia como ejes separados
El marco de valores SHALL mantener la valencia y la relevancia como columnas independientes, SHALL declarar para cada dimensión si su escala es de valencia o de prominencia, SHALL declarar qué métodos producen cada dimensión, y NO SHALL producir ninguna columna que combine ambos ejes en un solo escalar.

#### Scenario: Sin producto de valencia por relevancia
- **WHEN** se inspecciona cualquier marco, tabla o dato serializado hacia las figuras
- **THEN** NO SHALL existir ninguna magnitud que resulte de multiplicar la valencia por la relevancia, ni de ponderar una por la otra

#### Scenario: Relevancia ausente para el método léxico
- **WHEN** se registran los valores de un método léxico, que no produce relevancia
- **THEN** la relevancia SHALL quedar marcada como no disponible y NO SHALL sustituirse por cero, que significaría "no habló del tema"

#### Scenario: Escala declarada por dimensión
- **WHEN** una figura necesita saber si una dimensión va de menos uno a uno o de cero a uno
- **THEN** SHALL leerlo del marco y no inferirlo de los valores observados

#### Scenario: Dimensión producida por un solo método
- **WHEN** una dimensión no tiene equivalente en el método léxico
- **THEN** el marco SHALL declararlo, y las figuras que comparan métodos SHALL excluirla a partir de esa declaración en lugar de descubrirlo por ausencia de datos

### Requirement: Columnas de procedencia reservadas para el corpus
El marco de valores SHALL incluir columnas opcionales de identificador de tweet, fecha de publicación, idioma y estrato de recolección, vacías cuando la entrada sea una lista de textos y pobladas cuando la entrada provenga de un corpus, y ninguna figura SHALL exigir que estén pobladas.

#### Scenario: Entrada sin procedencia
- **WHEN** la entrada es una lista de textos sin identificador ni fecha
- **THEN** las columnas de procedencia SHALL existir vacías y todas las figuras SHALL construirse igualmente

#### Scenario: Entrada con idioma
- **WHEN** la entrada declara el idioma de cada texto, como ocurre con la batería de ejemplo
- **THEN** la columna de idioma SHALL poblarse y las figuras que comparan idiomas SHALL usarla

#### Scenario: Entrada desde corpus
- **WHEN** la entrada proviene de un corpus con identificador y fecha
- **THEN** las columnas de procedencia SHALL poblarse sin que las figuras existentes requieran cambios

#### Scenario: Entrada desde corpus con estratos
- **WHEN** el corpus declara con qué consulta y en qué modalidad se recolectó cada texto
- **THEN** esos campos SHALL poblarse como columnas del marco y quedar disponibles para desglosar cualquier agregado

## ADDED Requirements

### Requirement: Más de dos métodos por dimensión
El marco de valores SHALL admitir más de dos métodos sobre una misma dimensión, distinguidos por el valor de la columna de método, sin que ello cambie su forma ni añada columnas.

#### Scenario: Léxico sobre dos columnas de texto
- **WHEN** el corpus aporta texto original y traducción y se mide el método léxico sobre ambos
- **THEN** SHALL registrarse como dos valores distintos de la columna de método sobre las mismas dimensiones, y NO SHALL añadirse columnas nuevas al marco

#### Scenario: Origen del texto identificable
- **WHEN** se inspecciona una fila producida por un método léxico
- **THEN** SHALL poder determinarse sobre qué columna de texto se calculó

#### Scenario: Guardia de columnas numéricas preservada
- **WHEN** se añaden métodos o columnas de procedencia al marco
- **THEN** la comprobación que impide columnas numéricas no previstas SHALL seguir vigente y SHALL fallar ante cualquier magnitud que combine valencia y relevancia
