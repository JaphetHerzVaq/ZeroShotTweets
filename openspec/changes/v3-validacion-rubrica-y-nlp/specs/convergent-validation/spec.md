## ADDED Requirements

### Requirement: Correspondencia declarada entre criterios y dimensiones
El notebook SHALL declarar explícitamente qué magnitud del instrumento zero-shot se contrasta con cada criterio de la rúbrica, junto con una nota de constructo que diga qué mide cada uno, y NO SHALL inferir la correspondencia de los nombres.

#### Scenario: Tabla de correspondencia
- **WHEN** comienza la sección de validación
- **THEN** SHALL mostrarse, por criterio, la dimensión zero-shot, la magnitud usada como relevancia o prominencia, y la nota de constructo de ambos lados

#### Scenario: Dimensión sin contraparte
- **WHEN** una magnitud zero-shot no tiene criterio de rúbrica correspondiente
- **THEN** SHALL quedar fuera de la validación con la razón declarada

### Requirement: La validación se une por identificador
Los valores zero-shot y las calificaciones de la rúbrica SHALL unirse por identificador de tuit, y toda fila que no se pueda unir SHALL contarse e informarse.

#### Scenario: Unión completa
- **WHEN** todos los identificadores evaluados existen en la rúbrica
- **THEN** SHALL informarse el número de filas unidas

#### Scenario: Unión incompleta
- **WHEN** hay identificadores sin contraparte
- **THEN** SHALL informarse cuántos y en qué lado faltan, y NO SHALL unirse por texto

### Requirement: Plano de relevancia contra valencia con los niveles de la rúbrica
Para cada criterio de valencia, el notebook SHALL dibujar el plano de relevancia contra valencia del instrumento zero-shot, con los tuits en ausencia como fondo y los tuits con nivel 1 a 5 superpuestos y coloreados por nivel, marcando el umbral de relevancia.

#### Scenario: Capas diferenciadas
- **WHEN** se dibuja el plano de un criterio
- **THEN** los tuits en ausencia SHALL dibujarse como fondo neutro, cada nivel 1 a 5 SHALL ser una serie propia identificable también sin color, y los faltantes NO SHALL dibujarse

#### Scenario: Distribución de relevancia por nivel
- **WHEN** se dibuja el plano
- **THEN** SHALL acompañarse de la distribución de relevancia por nivel, incluida la ausencia, con el número de tuits de cada nivel

#### Scenario: Nivel escaso
- **WHEN** un nivel tiene menos tuits que el mínimo declarado
- **THEN** SHALL dibujarse igualmente con una advertencia de muestra insuficiente

### Requirement: Métricas de validez con incertidumbre
Para cada criterio, el notebook SHALL calcular la capacidad de la magnitud zero-shot para separar tuits presentes de ausentes como área bajo la curva ROC y, en los criterios de valencia, la correlación de rangos entre nivel 1 a 5 y valencia, cada una con intervalo de confianza por remuestreo con semilla fija y con su tamaño de muestra.

#### Scenario: Área bajo la curva
- **WHEN** se evalúa un criterio
- **THEN** SHALL informarse el área bajo la curva ROC con su intervalo, el número de presentes y el de ausentes

#### Scenario: Correlación nivel–valencia
- **WHEN** se evalúa un criterio de valencia
- **THEN** SHALL informarse la correlación de rangos entre nivel y valencia sobre los tuits presentes, con su intervalo y su tamaño de muestra

#### Scenario: Rendimiento no mejor que el azar
- **WHEN** el intervalo del área bajo la curva incluye 0.5 o queda por debajo
- **THEN** SHALL señalarse por escrito junto a la nota de constructo del criterio

### Requirement: Curva ROC para la saliencia de violencia
El criterio binario de violencia SHALL contrastarse contra la prominencia de violencia del instrumento con una curva ROC y la distribución de la prominencia por clase, y NO SHALL dibujarse en el plano de valencia.

#### Scenario: Figura de prominencia
- **WHEN** se valida el criterio de violencia
- **THEN** SHALL dibujarse la curva ROC con su área e intervalo, y la distribución de prominencia para presentes y ausentes

### Requirement: El rótulo distingue contraste entre instrumentos de validación humana
Toda figura y tabla de la sección SHALL rotularse como contraste contra una rúbrica aplicada por un modelo de lenguaje, y SHALL declarar que no sustituye la validación contra codificación humana.

#### Scenario: Rótulo presente
- **WHEN** se muestra cualquier resultado de la sección
- **THEN** su rótulo SHALL indicar que el contraste es entre dos instrumentos automáticos
