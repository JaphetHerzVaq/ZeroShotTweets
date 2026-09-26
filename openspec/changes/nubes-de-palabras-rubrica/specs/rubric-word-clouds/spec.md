## ADDED Requirements

### Requirement: Polaridad derivada de los criterios de valencia
El notebook SHALL derivar una polaridad por tuit a partir de los niveles de la rúbrica, usando únicamente los criterios de escala `valencia` y nunca los de escala `presencia`, y SHALL asignarla en la misma función que ya codifica la rúbrica, de modo que la regla viva en un solo lugar.

#### Scenario: Criterio de presencia excluido
- **WHEN** un criterio está declarado con escala `presencia`
- **THEN** su nivel NO SHALL contribuir a la polaridad, y un tuit calificado sólo por ese criterio SHALL recibir polaridad `sin_polaridad`

#### Scenario: Faltantes y ausencia
- **WHEN** un criterio es `BLOQUEADO` o su nivel es 0
- **THEN** NO SHALL contribuir a la polaridad, y un tuit sin ningún criterio presente SHALL quedar fuera de los grupos de polaridad

### Requirement: Partición disjunta con los polos primero
La polaridad SHALL asignarse dando prioridad a los polos sobre la ambivalencia: `positivo` cuando hay algún nivel 4–5 y ningún 1–2, `negativo` cuando hay algún 1–2 y ningún 4–5, y `ambivalente` sólo cuando todos los criterios de valencia presentes valen 3. La partición de los tuits calificados SHALL ser disjunta y exhaustiva, y el notebook SHALL comprobarlo con una aserción que detenga la ejecución si deja de cumplirse.

#### Scenario: Polo positivo con ambivalencia secundaria
- **WHEN** un tuit tiene un criterio en nivel 4 o 5 y otro en nivel 3
- **THEN** SHALL clasificarse como `positivo` y NO como `ambivalente`

#### Scenario: Polo negativo con ambivalencia secundaria
- **WHEN** un tuit tiene un criterio en nivel 3 y otro en nivel 1 o 2
- **THEN** SHALL clasificarse como `negativo` y NO como `ambivalente`

#### Scenario: Partición comprobada
- **WHEN** termina la asignación de polaridad
- **THEN** la suma de los grupos `positivo`, `negativo`, `ambivalente` y `sin_polaridad` SHALL ser igual al número de calificados, ningún tuit SHALL pertenecer a dos grupos, y si no se cumple la ejecución SHALL detenerse con un mensaje que nombre los tuits en conflicto

#### Scenario: Presencia de violencia no es polaridad negativa
- **WHEN** un tuit recibe nivel 1 en saliencia de violencia y no tiene ningún criterio de valencia presente
- **THEN** SHALL quedar en `sin_polaridad`, y NO SHALL contarse como negativo

### Requirement: Nubes descriptivas por frecuencia
El notebook SHALL mostrar dos nubes de palabras pesadas por frecuencia de lema: una sobre el corpus completo y otra sobre los tuits calificados, y cada panel SHALL declarar su universo y su número de tuits.

#### Scenario: Universos distintos y declarados
- **WHEN** se dibujan las dos nubes descriptivas
- **THEN** una SHALL cubrir todos los tuits del corpus y la otra sólo los calificados, y cada panel SHALL indicar cuál es cuál y con cuántos tuits

#### Scenario: Lectura de la colecta contra la rúbrica
- **WHEN** se presentan las dos nubes descriptivas
- **THEN** el panel SHALL explicar que la primera describe lo que trajo la colecta y la segunda lo que la rúbrica reconoció

### Requirement: Nubes de polaridad por log-odds
El notebook SHALL mostrar una nube por cada grupo de polaridad —`positivo`, `negativo` y `ambivalente`— pesada por la puntuación z de log-odds con prior informativo, calculada de cada grupo contra el resto de los tuits con polaridad. Los tuits `sin_polaridad` NO SHALL entrar ni en las nubes ni en el prior. El peso de estas nubes NO SHALL ser la frecuencia cruda.

#### Scenario: Prior restringido a los tuits con polaridad
- **WHEN** se calcula el contraste de un grupo de polaridad
- **THEN** el prior SHALL construirse únicamente con los grupos `positivo`, `negativo` y `ambivalente`, y los tuits `sin_polaridad` SHALL quedar fuera

#### Scenario: Sólo términos característicos del grupo
- **WHEN** se dibuja la nube de un grupo
- **THEN** SHALL incluir los términos con z positiva para ese grupo, y el tamaño de cada término SHALL crecer con su z

