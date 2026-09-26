## ADDED Requirements

### Requirement: Las calificaciones de la rúbrica se cargan del mismo archivo que el corpus
El notebook SHALL leer las calificaciones de la rúbrica de las columnas por criterio del archivo de entrada, SHALL identificar los criterios a partir de los nombres de columna y NO SHALL requerir un segundo archivo para obtenerlas.

#### Scenario: Criterios detectados
- **WHEN** el archivo de entrada contiene columnas de nivel, aplicabilidad y justificación para cuatro criterios
- **THEN** SHALL informarse qué criterios se detectaron, con su nombre corto y el número de tuits por clase

#### Scenario: Faltan columnas de rúbrica
- **WHEN** el archivo de entrada no contiene columnas de calificación
- **THEN** la sección de resultados de la rúbrica y todas las que dependen de ella SHALL omitirse con un aviso explícito, sin impedir que el instrumento zero-shot corra

### Requirement: Una sola codificación de la ausencia y del dato faltante
Cada calificación SHALL clasificarse en exactamente una clase —ausencia, valencia, presencia o faltante— según la regla declarada: el nivel 0 y la marca de no aplicable SHALL ser ausencia con nivel numérico 0, un bloqueo del proveedor SHALL ser faltante sin nivel numérico, y los niveles mayores que 0 SHALL ser valencia en los criterios de valencia y presencia en el criterio binario.

#### Scenario: No aplicable
- **WHEN** una calificación viene marcada como no aplicable y sin nivel
- **THEN** SHALL clasificarse como ausencia con nivel numérico 0

#### Scenario: Nivel cero explícito
- **WHEN** una calificación viene marcada como aplicable con nivel 0
- **THEN** SHALL clasificarse como ausencia con nivel numérico 0, idéntica a la anterior para todo cálculo

#### Scenario: Bloqueo
- **WHEN** una calificación viene marcada como bloqueada
- **THEN** SHALL clasificarse como faltante, NO SHALL contarse como ausencia ni como presencia, y SHALL quedar fuera de numeradores y denominadores

#### Scenario: Colisión informada
- **WHEN** se construye la clasificación
- **THEN** SHALL informarse por criterio cuántas ausencias provienen de la marca de no aplicable y cuántas de un nivel 0 explícito

### Requirement: El tipo de escala se declara por criterio
Cada criterio SHALL declarar si su escala es de valencia o de presencia binaria, y la paleta, el orden de niveles y las figuras SHALL derivarse de esa declaración.

#### Scenario: Criterio de valencia
- **WHEN** un criterio se declara de valencia
- **THEN** sus niveles 1 a 5 SHALL dibujarse con una paleta divergente de muy negativo a muy positivo, con el nivel neutro en un tono neutro

#### Scenario: Criterio binario
- **WHEN** un criterio se declara de presencia binaria
- **THEN** su nivel positivo SHALL dibujarse con un color propio que NO SHALL coincidir con el de un nivel de valencia negativa, y NO SHALL presentarse como una distribución de valencia

### Requirement: Grupos de tuits definidos por la rúbrica
El notebook SHALL definir como calificado todo tuit con nivel mayor que 0 en al menos un criterio, y como no calificado al resto, e SHALL informar el tamaño de cada grupo y cuántos tuits no calificados tienen algún criterio faltante.

#### Scenario: Tamaños informados
- **WHEN** se construyen los grupos
- **THEN** SHALL informarse el número de calificados, de no calificados y de no calificados con algún bloqueo

#### Scenario: Tuit con bloqueo y otro criterio presente
- **WHEN** un tuit tiene un criterio faltante y otro con nivel mayor que 0
- **THEN** SHALL pertenecer al grupo de calificados

### Requirement: Reproducción de los agregados de la rúbrica por día y período
La sección inicial SHALL reproducir, desde el archivo de entrada, el volumen diario por idioma, la saliencia diaria por criterio, la valencia diaria por criterio, y la distribución de niveles en todo el corpus y por período, con días cortados en la zona horaria declarada y períodos de límite inferior inclusivo y superior exclusivo.

#### Scenario: Día local
- **WHEN** un tuit se publicó a una hora UTC que corresponde al día anterior en la zona horaria declarada
- **THEN** SHALL contarse en el día local y en el período que le corresponde a ese día

#### Scenario: Denominador de la saliencia
- **WHEN** se calcula la saliencia de un criterio en un día
- **THEN** SHALL dividirse la cuenta de valencia o presencia entre la suma de valencia o presencia más ausencia, excluyendo los faltantes

#### Scenario: Filtros equivalentes
- **WHEN** se consultan las figuras de la sección
- **THEN** SHALL poder filtrarse por idioma y por tuits autosuficientes, alternar entre proporción y conteo absoluto, y activar una media móvil con la ventana declarada

#### Scenario: Autosuficiencia derivada
- **WHEN** se determina si un tuit es autosuficiente
- **THEN** SHALL considerarse no autosuficiente si es respuesta, si su texto empieza con una mención, si es retweet o si es cita

### Requirement: Contraste automático contra el HTML original
Cuando el HTML de calificaciones generado por EvaluadorTweets esté disponible en el directorio de trabajo, el notebook SHALL extraer sus datos embebidos y comparar los conteos por criterio, clase y nivel contra los recalculados, y SHALL poder mostrar el HTML original.

#### Scenario: Conteos coincidentes
- **WHEN** los conteos recalculados coinciden con los del HTML original
- **THEN** SHALL informarse la coincidencia

#### Scenario: Conteos distintos
- **WHEN** algún conteo difiere
- **THEN** SHALL listarse cada diferencia por criterio, clase y nivel como error de réplica

#### Scenario: HTML ausente
- **WHEN** el HTML original no está disponible
- **THEN** la sección SHALL completarse igualmente, indicando que el contraste no se realizó
