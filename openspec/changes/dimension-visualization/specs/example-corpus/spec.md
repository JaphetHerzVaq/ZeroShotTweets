## ADDED Requirements

### Requirement: Batería de ejemplo ejecutable sin datos del usuario
El notebook SHALL traer un corpus de ejemplo embebido que permita ejecutarlo de principio a fin y producir todas las figuras sin que el usuario aporte textos, y SHALL conservar el mecanismo que impide ejecutar con textos de relleno sin sustituir.

#### Scenario: Sesión limpia sin intervención
- **WHEN** se ejecuta el notebook de principio a fin en una sesión limpia sin modificar ninguna celda
- **THEN** la ejecución SHALL completarse sin excepción y SHALL producir todas las figuras

#### Scenario: Relleno sin sustituir
- **WHEN** el usuario sustituye la batería por textos propios y deja alguno con el marcador de relleno
- **THEN** la ejecución SHALL detenerse con un mensaje que indique cuántos textos de relleno quedan

#### Scenario: Sustitución por textos propios
- **WHEN** el usuario sustituye la batería completa por sus propios textos
- **THEN** todas las figuras SHALL construirse sobre esos textos sin requerir cambios de código

### Requirement: Cobertura de la batería por idioma y por dimensión
La batería SHALL contener cuatro frases —hospitalidad positiva, gobernanza negativa, violencia o inseguridad, y un control sin contenido evaluable— cada una en los seis grupos de idioma que el proyecto recolecta, y SHALL declarar para cada texto su frase de origen y su idioma.

#### Scenario: Contenido equivalente entre idiomas
- **WHEN** se comparan las seis versiones de una misma frase
- **THEN** SHALL corresponder al mismo contenido, de modo que cualquier diferencia de medición entre ellas sea atribuible al instrumento y no al texto

#### Scenario: Todas las dimensiones alcanzadas
- **WHEN** se ejecuta la batería completa
- **THEN** cada una de las cinco dimensiones reportadas SHALL recibir al menos un texto que la active

#### Scenario: Control mudo
- **WHEN** se evalúa el texto de control, que no habla de hospitalidad, ambiente ni autoridades
- **THEN** su relevancia en esas tres dimensiones SHALL ser baja, y ese resultado SHALL quedar visible como la demostración de que el eje de relevancia distingue "no habló" de "juzgó neutro"

### Requirement: La batería se identifica como instrumento de prueba
El sistema SHALL rotular de forma visible toda figura y toda tabla construida sobre la batería de ejemplo, indicando que no es una muestra del corpus y que sus valores no son reportables como hallazgo.

#### Scenario: Figura sobre la batería
- **WHEN** se genera una figura y la entrada activa es la batería de ejemplo
- **THEN** la figura SHALL llevar un rótulo visible que la identifique como batería de prueba del instrumento

#### Scenario: Figura sobre textos del usuario
- **WHEN** la entrada activa no es la batería de ejemplo
- **THEN** el rótulo de batería de prueba NO SHALL aparecer

#### Scenario: Batería auditable
- **WHEN** se genera la página de figuras
- **THEN** SHALL incluir los textos de la batería completos, para que la equivalencia entre traducciones pueda ser verificada por el lector

### Requirement: Costo de ejecución de la batería declarado y evitable
El sistema SHALL medir e informar el tiempo que toma evaluar la batería, y SHALL permitir omitirla mediante un parámetro cuando el usuario aporte sus propios textos.

#### Scenario: Tiempo informado
- **WHEN** termina la evaluación de la batería
- **THEN** el sistema SHALL informar el tiempo total, el número de textos y el número de pasadas de modelo realizadas

#### Scenario: Batería desactivada
- **WHEN** el parámetro correspondiente indica no evaluar la batería
- **THEN** la sección de la batería SHALL omitirse y las figuras que dependen exclusivamente de ella SHALL indicar que no hay datos, sin interrumpir la ejecución

#### Scenario: Ejecución sin GPU
- **WHEN** no hay GPU disponible
- **THEN** el sistema SHALL advertir, antes de empezar, que la batería requiere una cantidad de pasadas de modelo que puede resultar impracticable en CPU