#### Scenario: Peso declarado en el panel
- **WHEN** se presenta una nube de polaridad
- **THEN** el panel SHALL declarar que el tamaño es la puntuación z de log-odds con prior informativo y no la frecuencia, y SHALL citar la fuente del estimador

### Requirement: Aviso de vocabulario escaso
Cada nube SHALL declarar cuántos tuits y cuántos términos la sostienen, y cuando un grupo quede por debajo del vocabulario mínimo declarado SHALL mostrarse un aviso visible en el panel en lugar de dibujar la nube como si fuera comparable a las demás.

#### Scenario: Grupo con pocos términos
- **WHEN** un grupo aporta menos términos que el mínimo declarado
- **THEN** el panel SHALL mostrar un aviso que diga cuántos tuits y términos tiene y advierta que no es comparable con las otras nubes

#### Scenario: Grupo sin términos
- **WHEN** un grupo no aporta ningún término que supere el umbral de frecuencia
- **THEN** SHALL omitirse la nube con un aviso que explique el motivo, y NO SHALL dibujarse un lienzo vacío

#### Scenario: Recuento siempre visible
- **WHEN** se dibuja cualquiera de las cinco nubes
- **THEN** el panel SHALL mostrar el número de tuits y el número de términos representados

### Requirement: Tuits sin polaridad contados en nota
Los tuits calificados sin ningún criterio de valencia presente SHALL contarse en una nota del panel de polaridad, con el motivo de su exclusión.

#### Scenario: Nota de exclusión
- **WHEN** se presentan las nubes de polaridad
- **THEN** SHALL indicarse cuántos tuits calificados quedaron fuera por no tener ningún criterio de valencia, y SHALL explicarse que la saliencia de violencia es presencia y no valencia

### Requirement: Trazado determinista y reproducible
Las nubes SHALL dibujarse de forma determinista: mismo lienzo, misma disposición, sin rotación aleatoria, de modo que repetir la corrida o redimensionar la ventana NO cambie la figura. Los parámetros de trazado SHALL constar en la ficha técnica de la sección.

#### Scenario: Repetición de la corrida
- **WHEN** se vuelve a generar la página con los mismos datos, parámetros y versiones
- **THEN** cada nube SHALL mostrar los mismos términos en la misma posición y el mismo tamaño

#### Scenario: Cambio de tamaño de ventana
- **WHEN** el lector redimensiona la ventana del navegador
- **THEN** la disposición de la nube NO SHALL recomponerse en un orden distinto

#### Scenario: Parámetros en la ficha
- **WHEN** se consulta la ficha técnica de la sección
- **THEN** SHALL constar el umbral de frecuencia, el número máximo de términos por nube y los parámetros de trazado

### Requirement: Lemas de la traducción como unidad
Los términos de todas las nubes SHALL ser lemas obtenidos con spaCy sobre la traducción al español, restringidos a las categorías gramaticales ya declaradas para los tópicos, y SHALL reutilizarse los lemas calculados en la sección de análisis lingüístico sin volver a procesar el texto.

#### Scenario: Corpus multilingüe en un espacio común
- **WHEN** se construyen las nubes de un corpus con varios idiomas
- **THEN** SHALL usarse la traducción y NO el texto original, para que los términos sean comparables entre idiomas

#### Scenario: Declaración de la traducción
- **WHEN** se presenta cualquiera de las nubes
- **THEN** SHALL declararse que los términos vienen de una traducción automática producida como apoyo de lectura humana

### Requirement: Paleta y tipos existentes
Las nubes SHALL tomar sus colores de la paleta ya declarada del notebook. Las nubes descriptivas SHALL usar una tinta neutra, porque en ellas el color no codifica nada, y las de polaridad SHALL usar un color por grupo.

#### Scenario: Sin color inventado
- **WHEN** se asigna color a los términos
- **THEN** SHALL usarse valores de la paleta declarada, y NO SHALL asignarse color al azar por término

### Requirement: Segundo modo de falla de la biblioteca declarado
La página SHALL distinguir el fallo de carga del motor de gráficas del fallo de carga de la extensión de nubes, y cuando falte la extensión SHALL avisarlo en lugar de mostrar paneles vacíos.

#### Scenario: Extensión ausente
- **WHEN** el motor de gráficas carga pero la extensión de nubes no
- **THEN** los paneles de nube SHALL mostrar un aviso que nombre la extensión faltante, y el resto de la página SHALL seguir dibujándose

#### Scenario: Motor ausente
- **WHEN** el motor de gráficas no carga
- **THEN** SHALL mantenerse el aviso que ya existe hoy para ese caso
