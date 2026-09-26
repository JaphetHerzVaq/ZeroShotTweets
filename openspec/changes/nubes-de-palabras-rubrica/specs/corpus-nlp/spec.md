## MODIFIED Requirements

### Requirement: Contraste de vocabulario entre calificados y no calificados
El notebook SHALL comparar lemas y entidades entre dos conjuntos cualesquiera de tuits con log-odds con prior informativo, y SHALL mostrar los términos más característicos de cada lado con su puntuación. Los rótulos del resultado SHALL derivarse de los conjuntos comparados y NO SHALL estar escritos a mano, de modo que el mismo estimador sirva para el contraste entre calificados y no calificados y para cualquier otro par sin que la página nombre mal los grupos. El contraste entre calificados y no calificados SHALL seguir presentándose como hasta ahora.

#### Scenario: Términos característicos
- **WHEN** se ejecuta el contraste
- **THEN** SHALL mostrarse los términos más característicos de cada grupo y su frecuencia en ambos

#### Scenario: Rótulos derivados de los grupos comparados
- **WHEN** se compara un par de conjuntos distinto de calificados y no calificados
- **THEN** las llaves del resultado y los rótulos del panel SHALL nombrar esos conjuntos, y NO SHALL decir «calificados» ni «no calificados»

#### Scenario: El contraste original se conserva
- **WHEN** se generalizan los rótulos
- **THEN** el contraste entre calificados y no calificados SHALL seguir mostrándose con el mismo estimador y los mismos umbrales que hoy
