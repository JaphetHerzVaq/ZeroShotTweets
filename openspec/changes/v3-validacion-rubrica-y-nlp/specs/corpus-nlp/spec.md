## ADDED Requirements

### Requirement: Un solo espacio para calificados y no calificados
El agrupamiento SHALL ajustarse una sola vez sobre todos los tuits con texto útil, de modo que calificados y no calificados compartan espacio, clusters y tópicos, y SHALL poder filtrarse o colorearse por grupo.

#### Scenario: Ajuste común
- **WHEN** se ejecuta el agrupamiento
- **THEN** los dos grupos SHALL recibir cluster en el mismo ajuste, y NO SHALL ajustarse un modelo separado para los calificados

#### Scenario: Texto no útil
- **WHEN** un tuit solo contiene enlaces, menciones o medios, o su idioma no es detectable y no tiene palabras
- **THEN** SHALL excluirse del análisis con su número informado por grupo

### Requirement: Agrupamiento por embeddings del texto original
Los clusters SHALL obtenerse de embeddings multilingües del texto original, con reducción de dimensión y un algoritmo que admita ruido, con semilla y parámetros visibles, y SHALL informarse la proporción de tuits sin cluster.

#### Scenario: Independencia de la traducción
- **WHEN** se calculan los embeddings
- **THEN** SHALL usarse el texto original y NO la traducción

#### Scenario: Ruido informado
- **WHEN** termina el agrupamiento
- **THEN** SHALL informarse el número de clusters, su tamaño y la proporción de tuits marcados como ruido, por grupo

#### Scenario: Reproducibilidad
- **WHEN** se repite la sección con la misma semilla, parámetros y versiones
- **THEN** SHALL obtenerse la misma asignación, y semilla, parámetros y versiones SHALL constar en la ficha técnica

### Requirement: Análisis lingüístico con spaCy sobre la traducción
Los lemas, entidades y dependencias SHALL obtenerse con un pipeline de spaCy en español sobre la traducción, con un reconocedor de entidades por diccionario ejecutado antes del estadístico, y el uso de la traducción SHALL declararse.

#### Scenario: Diccionario de México editable
- **WHEN** se prepara el pipeline
- **THEN** el diccionario de entidades de México SHALL estar declarado en una celda editable con sus categorías, y SHALL informarse cuántos tuits reconoce por grupo

#### Scenario: Declaración de la traducción
- **WHEN** se presentan resultados de esta sección
- **THEN** SHALL declararse que la traducción es automática, que se produjo como apoyo de lectura humana, y que cinco traducciones se completaron manualmente con otro modelo

### Requirement: Tópicos por cluster
Cada cluster SHALL describirse con sus términos más distintivos calculados por TF-IDF de clase sobre lemas de sustantivos, nombres propios y adjetivos, junto con tuits de ejemplo.

#### Scenario: Descripción de cluster
- **WHEN** se muestra un cluster
- **THEN** SHALL listarse su tamaño, la proporción de calificados, sus términos distintivos y ejemplos con texto original y traducción

### Requirement: Grafo de co-ocurrencia de entidades
El notebook SHALL construir un grafo cuyos nodos sean entidades normalizadas y cuyas aristas unan entidades que aparecen en el mismo tuit, ponderadas por información mutua puntual, limitado por parámetros visibles de número de nodos y co-ocurrencia mínima, y dibujado con Apache ECharts.

#### Scenario: Grafo acotado
- **WHEN** se dibuja el grafo
- **THEN** SHALL mostrar como máximo el número de nodos declarado, con tamaño por frecuencia, color por categoría y aristas por encima del umbral declarado

#### Scenario: Filtro por grupo
- **WHEN** se consulta el grafo
- **THEN** SHALL poder mostrarse para calificados, no calificados o todos

### Requirement: Grafo de relaciones sujeto–verbo–objeto
El notebook SHALL extraer tripletas de sujeto, verbo y objeto de las dependencias en las que al menos un extremo sea una entidad, y SHALL dibujarlas como grafo dirigido con el verbo como etiqueta de la arista, declarando su carácter exploratorio.

#### Scenario: Relaciones con entidad
- **WHEN** se extraen relaciones
- **THEN** SHALL conservarse solo las tripletas con al menos una entidad y con frecuencia igual o mayor que el umbral declarado

### Requirement: Auditoría de la colecta
El notebook SHALL cruzar clusters con consulta de origen y período, y SHALL mostrar qué consultas aportan cada cluster y qué clusters casi no tienen calificados.

#### Scenario: Cruce cluster–consulta–período
- **WHEN** se ejecuta la auditoría
- **THEN** SHALL mostrarse una figura y una tabla del número de tuits por cluster, consulta y período, con la proporción de calificados de cada cluster

### Requirement: Candidatos a falso negativo para revisión manual
El notebook SHALL listar como candidatos a falso negativo los tuits no calificados que mencionan México según el diccionario y que superan el umbral de relevancia en alguna dimensión zero-shot o el umbral declarado de prominencia de violencia, y SHALL presentarlos como candidatos y no como errores de la rúbrica.

#### Scenario: Motivo explícito
- **WHEN** un tuit entra en la lista
- **THEN** SHALL indicarse qué condición lo incluyó, con los valores zero-shot, la justificación de la rúbrica de cada criterio y su cluster

#### Scenario: Sin tasa de error
- **WHEN** se presenta la lista
- **THEN** NO SHALL calcularse ni presentarse una tasa de falsos negativos, y SHALL indicarse que requiere revisión humana

#### Scenario: Umbral de prominencia congelado
- **WHEN** se fija el umbral de prominencia de violencia para candidatos
- **THEN** SHALL declararse en la configuración antes de listar candidatos, y NO SHALL ajustarse según el número de candidatos resultante

### Requirement: Temas fuera de la rúbrica
El notebook SHALL identificar clusters con alta proporción de tuits que mencionan México y baja proporción de calificados, y SHALL presentarlos como temas candidatos a dimensión con sus términos distintivos y ejemplos.

#### Scenario: Lista de temas
- **WHEN** se ejecuta la sección
- **THEN** SHALL listarse cada cluster que cumpla ambos umbrales declarados, con su tamaño, proporciones y descripción

### Requirement: Contraste de vocabulario entre calificados y no calificados
El notebook SHALL comparar lemas y entidades entre los dos grupos con log-odds con prior informativo, y SHALL mostrar los términos más característicos de cada grupo con su puntuación.

#### Scenario: Términos característicos
- **WHEN** se ejecuta el contraste
- **THEN** SHALL mostrarse los términos más característicos de cada grupo y su frecuencia en ambos
