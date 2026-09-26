## MODIFIED Requirements

### Requirement: Cobertura de la batería por idioma y por dimensión
La batería SHALL contener cinco frases —ambiente positivo, imagen cultural positiva, perspectiva política negativa, violencia o inseguridad, y un control sin contenido evaluable— cada una en los seis grupos de idioma que la batería usa como instrumento de prueba, y SHALL declarar para cada texto su frase de origen y su idioma.

#### Scenario: Contenido equivalente entre idiomas
- **WHEN** se comparan las seis versiones de una misma frase
- **THEN** SHALL corresponder al mismo contenido, de modo que cualquier diferencia de medición entre ellas sea atribuible al instrumento y no al texto

#### Scenario: Todas las dimensiones alcanzadas
- **WHEN** se ejecuta la batería completa
- **THEN** cada una de las cinco dimensiones reportadas SHALL recibir al menos un texto que la active

#### Scenario: Control mudo
- **WHEN** se evalúa el texto de control, que no habla de ambiente, de comida, lugares o cultura, ni de autoridades
- **THEN** su relevancia en esas tres dimensiones SHALL ser baja, y ese resultado SHALL quedar visible como la demostración de que el eje de relevancia distingue "no habló" de "juzgó neutro"

#### Scenario: Frases reasignadas sin traducir de nuevo
- **WHEN** una frase existente pasa a probar una dimensión distinta de la que probaba
- **THEN** SHALL conservar sus seis versiones tal cual, y solo las frases genuinamente nuevas SHALL requerir traducción

#### Scenario: Texto sobre comida como sonda de imagen cultural
- **WHEN** se evalúa el texto de la batería que habla de comida y de desplazarse por la ciudad
- **THEN** SHALL activar la dimensión de imagen cultural con relevancia alta, y NO SHALL usarse como control sin contenido evaluable

## ADDED Requirements

### Requirement: Procedencia de las traducciones nuevas declarada
Toda frase de la batería redactada para este change SHALL declarar quién o qué produjo sus traducciones, junto a las que ya existían, de modo que la salida de figuras permita auditarlas.

#### Scenario: Frase nueva auditable
- **WHEN** se embebe la batería en la salida de figuras
- **THEN** SHALL incluirse el texto completo de cada versión y la declaración de cómo se obtuvo la traducción
