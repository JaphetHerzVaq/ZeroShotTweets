## ADDED Requirements

### Requirement: La exportación incluye la codificación de la rúbrica y los resultados del análisis
El archivo ancho SHALL incluir, además de las columnas originales y las del instrumento, la clase y el nivel numérico de cada criterio según la codificación única, el grupo del tuit y los resultados del análisis NLP, y SHALL incluir las probabilidades de la compuerta cuando el diseño de relevancia la use.

#### Scenario: Columnas de rúbrica codificadas
- **WHEN** la entrada trae calificaciones
- **THEN** SHALL añadirse por criterio una columna de clase y una de nivel numérico, y una columna de grupo por tuit, sin modificar las columnas originales de la rúbrica

#### Scenario: Columnas de NLP
- **WHEN** se ejecutó el análisis NLP
- **THEN** SHALL añadirse cluster, tópico del cluster, mención de México, coordenadas de proyección, marca de candidato a falso negativo y su motivo

#### Scenario: Probabilidades de la compuerta
- **WHEN** el diseño de relevancia es la compuerta
- **THEN** la probabilidad de la compuerta de cada dimensión SHALL exportarse como columna, de modo que la relevancia pueda recalcularse desde el archivo

#### Scenario: Huella del instrumento en el archivo ancho
- **WHEN** se exporta el archivo ancho
- **THEN** SHALL incluir la huella de las hipótesis con que se produjeron sus valores

### Requirement: Volcado de la corrida reutilizable
Tras evaluar, el notebook SHALL escribir un volcado con los resultados crudos del instrumento, los identificadores en orden y la huella del instrumento, y la exportación SHALL completarlo con la demostración entre idiomas y la comparación del ancla cuando existan, de modo que la opción de carga de una corrida previa pueda reconstruir todos los marcos y figuras heredados.

#### Scenario: Volcado tras evaluar
- **WHEN** termina la evaluación del instrumento
- **THEN** SHALL escribirse el volcado en la carpeta de salida antes de continuar con las secciones siguientes

#### Scenario: Volcado completo al exportar
- **WHEN** se ejecuta la exportación
- **THEN** el volcado SHALL incluir también la demostración entre idiomas y la comparación del ancla si se calcularon

### Requirement: Archivo de candidatos a falso negativo
La exportación SHALL escribir un archivo separado con los candidatos a falso negativo, con una fila por tuit, y SHALL nombrarlo y encabezarlo como material para revisión manual.

#### Scenario: Contenido del archivo
- **WHEN** hay candidatos
- **THEN** el archivo SHALL contener identificador, texto original, traducción, idioma, consulta, período, valores zero-shot, justificaciones de la rúbrica, cluster, tópico, motivo de inclusión y una columna vacía para la decisión del revisor

#### Scenario: Sin candidatos
- **WHEN** no hay candidatos
- **THEN** SHALL informarse y NO SHALL escribirse un archivo vacío que parezca resultado

### Requirement: Las figuras nuevas se exportan en el archivo de figuras
Un archivo HTML de figuras SHALL incluir las figuras de resultados de la rúbrica, validación convergente, asociación entre criterios y análisis NLP, SHALL poder abrirse sin el notebook, y el archivo de figuras del instrumento SHALL seguir escribiéndose en la carpeta de salida.

#### Scenario: Archivo autocontenido
- **WHEN** se abre el HTML exportado en un navegador
- **THEN** SHALL mostrar todas las secciones con sus rótulos de procedencia y sus notas de constructo
